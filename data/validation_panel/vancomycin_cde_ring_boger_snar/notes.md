# vancomycin_cde_ring_boger_snar

**STATUS: Awaiting Ivan sign-off.** Structure.mol is a placeholder; the rule ID `aryl_etherification` does not yet exist in the rule library.

## Provenance

- Primary reference: Boger, D. L.; Miyazaki, S.; Kim, S. H.; Wu, J. H.; Castle, S. L.; Loiseleur, O.; Jin, Q. *J. Am. Chem. Soc.* **1999**, *121*, 10004–10011. DOI `10.1021/ja992577q`.
- Methodology reference: Boger, D. L.; Castle, S. L.; Miyazaki, S.; Wu, J. H.; Beresis, R. T.; Loiseleur, O. *J. Org. Chem.* **1999**, *64*, 70–80. DOI `10.1021/jo980880o`.
- CDE-ring system: Boger, D. L.; Beresis, R. T.; Loiseleur, O.; Wu, J. H.; Castle, S. L. *Bioorg. Med. Chem. Lett.* **1998**, *8*, 721–724. DOI `10.1016/S0960-894X(98)00110-3`.
- Crystal structure: PDB **1GHG** (vancomycin aglycon, 0.98 Å). Loll et al., *J. Med. Chem.* **2001**, *44*, 1837. DOI `10.1021/jm0005306`.
- Free SMILES / Molfile: ChEBI:47724 (aglycon) and ChEBI:28001 (parent).

## Encoding caveats

1. **Tactic class correction.** The panel proposal originally listed vancomycin under macrolactamization. It is biaryl-ether SNAr macroetherification. See `research_brief.md` §3 and §7.
2. **Rule does not yet exist.** `aryl_etherification` is referenced with a TODO; until the rule lands the runspec will not pass the panel.
3. **Two macrocycles, not one.** The Boger CDE system is two adjacent 16-membered biaryl ether rings (C–O–D and D–O–E). This case encodes only the C–O–D ring; a sibling case is needed for D–O–E.
4. **Substrate vs. product structure.** `structure.mol` must be the *cyclized product* (per panel convention, see `lactam_14_from_13_aminotridecanoic_acid/structure.mol`). For this case the product is the CD-ring intermediate from Boger JOC 64:70 (or, if Ivan prefers, the full aglycon from PDB 1GHG).
5. **HF byproduct.** AE accounting: HF, MW 20.01, mass-fraction of target ≈ 1.7 %. Class `high`.
6. **Atropisomerism is out of scope for v0.** The natural M/P configuration is set by thermal equilibration after macrocyclization; the rule itself does not need to predict it. Energetics disabled.
7. **Structure.mol is a PLACEHOLDER.** A CIF or careful 2D-figure audit is needed. Recommend extracting the aglycon from PDB 1GHG chain A and reducing it to the CD-ring fragment, or using the full aglycon directly. Either choice should be reviewed by Ivan before committing.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja992577q`, `10.1021/ja990189i`, `10.1021/jo980880o`, `10.1016/S0960-894X(98)00110-3`, `10.1002/(SICI)1521-3773(19981016)37:19<2700::AID-ANIE2700>3.0.CO;2-P`).
- Structural data: PDB 1GHG, 1SHO; ChEBI 28001, 47724; PDB Ligand Expo PRD_000204, PRD_000206; IUPHAR Guide to Pharmacology.
- Synthesis reviews: Nicolaou Chem. Eur. J. 1999 series (Parts 1–3), Boger Med. Res. Rev. 2001 review (DOI `10.1002/med.1014`).
