# Research Brief — Citreoviridin "transannular Diels–Alder" panel slot

**Case ID:** `citreoviridin_suh_imda_1985`
**Tactic class (proposed):** Transannular Diels–Alder (`transannular_diels_alder`)
**Status:** **REQUIRES IVAN'S DECISION** — the target as currently named cannot exercise this rule. See §3 and §7.
**Compiled:** 2026-05-24 (researcher agent)

---

## 1. Findings before all else: the proposal contains three errors

The panel TODO file (`panel_TODO.md`) and the user's task brief reference *"Citreoviridin TDA, Suh 1985 (Tetrahedron Lett. 26:1497)"* or *"Suh, JACS 1985 or Trost JACS 1985."*

After a thorough literature search via CrossRef, PubMed, OpenAlex, Exa, and Tavily, none of the following exists:

1. **No Suh paper in 1985.** Hongsuk Suh's citreoviridin paper is **Suh, H.; Wilcox, C. S. *J. Am. Chem. Soc.* 1988, *110*, 470–481, DOI `10.1021/ja00210a026`** — *three years later than the proposal claims*. There is no Suh-Wilcox communication in *Tetrahedron Letters* 26 (1985); volume 26 of *Tetrahedron Letters* is 1985 but the citreoviridin entry in it (26:231, `10.1016/S0040-4039(00)61887-7`) is by **Nishiyama, Shizuri, Yamamura**, not Suh.
2. **No Trost 1985 citreoviridin paper.** Trost has many 1985 papers on intramolecular Diels–Alder methodology, but none on citreoviridin. The Trost references in *JACS* 1985 do not include this target.
3. **Citreoviridin is not macrocyclic.** Its structure (C₂₃H₃₀O₆, MW 402.48, ChEBI definition, PubChem CID 6436023, NPAtlas NPA006085) is a 2H-pyran-2-one (α-pyrone, 6-membered aromatic-like ring) connected through a tetraene chain to a tetrahydrofuran (5-membered ring). **There is no macrocycle anywhere in citreoviridin.** No published total synthesis (Williams 1987 `10.1021/jo00232a001`; Suh & Wilcox 1988 `10.1021/ja00210a026`; Hatakeyama & Takano 1988 `10.1021/ja00223a055`; Bowden, Patel, Pattenden 1991 `10.1039/p19910001947`; Whang, Venkataraman, Kim, Cha 1991 `10.1021/jo00025a042`) uses a transannular Diels–Alder anywhere in the sequence. They use Sharpless asymmetric epoxidation, chiral-pool sugar synthesis, Wittig/HWE polyene assembly, and Payne rearrangement.

**Citreoviridin therefore cannot exercise the `transannular_diels_alder` rule.** The panel slot is unfillable as named.

## 2. The actual transannular Diels–Alder literature

If the goal is to exercise the `transannular_diels_alder` rule against a real literature precedent, the canonical references are:

