# TS-search cache — landed (Layer D, follow-up #5)

**Status:** v1 wired end-to-end. `compute_worked_example_barrier()`
consults the TS cache before invoking Sella; the second call on the
same `(workflow, substrate, tier, method, optimizer_config)` skips the
saddle refinement entirely.
**Closes:** `docs/energetics_ts_search_landed.md` §8 follow-up #5.

## 1. What landed

A content-addressed disk cache for the most expensive single Layer-D
operation: Sella P-RFO saddle refinement on the NEB-derived TS guess.
The xtb worked example takes ~1s; on production DFT the same call
budget is hours. Re-runs of the same target now bypass it.

```
compute_worked_example_barrier(tier="xtb")
        │
        ▼
   TSCache.lookup_or_compute(
       workflow="worked_example",
       substrate_id="nh3_inversion",
       tier="xtb", method="GFN2-xTB",
       optimizer_config=OptimizerConfig.from_saddle_search(search),
       compute=lambda: NH₃ endpoint pre-relax → Sella refine,
   )
        │
        ├── HIT  → return cached TSResult; no xtb, no Sella
        └── MISS → run compute(), persist, return
```

The cache lives at `.cache/ts/<CACHE_VERSION>/<key>.json`. Distinct
from `.cache/energetics/` (the ΔG-rxn cache) so the two version
schemas can evolve independently.

## 2. Key schema

SHA-256 over a sorted JSON object with these fields (32 hex chars):

| field | role |
|---|---|
| `cache_version` | namespaces the schema; bump invalidates pre-fix entries |
| `workflow` | `worked_example` (NH₃ surrogate, planar guess) or `neb_to_sella` (full R→P interpolation) |
| `substrate_id` | `nh3_inversion` for the surrogate; otherwise `substrate_id_from_smiles(R..., P...)` (canonical hash) |
| `tier` | `mlip` / `xtb` / `dft` |
| `method` | label like `GFN2-xTB`, `GFN2-xTB_ALPB-DMF`, `B3LYP-D3BJ_def2-TZVP` |
| `optimizer_fingerprint` | SHA-256 over `OptimizerConfig` (n_images, k, NEB/Sella tolerances + step caps) |

The optimizer fingerprint is what distinguishes this cache from the
ΔG cache. A tight-tolerance Sella refinement (sella_fmax=0.001) and
a loose one (sella_fmax=0.05) of the same substrate at the same
method produce different saddles; the key encodes that, so a loose
hit can't be silently served to a tight caller.

## 3. The persisted record

```json
{
  "cache_key": "e6f8f01524ce7bbd99489ab25a59494d",
  "workflow": "worked_example",
  "substrate_id": "nh3_inversion",
  "tier": "xtb",
  "method": "GFN2-xTB",
  "optimizer_fingerprint": "6209cf928746ca03",
  "result": {
    "barrier_kcal_per_mol": 6.11,
    "e_reactant_ev": -120.4442,
    "e_product_ev": -120.4442,
    "e_ts_ev": -120.1793,
    "n_neb_images": 0,
    "n_sella_iterations": 42,
    "converged": true,
    "method": "GFN2-xTB",
    "provenance": "Sella(order=1, internal=True, …) refined from caller-supplied TS guess; method=GFN2-xTB; E_R=-120.4442eV, E_TS=-120.1793eV; converged=True",
    "cache_key": "e6f8f01524ce7bbd99489ab25a59494d"
  }
}
```

The `cache_key` is repeated inside `result` so a reader can
cross-check that the entry they fetched is the one they meant —
analogous to the `EnergeticsCache` entry's self-identifying behavior.

## 4. Certificate impact

`energetics_dependencies` gains two fields when the worked-example
barrier ran through the cache:

```jsonc
"energetics_dependencies": {
  ...,
  "worked_example_barrier_kcal_per_mol": 6.110,
  "worked_example_provenance": "Sella(…) E_R=-120.4442eV, E_TS=-120.1793eV; converged=True",
  "worked_example_cache_key": "e6f8f01524ce7bbd99489ab25a59494d",   // NEW
  "worked_example_cache_stats": {"hits": 0, "misses": 1},           // NEW (this run only)
  "feasibility": "feasible"
}
```

`cache_stats` reports the **per-call** delta (this run's hits/misses),
not cumulative. A downstream reader can sum across certificates if
they want a fleet view.

## 5. Verifier behavior

Unchanged. `src/macrocert/verifier/verify.py::_check_energetics` only
structurally validates the `per_edge` map; the new
`worked_example_cache_key` / `worked_example_cache_stats` fields flow
through unchecked. This matches Layer-D's defeasibility (proposal
§3.5): the verifier doesn't re-run xtb/MLIP/DFT, and it doesn't
re-fetch from the cache. It checks that the certificate is honest
about what it claimed.

If a future cert-integrity hash is added (the P3 #7 follow-up in
`docs/adversarial_verifier_roadmap.md`), the cache key becomes
attestable cheaply: hashing the on-disk cache record under the
declared key and comparing to the certificate's
`worked_example_cache_key` would catch out-of-band tampering.

## 6. Test coverage

`tests/energetics/test_ts_cache.py` adds 12 tests:

**Unit (fast, 11 tests):**
- OptimizerConfig fingerprint stable + discriminates on each knob
- Disk round-trip; persisted JSON carries its own key
- Distinct keys for distinct workflows / methods (e.g. ALPB-DMF vs ALPB-DCM)
  / optimizer configs / substrates
- `lookup_or_compute` calls `compute()` exactly once per unique key
- `lookup_or_compute` persists the cache_key on the result
- `substrate_id_from_smiles` canonical under within-side order
- Cache root namespaced by `CACHE_VERSION`

**Integration (slow, 1 test):**
- `compute_worked_example_barrier` called twice on a shared TSCache:
  first call misses (xtb + Sella ran), second hits and returns the
  identical `barrier_kcal_per_mol`.

Plus the existing `tests/energetics/test_ts_search.py` updated for
the 5-tuple return signature: `(barrier, feasibility, provenance,
cache_key, cache_stats)` with `cache_key` is a 32-char hex string
and `cache_stats["hits"] + ["misses"] >= 1`.

Test count overall: 189/189 passing (was 177; +12 from this file).

## 7. Open follow-ups

This closes follow-up #5 from the prior `energetics_ts_search_landed`
list. The remaining open items there (MACE-OMol25 download, DFT
refinement tier, atom-mapped bound-complex constructors, 3-model
OOD ensemble) are unchanged; the TS cache will accelerate every one
of them when they land.

Anticipated additional wiring once those tiers exist:

- `neb_to_sella` workflow will be exercised by the
  bound-complex constructors (substrate_id comes from canonical R/P
  SMILES, optimizer_config will reflect the production
  `OptimizerConfig` defaults, not the worked-example tightened
  variant).
- A `pixi run python -m macrocert.cli cache-stats` subcommand
  aggregating both caches' on-disk record counts and last-modified
  times — useful for chemistry-team visibility into Layer-D cost
  amortization.
- A `--purge-tier <mlip|xtb|dft>` flag for cache eviction when a
  method's defaults change (e.g., MACE-OMol25 weight version bumps).
  Today cache invalidation is by CACHE_VERSION; selective eviction
  would help when only one tier needs to be re-run.
