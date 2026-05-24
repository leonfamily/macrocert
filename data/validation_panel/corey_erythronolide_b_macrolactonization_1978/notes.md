# corey_erythronolide_b_macrolactonization_1978

**STATUS: Encoded. structure.mol and erythronolide_b_seco building block built; runspec/expected updated. M5 campaign run pending pipeline activator wiring (see "Activator wiring gap" below).**

## Provenance

- **Primary reference:** Corey, E. J.; Kim, S.; Yoo, S.-E.; Nicolaou, K. C.; Melvin, L. S.; Brunelle, D. J.; Falck, J. R.; Trybulski, E. J.; Lett, R.; Sheldrake, P. W. "Total synthesis of erythromycins. 4. Total synthesis of erythronolide B." *J. Am. Chem. Soc.* **1978**, *100*, 4620–4622. DOI `10.1021/ja00482a063`.
- **Companion Part 3 (fragment synthesis):** Corey, E. J. *et al.* *J. Am. Chem. Soc.* **1978**, *100*, 4618–4620. DOI `10.1021/ja00482a062`.
- **Corey–Nicolaou activator methodology paper:** Corey, E. J.; Nicolaou, K. C. *J. Am. Chem. Soc.* **1974**, *96*, 5614–5616. DOI `10.1021/ja00824a073`.
- **Erythronolide B structural data:** **PubChem CID 441113** (not 122729), **C21H38O7** (not C21H38O6), MW 402.52, CAS 3225-82-9. InChIKey `ZFBRGCCVTUPRFQ-HWRKYNCUSA-N`. Canonical isomeric SMILES from PubChem 441113 used by `scripts/build_erythronolide_b.py`.

## Corrections vs. upstream documents

1. **DOI correction.** The proposal and `panel_TODO.md` cite `10.1021/ja00482a075` for the macrolactonization paper. CrossRef cannot resolve that DOI. The correct DOI is `10.1021/ja00482a063` (Part 4, pp 4620–4622). The page number "4618" is the *first page of Part 3* (fragment paper, DOI `10.1021/ja00482a062`); Part 4 (macrolactonization) starts at p. 4620.
2. **Formula correction.** The `research_brief.md` asserts C21H38O6 / MW 386.52 / PubChem CID 122729. All three are wrong:
   - Erythronolide B is **C21H38O7** (MW 402.52). It has *four* hydroxyls (C3, C5, C6, C12), one ketone (C9), and one lactone (C1–O13). The brief's "three β-hydroxyls" undercounts.
   - **PubChem CID 122729 is rifampicin**, not erythronolide B. The correct CID is **441113** (verified by PubChem name lookup; InChIKey `ZFBRGCCVTUPRFQ-HWRKYNCUSA-N`).
3. **Stereocenter count is still 10.** The brief's "10 sp³ stereocenters" agrees with PubChem-CID-441113-isomeric-SMILES; only the formula/CID were off.

## Encoding details

- `structure.mol`: built by `scripts/build_erythronolide_b.py` from the PubChem CID 441113 isomeric SMILES, embedded with ETKDGv3 + MMFF94 optimization, written through openbabel for strict V2000 output. 10 stereocenters all assigned post `Chem.AssignStereochemistry`. Single 14-membered ring confirmed.
- `data/building_blocks/erythronolide_b_seco.yaml`: derived by `scripts/build_erythronolide_b_seco.py` by surgically opening the C(=O)–O ester bond of the macrolactone and capping the acyl side with a new –OH (the C13 alcohol side is already an alcohol; RDKit fills in the implicit H). Mass balance verified: seco exact MW (420.2723) = cyclized exact MW (402.2618) + H₂O (18.0106).
- The seco-acid SMILES (canonical isomeric) preserves all 10 stereocenters and matches the literature seco-acid structure (the open-chain ω-hydroxy acid with C1 = COOH and C13 = secondary alcohol).

## Activator: Corey–Nicolaou (PySSPy/PPh₃)

The 1978 paper uses **2,2'-dipyridyl disulfide (Aldrithiol-2, PySSPy, MW 220.31)** + **triphenylphosphine (PPh₃, MW 262.28)** in xylene at reflux. This exercises the `Corey_Nicolaou` alternative in `data/rules/macrolactonization.meta.yaml` `reagent_mass_alternatives`:

```yaml
- name: "Corey_Nicolaou"
  reagent_mass_g_per_mol: 482.0           # PySSPy + PPh3
  additional_byproduct_mass_g_per_mol: 389.0   # 2-mercaptopyridine + Ph3P=O
  description: "PySSPy + PPh3, refluxing xylene. Historic; erythronolide B."
```

Bond-level byproduct: H₂O (18.015 g/mol, identical to the rule's default Yamaguchi byproduct).
Process-level byproducts: 2-mercaptopyridine (111.16 g/mol) + Ph₃P=O (278.28 g/mol) = 389 g/mol.

## **Activator wiring gap (TODO)**

The `ReagentAlternative` dataclass exists (`src/macrocert/spec/rules.py:25-52`) and the `RuleMeta.get_alternative(name)` method is defined (`rules.py:82-86`), but **`get_alternative` has no call sites in the pipeline** (verified by `grep -rn get_alternative src/`). The runspec's `solver.extra.activator: Corey_Nicolaou` field is parsed (RunSpec keeps a free-form `extra: dict` on the solver block) but **no downstream code reads it and threads it into the objective calculation**.

Concretely, the M5 campaign leg for this case will run under the *default Yamaguchi* process-level reagent mass (568 g/mol) until the override path lands. The **bond-level** chemistry (H₂O, 18.015 g/mol) is identical for both activators, so the *optimal bond-level objective is unchanged* — only the process-level AE penalty differs. For the macrocert v0 panel (which has `energetics.enabled: false`), this is acceptable; for v1 (with process-AE energetics), the wiring must be in place.

The fix is small (one method call: in the objective/AE builder, resolve `runspec.solver.extra.get("activator")` against the rule's `meta.get_alternative(...)` and substitute `reagent_mass_g_per_mol` + `additional_byproduct_mass_g_per_mol`). Out of scope for this M5 leg.

## Other encoding notes

3. **Ring size:** 14 (consistent across all literature; PubChem CID 441113 explicitly identifies erythronolide B as a 14-membered macrolide).
4. **Byproduct (bond level):** H₂O. Mass fraction 18.015 / 402.52 = **4.48 %** (corrected for the right MW). High AE band.
5. **Stereocenters:** 10 sp³ stereocenters. Stereodescriptor (from PubChem isomeric SMILES) matches the published Corey 1978 absolute configuration. α-stereo (C2, C12) is preserved under Corey–Nicolaou conditions (no enolization at the mild PySSPy/PPh₃ activation), matching the macrolactonization rule's `retains_alpha_stereo` flag.
6. **No nitrogen.** Erythronolide B is C₂₁H₃₈O₇ (no N). The lactam rule does not apply; only macrolactonization is relevant.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja00482a063`, `10.1021/ja00482a062`, `10.1021/ja00824a073`).
- Structural data: **PubChem CID 441113** (erythronolide B), C21H38O7, MW 402.52, CAS 3225-82-9, InChIKey ZFBRGCCVTUPRFQ-HWRKYNCUSA-N. The brief's reliance on CID 122729 was a copy-paste error — that CID is rifampicin (C39H47NO14).
- Activator mechanism: Corey & Nicolaou 1974, *JACS* 96:5614 (DOI `10.1021/ja00824a073`) — original methodology paper.
