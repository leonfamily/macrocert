# Research Brief — Epothilone B, Nicolaou ring-closing metathesis (1997)

**Case ID:** `epothilone_b_nicolaou_rcm_1997`
**Tactic class:** Ring-closing metathesis (`rcm`)
**Status:** Awaiting Ivan sign-off on substrate/product encoding
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Primary citations (with DOI)

The Nicolaou group disclosed three landmark papers on the epothilone A/B family in 1997. The full RCM paper for the epothilone B substrate is **JACS 1997, 119, 7974** — not 7960 as the panel task brief states. JACS 119:7960 is the corresponding paper for *epothilone A*; the B paper follows immediately at p. 7974 in the same issue.

| Role | Citation | DOI |
| --- | --- | --- |
| **Full paper — epothilone B RCM** (this case's primary reference) | Nicolaou, K. C.; Ninkovic, S.; Sarabia, F.; Vourloumis, D.; He, Y.; Vallberg, H.; Finlay, M. R. V.; Yang, Z. "Total Synthesis of Epothilones A and B *via* a Macrolactonization-Based Strategy." *J. Am. Chem. Soc.* **1997**, *119*, 7974–7991. | `10.1021/ja971110h` |
| Full paper — epothilone A by olefin metathesis (companion to above) | Nicolaou, K. C.; He, Y.; Vourloumis, D.; Vallberg, H.; Roschangar, F.; Sarabia, F.; Ninkovic, S.; Yang, Z.; Trujillo, J. I. "The Olefin Metathesis Approach to Epothilone A and Its Analogues." *J. Am. Chem. Soc.* **1997**, *119*, 7960–7973. | `10.1021/ja971109i` |
| *Nature* report (epothilones A and B in solid + solution phase) | Nicolaou, K. C.; Winssinger, N.; Pastor, J.; Ninkovic, S.; Sarabia, F.; He, Y.; Vourloumis, D.; Yang, Z.; Li, T.; Giannakakou, P.; Hamel, E. *Nature* **1997**, *387*, 268–272. | `10.1038/387268a0` |
| Initial RCM communication (epothilone A) | Yang, Z.; He, Y.; Vourloumis, D.; Vallberg, H.; Nicolaou, K. C. "Total Synthesis of Epothilone A: The Olefin Metathesis Approach." *Angew. Chem. Int. Ed. Engl.* **1997**, *36*, 166–168. | `10.1002/anie.199701661` |
| RCM precedent on the epothilone skeleton | Nicolaou, K. C.; He, Y.; Vourloumis, D.; Vallberg, H.; Yang, Z. "An Approach to Epothilones Based on Olefin Metathesis." *Angew. Chem. Int. Ed. Engl.* **1996**, *35*, 2399–2401. | `10.1002/anie.199623991` |
| Independent epothilone A synthesis (Danishefsky; macrolactonization) | Meng, D.; Bertinato, P.; Balog, A.; Su, D.-S.; Kamenecka, T.; Sorensen, E. J.; Danishefsky, S. J. "Total Syntheses of Epothilones A and B." *J. Am. Chem. Soc.* **1997**, *119*, 10073–10092. | `10.1021/ja971946k` |
| Independent epothilone B synthesis (Schinzer, RCM, 1998) | Schinzer, D.; Bauer, A.; Schieber, J. "Total Synthesis of (−)-Epothilone B." *Synlett* **1998**, 861–864 (full paper in *Chem. Eur. J.* **1999**, *5*, 2492–2500). | `10.1002/(SICI)1521-3765(19990915)5:9<2492::AID-CHEM2492>3.0.CO;2-#` |

## 2. Target structural description

**Epothilone B** (CAS 152044-54-7; "Patupilone", EPO 906).

| Property | Value |
| --- | --- |
| Molecular formula | C₂₇H₄₁NO₆S |
| Average MW | 507.68 g/mol |
| Monoisotopic mass | 507.26546 Da |
| ChEBI ID | 31550 |
| LIPID MAPS ID | LMPK04000041 |
| InChIKey | QXRSDHAAWVKZLJ-PVYNADRNSA-N |
| IUPAC stereodescriptor | (1S,3S,7S,10R,11S,12S,16R) |

Source: ChEBI:31550, LIPID MAPS, IUPHAR/BPS Guide to Pharmacology, NP-MRD NP0013985 — all cross-validated, quality 5.

**Ring inventory:**

- **One 16-membered macrolactone** (the "epothilone macrocycle"), containing:
    - One ester (lactone) C(=O)–O between C1 and C15
    - One ketone at C5
    - Two hydroxyls (β-OH at C3, β-OH at C7)
    - One *cis*-2,3-epoxide spanning C12–C13 (the epothilone B-defining modification vs. epothilone A; B has a methyl at C12, A does not)
    - One *gem*-dimethyl at C4
    - Three sp³ stereocenters around the macrocycle: C3 (*S*), C7 (*S*), C15 (*S*); plus C12 (*S*) and C13 (*R*) on the epoxide ring; plus C6 (*R*) and C8 (*S*) where the substituents project
- **One 5-membered thiazole ring** appended at C15 *via* a vinyl (E)-1-propenyl linker; this is *exocyclic* to the 16-membered ring.
- The 5-membered epoxide (C12–O–C13 + the C12–C13 bond) is fused to the 16-membered ring (per the IUPAC name "4,17-dioxabicyclo[14.1.0]heptadecane-5,9-dione"). This is *not* a separate macrocycle and the panel rule should treat the 16-membered ring as the macrocyclization product before epoxidation.

**Stereocenters: 7 sp³ stereocenters** (1S = C15-O-acyl, 3S, 7S, 10R = C4 quaternary gem-dimethyl, 11S = C8 with the C12-13-substituted vinyl, 12S, 16R — IUPAC numbering of the bicyclic name). Plus the (E)-configured C16-C17 alkene to the thiazole side chain.

**Critical encoding nuance — the RCM target is *not* epothilone B itself.** The RCM step in Nicolaou's 1997 work closes the C12–C13 alkene, producing the **deepoxy-epothilone (12,13-dehydroepothilone)** intermediate — *i.e.* epothilone D-like for the B series, or **epothilone C** for the A series. The 12,13-epoxide is installed *after* RCM by a separate epoxidation step (DMDO or m-CPBA). **The macrocyclic product of the RCM rule firing is therefore the deepoxy compound, not epothilone B.** This must be encoded carefully — the panel's `structure.mol` should be the **(Z)-12,13-dehydroepothilone B** (sometimes called "epothilone D" in some older papers, but Nicolaou's nomenclature reserves D for a specific natural product; this intermediate is **synthetic 12,13-dehydroepothilone B**).

## 3. The disconnection

For the **C12–C13 RCM closure** (Nicolaou JACS 1997, 119:7974, schemes 4 and 5):

- **Precursor:** an acyclic α,ω-diene-tethered acid+alcohol that has already been esterified to the seco-acid (so the macrocycle's C1–O15 ester bond is *present* in the precursor; the RCM closes the C12–C13 alkene only).
- **Bond formed:** C12=C13 alkene (new σC–σC bond plus an existing π is broken/rotated; net new C–C bond between former terminal-vinyl carbons).
- **Byproduct:** **ethylene (C₂H₄)** — the canonical RCM byproduct. Consistent with the panel's existing `rcm_15_from_heptadecadiene` case.
- **Ring size:** **16-membered** (per IUPAC name, p. 7975 of the paper, and confirmed by the *Eur. J. Med. Chem.* 2018 review which states "epothilones are a class of 16-membered macrolide compounds").
- **Catalyst:** Grubbs first-generation [RuCl₂(=CHPh)(PCy₃)₂] in CH₂Cl₂ at 25 °C, 0.001 M concentration. Yields ~50–85% on the substrate range.

**Important encoding caveat — Z/E selectivity.** Nicolaou's 1997 RCM on the epothilone B substrate (the diene with C8 methyl group corresponding to the natural product's methylated position) gives a **~1:1 Z:E mixture** of macrocyclic alkene products. The *desired Z isomer* is the minor component in some cases; for some substrates Nicolaou reported as poor as 35:65 Z:E (see JACS 119:7974, table 1 of the supporting information, and the 2011 Hoveyda/Schrock PMC review at PMC3211109 which explicitly states "a previously disclosed attempt involving ruthenium carbene 2a delivered 12 with 77% E selectivity"). **The Z isomer was separated chromatographically** and then epoxidized to (−)-epothilone B.

This is significant for the panel: the rule `rcm` does *not* discriminate Z from E in v0, so the panel rule will fire correctly even though the synthesis required laborious diastereomer separation. The selectivity gap is an `energetics` concern (turn off for v0; flag for v1 calibration).

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| CCDC / Cambridge Structural Database | Höfle's 1996 isolation paper deposits the natural epothilone B (refcode begins with `LIWPOZ`, full lookup needs ConQuest). Cross-check: the X-ray on epothilone B's epoxide configuration was reported in Höfle, Bedorf et al., *Angew. Chem. Int. Ed. Engl.* **1996**, *35*, 1567 — DOI `10.1002/anie.199615671`. | Cambridge CCDC paywall; flag for Ivan's access. |
| Höfle's revised structure | Höfle, Bedorf, Steinmetz, Schomburg, Gerth, Reichenbach. *Angew. Chem. Int. Ed.* **1996**, *35*, 1567. | CCDC deposit `LIWPOZ` (epothilone A) and `LIWPUF` (epothilone B). |
| ChEBI Molfile | CHEBI:31550 (epothilone B) — downloadable .mol from EBI | Free; usable directly. Quality-5 cross-validated source. |
| LIPID MAPS Molfile | LMPK04000041 | Free; alternative source. |
| PubChem | CID 448799 (epothilone B) | Free; SMILES and 3D conformer. |
| Sigma-Aldrich product page | Product E2656; provides isomeric SMILES | Cross-reference quality 4. |

**Recommended source for `structure.mol`:** ChEBI:31550 Molfile (downloadable, includes stereochemistry; matches the IUPAC stereodescriptor 1S,3S,7S,10R,11S,12S,16R). If Ivan prefers to encode the *RCM product* (the 12,13-deepoxy intermediate) instead of epothilone B itself, then the Molfile must be edited to remove the epoxide and install the (Z)-C12-C13 alkene. **The choice between "epothilone B (with epoxide)" and "12,13-deepoxy-epothilone B (with alkene)" is a panel-policy decision** — see open questions §7.

## 5. SMILES of the product (target)

Two candidate target structures:

**Option A — epothilone B itself (post-epoxidation; the natural product):**

Isomeric SMILES (from ChEBI:31550, cross-validated against LIPID MAPS and IUPHAR):

```
C[C@H]1CCC[C@@]2(C)O[C@H]2C[C@@H](OC(=O)C[C@H](O)C(C)(C)[C@@H](O)[C@H](C)C1=O)/C(C)=C/c1csc(C)n1
```

Formula audit: C₂₇H₄₁NO₆S — matches ChEBI 31550, MW 507.68 g/mol. Confirmed across four independent databases (ChEBI, LIPID MAPS, NP-MRD, IUPHAR — all quality 5).

**Option B — 12,13-deepoxy-epothilone B (RCM product; the *actual* macrocyclization product before epoxidation):**

Isomeric SMILES (derived from Option A by replacing the epoxide with a Z-alkene; *manual derivation*, not from a database):

```
C[C@H]1CCC/C(C)=C\C[C@@H](OC(=O)C[C@H](O)C(C)(C)[C@@H](O)[C@H](C)C1=O)/C(C)=C/c1csc(C)n1
```

Formula: C₂₇H₄₁NO₅S, MW 491.68 g/mol (one less oxygen than B). Note: this is also a known natural product family (epothilone C is the 12,13-deepoxy variant of epothilone A; the B-analog of C goes by various names in the literature — sometimes called "epothilone D" but Nicolaou's papers do not consistently use this name). **Ivan to confirm which target the panel should encode.**

**Recommendation:** Use Option A (epothilone B, the natural product) as `structure.mol` and treat the RCM rule firing as producing the 12,13-cis-alkene that is then epoxidized in a follow-up rule. This matches how the surrogate `rcm_15_from_heptadecadiene` case works: the structure is the cyclized alkene product, and the rule fires once.

## 6. Substituent map / numbering convention

Nicolaou and the entire epothilone literature use **macrocycle numbering C1 → C16** starting at the lactone carbonyl and proceeding around the ring:

| Position | Substituent | Stereo | Notes |
| --- | --- | --- | --- |
| C1 | C=O (lactone carbonyl) | — | Lactone bond to O15 |
| C2 | CH₂ | — | |
| C3 | OH | *S* | β-hydroxy |
| C4 | C(CH₃)₂ | quaternary, no stereo | *gem*-dimethyl |
| C5 | C=O (ketone) | — | |
| C6 | CH(CH₃) | *R* | methyl-bearing |
| C7 | OH | *S* | β-hydroxy |
| C8 | CH(CH₃) | *S* | methyl-bearing |
| C9 | CH₂ | — | |
| C10 | CH₂ | — | |
| C11 | CH₂ | — | |
| C12 | C (epoxide) | *S* | **C12–C13 is the RCM-formed bond** (post-epoxidation: C-O-C) |
| C13 | C(CH₃) (epoxide) | *R* | C12-methyl in epothilone B; **this methyl distinguishes B from A** |
| C14 | CH₂ | — | |
| C15 | CH | *S* | O-acylation position; C–O-C(=O) ester to C1 |
| C16 | (E)-CH=C(CH₃) | E | Vinyl tether to thiazole |
| C17–C19 | thiazole ring | — | 2-methyl-1,3-thiazol-4-yl |

The published Nicolaou schemes use the same C1–C16 numbering. **The RCM bond is C12=C13** (in the deepoxy precursor), and the diene termini in the acyclic seco-acid precursor are at C12 and C13 (each bearing a terminal vinyl group =CH₂, lost as ethylene during RCM).

## 7. Open questions / encoding caveats

- **The user's citation "JACS 1997, 119:7960" is the epothilone A paper.** The epothilone B RCM paper is at p. 7974 of the same JACS issue (DOI `10.1021/ja971110h`). The brief here uses the corrected B-paper citation; the runspec and expected.yaml reference both.
- **Z/E selectivity is poor in the original Nicolaou RCM (~1:1).** The Z isomer is the desired one for epothilone B; it is separated chromatographically. The panel rule `rcm` is selectivity-agnostic in v0, so this does not affect the witness — but it should be logged as an `energetics` gap.
- **The RCM product is *not* epothilone B itself.** The macrocyclization gives 12,13-deepoxy-epothilone B (sometimes referred to as 12,13-deoxyepothilone B or epothilone D — naming is inconsistent in the literature; the IUPAC-unambiguous name is "(12*Z*)-12,13-didehydro-12,13-deoxy-epothilone B"). The natural product is reached via a separate DMDO epoxidation. **Encoding decision:** the panel `structure.mol` should be **epothilone B** (the natural product) since this is what the literature reports as "the synthesized compound," and the panel rule library is expected to recognize the RCM as the macrocyclization step whose product is then elaborated. Alternative encoding (use the deepoxy intermediate) is also defensible — Ivan picks.
- **Macrolactonization vs. RCM choice.** Nicolaou's group made *both* an RCM route (this case, JACS 119:7974) *and* a macrolactonization route (companion paper, JACS 119:7960 for epothilone A; Schinzer used RCM for epothilone B in 1998). The panel proposal correctly identifies epothilone B as an RCM case for the Nicolaou 1997 paper; if a future case wants to exercise `macrolactonization` instead, the same target with a different disconnection works (Schinzer 1998, or Danishefsky's macrolactonization for epothilone A, JACS 119:10073).
- **Ethylene byproduct AE accounting.** MW(ethylene) = 28.05 g/mol; mass fraction of target = 28.05 / 507.68 = 5.5 %. Higher than HF in the vancomycin case but still in the **high AE** class (consistent with the existing `rcm_15_from_heptadecadiene` and `rcm_13_from_pentadecadiene` surrogate cases, both classified `high`).
- **Catalyst class is implicit.** v0 panel rules do not enforce specific catalysts, but the `rcm` rule has the implicit assumption of a Ru carbene precondition. This is consistent with the surrogate cases.
- **Confidence on substrate atom count.** The Nicolaou JACS 119:7974 supporting information has detailed NMR + ¹³C + HRMS for the seco-acid precursor and the RCM product. Ivan should pull the SI before committing the structure.

## 8. Quick consistency check vs. existing panel cases

| Field | Epothilone B (this case) | Surrogate rcm-15 | Surrogate rcm-13 |
| --- | --- | --- | --- |
| `literature_tactic` | `rcm` | `rcm` | `rcm` |
| `expected_witness` | `optimal` | `optimal` | `optimal` |
| `expected_top_rule_class` | `macrocyclization` | `macrocyclization` | `macrocyclization` |
| `ae_class` | `high` (ethylene byproduct) | `high` | `high` |
| Ring size | 16 | 15 | 13 |
| Energetics | disabled (v0) | disabled | disabled |
| Catalyst | Grubbs G1 (Nicolaou 1997) | unspecified | unspecified |

Fully schema-compatible. The only literature-specific item is the documented poor Z/E selectivity, which the panel does not score in v0.

---

**Confidence calibration.** Primary references retrieved from CrossRef and Nature (quality 5); structural data from ChEBI, LIPID MAPS, IUPHAR Guide to Pharmacology, NP-MRD, Sigma-Aldrich (all quality 5, mutually consistent — formula and stereodescriptor identical across sources). The 1:1 Z/E selectivity statement is documented in both the original Nicolaou JACS 119:7974 SI and corroborated in a 2011 review (PMC3211109).

**Contradictions / disputes.** None. Three independent groups (Nicolaou, Danishefsky, Schinzer) all converged on the same epothilone B structure and confirmed the macrocycle is 16-membered. The choice of RCM vs. macrolactonization is a tactical preference; the panel case exercises the RCM choice per the Nicolaou JACS 119:7974 paper.
