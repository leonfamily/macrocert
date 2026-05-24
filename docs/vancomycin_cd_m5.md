# M5 §5 Deliverable -- Vancomycin C-O-D Ring (Boger 1999 SNAr)

**Status:** complete; panel test passes.
**Date:** 2026-05-24
**Case:** `data/validation_panel/vancomycin_cde_ring_boger_snar/`
**Verdict:** **Y -- `biaryl_etherification` correctly identified as the literature tactic; objective 20.006 g/mol (HF byproduct).**

---

## 1. Encoding scope and rationale

The full vancomycin aglycon (C53H53Cl2N9O20, MW 1144.93) is sterically
demanding and would not embed reliably in 3D via RDKit/MMFF. For the M5
panel case we encode the **CD-ring model compound** in the style of Boger's
JOC 1999 (64, 70-80) simplified substrates -- a 16-membered biaryl ether
macrocycle that captures the SNAr disconnection without the full heptapeptide:

- Two arenes bridged by the new biaryl ether bond (O-Ar2 + Ar1-F before SNAr).
- Tripeptide tether between them (3 amide bonds, three L-amino-acid Calpha atoms).
- Residue D arene retains its ortho-NO2 activator in the cyclized intermediate
  (Boger reduces NO2 -> H *after* macrocyclization).
- Residue C arene has the bridge O at the para position relative to the
  Calpha attachment (matches Hpg / 4-hydroxyphenylglycine topology).
- Chloro substituent on residue D arene (vancomycin natural-product feature).
- Methyl side chains on the three Calpha atoms (alanine simplification;
  the SNAr rule firing doesn't depend on side-chain identity).
- N-methylamide cap on residue D's C-terminus (mimics the downstream peptide).

Formula: **C22H22ClN5O7**; exact MW **503.121 g/mol**; **16-membered ring**
present; 3 stereocenters (8:S, 13:S, 18:R per RDKit indexing). 3D embed
via RDKit/MMFF succeeds; V2000 Molfile written via OpenBabel.

## 2. Files written

| File | Role |
| --- | --- |
| `data/validation_panel/vancomycin_cde_ring_boger_snar/structure.mol` | V2000 Molfile, cyclized CD-ring model substrate (replaces the PLACEHOLDER) |
| `data/validation_panel/vancomycin_cde_ring_boger_snar/atom_label_map.txt` | RDKit atom-index audit |
| `data/validation_panel/vancomycin_cde_ring_boger_snar/runspec.yaml` | Updated to use `vancomycin_cd_seco` block and proper strategy predicates |
| `data/validation_panel/vancomycin_cde_ring_boger_snar/expected.yaml` | Unchanged (was already correct for `biaryl_etherification`) |
| `data/building_blocks/vancomycin_cd_seco.yaml` | Seco-precursor SMILES, derived by breaking Ar-O-Ar and adding F |
| `scripts/build_vancomycin_cd.py` | Author the cyclized SMILES, verify formula/ring/stereo, embed 3D, write Molfile |
| `scripts/build_vancomycin_cd_seco.py` | Derive the seco-precursor, verify HF mass balance, write block YAML |
| `docs/M5_REPORT_vancomycin_cde_ring_boger_snar.md` | Auto-generated campaign report |
| `docs/vancomycin_cd_m5.md` | **This file** -- M5 §5 narrative |

## 3. Mass balance

```
cyclized MW : 503.1208 g/mol  (C22H22ClN5O7)
seco MW     : 523.1270 g/mol  (C22H23ClFN5O7)
delta       :  20.0062 g/mol  (expected 20.0060 for +HF)
```

Verified by `scripts/build_vancomycin_cd_seco.py` at build time; assertion
trips if delta deviates from HF by more than 0.01 g/mol.

## 4. Campaign outcome

```
M5 campaign: vancomycin_cde_ring_boger_snar; evaluating 12 tactics
[ 1/12] macrolactamization           ... infeasible verifier=OK
[ 2/12] macrolactonization           ... infeasible verifier=OK
[ 3/12] aryl_etherification          ... infeasible verifier=OK
[ 4/12] biaryl_etherification        ... optimal obj=20.006 verifier=OK
[ 5/12] c_h_dehydrogenative_coupling ... infeasible verifier=OK
[ 6/12] rcm                          ... infeasible verifier=OK
[ 7/12] transannular_diels_alder     ... infeasible verifier=OK
[ 8/12] cross_coupling_suzuki        ... infeasible verifier=OK
[ 9/12] cross_coupling_negishi       ... infeasible verifier=OK
[10/12] cross_coupling_buchwald      ... infeasible verifier=OK
[11/12] cross_coupling_sonogashira   ... infeasible verifier=OK
[12/12] cross_coupling_stille        ... infeasible verifier=OK

summary: 1 optimal | 11 no-go | 0 errored
```

The shortlist contains exactly one tactic: `biaryl_etherification`,
matching `expected.yaml`'s `literature_tactic`. The objective value of
20.006 g/mol equals HF's exact mass (Boger's bond-level byproduct).
All 11 other rules emit no-go certificates whose IIS centers on the
`exactly_one_macrocyclization` constraint (none of them can produce the
target ring size from the seco-precursor under the runspec's predicates).

## 5. Panel test outcome

```
pixi run pytest tests/panel/ -q -k vancomycin
.   1 passed, 16 deselected
```

The case no longer skips on the placeholder-structure check, the
witness is `optimal`, and `biaryl_etherification` appears in the
top route's `rule_ids` set. M4 panel-passing policy is satisfied.

## 6. Verifier bug found and fixed

During initial campaign runs, **`aryl_etherification`** was attached as
the rule_id to the certificate's used edge instead of the actual
`biaryl_etherification` that fired. Root cause: `_find_rule_id`
in `src/macrocert/kernel/dg_to_ir.py` used a substring check
`rdef.id in name`, and `"aryl_etherification" in "biaryl_etherification (...)"`
returns True. The bug caused the campaign-pinned biaryl run to report
the wrong rule_id, and the full-rule-set panel run to pick the wrong
rule from among MOD's candidates.

Fix: split the check into two passes -- exact full-ruleID match first,
then word-boundary-safe prefix match (`id == name`, `name.startswith(id + " ")`,
`name.startswith(id + "(")`). The buggy substring check is removed.

After the fix, both campaign and panel certificate's used edge correctly
shows `rule_id=biaryl_etherification`. Verified ascomylactam_a still
produces `aryl_etherification` (no regression on the alkyl-aryl sibling).

## 7. One-line interpretation

**`biaryl_etherification` correctly identified as the literature
tactic for the Boger 1999 CD ring? Y. Objective value 20.006 g/mol (HF).**
