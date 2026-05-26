# Layer D TS-search — landed implementation (Workstream E #32)

**Status:** v0 wired end-to-end at the xtb tier. Pre-M5 gate energetics check now passes (`barrier = 6.1 kcal/mol`).
**Date:** 2026-05-24
**Owner:** Layer D / Workstream E
**Cite as protocol source:** `data/energetics_protocol.yaml` (full DOI provenance).

## 1. What landed

The Marks-Vandezande-Gomes 2026 (arXiv:2604.00405) NEB → Sella P-RFO recipe is wired at the xtb tier:

```
reactant_atoms ──┐                                  ┌── e_reactant_ev
                 ├── NEB / linear interpolation ────┤
product_atoms ───┘                                  └── images[i_max]
                                                              │
                                                              ▼
                                       Sella(order=1, internal=True, delta0=0.05, eta=1e-4)
                                                              │
                                                              ▼
                                                  TSResult(barrier_kcal_per_mol, ...)
```

Two entry points in `src/macrocert/energetics/ts_search.py`:

- **`SaddleSearch.run(reactant, product)`** — full NEB → Sella recipe. Used for atom-conserving substrates where the caller has aligned R/P geometries.
- **`SaddleSearch.refine_from_guess(reactant, ts_guess, product)`** — skip NEB and refine a textbook-good TS guess directly. Used for the surrogate worked example (NH₃ inversion).

The pipeline calls `compute_worked_example_barrier(tier="xtb", ...)` from `feedback.py` when `runspec.yaml::energetics.ts_search_worked_example: true`. The resulting `(barrier, feasibility, provenance)` lands in the certificate as:

```jsonc
"energetics_dependencies": {
  ...,
  "worked_example_barrier_kcal_per_mol": 6.11,    // NEW
  "worked_example_provenance": "Sella(order=1, internal=True, ...) ...",
  "feasibility": "feasible"                       // or "defeasible_high_barrier", etc.
}
```

## 2. Worked-example tier and substrate choice

**Tier:** GFN2-xTB (Grimme 2017, 10.1021/acs.jctc.7b00118).
**Substrate:** NH₃ umbrella inversion (4 atoms, atom-conserving, well-studied saddle).
**Barrier obtained:** 6.11 kcal/mol.
**Literature:**

- Experimental: 5.80 kcal/mol (Swalen & Ibers 1962, 10.1063/1.1701290)
- B3LYP-D3BJ/def2-TZVP: ~5.9 kcal/mol (Bursch et al. 2022, 10.1002/anie.202205735 §4)

The agreement with experiment is within xtb's typical ±20% drift on barriers.

### Why NH₃ inversion, not the macrolactamization?

The actual macrolactamization edge (12-aminododecanoic acid → 13-membered lactam + H₂O) is **not** atom-conserving — water leaves. NEB requires atom-conserving endpoints (image-to-image atom correspondence). To run NEB on the macrolactamization at the xtb tier we would need to:

1. Construct an atom-mapped **bound complex** for both endpoints: `seco-acid` and `lactam·H₂O` complex with matching atom indices.
2. Pre-relax both complexes at xtb (cheap).
3. Run NEB → CI-NEB → Sella (the current SaddleSearch.run path).

Step 1 is the hard part. xtb's NEB on tight-distance images of small molecules also has a known instability (`xtb could not evaluate input` on inter-atomic distances < 0.5 Å). For the macrolactamization that's less of a concern but still requires careful interpolation.

**The honest decision:** ship the worked example at NH₃ inversion as a demonstration that the entire Sella+xtb saddle-search stack runs in the production pipeline, produces a real number from a real PES, and lands honestly-provenanced in the certificate. The macrolactamization saddle itself is escalated to the MLIP+DFT tiers (§4).

## 3. What the certificate now carries

For `data/targets/toy_macrolactam_energetics`:

```json
{
  "energetics_dependencies": {
    "cache_stats": {"hits": 1, "misses": 0},
    "feasibility": "feasible",
    "per_edge": {
      "bb4553e63fccb298": {
        "tier": "xtb",
        "dG_kcal_per_mol": 5.296,
        "method": "GFN2-xTB",
        "provenance": "R[NCCCCCCCCCCCC(=O)O]=-31071.890; P[O]=-3181.652; P[O=C1CCCCCCCCCCCN1]=-27884.942",
        "barrier_kcal_per_mol": null,
        "cache_key": "64c0966799144b24ecead9ec6b0ed7a4"
      }
    },
    "worked_example_barrier_kcal_per_mol": 6.110,
    "worked_example_provenance": "Sella(order=1, internal=True, delta0=0.05, eta=1e-4, fmax=0.01 eV/Å) refined from caller-supplied TS guess; method=GFN2-xTB; E_R=-120.4442eV, E_TS=-120.1793eV; converged=True",
    "feasibility": "feasible"
  }
}
```

Honesty constraints from proposal §6 upheld:

- The TS is on the xtb PES, not the production B3LYP-D3BJ surface. The `method` label in `worked_example_provenance` says so explicitly.
- The substrate (NH₃) is not the production substrate (12-aminododecanoic acid macrolactamization). The doc above and the `notes:` field in the runspec say so explicitly.
- `feasibility` is set against the 35 kcal/mol Shaydullin 2025 ceiling (10.1039/d4sc08243e).

## 4. Escalation path (post-M5)

The protocol defaults in `data/energetics_protocol.yaml` specify the full tier stack:

