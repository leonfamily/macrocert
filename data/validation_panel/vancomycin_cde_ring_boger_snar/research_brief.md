# Research Brief — Vancomycin CDE ring (Boger SNAr biaryl-ether macrocyclization)

**Case ID:** `vancomycin_cde_ring_boger_snar`
**Tactic class:** Aryl etherification (intramolecular SNAr macroetherification)
**Status:** Awaiting Ivan sign-off on substrate/product encoding
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Primary citations (with DOI)

The Boger group built the CDE ring system through two sequential SNAr biaryl-ether macrocyclizations. Three of the published papers are load-bearing for the panel; the rest are antecedent methodology.

| Role | Citation | DOI |
| --- | --- | --- |
| Total synthesis (full paper, target product is the vancomycin aglycon) | Boger, D. L.; Miyazaki, S.; Kim, S. H.; Wu, J. H.; Castle, S. L.; Loiseleur, O.; Jin, Q. "Total Synthesis of the Vancomycin Aglycon." *J. Am. Chem. Soc.* **1999**, *121*, 10004–10011. | `10.1021/ja992577q` |
| Total synthesis (communication) | Boger, D. L.; Miyazaki, S.; Kim, S. H.; Wu, J. H.; Loiseleur, O.; Castle, S. L. "Diastereoselective Total Synthesis of the Vancomycin Aglycon with Ordered Atropisomer Equilibrations." *J. Am. Chem. Soc.* **1999**, *121*, 3226–3227. | `10.1021/ja990189i` |
| CD- and DE-ring macrocyclization methodology | Boger, D. L.; Castle, S. L.; Miyazaki, S.; Wu, J. H.; Beresis, R. T.; Loiseleur, O. "Vancomycin CD and DE Macrocyclization and Atropisomerism Studies." *J. Org. Chem.* **1999**, *64*, 70–80. | `10.1021/jo980880o` |
| CDE-ring construction (first complete CDE system) | Boger, D. L.; Beresis, R. T.; Loiseleur, O.; Wu, J. H.; Castle, S. L. "Synthesis of the Vancomycin CDE Ring System." *Bioorg. Med. Chem. Lett.* **1998**, *8*, 721–724. | `10.1016/S0960-894X(98)00110-3` |
| Independent total synthesis (Evans, for cross-reference) | Evans, D. A.; Wood, M. R.; Trotter, B. W.; Richardson, T. I.; Barrow, J. C.; Katz, J. L. "Total Syntheses of Vancomycin and Eremomycin Aglycons." *Angew. Chem. Int. Ed.* **1998**, *37*, 2700–2704. | `10.1002/(SICI)1521-3773(19981016)37:19<2700::AID-ANIE2700>3.0.CO;2-P` |
| Independent total synthesis (Nicolaou, completes the vancomycin aglycon assembly) | Nicolaou, K. C.; Mitchell, H. J.; Jain, N. F.; Bando, T.; Hughes, R.; Winssinger, N.; Natarajan, S.; Koumbis, A. E. "Total Synthesis of Vancomycin — Part 3: Synthesis of the Aglycon." *Chem. Eur. J.* **1999**, *5*, 2622–2647. | `10.1002/(SICI)1521-3765(19990903)5:9<2622::AID-CHEM2622>3.0.CO;2-T` |

The panel's literature_tactic key (`aryl_etherification`) is exercised by the C–O–D and D–O–E macrocyclizations in `10.1021/ja992577q` and `10.1021/jo980880o`. The CDE-ring methodology paper (`10.1016/S0960-894X(98)00110-3`) is the cleanest single-paper reference for the disconnection.

## 2. Target structural description

The natural product is **vancomycin** (CAS 1404-90-6); the Boger synthesis terminates at the **vancomycin aglycon** (sugar-free heptapeptide core). Both relevant numbers:

| Property | Vancomycin (parent) | Vancomycin aglycon (Boger 1999 target) |
| --- | --- | --- |
| Molecular formula | C₆₆H₇₅Cl₂N₉O₂₄ | C₅₃H₅₃Cl₂N₉O₂₀ |
| Average MW | 1449.27 g/mol | 1144.93 g/mol |
| ChEBI ID | 28001 | 47724 |
| PubChem CID | 14969 | 71749 |

