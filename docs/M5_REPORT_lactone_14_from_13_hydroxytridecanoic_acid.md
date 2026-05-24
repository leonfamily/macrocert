# M5 Campaign Report — lactone_14_from_13_hydroxytridecanoic_acid

_Auto-generated 2026-05-24T16:59:03.833315+00:00 by `scripts/build_m5_campaign.py`._

Proposal §5 deliverable: per-tactic certificates for `data/targets/lactone_14_from_13_hydroxytridecanoic_acid/` across all macrocyclization rules.

## Outcome by tactic

| Rule | Witness | Objective (g/mol) | Verifier | Certificate |
|------|---------|-------------------|----------|-------------|
| `aryl_etherification` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/aryl_etherification/lactone_14_from_13_hydroxytridecanoic_acid__aryl_etherification/certificate.json` |
| `biaryl_etherification` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/biaryl_etherification/lactone_14_from_13_hydroxytridecanoic_acid__biaryl_etherification/certificate.json` |
| `c_h_dehydrogenative_coupling` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/c_h_dehydrogenative_coupling/lactone_14_from_13_hydroxytridecanoic_acid__c_h_dehydrogenative_coupling/certificate.json` |
| `cross_coupling_buchwald` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/cross_coupling_buchwald/lactone_14_from_13_hydroxytridecanoic_acid__cross_coupling_buchwald/certificate.json` |
| `cross_coupling_negishi` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/cross_coupling_negishi/lactone_14_from_13_hydroxytridecanoic_acid__cross_coupling_negishi/certificate.json` |
| `cross_coupling_sonogashira` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/cross_coupling_sonogashira/lactone_14_from_13_hydroxytridecanoic_acid__cross_coupling_sonogashira/certificate.json` |
| `cross_coupling_stille` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/cross_coupling_stille/lactone_14_from_13_hydroxytridecanoic_acid__cross_coupling_stille/certificate.json` |
| `cross_coupling_suzuki` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/cross_coupling_suzuki/lactone_14_from_13_hydroxytridecanoic_acid__cross_coupling_suzuki/certificate.json` |
| `macrolactamization` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/macrolactamization/lactone_14_from_13_hydroxytridecanoic_acid__macrolactamization/certificate.json` |
| `macrolactonization` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/macrolactonization/lactone_14_from_13_hydroxytridecanoic_acid__macrolactonization/certificate.json` |
| `rcm` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/rcm/lactone_14_from_13_hydroxytridecanoic_acid__rcm/certificate.json` |
| `transannular_diels_alder` | **infeasible** | — | OK | `artifacts/lactone_14_from_13_hydroxytridecanoic_acid/campaign/transannular_diels_alder/lactone_14_from_13_hydroxytridecanoic_acid__transannular_diels_alder/certificate.json` |

## Interpretation

### Shortlist: empty

No tactic produced an optimal certificate for this target. Review the no-go certificates below.

### No-go certificates (12 ruled-out tactics)

- **`macrolactamization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`macrolactonization`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`aryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`biaryl_etherification`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`c_h_dehydrogenative_coupling`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`rcm`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`transannular_diels_alder`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`cross_coupling_suzuki`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`cross_coupling_negishi`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`cross_coupling_buchwald`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`cross_coupling_sonogashira`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`
- **`cross_coupling_stille`** — IIS (first 3): `exactly_one_macrocyclization`, `flow_balance:O=C(O)CCCCCCCCCCCCO`, `flow_balance:O=C1CCCCCCCCCCCCO1`

Each no-go certificate is independently verifier-clean — the verifier confirms that the rule cannot produce the target from the seco-precursor under the runspec's constraints.

## Provenance

- target dir: `data/targets/lactone_14_from_13_hydroxytridecanoic_acid/`
- seco-precursor block: `data/building_blocks/lactone_14_from_13_hydroxytridecanoic_acid_seco.yaml`
- rule library: `data/rules/_index.yaml` set `all_macrocyclization`
- generated by: `scripts/build_m5_campaign.py`
- each leg's working dir preserved under `artifacts/.../campaign/<rule>/_work/` for reproducibility

## Verification

Every certificate referenced above was independently re-checked by `pixi run macrocert-verify`. The `Verifier` column records the exit code (0 = OK).

