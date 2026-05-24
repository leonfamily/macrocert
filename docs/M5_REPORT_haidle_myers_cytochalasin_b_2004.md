# M5 Campaign Report — haidle_myers_cytochalasin_b_2004

_Auto-generated 2026-05-24T17:35:37.351495+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/haidle_myers_cytochalasin_b_2004/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `hwe_olefination` | **optimal** | 126.050 | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/hwe_olefination/haidle_myers_cytochalasin_b_2004__hwe_olefination/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/aryl_etherification/haidle_myers_cytochalasin_b_2004__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/biaryl_etherification/haidle_myers_cytochalasin_b_2004__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/c_h_dehydrogenative_coupling/haidle_myers_cytochalasin_b_2004__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/cross_coupling_buchwald/haidle_myers_cytochalasin_b_2004__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/cross_coupling_negishi/haidle_myers_cytochalasin_b_2004__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/cross_coupling_sonogashira/haidle_myers_cytochalasin_b_2004__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/cross_coupling_stille/haidle_myers_cytochalasin_b_2004__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/cross_coupling_suzuki/haidle_myers_cytochalasin_b_2004__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/macrolactamization/haidle_myers_cytochalasin_b_2004__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/macrolactonization/haidle_myers_cytochalasin_b_2004__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/rcm/haidle_myers_cytochalasin_b_2004__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/haidle_myers_cytochalasin_b_2004/campaign/transannular_diels_alder/haidle_myers_cytochalasin_b_2004__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`hwe_olefination`** — objective 126.050 g/mol; certificate verifier-clean: True

### No-go certificates (12 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C2(OC(=O)…`, `flow_balance:C=C1C(C)C2C(Cc3ccccc3)NC(=O)C23OC(=O)…`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/haidle_myers_cytochalasin_b_2004/`
- seco-precursor block: `data/building_blocks/haidle_myers_cytochalasin_b_2004_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

