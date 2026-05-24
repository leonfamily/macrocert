# trost_bryostatin_analogue_rcm_2007

**STATUS: Awaiting Ivan sign-off.** structure.mol is a placeholder.

This case fulfills the panel_TODO.md "Bryostatin RCM" slot via the
only published bryostatin-family RCM macrocyclization (a synthetic
*ring-expanded analogue*, not natural bryostatin). The task brief's
premise — that Wender 2008/2011, Trost 2008, and Keck 2011 all used
RCM for the natural-product macrocycle — is not consistent with the
published literature. See research_brief.md §1 and §7 for the
detailed diagnosis.

## Provenance

- **Primary communication:** Trost, B. M.; Yang, H.; Thiel, O. R.; Frontier, A. J.; Brindle, C. S. "Synthesis of a Ring-Expanded Bryostatin Analogue." *J. Am. Chem. Soc.* **2007**, *129*, 2206–2207. DOI `10.1021/ja067305j`.
- **Full paper:** Trost, B. M.; Yang, H.; Dong, G. "Total Syntheses of Bryostatins: Synthesis of Two Ring-Expanded Bryostatin Analogues and the Development of a New-Generation Strategy to Access the C7–C27 Fragment." *Chem. Eur. J.* **2011**, *17*, 9789–9805. DOI `10.1002/chem.201002932`.
- **Open-access review with redrawn structures:** Jahan, N. *et al.* "Synthesis of Bioactive Macrocycles Involving Ring-Closing Metathesis." *SynOpen* **2023**, *7*, 209–242. DOI `10.1055/s-0042-1751453`. (See Scheme 19 for the explicit structures of compounds **173–179**.)
- **Natural-product context (no RCM in these — for comparison only):**
    - Trost, B. M.; Dong, G. *Nature* **2008**, *456*, 485 (DOI `10.1038/nature07543`). Bryostatin 16 via Ru-Pd-Au cascade.
    - Wender, P. A.; Schrier, A. J. *J. Am. Chem. Soc.* **2011**, *133*, 9228 (DOI `10.1021/ja203034k`). Bryostatin 9 via Yamaguchi + Prins.
    - Keck, G. E. *J. Am. Chem. Soc.* **2011**, *133*, 744. Bryostatin 1 via Yamaguchi + Rainier.

## Encoding caveats

1. **The panel case is a synthetic analogue, not a natural product.** This is intrinsic to the bryostatin-RCM landscape. No natural bryostatin has been closed by RCM at the macrocyclic ring level — the C16–C17 *trans*-trisubstituted alkene is too hindered for Grubbs catalysts at the 26-membered macrocyclization. The Trost 2007 analogue inserts one extra –CH₂– into the seco-precursor, relocating the RCM alkene and expanding the macrocycle to 31 members; this relieves the strain enough to let RCM proceed.
2. **The structure is not in any public database (PubChem, ChEBI, CCDC verified).** Ivan must encode the analogue's structure manually from the 2007 *JACS* SI (or the 2011 *Chem. Eur. J.* full paper SI). The Jahan 2023 *SynOpen* review §5 Scheme 19 is the cleanest accessible redrawing.
3. **Ring size: 31.** This is an outlier in the panel (all other cases are 12–16 membered). Confirm with Ivan that the panel rules accept ring sizes ≥ 30 — some macrocyclization rule application conditions in the standard total-synthesis literature cap at 25.
4. **Byproduct: ethylene** (28.05 g/mol). Mass fraction = 28.05 / (estimated 1000) ≈ 2.8 % for the deprotected analogue 178/179. High AE band, consistent with the surrogate `rcm_15_from_heptadecadiene` and epothilone B cases.
5. **E/Z selectivity: 1:1.** Both isomers were chromatographically separated and characterized; both compounds (**178** and **179** in the Jahan 2023 numbering) have anticancer activity. The panel `rcm` rule is selectivity-agnostic in v0; this is an `energetics` gap for v1.
6. **Catalyst: Grubbs–Hoveyda 2nd-gen** in benzene at 50–80 °C, high dilution. ~80% yield (Jahan 2023 reports the 80% yield directly).
7. **Chemistry-error documentation in research_brief.md §1 and §7.** The task brief's premise about Wender 2008/2011, Trost 2008, and Keck 2011 all using RCM for the bryostatin macrocycle is not consistent with the published literature. Documented in the brief; flag for Ivan.
8. **structure.mol is a PLACEHOLDER.** No public-database source exists. The 2007 *JACS* SI is the canonical source for compound **3**; Ivan to encode from there.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja067305j`, `10.1002/chem.201002932`, `10.1055/s-0042-1751453`, `10.1038/nature07543`, `10.1021/ja203034k`, `10.1021/ja105129p`).
- Bryostatin-RCM-non-existence corroboration: Wender 2011 abstract (PMID 21618969), Trost 2008 *Nature* abstract, Hardman PhD thesis (Stanford 2020, Wender lab), Jahan 2023 *SynOpen* review Tables.
- Citation cross-check: Trost 2007 *JACS* has 97 citations and Trost 2011 *Chem. Eur. J.* has 34 citations in CrossRef's snapshot — both are well-cited papers in the bryostatin SAR literature.
- The Jahan 2023 review is open-access and provides the cleanest published redrawing of the metathesis precursor (compound **176** in the review's numbering) and the products **177/178/179**.
