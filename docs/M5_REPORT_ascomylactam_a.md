# M5 Campaign Report — ascomylactam_a

_Auto-generated 2026-05-24T16:44:44.416196+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/ascomylactam_a/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `aryl_etherification` | **optimal** | 20.006 | OK | `artifacts/ascomylactam_a/campaign/aryl_etherification/ascomylactam_a__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/biaryl_etherification/ascomylactam_a__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/c_h_dehydrogenative_coupling/ascomylactam_a__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/cross_coupling_buchwald/ascomylactam_a__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/cross_coupling_negishi/ascomylactam_a__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/cross_coupling_sonogashira/ascomylactam_a__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/cross_coupling_stille/ascomylactam_a__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/cross_coupling_suzuki/ascomylactam_a__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/macrolactamization/ascomylactam_a__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/macrolactonization/ascomylactam_a__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/rcm/ascomylactam_a__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/ascomylactam_a/campaign/transannular_diels_alder/ascomylactam_a__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`aryl_etherification`** — objective 20.006 g/mol; certificate verifier-clean: True

### No-go certificates (11 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:COC1C(=C(O)C23C(C)C(C)=CC2(C)C=C(C)C2…`, `flow_balance:COC1C2=C(O)C34C(C)C(C)=CC3(C)C=C(C)C3…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/ascomylactam_a/`
- seco-precursor block: `data/building_blocks/ascomylactam_a_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

