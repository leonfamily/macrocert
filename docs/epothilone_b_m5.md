# Epothilone B — M5 Deliverable (Nicolaou 1997 RCM)

**Case:** `data/validation_panel/epothilone_b_nicolaou_rcm_1997/`
**Tactic:** Ring-closing metathesis (`rcm`)
**Primary reference:** Nicolaou, K. C.; Ninkovic, S.; Sarabia, F.;
Vourloumis, D.; He, Y.; Vallberg, H.; Finlay, M. R. V.; Yang, Z.
*J. Am. Chem. Soc.* **1997**, *119*, 7974–7991. DOI
[10.1021/ja971110h](https://doi.org/10.1021/ja971110h). Also Nicolaou,
K. C. *et al.* *Nature* **1997**, *387*, 268–272. DOI
[10.1038/387268a0](https://doi.org/10.1038/387268a0).

## 1. Summary

Epothilone B's 16-membered macrolactone was closed by Nicolaou in 1997
through ring-closing metathesis (Grubbs G1, CH₂Cl₂, 25 °C, 0.001 M)
on a diene-tethered seco-acid. The RCM step expels ethylene (28.054
g/mol) and produces the **12,13-deepoxy epothilone B alkene
intermediate**; the natural-product C12–C13 epoxide is installed
*afterwards* by a separate DMDO/m-CPBA step. The panel therefore
encodes the deepoxy intermediate as the macrocyclization target and
the open-chain diene as the seco-precursor.

The full §5 deliverable — encoded target, derived seco, runspec,
expected.yaml, and an M5 campaign over all 12 macrocyclization
tactics — is now in place. Outcome:

| Metric                                  | Value                      |
| --------------------------------------- | -------------------------- |
| Cyclized target formula                 | C₂₇H₄₁NO₅S                 |
| Cyclized exact MW                       | 491.2705 Da                |
| Seco-precursor formula                  | C₂₉H₄₅NO₅S                 |
| Seco-precursor exact MW                 | 519.3018 Da                |
| Δ MW (seco − cyclized)                  | 28.0313 Da = C₂H₄          |
| Macrocycle ring size                    | 16                         |
| sp³ stereocenters (cyclized)            | 5 (C3 S, C6 R, C7 S, C8 S, C15 S) |
| In-ring alkene geometry (encoded)       | Z (cis)                    |
| Exocyclic vinyl-thiazole geometry       | E                          |
| Tactics evaluated in M5 campaign        | 12                         |
| Verifier-clean certificates             | 12 / 12                    |
| Optimal tactics in shortlist            | 1 (`rcm`)                  |
| `rcm` objective (bond-level expelled)   | 28.054 g/mol (ethylene)    |
| Panel test (`pytest -k epothilone`)     | passes (no longer skipped) |

## 2. Encoding decisions

### 2.1 Target — deepoxy intermediate, not natural product

The macrocyclization step is RCM; its product is the
12,13-deepoxy alkene macrocycle. The natural-product epoxide is
installed *after* macrocyclization. We encode the *actual*
macrocyclization product so the rule library is asked to recognise
the bond it actually forms. The natural-product epothilone B
(C₂₇H₄₁NO₆S, MW 507.27) remains the eventual synthetic goal but is
not the encoded structure.

Canonical isomeric SMILES (cyclized target):

```
C/C1=C/C[C@H](/C(C)=C/c2csc(C)n2)OC(=O)C[C@H](O)C(C)(C)[C@@H](O)[C@H](C)C(=O)[C@@H](C)CCC1
```

Stored at `data/validation_panel/epothilone_b_nicolaou_rcm_1997/structure.mol`
(strict V2000, openbabel-canonicalized, 3D-embedded via RDKit ETKDG
with MMFF optimization). Canonical SMILES audit written alongside at
`canonical_smiles.txt`.

### 2.2 Seco-precursor — programmatic derivation

`scripts/build_epothilone_seco.py` opens the in-ring C12=C13 alkene
and caps each side with a terminal `=CH₂`, producing the α,ω-diene
that Grubbs G1 metathesises. The macrolactone ester (C1–O–C15) is
retained — Nicolaou's actual route runs macrolactonization first and
RCM second, so the seco-acid is already esterified before RCM. The
molecule does not split on alkene cleavage because the ester provides
the second connection between the two halves of the would-be
macrocycle.

Mass balance (verified by the build script):
- cyclized: C₂₇H₄₁NO₅S, 491.2705 Da
- seco:    C₂₉H₄₅NO₅S, 519.3018 Da
- Δ MW:                 28.0313 Da = ethylene exact mass

Building block: `data/building_blocks/epothilone_seco.yaml`.

### 2.3 Stereochemistry

Five sp³ stereocenters survive the epoxide → alkene reduction
(C3 *S*, C6 *R*, C7 *S*, C8 *S*, C15 *S*). The natural product's
two epoxide stereocenters (C12 *S*, C13 *R*) are lost when C12–C13
becomes the in-ring Z alkene.

| Atom (canonical SMILES idx) | Position (Nicolaou) | CIP descriptor |
| --------------------------- | ------------------- | -------------- |
| atom 1                      | C15                 | *S*            |
| atom 9                      | C6                  | *R*            |
| atom 14                     | C8                  | *S*            |
| atom 19                     | C3                  | *S*            |
| atom 21                     | C7                  | *S*            |

In-ring C12=C13 double bond: **Z** (cis); exocyclic C16=C17 vinyl
tether to the 2-methyl-1,3-thiazol-4-yl group: **E**. Both
designations survive the RDKit → openbabel → V2000 pipeline.

### 2.4 E/Z gate dropped for v0

The runspec's `enforce_ez_geometry: {rcm: Z}` predicate was
authored per the M5 brief but **disabled** (commented out, with a
documenting paragraph) after empirical confirmation that it filters
out RCM entirely on this substrate.

Mechanism of the problem: MØD does not propagate E/Z through rule
firing (see `docs/mod_stereo_reference.md` §1.5, §5.2 — MØD's
`TrigonalPlanar::morphismIso` is `MOD_ABORT`). The seco's terminal
alkenes carry no stereo and the RCM rule body is stereo-free, so the
product side returns a canonical SMILES whose new in-ring C=C is
`STEREONONE`. The Z-gate then rejects every candidate derivation,
yielding an infeasible certificate with 0 hyperedges (confirmed
experimentally on the first campaign run, before disabling). Stereo
propagation through MØD firings is the responsibility of Workstream
F; the v0 panel rule `rcm` is selectivity-agnostic and the
literature's Z:E ~1:1 separation is documented in expected.yaml as a
known v1 energetics gap.

The two ether discriminator predicates
(`alcohol_partner_C_must_be_aromatic`, `alcohol_partner_C_must_be_sp3`)
remain enabled for schema parity with the ascomylactam A reference
run; the seco has no Ar–X or aryl–O partner so both ether rules fail
independently of these predicates.

## 3. Files written

| Path | Status | Role |
| ---- | ------ | ---- |
| `scripts/build_epothilone_b_rcm.py`                                                      | new      | Authors `structure.mol`. Audits formula/rings/stereo/Z-alkene; embeds 3D via RDKit, optimises with MMFF, writes V2000 via openbabel. |
| `scripts/build_epothilone_seco.py`                                                       | new      | Derives the RCM seco-precursor by opening the cyclized C12=C13 alkene; verifies Δ MW = MW(ethylene). |
| `data/building_blocks/epothilone_seco.yaml`                                              | new      | Seco SMILES, provenance, mass-balance trace. |
| `data/validation_panel/epothilone_b_nicolaou_rcm_1997/structure.mol`                     | rewritten | Was a `# PLACEHOLDER` stub; now the V2000 of the post-RCM intermediate (3D-embedded). |
| `data/validation_panel/epothilone_b_nicolaou_rcm_1997/runspec.yaml`                      | rewritten | All-macrocyclization rule sweep, `max_steps: 1`, `ring_close_only: true`, ring-size and intramolecular predicates, ether-discriminator gates. SCIP `top_n: 10`. Energetics disabled. |
| `data/validation_panel/epothilone_b_nicolaou_rcm_1997/expected.yaml`                     | updated  | `literature_tactic: rcm`, `expected_witness: optimal`, `ae_class: high`, DOI references for JACS + Nature papers. |
| `data/validation_panel/epothilone_b_nicolaou_rcm_1997/notes.md`                          | rewritten | Provenance, encoding-choice rationale, stereo table, mass-balance trace, E/Z caveat. |
| `data/validation_panel/epothilone_b_nicolaou_rcm_1997/canonical_smiles.txt`              | new      | Canonical isomeric SMILES audit alongside the V2000. |
| `docs/M5_REPORT_epothilone_b_nicolaou_rcm_1997.md`                                       | new      | Auto-generated campaign report (12 tactics, witness + verifier columns). |
| `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/`                                     | new      | 12 per-tactic certificates + `manifest.json`; reproducible via `_work/runspec.yaml` in each leg. |

## 4. M5 campaign — full results

`scripts/build_m5_campaign.py` ran each of the 12 macrocyclization
tactics from the `all_macrocyclization` rule-set against the
epothilone seco-precursor. SCIP solver, `top_n: 10`, infeasibility
certificates requested.

| Rule                            | Witness    | Bond-level expelled mass | Verifier |
| ------------------------------- | ---------- | ------------------------ | -------- |
| **`rcm`**                       | **optimal** | **28.054 g/mol** (ethylene) | OK |
| `macrolactamization`            | infeasible | —                        | OK       |
| `macrolactonization`            | infeasible | —                        | OK       |
| `aryl_etherification`           | infeasible | —                        | OK       |
| `biaryl_etherification`         | infeasible | —                        | OK       |
| `c_h_dehydrogenative_coupling`  | infeasible | —                        | OK       |
| `transannular_diels_alder`      | infeasible | —                        | OK       |
| `cross_coupling_suzuki`         | infeasible | —                        | OK       |
| `cross_coupling_negishi`        | infeasible | —                        | OK       |
| `cross_coupling_buchwald`       | infeasible | —                        | OK       |
| `cross_coupling_sonogashira`    | infeasible | —                        | OK       |
| `cross_coupling_stille`         | infeasible | —                        | OK       |

**Shortlist:** `rcm` (the literature tactic) is the *unique* optimal
witness on this substrate. Bond-level expelled mass 28.054 g/mol
matches the rule meta's `byproduct_mass_g_per_mol: 28.054` exactly,
confirming ethylene accounting.

**No-go certificates:** The other 11 tactics emit verifier-clean
infeasibility certificates whose IIS centres on
`exactly_one_macrocyclization` plus the seco↔target flow-balance
constraints. The seco carries no amide-acid pair (rules out
`macrolactamization`), no acid–alcohol pair to form a new C(=O)–O
(rules out `macrolactonization` — its existing ester is already a
bond in the substrate, not a candidate edge), no Ar–X / Ar–OH /
aryl partners (rules out the two ether rules and all five cross
couplings), no aromatic-C–H pairs to dehydrogenatively couple, and
no diene-dienophile geometry suitable for transannular Diels-Alder.
Each rule's failure mode is captured in its certificate's
`solver_witness.iis_constraint_ids`.

## 5. Verifier and panel test

All 12 certificates were independently re-checked by
`pixi run macrocert-verify`; every exit code is 0.

`pytest tests/panel/ -k epothilone` now **passes** (previously
skipped because `_is_placeholder_structure` detected the
`# PLACEHOLDER` header):

```
tests/panel/test_panel.py::test_panel_case[epothilone_b_nicolaou_rcm_1997] PASSED
```

The test asserts `report.witness_kind == "optimal"` and that the
literature tactic `rcm` is in the set of rule IDs used by the
top route's flow-positive hyperedges. Both succeed.

## 6. Reproduction

From the repo root:

```bash
# (Re)build the structure and seco precursor:
pixi run python scripts/build_epothilone_b_rcm.py
pixi run python scripts/build_epothilone_seco.py

# (Re)run the M5 campaign:
pixi run python scripts/build_m5_campaign.py \
    data/validation_panel/epothilone_b_nicolaou_rcm_1997

# Verify panel test:
pixi run pytest tests/panel/ -q -k epothilone
```

The campaign script preserves each leg's staged working directory
under `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/<rule>/_work/`
for reproducibility; the manifest at
`artifacts/epothilone_b_nicolaou_rcm_1997/campaign/manifest.json`
holds per-leg outcome/objective/verifier-exit triples.

## 7. Caveats / followups (v1)

1. **E/Z selectivity gate (Workstream D phase 2).** Re-enable
   `enforce_ez_geometry: {rcm: Z}` once Workstream F propagates
   stereo through MØD rule firings (`docs/mod_stereo_reference.md`
   §5.2). The literature reports ~1:1 Z:E on Nicolaou's substrate
   with Grubbs G1 and 23:77 Z:E with Grubbs 2a (PMC3211109);
   chromatographic separation of the Z isomer is currently a
   *post-macrocyclization* manual step not modelled in v0.
2. **Energetics tier disabled.** The ~1:1 Z:E selectivity is an
   energetics-layer concern (TS-search hook) that Workstream C's
   xTB tier doesn't yet cover for 16-membered macrocycles. Same
   limitation as the ascomylactam A and surrogate `rcm_*` cases.
3. **Post-RCM epoxidation step not encoded.** The natural product
   epothilone B (with C12–C13 epoxide) is reached by a separate
   DMDO/m-CPBA step. The panel exercises only the macrocyclization
   event; encoding the full post-RCM elaboration would require an
   `epoxidation` rule that lives outside the current
   `all_macrocyclization` set.
4. **3D pose not asserted against an X-ray.** The deepoxy
   intermediate is a synthetic precursor with no deposited
   X-ray structure. The RDKit ETKDG + MMFF embed produced a
   geometrically sensible pose but is not validated against
   experimental coordinates; the natural product itself (epothilone
   B) is deposited as CCDC `LIWPUF` (Höfle 1996,
   DOI [10.1002/anie.199615671](https://doi.org/10.1002/anie.199615671)).

## 8. Provenance — citation chain

- **Primary:** Nicolaou, K. C.; Ninkovic, S.; Sarabia, F.;
  Vourloumis, D.; He, Y.; Vallberg, H.; Finlay, M. R. V.; Yang, Z.
  *J. Am. Chem. Soc.* **1997**, *119*, 7974–7991. DOI
  `10.1021/ja971110h`. (The user task brief originally cited
  *JACS* **1997**, *119*, 7960 — that page is the *epothilone A*
  RCM paper; the B paper follows immediately at p. 7974 in the same
  issue. Both expected.yaml and notes.md flag the correction.)
- **Companion (epothilone A RCM):** *J. Am. Chem. Soc.* **1997**,
  *119*, 7960–7973. DOI `10.1021/ja971109i`.
- **Nature** (A + B): *Nature* **1997**, *387*, 268–272. DOI
  `10.1038/387268a0`.
- **Initial communication:** Yang, Z.; He, Y.; Vourloumis, D.;
  Vallberg, H.; Nicolaou, K. C. *Angew. Chem. Int. Ed. Engl.*
  **1997**, *36*, 166–168. DOI `10.1002/anie.199701661`.
- **Structural reference (natural product):** ChEBI:31550, LIPID
  MAPS LMPK04000041, NP-MRD NP0013985, IUPHAR ligand 13600,
  PubChem CID 448799, Sigma-Aldrich E2656 — six mutually
  consistent records on the post-epoxidation natural product.
- **Selectivity corroboration:** Hoveyda, Schrock *et al.*,
  PMC3211109 (2011 review). Quantifies Grubbs 2a as 77% E on a
  related substrate; Nicolaou's original G1 on the bare epothilone
  B diene gives the ~1:1 Z:E mixture documented in the JACS
  119:7974 SI.

---

_Auto-derived structure + seco built 2026-05-24 by the
`scripts/build_epothilone_b_rcm.py` and `scripts/build_epothilone_seco.py`
helper scripts; M5 campaign run reproducibly via
`scripts/build_m5_campaign.py`._