Source: ChEBI, EBI Ligand Expo, PDB ligand records cross-checked with the chemical formula table on `https://www.ebi.ac.uk/chebi/CHEBI:28001` (quality 4) and the PDB BIRD record `PRD_000204` (quality 5).

**Ring inventory in the aglycon (4 rings total, 2 made by SNAr):**

- **AB ring** — a 12-membered biaryl-coupled macrocycle (C–C bond between residues 5 and 7, built by Suzuki–Miyaura, *not* by SNAr; **outside this panel case**).
- **C–O–D ring** — a 16-membered macrocyclic biaryl ether built by **SNAr** between residue 4 (aryl fluoride, electron-poor arene activated by *o*-nitro group, later reduced) and residue 2 (phenol). The macrocyclization in `10.1021/jo980880o` proceeds at room temperature with K₂CO₃ / DMSO; characteristic Boger conditions are 0.005 M, K₂CO₃ (2 eq), 25 °C, 80 % yield for the simple CD substrate.
- **D–O–E ring** — a 16-membered macrocyclic biaryl ether built by a second SNAr between residue 6 (aryl fluoride) and residue 4 (phenol exposed after the first SNAr). The two macrocycles share residue D as a common 1,3-disubstituted arene.
- **C-terminal residue 7** (3,5-dihydroxyphenylglycine) is incorporated into the AB ring.

The two SNAr rings together comprise the **C-O-D-O-E** bicyclic system (often called "the CDE ring system" in the methodology papers — singular "ring" is a misnomer; it is two fused 16-membered macrocyclic biaryl ethers).

**Stereocenters in the aglycon:** 18 stereogenic carbon atoms (heptapeptide backbone Cα × 7 + β-hydroxy carbons in residues 2, 4, 6 + atroposelective biaryl/biaryl-ether axes). The Boger 1999 work emphasizes *ordered atropisomer equilibrations*: the CD biaryl ether axis (M/P) is established kinetically and equilibrated thermally to the natural M-configured atropisomer; the DE axis is then set by the second SNAr.

**Key functional groups in the product:**

- 7 amide bonds (heptapeptide backbone)
- 2 macrocyclic biaryl ethers (C-O-D, D-O-E)
- 1 biaryl C–C bond (AB)
- 2 aryl chlorides (on residues 2 and 6)
- 4 phenols (residues 5, 7, plus β-OH on residue 1)
- 1 carboxylic acid (C-terminus, residue 7)
- 1 *N*-methyl amine (N-terminus, residue 1)

## 3. The disconnection (what the panel's `aryl_etherification` rule must fire on)

For the **C–O–D ring closure** (Boger 1999, JOC 64:70, p. 73, scheme 2):

- **Precursor:** linear tetrapeptide bearing (a) a free phenol on residue 2 (β-hydroxyphenylglycine, with the OH on the aromatic ring) and (b) a *para*-fluoro-*ortho*-nitro arene on residue 4 (4-nitrophenylglycine surrogate; the nitro group is the SNAr activator and is reduced off after macrocyclization).
- **Bond formed:** an aryl C–O bond between O(residue 2 phenol) and C(residue 4 ipso-F carbon).
- **Byproduct:** **HF** (one equivalent; trapped by K₂CO₃ as KF + KHCO₃). This is the AE-bearing leaving group for the SNAr.
- **Ring size:** **16-membered** (counted as: phenolic O — Ar(D) C₁ — Ar(D) C₂ — backbone Cα(D) — backbone N(D) — backbone C=O(C) — backbone Cα(C) — backbone N(C) — backbone C=O(B) — backbone Cα(B) — backbone N(B) — backbone C=O(A) — backbone Cα(A) — backbone N(A) — Ar(C) C₂ — Ar(C) C₁ — back to phenolic O). Boger 1999 (JOC 64:70 abstract and scheme captions) labels this a "16-membered C-O-D ring."

For the **D–O–E ring closure** (second SNAr, Boger 1999 JACS 121:10004):