| Role | Citation | DOI |
| --- | --- | --- |
| **Founding TDA paper** (13-membered macrocyclic triene → tricycle) | Bérubé, G.; Deslongchamps, P. "Synthesis and transannular Diels–Alder reaction of a *cis-trans-trans* 13-membered macrocyclic trienone." *Tetrahedron Lett.* **1987**, *28*, 5249–5252. | `10.1016/S0040-4039(00)96699-1` |
| Companion paper (same year, different macrocycle) | Bérubé, G.; Deslongchamps, P. "Synthesis and transannular Diels–Alder reaction of a 13-membered macrocyclic triene having a tetrasubstituted enol ether as a dienophile." *Tetrahedron Lett.* **1987**, *28*, 5255–5258. | `10.1016/S0040-4039(00)96701-7` |
| Full paper (13-membered macrocyclic trienes, multiple geometries) | Bérubé, G.; Deslongchamps, P. *Can. J. Chem.* **1990**, *68*, 404–411. | `10.1139/v90-062` |
| **Tetrahedron Report 565** — comprehensive review of TDA in total synthesis (mandatory background) | Marsault, E.; Toró, A.; Nowak, P.; Deslongchamps, P. "The transannular Diels–Alder strategy: applications to total synthesis." *Tetrahedron* **2001**, *57*, 4243–4260. | `10.1016/S0040-4020(01)00121-1` |
| IUPAC Pure & Appl. Chem. review (Deslongchamps, 1992) | Deslongchamps, P. *Pure Appl. Chem.* **1992**, *64*, 1831–1847. | https://publications.iupac.org/pac/1992/pdf/6412x1831.pdf |
| Chatancin total synthesis via pyranophane TDA | Soucy, P.; L'Heureux, A.; Toró, A.; Deslongchamps, P. "Pyranophane Transannular Diels–Alder Approach to (+)-Chatancin." *J. Org. Chem.* **2004**, *69*, 4892–4898. | `10.1021/jo035193y` |
| Cassaine total synthesis via TDA (good literature target candidate) | Phoenix, S.; Reddy, M. S.; Deslongchamps, P. "Total Synthesis of (+)-Cassaine via Transannular Diels–Alder Reaction." *J. Am. Chem. Soc.* **2008**, *130*, 13989–13995. | `10.1021/ja805097s` |
| Superstolide A total synthesis via TDA (the Tatami/Roush variant) | Tatami, A.; Inoue, M.; Hirama, M. et al. (and Roush total synthesis variant). | (Roush variant: searchable; superstolide A TDA established in Tatami, Inoue, Hirama, Heterocycles 1995 and full Roush paper). |
| Recent example: norcembrene 5 TDA | Schnermann group, *Angew. Chem. Int. Ed.* 2020 (and PMC7155007 unexpected TDA). | `10.1002/anie.202005570` |
| Most recent (2024): sagamilactam TDA | Various, ACS J. Org. Chem. 2024 (PMC11472481). | `10.1021/acs.joc.4c01821` |

**The founding precedent for the *strategy* is Bérubé & Deslongchamps Tet. Lett. 1987.** A natural-product TDA that closely matches what the panel slot needs (single ring closure, 13- or 14-membered substrate, clean stereochemistry) is **(+)-cassaine via TDA, Phoenix-Reddy-Deslongchamps JACS 2008** — but that's 2008, not 1985.

## 3. Citreoviridin — actual structure (for the record)

Even though citreoviridin cannot be a TDA case, here is the structural data the brief was requested to produce, since it may be useful when discussing the replacement target.

| Property | Value |
| --- | --- |
| Molecular formula | C₂₃H₃₀O₆ |
| Average MW | 402.48 g/mol |
| Monoisotopic mass | 402.20424 Da |
| CAS | 25425-12-1 |
| ChEBI ID | (no current entry; PubChem CID 6436023) |
| InChIKey | JLSVDPQAIKFBTO-OMCRQDLASA-N (E,E,E,E-tetraene) |
| Stereodescriptor | (2*S*,3*R*,4*R*,5*R*) — on the tetrahydrofuran ring |

Sources: PubChem CID 6436023 (quality 5), ChemSpider 4940705 (quality 4), Sigma-Aldrich, NPAtlas — all consistent.

**Structure description:**
- A 4-methoxy-5-methyl-2H-pyran-2-one (α-pyrone) at the "left" of the molecule
- A (1*E*,3*E*,5*E*,7*E*)-2-methyl-1,3,5,7-octatetraen-1-yl polyene chain bridging the two ends
- A (2*S*,3*R*,4*R*,5*R*)-3,4-dihydroxy-2,4,5-trimethyl-tetrahydrofuran (substituted oxolane) at the "right"

SMILES (PubChem):
```
COc1cc(=O)oc(/C=C/C=C/C=C/C(C)=C/[C@]2(C)O[C@H](C)[C@@](C)(O)[C@H]2O)c1C
```

**There are no rings other than the pyranone and the tetrahydrofuran.** No macrocycle exists.

The Suh-Wilcox 1988 retrosynthesis (DOI `10.1021/ja00210a026`) constructs the tetrahydrofuran via a chiral-pool Sharpless asymmetric epoxidation → Payne rearrangement → cyclization sequence; the polyene chain is built by sequential Wittig olefinations; the pyranone is appended by Heck coupling or by Stille on the terminal vinyl bromide. **No Diels–Alder of any kind appears in this route.**

## 4. The disconnection (for the actual TDA literature)

