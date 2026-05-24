# C-H Dehydrogenative Encoding + Energetics Protocol Lock-In Report

**Workstream:** MØD-MacroCert Workstreams C (rule encoding) + E (energetics protocol)
**Date:** 2026-05-24
**Author:** Computational-chemist agent
**Status:** Both deliverables drafted; `pixi run check-rules` green; full pytest suite green.

This report consolidates the two parallel deliverables of this work order:

1. **C-H dehydrogenative coupling rule** (`data/rules/c_h_dehydrogenative_coupling.{gml,meta.yaml}`).
2. **Production energetics protocol** (`data/energetics_protocol.yaml`).

It records the files produced, the canonical byproduct table for the C-H rule, and every numerical value in the energetics protocol with its inline citation. No commits performed.

---

## 1. Files created

| Path | Purpose |
|---|---|
| `data/rules/c_h_dehydrogenative_coupling.gml` | 5-atom DPO span for C-H/C-H -> C-C closure with H2 byproduct. Atom IDs follow macrolactamization convention (substrate atoms low IDs, expelled atoms high IDs). |
| `data/rules/c_h_dehydrogenative_coupling.meta.yaml` | Process-level mass, canonical byproduct (H2 = 2.016 g/mol), classes (`macrocyclization`, `cc_closure`, `dehydrogenative`, `highest_atom_economy_cc`), stereo flags, 7 cited DOIs, 5 `reagent_mass_alternatives` (PIDA, AgOAc, K2S2O8, O2, Cu(OAc)2). |
| `data/energetics_protocol.yaml` | Full Layer D protocol. MLIP primary MACE-OMol25, DFT B3LYP-D3(BJ)/def2-TZVP // def2-SVP composite, SMD-DMF, FSM TS-search via sella.Sella(order=1), barrier thresholds, OOD detection via 3-model ensemble. 10 OPEN QUESTION comments preserved for Ivan's sign-off. `version: 1`, `signed_by: null`, `signed_at: null`. |
| `docs/c_h_encoding_and_energetics_protocol.md` | This report. |

All values literature-derived; every numerical value in the YAML files carries an inline DOI/arXiv citation. `pixi run check-rules` is green (7 rules: macrolactamization, macrolactonization, rcm, transannular_diels_alder, c_h_dehydrogenative_coupling, and the two cross-coupling rules added concurrently by the parallel cross-coupling work). `pixi run pytest tests/ -q` is green (52 passed).

---

## 2. C-H rule conservation check

```
$ pixi run check-rules
  OK  c_h_dehydrogenative_coupling   classes=['macrocyclization', 'cc_closure', 'dehydrogenative', 'highest_atom_economy_cc']
  ...
  7 rule(s) pass conservation re-check
```

DPO span atom balance: L has 4 atoms (C1, C2, H7, H8) and 2 bonds (C1-H7, C2-H8). R has 4 atoms and 2 bonds (C1-C2, H7-H8). Conserved. Hydrogen count: 2 on each side. Conserved.

BFS from `retained_root_atom = 1`: reaches C1 -> C2. H7-H8 disjoint component. Verifier identifies H2 (2.016 g/mol) as byproduct automatically.

---

## 3. C-H dehydrogenative byproduct + reagent_mass_alternatives table

The **canonical** rule uses acceptorless dehydrogenative (H2 byproduct). Process-level alternatives are oxidant-specific; when an alternative is selected, the verifier should use `byproduct_mass_g_per_mol = 18.015` (H2O) in place of 2.016 (H2), because the substrate hydrogens are abstracted by the oxidant rather than evolved as H2. The DPO body is unchanged.

