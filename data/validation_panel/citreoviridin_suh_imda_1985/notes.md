# citreoviridin_suh_imda_1985

**STATUS: REQUIRES IVAN DECISION — slot as named is unfillable.**

This directory was created per the user's task, but research found three problems:

1. **Citreoviridin is not macrocyclic.** Formula C₂₃H₃₀O₆ (PubChem CID 6436023, MW 402.48). The compound has a 6-membered pyranone and a 5-membered tetrahydrofuran connected by a tetraene chain. There is no macrocycle.
2. **"Suh 1985" does not exist.** The Suh-Wilcox citreoviridin paper is *J. Am. Chem. Soc.* **1988**, *110*, 470-481, DOI `10.1021/ja00210a026`. Not 1985, not *Tetrahedron Letters*. The 1985 *Tet. Lett.* 26:231 entry is Nishiyama-Shizuri-Yamamura, not Suh.
3. **No citreoviridin synthesis uses a transannular Diels-Alder.** Suh-Wilcox 1988 uses Sharpless asymmetric epoxidation + Payne rearrangement + Wittig polyene assembly. Williams 1987 (`10.1021/jo00232a001`), Hatakeyama-Takano 1988 (`10.1021/ja00223a055`), Bowden-Patel-Pattenden 1991 (`10.1039/p19910001947`), Whang-Venkataraman-Kim-Cha 1991 (`10.1021/jo00025a042`) all use non-TDA routes.

See `research_brief.md` for full details and proposed substitutions.

## Recommended path forward (Ivan to choose)

- **Option A:** Rename directory to `berube_deslongchamps_tda_1987` and encode the 13-membered macrocyclic CTT trienone from Bérubé & Deslongchamps *Tet. Lett.* **1987**, *28*, 5249 (DOI `10.1016/S0040-4039(00)96699-1`). This is the founding TDA precedent; methodology paper, not a total synthesis.
- **Option B (recommended):** Rename to `cassaine_tda_phoenix_2008` and encode the cassaine target (Phoenix-Reddy-Deslongchamps *J. Am. Chem. Soc.* **2008**, *130*, 13989, DOI `10.1021/ja805097s`). Clean 14-membered macrocyclic trienone → trans-decalin TDA closure; real natural product target.
- **Option C:** Delete this directory and update `panel_TODO.md` to remove the TDA literature slot until a literature target with a deposited structure is selected.

## Encoding caveats (if Option A or B is chosen)

- **Byproduct:** none (cycloaddition is concerted and atom-economical). AE class `high`.
- **Ring size:** the macrocyclic *precursor* is 13- or 14-membered; the TDA *product* is a fused bicyclic 6/m. The panel rule fires on the macrocyclic precursor → bicyclic transformation.
- **Catalyst/conditions:** thermal (typically 200–350 °C, neat or in xylenes). No metal catalyst.
- **Stereochemistry:** strongly geometry-dependent (Deslongchamps's CTT/TCC/TCT nomenclature). The rule must encode the *intramolecular* nature.

## Current state of `structure.mol`

PLACEHOLDER — explicitly marked as unencodable until target is reassigned.

## Sources cross-referenced

- Citreoviridin structure: PubChem CID 6436023, ChemSpider 4940705, NPAtlas NPA006085, Sigma-Aldrich C7657 (all quality 5, mutually consistent).
- Citreoviridin syntheses: CrossRef returned 8 total-synthesis papers; none uses TDA. Cross-checked with the Marsault-Toró-Nowak-Deslongchamps *Tetrahedron* 2001 review (the definitive TDA total-synthesis review, DOI `10.1016/S0040-4020(01)00121-1`) which does not list citreoviridin.
- TDA founding literature: Bérubé-Deslongchamps Tet. Lett. 1987, 28:5249 + 28:5255; Can. J. Chem. 1990 v90-062; Pure Appl. Chem. 1992, 64:1831 (Deslongchamps review).
- Cassaine TDA: Phoenix-Reddy-Deslongchamps *J. Am. Chem. Soc.* **2008**, *130*, 13989, DOI `10.1021/ja805097s`.
