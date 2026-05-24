# phoenix_reddy_cassaine_tda_2008

**STATUS: Awaiting Ivan sign-off.** structure.mol is a placeholder.

This case substitutes the unfillable `citreoviridin_suh_imda_1985` slot. The citreoviridin diagnosis is preserved in that directory; the present case picks up the recommended substitute target.

## Provenance

- **Primary reference:** Phoenix, S.; Reddy, M. S.; Deslongchamps, P. "Total Synthesis of (+)-Cassaine *via* Transannular Diels−Alder Reaction." *J. Am. Chem. Soc.* **2008**, *130*, 13989–13995. DOI `10.1021/ja805097s`.
- **Earlier communication:** Phoenix, S.; Bourque, E.; Deslongchamps, P. *Org. Lett.* **2000**, *2*, 4149–4152. DOI `10.1021/ol006670r`.
- **14-membered TDA methodology:** Lamothe, S.; Ndibwami, A.; Deslongchamps, P. *Tetrahedron Lett.* **1988**, *29*, 1639 (theoretical, DOI `10.1016/S0040-4039(00)82005-5`) and 1641 (experimental, DOI `10.1016/S0040-4039(00)82006-7`).
- **13-membered TDA lineage (sibling references):** Baettig, K. *et al.* *Tetrahedron Lett.* **1987**, *28*, 5249 (cis-trans-trans, DOI `10.1016/S0040-4039(00)96699-1`); Baettig, K. *et al.* *Tetrahedron Lett.* **1987**, *28*, 5253 (trans-cis-cis, DOI `10.1016/S0040-4039(00)96700-5`); Bérubé, G.; Deslongchamps, P. *Tetrahedron Lett.* **1987**, *28*, 5255 (tetrasubstituted enol-ether dienophile, DOI `10.1016/S0040-4039(00)96701-7`).
- **Cassaine structural data:** PubChem CID 5281267; ChEBI:3454; CAS 468-76-8.

## Encoding caveats

1. **Citation correction (vs. panel_TODO.md).** The Tet. Lett. 1987 paper at pp 5249–5252 is by Baettig, Dallaire, Pitteloud, Deslongchamps — NOT by Bérubé. The Bérubé-Deslongchamps paper in the same issue is at pp 5255–5258 (tetrasubstituted enol-ether-dienophile variant). The 1987 *Tet. Lett.* 28 issue contains three back-to-back Deslongchamps-group TDA papers at pp 5249/5253/5255. The current panel_TODO.md attribution should be updated.
2. **Selected over Bérubé-Deslongchamps 1987 on the panel_TODO.md recommendation.** Phoenix-Reddy 2008 is newer (X-ray characterization, full *JACS* paper, 30 citations), more cleanly characterizes the TDA stereochemistry, and uses a 14-membered precursor (Lamothe methodology lineage). The 13-membered Baettig/Bérubé papers are methodology not total synthesis; they target a hypothetical *cis*-decalin trienone rather than a natural product. Phoenix-Reddy 2008 closes a real natural-product target via TDA, which is the panel's intended use case.
3. **TDA product ≠ natural product.** TDA closes the 14-membered macrocyclic triene **4** to give tricycle **5** (the *trans*-decalin steroid framework). Cassaine **1** is reached via ~6 additional steps (reduction, hydroboration, methyl cuprate 1,4-addition, dimethylaminoethyloxycarbonyl tethering, C8 epimerization, C3 alcohol deprotection). `structure.mol` should be cassaine (the natural product) for v0 consistency with the other panel cases; the TDA rule is treated as the macrocyclization-forming step.
4. **Ring size:** 14 (macrocyclic-triene precursor). The TDA produces a 6-6-6 fused tricyclic product; the panel rule fires once, closing two σC-C bonds in one cycloaddition event.
5. **Byproduct:** **NONE** (cycloaddition is byproduct-free). AE class `high` and matches the `high_atom_economy_bond` class flag.
6. **Stereochemistry of TDA is controlled by macrocyclic preorganization** (the *cis-trans-trans* triene geometry of compound **4**). No external chiral catalyst is used — this is the central thesis of the Deslongchamps TDA strategy.
7. **structure.mol is a PLACEHOLDER.** PubChem CID 5281267 Molfile is the recommended source. Ivan to audit before commit. Note: PubChem 3D conformer is computed, not X-ray; the 2008 *JACS* SI may contain an X-ray-determined structure of tricycle **5** (the TDA product, pre-elaboration). If Ivan wants a literature X-ray, CCDC ConQuest by DOI lookup is needed.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja805097s`, `10.1021/ol006670r`, `10.1016/S0040-4039(00)82005-5`, `10.1016/S0040-4039(00)82006-7`, `10.1016/S0040-4039(00)96699-1`, `10.1016/S0040-4039(00)96700-5`, `10.1016/S0040-4039(00)96701-7`).
- Structural data: PubChem CID 5281267, ChEBI:3454 — mutually consistent (C₂₄H₃₉NO₄, MW 405.6 g/mol, CAS 468-76-8).
- Mechanism: Phoenix-Reddy-Deslongchamps 2008 abstract (PubMed 18817389, full text *JACS* 130:13989); described in Taber's *Organic Synthesis* book chapter (DOI `10.1093/oso/9780199764549.003.0079`).
- Bioactivity context: PubChem description (Erythrophleum genus, cardiotonic, antihypertensive, local anaesthetic).