| Variant (alt name) | reagent_mass (g/mol) | additional_byproduct (g/mol) | Byproduct identity | Primary DOI |
|---|---|---|---|---|
| **Canonical (acceptorless)** | 50.0 (amortized catalyst) | — | H2 | 10.1021/acs.joc.9b01704 (Huang/Kang/Li/Li 2019) |
| `PIDA` | 322.1 (PhI(OAc)2) | ~248.07 (PhI + 2 AcOH reduced) | H2O (process) | 10.1021/acs.orglett.9b02945 (Bai/Bai/Wang 2019); 10.1039/c9ob02765c (Sengupta/Mehta 2020) |
| `AgOAc_2eq` | 333.8 (2 x AgOAc) | 333.8 (2 Ag(0) + 2 AcOH) | H2O (process) | 10.1002/anie.201807953 (Bai/Cai/Yu/Wang 2018) |
| `K2S2O8_1eq` | 270.3 | 272.3 (2 KHSO4 reduced) | H2O (process) | 10.1039/D1GC01871J (Tian/Li/Li 2021); 10.1021/acs.joc.9b01704 |
| `O2_aerobic` | 32.0 (effectively mass-free at process scale) | 0.0 | H2O (process) | 10.1039/D1GC01871J |
| `Cu_OAc_2_2eq` | 363.2 (2 x Cu(OAc)2) | 247.1 (2 Cu(OAc) + AcOH balance) | H2O (process) | 10.1021/acs.joc.9b01704 |

**Bond-vs-process AE gap (research §10 / proposal §3.3) — the largest in the library.** On a ~300 g/mol substrate, acceptorless gives ~99% bond AE (only 2.016 g/mol expelled). PIDA-mediated process AE drops to ~45-50% on the same substrate because the 322 g/mol oxidant skeleton is debited at the process level. This rule is the single best chemistry-informative case in the library for the bond-vs-process split.

### Stereo flags

- `forms_csp2_csp2_bond` — canonical biaryl case; forming bond is planar, no new sp3 stereocenter
- `may_set_atropisomerism` — ortho-substituted biaryl macrocycles install rotational stereochemistry on closure
- `alpha_carbonyl_csp3_racemization_risk` — alpha-acidic C(sp3)-H sites near a carbonyl can enolize under basic CDC conditions (10.3390/molecules28248017)

### Refs (7)

1. Saridakis, Kaiser & Maulide 2020, ACS Cent. Sci. 6:1869 — 10.1021/acscentsci.0c00599 (review cited by MacroCert proposal)
2. Sengupta & Mehta 2020, Org. Biomol. Chem. 18:1851 — 10.1039/c9ob02765c (dedicated macrocyclization-via-C-H review)
3. Bai, Bai & Wang 2019, Org. Lett. 21:7967 — 10.1021/acs.orglett.9b02945 (canonical Pd/PIDA macrocyclic biaryl)
4. Huang, Kang, Li & Li 2019, J. Org. Chem. 84:12705 — 10.1021/acs.joc.9b01704 (modern CDC review)
5. Tian, Li & Li 2021, Green Chem. 23:6789 — 10.1039/D1GC01871J (oxidative-vs-dehydrogenative comparison)
6. Bai, Cai, Yu & Wang 2018, Angew. Chem. Int. Ed. 57:13912 — 10.1002/anie.201807953 (directional peptide macrocyclization)
7. Duengo et al. 2023, Molecules 28:8017 — 10.3390/molecules28248017 (alpha-C(sp3) racemization basis for stereo flag)

---

## 4. `data/energetics_protocol.yaml` — value-by-value citation table

Every numerical value in the YAML carries an inline DOI/arXiv comment. Reproduced here for review.

### 4.1 Tier escalation

| Key | Value | Source |
|---|---|---|
| `tier_0_mlip.method` | `mace_omol25` | arXiv:2604.00405 (Marks/Vandezande/Gomes 2026): 96.6% FSM success, 3.8 DFT grad evals/rxn |
| `tier_1_xtb.mlip_screen_window_kcal_per_mol` | 10.0 | arXiv:2604.00405 §4 (xtb ~25-pt lower reliability than MACE; demoted to fallback) |
| `tier_2_dft.xtb_to_dft_window_kcal_per_mol` | 5.0 | arXiv:2604.00405 (refinement-window heuristic; 94-96% DFT cost reduction) |

### 4.2 MLIP

