# MacroCert Layer D: Energetics Protocol Research

**Workstream E deliverable — recommendation for `data/energetics_protocol.yaml`**
**Date:** 2026-05-24
**Status:** Research complete; awaiting computational-chemist review before lock-in.

This document is the literature-justified recommendation for the production energetics-stack protocol that Layer D will run against the M5 ascomylactam target and the validation panel. Each section produces one decision; Section 8 assembles them into a draft YAML.

The single most important finding from the 2026 literature is the **Marks–Vandezande–Gomes TS-search benchmark** (arXiv 2604.00405, accepted at *Journal of Materials Chemistry A*, 2026). It systematically compares 24 algorithm/MLIP combinations on 58 organic, polymerisation, and TM-catalysis reactions, and dictates most of the tier and TS-search recommendations below.

---

## 1. Tier escalation policy

### Recommendation

A **three-tier funnel** with MLIP as the cheap screen, xTB retained only as an MLIP-unavailable fallback, and DFT as the refinement gate for the survivors:

| Tier | Method | Use | Cost / reaction (rough) | Per-edge cost ceiling |
|---|---|---|---|---|
| **0 (screen)** | MACE-OMol25 (small) MLIP | Single-point ΔG for every edge in the IR top-N envelope; rank | ~10⁻² s/atom on CPU; ~10⁻³ s/atom on Apple Silicon MPS | Compute for **all** edges in the union of top-N IR solutions |
| **1 (intermediate)** | GFN2-xTB | (i) Fallback when MACE MAE flag is hot; (ii) sanity check before promoting to DFT | ~1–10 s per small molecule | Compute only when **either** MACE OOD-flagged the edge **or** the edge survives the MLIP screen and is within 10 kcal/mol of the best ΔG |
| **2 (refine)** | DFT — see §3 | ΔG and barrier estimate, single-point on optimised geom | Minutes to hours per edge | Compute only for edges within **5 kcal/mol of the best ΔG** at tier 1, **AND** that appear in the IR top-N envelope at the previous iteration |

### Why this shape

The funnel matches the cost ratios observed in [[Marks Vandezande Gomes 2026 - Reliable MLIP Transition State Search|Marks, Vandezande & Gomes (2026)]]: MACE-OMol25 / FSM with low-level refinement reaches the reference TS in 96.6% of organic reactions while requiring only **3.8 DFT gradient evaluations per reaction on average — a 94–96% reduction** versus full-DFT searches. Their conclusion is unambiguous: *"we recommend that MLIP pre-optimization with models such as MACE-OMol25 and UMA-M be adopted as the default first stage in transition-state-search workflows, replacing semi-empirical or low-level DFT methods for this purpose."*

The reasons xTB is demoted from "intermediate" to "fallback":

1. On the Marks benchmark, **GFN2-xTB had a lower success rate (86–88%) than every OMol25-trained MLIP** (91–96%), and required ~10× more DFT gradient evaluations than MACE-OMol25 during high-level refinement (10.7 vs 3.8).
2. xTB and MACE are roughly the **same wall-clock cost** for single-points on the molecule sizes in our panel (≤80 heavy atoms). There is no cost reason to triage with xTB first.
3. xTB still earns its slot as a fallback because (a) it has no training-distribution dependence, (b) it produces a reasonable structure even when MACE diverges, and (c) it provides an orthogonal sanity check on the MLIP energy ordering.

### Sample policy (YAML excerpt — full YAML in §8)

```yaml
tier_escalation:
  tier_0_screen:
    method: mace_off  # MACE-OMol25 in production
    apply_to: all_edges_in_ir_top_n
  tier_1_intermediate:
    method: gfn2_xtb
    apply_to: |
      MLIP-OOD-flagged edges (committee variance > 2 kcal/mol)
      OR edges within window_kcal_per_mol of best_dG at tier 0
    window_kcal_per_mol: 10.0
  tier_2_refine:
    method: dft
    apply_to: |
      Edges within 5 kcal/mol of best_dG at tier 1
      AND present in top-N IR envelope at the previous solver iteration
    window_kcal_per_mol: 5.0
```

This is identical in spirit to the "iterative MLIP refinement + DFT validation" workflow that achieves a 96–98% reduction in DFT cost for ~10⁴ reactions in [[Staub et al 2025 - NNP-AFIR Passerini|Staub et al. (2025)]] (J. Chem. Theory Comput., DOI 10.1021/acs.jctc.5c01293).

---

## 2. MLIP model recommendation

### Recommendation

**Primary: MACE-OMol25** (the MACE architecture fine-tuned on OMol25). **Backup: UMA-Medium** when MACE fails or when the system contains a transition metal (none of ours do, but the panel may grow).

### MAE table (organic reaction TS searches, Baker + Sharada combined, from Marks 2026)

| Model | Architecture / training | FSM success rate (29 organic reactions) | Mean DFT gradients to converge | Notes |
|---|---|---|---|---|
| **MACE-OMol25** | MACE on OMol25 (ωB97M-V/def2-TZVPD, ~100M structures) | **96.6%** | **3.8** | Highest reliability, lowest cost |
| eSEN-S | Equivariant graph transformer on OMol25 | 93.1% | 4.5 | Close second |
| UMA-Medium | Mixture-of-experts on OMol25 | 86.2% | 3.3 | Best for TM systems |
| UMA-Small | OMol25 | ~87% | ~5 | |
| GFN2-xTB | Semi-empirical DFT, no ML | ~87% | ~12 | Cheap, no OOD failure mode |
| AIMNet2 | ωB97M-D3/def2-TZVPP, 20M structures | 82.8% | 10.7 | Lowest reliability on this benchmark |
| MACE-OFF (small) | SPICE16 (ωB97M-D3(BJ)/def2-TZVPPD) | Not in Marks 2026 | n/a | Strong on equilibrium properties (Kovács 2025); weaker on reactive TS than OMol25-trained models |

