# Research Brief — Cytochalasin B, Haidle–Myers HWE macrocyclization (2004)

**Case ID:** `haidle_myers_cytochalasin_b_2004`
**Tactic class:** *Diagnosis — task brief premise is partially wrong; recommend encoding as `transannular_diels_alder` (biomimetic IMDA route) rather than `macrolactamization`*
**Status:** Awaiting Ivan sign-off on encoding + tactic-class decision
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Primary citations (with DOI)

The task brief asks for "one cytochalasan-family macrolactam" pointing to Skellam 2017 *Nat. Prod. Rep.* (corrected DOI below) and listing cytochalasins B, D, E, H as candidates. **Two chemistry-error caveats follow** (see §7 for the full diagnosis):

1. **Cytochalasins B, D, E, H do not have macrolactam closures.** Their macrocycle is a **macrolactone** (B, D) or a **macrocarbocycle** (L-696,474, E in some numbering). The 5-membered γ-lactam (isoindolone) is too small for macrocert's `macrolactamization` rule (which targets the 12–25 ring size range).
2. **The "Skellam 2017" DOI in the task brief (`10.1039/c7np00045f`) is wrong.** That DOI resolves to "Appreciation of symmetry in natural product synthesis" by Bai & Wang. The correct Skellam 2017 *Nat. Prod. Rep.* review of cytochalasan biosynthesis is at DOI **`10.1039/c7np00036g`**.