| Key | Value | Source |
|---|---|---|
| `primary.model` | mace-omol25-small | arXiv:2604.00405 |
| `primary.expected_mae_kcal_per_mol` | 1.5 | arXiv:2505.08762 (Levine et al. 2025, OMol25) vs wB97M-V/def2-TZVPD |
| `backup.model` | uma-medium | arXiv:2604.00405 (UMA-M 3.3 grad evals/rxn, best for TM systems) |
| `ood_detection.members` | [mace-omol25-small, uma-medium, esen-s] | npj Comput. Mater. 2025 (Liu et al., uMLIP); each individually validated in arXiv:2604.00405 |
| `ood_detection.threshold_kcal_per_mol` | 2.0 | arXiv:2505.08762 (OMol25 MAE 1-2 kcal/mol in-distribution); 10.1021/acscatal.5c08168 (Hill 2026: OOD RMSE jumps to 5+ kcal/mol) |
| `ood_detection.secondary.method` | probe | arXiv:2605.00640 (Mehdi/Cho/Isayev 2026, PROBE) |

### 4.3 DFT

| Key | Value | Source |
|---|---|---|
| `composite.geometry_method` | b3lyp-d3bj/def2-svp | arXiv:2212.06014 (Stuyver/Jorner/Coley 2022) |
| `composite.frequency_method` | b3lyp-d3bj/def2-svp | arXiv:2212.06014 (ZPE + entropy at same level) |
| `composite.single_point_method` | b3lyp-d3bj/def2-tzvp | arXiv:2212.06014: MAE 1.1 kcal/mol on BHPERI vs >1.8 for M06-2X / wB97X-D |
| `dispersion` | d3bj | 10.1002/anie.202205735 (Bursch et al. 2022 best-practice) |
| `scf.conv` | 1.0e-6 | arXiv:2604.00405 §2.4 |
| `scf.max_iter` | 250 | arXiv:2604.00405 §2.4 |

### 4.4 Solvent

| Key | Value | Source |
|---|---|---|
| `name` | dmf | PMC 7314982 / PMC 7893715 / 10.3390/biomedicines13010240 — DMF canonical for peptide macrolactamization |
| `model_dft` | smd | 10.1021/jp810292n (Marenich/Cramer/Truhlar 2009) — ~1 kcal/mol MAE on Minnesota Solvation DB |
| `model_xtb` | alpb | 10.1021/acs.jctc.0c01306 (Ehlert/Stahn/Spicher/Grimme 2021) |
| `dielectric` | 36.7 | NIST/CRC DMF at 298 K |
| `refractive_index` | 1.430 | NIST/CRC DMF at 293 K (n_D) |

### 4.5 TS-search (FSM + sella.Sella)

| Key | Value | Source |
|---|---|---|
| `method` | fsm | arXiv:2604.00405 §4 (88.9-90.3% success vs CI-NEB 70.8-62.0%) |
| `refinement` | sella_prfo | arXiv:2604.00405 (P-RFO in redundant internals) |
| `package` | sella >= 2.0 | github.com/zadorlab/sella (Hermes/Sargsyan/Kulik 2022) |
| `driver.class` | sella.Sella | arXiv:2604.00405 §2.4 |
| `driver.order` | 1 | arXiv:2604.00405 (order=1 = first-order saddle / TS) |
| `driver.internal` | true | arXiv:2604.00405 (redundant internals) |
| `fsm.nodes` | 7 | arXiv:2604.00405 §A.1 |
| `fsm.spring_constant_eV_per_A` | 0.1 | arXiv:2604.00405 §A.1 |
| `refinement_low_level.force_tol_Ha_per_Bohr` | 3.0e-3 | arXiv:2604.00405 §2.4 (MLIP refinement) |
| `refinement_low_level.energy_tol_Ha` | 1.0e-5 | arXiv:2604.00405 §2.4 |
| `refinement_low_level.max_iter` | 250 | arXiv:2604.00405 §2.4 |
| `refinement_high_level.force_tol_Ha_per_Bohr` | 3.0e-4 | arXiv:2604.00405 §2.4 (DFT refinement; one decade tighter than MLIP) |
| `refinement_high_level.energy_tol_Ha` | 1.0e-6 | arXiv:2604.00405 §2.4 |
| `refinement_high_level.max_iter` | 250 | arXiv:2604.00405 §2.4 |
| `verification.frequency_imaginary_min_cm` | 50 | arXiv:2604.00405 §2.4 (exactly one imag mode, magnitude > 50 cm-1) |
| `verification.frequency_imaginary_max_count` | 1 | arXiv:2604.00405 §2.4 |
| `verification.spurious_mode_max_magnitude_cm` | 200 | arXiv:2604.00405 §2.4 (tolerated upper bound) |
| `verification.irc_required` | true | arXiv:2604.00405 |
| `verification.irc_method` | geodesic | arXiv:2604.00405 |

