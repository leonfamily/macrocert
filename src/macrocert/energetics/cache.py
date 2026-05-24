"""Content-addressed ΔG cache (Layer D).

Cache key: SHA-256 over (rule_id, canonical_substrate_smiles, canonical_product_smiles,
tier, method_settings). Disk-backed under .cache/energetics/ — the directory is
gitignored, regenerable, and may grow large.

Three tiers in proposal §3.5 order of increasing cost:
  - mlip     (MACE-OFF / AIMNet2 triage)
  - xtb      (GFN2-xTB intermediate)
  - dft      (Psi4 refinement, only used after MLIP triage selects survivors)

A cache hit at any tier prevents re-running the (expensive) underlying
calculation. The tier name is part of the key so an MLIP estimate and
a DFT estimate for the same reaction coexist.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal


Tier = Literal["mlip", "xtb", "dft"]


@dataclass(frozen=True)
class CacheEntry:
    rule_id: str
    reactant_smiles: tuple[str, ...]
    product_smiles: tuple[str, ...]
    tier: Tier
    method: str
    dG_kcal_per_mol: float
    barrier_kcal_per_mol: float | None = None
    provenance: str = ""

    def cache_key(self) -> str:
        return make_cache_key(self.rule_id, self.reactant_smiles, self.product_smiles,
                              self.tier, self.method)


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
        key_args: tuple[str, tuple[str, ...], tuple[str, ...], Tier, str],
        compute: "callable[[], tuple[float, float | None, str]]",
    ) -> tuple[CacheEntry, bool]:
        """Look up; on miss, call `compute()` → (dG_kcal, barrier_kcal_or_None,
        provenance), store, return (entry, was_miss)."""
        key = make_cache_key(*key_args)
        existing = self.get(key)
        if existing is not None:
            return existing, False
        rule_id, reactant_smiles, product_smiles, tier, method = key_args
        dG, barrier, provenance = compute()
        entry = CacheEntry(
            rule_id=rule_id,
            reactant_smiles=reactant_smiles,
            product_smiles=product_smiles,
            tier=tier,
            method=method,
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
) -> str:
    payload = json.dumps({
        "rule_id": rule_id,
        "reactants": sorted(reactant_smiles),
        "products": sorted(product_smiles),
        "tier": tier,
        "method": method,
    }, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:32]