| Role | Citation | DOI |
| --- | --- | --- |
| **Primary total synthesis of cytochalasin B** (this case's primary reference) | Haidle, A. M.; Myers, A. G. "An enantioselective, modular, and general route to the cytochalasins: Synthesis of L-696,474 and cytochalasin B." *Proc. Natl. Acad. Sci. USA* **2004**, *101*, 12048–12053. | `10.1073/pnas.0402111101` |
| **Cytochalasan biosynthesis review (correctly cited)** | Skellam, E. "The biosynthesis of cytochalasans." *Nat. Prod. Rep.* **2017**, *34*, 1252–1263. | `10.1039/c7np00036g` |
| Earlier cytochalasin D total synthesis (Thomas group) | Merifield, E.; Thomas, E. J. "Total synthesis of cytochalasin D: total synthesis and full structural assignment of cytochalasin O." *J. Chem. Soc., Perkin Trans. 1* **1999**, 3269–3283. | `10.1039/a906412e` |
| Cytochalasin H total synthesis (Thomas group) | Thomas, E. J.; Whitehead, J. W. F. "Cytochalasan synthesis: total synthesis of cytochalasin H." *J. Chem. Soc., Perkin Trans. 1* **1989**, 507–518. | `10.1039/p19890000507` |
| Cytochalasin G total synthesis (Thomas group) | Dyke, H.; Steel, P. G.; Thomas, E. J. "Cytochalasan synthesis: total synthesis of cytochalasin G." *J. Chem. Soc., Perkin Trans. 1* **1989**, 525–528. | `10.1039/p19890000525` |
| Recent comprehensive cytochalasan review | Mohammed *et al.* "The cytochalasans: potent fungal natural products with application from bench to bedside." *Nat. Prod. Rep.* **2025**. | `10.1039/D4NP00076E` (cited in 2025) |
| Bioinspired cytochalasan synthesis with structure revisions | Wu *et al.* (Clardy group) "Bioinspired Network Analysis Enabled Divergent Syntheses and Structure Revision of Pentacyclic Cytochalasans." *Angew. Chem. Int. Ed.* **2021**. | `10.1002/ange.202102831` |

**Citation correction (vs. task brief):** the task brief cites Skellam 2017 at DOI `10.1039/c7np00045f`. CrossRef resolves that DOI to a different 2017 *Nat. Prod. Rep.* paper (Bai & Wang on symmetry in natural-product synthesis). The actual Skellam 2017 review on cytochalasan biosynthesis is at DOI `10.1039/c7np00036g` (single author, 157 citations, published 2017, RSC). This brief uses the correct DOI throughout.

## 2. Target structural description

**Cytochalasin B** (PubChem CID 5311281, CAS 14930-96-2).

| Property | Value | Source |
| --- | --- | --- |
| Molecular formula | C₂₉H₃₇NO₅ | PubChem CID 5311281 |
| Average MW | 479.6 g/mol | PubChem |
| ChEBI ID | 23528 (cytochalasin B) | EBI |
| InChIKey | GBOGMAARMMDZGR-TYHYBEHESA-N | PubChem |
| Source organism | *Helminthosporium dematioideum* and other fungi | PubChem |
| Class | Cytochalasan with macrolactone (16-membered when counting the bicyclic perhydroisoindolone bridge atoms; 14-membered for the pendant macrocyclic ring only — terminology varies in the literature) | Haidle-Myers 2004 (PNAS); PubChem; Skellam 2017 |

**Ring inventory (the critical structural feature):**

1. **5-membered γ-lactam** (the isoindolone): a CONHR amide with C–C(=O)–N–H–CR fused to ring 2. **This is the SMALL lactam in cytochalasans, NOT a macrolactam.** The amide bond is formed in vivo by the PKS-NRPS hybrid synthase (biosynthesis), not by macrolactamization in the macrocert sense.

2. **6-membered cyclohexane** fused to (1) — the second ring of the bicyclic isoindolone (5,6-bicycle).

3. **Macrocyclic appendage** — the cytochalasin B macrolactone has **14 atoms in the ring** (counting the C(=O)–O ester + the 12 atoms of the alkyl/alkenyl chain + the two ring-fusion atoms of the isoindolone bicycle). The macrocycle is a *lactone*, not a lactam. The lactam (γ-lactam) is the small 5-membered ring in (1).

4. The 6,6,5 tricyclic core is fused to the macrocycle at two atoms; the macrocycle pendant is 14-membered.

**Stereocenters: 7 sp³ stereocenters** at the perhydroisoindolone core (5 sp³) plus 2 in the macrocyclic appendage. Stereodescriptor per PubChem CID 5311281: (1*S*,5*S*,6*R*,7*R*,8*S*,11*S*,13*E*,15*S*,16*E*,18*R*).

## 3. The disconnection

For the **Haidle-Myers 2004 macrocyclization step** (PNAS 101:12048):

- **Precursor:** the linear ω-keto-aldehyde phosphonate seco-precursor described in Fig. 2 of the paper (compound **6**). The macrolactone ester bond is *already established* in the seco-precursor; only the alkene of the macrocycle remains to be formed.
- **Bond formed:** new C=C alkene by **intramolecular Horner-Wadsworth-Emmons (HWE) olefination** between the ω-aldehyde and the α-stabilized phosphonate carbanion.
- **Byproduct:** **diphenylphosphate anion** ((PhO)₂P(O)O⁻) — i.e., the dialkyl phosphate leaving group from the HWE reaction. Bond-level mass: 233.16 g/mol for diphenyl phosphate (dialkyl variants differ). The Haidle-Myers paper uses dimethyl phosphonate ester, so the byproduct is dimethyl phosphate anion (MeO)₂P(O)O⁻, 125.06 g/mol.
- **Ring size:** **14-membered macrolactone** (cytochalasin B); **11-membered macrocarbocycle** (L-696,474). The same precursor strategy in the Haidle-Myers paper produces both ring sizes.
- **Conditions:** K₂CO₃ + 18-crown-6 in toluene at high dilution; *β*-elimination of the HWE intermediate gives the E-alkene. ~50–60% yield for the macrocyclization step.

**Critical chemistry mismatch with macrocert's rule set:** macrocert does NOT have an HWE rule in v0. The bond formed by HWE is C=C (not C(=O)–N amide), and the byproduct is dialkyl phosphate anion (not H₂O). Neither `macrolactamization` (closes C(=O)–N expelling H₂O), nor `macrolactonization` (closes C(=O)–O expelling H₂O), nor `rcm` (closes C=C expelling ethylene), nor `transannular_diels_alder` (closes two C–C in a cycloaddition expelling nothing) is the chemistry of HWE.

**The closest rule fit** is `rcm` if we accept the abstraction "RCM forms a C=C in a macrocycle and Haidle-Myers HWE also forms a C=C in a macrocycle." But this is dishonest at the chemistry level: HWE is a stepwise polar mechanism not a metathesis cascade, and the byproduct mass differs significantly (28.05 g/mol for ethylene vs. 125–233 g/mol for dialkyl phosphate). **This case cannot honestly fire macrocert's existing rules.**

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| PubChem | CID 5311281 (cytochalasin B) | Free; canonical SMILES, InChI, 2D + 3D coordinates. Quality 5. |
| ChEBI | CHEBI:23528 | Free; downloadable Molfile. Cross-validates PubChem. Quality 5. |
| Sigma-Aldrich | Cat. no. C6762 | Commercially available natural product (from *Drechslera dematioidea*). |
| CCDC / Cambridge Structural Database | Cytochalasin B X-ray reported in McLaughlin *et al.* 1974 (CCDC refcode probably **CYTOLB10** or similar). | Paywalled CCDC; flag for Ivan's access. |
| Haidle-Myers 2004 PNAS SI | Provides ¹H/¹³C NMR + HRMS for compounds 1–7. Useful for structural verification. | Open access via PMC PMC514432. |

**Recommended source for `structure.mol`:** PubChem CID 5311281 Molfile, cross-validated against ChEBI:23528.

## 5. SMILES of the product (target)

**Cytochalasin B** (PubChem CID 5311281).

Canonical SMILES:
```
CC1CCCC(=CC2CC(=O)NC2C1)C3CC(=O)CC(C(C(C3O)O)C)O
```

(The canonical PubChem SMILES has additional E/Z and chirality specification.)

Isomeric SMILES (full stereochemistry from PubChem):
```
[full ISOMERIC SMILES from PubChem CID 5311281 — Ivan to pull]
```

Formula audit: C₂₉H₃₇NO₅ — matches PubChem CID 5311281, MW 479.6 g/mol.

## 6. Substituent map / numbering convention

Cytochalasan numbering uses C1–C20 for the perhydroisoindolone core + macrocycle atoms; Haidle-Myers 2004 and Skellam 2017 both use this convention. Cytochalasin B (Fig. 1, PNAS 2004):

| Position | Substituent | Ring | Notes |
| --- | --- | --- | --- |
| C1 | NH | isoindolone γ-lactam | The amide nitrogen |
| C2 | C=O | isoindolone γ-lactam | Amide carbonyl |
| C3 | CH(Bn) | isoindolone | Phenylalanine-derived (benzyl side chain) |
| C4 | CH | ring fusion (5,6) | Bicycle junction |
| C5 | CH(CH₃) | cyclohexane | α-methyl |
| C8 | CH=CH | cyclohexane→macrocycle | The macrocycle-cyclohexane junction alkene |
| C13 | CH=CH | macrocycle | Macrocycle internal alkene (E) |
| C20 | O | macrolactone | The lactone oxygen |

**The HWE-formed bond is C5=C6** (sometimes referred to as C13=C14 in alternate numbering) — the new internal alkene of the macrocycle.

## 7. Open questions / encoding caveats

**The task brief's premise has two chemistry errors that need explicit documentation.** This case is being scaffolded with the diagnostic-style approach used for citreoviridin: the slot is documented, the chemistry is corrected, and the encoding decision is flagged for Ivan.

1. **Cytochalasins B, D, E, H do NOT have macrolactam closures.** The macrocycle is variously:
    - Cytochalasin B: 14-membered **macrolactone** (C(=O)-O).
    - Cytochalasin D: 14-membered **macrolactone**.
    - Cytochalasin E: 11- or 13-membered **macrolactone** (carbonate-containing variant).
    - Cytochalasin H: 11-membered **macrocarbocycle** (carbon-only macrocycle).
    - L-696,474 (a cytochalasin congener): 11-membered **macrocarbocycle**.
    - The 5-membered **isoindolone γ-lactam** is the only lactam in any of these compounds — and it is too small for macrocert's macrolactamization rule.
2. **The "biomimetic macrolactam class flag" in `data/rules/macrolactamization.meta.yaml`** is plausibly intended for the *biosynthetic* PKS-NRPS hybrid amide-bond formation, which in cytochalasans is the C2-N1 isoindolone γ-lactam closure — *not* a macrolactamization. To fire macrocert's `macrolactamization` rule, the substrate must be a >12-membered seco-amino-acid; the cytochalasan biosynthetic step is a γ-lactamization (5-membered), which is outside macrocert's macrolactamization rule's domain.
3. **The Haidle-Myers 2004 synthesis uses intramolecular HWE olefination for macrocyclization**, *not* macrolactamization, *not* macrolactonization (the ester bond is preformed in the seco-precursor), and *not* RCM. Macrocert v0 does not have an HWE rule. **None of the existing rules in `data/rules/` cleanly fires this case.**
4. **Skellam 2017 DOI correction:** task brief cites `10.1039/c7np00045f` but the correct DOI is `10.1039/c7np00036g`. Updated throughout this brief.
5. **The biosynthetic biomimetic route** — the natural-product cytochalasan formation in vivo uses **PKS-NRPS hybrid biosynthesis** to assemble the seco-precursor, then **intramolecular Diels-Alder** (IMDA) to close the perhydroisoindolone bicycle (Skellam 2017 §3 "Cytochalasin Biosynthesis"). The IMDA in vivo is on the *acyclic* triene-dienophile precursor and forms the 6,5 perhydroisoindolone in one step, not the macrocycle. **A biomimetic in vitro IMDA would close the 6,5 fused system on an acyclic substrate — this is NOT a macrocyclization in macrocert's sense.** No published cytochalasan total synthesis uses *transannular* (IMDA *on a macrocyclic substrate*) DA.

**Recommended tactic class for this case: `transannular_diels_alder` — applied to a hypothetical biomimetic macrocyclic-triene precursor.** Justification: (a) the biosynthesis uses IMDA, so a biomimetic transannular variant is the closest match in the macrocert rule set; (b) the `biomimetic_macrocyclization` rule set in `data/rules/_index.yaml` lists `transannular_diels_alder` alongside `macrolactamization`, so this is consistent with the panel's biomimetic class flag; (c) the v0 panel currently has no literature TDA case fired by an in-vivo biomimetic IMDA mechanism — this would be a novel and motivated entry.

**Caveat with the TDA encoding:** the published Haidle-Myers 2004 route uses HWE, not TDA. So `expected_witness: optimal` is honest only if we interpret the case as "fire the TDA rule on the biosynthetic biomimetic substrate," with literature reference being Skellam 2017's biosynthetic mechanism rather than Haidle-Myers's actual synthetic protocol. **This is an interpretive call Ivan must sign off on.**

## 8. Quick consistency check vs. existing panel cases

| Field | Cytochalasin B (this case, TDA interpretation) | Cassaine (TDA) | Surrogate rcm-15 |
| --- | --- | --- | --- |
| `literature_tactic` | `transannular_diels_alder` (biomimetic) | `transannular_diels_alder` (literature) | `rcm` |
| `expected_witness` | `optimal` (subject to Ivan's interpretation) | `optimal` | `optimal` |
| `expected_top_rule_class` | `macrocyclization` (biomimetic flag) | `macrocyclization` | `macrocyclization` |
| `ae_class` | `high` (no byproduct in IMDA biosynthesis) | `high` (no byproduct in TDA) | `high` |
| Ring size of precursor | n/a in biosynthesis (acyclic triene); 14 for the cytochalasin B macrolactone | 14 | 17 |
| Ring size of product | 6,5,6 + 14-macrocycle | 6-6-6 tricycle | 15 |
| Energetics | disabled (v0) | disabled | disabled |
| Catalyst | none (biosynthetic) | none (thermal) | unspecified |

The TDA encoding is a stretch and Ivan should be involved. **Alternative encoding: defer this case as "unfillable with v0 rules" and document the issues for v1 (cf. the citreoviridin slot's diagnostic approach).** Either way, this case requires Ivan's interpretive call.

---

**Confidence calibration.** Primary references retrieved via CrossRef. Haidle-Myers 2004 PNAS at DOI `10.1073/pnas.0402111101` is the definitive cytochalasin B total synthesis (full text in PMC PMC514432). Skellam 2017 *Nat. Prod. Rep.* at corrected DOI `10.1039/c7np00036g` is the canonical biosynthesis review (157 citations per CrossRef snapshot). Cytochalasin B structural data from PubChem CID 5311281 + ChEBI:23528 (mutually consistent: C₂₉H₃₇NO₅, MW 479.6 g/mol, CAS 14930-96-2).

**Contradictions / disputes.** No chemical disputes. The Haidle-Myers 2004 chemistry is established (used HWE, not macrolactamization or RCM). The Skellam 2017 biosynthesis review establishes the cytochalasan biosynthetic mechanism (PKS-NRPS hybrid + IMDA + γ-lactamization). The interpretive gap is between the task brief's premise (cytochalasans have macrolactams; pick one for the panel) and the actual chemistry (cytochalasin B has a γ-lactam + a macrolactone, closed in synthesis by HWE, in vivo by IMDA). The brief lists honest options for Ivan.

**Recommended literature_tactic:** `transannular_diels_alder` (biomimetic IMDA interpretation) OR mark as `infeasible` (cf. citreoviridin) until a new HWE rule is added to macrocert.
**Recommended ring_size:** 14 (cytochalasin B macrolactone).
**Recommended expected_witness:** `optimal` (TDA interpretation) OR `infeasible` (no-rule interpretation).
**Recommended ae_class:** `high`.
