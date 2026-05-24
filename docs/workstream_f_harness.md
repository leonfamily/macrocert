# Workstream F Harness Report

Implementation of the three Workstream F components surfaced by the
MØD stereo audit (`docs/mod_stereo_reference.md`). All changes
unstaged.

## Component 1 — LabelSettings stereo enforcement wired through build_dg.py

**Files touched.**
- `src/macrocert/spec/runspec.py`: added `StrategySpec.stereo_enforcement: bool = False` and the corresponding YAML loader hook under `strategy.stereo_enforcement`.
- `src/macrocert/generate/build_dg.py`: gated `LabelSettings(LabelType.Term, LabelRelation.Specialisation, LabelRelation.Specialisation)` on `spec.strategy.stereo_enforcement`. Default (off) preserves the original 2-arg-`LabelSettings` (i.e. omits `labelSettings` from `mod.DG(...)`), so the existing stereo-free rule library is bit-for-bit equivalent.
- `tests/spec/test_runspec.py`: extended to assert the default and an explicit `stereo_enforcement: true` YAML round-trip.
- `tests/spec/test_generate_toy.py`: added `test_stereo_enforcement_constructs_labelsettings_for_dg`, which monkeypatches `mod.DG` to capture its kwargs and verifies the on-path produces `labelSettings` with `withStereo=True` while the off-path omits the field entirely.

**Diff summary.**
- `runspec.py` +14 / –1
- `build_dg.py` +20 / –1
- `test_runspec.py` +22 / 0
- `test_generate_toy.py` +75 / 0

**Citation.** Each block carries a comment pointing to `external/mod/libs/libmod/src/mod/Config.hpp:82-118` (the `LabelSettings` overload set) and `external/mod/examples/py/030_stereo/320_aconitase.py:54-58` (the canonical 3-arg usage).

## Component 2 — Stereo conservation validator

**Files created.**
- `src/macrocert/verifier/stereo_conservation.py` — implements `check_rule_stereo_conservation(gml: str) -> list[StereoIssue]` covering all four invariants from `mod_stereo_reference.md` §3.1:
  - (1) **Even-permutation discipline** — odd-permutation L/R bracket pairs are flagged as `odd_permutation_inversion` *errors* (the highest-value invariant per the task brief).
  - (2) **Fixation transitions** — Sym↔Fixed on the same vertex emits `fixation_transition` *warnings*.
  - (3) **Edge stereo** — emits `edge_stereo_ignored` *info* messages (MØD will ignore the annotation per §5.1).
  - (4) **Geometry registration** — non-tetrahedral *fixed* geometries emit `unenforced_geometry_fixed` warnings (the MOD_ABORT trap from §5.2/§5.3).
- `tests/verifier/test_stereo_conservation.py` — 17 tests covering the sub-grammar parser, permutation parity, all four invariants, and a regression test on the shipped stereo-free macrolactamization rule.

**Files modified.**
- `src/macrocert/cli.py` — `_cmd_check_rules` now runs `check_rule_stereo_conservation` alongside `check_rule_conservation`. Stereo errors flip the exit code; warnings/infos report but do not. The summary line includes counts for warnings and infos.
- `src/macrocert/verifier/gml_reader.py` — softened the `label` field requirement on `left`/`right` nodes so that MØD's stereo-only side annotations (used in `data/stereo` examples) parse. The label is now optional and defaults to `""` (interpreted as "inherit from context").
- `src/macrocert/verifier/conservation.py` — `_labels_disagree` and `_atom_counter` updated so that an empty-label side node inherits its label from `context`, preserving the existing element/charge balance semantics under the relaxed reader.

**Diff summary.**
- `stereo_conservation.py` +290 / 0 (new file)
- `test_stereo_conservation.py` +269 / 0 (new file)
- `cli.py` +34 / –3
- `gml_reader.py` +8 / –1
- `conservation.py` +18 / –4

**Citation.** Comments throughout reference `mod_stereo_reference.md` §3.1, the MØD sources for the partition (`Tetrahedral.cpp:118-155`), the parser (`Stereo/IO/Read.cpp`), and the geometry vocabulary (`Stereo/GeometryGraph.cpp`).

## Component 3 — R/S → local-cyclic-permutation translation doc

**File created.**
- `docs/stereo_encoding_procedure.md` — 178 lines, structured per the brief:
  - §1 *Why R/S is not bracket order* — cross-links to `mod_stereo_reference.md` §1.4 and `Tetrahedral.cpp:118-155`.
  - §2 *Procedure* — the five steps (draw, list, sort, verify against L-alanine, write with `!`).
  - §3 *Worked examples* — lactam α-carbon retention, RCM new sp3 center, Diels–Alder bridgehead.
  - §4 *Pitfalls* — atropisomerism, lone-pair letter tokens, "Sym means either chirality", edge-stereo silent drop, `trigonalPlanar` MOD_ABORT.
  - §5 *References* — Andersen et al. 2017 (DOI 10.1007/978-3-319-61470-0_4), MØD example files, and the four MØD source files most relevant in practice.