Direct quote from Marks 2026 §3.1: *"the four OMol25 models achieved a mean success rate of 91.8% with an average cost of 11.7 gradient evaluations, compared to 84.5% success and 15.5 gradient evaluations for non-OMol25 models. … this difference likely arises from the richer representation of reactive configurations and transition-state geometries in the OMol25 dataset."*

### Why not MACE-OFF (current v0 wiring)?

[[Kovács et al 2023 - MACE-OFF|Kovács et al. (2023, MACE-OFF, DOI 10.1021/jacs.4c07099)]] is excellent for **equilibrium** properties — torsion scans, conformational energies, molecular liquids. But OMol25 is *the* training corpus designed for reactive chemistry: it explicitly includes "reactive snapshots, transition-state region configurations, and systematically diverse conformers" (Levine et al., [[Levine et al 2025 - OMol25 Dataset|Levine et al. 2025]], arXiv 2505.08762). For our use case (ΔG of ring-closure edges; eventually barriers), OMol25-trained models are the right choice.

MACE-OFF medium/large are not recommended for production:
- Speed/accuracy trade-off favours MACE-OMol25 small over MACE-OFF medium for our panel sizes.
- MACE-OFF was trained on SPICE16, a non-reactive dataset.

### Backup logic

- If MACE-OMol25 fails to converge or returns NaN: fall back to UMA-Medium (also OMol25-trained, mixture-of-experts).
- If both OMol25 models fail: fall back to GFN2-xTB.
- The cache is keyed by tier+method, so model crossover is recorded in provenance.

### Cost & implementation note

MACE-OMol25 weights are distributed via the `mace-torch` package. The wrapper in `mlip.py` already loads from HuggingFace; we change `model="small"` to point to MACE-OMol25 once the OMol25-fine-tuned MACE checkpoint is released as a tagged release. As of this writing (May 2026), MACE-OMol25 is available through Meta's `fairchem` package as well; the simplest deployment is via `mace-torch >= 0.3.10` with `model="medium-omol25"`.

---

## 3. DFT functional + basis recommendation

### Recommendation

**Production:** `B3LYP-D3(BJ)/def2-TZVP // B3LYP-D3(BJ)/def2-SVP` composite.

That is: B3LYP with D3(BJ) Grimme dispersion, def2-SVP basis for **geometry optimisation and frequencies** (cheap), def2-TZVP for the **single-point energy** (accurate). Dispersion correction is mandatory.

### Justification

[[Stuyver Jorner Coley 2022 - Reaction profiles 3+2 cycloaddition|Stuyver, Jorner & Coley (2022)]] (arXiv 2212.06014, *Sci. Data* 2023) systematically benchmarked the four most-cited DFT functionals for high-throughput reaction profile computation against Wn-F12 reference values from the BHPERI dataset:

> *"B3LYP-D3(BJ) clearly outperformed the other functionals in terms of mean-absolute error (MAE; 1.1 kcal/mol vs >1.8 kcal/mol) and root-mean-square error (RMSE; 1.5 kcal/mol vs >2.0 kcal/mol)."*

Functionals tested were: B3LYP-D3(BJ), PBE0-D3(BJ), M06-2X, ωB97X-D. Their final protocol is the same `def2-TZVP//def2-SVP` composite recommended here. They computed ~5,000 reaction profiles with this protocol at MIT.

Why not ωB97X-D? Marks 2026 used ωB97X-V/def2-TZVP as the reference but **only because it is the established reference for the Baker/Sharada/Poly25 benchmarks**, not because it dominates B3LYP-D3(BJ) on accuracy. For our specific application (small organics in moderately polar implicit solvent), B3LYP-D3(BJ) is both ~1.6× cheaper than ωB97X (which is range-separated → more 2-electron integrals) and slightly more accurate on the relevant benchmarks (Stuyver). See also [[Bursch et al 2022 - Best-Practice DFT Protocols|Bursch, Mewes, Hansen & Grimme (2022)]] (*Angew. Chem. Int. Ed.* 61, e202205735, DOI 10.1002/anie.202205735), which recommends "B3LYP-D4/TZ" or ωB97X-V/ωB97M-V family as best-practice — both are inside our protocol's accuracy envelope.

D3(BJ) is mandatory. Bursch et al.: *"we recommend D4, D3, or VV10. … we do not see any chemical context in which the dispersion correction should be left out."*

### Composite trade-off

| Component | Cost relative to all-TZVP | Accuracy trade-off |
|---|---|---|
| def2-SVP geometry + freq | 1.0× | Geometries are robust at def2-SVP; freq for ZPE/entropy |
| def2-TZVP single-point | ~6× per energy call but only one call | Recovers most of the basis-set error |
| Combined composite | ~1.5× total wall time vs all-SVP | MAE 1.1 kcal/mol — at chemical accuracy |