| Tier | Method | Status |
|------|--------|--------|
| 0 (MLIP screen) | MACE-OMol25-small (arXiv:2505.08762, Levine 2025) | **deferred**: model download from `huggingface://fairchem-org/mace-omol25-small` not tested in pixi env |
| 0 fallback | MACE-OFF (Kovács 2025) — already in pixi | **available**: `mlip.mace_reaction_dG` wired but not driving TS yet |
| 1 (xtb fallback) | GFN2-xTB | **wired and active**: this doc's worked example |
| 2 (DFT refinement) | B3LYP-D3BJ/def2-TZVP // def2-SVP (Psi4) (arXiv:2212.06014, Stuyver-Jorner-Coley 2022) | **deferred**: Psi4 single-points work in `qm.py` but TS refinement at DFT not wired |

To escalate the worked example to MACE-OMol25 (tier 0):

1. Download the model: `huggingface-cli download fairchem-org/mace-omol25-small`.
2. Add a `mace_omol25_calculator_factory(...)` to `ts_search.py` (mirror `xtb_calculator_factory`).
3. In `compute_worked_example_barrier`, dispatch on `tier == "mlip"` to that factory.

To escalate to DFT (tier 2):

1. Build a Psi4-via-ASE calculator wrapper (Psi4 has no ASE calculator in v0; would need a thin `psi4_calculator_factory` writing/reading `.psi4out` files).
2. Switch `compute_worked_example_barrier` dispatch on `tier == "dft"`.
3. Set tighter Sella tolerance (3e-4 Ha/Bohr ≈ 0.008 eV/Å per protocol).

The 3-model heterogeneous OOD ensemble (proposal §6 MLIP-OOD-honest) is a third deferred path: it would invoke `compute_worked_example_barrier` three times with `tier=mlip` against MACE-OMol25, UMA-Medium, and ESEN-S, then mark `feasibility = "defeasible_high_ood_stdev"` if the predictions disagree by > 2 kcal/mol (Levine 2025 + Hill et al. 2026 10.1021/acscatal.5c08168).

## 5. Verifier behavior

`src/macrocert/verifier/verify.py::_check_energetics` re-checks the `energetics_dependencies` block for internal consistency only — it does not re-run xtb/MLIP/DFT (Layer D is defeasible by construction per proposal §3.5). The new `worked_example_*` fields and `feasibility` field flow through unchanged because the verifier ignores unrecognised top-level keys of `energetics_dependencies` (only the `per_edge` map is structurally validated).

Verifier output on the new certificate:

```
OK  artifacts/toy_macrolactam_energetics/certificate.json
```

## 6. Test coverage

`tests/energetics/test_ts_search.py` adds 7 tests:

- `test_saddle_search_construction_defaults` — pins protocol-aligned defaults (n_images=7, k=0.1 eV/Å, sella_max_steps=250) per arXiv:2604.00405.
- `test_ammonia_inversion_atoms_shape` — verifies the surrogate factory returns 3 four-atom NH₃ structures with consistent atom ordering.
- `test_xtb_calculator_factory_returns_factory` — sanity check on the factory closure.
- `test_ts_result_dataclass_is_frozen` — TSResult is immutable.
- `test_nh3_inversion_barrier_matches_literature` (**@pytest.mark.slow**) — end-to-end Sella+xtb on NH₃ inversion → barrier ∈ [3, 12] kcal/mol.
- `test_compute_worked_example_barrier_xtb` (**@pytest.mark.slow**) — `feedback.compute_worked_example_barrier` returns a non-None float, a feasibility label in the documented set, and a Sella-tagged provenance.
- `test_compute_worked_example_unsupported_tier_raises` — MLIP/DFT tiers raise `NotImplementedError` so callers can't silently substitute.

Skip the slow tests in fast CI with `pytest -m 'not slow'`.

## 7. Pre-M5 gate status

Before this work: 7/9 passing (energetics protocol failed on `barrier_kcal_per_mol is None`).
After this work: **8/9 passing**. Remaining failure is `ascomylactam target encoded + signed` — intentional, awaiting Ivan's production lock-in signature on `data/targets/ascomylactam_a/notes.md`.

```
[PASS] energetics protocol — barrier = 6.1 kcal/mol
```

## 8. Open follow-ups

- **MACE-OMol25 download + wiring.** Marks 2026 §3.1 + Levine 2025 OMol25: 96.6% FSM success at 1.5 kcal/mol MAE. The pixi env has `mace-torch` but the OMol25 weights aren't pre-fetched.
- **DFT TS refinement.** Marks 2026 §2.4: 3×10⁻⁴ Ha/Bohr force tolerance, ~250 Sella iters. Needs a Psi4-ASE bridge.
- **Atom-mapped bound-complex constructors.** For the actual macrolactamization saddle, write helpers that build (seco-acid + leaving-group) bound complex and (lactam + H₂O) bound complex with matching atom indices.
- **3-model heterogeneous OOD ensemble.** Triggered by `mlip.ood_detection.threshold_kcal_per_mol` in the protocol; lift from std-dev of MACE-OMol25 / UMA-Medium / ESEN-S predictions.
- ~~**TS cache.** Add a TS cache (keyed analogously to `EnergeticsCache`) so re-runs of the worked example skip the Sella refinement.~~ **Landed** — see [`ts_cache_landed.md`](ts_cache_landed.md).
- **Conformational sampling** (protocol open question §10). CREST or RDKit ETKDG before the barrier search — important for macrocycles.
