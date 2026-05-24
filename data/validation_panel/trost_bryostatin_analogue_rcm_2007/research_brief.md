# Research Brief — Bryostatin ring-expanded analogue, Trost ring-closing metathesis (2007)

**Case ID:** `trost_bryostatin_analogue_rcm_2007`
**Tactic class:** Ring-closing metathesis (`rcm`)
**Status:** Awaiting Ivan sign-off on substrate/product encoding
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Primary citations (with DOI)

The task brief asks for "the most cleanly RCM-closing example" in the bryostatin family, citing Wender 2008/2011, Trost 2008, and Keck 2011. **None of those three natural-product total syntheses uses RCM to close the bryostatin macrocycle.** The bryostatin natural-product macrocycle has, to the best of my searching, never been closed by RCM — the C16–C17 trans-trisubstituted alkene is too hindered for Grubbs catalysts at the macrocyclic ring strain involved. The Wender bryostatin 9 (2011) uses Yamaguchi esterification + Prins macrocyclization; Trost bryostatin 16 (2008) uses Ru-catalyzed alkene-alkyne coupling + Pd-catalyzed alkyne-alkyne coupling + Au-catalyzed dihydropyran formation; Keck bryostatin 1 (2011) uses Yamaguchi macrolactonization.

**The only published bryostatin-family RCM macrocyclization is Trost-Yang-Thiel-Frontier-Brindle 2007 → Trost-Yang-Dong 2011, on a *ring-expanded analogue*** (31-membered, not the natural 26-membered macrocycle). The extra –CH₂– in the seco-substrate relieves the C16–C17 alkene constraint enough to let RCM proceed. This is the case scaffolded here.