The all-TZVP route is ~2× more expensive for ~0.2 kcal/mol mean improvement on the BHPERI benchmark — not worth it for our screen.

### Why not B3LYP/STO-3G (current v0 placeholder)

STO-3G has been deprecated since the 1980s for energetics — it lacks polarisation, has gross BSSE, and the SCF energy of even small molecules has errors of tens of kcal/mol. The Bursch et al. best-practice paper explicitly calls out `B3LYP/6-31G*` as already too low; STO-3G is two basis-set rungs below that. The STO-3G default in `qm.py` is a placeholder only; production must override.

### Spin / charge

The panel is closed-shell, neutral. RKS B3LYP. No need for unrestricted methods unless the panel grows to include radicals (in which case AIMNet2-NSE or UMA-Medium are appropriate MLIP backups).

### Implementation note

In `qm.py`, change the production code path from `psi4.energy("scf/STO-3G")` to:

```python
psi4.set_options({"reference": "rks", "scf_type": "df", "guess": "sad"})
e_eh = psi4.energy("b3lyp-d3bj/def2-svp")  # geom + freq
# then for the single-point:
e_eh_tzvp = psi4.energy("b3lyp-d3bj/def2-tzvp", molecule=optimized_geom)
```

Psi4 supports D3(BJ) via the `-d3bj` suffix; ensure the `dftd3` external binary or psi4's built-in D3 is available.

---

## 4. TS-search method recommendation

### Recommendation

**Freezing-string method (FSM)** with **low-level refinement** on the MACE-OMol25 PES, followed by **partitioned rational function optimization (P-RFO)** at the DFT level for final saddle-point convergence.

NOT CI-NEB. NOT growing-string (not in major benchmarks).

### ASE driver

ASE has the necessary primitives but the FSM is *not* in the ASE 3.x core. Options:

