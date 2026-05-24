# Verifier tests

This package tests the certificate verifier in
`src/macrocert/verifier/`. The verifier is the load-bearing trust
anchor of the system (proposal §1.1): if the verifier passes a
tampered certificate, the certificate is worthless. Every test in
this directory exists to pin one well-defined bug pattern the
verifier MUST catch.

## Layout

| File | What it covers |
| --- | --- |
| `test_gml_reader.py` | Tokenization and parsing of MØD GML rule bodies (the verifier's only producer-stack-free GML reader). |
| `test_conservation.py` | Atom-multiset / atom-map conservation checks on the rule's DPO span. |
| `test_stereo_conservation.py` | Stereo-flag preservation across composed rules. |
| `test_adversarial.py` | End-to-end: take a known-good certificate, mutate one field, assert the verifier returns the expected exit code. |
| `fixtures/` | Helper that synthesizes a minimal valid certificate around a rule's real GML body — see below. |

## Verifier exit codes

The verifier's contract (`src/macrocert/verifier/verify.py:7-11`):

| Code | Meaning |
| --- | --- |
| 0  | valid certificate |
| 10 | conservation / atom-map failure |
| 20 | solver-witness invalid (re-check fails) |
| 30 | schema / format error |

Every adversarial test asserts a specific exit code; a regression
that silently downgrades 10 → 0 (or 20 → 0) is the failure mode
this directory exists to prevent.

## Parametrized adversarial framework (`test_adversarial.py`)

Before 2026-05-24, the adversarial tests only exercised three of the
twelve macrocyclization rules in `data/rules/` (macrolactamization,
rcm, transannular_diels_alder — via the `toy_macrolactam` and panel
artifacts). Workstream C added nine new rules without rule-specific
tampering coverage.

The expansion in 2026-05-24 closes that gap with a parametrized
fixture that builds, for each new rule, a **minimal-but-valid
certificate around the rule's real GML body**:

- `composed_rule.gml` is read verbatim from `data/rules/{rule}.gml`,
  so the verifier's conservation, atom-map, and expelled-mass
  recomputation paths all run against the actual rule the producer
  ships.
- `derivation_graph` is a synthetic 3-vertex / 1-edge scaffold
  (precursor → product + byproduct via a single macrocyclization
  firing). Sufficient to exercise flow-balance, step-budget, and
  macrocyclization-uniqueness checks without invoking the full
  producer pipeline for each rule.
- `solver_witness` is `optimal` with `dual_bound == obj_value ==`
  the rule's bond-level expelled mass.

The helper lives at `fixtures/builders.py`; reuse via
`from .fixtures import build_minimal_certificate, NEW_RULES,
ATOM_MAP_BREAK`.

## Coverage matrix (12 rules × 4 generic mutation types)

| Rule | good cert | atom-map break (10) | tampered expelled mass (10) | obj_value vs flow (20) | edge mass mismatch (20) |
| --- | --- | --- | --- | --- | --- |
| macrolactamization                   | ✓ existing | ✓ existing | ✓ existing | ✓ existing | (n/a — single edge) |
| rcm                                  | (panel)    |  —         |  —         |  —         |  —         |
| transannular_diels_alder             | (panel)    |  —         |  —         |  —         |  —         |
| macrolactonization                   | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| aryl_etherification                  | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| biaryl_etherification                | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| c_h_dehydrogenative_coupling         | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| cross_coupling_suzuki                | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| cross_coupling_negishi               | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| cross_coupling_buchwald              | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| cross_coupling_sonogashira           | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |
| cross_coupling_stille                | ✓ new      | ✓ new      | ✓ new      | ✓ new      | ✓ new      |

Cells marked `—` for `rcm` / `transannular_diels_alder` are deferred:
the existing `test_adversarial.py` exercises only the *exit-code*
behaviour of each generic mutation (via the toy_macrolactam cert), so
the same code path is already pinned. Adding per-rule rcm/TDA
parametrization is straightforward (same fixtures pattern) but was
out of scope for the 2026-05-24 verifier-coverage pass.

## Rule-specific tests (beyond the matrix)

| Test | Rule | Bug pattern guarded against |
| --- | --- | --- |
| `test_stille_sn_mass_recomputed_not_trusted` | cross_coupling_stille | Sn atomic mass regression — Workstream C added Sn (118.710) to `_ATOMIC_MASS`; if dropped, the rule's mass-recompute path would raise instead of returning exit 10. |
| `test_suzuki_off_by_one_boron_oxygen_rejected` | cross_coupling_suzuki | Off-by-one on the boronate B(OH)2O byproduct — the only multi-heteroatom expelled fragment in the rule library. |
| `test_dehydrog_byproduct_claimed_in_product_rejected` | c_h_dehydrogenative_coupling | H2 byproduct hidden in product via spurious R-side bond from retained-root C to byproduct H — only rule with a disconnected-component byproduct. |

## Running

```bash
pixi run pytest tests/verifier/ -q
```

Expected: 85 passed (37 pre-existing + 48 added 2026-05-24).
