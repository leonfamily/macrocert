"""Content-addressed transition-state cache (Layer D).

Mirrors :mod:`macrocert.energetics.cache` but persists full ``TSResult``
records (barrier + endpoint/TS energies + Sella convergence flag +
provenance string) rather than reaction-energy entries.

Why a separate cache. A Sella P-RFO refinement of an MLIP / xtb / DFT
saddle is the most expensive single computation in Layer D — minutes
on xtb for the NH₃ worked example, hours-to-days on DFT for production
substrates. The ΔG cache in :mod:`cache` keys on
``(rule_id, R/P SMILES, tier, method, solvent_name)``; saddle results
also vary with the *optimizer configuration* — the NEB image count,
the spring constant, the Sella force tolerance — so a separate key
namespace is needed to avoid mis-serving a 5-image NEB result to a
7-image caller and vice versa.

Key schema (SHA-256, 32 hex chars):

  cache_version
  workflow            "worked_example"  (NH₃ surrogate, planar guess refined directly)
                      "neb_to_sella"    (full R→P NEB → Sella; for real macrocycles)
  substrate_id        stable identifier — "nh3_inversion" for the surrogate,
                      otherwise sorted-SMILES tuple of (R..., P...)
  tier                Layer-D tier: mlip / xtb / dft
  method              human-readable label, e.g. "GFN2-xTB_ALPB-DMF"
  optimizer_config    n_images, NEB steps/fmax, Sella steps/fmax, spring k

The on-disk layout is ``.cache/ts/<CACHE_VERSION>/<key>.json``,
gitignored and regenerable. Bumping ``CACHE_VERSION`` invalidates
pre-fix entries without deleting them — they're simply unreachable
from the new schema.

Honesty constraint per proposal §6: the verifier *does not* re-run TS
search. Cached results carry their provenance string, and the
certificate's ``solver_witness`` / ``energetics_dependencies`` declare
the cache key. A reader who wants to challenge the saddle does so by
inspecting the cache entry (its method label and optimizer config
are part of the key, so tampering is detectable).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Literal

from .cache import CacheStats
from .ts_search import TSResult

Tier = Literal["mlip", "xtb", "dft"]
Workflow = Literal["worked_example", "neb_to_sella"]

# Bump independently of EnergeticsCache CACHE_VERSION whenever the TS-cache
# key schema or the persisted ``TSResult`` shape changes. v1 is the initial
# release (this commit).
CACHE_VERSION = "v1"


@dataclass(frozen=True)
class OptimizerConfig:
    """Subset of SaddleSearch knobs that materially affects the saddle.

    ``spring_constant_eV_per_A`` and the NEB image count change the path
    the optimizer explores. ``sella_fmax`` and ``sella_max_steps`` change
    *when* convergence is declared and therefore which saddle is
    returned. Defaults match :class:`macrocert.energetics.ts_search.SaddleSearch`
    so a caller that doesn't override anything gets the protocol-aligned
    key without thinking about it.
    """
    n_images: int = 7
    spring_constant_eV_per_A: float = 0.1
    neb_steps: int = 100
    neb_fmax: float = 0.2
    sella_fmax: float = 0.05
    sella_max_steps: int = 250

    @classmethod
    def from_saddle_search(cls, search) -> "OptimizerConfig":
        return cls(
            n_images=search.n_images,
            spring_constant_eV_per_A=search.spring_constant_eV_per_A,
            neb_steps=search.neb_steps,
            neb_fmax=search.neb_fmax,
            sella_fmax=search.sella_fmax,
            sella_max_steps=search.sella_max_steps,
        )

    def fingerprint(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True).encode()
        ).hexdigest()[:16]


@dataclass(frozen=True)
class TSCacheEntry:
    """Persisted TS-search outcome."""
    workflow: Workflow
    substrate_id: str
    tier: Tier
    method: str
    optimizer_fingerprint: str
    result: TSResult

    def cache_key(self) -> str:
        return make_ts_cache_key(
            workflow=self.workflow,
            substrate_id=self.substrate_id,
            tier=self.tier,
            method=self.method,
            optimizer_fingerprint=self.optimizer_fingerprint,
        )


class TSCache:
    def __init__(self, root: str | Path = ".cache/ts"):
        self.root = Path(root) / CACHE_VERSION
        self.root.mkdir(parents=True, exist_ok=True)
        self.stats = CacheStats()

    def get(self, key: str) -> TSCacheEntry | None:
        path = self._path(key)
        if not path.exists():
            self.stats.misses += 1
            return None
        self.stats.hits += 1
        data = json.loads(path.read_text())
        return _entry_from_dict(data)

    def put(self, entry: TSCacheEntry) -> str:
        key = entry.cache_key()
        path = self._path(key)
        path.write_text(json.dumps(_entry_to_dict(entry, key), sort_keys=True, indent=2))
        return key

    def lookup_or_compute(
        self,
        *,
        workflow: Workflow,
        substrate_id: str,
        tier: Tier,
        method: str,
        optimizer_config: OptimizerConfig,
        compute: Callable[[], TSResult],
    ) -> tuple[TSCacheEntry, bool]:
        """Look up; on miss, call ``compute()`` → ``TSResult``, store,
        return ``(entry, was_miss)``."""
        fp = optimizer_config.fingerprint()
        key = make_ts_cache_key(
            workflow=workflow, substrate_id=substrate_id, tier=tier,
            method=method, optimizer_fingerprint=fp,
        )
        existing = self.get(key)
        if existing is not None:
            return existing, False
        result = compute()
        # TSResult is frozen; replace the cache_key field with the
        # computed one so the persisted record knows its own key.
        result_with_key = replace(result, cache_key=key)
        entry = TSCacheEntry(
            workflow=workflow,
            substrate_id=substrate_id,
            tier=tier,
            method=method,
            optimizer_fingerprint=fp,
            result=result_with_key,
        )
        self.put(entry)
        return entry, True

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"


def make_ts_cache_key(
    *,
    workflow: Workflow,
    substrate_id: str,
    tier: Tier,
    method: str,
    optimizer_fingerprint: str,
) -> str:
    payload = json.dumps({
        "cache_version": CACHE_VERSION,
        "workflow": workflow,
        "substrate_id": substrate_id,
        "tier": tier,
        "method": method,
        "optimizer_fingerprint": optimizer_fingerprint,
    }, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:32]


def substrate_id_from_smiles(
    reactant_smiles: tuple[str, ...],
    product_smiles: tuple[str, ...],
) -> str:
    """Canonical substrate identifier for the neb_to_sella workflow.

    Sorted within each side so atom-order permutations don't produce
    distinct keys; pipe-separated so reactant vs product distinction
    survives the canonicalization.
    """
    r = ";".join(sorted(reactant_smiles))
    p = ";".join(sorted(product_smiles))
    return hashlib.sha256(f"R[{r}]|P[{p}]".encode()).hexdigest()[:16]


def _entry_to_dict(entry: TSCacheEntry, key: str) -> dict[str, Any]:
    return {
        "cache_key": key,
        "workflow": entry.workflow,
        "substrate_id": entry.substrate_id,
        "tier": entry.tier,
        "method": entry.method,
        "optimizer_fingerprint": entry.optimizer_fingerprint,
        "result": asdict(entry.result),
    }


def _entry_from_dict(data: dict[str, Any]) -> TSCacheEntry:
    r = data["result"]
    return TSCacheEntry(
        workflow=data["workflow"],
        substrate_id=data["substrate_id"],
        tier=data["tier"],
        method=data["method"],
        optimizer_fingerprint=data["optimizer_fingerprint"],
        result=TSResult(
            barrier_kcal_per_mol=float(r["barrier_kcal_per_mol"]),
            e_reactant_ev=float(r["e_reactant_ev"]),
            e_product_ev=float(r["e_product_ev"]),
            e_ts_ev=float(r["e_ts_ev"]),
            n_neb_images=int(r["n_neb_images"]),
            n_sella_iterations=int(r["n_sella_iterations"]),
            converged=bool(r["converged"]),
            method=r["method"],
            provenance=r["provenance"],
            cache_key=r.get("cache_key", ""),
        ),
    )