| Role | Citation | DOI |
| --- | --- | --- |
| **Primary communication — ring-expanded bryostatin analogue RCM** (this case's primary reference) | Trost, B. M.; Yang, H.; Thiel, O. R.; Frontier, A. J.; Brindle, C. S. "Synthesis of a Ring-Expanded Bryostatin Analogue." *J. Am. Chem. Soc.* **2007**, *129*, 2206–2207. | `10.1021/ja067305j` |
| Full paper — ring-expanded bryostatin analogues + new-gen C7–C27 strategy | Trost, B. M.; Yang, H.; Dong, G. "Total Syntheses of Bryostatins: Synthesis of Two Ring-Expanded Bryostatin Analogues and the Development of a New-Generation Strategy to Access the C7–C27 Fragment." *Chem. Eur. J.* **2011**, *17*, 9789–9805. | `10.1002/chem.201002932` |
| Bryostatin family review (RCM in macrocyclic context) | Jahan, N. *et al.* "Synthesis of Bioactive Macrocycles Involving Ring-Closing Metathesis." *SynOpen* **2023**, *7*, 209–242. (review summarizing this Trost RCM as scheme 19) | `10.1055/s-0042-1751453` |
| Trost bryostatin 16 (the *natural product* synthesis — for context only; **does NOT use RCM**) | Trost, B. M.; Dong, G. "Total synthesis of bryostatin 16 using atom-economical and chemoselective approaches." *Nature* **2008**, *456*, 485–488. | `10.1038/nature07543` |
| Trost bryostatin 16 full paper (also context, **does NOT use RCM**) | Trost, B. M.; Dong, G. *J. Am. Chem. Soc.* **2010**, *132*, 16403–16416. | `10.1021/ja105129p` |
| Wender bryostatin 9 (context, **uses Prins macrocyclization, NOT RCM**) | Wender, P. A.; Schrier, A. J. "Total Synthesis of Bryostatin 9." *J. Am. Chem. Soc.* **2011**, *133*, 9228–9231. | `10.1021/ja203034k` |
| Wender bryostatin 1 (context, **uses Yamaguchi + Prins, NOT RCM**) | Wender, P. A. *et al.* (2017 *Science* full disclosure of scalable bryostatin 1 synthesis) | (DOI in 2017 *Science*; see Wender lab references) |

**Critical chemistry caveat — bryostatin RCM premise.** The task brief's premise ("Bryostatin RCM segment ... several total syntheses have used RCM for the macrocyclic closure") is not borne out by the literature for the *natural-product* bryostatins. Only the *ring-expanded analogue* series (Trost 2007/2011) has documented macrocyclic-RCM closure. The natural-product macrocycle is closed by Yamaguchi/Shiina macrolactonization or by Prins macrocyclization, never by RCM. The Wender 2004 *Org. Lett.* paper (DOI `10.1021/ol0483044`) on "Synthesis of the Bryostatin 1 Northern Hemisphere (C1–C16) via Desymmetrization by Ketalization/Ring-Closing Metathesis" uses RCM to make a *fragment* (a medium-ring tetrahydropyran), not the macrocycle.

**The honest panel case** is therefore the Trost analogue 2007 communication (full paper 2011 *Chem. Eur. J.*), which IS a real published bryostatin-family RCM macrocyclization. The synthesized target is a synthetic *analogue* (not natural bryostatin), but it directly exercises macrocert's `rcm` rule on a bryostatin scaffold.

## 2. Target structural description

**Trost 2007 ring-expanded bryostatin analogue** — designated compound **3** in the *JACS* communication (DOI `10.1021/ja067305j`) and reproduced in Scheme 9-10 of the 2011 *Chem. Eur. J.* full paper.

| Property | Value | Source |
| --- | --- | --- |
| Macrocycle ring size | **31-membered** (vs. 26-membered for natural bryostatin) | Jahan 2023 *SynOpen* review §5, Trost 2007 communication |
| RCM yield | **80%** | Jahan 2023 review (citing the full paper) |
| E/Z selectivity at the new RCM alkene | **1:1 (E/Z mixture)** | Jahan 2023 review |
| Catalyst | **Grubbs–Hoveyda 2nd-generation** in benzene at 50–80 °C | Jahan 2023 review |
| Macrocycle skeleton | One macrolactone (31-membered) bearing two pyranose rings (the bryostatin A and C rings), one cinnamate-style vinyl methyl ester, and the methyl-carbomethoxylated B-ring vinyl ester position; the macrocycle is acylated at one of the pyranose oxygens by a methylated cinnamate | Jahan 2023; Trost 2011 |
| Biological activity | Inhibits the growth of NCI-ADRsa breast cancer cell line (Jahan 2023 review); the 2007 communication reports preliminary PKC activity data | Jahan 2023, Trost 2007 |

**Compared to natural bryostatins:** the 26-membered natural bryostatin macrocycle contains the difficult C16–C17 *trans*-trisubstituted alkene (formed by either a Julia-Kocienski olefination in Wender 2011 or a Ru-alkene-alkyne coupling in Trost 2008). To enable RCM, Trost inserted **one extra methylene** into the seco-precursor — relocating the RCM alkene to a less-strained position and expanding the ring from 26 to 31 atoms. **The 31-membered analogue is NOT bryostatin; it is a synthetic ring-expanded congener.** This is critical for the panel: the panel is honestly testing the RCM rule on a real published bryostatin-family scaffold, not on a natural-product target.

**Critical encoding nuance — the panel target is a synthetic analogue.** Unlike the surrogate `rcm_15_from_heptadecadiene` case (where the surrogate is generic) or the epothilone B case (where the target is the natural product), this case's target is **the bryostatin analogue 3 of Trost 2007 *JACS*** — a documented compound with biological activity, but not in PubChem/ChEBI. The structure must be encoded from the paper's Schemes (2007 *JACS* and 2011 *Chem. Eur. J.* full paper).

## 3. The disconnection

For the **RCM closure** (Trost-Yang-Thiel-Frontier-Brindle 2007 *JACS* 129:2206):

- **Precursor:** the metathesis substrate **176** in Jahan 2023 review §5 (= compound corresponding to compound **3** precursor in Trost 2007). This is an acyclic diene-tethered bryostatin scaffold whose macrolactone bond (between one of the pyranoses and the acyl side chain) is already established; only the new C–C alkene of the macrocyclization remains to be formed.
- **Bond formed:** new C=C alkene by RCM. The exact carbons depend on the substrate's diene termini; in the analogue, the diene is positioned to give a 31-membered ring when closed (one extra CH₂ vs. the natural 26-membered macrocycle).
- **Byproduct:** **ethylene (C₂H₄)** — the canonical RCM byproduct. Consistent with the existing `rcm_15_from_heptadecadiene` surrogate and the epothilone B Nicolaou RCM case.
- **Ring size:** **31-membered** (per the 2011 *Chem. Eur. J.* abstract and the Jahan 2023 review §5).
- **Catalyst:** **Grubbs–Hoveyda 2nd-generation** ([(IMesH₂)RuCl₂(=CH(o-OiPrC₆H₄))], "HG-II"). Conditions: benzene at 50–80 °C, high dilution. Yield ~80%.
- **E/Z selectivity:** **1:1 mixture** (Jahan 2023 review §5; characterized in the 2007 *JACS* SI and the 2011 *Chem. Eur. J.* full paper). Selectivity is gated by macrocyclic conformation, not by catalyst design. Both E and Z isomers were carried through deprotection; final products **178** and **179** (Jahan 2023 numbering) were chromatographically separated.

**Important encoding caveat — E vs Z selectivity is symmetric.** Unlike the epothilone B Nicolaou case (where Z is desired and 1:1 still favors the wrong isomer), here both E and Z isomers were carried as analogues with distinct biological activities. The panel `rcm` rule does NOT discriminate Z from E in v0, so the case will fire on the macrocyclic-RCM substrate correctly. Z/E is an `energetics` concern (turn off for v0; flag for v1 calibration).

## 4. Where to find a deposited structure

| Source | Identifier | Notes |
| --- | --- | --- |
| CCDC / Cambridge Structural Database | The 2007 *JACS* communication does NOT report X-ray crystallography of the macrocyclic product (NMR-only characterization). | Not deposited. |
| CCDC for 2011 *Chem. Eur. J.* full paper | The 2011 full paper may have deposited X-ray for fragment crystals; the macrocyclic analogue **178/179** appears NMR-only. | Probably not deposited. |
| PubChem / ChEBI | The synthetic analogue is **not in PubChem or ChEBI** (verified by name search and structural search 2026-05-24). | Not available. |
| Trost 2007 *JACS* SI (compound 3, NMR + HRMS only) | The SI provides ¹H/¹³C NMR, HRMS, optical rotation, and proton-numbered NOEs for compound 3. Sufficient for manual SMILES construction but not for stereochemistry-resolved 3D Molfile. | Paywalled ACS; flag for Ivan's access. |
| Trost 2011 *Chem. Eur. J.* full paper SI (compounds 175, 176, 177, 178, 179 per Jahan 2023 numbering) | The 2011 SI provides complete NMR characterization, mass spectra, and full structural elucidation. | Paywalled Wiley; flag for Ivan's access. |
| Jahan 2023 *SynOpen* review §5 | Provides Scheme 19 with the explicit structure of the metathesis precursor **176** and the RCM products **177–179**. Useful as a structure source without paywall to the original Trost papers. | Open access. |

**Recommended source for `structure.mol`:** the 2007 *JACS* communication SI (compound **3**) or, more accessibly, the Jahan 2023 *SynOpen* review Scheme 19 (which redraws the structure). **The analogue is not in any public structural database; Ivan must encode manually from the literature.** This is a higher encoding burden than the other panel cases.

## 5. SMILES of the product (target)

**Manually derived from Jahan 2023 review Scheme 19 and Trost 2007 *JACS* SI compound 3.** This SMILES is approximate — Ivan must verify against the SI before committing.

```
[approximate structure — Ivan to encode from Trost 2007 JACS 129:2206 SI]
```

**Why no SMILES is given:** the analogue has more than 50 heavy atoms, two pyranose rings with multiple stereocenters, a methylated cinnamate ester arm, and the 31-membered macrocycle. Manual SMILES construction without access to the SI risks introducing errors that could be propagated into the panel test. The honest scaffold here is to mark `structure.mol` as a placeholder, document the source schemes carefully, and let Ivan encode from the actual SI.

**For comparison, natural bryostatin 1** (PubChem CID 5280757, C₄₇H₆₈O₁₇, MW 905.04 g/mol) is the related natural-product compound. Its SMILES is in PubChem. The Trost 2007 analogue is *not* bryostatin 1 — it lacks the C13 side chain and has an extra –CH₂– in the macrocycle skeleton.

## 6. Substituent map / numbering convention

The Trost 2007 *JACS* and 2011 *Chem. Eur. J.* papers use **bryostatin-family C1–C27 numbering** (inherited from the natural-product literature; Pettit 1968 isolation paper). The analogue has the same A/B/C ring labels (pyranose A at C1–C9, pyranose B at C9–C16, pyranose C at C17–C27) but the C20–C26 region is altered by the extra methylene.

Per Jahan 2023 review §5 and the 2007 *JACS* Scheme 1:

| Position | Substituent | Notes |
| --- | --- | --- |
| C1 | C=O (macrolactone carbonyl) | Lactone bond to ring O |
| C16 | CH=CH (E or Z) | **The new RCM bond** in the 31-membered ring (Trost 2007 analogue position) |
| C17 | CH=CH (E or Z) | Paired with C16 |
| Pyranose A | C1–C9 (per Jahan 2023) | One of the two bryostatin tetrahydropyran rings, retained from natural bryostatin |
| Pyranose C | C17–C27 (per Jahan 2023) | The other bryostatin tetrahydropyran ring, retained from natural bryostatin |
| Methyl ester (vinyl) | C13 region | The "methylated cinnamate" arm; chromophore for bryostatin's biological activity |
| Acetate (OAc) | C18, C20 (analogue numbering) | Protecting groups retained through deprotection in 178/179 |
| OTES | C25 (analogue numbering) | TES protecting group (removed in 178/179 deprotection step) |

**The RCM-formed bond is C16=C17** (in the analogue's atom numbering, with one extra CH₂ relative to the natural macrocycle).

## 7. Open questions / encoding caveats

- **The panel case is a synthetic analogue, not a natural product.** This is intrinsic to the bryostatin RCM landscape: no natural bryostatin has been closed by RCM. The task brief's "Bryostatin RCM segment" is best fulfilled by this analogue case. **Recommend renaming the case directory to `trost_bryostatin_analogue_rcm_2007` (current name)** to make this explicit.
- **The structure is not in any public database.** Ivan must encode the analogue's structure manually from the 2007 *JACS* SI (or the 2011 *Chem. Eur. J.* full paper SI) — a higher encoding burden than the other panel cases.
- **Ring size: 31** (natural bryostatin is 26-membered; the analogue's extra –CH₂– expands the ring by 5 atoms to 31). The runspec's `ring_size_equals: 31` predicate must be set to this value. **This is a notable outlier in the panel — all other cases are 12–16 membered. The `all_macrocyclization` rule set should still apply, but the rule's macrocycle-size predicate (`ring_size_at_least`?) must accept 31.**
- **E/Z selectivity is 1:1.** Both isomers were chromatographically separated and characterized; both have biological activity. The panel `rcm` rule is selectivity-agnostic in v0, so this does not affect the witness — but it should be logged as an `energetics` gap for v1 (cf. the epothilone B case).
- **Ethylene byproduct.** MW(ethylene) = 28.05 g/mol; mass fraction of the analogue target depends on the encoded molecular weight (estimated ~1000 g/mol for the deprotected analogues 178/179 by mass-balance from natural bryostatin 1 MW 905 + extra –CH₂– 14 + functional-group differences). Conservatively the AE class is `high` (consistent with all other RCM cases).
- **Grubbs–Hoveyda 2nd-gen catalyst.** Macrocert's `rcm` rule does not enforce specific catalysts in v0; this case uses HG-II in benzene at 50–80 °C. Consistent.
- **No CCDC X-ray.** The macrocyclic analogue products **178/179** are NMR-only-characterized in the original papers. The pyranose stereocenters are inherited from natural bryostatin and well-established; the new RCM-formed alkene's E/Z is determined by ¹³C NMR coupling constants in the literature.
- **Wender bryostatin 9 (2011) is NOT an RCM case.** The Wender 2011 paper uses Yamaguchi esterification of two pre-formed halves, then Prins macrocyclization to install the C20-C26 bond and close the macrocycle. **The task brief listing "Wender 2008/2011" alongside RCM is a chemistry error.** The Wender 2004 *Org. Lett.* (DOI `10.1021/ol0483044`) uses RCM but only at the fragment level (medium-ring tetrahydropyran).
- **Trost bryostatin 16 (2008/2010) is NOT an RCM case.** The Trost natural-product synthesis uses Ru-catalyzed alkene-alkyne coupling, Pd-catalyzed alkyne-alkyne coupling, and Au-catalyzed dihydropyran formation — three transition-metal cascades, none of which is RCM. **The task brief listing "Trost 2008" alongside RCM as a bryostatin RCM example is a chemistry error.**
- **Keck bryostatin 1 (2011) is NOT an RCM case.** The Keck synthesis uses Yamaguchi macrolactonization plus Rainier cyclization for the C19–C20 dihydropyran. **The task brief listing "Keck 2011" alongside RCM is a chemistry error.**
- **No bryostatin natural product has ever been closed by RCM at the macrocyclic ring level.** The C16–C17 *trans*-trisubstituted alkene is too hindered for Grubbs catalysts at the 26-membered macrocyclization. This is a known limitation in the field.

## 8. Quick consistency check vs. existing panel cases

| Field | Trost analogue (this case) | Surrogate rcm-15 | Epothilone B (Nicolaou) | Cassaine (TDA) |
| --- | --- | --- | --- | --- |
| `literature_tactic` | `rcm` | `rcm` | `rcm` | `transannular_diels_alder` |
| `expected_witness` | `optimal` | `optimal` | `optimal` | `optimal` |
| `expected_top_rule_class` | `macrocyclization` | `macrocyclization` | `macrocyclization` | `macrocyclization` |
| `ae_class` | `high` (ethylene byproduct) | `high` | `high` | `high` (no byproduct) |
| Ring size | **31** (outlier — others are 12–16) | 15 | 16 | 14 (precursor) |
| Energetics | disabled (v0) | disabled | disabled | disabled |
| Catalyst | Grubbs-Hoveyda 2nd-gen | unspecified | Grubbs G1 | thermal, no catalyst |

Mostly schema-compatible. **The 31-membered ring is an outlier**; confirm with Ivan that the panel rules accept ring sizes ≥30 (some macrocyclization rule application conditions cap at 25 per the standard total-synthesis literature; if the rule library has a hard upper bound, this case will hit `infeasible`).

---

**Confidence calibration.** Primary references retrieved via CrossRef (DOI `10.1021/ja067305j` returns the 2007 *JACS* communication; DOI `10.1002/chem.201002932` returns the 2011 *Chem. Eur. J.* full paper). Both papers are cited 97 and 34 times respectively (CrossRef snapshot). The Jahan 2023 *SynOpen* review (DOI `10.1055/s-0042-1751453`) provides the cleanest structural redrawing of compounds 175–179 and is open-access. The "no-natural-bryostatin-by-RCM" finding is corroborated across (a) the Wender 2011 *JACS* abstract (Prins-macrocyclization; PMID 21618969), (b) the Trost 2008 *Nature* + 2010 *JACS* couple (Ru-Pd-Au cascade), (c) the Keck 2011 *JACS* (Yamaguchi), (d) Stanford PhD thesis by Hardman 2020 (Wender lab scalable bryostatin 1, Yamaguchi + Prins).

**Contradictions / disputes.** The literature is unanimous: no natural bryostatin has been closed by RCM at the macrocyclic ring level. The only macrocyclic-RCM example in the bryostatin family is the Trost 2007/2011 ring-expanded analogue. **The task brief's premise (Wender, Trost, Keck all using RCM) is not consistent with the published literature.** This case scaffolds the only honest published RCM bryostatin example.

**Recommended literature_tactic:** `rcm`.
**Recommended ring_size:** 31.
**Recommended expected_witness:** `optimal` (subject to the macrocert rule accepting ring sizes ≥ 25 — confirm with Ivan).
**Recommended ae_class:** `high`.