## Test results

The Workstream F tests all pass. Running just the spec + verifier scope I touched:

```
$ pixi run pytest tests/verifier/ tests/spec/test_runspec.py tests/spec/test_rules.py \
    tests/spec/test_target.py tests/spec/test_generate_toy.py::test_stereo_enforcement_constructs_labelsettings_for_dg -q
.............................................. 46 passed
```

A broader `pixi run pytest tests/ -q` shows additional failures **unrelated to Workstream F**:

- `tests/panel/test_panel.py::test_panel_case[*]` — multiple panel cases fail because the `data/rules/` directory is being expanded by parallel work (e.g., `aryl_etherification.gml`, `cross_coupling_stille.gml`, etc.) without matching `.meta.yaml` files. This is a `FileNotFoundError` in `spec.rules.load_rule_library`, pre-existing relative to Workstream F.
- `tests/spec/test_generate_toy.py::test_generates_4_vertices_2_edges` — fails 5 ≠ 4 because new rules (`macrolactonization.gml`) added to the library by other work fire on the toy substrate and produce an extra DG vertex.
- `tests/panel/test_panel.py::test_panel_case[vancomycin_cde_ring_boger_snar]` — the structure.mol file is a placeholder ("AWAITING CIF") not a valid V2000 MOL file. Pre-existing.

Workstream F's new test
`test_stereo_enforcement_constructs_labelsettings_for_dg` isolates
itself from the in-flight rule-library churn by staging a one-rule
library (`macrolactamization` only) in `tmp_path`, so it passes
deterministically regardless of what files appear in `data/rules/`.

## Divergence from `mod_stereo_reference.md`

One material divergence between the reference doc and the empirical
MØD behaviour:

- **`MOD_ABORT` on rule composition under `withStereo=true`.** When I
  attempted the obvious end-to-end test for Component 1 — building the
  toy macrolactam DG with `stereo_enforcement=True` using the existing
  stereo-free rule library — MØD fatal-aborts in
  `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:406`
  during the `Repeat`/`Parallel` strategy. The visitor walks stereo
  configurations even for rule pairs whose source GML has *no* stereo
  annotations, hitting `MOD_ABORT` on a `LonePair`/`Radical` branch.
  The warning chatter `WARNING: No viable geometries for O with bonds
  D = 1.` shows that MØD's geometry deduction also struggles with the
  hydroxyl/water oxygens in `macrolactamization.gml`.

  **Consequence.** The stereo-enforcement on-path is currently *only*
  safe for rule libraries explicitly authored to satisfy MØD's
  geometry-deduction pass and to avoid rule composition under
  `Repeat`/`Parallel`. The harness wires the flag correctly, but
  using it on the existing stereo-free library will crash MØD. The
  reference doc's §5.4 anticipated needing empirical verification of
  this corner; the empirical answer is: *the default-off behaviour
  remains the correct setting for the current library*, and turning
  it on requires rule-authoring work that is itself part of the
  larger Workstream F roadmap.

  This is captured in the Component-1 test's docstring and is the
  reason the test verifies constructor wiring (via monkeypatch)
  rather than driving a full `builder.execute` end-to-end.

No other divergences: the `LabelSettings`, `LabelType`, `LabelRelation`
API surfaces match the reference exactly; the GML sub-grammar matches;
the geometry vocabulary matches; the `Good`/`Bad` partition matches
the cycle-decomposition parity used by `_permutation_parity`.

## Blockers

None on the deliverables themselves — all three components are
complete and tested.

The end-to-end "rules with real tetrahedral annotations build under
`stereo_enforcement=True`" sequence is gated on:

1. Reproducing the MOD_ABORT trace under a *single* rule (no `Repeat`
   composition) so we can tell whether the abort is intrinsic to
   match-time stereo or specific to rule composition.
2. Authoring a stereo-augmented variant of `macrolactamization.gml`
   that uses the patterns from `mod_stereo_reference.md` §4.1 (α-carbon
   retention) and the procedure in `docs/stereo_encoding_procedure.md`.
3. Wiring the verifier's stereo conservation check into the certificate
   re-check path (`verifier/verify.py`) so that certificates produced
   with `stereo_enforcement=True` carry stereo-conservation proofs
   in the certificate body.

Items 2 and 3 are follow-ups outside the current task.
