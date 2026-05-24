# Cytochalasin B M5 Campaign Report

**Case:** `haidle_myers_cytochalasin_b_2004`
**Target:** Cytochalasin B (PubChem CID 5311281, ChEBI:23528, CAS 14930-96-2)
**Reference:** Haidle, A. M.; Myers, A. G. *Proc. Natl. Acad. Sci. USA* **2004**, *101*, 12048–12053. DOI: [`10.1073/pnas.0402111101`](https://doi.org/10.1073/pnas.0402111101) (PMC PMC514432, open access).
**Date:** 2026-05-24
**Status:** ✅ M5 campaign clean — 13/13 verifier-clean certificates; `hwe_olefination` is the unique optimal tactic.

---

## 1. Summary

Two-phase Workstream C deliverable:

1. **Rule encoding** — a new DPO rule `hwe_olefination` (data/rules/hwe_olefination.{gml,meta.yaml}) covering intramolecular Horner–Wadsworth–Emmons olefination of a β-keto-phosphonate (or phosphonoacetate ester) with a tethered aldehyde. Closes a macrocyclic C=C alkene at the bond level and expels dialkyl phosphate (canonical: dimethyl `(MeO)₂P(O)OH`, 126.05 g/mol). Eight activator variants encoded in `reagent_mass_alternatives` (canonical NaH/dimethyl, KHMDS, Masamune–Roush LiCl/DBU, Haidle–Myers NaOCH₂CF₃, Still–Gennari Z, Ando Z, Ando macrocyclic Z, Nagorny Zn). Conservation re-check: **13/13 rules pass** under `pixi run check-rules`.

2. **Panel case** — `haidle_myers_cytochalasin_b_2004` is now fully encoded with:
   - **structure.mol** built from the PubChem CID 5311281 isomeric SMILES via RDKit ETKDGv3 + MMFF94 → openbabel V2000. Formula C₂₉H₃₇NO₅, MW 479.62, rings = [5, 6, 6, 14] (γ-lactam isoindolone + cyclohexane + phenyl + 14-membered macrolactone), 8 stereocenters, two E-alkenes in the 14-ring. 3D embedding succeeded on first attempt.
   - **seco precursor** `data/building_blocks/cytochalasin_b_seco.yaml`: the α,β-unsaturated ester C=C is broken; α-side gets `-P(=O)(OCH₃)₂` (canonical dimethyl phosphonate variant), β-side gets `=O` (aldehyde). Mass balance verified: Δ MW (avg) = **126.05 g/mol**, Δ MW (exact) = **126.008 g/mol** = `(MeO)₂P(O)OH` byproduct.
   - **M5 campaign**: 13 tactics (full `all_macrocyclization` sweep) → **1 optimal** (`hwe_olefination`, objective 126.050 g/mol) + **12 no-go** infeasibility certificates. Every certificate independently verifier-clean.

---

## 2. Chemistry

The Haidle–Myers synthesis closes cytochalasin B's 14-membered macrolactone by intramolecular HWE olefination of the seco-precursor (compound 3 in Scheme 7 of the paper):

$$
\text{(MeO)}_2\text{P(O)}\!-\!\text{CH}_2\!-\!\text{C(=O)}\!-\!\text{O}\!-\!R'\!-\!...\!-\text{CHO}
\;\xrightarrow{\text{NaOCH}_2\text{CF}_3,\ \text{CF}_3\text{CH}_2\text{OH/DME, 23 °C}}\;
\text{macrolactone-}C=C\text{ (E)} \;+\; (\text{MeO})_2\text{P(O)OH}
$$

Yield: **65%**, single (E) diastereomer with α-C18 stereocenter preserved. The trifluoroethoxide / trifluoroethanol system (the "Haidle–Myers conditions" — encoded as the `haidle_myers` activator in the rule's meta) suppresses α-epimerization that would occur under strong amine base on the L-696,474 11-ring case at 80 °C.

The new in-ring bond is `C13=C14` per the cytochalasan numbering; the other in-ring alkene (C20=C21, also E) was preformed in the seco precursor and is preserved across HWE.

---

## 3. Build provenance

| Artifact | Built by | Audits |
|---|---|---|
| `data/rules/hwe_olefination.gml` | hand-written from `docs/hwe_olefination_research.md` §2.5 / §10 | Conservation re-check: balanced; 13 rule(s) pass under `pixi run check-rules` |
| `data/rules/hwe_olefination.meta.yaml` | hand-written from §9 of the research brief | 8 activator variants; byproduct_mass_g_per_mol = 126.05; retained_root_atom = 1 |
| `data/validation_panel/haidle_myers_cytochalasin_b_2004/structure.mol` | `scripts/build_cytochalasin_b.py` | C₂₉H₃₇NO₅ ✓; rings [5,6,6,14] ✓; 8 stereocenters ✓; 2× E alkenes in 14-ring ✓; 3D ETKDG+MMFF |
| `data/building_blocks/cytochalasin_b_seco.yaml` | `scripts/build_cytochalasin_b_seco.py` | Δ MW (avg) = 126.05 ✓; Δ MW (exact) = 126.008 ✓; ring sizes [5,6,6] ✓ (14-ring opened) |
| `docs/M5_REPORT_haidle_myers_cytochalasin_b_2004.md` | `scripts/build_m5_campaign.py` | 1 optimal + 12 no-go; every certificate verifier-clean |

---

## 4. Rule-set membership

Updated `data/rules/_index.yaml`:

- **`all_macrocyclization`** — added `hwe_olefination` (13 tactics total).
- **`high_ae_macrocyclization`** — added `hwe_olefination` (judgment call documented inline). The 126 g/mol byproduct is heavier than the H₂O/HF/H₂ high-AE family but lighter than the cross-coupling threshold (>140 g/mol Suzuki/Negishi/Stille). Both alkene carbons come from the substrate; no transition-metal catalyst.

---

## 5. M5 campaign outcome

| Rule | Witness | Objective (g/mol) | Verifier |
|------|---------|-------------------|----------|
| `hwe_olefination` | **optimal** | 126.050 | ✓ |
| `macrolactamization` | infeasible | — | ✓ |
| `macrolactonization` | infeasible | — | ✓ |
| `aryl_etherification` | infeasible | — | ✓ |
| `biaryl_etherification` | infeasible | — | ✓ |
| `c_h_dehydrogenative_coupling` | infeasible | — | ✓ |
| `rcm` | infeasible | — | ✓ |
| `transannular_diels_alder` | infeasible | — | ✓ |
| `cross_coupling_suzuki` | infeasible | — | ✓ |
| `cross_coupling_negishi` | infeasible | — | ✓ |
| `cross_coupling_buchwald` | infeasible | — | ✓ |
| `cross_coupling_sonogashira` | infeasible | — | ✓ |
| `cross_coupling_stille` | infeasible | — | ✓ |

**13/13 certificates verifier-clean.** The shortlist contains exactly one tactic (`hwe_olefination`) with objective 126.050 g/mol — matching the rule's bond-level byproduct mass exactly.

The 12 no-go certificates each carry an IIS (Irreducible Infeasible Subsystem) showing that no other rule's L-pattern matches the seco-precursor's α-aldehyde + phosphonoacetate functional groups under the strategy predicates (`is_intramolecular: true`, `ring_size_equals: 14`).

---

## 6. Panel test

The `tests/panel/test_panel.py::test_panel_case[haidle_myers_cytochalasin_b_2004]` test:

- Previously **skipped** under the Workstream B placeholder detector (`structure.mol` began with `# PLACEHOLDER`).
- Now **passes** after the structure encoding lands: the campaign runs to completion, the certificate's witness is `optimal`, and `hwe_olefination` is the rule_id of the top route's used edge — matching the `literature_tactic: hwe_olefination` in `expected.yaml`.

```
$ pixi run pytest tests/panel/ -q -k haidle
.                                                                        [100%]
1 passed, 16 deselected
```

---

## 7. Citations & references

All citations have DOIs (per the vault's wiki-link-every-paper rule):

- **Wadsworth, W. S.; Emmons, W. D.** *J. Am. Chem. Soc.* **1961**, *83*, 1733. DOI: [`10.1021/ja01468a042`](https://doi.org/10.1021/ja01468a042) — original HWE.
- **Boutagy, J.; Thomas, R.** *Chem. Rev.* **1974**, *74*, 87. DOI: [`10.1021/cr60287a005`](https://doi.org/10.1021/cr60287a005) — mechanism review.
- **Still, W. C.; Gennari, C.** *Tetrahedron Lett.* **1983**, *24*, 4405. DOI: [`10.1016/S0040-4039(00)85909-2`](https://doi.org/10.1016/S0040-4039(00)85909-2) — Z-selective HWE.
- **Masamune, S.; Blanchette, M. A.; Choy, W.; Davis, J. T.; Essenfeld, A. P.; Sato, F.; Roush, W. R.** *Tetrahedron Lett.* **1984**, *25*, 2183. DOI: [`10.1016/S0040-4039(01)80205-7`](https://doi.org/10.1016/S0040-4039(01)80205-7) — LiCl/amine mild HWE.
- **Ando, K.** *J. Org. Chem.* **1997**, *62*, 1934. DOI: [`10.1021/jo970057c`](https://doi.org/10.1021/jo970057c) — Z-selective diaryl phosphonate.
- **Haidle, A. M.; Myers, A. G.** *Proc. Natl. Acad. Sci. USA* **2004**, *101*, 12048. DOI: [`10.1073/pnas.0402111101`](https://doi.org/10.1073/pnas.0402111101) — cytochalasin B / L-696,474, primary reference for this case.
- **Ando, K.; Narumiya, K.; Takada, H.; Teruya, T.** *Org. Lett.* **2010**, *12*, 1460. DOI: [`10.1021/ol100071d`](https://doi.org/10.1021/ol100071d) — Z-selective macrolactone HWE.
- **Ando, K.; Sato, K.** *Tetrahedron Lett.* **2011**, *52*, 1284. DOI: [`10.1016/j.tetlet.2011.01.043`](https://doi.org/10.1016/j.tetlet.2011.01.043) — 13–18 membered Z-cyclic alkene HWE.
- **Larsen, B. J.; Sun, Z.; Nagorny, P.** *Org. Lett.* **2013**, *15*, 2998. DOI: [`10.1021/ol401186f`](https://doi.org/10.1021/ol401186f) — Zn(II)-mediated HWE macrocyclization (lactimidomycin).
- **Bisceglia, J. A.; Orelli, L. R.** *Curr. Org. Chem.* **2015**, *19*, 744. DOI: [`10.2174/1385272819666150311231006`](https://doi.org/10.2174/1385272819666150311231006) — HWE review.
- **Kobayashi, K.; Tanaka, K.; Kogen, H.** *Tetrahedron Lett.* **2018**, *59*, 568. DOI: [`10.1016/j.tetlet.2017.12.076`](https://doi.org/10.1016/j.tetlet.2017.12.076) — recent HWE in NP synthesis.
- **Skellam, E.** *Nat. Prod. Rep.* **2017**, *34*, 1252. DOI: [`10.1039/c7np00036g`](https://doi.org/10.1039/c7np00036g) — cytochalasan biosynthesis (corrected DOI; task brief had `10.1039/c7np00045f` which is a different paper).

Structural data: PubChem CID 5311281, ChEBI:23528, CAS 14930-96-2.
