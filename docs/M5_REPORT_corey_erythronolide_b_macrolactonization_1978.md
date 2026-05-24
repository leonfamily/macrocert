# M5 Campaign Report — corey_erythronolide_b_macrolactonization_1978

_Auto-generated 2026-05-24T17:33:08.549234+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/corey_erythronolide_b_macrolactonization_1978/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `macrolactonization` | **optimal** | 18.015 | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/macrolactonization/corey_erythronolide_b_macrolactonization_1978__macrolactonization/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/aryl_etherification/corey_erythronolide_b_macrolactonization_1978__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/biaryl_etherification/corey_erythronolide_b_macrolactonization_1978__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/c_h_dehydrogenative_coupling/corey_erythronolide_b_macrolactonization_1978__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/cross_coupling_buchwald/corey_erythronolide_b_macrolactonization_1978__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/cross_coupling_negishi/corey_erythronolide_b_macrolactonization_1978__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/cross_coupling_sonogashira/corey_erythronolide_b_macrolactonization_1978__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/cross_coupling_stille/corey_erythronolide_b_macrolactonization_1978__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/cross_coupling_suzuki/corey_erythronolide_b_macrolactonization_1978__cross_coupling_suzuki/certificate.json` |
| `hwe_olefination` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/hwe_olefination/corey_erythronolide_b_macrolactonization_1978__hwe_olefination/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/macrolactamization/corey_erythronolide_b_macrolactonization_1978__macrolactamization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/rcm/corey_erythronolide_b_macrolactonization_1978__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/corey_erythronolide_b_macrolactonization_1978/campaign/transannular_diels_alder/corey_erythronolide_b_macrolactonization_1978__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`macrolactonization`** — objective 18.015 g/mol; certificate verifier-clean: True

### No-go certificates (12 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CC1CC(C)(O)C(O)C(C)C(O)C(C(=O)O)CC(C)…`, `flow_balance:CC1CC(C)(O)C(O)C(C)C(O)C(C)(C(=O)O)CC…`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`
- **`hwe_olefination`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CCC(O)C(C)C(O)C(C)C(=O)C(C)CC(C)(O)C(…`, `flow_balance:CCC1OC(=O)C(C)C(O)C(C)C(O)C(C)(O)CC(C…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/corey_erythronolide_b_macrolactonization_1978/`
- seco-precursor block: `data/building_blocks/corey_erythronolide_b_macrolactonization_1978_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

