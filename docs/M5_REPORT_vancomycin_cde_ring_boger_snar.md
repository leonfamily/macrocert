# M5 Campaign Report — vancomycin_cde_ring_boger_snar

_Auto-generated 2026-05-24T17:02:44.625736+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/vancomycin_cde_ring_boger_snar/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `biaryl_etherification` | **optimal** | 20.006 | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/biaryl_etherification/vancomycin_cde_ring_boger_snar__biaryl_etherification/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/aryl_etherification/vancomycin_cde_ring_boger_snar__aryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/c_h_dehydrogenative_coupling/vancomycin_cde_ring_boger_snar__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/cross_coupling_buchwald/vancomycin_cde_ring_boger_snar__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/cross_coupling_negishi/vancomycin_cde_ring_boger_snar__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/cross_coupling_sonogashira/vancomycin_cde_ring_boger_snar__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/cross_coupling_stille/vancomycin_cde_ring_boger_snar__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/cross_coupling_suzuki/vancomycin_cde_ring_boger_snar__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/macrolactamization/vancomycin_cde_ring_boger_snar__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/macrolactonization/vancomycin_cde_ring_boger_snar__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/rcm/vancomycin_cde_ring_boger_snar__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/vancomycin_cde_ring_boger_snar/campaign/transannular_diels_alder/vancomycin_cde_ring_boger_snar__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`biaryl_etherification`** — objective 20.006 g/mol; certificate verifier-clean: True

### No-go certificates (11 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:CNC(=O)C(NC(=O)C(C)NC(=O)C(C)NC(=O)c1…`, `flow_balance:CNC(=O)C1NC(=O)C(C)NC(=O)C(C)NC(=O)c2…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/vancomycin_cde_ring_boger_snar/`
- seco-precursor block: `data/building_blocks/vancomycin_cde_ring_boger_snar_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

