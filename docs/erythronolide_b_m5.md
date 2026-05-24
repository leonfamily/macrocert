# Erythronolide B (Corey 1978) — M5 Deliverable

**Case:** `corey_erythronolide_b_macrolactonization_1978`
**Target:** Erythronolide B — the 14-membered macrolactone aglycone of erythromycin B.
**Tactic class:** Macrolactonization (Corey-Nicolaou PySSPy/PPh₃ activator).
**Authored:** 2026-05-24 (structure-encoder agent).
**Status:** **Complete.** Shortlist contains `macrolactonization` as the optimal tactic; all 12 certificates verifier-clean; panel test passes.

---

## 1. Summary

This M5 deliverable encodes the **erythronolide B macrolactonization case** as the literature anchor for the `Corey_Nicolaou` alternative in `data/rules/macrolactonization.meta.yaml`. The case directly exercises the macrolactonization rule on a stereochemically rich 14-membered polyketide macrolactone (10 sp³ stereocenters, four hydroxyls, one ketone, one ester).

**Artifacts produced:**

- `structure.mol` — built from PubChem CID 441113 isomeric SMILES; ETKDGv3 + MMFF94; openbabel-strict V2000; **C21H38O7**, MW 402.52, single 14-ring, 10 stereocenters all assigned. Replaces the placeholder.
- `data/building_blocks/erythronolide_b_seco.yaml` — derived programmatically from the cyclized target by surgically opening the C(=O)–O ester bond and capping the acyl side with –OH. **Mass balance verified**: seco exact MW = cyclized + H₂O (420.2723 = 402.2618 + 18.0106). Stereo preserved on all 10 centers.
- `runspec.yaml` — updated to point at the new structure + seco-acid block; predicates include `is_intramolecular`, `ring_size_equals: 14`, plus etherification partner-type gates.
- `expected.yaml` — corrected formula/CID/DOI; `literature_tactic: macrolactonization`, `expected_witness: optimal`, `ae_class: high`.
- `notes.md` — encoding caveats, three upstream-document corrections, activator-wiring-gap TODO.

**M5 campaign outcome:**

| Metric | Value |
| --- | --- |
| Tactics evaluated | **12** (set `all_macrocyclization`) |
| Verifier-clean certificates | **12 / 12** ✓ |
| Optimal certificates | **1** (`macrolactonization`, obj = 18.015 g/mol) |
| No-go (infeasible) certificates | **11** |
| Pipeline errors | 0 |
| Panel test (`tests/panel/test_panel.py::test_panel_case[corey_erythronolide…]`) | **PASS** (no longer skipped) |

The optimal bond-level objective **18.015 g/mol** matches the macrolactonization rule's expelled-water mass exactly (`byproduct_mass_g_per_mol: 18.015`), which independently confirms the certificate's AE accounting.

---

## 2. Corrections vs. upstream documents

Three substantive errors in the proposal / `research_brief.md` / `panel_TODO.md` were caught and corrected by this encoding pass.

### 2.1 DOI

| Source | Cited DOI | Resolves? | Correction |
| --- | --- | --- | --- |
| Proposal & `panel_TODO.md` | `10.1021/ja00482a075` | **no** (CrossRef returns empty) | Use `10.1021/ja00482a063` (Part 4, pp 4620–4622). |
| `research_brief.md` (caught upstream by Workstream B) | `10.1021/ja00482a063` | yes | already correct in brief |

The proposal's page number "4618" is the first page of **Part 3** (fragment synthesis, DOI `10.1021/ja00482a062`); the macrolactonization is **Part 4**, starting at p. 4620.

### 2.2 Molecular formula

| Source | Claim | Reality |
| --- | --- | --- |
| `research_brief.md` & `notes.md` placeholder | C₂₁H₃₈O₆, MW 386.52 | **C₂₁H₃₈O₇, MW 402.52** |

Erythronolide B has **four hydroxyls** (C3, C5, C6, C12), not three. The brief's "three β-hydroxyls" undercount drops one oxygen.

Verified by (a) PubChem name lookup → CID 441113 → C₂₁H₃₈O₇ / MW 402.52; (b) RDKit reparse of the PubChem isomeric SMILES → `CalcMolFormula = "C21H38O7"`; (c) InChIKey `ZFBRGCCVTUPRFQ-HWRKYNCUSA-N` matches the published erythronolide B record.

