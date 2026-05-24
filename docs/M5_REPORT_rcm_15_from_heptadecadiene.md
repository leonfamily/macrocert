# M5 Campaign Report — rcm_15_from_heptadecadiene

_Auto-generated 2026-05-24T16:58:06.948220+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/rcm_15_from_heptadecadiene/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `rcm` | **optimal** | 28.054 | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/rcm/rcm_15_from_heptadecadiene__rcm/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/aryl_etherification/rcm_15_from_heptadecadiene__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/biaryl_etherification/rcm_15_from_heptadecadiene__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/c_h_dehydrogenative_coupling/rcm_15_from_heptadecadiene__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/cross_coupling_buchwald/rcm_15_from_heptadecadiene__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/cross_coupling_negishi/rcm_15_from_heptadecadiene__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/cross_coupling_sonogashira/rcm_15_from_heptadecadiene__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/cross_coupling_stille/rcm_15_from_heptadecadiene__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/cross_coupling_suzuki/rcm_15_from_heptadecadiene__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/macrolactamization/rcm_15_from_heptadecadiene__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/macrolactonization/rcm_15_from_heptadecadiene__macrolactonization/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/rcm_15_from_heptadecadiene/campaign/transannular_diels_alder/rcm_15_from_heptadecadiene__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`rcm`** — objective 28.054 g/mol; certificate verifier-clean: True

### No-go certificates (11 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=C1CCCCCCCCCCCCCC1=C`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C1=CCCCCCCCCCCCCC1`, `flow_balance:C=CCCCCCCCCCCCCCC=C`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/rcm_15_from_heptadecadiene/`
- seco-precursor block: `data/building_blocks/rcm_15_from_heptadecadiene_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

