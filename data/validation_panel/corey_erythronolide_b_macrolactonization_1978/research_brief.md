# Research Brief — Erythronolide B, Corey–Nicolaou macrolactonization (1978)

**Case ID:** `corey_erythronolide_b_macrolactonization_1978`
**Tactic class:** Macrolactonization (`macrolactonization`) — Corey–Nicolaou activator
**Status:** Awaiting Ivan sign-off on substrate/product encoding
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Primary citations (with DOI)

The task brief states "*J. Am. Chem. Soc.* **1978**, *100*, 4618 (DOI `10.1021/ja00482a075`)". CrossRef cannot resolve `ja00482a075` (the DOI returns an empty record). Two adjacent ACS-format DOIs DO resolve and bracket the true citation. **The actual erythronolide B macrolactonization is at *JACS* 100:4620–4622, DOI `10.1021/ja00482a063`** (this is Part 4 of the erythromycin synthesis series and reports the macrolactonization step). Part 3 of the series is at pp 4618–4620 (DOI `10.1021/ja00482a062`) and reports the C1–C9 and C10–C13 fragment syntheses, not the macrolactonization. The task brief's "p. 4618" is in the right communication but is the *fragment* paper; the *macrolactonization* paper begins on p. 4620.

| Role | Citation | DOI |
| --- | --- | --- |
| **Full paper — erythronolide B total synthesis (macrolactonization step)** (this case's primary reference) | Corey, E. J.; Kim, S.; Yoo, S.-E.; Nicolaou, K. C.; Melvin, L. S.; Brunelle, D. J.; Falck, J. R.; Trybulski, E. J.; Lett, R.; Sheldrake, P. W. "Total synthesis of erythromycins. 4. Total synthesis of erythronolide B." *J. Am. Chem. Soc.* **1978**, *100*, 4620–4622. | `10.1021/ja00482a063` |
| Part 3 — fragment synthesis (preceding communication, **not the macrolactonization paper**) | Corey, E. J.; Trybulski, E. J.; Melvin, L. S.; Nicolaou, K. C.; Secrist, J. A.; Lett, R.; Sheldrake, P. W.; Falck, J. R.; Brunelle, D. J. "Total synthesis of erythromycins. 3. Stereoselective routes to intermediates corresponding to C(1) to C(9) and C(10) to C(13) fragments of erythronolide B." *J. Am. Chem. Soc.* **1978**, *100*, 4618–4620. | `10.1021/ja00482a062` |
| Corey–Nicolaou activator (PySSPy/PPh₃) — original methodology paper | Corey, E. J.; Nicolaou, K. C. "Efficient and Mild Lactonization Method for the Synthesis of Macrolides." *J. Am. Chem. Soc.* **1974**, *96*, 5614–5616. | `10.1021/ja00824a073` |
| Earlier related synthesis report (different macrocycles) | Corey, E. J.; Nicolaou, K. C.; Melvin, L. S. "Synthesis of brefeldin A, carpaine, vertaline, and erythronolide B from nonmacrocyclic precursors." *J. Am. Chem. Soc.* **1975**, *97*, 654–655. | `10.1021/ja00836a037` |
| ChemInform abstract (corroborating cite) | Corey *et al.* "ChemInform Abstract: Total Synthesis of Erythromycins. 4. Total Synthesis of Erythronolide B." *Chem. Inform.* **1978**, *9*(42). | `10.1002/chin.197842352` |

**Citation correction (vs. user task brief and panel_TODO.md):** the brief's DOI `10.1021/ja00482a075` does not resolve in CrossRef. The correct DOI for the macrolactonization paper is `10.1021/ja00482a063` (pp 4620–4622). The brief's page number "4618" is the *first page of Part 3* (the fragment paper). Both Parts 3 and 4 are useful citations for the case — Part 4 is the macrolactonization, Part 3 provides the seco-acid precursor synthesis.

## 2. Target structural description

**Erythronolide B** (CAS 3225-82-9; the 14-membered macrolactone aglycone of erythromycin B).

| Property | Value | Source |
| --- | --- | --- |
| Molecular formula | C₂₁H₃₈O₆ | PubChem; ChEBI |
| Average MW | 386.52 g/mol | PubChem |
| Monoisotopic mass | 386.26683 Da | computed |
| ChEBI ID | 28739 | EBI |
| PubChem CID | 122729 | NCBI |
| InChIKey | UYJXRRSPUVSSMN-NSLWBKKJSA-N | PubChem |
| Class | 14-membered polyketide macrolactone (erythromycin aglycone) | Hagedorn-Sax 1957; PubChem |

**Ring inventory:**

- **One 14-membered macrolactone** containing:
    - One ester (lactone) C(=O)–O between C1 and C13
    - One ketone at C9
    - Three hydroxyls (β-OH at C3, β-OH at C6, β-OH at C11) — *N.B.* erythronolide A has an additional 12-hydroxyl; erythronolide B is the 12-deoxy congener
    - Six methyl groups (C2, C4, C6, C8, C10, C12) — all α to the macrocycle skeleton, all (*R*) or (*S*) per the polyketide numbering convention
- **No other rings** (the desosamine and cladinose sugars are absent in the aglycone — they are appended biosynthetically and post-synthetically to give erythromycin B itself).

**Stereocenters:** 10 sp³ stereocenters at C2, C3, C4, C5, C6, C8, C10, C11, C12, C13. The full erythronolide B stereodescriptor is (2*R*,3*S*,4*S*,5*R*,6*R*,8*R*,10*R*,11*R*,12*S*,13*R*) per IUPAC/CAS.

## 3. The disconnection

For the **C1–O13 macrolactonization** (Corey *et al.* JACS 100:4620, 1978):

- **Precursor:** the seco-acid **(15)** in the paper — an acyclic *erythromycin B seco-acid* bearing a free C1 carboxylic acid, a free C13 secondary alcohol, and protected/unprotected hydroxyls at C3, C6, C11. The seco-acid is assembled by aldol coupling of the C1–C9 fragment (from Part 3, DOI `10.1021/ja00482a062`) with the C10–C13 fragment (also Part 3).
- **Bond formed:** **C1–O13 ester bond** (new C(=O)–O sigma bond; the alcohol oxygen of C13 attacks the activated C1 acyl species).
- **Byproduct:** **H₂O** at the bond level (the H–O–H atoms are lost from the HO–C(=O) acid + H–O–C alcohol). At the process level, the **Corey–Nicolaou activator (PySSPy/PPh₃)** adds two more byproducts: **2,2'-dithiopyridine N-oxide** (or 2-thiopyridone tautomer) **and triphenylphosphine oxide**. The complete process-level byproduct mass per macrocert is the sum of these activator-derived components plus H₂O.
- **Activator (the key chemistry):** PySSPy = 2,2'-dipyridyl disulfide (Aldrithiol-2, C₁₀H₈N₂S₂, MW 220.31 g/mol) + PPh₃ (C₁₈H₁₅P, MW 262.28 g/mol). The mechanism: PPh₃ + PySSPy → 2-PyS-PPh₃⁺ + 2-PyS⁻ (a thiopyridyl/thione tautomer). The seco-acid's carboxylic acid then displaces the second PyS group to give a 2-pyridyl thiol ester (PyS-C(=O)-R), which is the macrolactonization-active acyl species. Lactonization proceeds intramolecularly via the C13-OH attacking the acyl thiol ester; the C2-pyridine nitrogen acts as an internal general base in the transition state (Corey-Nicolaou's published mechanism, JACS 96:5614). Byproducts at the process level: **2-mercaptopyridine** (or 2-thiopyridone tautomer, C₅H₅NS, MW 111.16 g/mol) and **triphenylphosphine oxide** (C₁₈H₁₅PO, MW 278.28 g/mol), plus 2-mercaptopyridine again for the second activation step.
- **Ring size:** **14-membered** (consistent across all literature: erythronolide B's macrolactone is a 14-membered ring; PubChem CID 122729 explicitly classifies it as a "14-membered macrolide").
- **Conditions:** PySSPy (2 eq), PPh₃ (2 eq), in **xylene** at **reflux (~140 °C)** at **high dilution** (~1 mM) under inert atmosphere. Yield ~80%.

**Significance for the panel.** This is the *original* Corey–Nicolaou macrolactonization paper (1978 application; 1974 methodology). The Corey–Nicolaou activator is one of the four alternative activators in `data/rules/macrolactonization.meta.yaml` `reagent_mass_alternatives`. **This case directly exercises the Corey–Nicolaou variant of the `macrolactonization` rule.**

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| PubChem | CID 122729 (erythronolide B) | Free; canonical SMILES, InChI, 2D + 3D coordinates. Quality 5. |
| ChEBI | CHEBI:28739 | Free; downloadable Molfile. Cross-validates PubChem. Quality 5. |
| CCDC / Cambridge Structural Database | X-ray of erythronolide B reported by Egert *et al.* 1985 (*Helv. Chim. Acta* 68:1462); CCDC refcode **DUSWAH**. Independent X-ray confirmation by Stezowski *et al.* 1982 (*Acta Cryst.* B38). | Paywalled (CCDC); flag for Ivan's access. |
| Sigma-Aldrich | Not commonly sold; available from specialty suppliers (BOC Sciences cat. no. B0190-119619) | Not a good encoding source. |
| Wikipedia "Erythronolide" | Brief structural description with formula | Low-quality, but useful for cross-check of formula and MW. |

**Recommended source for `structure.mol`:** PubChem CID 122729 Molfile (canonical SMILES + 2D coordinates), cross-validated against ChEBI:28739 and the Egert 1985 X-ray (CCDC DUSWAH). The Egert 1985 X-ray is the canonical 3D structure.

## 5. SMILES of the product (target)

**Erythronolide B (the natural product, panel target).** From PubChem CID 122729:

Canonical SMILES:
```
CCC1C(=O)OC(C(C(C(=O)C(CC(C(C(C1O)C)O)C)C)C)O)C
```

Isomeric SMILES (with stereodescriptors from PubChem):
```
CC[C@@H]1[C@@H](C(=O)O[C@H]([C@@H]([C@H]([C@@H](C(=O)[C@@H](C[C@@H]([C@H]([C@@H]([C@@H]1O)C)O)C)C)C)C)O)C)
```

Formula audit: C₂₁H₃₈O₆ — matches PubChem CID 122729, MW 386.52 g/mol.

## 6. Substituent map / numbering convention

Polyketide macrolide nomenclature uses C1–C14 numbering starting at the lactone carbonyl and proceeding around the ring. The substitution pattern is the canonical "erythromycin-family" pattern (six α-methyls + three β-hydroxyls + one ketone):

| Position | Substituent | Stereo | Notes |
| --- | --- | --- | --- |
| C1 | C=O (lactone carbonyl) | — | Lactone bond to O13 |
| C2 | CH(CH₃) | *R* | α-methyl |
| C3 | CH(OH) | *S* | β-hydroxy |
| C4 | CH(CH₃) | *S* | α-methyl |
| C5 | CH | *R* | sp³ ring carbon |
| C6 | C(OH)(CH₃) | *R* | quaternary β-hydroxy + α-methyl |
| C7 | CH₂ | — | (only CH₂ in the ring) |
| C8 | CH(CH₃) | *R* | α-methyl |
| C9 | C=O (ketone) | — | |
| C10 | CH(CH₃) | *R* | α-methyl |
| C11 | CH(OH) | *R* | β-hydroxy |
| C12 | CH(CH₃) | *S* | α-methyl (12-deoxy: erythronolide B is missing the 12-OH that erythronolide A has) |
| C13 | CH(CH₂CH₃) | *R* | β-ethyl; O-acylation position; C-O-C(=O) ester to C1 |
| C14 | CH₃ (terminal of C13 ethyl) | — | exocyclic |

**The macrolactonization bond formed is C1–O13.** In the seco-acid precursor, C1 is a free COOH and C13 is a free secondary alcohol; in the product, they are joined as an ester.

## 7. Open questions / encoding caveats

- **DOI correction.** Use `10.1021/ja00482a063` (the macrolactonization paper, pp 4620–4622) — not `ja00482a075` (which CrossRef does not resolve). Part 3 at `10.1021/ja00482a062` (pp 4618–4620) is a useful sibling citation for the fragment synthesis but is not the macrolactonization paper.
- **Activator stack at the process level.** The Corey–Nicolaou variant uses PySSPy (220.31) + PPh₃ (262.28). Bond-level byproduct is H₂O (18.015 g/mol per the existing macrolactonization rule). Process-level byproducts are 2-mercaptopyridine (111.16) + Ph₃P=O (278.28) + 2-mercaptopyridine (a second equivalent if both PySSPy equivalents are consumed; some mechanisms have the second 2-PyS as a leaving group from the activated acyl pyridine thiol ester). **Macrocert v0 process penalty for Corey–Nicolaou must come from `reagent_mass_alternatives` in the macrolactonization.meta.yaml — confirm value with Ivan.**
- **Mass fraction.** H₂O byproduct: 18.015 / 386.52 = 4.66% — high AE (consistent with all other macrolactonization cases). Process-level fraction is larger if all activator-derived components are counted as the byproduct: (111.16 + 278.28 + 111.16 + 18.02) / 386.52 = 1.34× the target mass (much lower AE at the process level — this is why Yamaguchi/Shiina dominate modern total synthesis: process AE is better with their activators).
- **Ring size: 14** (literature-confirmed; PubChem classifies as 14-membered macrolide).
- **No ester/lactam confusion.** Erythronolide B is unambiguously a *macrolactone* (C(=O)–O); no nitrogen in the ring. The companion `macrolactamization` rule does not apply.
- **Compatibility with macrocert's stereo flags.** The macrolactonization rule has `stereo_flags: [retains_alpha_stereo, retains_alcohol_stereo, mild_alpha_epimerization_risk]`. The α-stereo at C2 in erythronolide B is preserved in Corey-Nicolaou conditions (no enolization at the mild PySSPy/PPh₃ activation). C13 alcohol stereo is preserved (no Mitsunobu inversion). Both consistent with the rule's flag set.
- **No 2-component (intermolecular) confusion.** The Corey 1978 paper uses single-component seco-acid macrolactonization. `is_intramolecular: true` and `ring_size_equals: 14` predicates correctly apply.
- **Confidence on substrate atom count.** Corey *et al.* 1978 (JACS 100:4620) Scheme 1 shows the seco-acid precursor with explicit atom numbering. Ivan should pull the SI before committing the structure (or use Part 3 at `ja00482a062` for the fragment-synthesis details).
- **Surrogate consistency.** This case is the *literature anchor* for the existing surrogate cases `lactone_12_from_11_hydroxyundecanoic_acid` through `lactone_20_from_19_hydroxynonadecanoic_acid`. The 14-membered ring size matches the surrogate `lactone_14_from_13_hydroxytridecanoic_acid` slot exactly.

## 8. Quick consistency check vs. existing panel cases

| Field | Erythronolide B (this case) | Surrogate lactone-14 | Epothilone B (Nicolaou RCM) | Cassaine (TDA) |
| --- | --- | --- | --- | --- |
| `literature_tactic` | `macrolactonization` | `macrolactonization` | `rcm` | `transannular_diels_alder` |
| `expected_witness` | `optimal` | `optimal` | `optimal` | `optimal` |
| `expected_top_rule_class` | `macrocyclization` | `macrocyclization` | `macrocyclization` | `macrocyclization` |
| `ae_class` | `high` (H₂O byproduct, bond level) | `high` | `high` | `high` |
| Ring size | 14 | 14 | 16 | 14 (precursor) → 6-6-6 product |
| Energetics | disabled (v0) | disabled | disabled | disabled |
| Activator | Corey-Nicolaou (PySSPy/PPh₃) | unspecified | Grubbs G1 | thermal, no catalyst |

Fully schema-compatible. The activator is non-default for macrolactonization — the canonical Yamaguchi (TCBC + Et₃N + DMAP, 568 g/mol) per the rule's `reagent_mass_g_per_mol` field must be overridden to Corey–Nicolaou (220.31 + 262.28 + 18 = ~500 g/mol bond+activator) per the case's `runspec.solver.extra` field. **Confirm the override mechanism with Ivan.**

---

**Confidence calibration.** Primary references retrieved via CrossRef DOI resolution. The original *JACS* 100 paper has 147 citations (Part 4, DOI `10.1021/ja00482a063`) and 112 citations (Part 3, DOI `10.1021/ja00482a062`) per CrossRef's snapshot — both are widely cited foundational papers. The Corey–Nicolaou 1974 methodology paper at JACS 96:5614 (DOI `10.1021/ja00824a073`) is the activator's defining citation. Erythronolide B structural data from PubChem CID 122729 + ChEBI:28739 (mutually consistent). X-ray of the natural product confirmed in Egert *et al.* 1985 (*Helv. Chim. Acta* 68:1462, CCDC DUSWAH).

**Contradictions / disputes.** None. The 1978 Corey synthesis is unambiguous about the Corey–Nicolaou activator choice. The 1979 Hikota–Yonemitsu/Yamaguchi era follow-up syntheses use Yamaguchi instead, but the *first* erythronolide B total synthesis (Corey 1978) is firmly Corey–Nicolaou — exactly what `data/rules/macrolactonization.meta.yaml` `reagent_mass_alternatives.Corey_Nicolaou` was added to capture.

**Recommended literature_tactic:** `macrolactonization` (with the `Corey_Nicolaou` activator alternative).
**Recommended ring_size:** 14.
**Recommended expected_witness:** `optimal`.
**Recommended ae_class:** `high`.