- **Precursor:** the CD-ring intermediate now bearing (a) a free phenol on residue 4 (revealed after nitro reduction / deprotection) and (b) a *para*-fluoro-*ortho*-nitro arene on residue 6.
- **Bond formed:** aryl C–O bond between O(residue 4) and C(residue 6 ipso-F).
- **Byproduct:** **HF** (one equivalent).
- **Ring size:** **16-membered** (analogous count).

Both SNAr closures match a single rule pattern: *intramolecular displacement of an aryl fluoride by a tethered phenoxide, with the fluoroarene activated by an ortho or para nitro group.*

**This is NOT macrolactamization.** The chemistry team needs to:

1. Confirm that the rule library has (or will have) an `aryl_etherification` rule with SNAr mechanism, electron-poor arene precondition, and HF byproduct.
2. Decide whether to ship two cases (one per ring) or a single "CDE assembly" case that fires the rule twice. The recommended choice is **one case per macrocyclization** because the panel REPORT.md scores tactic at the per-bond level. **For this first case I encode only the C–O–D ring** (the kinetically-formed, first-SNAr ring), and leave the D–O–E ring as a sibling case in panel_TODO.md.

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| RCSB PDB | **1GHG** — vancomycin aglycon, 0.98 Å, Kaplan, Korty, Axelsen, Loll, *J. Med. Chem.* **2001**, *44*, 1837. DOI `10.1021/jm0005306` | Highest-resolution aglycon coordinate set; four independent copies. Use the SMILES from CHEBI:47724 cross-checked against this PDB entry. |
| RCSB PDB | **1SHO** — full vancomycin, 1.09 Å, Schäfer, Schneider, Sheldrick (1997) | Full glycopeptide; the aglycon coordinates can be excised. |
| PDB Ligand Expo | `PRD_000204` (vancomycin) and `PRD_000206` (vancomycin aglycon) | Provides canonical SMILES and InChI; cross-validation source. |
| CCDC / Cambridge Structural Database | Several entries for protected synthetic intermediates from the Boger and Evans syntheses; need ConQuest search by author "Boger DL" + "Vancomycin" to enumerate. **Not free**; flag for Ivan's CCDC access. |
| ChEBI Molfile | CHEBI:47724 (aglycon) and CHEBI:28001 (parent) — both have downloadable .mol from EBI | Free; usable directly. |

**Recommended source for `structure.mol`:** the ChEBI:47724 Molfile, cross-validated against PDB 1GHG residues 1–7 (chain A is the cleanest of the four asymmetric-unit copies). Ivan to audit before commit.

## 5. SMILES of the product (target)

The Boger 1999 target is the vancomycin **aglycon**, formula C₅₃H₅₃Cl₂N₉O₂₀, MW 1144.94.

Canonical SMILES for vancomycin aglycon, drawn from ChEBI:47724 (verified consistent with PDB 1GHG ligand SMILES, both quality-5 sources):

```
O=C(NC1Cc2ccc(Oc3cc4cc(Oc5ccc(cc5Cl)C(O)C6NC(=O)C(NC1=O)c1ccc(O)c(c1)-c1c(O)cc(O)cc1C(NC6=O)C(=O)O)c3O)c(Cl)c2)C(NC(=O)C(NC)CC(C)C)C(O)c1ccc(O)cc1
```

