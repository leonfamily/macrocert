# MØD-MacroCert

**Constraint-certified macrocyclization design.** Adapts the
mechanized-proof workflow of Lean 4 to mechanism-level chemistry:
enumerate ring-closing strategies via DPO graph rewriting on
[MØD](https://github.com/jakobandersen/mod), rank by atom economy
via hyperflow ILP, filter by thermodynamic feasibility, and deliver
a small set of certified candidates plus machine-checkable no-go
certificates for ruled-out classes.

## Status

The proposal §5 deliverable line is **operational**.

| Layer | State |
|---|---|
| A — Specification + encoding | Production |
| B — Generation (DPO + MØD) | Production |
| C — Verification + ILP | Production; 15-rule library; 80 adversarial tests |
| D — Energetics (defeasible) | Protocol locked (`data/energetics_protocol.yaml`); MLIP/DFT/TS-search tier-escalation wiring in progress |
| E — Reporting | Production; per-target M5 reports auto-generated |

Seven §5 deliverables shipped, spanning ring sizes 13–31 and
byproducts from zero (TDA) to 126 g/mol (HWE). Every certificate
independently verifier-clean.

See [`docs/INDEX.md`](docs/INDEX.md) for the full document map.

## Quick start

```bash
# 1. Set up the pixi env + native MØD build (see SETUP.md)
pixi install
pixi run build-mod

# 2. Sanity check
pixi run python -m macrocert.cli check-rules data/rules
pixi run pytest tests/ -q

# 3. Run a target end-to-end (single-rule)
pixi run python -m macrocert.cli run data/targets/toy_macrolactam

# 4. Run an M5 campaign (all 15 rules + report)
pixi run python scripts/build_m5_campaign.py data/targets/ascomylactam_a

# 5. Independent verifier (any cert)
pixi run macrocert-verify artifacts/ascomylactam_a/certificate.json
```

## Repository layout

```
data/
  rules/          15 GML rules + meta.yaml + _index.yaml rule-sets
  targets/        production targets (ascomylactam_a is the M5 target)
  validation_panel/    16 panel cases (10 surrogates + 6 literature)
  building_blocks/     seco-precursor YAMLs
  energetics_protocol.yaml   Layer-D production protocol
  pre_registration.template.yaml   §5 pre-registration template

src/macrocert/
  spec/         RunSpec, RuleLibrary, target encoder, SMILES canonicalize
  generate/     MØD strategy composer (Layer B)
  kernel/       backend-neutral IR + two ILP backends (pyscipopt for
                certificates with IIS / duals; mod.hyperflow.Model for
                fast top-N enumeration), rule composition, certificate
                emission (Layer C)
  energetics/   xtb + Psi4 + MACE-OFF drivers, cache, feedback (Layer D)
  verifier/     Independent re-checker (separate-process; import-free
                of macrocert.* except conservation, atom-map, witness)

tests/          spec, kernel, verifier (80 adversarial), energetics,
                panel, integration (byte-determinism)

patches/        Vendored MØD source patches. Currently one: the
                upstream Stereo.hpp:404-407 lone-pair fix (PR draft
                in patches/upstream_PR_draft.md).

scripts/        Build scripts for panel surrogates + the 7 M5 targets;
                build_m5_campaign.py is the §5 deliverable producer;
                pre_m5_gate.py is the deployment gate.

docs/           Research briefs, M5 reports, stereo reference, MØD
                investigation, encoding procedures. Entry point:
                [`docs/INDEX.md`](docs/INDEX.md).

external/mod/   Vendored MØD; `git remote` points to jakobandersen/mod.
                Local branch fix/stereo-finalize-copy-unmatched-r1
                carries the upstream patch that's required for runtime
                stereo enforcement.
```

## The §5 deliverable line

Drop a target in `data/validation_panel/<case>/` or
`data/targets/<case>/` with:

- `structure.mol` (V2000, the cyclized product)
- `runspec.yaml` (declares blocks, rules, predicates, solver, energetics)
- A seco-precursor `building_block` YAML in `data/building_blocks/`
- An optional `expected.yaml` (literature_tactic + ae_class) for panel
  cases

Then `pixi run python scripts/build_m5_campaign.py <dir>` produces:

- 15 per-tactic certificates under
  `artifacts/<target>/campaign/<rule_id>/`
- An aggregated markdown report at `docs/M5_REPORT_<target>.md`
- Each certificate independently re-checked by `macrocert-verify`
- Byte-deterministic across runs (MØD seed pinned via
  `MACROCERT_MOD_SEED` env var, default `0xC0FFEE`)

Examples shipped: ascomylactam A, vancomycin C-O-D ring, epothilone B,
erythronolide B, cytochalasin B, Trost bryostatin analogue,
Phoenix-Reddy cassaine. Per-target reports listed in
[`docs/INDEX.md`](docs/INDEX.md).

## Pre-M5 gate

`pixi run python scripts/pre_m5_gate.py` is the deployment gate that
locks acceptance criteria before any M5 production run. Nine checks:
pre-registration signed, target encoded + signed, panel pass rate ≥
80%, rules conserve, stereo policy declared, energetics protocol
loadable, adversarial verifier exits 0, reproducibility hash matches.
The gate's reproducibility-hash check is backed by deterministic MØD
seeding (`mod.rngReseed` + `MACROCERT_MOD_SEED`, `PYTHONHASHSEED=0`).
Use `data/pre_registration.template.yaml` as the lockfile template;
sign and rename to `pre_registration.lock.yaml` when ready.

## Verifier independence

`pixi run macrocert-verify <cert.json>` is an independent process
that imports only `gml_reader.py` + `conservation.py` +
`stereo_conservation.py` from macrocert; no rule library, no MØD,
no solver. It re-derives every claim from the IR + composed rule.
Exit codes: 0 (OK), 10 (conservation/atom-map fail), 20 (witness
invalid), 30 (schema error).

The 80-test adversarial suite at `tests/verifier/test_adversarial.py`,
the 17-test stereo-conservation suite, and the 8-test cache-key suite
together exercise the verifier against every mutation class catalogued
in [`docs/adversarial_verifier_roadmap.md`](docs/adversarial_verifier_roadmap.md).

## Key references

- [`proposal.md`](proposal.md) — the original design document
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — layer map + load-bearing invariants
- [`RESEARCH_PROPOSAL.md`](RESEARCH_PROPOSAL.md) — the 6-workstream execution plan
- [`SETUP.md`](SETUP.md) — environment provisioning (pixi + native MØD build)
- [`HANDOFF.md`](HANDOFF.md) — current state + onboarding for the next agent
- [`docs/INDEX.md`](docs/INDEX.md) — canonical doc map