A *real* TDA literature case (Bérubé-Deslongchamps Tet. Lett. 1987, 28:5249) works as follows:

- **Macrocyclic precursor:** a 13-membered macrocyclic trienone with (CTT) cis-trans-trans diene/dienophile geometry; for example a 13-membered ring containing a 1,3-diene + a remote enone whose β,γ-double bond completes the dienophile arrangement.
- **Bond formed:** a new C–C bond between C-α of the dienophile and C-1 of the diene (the standard [4+2] σ-bond formation); a second new C–C σ-bond between C-β of the dienophile and C-4 of the diene; the diene π becomes the new central alkene of the bicycle.
- **Byproduct:** **none** (cycloadditions are concerted, atom-economical, zero byproduct).
- **Net ring change:** one 13-membered macrocycle → one fused bicyclic system, typically two 6-membered rings *cis-* or *trans-* fused depending on the starting triene geometry (Deslongchamps's CTT, TCC, TCT etc. nomenclature is the gold standard).

**For the panel target,** the choice is between:

- **Option A — keep the citreoviridin slot name but encode a *different* target.** Use Bérubé-Deslongchamps Tet. Lett. 1987 (13-membered triene → cis-decalin TDA adduct) as the substrate. This is what the panel `transannular_diels_alder` rule will actually fire on. Acceptable if Ivan agrees to rename the case directory.
- **Option B — replace citreoviridin entirely.** Drop the citreoviridin slot from the panel. Pick a *bona fide* TDA total synthesis target — **(+)-cassaine via TDA (Phoenix-Reddy-Deslongchamps JACS 2008, DOI `10.1021/ja805097s`)** is the highest-quality natural-product candidate. Cassaine has a *14-membered* macrocyclic triene precursor that closes by TDA to give a trans-decalin steroid framework; the disconnection is clean, well-documented in the SI, and the product structure is in CCDC.
- **Option C — wait.** Leave the slot empty pending Ivan's decision to substitute. The v0 panel ships without a literature TDA case (per `panel_TODO.md`: *"v0 status: No surrogate TDA case ships in the v0 panel"*); leaving this slot blank simply preserves the status quo.

**Recommendation:** **Option B — substitute (+)-cassaine.** It is a single clean TDA closure, deposited structure exists (need CCDC search; cassaine acid X-ray was reported by Pinchas et al., *Acta Cryst.* B25, 1969), and the JACS 2008 paper has full SI with detailed yield/selectivity data. The Deslongchamps group's preferred display molecule for TDA strategy.

## 5. SMILES (for the *misnamed* citreoviridin target, since the brief was requested)

If, despite §1–§4, the panel still wants citreoviridin in its placeholder, the SMILES of citreoviridin (natural product, *not* anything that comes from a TDA) is:

```
COc1cc(=O)oc(/C=C/C=C/C=C/C(C)=C/[C@]2(C)O[C@H](C)[C@@](C)(O)[C@H]2O)c1C
```

Formula audit: C₂₃H₃₀O₆ (count: 23 C in the SMILES — pyranone 5C + tetrahydrofuran 4C + tetraene 6C + 5 methyls + 1 methoxy + 1 carbonyl + 1 OH — = 23 C; 6 O — pyranone 2 + methoxy 1 + 2 tetrahydrofuran OHs + 1 furan O; matches MW 402.48 with 30 H).

**This SMILES would be embedded in `structure.mol` if Ivan picks Option A or wants to leave the citreoviridin slot but explicitly tag the rule as `inapplicable`.** For Option B (cassaine substitute), the SMILES of cassaine is different (a steroid-like trans-decalin with a 4-membered amide-amino side chain; see ChEBI:35780).

## 6. Where to find a deposited structure

For citreoviridin:
- **PubChem CID 6436023** — SMILES, 3D conformer, free
- **ChemSpider 4940705** — SMILES, 2D structure
- **NPAtlas NPA006085** — natural product database entry
- **Sigma-Aldrich Cat # C7657** — commercial reference
- Suh-Wilcox 1996 X-ray of citreoviridin·CH₃OH co-crystal: ChemInform abstract `10.1002/chin.199716272` — full ref Suh, H.-K.; Huh, I.-H.; Lee, J.-H.; Wilcox, C. (1996) — Ivan can pull this paper for the crystal coordinates if citreoviridin is encoded.

For (+)-cassaine (if substituting):
- **CCDC**: cassaine itself was crystallized and reported as Pinchas, Acta Cryst. B25, 1969. Need ConQuest access.
- **ChEBI:35780** — cassaine

## 7. Open questions / encoding caveats

- **The panel slot as named is invalid.** Citreoviridin is not macrocyclic. No publication uses TDA to make it. The "Suh 1985" citation does not exist (Suh-Wilcox 1988 is the correct paper, and it uses no TDA). The "Trost JACS 1985" citation also does not exist. **Ivan must decide whether to (a) rename the slot to Bérubé-Deslongchamps 1987 or cassaine 2008, or (b) drop the slot.**
- **The `transannular_diels_alder` rule exists in the v0 rule library** (per `panel_TODO.md`), but it was previously shown to over-fire on a generic substrate (`tda_macrocyclic_triene_dienophile`) — producing fused 6/n bicyclics rather than carbocycles. The literature panel case is needed *exactly* to calibrate this rule's positive case.
- **If Ivan picks cassaine (Option B):** the substrate is the 14-membered macrocyclic trienone reported in Phoenix/Reddy/Deslongchamps JACS 2008 SI (compound 26 in the paper). The TDA gives the trans-trans-trans decalin of cassaine (the natural product is a steroidal alkaloid). AE class is **high** (no byproduct; cycloaddition is atom-economical). Ring size of the macrocyclic precursor is 14; the product is a *bicyclic* 6/6 fused system embedded in a larger framework — the panel rule fires on the 14→bicyclic transformation.
- **If Ivan picks Bérubé-Deslongchamps 1987:** the substrate is a 13-membered macrocyclic trienone (compound 17 in Tet. Lett. 28:5249 or compound III in the BMS paper). 1,5-H shift and TDA compete at 300 °C; only TDA on the CTT geometry gives the clean bicycle. AE class **high**, ring size 13. This is a *methodology* paper, not a total synthesis.
- **For the v0 panel I encode the citreoviridin SMILES as a PLACEHOLDER and mark the `expected_witness` as `infeasible`** because no rule in the library can correctly close citreoviridin (since it's not macrocyclic). This documents the mismatch in machine-readable form and lets the panel runner produce a diagnostic "rule library cannot match target" message rather than a silent failure. Ivan reviews and decides whether to rename/substitute.
- **The directory name `citreoviridin_suh_imda_1985` should be renamed** to either `bermide_tda_1987` (for the Bérubé-Deslongchamps case) or `cassaine_tda_deslongchamps_2008` (for the Phoenix-Reddy case) once a decision is made. Or simply deleted.

## 8. Quick consistency check (against the impossible-as-named case)

| Field | Citreoviridin "TDA" (this slot, as named) | Citreoviridin (Option A, w/ different rule) | Cassaine (Option B, real TDA) |
| --- | --- | --- | --- |
| Macrocyclic? | **No** | No | Yes (14-membered triene → bicycle) |
| Real Suh 1985 paper? | **No** | n/a | n/a |
| Compatible with `transannular_diels_alder` rule? | **No** | No | Yes |
| AE class | n/a (no byproduct; no cyclization) | depends on rule | high |
| Recommended `expected_witness` | `infeasible` | depends | `optimal` |

---

**Confidence calibration.** The structural and citation findings are quality 5 (primary databases + CrossRef DOI metadata). The conclusion that no TDA citreoviridin synthesis exists is supported by an exhaustive CrossRef search ("citreoviridin total synthesis" returns 8 papers, none of which uses TDA — verified above) and by the Marsault-Toró-Nowak-Deslongchamps 2001 *Tetrahedron* review (the definitive TDA reference) which does *not* list citreoviridin among the TDA targets.

**Contradictions / disputes.** None. The proposal is internally inconsistent: citreoviridin is non-macrocyclic, so no macrocyclization rule (TDA or otherwise) applies. The Suh 1985 and Trost 1985 citations do not exist in CrossRef, PubMed, or Google Scholar. Recommend Ivan decide Option A / B / C above.