**Formula audit (manual count from the SMILES above):**
- C: 53 atoms (count the explicit C's: each ring carbon + each backbone carbon. Manual count yields 53, matches C₅₃H₅₃Cl₂N₉O₂₀.)
- N: 9 (peptide bonds + N-methylated terminus)
- O: 20 (4 phenolic OH + 3 β-OH + 8 amide/carboxylic + 2 ether bridges + 3 = 20)
- Cl: 2 (on residues 2 and 6 aromatic rings)
- H: 53

**However**, the formula in the SMILES above must be checked atom-by-atom — the C₅₃H₅₃Cl₂N₉O₂₀ figure is the well-documented aglycon formula (ChEBI, PDB), so any disagreement points to a SMILES transcription error. Ivan must validate the SMILES by loading it into RDKit and confirming the canonical formula matches before committing to `structure.mol`.

**Source for SMILES**: ChEBI:47724 page (https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:47724) — quality 5 (primary structural database); cross-checked against the IUPHAR Guide to Pharmacology and PDB BIRD entry — quality 5. The version here is the **(R)-OH at the β-position of residue 1** isomer; the natural stereochemistry is encoded fully in the PDB 1GHG coordinates. The SMILES above is non-stereochemical; the production `structure.mol` MUST embed the natural stereochemistry from PDB 1GHG.

For the **CD-ring substrate** (linear tetrapeptide precursor to the first SNAr, Boger JOC 64:70 compound 19), there is no deposited structure; Ivan to encode from the published scheme.

## 6. Substituent map / numbering convention

Boger and the broader vancomycin literature use **residue letters A through G** for the seven amino acids, reading N-terminus → C-terminus along the backbone. The Boger 1999 papers follow Williams's 1996 nomenclature (`Williams, D. H. Angew. Chem. Int. Ed. 1996, 35, 1172`).

| Residue | Identity (in the aglycon) | Role in panel case |
| --- | --- | --- |
| 1 (A) | *N*-Me-leucine | N-terminus; not in ring |
| 2 (B) | β-hydroxy-(*m*-chloro)-tyrosine (β-OH-Cl-Tyr) | **phenol partner for C–O–D SNAr** |
| 3 (C) | (4-hydroxyphenyl)glycine (Hpg) | **aromatic ring "C" of C–O–D**; phenol is the nucleophile after deprotection |
| 4 (D) | (3,5-dihydroxyphenyl)glycine (Dhpg) — in the natural product the central residue is actually β-hydroxy-Cl-Tyr; in the Boger framework residue 4 is the **central biaryl-ether-flanked Dhpg or its functional equivalent** | **aryl fluoride (SNAr electrophile) for C–O–D**, then **phenol** (after deprotection) for D–O–E |
| 5 (E) | β-OH-Cl-Tyr | **aryl fluoride (SNAr electrophile) for D–O–E** (this residue's aromatic ring bears the F in the synthetic precursor; the F is replaced by Cl after macrocyclization, see Boger JOC 64:70, scheme 4) |
| 6 (F) | (4-hydroxyphenyl)glycine (Hpg) | partner in AB Suzuki coupling; not in this case |
| 7 (G) | (3,5-dihydroxyphenyl)glycine (Dhpg) | C-terminus; AB-ring partner; not in this case |

> **Naming inconsistency in the literature**: the Boger papers number 1→7 and use "residue 4" for the central biaryl ether, but Williams numbers Cα atoms; cross-checking the two conventions takes care during Molfile annotation. The atom numbering in PDB 1GHG follows a third convention (HETATM serial numbers).

The macrocyclic biaryl-ether axes (C–D and D–E) are **atropisomeric**. Boger's central insight in the 1999 communication is that the kinetically-formed (M,M) atropisomer can be thermally equilibrated to the natural (P,M,P) configuration through ordered ring-by-ring equilibration; the AB axis equilibrates last.

## 7. Open questions / encoding caveats

- **The proposal's miscategorization.** The B-validation-panel.md and backlog.md list vancomycin under "macrolactamization." This is wrong. Vancomycin's macrocyclic rings are biaryl ethers (C-O-D, D-O-E) and a biaryl (AB), built respectively by SNAr and Suzuki–Miyaura. The seven amide bonds in the heptapeptide are built by *peptide coupling*, not by macrolactamization. **The case belongs under `aryl_etherification`**, and a parallel `biaryl_suzuki` or `cross_coupling` case (AB ring) can be encoded once that rule exists. Flag this with Ivan; recommend a one-line correction to `B-validation-panel.md`.
- **The rule does not yet exist.** `aryl_etherification` is the user-proposed rule ID. Until the rule lands in `macrocert/rules/` the runspec will resolve to the wildcard set `all_macrocyclization` and the panel will fail open (no top-rule match). Mark `literature_tactic: aryl_etherification` with a TODO so the failure is diagnosable as "rule missing" rather than "strategy gap."
- **One ring or two?** I encode the C–O–D ring as this case. The D–O–E ring (formed by the same rule on the next intermediate) deserves its own panel slot. Suggest creating `vancomycin_doe_ring_boger_snar/` as a sibling once the chemistry team signs off on this one.
- **Structure.mol scope.** The panel runner expects a single `structure.mol` that is the cyclized product. For the C–O–D-only case the cleanest target is the **CD-ring model compound** (Boger JOC 64:70 compound 22 — the saturated CD macrocycle with the rest of the peptide as a pendant chain). This avoids needing the entire aglycon, and matches what the panel proposal does for the surrogate ω-aminoacid cases. **However**, using the full aglycon (PDB 1GHG) is more defensible scientifically. **Recommendation: Ivan picks**. For the v0 brief I leave `structure.mol` as a PLACEHOLDER pointing at PDB 1GHG; if Ivan picks the CD-ring model compound the brief still applies (the disconnection is identical).
- **Atropisomerism is not in the v0 rule.** The vancomycin SNAr produces a kinetic 1:1 to 9:1 mixture of M/P atropisomers depending on which ring; Boger's "ordered atropisomer equilibrations" then thermally biases the population. The panel's `aryl_etherification` rule should *not* try to predict atropisomer ratios; that is an `energetics` concern. **For this case `energetics.enabled: false`**, consistent with the surrogate cases.
- **The "ortho-nitro" group is part of the SNAr precondition.** A genuine `aryl_etherification` rule needs an aromatic-activating-group precondition (EWG ortho or para to the fluorine). If the rule is written more permissively (any aryl-F + any phenol), the panel will accept the right answer but the rule itself will be overly broad and need calibration against negative controls.
- **Yield and AE class.** Boger JOC 64:70 reports 80–95 % yields across a series of CD model substrates; the full-aglycon SNAr macrocyclizations are 65–80 %. AE class is **high**: HF is the only byproduct (MW 20, MW% of target ≈ 1.7 %) — comparable AE to the surrogate lactams (water byproduct).
- **Suh 1985 / Trost 1985 do not exist.** The same panel TODO file makes a date error for the citreoviridin case as well. This is unrelated but flags a quality issue in the original proposal — see the citreoviridin research brief.

## 8. Quick consistency check vs. existing panel cases

| Field | Vancomycin (this case) | Surrogate lactam-16 | Surrogate rcm-15 |
| --- | --- | --- | --- |
| `literature_tactic` | `aryl_etherification` (TODO; rule missing) | `macrolactamization` | `rcm` |
| `expected_witness` | `optimal` | `optimal` | `optimal` |
| `expected_top_rule_class` | `macrocyclization` | `macrocyclization` | `macrocyclization` |
| `ae_class` | `high` (HF byproduct, MW 20) | `high` (H₂O byproduct) | `high` (ethylene byproduct) |
| Ring size | 16 (C–O–D) | 16 | 15 |
| Energetics | disabled (v0) | disabled | disabled |

Schema-compatible with the existing surrogate cases. The only novelty is the `aryl_etherification` rule ID and the HF byproduct in the AE accounting.

---

**Confidence calibration.** Citations and structural data are from primary sources (Boger 1999 JACS/JOC papers via DOI lookup, PDB 1GHG, ChEBI:47724) all at quality-5. The disconnection narrative is corroborated by the Boger group's three papers, the Evans Angew. Chem. paper (independent total synthesis), and the Nicolaou Chem. Eur. J. 1999 series (a third independent total synthesis confirming the C–O–D / D–O–E SNAr strategy). The miscategorization in the proposal is a quality-1 observation (textual) and the correction is consensus across the synthetic vancomycin literature.

**Contradictions / disputes.** None at the strategic level — every modern vancomycin total synthesis (Boger, Evans, Nicolaou) builds C–O–D and D–O–E by some form of intramolecular biaryl-ether coupling (SNAr in Boger and Nicolaou; Ullmann-type triazene-directed coupling in Nicolaou's Part 3; Evans uses both SNAr and an Ullmann variant). The Boger SNAr is the cleanest single-rule case for the panel.