### 2.3 PubChem CID

| Source | Claim | Reality |
| --- | --- | --- |
| `research_brief.md` | PubChem CID 122729 | **CID 441113** (CID 122729 is rifampicin, C₃₉H₄₇NO₁₄) |

Direct lookup against `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/122729/property/...` returned the rifampicin record. The brief's downstream claim "PubChem classifies erythronolide B as a 14-membered macrolide" is correct *for the actual erythronolide B record at CID 441113*, but the wrong CID would have led to encoding a rifampicin structure.

### 2.4 Net impact

The brief's encoding caveats (10 stereocenters, 14-ring, polyketide pattern, Corey-Nicolaou activator selection, H₂O bond-level byproduct, ~80 % yield, high AE class) are all *correct in substance*. Only the formula/MW/CID identifiers were wrong. The encoded structure (this deliverable) uses the verified PubChem CID 441113 record.

---

## 3. Encoded artifacts

### 3.1 Target: `structure.mol`

Built by `scripts/build_erythronolide_b.py`:

- Source: PubChem CID 441113 isomeric SMILES.
- Canonical SMILES (RDKit, post-sanitization):
  `CC[C@H]1OC(=O)[C@H](C)[C@@H](O)[C@H](C)[C@@H](O)[C@](C)(O)C[C@@H](C)C(=O)[C@H](C)[C@@H](O)[C@H]1C`
- **Formula audit:** `C21H38O7` ✓
- **Ring inventory:** exactly one 14-membered ring ✓
- **Stereocenters:** 10 sp³, all assigned by `Chem.AssignStereochemistry` ✓
- **InChIKey:** `ZFBRGCCVTUPRFQ-HWRKYNCUSA-N` (matches PubChem) ✓
- Embedded with ETKDGv3 + random coords + MMFF94 optimization (2000 iters); written via openbabel for strict V2000 output (matches the convention of `build_ascomylactam_a.py` and the panel_lactones surrogates).

### 3.2 Seco-acid block: `data/building_blocks/erythronolide_b_seco.yaml`

Derived by `scripts/build_erythronolide_b_seco.py`:

- Finds the ring-internal C(=O)–O ester bond programmatically (the only sp³ O with both neighbours in the 14-ring, one of which is sp² with a double-bonded exocyclic O).
- Surgically removes the C(acyl)–O bond; adds a new –OH on the acyl carbon (becomes –COOH); the C13 side retains its alcohol O with implicit H.
- Canonical seco SMILES:
  `CC[C@@H](O)[C@H](C)[C@H](O)[C@@H](C)C(=O)[C@H](C)C[C@@](C)(O)[C@H](O)[C@@H](C)[C@H](O)[C@@H](C)C(=O)O`
- **Mass-balance assertion** (in the build script):
  `seco_exact_MW = cyclized_exact_MW + H₂O`
  → `420.2723 = 402.2618 + 18.0106` ✓ (delta within 1e-4)
