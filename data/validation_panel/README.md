# Retrodictive validation panel (M4)

Per proposal §4.1, the panel runs the *identical* pipeline on a set of
known macrocyclizations and checks that the literature ring-closure
appears as a top-ranked, feasibility-passing candidate.

Each case lives in its own directory:

```
data/validation_panel/<case>/
    runspec.yaml      # consumed by pipeline.run, identical to a target spec
    structure.mol     # the target macrocycle (strict V2000)
    expected.yaml     # the literature outcome we assert
    notes.md          # provenance, reference
```

`expected.yaml` schema:

```yaml
literature_tactic: macrolactamization | rcm | transannular_diels_alder | ...
literature_ring_size: 13
expected_witness: optimal | infeasible
expected_top_rule_class: macrocyclization
ae_class: high | medium | low      # bond-level AE band
reference: |
  Full citation
```

The panel runner (`tests/panel/test_panel.py`) invokes `pipeline.run`
on every case and asserts the witness, the top route's rule class, and
the AE band against `expected.yaml`. ≥ 80% pass rate is the proposal's
M4 exit threshold, and failures are triaged per the `failure_modes`
in `REPORT.md` (rule-library gap vs strategy gap vs τ miscalibration).

## v0 panel composition

**Surrogate cases (encoded here, demonstrating the runner)**: ω-aminoacid
ring-size series + a simple intramolecular RCM + a transannular Diels–Alder
substrate. SMILES are verifiable from public-domain chemistry knowledge;
provenance documented per case.

**Literature cases (TODO — `panel_TODO.md`)**: the proposal calls for
≥ 10 cases drawn from Acc. Chem. Res. 2021 / ACS Cent. Sci. 2020 / Nat.
Prod. Rep. 2019. These require institutional access to the reviews and
chemistry-team sign-off on the encoded substrates before they're added.
The infrastructure here is ready to accept them by dropping
`<case>/{runspec.yaml, structure.mol, expected.yaml, notes.md}` into
this directory — no other plumbing changes needed.