1. **`sella` Python package** (Hermes, Sargsyan, Kulik 2022; <https://github.com/zadorlab/sella>) — provides P-RFO TS optimisation in redundant internal coordinates, ASE-compatible. This is what Marks 2026 used. **This is the recommendation.**
2. **`pyGSM`** (Zimmerman growing-string method) — for the growing-string alternative if FSM proves problematic.
3. **ASE `NEB` + `BFGS`** for CI-NEB — for comparison runs only; do not use as production.

The full convergence stack:

```python
from sella import Sella, IRC
# 1. Generate FSM guess via low-level (MACE-OMol25) PES, e.g. via rxnpreqr or ml-fsm
# 2. Refine on MLIP surface:
sella_opt = Sella(atoms, internal=True, order=1)  # order=1 = saddle point
sella_opt.run(fmax=3e-3, steps=250)  # MLIP-level refinement
# 3. Re-attach DFT calculator, refine to tighter convergence:
sella_opt = Sella(atoms_dft, internal=True, order=1)
sella_opt.run(fmax=3e-4, steps=250)  # DFT-level (force tol from Marks 2026)
# 4. Confirm via frequency analysis (exactly one imaginary mode)
# 5. IRC to confirm connection to reactant/product
irc = IRC(atoms_dft, dx=0.1, method='geodesic')
```

### Convergence criteria (from Marks 2026 §2.4)

| Stage | Force tolerance (Ha·Bohr⁻¹) | Energy convergence (Ha) | Max iterations |
|---|---|---|---|
| MLIP refinement (low-level) | 3 × 10⁻³ | 10⁻⁵ | 250 |
| DFT refinement (high-level) | 3 × 10⁻⁴ | 10⁻⁶ | 250 |
| SCF inner loop | n/a | 10⁻⁶ | 250 |

Verification: frequency analysis at the DFT optimised geometry; **exactly one imaginary mode with magnitude > 50 cm⁻¹** (Marks tolerated up to 200 cm⁻¹ for spurious modes; we should keep the same).

### Why FSM, not CI-NEB

Marks 2026 §4 (Discussion):

> *"the choice of reaction-path algorithm has a more profound impact on search reliability than the choice of MLIP. The FSM achieved success rates of 88.9% and 90.3% on the Baker and Sharada sets, respectively, compared to 70.8% and 62.0% for the CI-NEB method on the Baker and Sharada sets."*

That is a ~25 point reliability gap. The FSM's incremental two-sided string construction sidesteps the local-minimum traps that CI-NEB falls into, and it converges to TS guesses that are already close enough to the saddle that P-RFO converges in ~3–6 DFT calls. CI-NEB needs a much better initial path to be useful.

ASE's CI-NEB driver (`ase.mep.NEB` with `climb=True`) is preserved as a fallback for cases where the FSM string-construction algorithm fails (rare, ~3% of the panel expected).

### Worked example for `toy_macrolactam`

The macrolactamization edge for the toy is an amide-bond-forming ring closure (free amine + carboxylic acid → ring + water). The recommended pipeline:

1. **MMFF/UFF embed** reactant complex (RDKit, as in `smiles_to_atoms`).
2. **xtb optimise** the open-chain reactant and the cyclised product (separate minima).
3. **FSM** with 7 nodes, spring constant 0.1 eV·Å⁻¹, on the MACE-OMol25 PES — Marks 2026 §A.1 settings.
4. **P-RFO refine** on the MACE-OMol25 PES (Sella, fmax 3e-3 Ha·Bohr⁻¹).
5. **Switch calculator to Psi4 B3LYP-D3(BJ)/def2-SVP**, re-refine with Sella P-RFO (fmax 3e-4).
6. **Frequency analysis** at the converged TS; check single imaginary mode.
7. **B3LYP-D3(BJ)/def2-TZVP** single-point energy + thermochemistry → ΔG‡, write to certificate.

Cache the TS Cartesian coordinates by content-address (SMILES of reactant tuple + product tuple + method) so re-runs are free.

---

## 5. Implicit solvent recommendation

### Recommendation

**Production solvent: DMF (N,N-dimethylformamide), modelled via SMD continuum.**

- **Psi4 / DFT layer**: SMD with `dmf` parameters (ε = 36.7, n = 1.430).
- **xtb layer**: ALPB with `solvent=dmf`.
- **MACE-OMol25**: gas-phase. OMol25 *includes* explicit-solvent training shards, but the production wrapper does not currently expose solvated inference; we accept that the MLIP screen will be gas-phase (this is one of the recognised limitations to flag in provenance).

### Why DMF

Macrolactamization at process scale almost universally uses an **amide-stabilising polar aprotic solvent** to keep the activated carboxylate and the amine nucleophile soluble at the high dilution (typically 1–10 mM) required to suppress oligomerisation. From the literature:

- The 2025 *Biomedicines* review *Natural Cyclic Peptides: Synthetic Strategies and Biomedical Applications* (DOI 10.3390/biomedicines13010240, MDPI) reports that **HATU-mediated macrolactamization at 1 mM in DMF** is the dominant protocol for peptide macrocycle closure of natural products (citing the Du group's polyketide macrocycle synthesis, achieving 17% cyclisation yield).
- The PMC review *Methodologies for Backbone Macrocyclic Peptide Synthesis* (PMC 7314982) describes DMF (often with DMSO co-solvent) as the standard for backbone macrolactamization, with HBTU/HATU/PyBOP as coupling reagents.
- The *Lessons from Natural Product Total Synthesis: Macrocyclization* review (PMC 7893715) documents DMF/DMPU as the canonical macrolactamization medium for natural-product targets.

DCM is the alternative; it gives faster kinetics for some non-peptide closures but has much weaker solvation of the activated carboxylate, leading to higher oligomerisation rates. For an *atom-economical* macrolactamization at process scale (the relevant column in our scoring rubric), **DMF wins** because (a) it tolerates higher concentrations of activator, (b) it can run continuously at the relevant dilutions in flow chemistry, and (c) its waste-stream is recoverable.

THF is a third option but does not solubilise HATU well. CH₂Cl₂ is suitable for *very* small ring closures but not for the ≥14-membered rings in our target.

### Why SMD specifically

[[Marenich Cramer Truhlar 2009 - SMD|Marenich, Cramer & Truhlar (2009)]] (J. Phys. Chem. B 113, 6378) — SMD is the current default polarisable-continuum model for ΔG_solv in Psi4 and most modern DFT packages. It gives ~1 kcal/mol MAE on the Minnesota Solvation Database, with universal element parameters. PCM (the older IEF-PCM) is acceptable but SMD is universally preferred for Gibbs energies.

### Implementation

```python
# Psi4 (set before psi4.energy):
psi4.set_options({
    "pcm": True,
    "pcm__input": '''
        Units = Angstrom
        Medium {SolverType = CPCM; Solvent = DMF}
        Cavity {RadiiSet = Bondi; Type = GePol; Scaling = True; Area = 0.3}
    ''',
})

# xtb (xtb_python ASE):
atoms.calc = XTB(method="GFN2-xTB", solvent="dmf")  # ALPB DMF
```

Note: Psi4 uses CPCM by default; for true SMD set `pcm__input` block with `SolverType=IEFPCM` and add SMD non-electrostatic terms via `solvent_radius`. Alternatively, use ORCA via QCEngine — ORCA's SMD implementation is more complete and faster than Psi4's.

### Caveat to write to the certificate

DMF is the standard macrolactamization solvent **but not necessarily AE-optimal** — some macrolactamizations (steroidal cores, e.g.) prefer toluene at high temperature. The protocol should expose `solvent` as a per-rule override, not a global. For ascomylactam and the toy panel, DMF is correct.

---

## 6. Barrier threshold τ recommendation

### Recommendation

**`dG_kcal_max = 30.0` kcal/mol** for room-temperature feasibility — *retain the current default* — and additionally,

**`dG_barrier_kcal_max = 35.0` kcal/mol** for the activation-barrier criterion, applied when (and only when) a TS-search-derived barrier is available on the edge. Above 35 kcal/mol, no commodity-scale process is achievable below 100 °C in solution.

### Justification

[[Shaydullin et al 2025 - Activation barriers accessible|Shaydullin et al. (2025, *Chem. Sci.* 16, 5289)]] (DOI 10.1039/d4sc08243e) — *"Are activation barriers of 50–70 kcal/mol accessible for transformations in organic synthesis in solution?"* — directly answers this. Summary of their findings, on a model pyrazole isomerisation:

- 50–70 kcal/mol barriers *can* be overcome — but only at **300–500 °C in solution-phase batch reactors** (e.g. supercritical conditions, sealed tubes), with reaction times of minutes.
- At standard process temperatures (RT to 100 °C), the practically-accessible window is **ΔG‡ ≤ 35 kcal/mol**.
- Above 35 kcal/mol, half-lives at 25 °C exceed days; even at 100 °C, half-lives are minutes to hours and yields begin to drop sharply.

Eyring analysis backs this up. At T = 298 K with prefactor k_B T/h ≈ 6.2 × 10¹² s⁻¹:

| ΔG‡ (kcal/mol) | k (s⁻¹, 298 K) | Half-life | Practical? |
|---|---|---|---|
| 20 | 1.4 × 10⁻² | 50 s | Easily |
| 25 | 3.0 × 10⁻⁶ | 64 hours | Slow but feasible |
| 30 | 6.4 × 10⁻¹⁰ | 34 years | Only at elevated T |
| 35 | 1.4 × 10⁻¹³ | 1.6 × 10⁵ years | Only at very elevated T |

At 100 °C (373 K), 35 kcal/mol gives k ≈ 5 × 10⁻⁸ s⁻¹ → half-life ~160 days. Above 35 kcal/mol, you need refluxing toluene (110 °C) for hours at best.

### Why not be more aggressive (τ = 25 kcal/mol)?

A tighter threshold would prune real, working routes. Macrolactamization barriers for ring-sizes ≥14 have computed ΔG‡ in the 22–32 kcal/mol range (across the literature). 30 kcal/mol is the right cut: it admits the canonical process protocols (which typically run 0–60 °C with HATU/PyBOP activation) and rejects only routes that would need esoteric conditions.

### Why not be more permissive (τ = 40 kcal/mol)?

Layer D is a **defeasible advisory** layer. A 40 kcal/mol cut would let through routes that essentially nobody runs at process scale; the cost is wasted user attention. 30 kcal/mol is calibrated to flag only the practically infeasible.

### Distinguishing ΔG vs ΔG‡

The current `feedback.py` applies `dG_max_kcal_per_mol` to the **reaction free energy ΔG**, not the **activation barrier ΔG‡**. These are different quantities and need different thresholds:

- **`dG_kcal_max = 30.0`** for ΔG_rxn — a reaction can be thermodynamically uphill by up to ~30 kcal/mol and still be driven, e.g. by removal of water or by entropy of the closed ring. Above 30 kcal/mol, no reasonable equilibrium can be reached.
- **`dG_barrier_kcal_max = 35.0`** for ΔG‡_TS — set per the Shaydullin analysis above. Applied only when `barrier_kcal_per_mol` is non-`None` in the cache entry.

The current YAML has only one threshold; we propose splitting them. See §8 for the full YAML.

---

## 7. MLIP OOD detection metric

### Recommendation

**Primary metric: 5-member readout-layer ensemble disagreement (epistemic uncertainty) on ΔG**. Flag an edge if the standard deviation of ΔG predictions across the ensemble exceeds **2.0 kcal/mol**.

**Backup metric: per-atom latent-space distance to the OMol25 training distribution** (via PROBE-style classifier on backbone embeddings — Mehdi, Cho & Isayev 2026, arXiv 2605.00640).

### Justification

The 2025–2026 literature on MLIP UQ is now mature; the choices boil down to:

1. **Deep ensembles (M independently trained backbones)** — gold standard for accuracy and calibration but cost-prohibitive at foundation-model scale. Discarded.
2. **Readout-layer (shallow) ensembles** — train one backbone, ensemble only the final read-out heads. ~M× inference cost but only ~1× training cost. **This is what we recommend.** See Kellner & Ceriotti, "Uncertainty quantification by direct propagation of shallow ensembles" (arXiv 2402.16621, 2024) and Bigi, Pozdnyakov & Ceriotti, "Shallow ensembles for MLIP UQ" (J. Chem. Theory Comput. 2024).
3. **Bayesian variational dropout (BLIPs)** — competitive accuracy but adds inference cost and a probabilistic training regime. Defer.
4. **Force Delta (U_Δ) — internal disagreement in a single NNIP** — fast, data-free, single model. Promising but underspecified for energetic ΔG predictions specifically.
5. **PROBE (post-hoc reliability from backbone embeddings)** — Mehdi, Cho & Isayev 2026 (arXiv 2605.00640) — *"PROBE outperforms ensemble disagreement as a binary reliability signal, which strengthens with the expressiveness of the backbone representation."* A small classifier on frozen MLIP embeddings predicts reliability without retraining. This is the best 2026 method for OOD detection on foundation MLIPs and is what we recommend as the **secondary** check.
6. **Heterogeneous ensemble (uMLIP)** — Liu et al., *npj Comput. Mater.* 2025 — combine predictions from MACE-OMol25, UMA-M, and eSEN-S; flag when their ΔG predictions disagree by > 2 kcal/mol. **This is operationally the same as our primary recommendation** and has the advantage of being trivially implementable.

The 2 kcal/mol threshold comes from:

- The MAE of OMol25-trained MLIPs vs hybrid DFT on conformational and reaction-barrier benchmarks is ~1–2 kcal/mol on in-distribution data (Levine et al. 2025, Batatia et al. 2026 MACE-POLAR-1 reports "competitive with hybrid DFT on thermochemistry, reaction barriers, conformational energies").
- For organic reaction networks **outside the training distribution**, MAEs commonly reach 3–5+ kcal/mol per the proposal §2.5 honesty constraint and corroborated by Hill, Ruiz-Escudero & Montemore (2026, *ACS Catal.*, DOI 10.1021/acscatal.5c08168) which reports RMSEs reduced by 60% after few-shot bias correction starting from 5+ kcal/mol baselines.
- 2 kcal/mol disagreement is a defensible threshold: it's at the MAE limit of the foundation model, so disagreement above this almost certainly means OOD.

### Implementation in the certificate

When the MLIP screen runs for an edge:

```python
ensemble_dG = [m.predict_dG(reactant, product) for m in [mace_oml25, uma_m, esen_s]]
mean_dG = np.mean(ensemble_dG)
std_dG = np.std(ensemble_dG)
ood_flag = std_dG > 2.0  # threshold in kcal/mol
provenance["mlip_uncertainty_kcal_per_mol"] = std_dG
provenance["mlip_ood_flag"] = ood_flag
```

The `EnergeticsCache` entry should record `mlip_uncertainty_kcal_per_mol` (already supported via the `provenance` field but we add a structured key). An OOD-flagged edge is **automatically escalated to xtb + DFT** even if it would otherwise pass the MLIP triage.

This honours proposal §2.5: *"C must report this honestly in the certificate's `provenance` field."*

---

## 8. Proposed `data/energetics_protocol.yaml` (full draft)

```yaml
# data/energetics_protocol.yaml
#
# Layer D — production energetics-stack protocol.
# Researched against the panel and ascomylactam M5 target — see
# docs/energetics_protocol_research.md for full citations.
#
# Status: DRAFT for computational-chemist review (Workstream E deliverable).
# Locked-in version is the one consumed by macrocert.energetics.feedback at M5.

version: "1.0.0-draft"
schema_version: "1"
date: "2026-05-24"

# -------------------------------------------------------------------
# Tier escalation policy — see §1 of research doc
# -------------------------------------------------------------------
tier_escalation:
  initial_tier: mlip  # was xtb in v0

  tier_0_mlip:
    method: mace_oml25
    apply_to: all_edges_in_ir_top_n
    settings:
      backbone: mace-omol25-small  # MACE-OMol25 from fairchem; promote to medium for M5
      device: mps                  # Apple Silicon; falls back to cpu
      dtype: float64

  tier_1_xtb:
    method: gfn2_xtb
    apply_to: |
      MLIP-OOD-flagged edges (committee variance > ood_threshold_kcal_per_mol)
      OR edges within mlip_screen_window_kcal_per_mol of best_dG at tier 0
    mlip_screen_window_kcal_per_mol: 10.0

  tier_2_dft:
    method: dft
    apply_to: |
      Edges within xtb_to_dft_window_kcal_per_mol of best_dG at tier 1
      AND present in top-N IR envelope at the previous solver iteration
    xtb_to_dft_window_kcal_per_mol: 5.0

# -------------------------------------------------------------------
# MLIP settings — see §2
# -------------------------------------------------------------------
mlip:
  primary:
    model: mace-omol25-small
    package: fairchem        # or mace-torch >= 0.3.10
    weights_source: huggingface://fairchem-org/mace-omol25-small
    expected_mae_kcal_per_mol: 1.5  # vs ωB97M-V/def2-TZVPD on OMol25 evals
  backup:
    model: uma-medium
    use_when: primary_failed_to_converge or contains_transition_metal
  ood_detection:
    method: heterogeneous_ensemble
    members: [mace-omol25-small, uma-medium, esen-s]
    metric: stdev_of_dG_predictions
    threshold_kcal_per_mol: 2.0
    secondary:
      method: probe          # post-hoc reliability classifier
      reference: "Mehdi, Cho & Isayev 2026 (arXiv 2605.00640)"

# -------------------------------------------------------------------
# DFT settings — see §3
# -------------------------------------------------------------------
dft:
  package: psi4              # or qchem/orca via qcengine
  composite:
    geometry_method:    "b3lyp-d3bj/def2-svp"
    frequency_method:   "b3lyp-d3bj/def2-svp"
    single_point_method: "b3lyp-d3bj/def2-tzvp"
  dispersion: d3bj           # Grimme D3 with Becke-Johnson damping; mandatory
  reference: rks             # closed-shell singlet
  scf:
    conv: 1.0e-6
    max_iter: 250
  rationale: |
    B3LYP-D3(BJ) MAE 1.1 kcal/mol on BHPERI reaction barriers vs >1.8 for M06-2X
    and ωB97X-D (Stuyver, Jorner, Coley 2022, arXiv 2212.06014).

# -------------------------------------------------------------------
# Implicit solvent — see §5
# -------------------------------------------------------------------
solvent:
  name: dmf
  model_dft: smd            # SMD continuum, via Psi4 PCM block
  model_xtb: alpb           # GFN2-xtb ALPB
  dielectric: 36.7
  refractive_index: 1.430
  rationale: |
    DMF is the canonical macrolactamization solvent at process scale (peptide
    natural-product macrocyclisation literature, e.g. PMC 7314982). HATU/PyBOP
    activation, 1–10 mM dilution to suppress oligomerisation.
  per_rule_overrides:
    # Future hook — chemistry-team can override per-rule
    # E.g. steroidal closures may prefer toluene-at-reflux

# -------------------------------------------------------------------
# TS-search — see §4
# -------------------------------------------------------------------
ts_search:
  method: fsm                # Freezing-string method; NOT CI-NEB
  refinement: sella_prfo     # partitioned rational-function opt, Sella package
  package: sella >= 2.0      # https://github.com/zadorlab/sella
  fsm:
    nodes: 7
    spring_constant_eV_per_A: 0.1
  refinement_low_level:
    surface: mace-omol25-small
    force_tol_Ha_per_Bohr: 3.0e-3
    max_iter: 250
  refinement_high_level:
    surface: dft             # b3lyp-d3bj/def2-svp
    force_tol_Ha_per_Bohr: 3.0e-4
    max_iter: 250
  verification:
    frequency_imaginary_min_cm: 50
    frequency_imaginary_max_count: 1
    irc_required: true
    irc_method: geodesic
  rationale: |
    FSM with low-level refinement achieves 96.6% success rate on organic
    benchmarks, ~3.8 DFT gradient evaluations/reaction (Marks, Vandezande,
    Gomes 2026, arXiv 2604.00405). CI-NEB only achieves 70.8% on the same
    Baker set — a 25-point reliability gap. P-RFO via Sella.

# -------------------------------------------------------------------
# Barrier thresholds — see §6
# -------------------------------------------------------------------
thresholds:
  dG_rxn_kcal_max: 30.0      # Reaction free energy ceiling
  dG_barrier_kcal_max: 35.0  # Applied when a TS search has been done
  rationale: |
    35 kcal/mol is the Eyring-derived feasibility ceiling at room temperature
    to 100°C in solution (Shaydullin et al. 2025, Chem. Sci. 16, 5289,
    doi:10.1039/d4sc08243e). 30 kcal/mol on ΔG_rxn is conservative; covers
    canonical macrolactamization protocols (HATU/PyBOP at 0-60°C).

# -------------------------------------------------------------------
# Cache & provenance — already implemented in cache.py
# -------------------------------------------------------------------
cache:
  root: .cache/energetics
  key_inputs:
    - rule_id
    - canonical_substrate_smiles
    - canonical_product_smiles
    - tier
    - method
    - solvent_name        # NEW: solvent must be part of the key
    - dft_composite       # NEW: composite identifier ("b3lyp-d3bj+def2-svp+def2-tzvp")

# -------------------------------------------------------------------
# Feedback-loop knobs — see feedback.py
# -------------------------------------------------------------------
feedback:
  max_iterations: 5         # was 3 in v0
  time_budget_s: 300        # was 60 in v0; DFT needs more time
  blacklist_on_violation: true
  re_solve_on_new_violation: true

# -------------------------------------------------------------------
# Honesty constraints — proposal §2.5
# -------------------------------------------------------------------
honesty:
  mlip_known_mae_on_novel_networks_kcal_per_mol: 5.0
  write_provenance_field: mlip_uncertainty_kcal_per_mol
  defeasible_label_required: true   # Layer D verdicts are always advisory
```

---

## 9. Citations (DOIs / arXiv)

Primary literature underwriting these recommendations, in roughly order of importance to the protocol:

1. **Marks, Vandezande & Gomes (2026)** — "Reliable and Efficient Automated Transition-State Searches with Machine-Learned Interatomic Potentials." arXiv:2604.00405. Accepted *J. Mater. Chem. A*, 2026. — Source of TS-search method (§4), MLIP ranking (§2), tier policy (§1).
2. **Levine, Shuaibi, Spotte-Smith, … Blau & Wood (2025)** — "The Open Molecules 2025 (OMol25) Dataset, Evaluations, and Models." arXiv:2505.08762. (Meta FAIR). — Source for OMol25 training corpus underpinning §2.
3. **Kovács, Moore, Browning, … Cole, Csányi (2023, J. Am. Chem. Soc. 2024)** — "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules." DOI 10.1021/jacs.4c07099, arXiv:2312.15211. — Background for §2.
4. **Anstine, Zubatyuk & Isayev (2025)** — "AIMNet2: a neural network potential to meet your neutral, charged, organic, and elemental-organic needs." *Chem. Sci.* DOI 10.1039/d4sc08572h. — Background for §2 (AIMNet2 comparison).
5. **Batatia, Baldwin, Kuryla, … Csányi (2026)** — "MACE-POLAR-1: A Polarisable Electrostatic Foundation Model for Molecular Chemistry." arXiv:2602.19411. — Latest OMol25-trained MACE variant, basis for upgrade path.
6. **Stuyver, Jorner & Coley (2022/2023)** — "Reaction profiles for quantum chemistry-computed [3+2] cycloaddition reactions." arXiv:2212.06014; *Sci. Data*. — Source of DFT functional choice and basis composite (§3).
7. **Bursch, Mewes, Hansen & Grimme (2022)** — "Best-Practice DFT Protocols for Basic Molecular Computational Chemistry." *Angew. Chem. Int. Ed.* 61, e202205735. DOI 10.1002/anie.202205735. — Best-practice DFT for §3.
8. **Marenich, Cramer & Truhlar (2009)** — "Universal solvation model based on solute electron density." *J. Phys. Chem. B* 113, 6378. DOI 10.1021/jp810292n. — SMD foundation, §5.
9. **Shaydullin, Lyaskovskyy, … (2025)** — "Are activation barriers of 50–70 kcal mol⁻¹ accessible for transformations in organic synthesis in solution?" *Chem. Sci.* 16, 5289. DOI 10.1039/d4sc08243e. — Barrier-threshold justification, §6.
10. **Mehdi, Cho & Isayev (2026)** — "Knowing when to trust machine-learned interatomic potentials." arXiv:2605.00640 (PROBE). — Source for OOD detection §7 (secondary).
11. **Hill, Ruiz-Escudero & Montemore (2026)** — "Few-Shot Ensemble Learning for Catalysis." *ACS Catal.* DOI 10.1021/acscatal.5c08168. — UQ-via-ensembles support for §7.
12. **Staub, Harabuchi, Seraphim, Varnek & Maeda (2025)** — "An Accurate and Efficient Reaction Path Search with Iteratively Trained Neural Network Potential." *J. Chem. Theory Comput.* DOI 10.1021/acs.jctc.5c01293. — Iterative MLIP-AFIR workflow precedent, §1.
13. **Hermes, Sargsyan & Kulik (2022)** — `sella` package, P-RFO implementation. — Software for §4. https://github.com/zadorlab/sella
14. **Macrolactamization literature (review):** *Lessons from Natural Product Total Synthesis: Macrocyclization* (PMC 7893715); *Natural Cyclic Peptides* (MDPI biomedicines 2025); *Methodologies for Backbone Macrocyclic Peptide Synthesis* (PMC 7314982). — Solvent choice §5.

---

## 10. Open questions / things requiring computational-chemist review

The following decisions in this document should be confirmed by a computational chemist (e.g. a member of Coley, Kulik, or Head-Gordon's group) before locking the YAML. I have a defensible literature answer for each; the chemist's role is to override on local knowledge.

1. **MACE-OMol25 vs UMA-Medium as production primary.** Marks 2026 gives MACE-OMol25 a higher organic success rate, but UMA-Medium has a lower per-call cost (3.3 vs 3.8 gradient evals to converge). If the panel grows to include TM-catalysed steps, UMA-M should become primary. *Default: MACE-OMol25.* **Override decision needed.**

2. **DFT functional: B3LYP-D3(BJ) vs ωB97X-V vs r²SCAN-3c.** B3LYP-D3(BJ) is recommended per Stuyver/Coley benchmarking, but the Bursch/Grimme group prefers r²SCAN-3c for cheap routine calculations (composite scheme already including dispersion). r²SCAN-3c is faster and similarly accurate; some panels run it as the standard. *Default: B3LYP-D3(BJ).* **Override decision needed** (r²SCAN-3c vs B3LYP-D3(BJ) is roughly equivalent).

3. **Solvent: DMF vs DCM vs toluene per-rule.** DMF is the *peptide macrolactamization* default; but ascomylactam-class macrocycles may have particular solvent preferences from the literature on related natural products. The chemistry team should check the published synthesis of ascomylactam (or its close analogues) and override the solvent on a per-rule basis. *Default: DMF.* **Per-rule override hook is in the YAML.**

4. **Whether to also run a barrier estimate for *every* edge in the IR top-N envelope, or only for the rate-limiting candidate per route.** Running TS searches for all ~10² edges in the envelope is ~10 hours of DFT wall-time. Running them only for the top-3 candidates (post-MLIP triage) is ~1 hour. The proposal says "barrier estimates lift the bar for trusting a route, not for ruling one out." So **TS search is optional per-edge**. *Default: TS search only for the rate-limiting step of the top-1 route per IR iteration.* **Override decision needed.**

5. **Frequency calculation: harmonic only, or also include anharmonic / quasi-RRHO?** Bursch et al. recommend quasi-RRHO (Grimme's qRRHO scheme) for entropy corrections on flexible molecules. Macrocycles are by definition flexible — this matters. *Default: harmonic ZPE + Truhlar low-frequency truncation at 100 cm⁻¹.* **Override decision needed.**

6. **xtb's role: keep as fallback, or remove entirely?** If MACE-OMol25 + UMA-Medium are both available, xtb adds little (it's slower than MACE for our sizes and less accurate). Removal would simplify the protocol. *Default: keep xtb as fallback because it has no training-distribution dependence.* **Decision needed; not blocking.**

7. **Conformational sampling.** None of the current `qm.py` code generates multiple conformers; a single MMFF-optimised structure is used. For macrocycles, conformational diversity matters. Should the protocol incorporate CREST or RDKit ETKDG-based conformer sampling at the MLIP tier? *Default: out of scope for v0.* **Stretch goal for v1.**

8. **OMol25 model availability and licensing.** MACE-OMol25 is distributed via fairchem (Meta) under a non-commercial license. For non-research production use we may need MACE-OFF or UMA-Small as a permissively-licensed alternative. *Default: assume non-commercial usage is fine for the v0/M5 demo.* **Decision required if the certificate is to be shared externally.**

9. **Cache key inclusion of solvent and DFT composite.** The current `cache.py` does *not* include the solvent name or DFT composite as part of the SHA-256 key — only `rule_id`, SMILES, tier, and method. **This is a bug for production**: an entry computed in DMF and one computed in DCM would collide. The YAML in §8 lists the additional cache key fields; `cache.py` must be amended. **Action item.**

10. **Multi-reference / radical chemistry.** Layer D in v0 assumes closed-shell singlet. The ascomylactam ring closure is closed-shell, but if the rule library grows to include radical macrocyclisation (e.g. SET-coupled approaches), the protocol needs the unrestricted variant: UMA-Medium-NSE or AIMNet2-NSE for MLIP, UB3LYP-D3(BJ) for DFT. *Default: closed-shell singlet only for v0.*

---

End of research. Open items 1–4 and 9 should be settled before locking `data/energetics_protocol.yaml`. Open item 9 (cache key bug) is a code change irrespective of the protocol decision.