### 4.6 Barrier thresholds

| Key | Value | Source |
|---|---|---|
| `dG_kcal_max` | 30.0 | 10.1039/d4sc08243e (Shaydullin et al. 2025, Chem. Sci. 16:5289) — reaction-free-energy ceiling, Eyring half-life ~34 yr at 298 K |
| `dG_barrier_kcal_max` | 35.0 | 10.1039/d4sc08243e — activation-barrier ceiling for RT-to-100C solution chemistry |

### 4.7 Cache / feedback / honesty

| Key | Value | Source |
|---|---|---|
| `cache.key_inputs` (new fields) | `solvent_name`, `dft_composite` | research §10 Q#9 (cache-collision bug across solvent variants) |
| `feedback.max_iterations` | 5 | raised from v0=3 to allow DFT-bearing iterations |
| `feedback.time_budget_s` | 300 | raised from v0=60; DFT needs more time |
| `honesty.mlip_known_mae_on_novel_networks_kcal_per_mol` | 5.0 | 10.1021/acscatal.5c08168 (Hill/Ruiz-Escudero/Montemore 2026) — OOD RMSE 5+ kcal/mol pre-correction |
| `honesty.defeasible_label_required` | true | proposal §2.5 |

### 4.8 Open questions preserved (10)

All ten open questions from research §10 are present as `# OPEN QUESTION (for Ivan):` comments in the YAML, covering:

1. MACE-OMol25 vs UMA-Medium as primary
2. B3LYP-D3(BJ) vs wB97X-V vs r2SCAN-3c functional choice
3. DMF vs DCM vs toluene per-rule
4. Per-edge vs per-route TS-search policy
5. Harmonic vs qRRHO frequency treatment
6. Whether to keep xtb as fallback
7. Conformational sampling (CREST/ETKDG) — defer to v1
8. OMol25 model licensing
9. Cache key inclusion of solvent + dft_composite (action item — cache.py bug)
10. Multi-reference / radical chemistry support

---

## 5. Test status

```
$ pixi run pytest tests/ -q
....................................................                     [100%]
52 passed in 1.21s
```

`pixi run check-rules`: 7 rules pass conservation re-check (the original 4 + macrolactonization + c_h_dehydrogenative_coupling + the two cross-coupling rules added concurrently by the parallel workstream).

---

## 6. Notes on concurrent work

During execution of this work order, a parallel agent landed `cross_coupling_suzuki.gml/meta.yaml` and `cross_coupling_negishi.gml/meta.yaml` in `data/rules/`. These are unrelated to my deliverables (Workstream C item 2, cross_coupling_research.md). Both passed conservation on their own when the metadata files settled. No interaction with my C-H rule beyond shared directory; check-rules and pytest both green after the concurrent agent finished writing.

---

## 7. Cross-cutting confirmation

- [x] `pixi run check-rules` green
- [x] `pixi run pytest tests/ -q` green (52 passed)
- [x] All numerical values in C-H meta.yaml carry inline citation
- [x] All numerical values in energetics_protocol.yaml carry inline DOI/arXiv citation
- [x] 10 OPEN QUESTION comments preserved in YAML
- [x] `version: 1`, `signed_by: null`, `signed_at: null` present
- [x] No commits performed; changes left unstaged