- All 10 stereocenters preserved (the macrolactonization rule's stereo flags `retains_alpha_stereo` + `retains_alcohol_stereo` make this the right encoding).

### 3.3 RunSpec

- `target.structure_path: structure.mol`
- `target.ring_size: 14`
- `blocks: [erythronolide_b_seco]`
- `rules: all_macrocyclization`
- `strategy.max_steps: 1`, `strategy.ring_close_only: true`
- Predicates: `is_intramolecular: true`, `ring_size_equals: 14`, plus the etherification partner-type gates from the brief (`alcohol_partner_C_must_be_aromatic: {biaryl_etherification: true}`, `alcohol_partner_C_must_be_sp3: {aryl_etherification: true}`).
- `solver.backend: scip`, `solver.top_n: 10`, `solver.time_budget_s: 60`.
- `solver.extra.activator: Corey_Nicolaou` — see §4 for the wiring gap.
- `energetics.enabled: false`.

### 3.4 Expected

- `literature_tactic: macrolactonization`
- `literature_activator: Corey_Nicolaou`
- `literature_ring_size: 14`
- `expected_witness: optimal`
- `expected_top_rule_class: macrocyclization`
- `ae_class: high` (bond-level H₂O, 18.015 / 402.52 = 4.48 %)
- `reference` includes both Corey 1978 (`10.1021/ja00482a063`) and Corey-Nicolaou 1974 (`10.1021/ja00824a073`).

---

## 4. Activator wiring gap (TODO, out of scope for this M5 leg)

The `Corey_Nicolaou` activator override in `data/rules/macrolactonization.meta.yaml`:

```yaml
- name: "Corey_Nicolaou"
  reagent_mass_g_per_mol: 482.0           # PySSPy 220.31 + PPh3 262.28
  additional_byproduct_mass_g_per_mol: 389.0  # 2-mercaptopyridine 111.16 + Ph3P=O 278.28
  description: "PySSPy + PPh3, refluxing xylene. Historic; erythronolide B."
```

**Is parsed and available** in `RuleMeta.reagent_mass_alternatives` via `RuleMeta.get_alternative("Corey_Nicolaou")` (`src/macrocert/spec/rules.py:82`), but **has no consumer in the pipeline**. `grep -rn get_alternative src/` returns only the method definition; no call sites.

The runspec's `solver.extra.activator: Corey_Nicolaou` is parsed into `RunSpec.solver.extra` (a free-form dict at `src/macrocert/spec/runspec.py:88`), but no downstream code in `objective.py` / `build_dg.py` / the Layer-C composers reads it and substitutes the alternative's reagent/byproduct masses into the AE objective.

**Concrete fix (small, ~10 LOC):** in the objective construction (or wherever `rule.meta.reagent_mass_g_per_mol` is currently consumed for the process-level AE term), look up `runspec.solver.extra.get("activator")` and, when present, fetch `rule.meta.get_alternative(name)` and substitute `reagent_mass_g_per_mol` + `additional_byproduct_mass_g_per_mol`. Out of scope for this M5 leg.

**Impact on this campaign:** the bond-level chemistry (H₂O, 18.015 g/mol) is identical for Yamaguchi and Corey-Nicolaou. The optimal *bond-level* objective is **18.015 g/mol** (matches the H₂O mass; certificate is verifier-clean). Only the process-level AE penalty differs (Yamaguchi 568+362 = 930 g/mol of activator+process byproduct vs. Corey-Nicolaou 482+389 = 871 g/mol). Since `energetics.enabled: false` in v0, this difference is invisible to the current panel; for v1 with process-AE energetics, the wiring must be in place.

---

## 5. M5 campaign results

Run command:

```bash
pixi run python scripts/build_m5_campaign.py \
  data/validation_panel/corey_erythronolide_b_macrolactonization_1978
```

Per-tactic outcome (full table in `docs/M5_REPORT_corey_erythronolide_b_macrolactonization_1978.md`):

| Rule | Witness | Objective (g/mol) | Verifier |
| --- | --- | --- | --- |
| `macrolactonization` | **optimal** | **18.015** | OK |
| `macrolactamization` | infeasible | — | OK |
| `aryl_etherification` | infeasible | — | OK |
| `biaryl_etherification` | infeasible | — | OK |
| `c_h_dehydrogenative_coupling` | infeasible | — | OK |
| `rcm` | infeasible | — | OK |
| `transannular_diels_alder` | infeasible | — | OK |
| `cross_coupling_suzuki` | infeasible | — | OK |
| `cross_coupling_negishi` | infeasible | — | OK |
| `cross_coupling_buchwald` | infeasible | — | OK |
| `cross_coupling_sonogashira` | infeasible | — | OK |
| `cross_coupling_stille` | infeasible | — | OK |

**Shortlist (1 optimal tactic):**

1. **`macrolactonization`** — objective 18.015 g/mol; certificate verifier-clean.

**No-go certificates (11 ruled-out tactics):** each is verifier-clean with an IIS that includes `exactly_one_macrocyclization`, the seco-acid flow constraint, the target macrolactone flow constraint, and `step_budget`. The verifier confirms that no other rule can produce the target from the seco-precursor under the runspec's `ring_size_equals: 14` + `is_intramolecular: true` predicates.

The optimal tactic equals the literature tactic — this case validates that the macrocert pipeline correctly identifies the Corey 1978 macrolactonization disconnection from an open-form seco-acid precursor when the macrolactonization rule and the matching ring-size predicate are in scope.

---

## 6. Reproducibility note

A flaky-embedding behaviour was observed during this run: the macrolactonization leg of the M5 campaign initially produced `infeasible` (the MØD `Result subset has 0 graphs` path), and a clean re-run after warming the artifacts cache produced the optimal `Result subset has 5 graphs` certificate. The same flakiness was visible on the simpler surrogate `lactone_14_from_13_hydroxytridecanoic_acid`. The non-determinism appears to be in MØD's geometry-finalization step (multiple `WARNING: No viable geometries for O with bonds S = 2` lines preceding the `Round 1` count). The final results in this report (1 optimal + 11 no-go) are stable across the last several reruns; if a future CI run shows the macrolactonization leg flipping to `infeasible`, the fix is to delete `artifacts/<case>/` and re-run.

Recommended follow-up: deterministic MØD geometry seeding (`mod.Mod.config(...)` or per-rule `seed: ...`), or pin the MØD random seed at the campaign-script level.

---

## 7. Validation checklist

- [x] `structure.mol` is no longer a placeholder. The placeholder gate in `tests/panel/test_panel.py::_is_placeholder_structure` (looks for `# PLACEHOLDER` as the first non-whitespace token) no longer matches.
- [x] `pixi run pytest tests/panel/ -q -k corey_erythronolide` **passes** (no longer skipped).
- [x] All 12 M5-campaign certificates are independently verifier-clean (`pixi run macrocert-verify` returns exit 0 for every cert).
- [x] Shortlist contains `macrolactonization` as the optimal tactic with bond-level objective 18.015 g/mol.
- [x] Mass-balance assertion `seco = cyclized + H₂O` holds to <1e-4 g/mol.
- [x] Stereocenter count = 10 in both the cyclized target and the derived seco-acid.
- [x] Ring inventory: exactly one 14-membered ring in the target.
- [x] InChIKey of the encoded target (`ZFBRGCCVTUPRFQ-HWRKYNCUSA-N`) matches the published erythronolide B InChIKey.
- [x] All upstream document errors (DOI, formula, CID) caught and corrected in `notes.md` and `expected.yaml`.

---

## 8. Files touched

| Path | Change |
| --- | --- |
| `data/validation_panel/corey_erythronolide_b_macrolactonization_1978/structure.mol` | Placeholder → real V2000 (built from PubChem CID 441113). |
| `data/validation_panel/corey_erythronolide_b_macrolactonization_1978/runspec.yaml` | Block ID, predicates, activator extra, formula-correction note. |
| `data/validation_panel/corey_erythronolide_b_macrolactonization_1978/expected.yaml` | Formula/CID/DOI corrections. |
| `data/validation_panel/corey_erythronolide_b_macrolactonization_1978/notes.md` | Encoding caveats, corrections, activator-wiring-gap TODO. |
| `data/building_blocks/erythronolide_b_seco.yaml` | **New** seco-acid block (derived programmatically). |
| `scripts/build_erythronolide_b.py` | **New** — RDKit ETKDG/MMFF + openbabel V2000 (mirrors `build_ascomylactam_a.py`). |
| `scripts/build_erythronolide_b_seco.py` | **New** — surgical ester-bond opening + mass-balance verification. |
| `docs/M5_REPORT_corey_erythronolide_b_macrolactonization_1978.md` | Auto-generated by `build_m5_campaign.py`. |
| `docs/erythronolide_b_m5.md` | **This deliverable.** |

---

## 9. Open items (handoff)

1. **Activator-override wiring.** `solver.extra.activator: Corey_Nicolaou` needs a consumer in the objective/AE builder. See §4 for the proposed fix shape. Blocks v1 (process-AE energetics) but not v0. Once wired, the Corey-Nicolaou-vs-Yamaguchi process-AE delta (871 vs 930 g/mol) becomes visible in the certificate's AE term — this is the case's main scientific point and should be validated end-to-end at v1.
2. **MØD geometry-seeding non-determinism.** §6 above. Surfaces as flaky macrolactonization-leg results; mitigated by clean reruns. Worth a one-hour fix to pin the MØD seed at campaign-script level.
3. **Panel test now exercises real chemistry.** `tests/panel/test_panel.py::test_panel_case[corey_erythronolide…]` was previously skipped (placeholder structure); it now runs through the full pipeline and asserts that the optimal route uses `macrolactonization`. If CI flakes on this leg, see §6.
