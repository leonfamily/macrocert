# phoenix_reddy_cassaine_tda_2008

**STATUS:** M5 deliverable complete. `structure.mol` is the TDA-immediate
tricycle 5 (post-TDA, pre-elaboration), authored programmatically by
`scripts/build_cassaine.py`.

## Provenance

- **Primary reference:** Phoenix, S.; Reddy, M. S.; Deslongchamps, P.
  "Total Synthesis of (+)-Cassaine *via* Transannular Diels-Alder
  Reaction." *J. Am. Chem. Soc.* **2008**, *130*, 13989-13995.
  DOI `10.1021/ja805097s`.
- **Earlier communication:** Phoenix, S.; Bourque, E.; Deslongchamps, P.
  *Org. Lett.* **2000**, *2*, 4149-4152. DOI `10.1021/ol006670r`.
- **14-membered TDA methodology:** Lamothe, S.; Ndibwami, A.;
  Deslongchamps, P. *Tetrahedron Lett.* **1988**, *29*, 1639 (theoretical,
  DOI `10.1016/S0040-4039(00)82005-5`) and 1641 (experimental, DOI
  `10.1016/S0040-4039(00)82006-7`).
- **13-membered TDA lineage (sibling references):** Baettig, K.
  *et al.* *Tetrahedron Lett.* **1987**, *28*, 5249/5253/5255 (three
  back-to-back Deslongchamps-group papers).
- **Cassaine structural data:** PubChem CID 5281267; ChEBI:3454;
  CAS 468-76-8. Authoritative isomeric SMILES (from PubChem REST):
  `C[C@@H]\1[C@H]2[C@H](CC/C1=C\C(=O)OCCN(C)C)[C@]3(CC[C@@H](C([C@@H]3CC2=O)(C)C)O)C`
  — formula C24H39NO4, exact MW 405.288.

## Encoding decision: tricycle 5, not the natural product

The panel rule (`transannular_diels_alder`,
`data/rules/transannular_diels_alder.gml`) demands a cyclohexene RHS
with one residual in-ring C=C (the diene's 2=3 bond preserved in
the [4+2] product). Cassaine itself (after ~6 post-TDA elaboration
steps) carries a saturated 6-6-6 trans-decalin and so cannot match
the TDA RHS in reverse on a structure-mol audit. Encoding the
natural product would require `expected_witness: infeasible` for
the literature tactic, which contradicts both the task brief and
the proposal §5 deliverable shape.

The encoded `structure.mol` is therefore the **TDA-immediate
intermediate (compound 5)**, with two v0 simplifications:

1. **Methyl ester in place of the t-butyl ester used by the paper.**
   Cassaine's natural dimethylaminoethyl ester is installed *after*
   the TDA by a separate tethering step; the paper uses t-butyl
   at this stage. Methyl is the panel convention for compactness.
2. **Free C3-OH in place of the silyl-protected alcohol.** Silyl
   protection is a chemoselectivity device for downstream functional-
   group manipulations; it has no bearing on the TDA macrocyclization
   itself.

Formula of the encoded tricycle 5: **C21H32O3, exact MW 332.235 Da**.
6-6-6 fused trans-decalin tricycle; 6 sp3 stereocenters (4 new from
the TDA + 2 pre-existing); one in-ring C=C (the cyclohexene); one
exocyclic α,β-unsaturated ester C=C.

## TDA disconnection

The transannular [4+2] of compound 4 (14-membered macrocyclic
*cis-trans-trans* triene) → compound 5 forms TWO new sigma C-C bonds
in a single pericyclic event. Per the TDA rule (LHS C(1)=C(2)-C(3)=C(4)
+ C(5)=C(6); RHS cyclohexene with new σ at 1-6 and 4-5, residual
alkene at 2=3), the seco-precursor is derived from the cyclized
tricycle by:

1. Locate the unique cyclohexene ring (the TDA-residual alkene).
2. Map the cyclohexene atoms to rule positions 1..6 by walking the
   ring outward from the alkene.
3. Break the two sigma bonds at (1-6) and (4-5).
4. Convert the (2-3) bond from double to single (restoring the
   diene's central single bond).
5. Convert the (1-2), (3-4), and (5-6) bonds to double (restoring
   the diene C=C-C=C and the dienophile C=C).

Result: a 14-membered macrocyclic triene whose ring has three in-ring
C=C bonds. The exocyclic α,β-unsaturated methyl ester is unchanged
(it was already exocyclic in the cyclized form). Mass balance:
**Δ MW = 0** (TDA byproduct mass = 0). See `data/building_blocks/
cassaine_seco.yaml` for the seco SMILES and the script-emitted audit
trace.

## Stereo caveat — Workstream F task #35 (queued, not yet done)

The v0 transannular_diels_alder GML rule
(`data/rules/transannular_diels_alder.gml`) carries no stereo
annotations on either side of the rewrite. As a consequence:

- The seco's three in-ring C=C bonds are encoded *without* E/Z
  descriptors. The Lamothe-Ndibwami-Deslongchamps 1988 papers
  describe the *cis-trans-trans* geometry of compound 4 as the
  Deslongchamps T4-transition-state precursor; that geometry is
  documented in `cassaine_seco.yaml`'s notes but not enforced on
  the seco SMILES.
- The four new sp3 stereocentres installed by the TDA (C5 and C8
  ring junctions; C10 and C13 angular methyl-bearing quaternaries)
  are encoded on `structure.mol` per the predicted T4-transition-state
  stereochemistry but are *not* enforced by the rule on the panel
  run.
- The endo/exo selectivity of the TDA is not modelled.

Workstream F task #35 (TDA stereo encoding for 4 new sp3 centres +
endo/exo split) is queued behind the broader MØD stereo-propagation
work (see `docs/mod_stereo_reference.md` §1.5, §5.2 and
`docs/workstream_f_harness.md`). The M5 campaign runs without stereo
enforcement on the TDA leg and the documentation here, in
`expected.yaml`, and in `docs/cassaine_m5.md` flags the gap.

## Building blocks

- `data/building_blocks/cassaine_seco.yaml` — 14-membered macrocyclic
  triene SMILES, provenance, mass-balance trace (Δ MW = 0).

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja805097s`, `10.1021/ol006670r`,
  `10.1016/S0040-4039(00)82005-5`, `10.1016/S0040-4039(00)82006-7`).
- Structural data: PubChem REST API for CID 5281267 (authoritative
  isomeric SMILES); ChEBI:3454 cross-validated.
- Rule reference: `data/rules/transannular_diels_alder.gml` and
  `transannular_diels_alder.meta.yaml`.
- Build scripts: `scripts/build_cassaine.py` (cyclized target),
  `scripts/build_cassaine_seco.py` (seco precursor).
- M5 campaign report: `docs/cassaine_m5.md`.
