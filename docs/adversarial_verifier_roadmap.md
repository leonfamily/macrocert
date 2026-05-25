# Adversarial Verifier Roadmap

The current adversarial test suite at `tests/verifier/test_adversarial.py`
(80 tests; commit `f97c075` 2026-05-24) covers the 12-rule library that
existed before Workstream F's TDA endo/exo siblings + the HWE rule landed.
Every introduced mutation was caught with the expected exit code on first
run — **no verifier bugs found** by adversarial testing alone (though one
real bug — `dg_to_ir._find_rule_id` substring match — was caught later
during real-target campaign validation).

This document outlines where to extend the suite as the proposal §6
"verifier independence" rigor matures.

## Current coverage

| Mutation class | Exit code | Rules covered | Test count |
|---|---|---|---|
| Atom-map break (label swap) | 10 (conservation) | 9 new rules + 3 original | 12 |
| Tampered expelled-mass | 10 | same 12 | 12 |
| `obj_value`/`flow` disagreement | 20 (witness) | 9 new rules | 9 |
| Edge-mass mismatch | 20 | 9 new rules | 9 |
| Rule-specific | varies | Stille Sn mass, Suzuki boronate O count, dehydrog H₂ disconnection | 3 |
| Original tests (atom-map, expelled mass, dual bound, flow, schema) | 10/20/30 | macrolact + RCM + TDA + energetics | 13 |
| Energetics dependencies | 20 | per-edge tier + OOD | 4 |

Total: 61 in `test_adversarial.py` + 17 in `test_stereo_conservation.py`
+ 8 in `test_cache_key.py` = 86 verifier-adversarial-class tests at end
of 2026-05-24 session. Plus 4 in `test_certify_provenance.py` (cert-
side advisory propagation).

## Coverage gaps (the roadmap)

### 1. Per-rule parametrization for the 3 original rules

`macrolactamization`, `rcm`, `transannular_diels_alder` are tested via
the legacy 13-test path against `artifacts/toy_macrolactam/`. They
should be re-parametrized through the `tests/verifier/fixtures/builders.py`
synthetic-cert harness so they exercise the SAME mutation matrix as
the 9 new rules. Mechanical follow-up; ~20 LOC + 12 new test cases.

### 2. TDA endo/exo stereo-aware adversarial

Workstream F #35 landed `transannular_diels_alder_endo` and `_exo`
siblings (commit `c245bf2`) with `tetrahedral[...]!` annotations on
4 sp³ centres each. Adversarial mutations:

- **Swap endo↔exo in cert**: assert the verifier catches that the
  composed rule's `ruleID` says `_endo` but the atom-map's bracket
  ordering matches `_exo` (i.e., the certificate lies about which
  rule fired). This requires the verifier to actually parse and
  validate stereo annotations against the composed rule — currently
  `check_rule_stereo_conservation` does this for rule-load time
  (`pixi run check-rules`); extending to cert-time is the next step.
- **Tamper with one of the 4 bracket-list entries**: verifier should
  detect that the resulting permutation is no longer a member of
  Tetrahedral's `Good` (even-permutation) table — i.e., the cert
  claims R but the bracket list encodes S.

### 3. Stereo-policy advisory propagation

Workstream F #36 (commit `a57571a`) added
`provenance.stereo_advisories` to certificates that use
`advisory_only` rules (biaryl_etherification, hwe_olefination, rcm).
Adversarial mutations:

- **Strip the advisory** from the cert: assert the verifier rejects
  (or, lighter, warns) when an advisory_only rule fires but the
  cert lacks the expected advisory text.
- **Forge an advisory** that doesn't match the rule's meta.yaml text.
- **Wrong advisory text** for the wrong rule.

These exercise the proposal §6 honesty-constraint plumbing.

### 4. Activator-override adversarial

Workstream C activator override (commit `ee9fd7a`):
`solver.extra.activators` selects per-rule activator from the
`reagent_mass_alternatives` table. Adversarial mutations:

- **Forge an activator name** that doesn't exist in
  `reagent_mass_alternatives`: should fail at runspec-load time
  (verified to fail-fast per `ee9fd7a`). Cert-time adversarial would
  be a cert that names an activator + carries a `reagent_mass`
  value that doesn't match the activator's known value.
- **Substitute mass without renaming**: claim Yamaguchi (568) but
  report mass 482 (Corey-Nicolaou): verifier should detect the
  internal inconsistency.

### 5. Cross-rule attacks (composed adversarial)

The current suite mutates one rule at a time. Real-world attacks
might compose:

- **Stitch two valid hyperedges into a malformed flow**: two edges
  that each verify individually but whose composition violates
  conservation (e.g., the byproduct of one edge is the source of
  another edge that shouldn't fire).
- **Smuggle a byproduct into the product graph**: similar to the
  c_h_dehydrogenative H₂-hidden-in-product attack already in the
  suite, but across two edges instead of one.

### 6. IIS spoofing (infeasibility-cert attacks)

Most existing tests target optimal certs. The 7 §5 deliverables also
emit 12 no-go certs each (84 no-go certs total). Adversarial:

- **Forge an IIS** that includes constraints the rule actually
  satisfies. The verifier should re-derive the IIS from the IR and
  reject if the forged IIS doesn't match.
- **Claim feasibility on a genuinely infeasible cert**: change
  `solver_witness.kind` from `infeasible` to `optimal` without
  changing the flow. Currently caught by witness validation (exit 20)
  but worth a dedicated test.

### 7. SHA-256 tamper detection

Certificates carry no integrity hash today (relying on git history +
the verifier re-deriving everything from the IR). For
deployment-grade rigor:

- Add a `cert.integrity_hash = sha256(canonical_json(cert without
  integrity_hash))` field, signed when produced
- Verifier checks the hash matches the rest of the content
- Adversarial test: tamper with any single field, assert verifier
  rejects

This is a 2026 H2 task; not blocking M5.

## How to extend

`tests/verifier/fixtures/builders.py` is the synthetic-cert factory.
To add a new mutation type:

1. Add a builder function `build_<mutation_class>(rule_id, good_cert)`
2. Parametrize `tests/verifier/test_adversarial.py` over the rule list
3. Assert the expected exit code

The framework was Option-A-lite (per the adversarial expansion agent's
report): real GML body + synthetic IR scaffolding. This decouples the
adversarial coverage from MØD's rate-of-DG-construction (some new
rules take minutes to run real end-to-end campaigns).

## Discoverability

The roadmap above is the documented next set of adversarial mutation
classes. None are blocking M5 — the 80-test current suite already
catches every introduced mutation on first run, and the proposal §6
"verifier independence" criterion is met (the verifier is a separate
process, re-derives everything from the IR, has no rule library
import).

Estimated effort to land all items: 1-2 focused sessions per group;
8-10 hours total for groups 1-4. Groups 5-7 are deployment-grade
hardening; not priorities for the v0 release.
