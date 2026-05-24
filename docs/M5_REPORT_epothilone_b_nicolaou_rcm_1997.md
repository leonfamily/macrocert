# M5 Campaign Report — epothilone_b_nicolaou_rcm_1997

_Auto-generated 2026-05-24T16:58:48.265665+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/epothilone_b_nicolaou_rcm_1997/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `rcm` | **optimal** | 28.054 | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/rcm/epothilone_b_nicolaou_rcm_1997__rcm/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/aryl_etherification/epothilone_b_nicolaou_rcm_1997__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/biaryl_etherification/epothilone_b_nicolaou_rcm_1997__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/c_h_dehydrogenative_coupling/epothilone_b_nicolaou_rcm_1997__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/cross_coupling_buchwald/epothilone_b_nicolaou_rcm_1997__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/cross_coupling_negishi/epothilone_b_nicolaou_rcm_1997__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/cross_coupling_sonogashira/epothilone_b_nicolaou_rcm_1997__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/cross_coupling_stille/epothilone_b_nicolaou_rcm_1997__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/cross_coupling_suzuki/epothilone_b_nicolaou_rcm_1997__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/macrolactamization/epothilone_b_nicolaou_rcm_1997__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/macrolactonization/epothilone_b_nicolaou_rcm_1997__macrolactonization/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/epothilone_b_nicolaou_rcm_1997/campaign/transannular_diels_alder/epothilone_b_nicolaou_rcm_1997__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`rcm`** — objective 28.054 g/mol; certificate verifier-clean: True

### No-go certificates (11 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C(C)C1C=CCC(C(C)=Cc2csc(C)n2)OC(=O)…`, `flow_balance:C=CC1C=C(C)CCCC(C)C(=O)C(C)C(O)C(C)(C…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCC(OC(=O)CC(O)C(C)(C)C(O)C(C)C(=O)…`, `flow_balance:CC1=CCC(C(C)=Cc2csc(C)n2)OC(=O)CC(O)C…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/epothilone_b_nicolaou_rcm_1997/`
- seco-precursor block: `data/building_blocks/epothilone_b_nicolaou_rcm_1997_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

