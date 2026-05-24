# M5 Campaign Report — lactam_12_from_11_aminoundecanoic_acid

_Auto-generated 2026-05-24T18:05:59.656589+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/lactam_12_from_11_aminoundecanoic_acid/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `macrolactamization` | **optimal** | 18.015 | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/macrolactamization/lactam_12_from_11_aminoundecanoic_acid__macrolactamization/certificate.json` |
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/aryl_etherification/lactam_12_from_11_aminoundecanoic_acid__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/biaryl_etherification/lactam_12_from_11_aminoundecanoic_acid__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/c_h_dehydrogenative_coupling/lactam_12_from_11_aminoundecanoic_acid__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/cross_coupling_buchwald/lactam_12_from_11_aminoundecanoic_acid__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/cross_coupling_negishi/lactam_12_from_11_aminoundecanoic_acid__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/cross_coupling_sonogashira/lactam_12_from_11_aminoundecanoic_acid__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/cross_coupling_stille/lactam_12_from_11_aminoundecanoic_acid__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/cross_coupling_suzuki/lactam_12_from_11_aminoundecanoic_acid__cross_coupling_suzuki/certificate.json` |
| `hwe_olefination` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/hwe_olefination/lactam_12_from_11_aminoundecanoic_acid__hwe_olefination/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/macrolactonization/lactam_12_from_11_aminoundecanoic_acid__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/rcm/lactam_12_from_11_aminoundecanoic_acid__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/lactam_12_from_11_aminoundecanoic_acid/campaign/transannular_diels_alder/lactam_12_from_11_aminoundecanoic_acid__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist (1 optimal tactic)

Ordered by bond-level expelled mass (lower = better AE):

1. **`macrolactamization`** — objective 18.015 g/mol; certificate verifier-clean: True

### No-go certificates (12 ruled-out tactics)

- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`
- **`hwe_olefination`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:NCCCCCCCCCCC(=O)O`, `flow_balance:O=C1CCCCCCCCCCN1`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/lactam_12_from_11_aminoundecanoic_acid/`
- seco-precursor block: `data/building_blocks/lactam_12_from_11_aminoundecanoic_acid_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

