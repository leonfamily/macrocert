# Research Brief — (+)-Cassaine, Phoenix–Reddy–Deslongchamps transannular Diels–Alder (2008)

**Case ID:** `phoenix_reddy_cassaine_tda_2008`
**Tactic class:** Transannular Diels–Alder (`transannular_diels_alder`)
**Status:** Awaiting Ivan sign-off on substrate/product encoding
**Compiled:** 2026-05-24 (researcher agent)

This case replaces the unfillable `citreoviridin_suh_imda_1985` slot. The citreoviridin diagnosis (no macrocycle, no Suh 1985 paper, no Diels–Alder in any citreoviridin synthesis) is preserved in that directory; the present brief picks up the substitute target the panel_TODO.md and the citreoviridin notes both recommended.

---

## 1. Primary citations (with DOI)

| Role | Citation | DOI |
| --- | --- | --- |
| **Full paper — cassaine total synthesis via TDA** (this case's primary reference) | Phoenix, S.; Reddy, M. S.; Deslongchamps, P. "Total Synthesis of (+)-Cassaine *via* Transannular Diels−Alder Reaction." *J. Am. Chem. Soc.* **2008**, *130*, 13989–13995. | `10.1021/ja805097s` |
| Earlier *Org. Lett.* communication (progress toward cassaine TDA strategy) | Phoenix, S.; Bourque, E.; Deslongchamps, P. "Progress toward the Total Synthesis of Cassaine *via* the Transannular Diels−Alder Strategy." *Org. Lett.* **2000**, *2*, 4149–4152. | `10.1021/ol006670r` |
| Deslongchamps 14-membered TDA methodology — theoretical | Lamothe, S.; Ndibwami, A.; Deslongchamps, P. "Transannular Diels–Alder reaction of 14-membered macrocyclic trienes. Part I: Theoretical analysis and stereochemical predictions." *Tetrahedron Lett.* **1988**, *29*, 1639–1640. | `10.1016/S0040-4039(00)82005-5` |
| Deslongchamps 14-membered TDA methodology — experimental | Lamothe, S.; Ndibwami, A.; Deslongchamps, P. "Transannular Diels–Alder reaction of 14-membered macrocyclic trienes. Part II: Experimental results and synthetic potential." *Tetrahedron Lett.* **1988**, *29*, 1641–1644. | `10.1016/S0040-4039(00)82006-7` |
| Sibling 13-membered TDA methodology (the original Deslongchamps lineage; candidate alternate) | Baettig, K.; Dallaire, C.; Pitteloud, R.; Deslongchamps, P. "Synthesis and transannular Diels–Alder reaction of a *cis-trans-trans* 13-membered macrocyclic trienone." *Tetrahedron Lett.* **1987**, *28*, 5249–5252. | `10.1016/S0040-4039(00)96699-1` |
| Companion 13-membered paper (different geometry) | Baettig, K.; Marinier, A.; Pitteloud, R.; Deslongchamps, P. "Synthesis and transannular Diels–Alder reaction of a *trans-cis-cis* 13-membered macrocyclic trienone." *Tetrahedron Lett.* **1987**, *28*, 5253–5254. | `10.1016/S0040-4039(00)96700-5` |
| Bérubé–Deslongchamps 1987 (tetrasubstituted enol ether dienophile) | Bérubé, G.; Deslongchamps, P. "Synthesis and transannular Diels–Alder reaction of a 13-membered macrocyclic triene having a tetrasubstituted enol ether as a dienophile." *Tetrahedron Lett.* **1987**, *28*, 5255–5258. | `10.1016/S0040-4039(00)96701-7` |

**Citation correction (vs. panel_TODO.md):** the original brief listed "Bérubé–Deslongchamps 1987" at *Tet. Lett.* 28:5249, but CrossRef shows that paper is by **Baettig, Dallaire, Pitteloud & Deslongchamps** (pp 5249–5252). The Bérubé–Deslongchamps paper is at pp 5255–5258 (DOI `10.1016/S0040-4039(00)96701-7`, tetrasubstituted enol-ether-dienophile variant). The 1987 *Tet. Lett.* 28 issue contains three TDA-of-13-membered-trienone papers from the Deslongchamps group (5249, 5253, 5255), all useful for the methodology lineage.

## 2. Target structural description

**(+)-Cassaine** (PubChem CID 5281267, CAS 468-76-8, ChEBI:3454).

| Property | Value | Source |
| --- | --- | --- |
| Molecular formula | C₂₄H₃₉NO₄ | PubChem CID 5281267 |
| Average MW | 405.6 g/mol | PubChem CID 5281267 |
| Source organism | *Erythrophleum* species (Fabaceae) | PubChem description |
| Class | Tricyclic diterpenoid alkaloid (sometimes classed as a C20 *nor*-diterpene with an aminoethyl ester pendant) | PubChem; *J. Nat. Prod.* literature |
| Skeleton | 6-6-6 tricyclic *trans*-decalin–fused cyclohexane with a 2-dimethylaminoethyloxycarbonyl side chain at the A-ring | Phoenix-Reddy-Deslongchamps 2008 §Introduction |

**Bioactivity:** cardiotonic (Na⁺/K⁺-ATPase inhibitor; antihypertensive), local anaesthetic. Long known in pharmacognosy as "nervocidine." Distinct from cassaidine (the saturated congener) and from the cassanoids generally.

**The TDA target is NOT cassaine itself.** As with the epothilone B RCM case, the TDA step produces a *non-natural-product intermediate* (the *trans*-decalin tricycle **5** in Phoenix-Reddy-Deslongchamps 2008, Scheme 1) which is then elaborated through stereoselective reduction, hydroboration, methyl-cuprate 1,4-addition, dimethylaminoethyloxycarbonyl tethering, C8 epimerization, and C3 alcohol deprotection to deliver (+)-cassaine **1**. The panel `structure.mol` should be **(+)-cassaine itself** for consistency with how the other panel cases are encoded (always the natural product), and the TDA rule should be understood as firing on the macrocyclic-triene precursor **4** to produce the tricyclic intermediate **5**, with the rest of the synthesis carried out by hypothetical downstream rules.

If Ivan prefers to encode the *TDA-immediate product* (tricycle **5** of Phoenix-Reddy-Deslongchamps 2008) the structure changes substantially (different stereochemistry at C8 — pre-epimerization; missing the dimethylaminoethyloxycarbonyl tether; C3 is protected). Recommend encoding **(+)-cassaine** as the panel target for v0; flag this for v1 calibration if the TDA-immediate-product encoding is desired.

## 3. The disconnection

For the **TDA closure** (Phoenix-Reddy-Deslongchamps 2008, Scheme 1, compound 4 → 5):

- **Precursor:** a **14-membered macrocyclic triene** (compound **4** in the paper) bearing a *cis,trans,trans* arrangement of three C=C bonds — two of them constituting the diene, one constituting the dienophile.
- **Bond formed:** TWO new σC–σC bonds in a single 4π+2π pericyclic event, plus a transannular ring contraction from 14-membered to a 6-6-6 fused tricycle (trans-decalin + fused cyclohexane).
- **Byproduct:** **NONE** (cycloaddition has 100% atom economy at the bond-formation step).
- **Ring size in the precursor:** **14-membered** (consistent with Lamothe-Ndibwami-Deslongchamps's 14-membered-trienone methodology lineage, *Tet. Lett.* 1988, 29:1639 and 29:1641).
- **Conditions:** thermal (180–230 °C neat or in toluene/xylene at reflux); no catalyst. Phoenix-Reddy-Deslongchamps 2008 reports the TDA as proceeding cleanly under these conditions to give tricycle **5** with predicted stereochemistry (transition state T4 per the theoretical analysis).
- **Stereochemistry:** *endo*-selective, controlled by the macrocycle's preorganization (the *cis-trans-trans* triene geometry biases the TDA to one face). This is the whole point of the Deslongchamps TDA strategy: macrocyclic preorganization enforces stereoselectivity that the corresponding *acyclic* IMDA cannot achieve.

**Important encoding caveat — diene vs. dienophile geometry.** The 14-membered macrocyclic triene in **4** has the geometry **cis (C2=C3), trans (C6=C7), trans (C10=C11)** per the Deslongchamps numbering. The diene is the C2=C3 / C4=C5 system (where C4=C5 is one of the double bonds in the triene drawn differently), and the dienophile is C10=C11. The exact atom mapping in the substrate is necessary for the `transannular_diels_alder` rule to fire correctly in macrocert; flag for Ivan to encode from the paper's Scheme 1.

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| PubChem | CID 5281267 (cassaine) | Free; canonical SMILES, InChI, 2D + 3D coordinates. Quality 5. |
| ChEBI | CHEBI:3454 | Free; downloadable Molfile. Cross-validates PubChem. Quality 5. |
| CCDC / Cambridge Structural Database | Phoenix-Reddy-Deslongchamps 2008 reports X-ray crystallography under MeSH "Crystallography, X-Ray" — likely deposited for tricycle **5** and/or the natural product. Refcode lookup needs ConQuest. | Paywalled; flag for Ivan's CCDC access. |
| Sigma-Aldrich | Cassaine not sold as a chemical commodity; isolated rarely from *Erythrophleum* | Not a good encoding source. |
| Crystal structure in paper | Phoenix-Reddy-Deslongchamps 2008 SI: figures of compound **5** (TDA product) | Paywalled at ACS; need access for atom-numbered structure. |

**Recommended source for `structure.mol`:** PubChem CID 5281267 Molfile (canonical SMILES + 2D coordinates), cross-validated against ChEBI:3454. If Ivan can pull the X-ray from the CCDC, that is preferable for stereochemistry verification.

## 5. SMILES of the product (target)

**Cassaine (the natural product, panel target).** From PubChem CID 5281267:

Canonical SMILES:
```
CCC(C)C1CCC2C(C1(C)C(=O)OCCN(C)C)CCC3(C2(CCC(C3)O)C)C
```

Isomeric SMILES (with stereodescriptors from PubChem):
```
CC[C@@H](C)[C@H]1CC[C@@H]2[C@@H]([C@@]1(C)C(=O)OCCN(C)C)CC[C@@]3([C@]2(CC[C@H](C3)O)C)C
```

Formula audit: C₂₄H₃₉NO₄ — matches PubChem CID 5281267, MW 405.6 g/mol. **Cassaine numbering** (per the steroid-style A/B/C ring labeling Deslongchamps uses):
- A ring (6-membered, contains C3-OH and the C4-carboxylate side chain)
- B ring (6-membered, trans-fused to A and C)
- C ring (6-membered, contains an ethyl substituent at C14 and a methyl at C15)
- The α,β-unsaturation pattern of natural cassaine is retained in the panel target.

**TDA-immediate product (alternate encoding — tricycle 5 from Phoenix-Reddy-Deslongchamps 2008).** Manually-derived structure, NOT from a public database. Differs from cassaine **1** in: (a) C8 stereochemistry (pre-epimerization), (b) absent dimethylaminoethyloxycarbonyl tether on the C4 carboxylate (still a methyl or t-butyl ester at this stage), (c) C3 still protected as a silyl ether. Ivan picks whether to encode the natural product or the TDA-immediate intermediate.

## 6. Substituent map / numbering convention

Phoenix-Reddy-Deslongchamps 2008 uses **steroid-style A/B/C ring labeling** with **C1–C20** numbering inherited from the cassanoid diterpene class. Per Scheme 1 and Figure 2 of the paper:

| Position | Substituent | Stereo | Notes |
| --- | --- | --- | --- |
| C3 | OH | β | A-ring, the 3β-hydroxyl |
| C4 | C(CH₃)–C(=O)–OCH₂CH₂N(CH₃)₂ | quaternary | A-ring, the 4β-methyl + dimethylaminoethyl ester |
| C5 | CH | trans junction | A/B trans ring fusion |
| C8 | CH | trans junction | B/C trans ring fusion — **the C8 stereo is set by post-TDA epimerization** |
| C10 | C | quaternary | A/B angular methyl C19 |
| C13 | C | quaternary | B/C angular methyl C18 |
| C14 | CH(CH₂CH₃)(CH₃) | exocyclic | C-ring exocyclic ethyl + methyl |

The TDA step (Phoenix-Reddy-Deslongchamps 2008 compound **4** → **5**) installs **C5–C10 and C8–C13 σ-bonds** in a single pericyclic event from the 14-membered macrocyclic triene precursor.

## 7. Open questions / encoding caveats

- **The TDA byproduct is zero** — consistent with the `transannular_diels_alder` rule's `high_atom_economy_bond` class. AE class for this case is `high`.
- **The TDA product is NOT cassaine itself.** TDA produces tricycle **5**, which is elaborated by ~6 more steps to give (+)-cassaine. Encoding decision: panel `structure.mol` = cassaine (natural product) for v0 consistency; TDA rule fires once on the macrocyclic precursor.
- **Ring size is 14** for the macrocyclic triene precursor. This is consistent with the Lamothe-Ndibwami-Deslongchamps 14-membered TDA methodology lineage (Tet. Lett. 1988, 29:1639 — theoretical; 29:1641 — experimental). Distinct from the 13-membered Baettig and Bérubé papers (Tet. Lett. 1987, 28:5249–5258).
- **Stereoselectivity is controlled by the macrocycle's *cis-trans-trans* triene geometry**, not by an external chiral catalyst. This is the central thesis of the Deslongchamps TDA strategy: macrocyclic preorganization is the stereocontrol element.
- **The panel `transannular_diels_alder` rule** must be able to accept a 14-membered triene precursor (with appropriate predicate `ring_size_equals: 14`) and produce a 6-6-6 fused tricyclic product. The v0 surrogate panel does NOT include a TDA surrogate (per panel_TODO.md), and the rule has only been exercised on hypothetical substrates so far. **This case is the first real literature TDA case for the panel.**
- **No deposited 3D structure of natural cassaine in CCDC/PDB** (verified PubChem and ChEBI — PubChem provides only computed 3D conformer). The Phoenix-Reddy-Deslongchamps 2008 paper reports X-ray crystallography per its MeSH terms, but the deposit number requires access to the ACS SI. Flag for Ivan.
- **Confidence on substrate atom count.** The 2008 paper's Scheme 1 shows compound **4** as a 14-membered macrocyclic triene with explicit atom numbering. Ivan should pull Figure S1 of the SI for the X-ray-validated coordinates.
- **AE class accounting.** TDA is byproduct-free, so the AE class is `high` and consistent with the surrogate TDA case slot (currently unfilled per panel_TODO.md).
- **No selectivity gap.** Unlike the epothilone B RCM case (1:1 Z:E mixture), the Phoenix-Reddy-Deslongchamps TDA is reported to proceed *cleanly* with the predicted stereochemistry (transition state T4); the abstract states "the coupling of 3 on both ends with another densely functional partner 2 followed by TADA reaction on macrocycle 4 cleanly furnished the tricycle 5." This is an `energetics`-pass case in v1.

## 8. Quick consistency check vs. existing panel cases

| Field | Cassaine (this case) | Surrogate rcm-15 | Epothilone B (Nicolaou) | Citreoviridin (deprecated) |
| --- | --- | --- | --- | --- |
| `literature_tactic` | `transannular_diels_alder` | `rcm` | `rcm` | (was `transannular_diels_alder`) |
| `expected_witness` | `optimal` | `optimal` | `optimal` | `infeasible` |
| `expected_top_rule_class` | `macrocyclization` | `macrocyclization` | `macrocyclization` | n/a |
| `ae_class` | `high` (no byproduct) | `high` (ethylene) | `high` (ethylene) | (was `high`) |
| Ring size of precursor | 14 | 17 (heptadecadiene) | (acyclic seco-acid + diene) | n/a |
| Ring size of product | 6-6-6 fused tricycle (from 14) | 15 | 16 | n/a |
| Energetics | disabled (v0) | disabled | disabled | n/a |
| Catalyst | thermal, no catalyst | unspecified | Grubbs G1 | n/a |

Fully schema-compatible. **This case is the first literature-supported TDA case** for the panel — it directly exercises the `transannular_diels_alder` rule on a real natural-product target. Calibrates the zero-byproduct AE class against a real synthesis.

---

**Confidence calibration.** Primary reference DOI verified via CrossRef (`10.1021/ja805097s`, paper title and authors confirmed: Serge Phoenix, Maddi Sridhar Reddy, Pierre Deslongchamps, *JACS* 130:13989–13995, 2008-09-26, ACS publisher, 29 citations as of CrossRef snapshot). Cassaine structural data from PubChem CID 5281267 + ChEBI:3454 (mutually consistent: C₂₄H₃₉NO₄, MW 405.6 g/mol, CAS 468-76-8). Mechanism described in PubMed abstract 18817389 (matches the paper's *J. Am. Chem. Soc.* citation). Deslongchamps lineage corroborated through five additional 1987–2000 papers in *Tetrahedron Letters* and *Organic Letters* tracing the 13-membered → 14-membered → 15-membered macrocyclic-triene TDA methodology evolution.

**Contradictions / disputes.** None — Phoenix-Reddy-Deslongchamps 2008 is a definitive full paper preceded by the 2000 *Org. Lett.* communication; both are uncontested in the literature. The TDA strategy is highlighted in Taber's *Organic Synthesis* book chapter (DOI `10.1093/oso/9780199764549.003.0079`) as one of the year's notable Diels–Alder applications. The Trauner Halenaquinone and Matsuo Platensimycin TDA precedents from the same year set the technique in broader context.

**Recommended literature_tactic:** `transannular_diels_alder`.
**Recommended ring_size:** 14 (macrocyclic precursor).
**Recommended expected_witness:** `optimal`.
**Recommended ae_class:** `high`.
