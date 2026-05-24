"""Content-addressed ΔG cache (Layer D).

Cache key: SHA-256 over (cache_version, rule_id, canonical_substrate_smiles,
canonical_product_smiles, tier, method_id, solvent_name). Disk-backed under
.cache/energetics/ — the directory is gitignored, regenerable, and may grow
large.

Three tiers in proposal §3.5 order of increasing cost:
  - mlip     (MACE-OFF / AIMNet2 triage)
  - xtb      (GFN2-xTB intermediate)
  - dft      (Psi4 refinement, only used after MLIP triage selects survivors)

A cache hit at any tier prevents re-running the (expensive) underlying
calculation. The tier name is part of the key so an MLIP estimate and
a DFT estimate for the same reaction coexist. The `method_id` composes
functional + basis + dispersion + implicit-solvent solver into a single
canonical string (e.g. ``"B3LYP-D3BJ_def2-SVP_PCM-DMF"``); ``solvent_name``
is held *separately* in the key so collisions between (e.g.) DMF and DCM
on the same SMILES and same functional cannot occur even if a caller
sloppily reuses the same ``method_id``.

Workstream E (Marks Vandezande Gomes 2026, arXiv:2604.00405) found
collision risk via solvent omission — the prior key included only
(rule_id, smiles, tier, method) and would silently return DMF energies
to a DCM caller, or PBE energies to a B3LYP caller, whenever the bare
``method`` label was the same. Including ``solvent_name`` and a richer
``method_id`` closes that hole; bumping CACHE_VERSION invalidates any
pre-fix entries so the old, ambiguous keys are never returned.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Literal


Tier = Literal["mlip", "xtb", "dft"]

# Bump whenever the key schema changes; pre-fix entries become unreachable.
# v2: added solvent_name + method_id (Workstream E collision fix, 2026-05).
CACHE_VERSION = "v2"

# Sentinel used when no implicit solvent is in effect (gas-phase / vacuum).
VACUUM_SOLVENT = "vacuum"


@dataclass(frozen=True)
class CacheEntry:
    rule_id: str
    reactant_smiles: tuple[str, ...]
    product_smiles: tuple[str, ...]
    tier: Tier
    method: str
    # New (v2) fields — required for the disambiguated key. Defaults keep
    # adversarial-test fixtures that build CacheEntry by hand still valid.
    method_id: str = ""
    solvent_name: str = VACUUM_SOLVENT
    dG_kcal_per_mol: float = 0.0
    barrier_kcal_per_mol: float | None = None
    provenance: str = ""

    def cache_key(self) -> str:
        return make_cache_key(
            self.rule_id,
            self.reactant_smiles,
            self.product_smiles,
            self.tier,
            self.method,
            method_id=self.method_id or self.method,
            solvent_name=self.solvent_name,
        )


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class EnergeticsCache:
    def __init__(self, root: str | Path = ".cache/energetics"):
        self.root = Path(root)
        # Namespace the on-disk layout by CACHE_VERSION so v1 entries can
        # coexist on disk but never be served by a v2 lookup.
        self.root = self.root / CACHE_VERSION
        self.root.mkdir(parents=True, exist_ok=True)
        self.stats = CacheStats()

    def get(self, key: str) -> CacheEntry | None:
        path = self._path(key)
        if not path.exists():
            self.stats.misses += 1
            return None
        self.stats.hits += 1
        data = json.loads(path.read_text())
        return CacheEntry(
            rule_id=data["rule_id"],
            reactant_smiles=tuple(data["reactant_smiles"]),
            product_smiles=tuple(data["product_smiles"]),
            tier=data["tier"],
            method=data["method"],
            method_id=data.get("method_id", data["method"]),
            solvent_name=data.get("solvent_name", VACUUM_SOLVENT),
            dG_kcal_per_mol=float(data["dG_kcal_per_mol"]),
            barrier_kcal_per_mol=data.get("barrier_kcal_per_mol"),
            provenance=data.get("provenance", ""),
        )

    def put(self, entry: CacheEntry) -> str:
        key = entry.cache_key()
        path = self._path(key)
        path.write_text(json.dumps(asdict(entry), sort_keys=True, indent=2))
        return key

    def lookup_or_compute(
        self,
        key_args: tuple,
        compute: "callable[[], tuple[float, float | None, str]]",
    ) -> tuple[CacheEntry, bool]:
        """Look up; on miss, call ``compute()`` → (dG_kcal, barrier_kcal_or_None,
        provenance), store, return (entry, was_miss).

        ``key_args`` is a 7-tuple:
            (rule_id, reactant_smiles, product_smiles, tier, method,
             method_id, solvent_name)

        For backward compatibility, a 5-tuple is accepted and treated as
        method_id=method, solvent_name=VACUUM_SOLVENT — but this path is
        deprecated; callers should pass the full 7-tuple so the
        Workstream-E collision fix takes effect.
        """
        if len(key_args) == 5:
            rule_id, reactant_smiles, product_smiles, tier, method = key_args
            method_id, solvent_name = method, VACUUM_SOLVENT
        elif len(key_args) == 7:
            (rule_id, reactant_smiles, product_smiles, tier, method,
             method_id, solvent_name) = key_args
        else:
            raise ValueError(
                f"key_args must be a 5- or 7-tuple, got {len(key_args)}"
            )

        key = make_cache_key(
            rule_id, reactant_smiles, product_smiles, tier, method,
            method_id=method_id, solvent_name=solvent_name,
        )
        existing = self.get(key)
        if existing is not None:
            return existing, False
        dG, barrier, provenance = compute()
        entry = CacheEntry(
            rule_id=rule_id,
            reactant_smiles=reactant_smiles,
            product_smiles=product_smiles,
            tier=tier,
            method=method,
            method_id=method_id,
            solvent_name=solvent_name,
            dG_kcal_per_mol=dG,
            barrier_kcal_per_mol=barrier,
            provenance=provenance,
        )
        self.put(entry)
        return entry, True

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"


def make_cache_key(
    rule_id: str,
    reactant_smiles: tuple[str, ...],
    product_smiles: tuple[str, ...],
    tier: Tier,
    method: str,
    *,
    method_id: str | None = None,
    solvent_name: str = VACUUM_SOLVENT,
) -> str:
    """Compute the SHA-256 cache key.

    Workstream E (Marks Vandezande Gomes 2026, arXiv:2604.00405) found
    collision risk via solvent omission — the prior key did not include
    ``solvent_name`` or a structured ``method_id``, so DMF and DCM runs
    of the same SMILES (or B3LYP vs PBE runs with the same display
    ``method`` label) would collide and silently return wrong energies.
    """
    payload = json.dumps({
        "cache_version": CACHE_VERSION,
        "rule_id": rule_id,
        "reactants": sorted(reactant_smiles),
        "products": sorted(product_smiles),
        "tier": tier,
        "method": method,
        "method_id": method_id if method_id is not None else method,
        "solvent_name": solvent_name,
    }, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:32]
