# M5 Campaign Report — phoenix_reddy_cassaine_tda_2008

_Auto-generated 2026-05-24T17:39:48.724465+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/phoenix_reddy_cassaine_tda_2008/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `transannular_diels_alder` | **optimal** | 0.000 | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/transannular_diels_alder/phoenix_reddy_cassaine_tda_2008__transannular_diels_alder/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/aryl_etherification/phoenix_reddy_cassaine_tda_2008__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/biaryl_etherification/phoenix_reddy_cassaine_tda_2008__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/c_h_dehydrogenative_coupling/phoenix_reddy_cassaine_tda_2008__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/cross_coupling_buchwald/phoenix_reddy_cassaine_tda_2008__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/cross_coupling_negishi/phoenix_reddy_cassaine_tda_2008__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/cross_coupling_sonogashira/phoenix_reddy_cassaine_tda_2008__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/cross_coupling_stille/phoenix_reddy_cassaine_tda_2008__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/cross_coupling_suzuki/phoenix_reddy_cassaine_tda_2008__cross_coupling_suzuki/certificate.json` |
| `hwe_olefination` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/hwe_olefination/phoenix_reddy_cassaine_tda_2008__hwe_olefination/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/macrolactamization/phoenix_reddy_cassaine_tda_2008__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/macrolactonization/phoenix_reddy_cassaine_tda_2008__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/phoenix_reddy_cassaine_tda_2008/campaign/rcm/phoenix_reddy_cassaine_tda_2008__rcm/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`transannular_diels_alder`** — objective 0.000 g/mol; certificate verifier-clean: True

### No-go certificates (12 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CC1=CCC2COC(=O)C=C2C(C)C=CC=CC(C)(C)C…`, `flow_balance:CC1=CCCC2=CC(=O)OCC2(C)C=CC=CC(C)(C)C…`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`
- **`hwe_olefination`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC(=O)C=C1CCC2C(C=CC3C(C)(C)C(O)CCC2…`, `flow_balance:COC(=O)C=C1CCC=C(C)CCC(O)C(C)(C)C=CC=…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/phoenix_reddy_cassaine_tda_2008/`
- seco-precursor block: `data/building_blocks/phoenix_reddy_cassaine_tda_2008_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

