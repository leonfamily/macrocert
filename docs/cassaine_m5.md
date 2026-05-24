# Cassaine — M5 Deliverable (Phoenix-Reddy-Deslongchamps 2008 TDA)

**Case:** `data/validation_panel/phoenix_reddy_cassaine_tda_2008/`
**Tactic:** Transannular Diels-Alder (`transannular_diels_alder`)
**Primary reference:** Phoenix, S.; Reddy, M. S.; Deslongchamps, P.
"Total Synthesis of (+)-Cassaine *via* Transannular Diels-Alder
Reaction." *J. Am. Chem. Soc.* **2008**, *130*, 13989-13995.
DOI [10.1021/ja805097s](https://doi.org/10.1021/ja805097s). Earlier
communication: Phoenix, S.; Bourque, E.; Deslongchamps, P.
*Org. Lett.* **2000**, *2*, 4149-4152.
DOI [10.1021/ol006670r](https://doi.org/10.1021/ol006670r).
Methodology lineage: Lamothe, S.; Ndibwami, A.; Deslongchamps, P.
*Tetrahedron Lett.* **1988**, *29*, 1639 (theoretical,
DOI [10.1016/S0040-4039(00)82005-5](https://doi.org/10.1016/S0040-4039(00)82005-5))
and 1641 (experimental,
DOI [10.1016/S0040-4039(00)82006-7](https://doi.org/10.1016/S0040-4039(00)82006-7)).

## 1. Summary

(+)-Cassaine's 6-6-6 trans-decalin tricyclic core was forged by
Phoenix, Reddy and Deslongchamps in 2008 through a transannular
Diels-Alder cycloaddition on a 14-membered *cis-trans-trans*
macrocyclic triene (compound 4) under thermal conditions (180-230 °C
in toluene/xylene, no catalyst). The TDA forms TWO new sigma C-C bonds
in a single pericyclic event with **ZERO byproduct** (cycloaddition
has 100% atom economy at the bond-formation step), producing the
*trans*-decalin tricycle compound 5. Compound 5 is then elaborated
through ~6 further steps (stereoselective reduction, hydroboration,
methyl cuprate 1,4-addition, dimethylaminoethyloxycarbonyl tethering,
C8 epimerization, C3 deprotection) to (+)-cassaine 1 (C₂₄H₃₉NO₄,
MW 405.288 g/mol, PubChem CID 5281267, ChEBI:3454).

The §5 deliverable — encoded TDA product, derived 14-membered
macrocyclic-triene seco-precursor, runspec, expected.yaml, and an
M5 campaign over all 13 macrocyclization tactics — is now in place.
Outcome:

| Metric                                       | Value                                   |
| -------------------------------------------- | --------------------------------------- |
| Cyclized target (compound 5) formula         | C₂₁H₃₂O₃                                |
| Cyclized exact MW                            | 332.2351 Da                             |
| Seco-precursor (compound 4) formula          | C₂₁H₃₂O₃                                |
| Seco-precursor exact MW                      | 332.2351 Da                             |
| Δ MW (seco − cyclized)                       | 0.0000 Da (TDA byproduct = 0)           |
| Macrocyclic-triene ring size (precursor)     | 14                                      |
| Fused ring inventory (product)               | 6-6-6 (trans-decalin + cyclohexene)     |
| In-ring alkene of product (TDA residual)     | 1 (cyclohexene C=C)                     |
| Exocyclic alkene of product                  | 1 (α,β-unsat methyl ester)              |
| sp³ stereocenters (cyclized)                 | 6 (4 new from TDA + 2 pre-existing)     |
| Tactics evaluated in M5 campaign             | 13                                      |
| Verifier-clean certificates                  | 13 / 13                                 |
| Optimal tactics in shortlist                 | 1 (`transannular_diels_alder`)          |
| TDA objective (bond-level expelled mass)     | 0.000 g/mol (zero byproduct)            |
| AE class                                     | `high` (rule meta: byproduct_mass = 0)  |
| Panel test (`pytest -k phoenix_reddy`)       | passes                                  |

## 2. Encoding decisions

### 2.1 Target — TDA-immediate tricycle 5, not the natural product

The transannular [4+2] cycloaddition in Phoenix-Reddy-Deslongchamps
2008 closes the macrocyclic triene 4 to give compound 5; the natural
product (+)-cassaine 1 is reached by ~6 additional post-TDA steps
that *saturate* the residual in-ring alkene of 5 (stereoselective
reduction of the diene's 2=3 bond, hydroboration, etc.). Encoding the
natural product as `structure.mol` would mean the
`transannular_diels_alder` rule cannot match in reverse on the
encoded target — the rule's RHS demands a cyclohexene with one
residual in-ring C=C (the diene's 2=3 bond), but cassaine has only
saturated 6-rings (and an exocyclic α,β-unsaturated ester).

Encoding compound 5 — the **actual macrocyclization product** —
preserves the in-ring cyclohexene the rule expects. The encoded form
uses two v0 simplifications:

1. **Methyl ester** in place of the paper's *t*-butyl ester at this
   stage (cassaine's natural dimethylaminoethyl ester is installed
   *after* the TDA by a separate tethering step). Methyl is the
   panel convention.
2. **Free C3 hydroxyl** in place of the paper's silyl-protected
   alcohol (silyl protection has no bearing on the TDA itself).

Cyclized SMILES (`scripts/build_cassaine.py`, RDKit-canonical
isomeric):

```
COC(=O)/C=C1\CC[C@H]2[C@@H](C=C[C@H]3C(C)(C)[C@@H](O)CC[C@]23C)[C@H]1C
```

Stored at `data/validation_panel/phoenix_reddy_cassaine_tda_2008/
structure.mol` (strict V2000, openbabel-canonicalized, 3D-embedded
via RDKit ETKDG + MMFF). Canonical SMILES audit alongside in
`canonical_smiles.txt`.

### 2.2 Seco-precursor — programmatic derivation

`scripts/build_cassaine_seco.py` opens the cyclized tricycle by
applying the reverse of the `transannular_diels_alder` rule:

1. Locate the unique cyclohexene ring of the tricycle (the TDA-
   residual alkene).
2. Walk the ring outward from the alkene to map cyclohexene atoms
   to rule positions 1..6.
3. Break the two new sigma bonds at (rule 1-6) and (rule 4-5).
4. Convert the (rule 2-3) bond from double to single (the diene's
   central single bond is restored).
5. Convert (rule 1-2) and (rule 3-4) to double (diene C=C-C=C
   restored).
6. Convert (rule 5-6) to double (dienophile C=C restored).

Result: a 14-membered macrocyclic *triene* — the macrocycle has
three in-ring C=C bonds (the diene's two double bonds plus the
dienophile's). The exocyclic α,β-unsaturated methyl ester is
unchanged (it was already exocyclic in compound 5).

Mass balance (verified by the build script):
- cyclized (compound 5): C₂₁H₃₂O₃, 332.2351 Da
- seco     (compound 4): C₂₁H₃₂O₃, 332.2351 Da
- Δ MW = 0.0000 Da (TDA byproduct = 0)

Building block: `data/building_blocks/cassaine_seco.yaml`.

Seco canonical SMILES (stereo-free per the Workstream F gap below):

```
COC(=O)/C=C1\CCC=C(C)CCC(O)C(C)(C)C=CC=CC1C
```

### 2.3 ring_size: 6 (not 14) for the strategy gate

The macrocyclic-triene precursor 4 has a 14-membered ring. The
*post-TDA* product 5 has no 14-ring — the [4+2] *contracts* the 14-
membered system into the 6-6-6 fused tricycle, forming a new
cyclohexene (the rule's RHS). MacroCert's `target.ring_size` and the
`strategy.predicates.ring_size_equals` predicate filter the
*product* side of each derivation:

- `target.ring_size = 6` — the new cyclohexene ring the TDA creates.
  Used by `kernel.dg_to_ir._produces_ring_of_size` to flag TDA edges
  as `is_macrocyclization`. With `ring_size = 14`, every TDA edge is
  flagged `is_macrocyclization = false` (the product has no 14-ring)
  and the `exactly_one_macrocyclization` constraint is unsatisfiable.
- `strategy.predicates.ring_size_equals = 6` — same logic at the
  MØD strategy layer; the rightPredicate accepts derivations whose
  product contains a 6-ring (the TDA-formed cyclohexene).

The **literature ring size 14** (the macrocyclic-triene precursor's
ring) is recorded in `expected.yaml` as `literature_ring_size: 14`
for documentation; this field is not used as a strategy filter.

This is a TDA-specific encoding convention because the TDA is the
only macrocyclization rule in macrocert that contracts a larger
substrate ring into a smaller product ring. The other rules
(`rcm`, the lactam/lactone closures, ether closures, cross
couplings, dehydrogenative coupling) all produce a *new ring of the
substrate's macrocycle size*, so `target.ring_size` and
`literature_ring_size` are identical for those cases.

### 2.4 Stereo — Workstream F task #35 (queued, not yet done)

The v0 `data/rules/transannular_diels_alder.gml` rule carries no
stereo annotations on either side of the rewrite. As a consequence:

- The seco's three in-ring C=C bonds are encoded *without* E/Z
  descriptors. Lamothe-Ndibwami-Deslongchamps 1988 (*Tet. Lett.*
  29:1639/1641) specify the *cis-trans-trans* geometry of compound
  4 as the Deslongchamps T4-transition-state precursor; that
  geometry is documented in `cassaine_seco.yaml`'s notes but not
  enforced on the seco SMILES.
- The four new sp³ stereocentres installed by the TDA (C5, C8 ring
  junctions; C10, C13 angular methyl-bearing quaternaries) are
  encoded on `structure.mol` per the predicted T4-transition-state
  stereochemistry but are *not* enforced by the rule on the panel
  run.
- The *endo/exo* selectivity of the TDA is not modelled.

Workstream F **task #35** (TDA stereo encoding for 4 new sp³ centres
+ endo/exo split) is queued behind the broader MØD stereo-
propagation work (see `docs/mod_stereo_reference.md` §1.5, §5.2 and
`docs/workstream_f_harness.md`). The M5 campaign runs without stereo
enforcement on the TDA leg; the documentation here and in
`expected.yaml` flags the gap. v1 will re-enable stereo enforcement
once Workstream F lands the stereo machinery for sets-four-stereo-
centres rules.

## 3. Files written

| Path | Status | Role |
| ---- | ------ | ---- |
| `scripts/build_cassaine.py`                                                                | new      | Authors `structure.mol` (post-TDA tricycle 5). Audits formula/rings/stereo/in-ring-alkene; embeds 3D via RDKit ETKDG, optimises with MMFF, writes V2000 via openbabel. |
| `scripts/build_cassaine_seco.py`                                                           | new      | Derives the 14-membered macrocyclic-triene seco-precursor by applying the reverse of the `transannular_diels_alder` rule on the cyclized tricycle; verifies Δ MW = 0 (TDA byproduct = 0). |
| `data/building_blocks/cassaine_seco.yaml`                                                  | new      | Seco SMILES, provenance, mass-balance trace (Δ MW = 0). |
| `data/validation_panel/phoenix_reddy_cassaine_tda_2008/structure.mol`                      | rewritten | Was a `# PLACEHOLDER` stub; now the V2000 of the post-TDA tricycle (3D-embedded). |
| `data/validation_panel/phoenix_reddy_cassaine_tda_2008/runspec.yaml`                       | rewritten | All-macrocyclization rule sweep, `max_steps: 1`, `ring_close_only: true`, `target.ring_size: 6` (TDA-formed cyclohexene), `predicates.ring_size_equals: 6`, ether-discriminator gates, SCIP `top_n: 10`, energetics disabled. |
| `data/validation_panel/phoenix_reddy_cassaine_tda_2008/expected.yaml`                      | updated  | `literature_tactic: transannular_diels_alder`, `literature_ring_size: 14` (the *precursor*'s ring size), `expected_witness: optimal`, `ae_class: high`, DOI references. |
| `data/validation_panel/phoenix_reddy_cassaine_tda_2008/notes.md`                           | rewritten | Provenance, encoding-choice rationale, TDA disconnection, stereo caveat, references. |
| `data/validation_panel/phoenix_reddy_cassaine_tda_2008/canonical_smiles.txt`               | new      | Canonical isomeric SMILES audit alongside the V2000. |
| `docs/M5_REPORT_phoenix_reddy_cassaine_tda_2008.md`                                        | new      | Auto-generated campaign report (13 tactics, witness + verifier columns). |
| `docs/cassaine_m5.md`                                                                      | new      | This file. |
| `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/`                                      | new      | 13 per-tactic certificates + `manifest.json`; reproducible via `_work/runspec.yaml` in each leg. |

## 4. M5 campaign — full results

`scripts/build_m5_campaign.py` ran each of the 13 macrocyclization
tactics from the `all_macrocyclization` rule-set against the
cassaine 14-membered macrocyclic-triene precursor. SCIP solver,
`top_n: 10`, infeasibility certificates requested.

| Rule                            | Witness    | Bond-level expelled mass | Verifier |
| ------------------------------- | ---------- | ------------------------ | -------- |
| **`transannular_diels_alder`**  | **optimal** | **0.000 g/mol** (zero byproduct) | OK |
| `macrolactamization`            | infeasible | —                        | OK       |
| `macrolactonization`            | infeasible | —                        | OK       |
| `aryl_etherification`           | infeasible | —                        | OK       |
| `biaryl_etherification`         | infeasible | —                        | OK       |
| `c_h_dehydrogenative_coupling`  | infeasible | —                        | OK       |
| `rcm`                           | infeasible | —                        | OK       |
| `cross_coupling_suzuki`         | infeasible | —                        | OK       |
| `cross_coupling_negishi`        | infeasible | —                        | OK       |
| `cross_coupling_buchwald`       | infeasible | —                        | OK       |
| `cross_coupling_sonogashira`    | infeasible | —                        | OK       |
| `cross_coupling_stille`         | infeasible | —                        | OK       |
| `hwe_olefination`               | infeasible | —                        | OK       |

**Shortlist:** `transannular_diels_alder` (the literature tactic) is
the *unique* optimal witness on this substrate. Bond-level expelled
mass 0.000 g/mol matches the rule meta's `byproduct_mass_g_per_mol:
0.0` exactly, confirming zero-byproduct accounting. This is the
highest-atom-economy bond closure in the macrocert rule library;
TDA holds the AE leaderboard for macrocyclization bonds.

**No-go certificates:** The other 12 tactics emit verifier-clean
infeasibility certificates whose IIS centres on
`exactly_one_macrocyclization` plus the seco↔target flow-balance
constraints. The seco substrate carries:

- no amide-acid pair (rules out `macrolactamization`);
- no carboxylic-acid/alcohol pair to form a *new* ester C(=O)-O
  bond (the existing α,β-unsat methyl ester is already a bond in
  the substrate, not a candidate edge — rules out
  `macrolactonization`);
- no Ar-X / Ar-OH / aryl partners (rules out both ether rules and
  all five cross couplings);
- no aromatic-C-H pairs to dehydrogenatively couple (rules out
  `c_h_dehydrogenative_coupling`);
- terminal alkenes are absent from the 14-membered ring (the
  triene's three alkenes are all internal in-ring) — RCM fires
  *across* the alkene pair geometrically but the predicate gate
  rules it out as not matching the target's saturated decalin
  cyclohexanes;
- no phosphonate β-ketoaldehyde pair to HWE-couple (rules out
  `hwe_olefination`).

Each rule's failure mode is captured in its certificate's
`solver_witness.iis_constraint_ids`.

## 5. Verifier and panel test

All 13 certificates were independently re-checked by
`pixi run macrocert-verify`; every exit code is 0.

`pytest tests/panel/ -k phoenix_reddy_cassaine` **passes**
(previously skipped because `_is_placeholder_structure` detected the
`# PLACEHOLDER` header on `structure.mol`):

```
tests/panel/test_panel.py::test_panel_case[phoenix_reddy_cassaine_tda_2008] PASSED
```

The test asserts `report.witness_kind == "optimal"` and that the
literature tactic `transannular_diels_alder` is in the set of rule
IDs used by the top route's flow-positive hyperedges. Both succeed.

## 6. Reproduction

From the repo root:

```bash
# (Re)build the structure and seco precursor:
pixi run python scripts/build_cassaine.py
pixi run python scripts/build_cassaine_seco.py

# (Re)run the M5 campaign:
pixi run python scripts/build_m5_campaign.py \
    data/validation_panel/phoenix_reddy_cassaine_tda_2008

# Verify panel test:
pixi run pytest tests/panel/ -q -k phoenix_reddy
```

The campaign script preserves each leg's staged working directory
under `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/<rule>/_work/`
for reproducibility; the manifest at
`artifacts/phoenix_reddy_cassaine_tda_2008/campaign/manifest.json`
holds per-leg outcome/objective/verifier-exit triples.

## 7. Caveats / followups (v1)

1. **TDA stereo encoding (Workstream F task #35, queued not done).**
   The v0 `transannular_diels_alder.gml` rule carries no stereo
   annotations. The four sp³ centres set by the TDA (C5, C8
   junctions; C10, C13 angular methyls) and the endo/exo split are
   not enforced. The seco's three in-ring alkenes carry no E/Z
   descriptors (the Lamothe-Ndibwami-Deslongchamps *cis-trans-trans*
   geometry is documented but not enforced). v1 should re-enable
   stereo enforcement once Workstream F lands the stereo machinery
   for `sets_four_stereocenters` rules.
2. **Encoded target is compound 5, not natural-product cassaine.**
   The TDA produces a cyclohexene with one residual in-ring alkene;
   cassaine itself (post-elaboration) has only saturated 6-rings.
   Encoding the natural product would force `expected_witness:
   infeasible` (the rule can't match in reverse), contradicting the
   panel convention. The post-TDA elaboration (~6 further steps to
   reach the natural product) would require additional rule classes
   (alkene reduction, hydroboration, methyl cuprate 1,4-addition,
   ester tethering) that are outside `all_macrocyclization`. The
   panel exercises *only* the macrocyclization event.
3. **Methyl ester / free OH simplifications.** The encoded
   tricycle 5 uses a methyl ester (paper: *t*-butyl) and a free C3
   hydroxyl (paper: silyl-protected). These are v0 panel
   conventions; v1 could swap to the paper's *t*-butyl ester +
   silyl ether for closer literature fidelity.
4. **target.ring_size = 6 convention.** Unlike all other panel
   cases, the TDA's `target.ring_size` is the size of the *new*
   ring the rule creates (the cyclohexene), not the size of the
   substrate's macrocycle (14). This is because TDA contracts a
   larger substrate ring into a smaller product ring. The
   convention is documented inline in the runspec; consider a
   schema extension in v1 to distinguish "substrate_ring_size" vs
   "product_ring_size" if more contraction-type rules are added.
5. **Energetics tier disabled.** The TDA is reported as proceeding
   cleanly to the predicted T4 transition-state product on
   compound 4 (the cis-trans-trans triene preorganises the diene
   and dienophile for the *endo* approach). No selectivity gap to
   flag in v1 energetics; the only stereo concern is the rule-level
   gap (#1 above).
6. **3D pose not asserted against an X-ray.** The Phoenix-Reddy-
   Deslongchamps 2008 paper reports X-ray crystallography per its
   MeSH terms but the deposit number requires ACS SI access. The
   RDKit ETKDG + MMFF embed of compound 5 produced a geometrically
   sensible pose but is not validated against experimental
   coordinates. If Ivan has CCDC ConQuest access, a refcode lookup
   by DOI (`10.1021/ja805097s`) would yield the X-ray structure.

## 8. Provenance — citation chain

- **Primary:** Phoenix, S.; Reddy, M. S.; Deslongchamps, P.
  *J. Am. Chem. Soc.* **2008**, *130*, 13989-13995. DOI
  `10.1021/ja805097s`.
- **Earlier communication:** Phoenix, S.; Bourque, E.;
  Deslongchamps, P. *Org. Lett.* **2000**, *2*, 4149-4152. DOI
  `10.1021/ol006670r`.
- **14-membered TDA methodology (theoretical):** Lamothe, S.;
  Ndibwami, A.; Deslongchamps, P. *Tetrahedron Lett.* **1988**,
  *29*, 1639-1640. DOI `10.1016/S0040-4039(00)82005-5`.
- **14-membered TDA methodology (experimental):** Lamothe, S.;
  Ndibwami, A.; Deslongchamps, P. *Tetrahedron Lett.* **1988**,
  *29*, 1641-1644. DOI `10.1016/S0040-4039(00)82006-7`.
- **13-membered TDA lineage (sibling references):** Baettig, K.
  *et al.* *Tetrahedron Lett.* **1987**, *28*, 5249 (DOI
  `10.1016/S0040-4039(00)96699-1`); Baettig, K. *et al.*
  *Tetrahedron Lett.* **1987**, *28*, 5253 (DOI
  `10.1016/S0040-4039(00)96700-5`); Bérubé, G.; Deslongchamps, P.
  *Tetrahedron Lett.* **1987**, *28*, 5255 (DOI
  `10.1016/S0040-4039(00)96701-7`). Three back-to-back Deslongchamps-
  group papers in the 1987 *Tet. Lett.* 28 issue covering the
  cis-trans-trans, trans-cis-cis, and tetrasubstituted-enol-ether-
  dienophile variants of the 13-membered macrocyclic-trienone TDA
  methodology.
- **Structural reference (natural product):** PubChem CID 5281267
  (cassaine), ChEBI:3454, CAS 468-76-8 — mutually consistent
  records on (+)-cassaine (C₂₄H₃₉NO₄, MW 405.288 g/mol). PubChem
  REST API gave the authoritative isomeric SMILES used to cross-
  validate the natural-product framework.
- **Mechanism in broader context:** Taber's *Organic Synthesis*
  book chapter (DOI `10.1093/oso/9780199764549.003.0079`)
  highlighted the Phoenix-Reddy-Deslongchamps cassaine TDA as one
  of 2008's notable Diels-Alder applications. Trauner's
  halenaquinone and Matsuo's platensimycin TDA precedents from
  the same year set the technique in broader context.

---

_Auto-derived structure + seco built 2026-05-24 by the
`scripts/build_cassaine.py` and `scripts/build_cassaine_seco.py`
helper scripts; M5 campaign run reproducibly via
`scripts/build_m5_campaign.py`._
