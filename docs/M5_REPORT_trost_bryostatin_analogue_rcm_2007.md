# M5 Campaign Report — trost_bryostatin_analogue_rcm_2007

_Auto-generated 2026-05-24T17:33:57.442616+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/trost_bryostatin_analogue_rcm_2007/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `rcm` | **optimal** | 28.054 | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/rcm/trost_bryostatin_analogue_rcm_2007__rcm/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/aryl_etherification/trost_bryostatin_analogue_rcm_2007__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/biaryl_etherification/trost_bryostatin_analogue_rcm_2007__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/c_h_dehydrogenative_coupling/trost_bryostatin_analogue_rcm_2007__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/cross_coupling_buchwald/trost_bryostatin_analogue_rcm_2007__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/cross_coupling_negishi/trost_bryostatin_analogue_rcm_2007__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/cross_coupling_sonogashira/trost_bryostatin_analogue_rcm_2007__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/cross_coupling_stille/trost_bryostatin_analogue_rcm_2007__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/cross_coupling_suzuki/trost_bryostatin_analogue_rcm_2007__cross_coupling_suzuki/certificate.json` |
| `hwe_olefination` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/hwe_olefination/trost_bryostatin_analogue_rcm_2007__hwe_olefination/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/macrolactamization/trost_bryostatin_analogue_rcm_2007__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/macrolactonization/trost_bryostatin_analogue_rcm_2007__macrolactonization/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/transannular_diels_alder/trost_bryostatin_analogue_rcm_2007__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`rcm`** — objective 28.054 g/mol; certificate verifier-clean: True

### No-go certificates (12 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1CCCCC2OCC(OC(C)=O)CC2CCCCCCCCCCCC…`, `flow_balance:C=CC(CCCC1C(O)CC(O)OC1CC1CCOC(=O)CCCC…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`
- **`hwe_olefination`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=CCCCCC1OCC(OC(C)=O)CC1CCCCCCCCCCCC(…`, `flow_balance:COC(=O)C(C)=CC(=O)OC1CCOC(=O)CCCCCCCC…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/trost_bryostatin_analogue_rcm_2007/`
- seco-precursor block: `data/building_blocks/trost_bryostatin_analogue_rcm_2007_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

