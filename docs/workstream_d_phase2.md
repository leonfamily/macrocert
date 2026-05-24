# Workstream D phase 2 — `enforce_ez_geometry` rightPredicate

Implementation report for the third Workstream D predicate. Builds on
phase 1's `is_intramolecular` (leftPredicate) and `ring_size_equals`
(rightPredicate) framework, using the same outside-in composition
around the inner `mod.repeat[steps](rules)` block.

The phase-1 reference doc `docs/workstream_d_predicates.md` has been
extended with a new §3 covering the user-facing semantics; this file
captures the implementation-side surface area, tests, and the
divergences from the task spec discovered during integration.

## API

### YAML schema

```yaml
strategy:
  predicates:
    enforce_ez_geometry:
      rcm: "E"                       # or "e", "E" — normalised to upper case
      transannular_diels_alder: "Z"
```

- Dict keyed by macrocert `rule_id` (GML filename stem).
- Value `"E"` or `"Z"`; anything else raises `ValueError` at
  `load_runspec`.
- Field is optional. A RunSpec without it deserialises to
  `PredicateSpec.enforce_ez_geometry = None`, which composes as a
  no-op (strategy is identical to the v0 path).

### Python dataclasses

- `macrocert.spec.runspec.PredicateSpec.enforce_ez_geometry:
  dict[str, str] | None = None`
- `macrocert.generate.strategies.PredicateSpec.enforce_ez_geometry:
  Optional[dict] = None`
- `PredicateSpec.is_empty()` now also requires
  `not self.enforce_ez_geometry`.

### Strategy wiring

`apply_rules_up_to_with_predicates` adds, when `enforce_ez_geometry`
is non-empty:

```python
gated = mod.rightPredicate[_enforce_ez_geometry_factory(map_)](gated)
```

Composed *inside* the leftPredicate / outside the
`ring_size_equals` rightPredicate, but the three predicates are
conjunctive so order is semantically irrelevant.

### Predicate factory

`_enforce_ez_geometry_factory(rule_to_geometry: dict) -> Callable`

For each candidate derivation:

1. `rule_name = derivation.rule.name` (with `derivation.r` fallback —
   see "MØD-API divergences" below).
2. Find the key `k` in the map such that `rule_name == k` or
   `rule_name.startswith(k + " ")`. Macrocert GML files name their
   rules with the convention `ruleID "<rule_id> (<description>)"` —
   see e.g. `data/rules/rcm.gml:2` —
   `"rcm (ring-closing metathesis, -C2H4)"`.
3. If no match → return `True` (no-op for unmapped rules).
4. Otherwise iterate `derivation.right`, parse each product's
   `g.smiles` via RDKit, run `Chem.FindPotentialStereoBonds`, and
   return `True` iff any `BondType.DOUBLE` bond has
   `Bond.GetStereo()` in the requested geometry class
   (`STEREOE`/`STEREOTRANS` for "E", `STEREOZ`/`STEREOCIS` for "Z").

## Tests

`tests/spec/test_generate_predicates.py` — seven new tests:

| Test                                                  | Surface |
|-------------------------------------------------------|---------|
| `test_ez_predicate_accepts_e_and_rejects_z`           | Direct unit test on mock `_MockDerivation` with explicit `/C=C/` vs `/C=C\` SMILES — the predicate's only real behaviour |
| `test_ez_predicate_noop_for_other_rules`              | Map `{rcm: "E"}` is a no-op when `derivation.rule.name` is `macrolactamization (…)` |
| `test_ez_predicate_rejects_stereo_undetermined_products` | Documents the MØD stereo-gap consequence: STEREONONE fails an E gate |
| `test_ez_predicate_parsed_from_yaml`                  | YAML round-trip with case normalisation (`e` → `"E"`) |
| `test_ez_predicate_yaml_rejects_invalid_token`        | `{rcm: "cis"}` raises `ValueError` at load |
| `test_ez_predicate_filters_rcm_to_e_only`             | End-to-end DG build on `pentadecadiene` + `rcm`: ungated has 4 vertices / 2 edges, gated has 0 RCM-closure edges. `gated.numEdges < ungated.numEdges` records the filter effect |
| `test_ez_predicate_macrolactam_run_unaffected`        | The map `{rcm: "E"}` on a macrolactamization-only run leaves the toy_macrolactam 4-vertex / 2-edge baseline intact |

`test_empty_predicate_spec_is_empty` was extended to assert that
`PredicateSpec(enforce_ez_geometry={"rcm": "E"})` is *not* empty.

```
$ pixi run pytest tests/ -q
76 passed, 3 skipped in 2.70s
```

Baseline (before changes): 69 passed / 3 skipped. Increase: +7 = the
seven additions above. No prior tests were modified.

## Edge cases

1. **`derivation.rule is None`.** Defensive — the predicate returns
   `True` (no-op). Cannot happen via `mod.rightPredicate` of a
   `repeat[rules]` strategy in practice, but guards against future
   non-rule derivations.
2. **`Chem.MolFromSmiles` returns `None`.** Treated as "no double bond
   in the right geometry" → reject. Should be unreachable for products
   MØD considers valid graphs, but a malformed SMILES never crashes
   the predicate.
3. **STEREONONE / STEREOANY products.** The predicate is a *positive*
   filter — undetermined geometry fails the gate. This is the correct
   behaviour for "we don't know if it's E, so don't trust it" but it
   means that, in the current rule library (where no rule's GML
   carries `trigonalPlanar[...]!` annotations), the E/Z predicate
   blocks every RCM derivation. `test_ez_predicate_filters_rcm_to_e_only`
   asserts this. The natural follow-up is Workstream F adding
   stereo-creating rule annotations.
4. **Unknown rule_id in the map.** Logged implicitly — the predicate
   simply never matches, and behaves as if the map were empty for that
   rule. (No early validation against the rule library, which would
   couple the parser to the rules directory.)
5. **Multiple products per derivation.** The predicate accepts the
   derivation if *any* product graph in `derivation.right` carries the
   wanted geometry. This matches the existing `ring_size_equals`
   semantics (also "any product carries the ring") and the formose
   example pattern in
   `external/mod/examples/py/020_dg/212_dgPredicate.py`.
6. **Empty map vs `None`.** Both deserialise to the empty/None form
   and skip the predicate wiring. `PredicateSpec.is_empty()` uses a
   truthiness test (`not self.enforce_ez_geometry`).
7. **Case insensitivity.** YAML loader accepts `e`, `E`, `z`, `Z` and
   normalises to upper case; the predicate compares against
   upper-case tokens.
8. **Backward compatibility.** Two RunSpecs in the repo were
   re-tested:
   - `data/targets/toy_macrolactam` — no `predicates:` section at all,
     parses to `PredicateSpec()` with `enforce_ez_geometry=None`. v0
     path unchanged.
   - `data/targets/toy_macrolactam_predicated` — sets
     `is_intramolecular: true` and `ring_size_equals: 13`. Phase 1
     fields still parse identically and the existing
     `test_predicated_dg_has_3_vertices_1_edge` test still passes.

## MØD-API divergences encountered

1. **`derivation.rule`, not `derivation.r`.** The task description
   instructed me to call `derivation.r.name`. MØD's C++ field
   `mod::Derivation::r`
   (`external/mod/libs/libmod/src/mod/Derivation.hpp:39`) is renamed
   to the Python attribute **`rule`** by the binding
   (`external/mod/libs/pymod/src/mod/py/Derivation.cpp:32`). Hitting
   this raised `AttributeError: 'Derivation' object has no
   attribute 'r'` inside the predicate; the segfault that masked it
   was pytest's `saferepr` trying to print a MØD-backed exception
   payload. The predicate now reads `getattr(derivation, "rule",
   None) or getattr(derivation, "r", None)` so both names work, and
   the test mock exposes both attributes for the same reason.

2. **Rule name carries a description tail.** `derivation.rule.name`
   returns the full GML `ruleID` string, e.g. `"rcm (ring-closing
   metathesis, -C2H4)"`, not the macrocert filename stem. The
   predicate matches both `rule_name == k` *and* `rule_name.startswith(k
   + " ")` so the YAML key `rcm` matches the on-disk MØD name. If a
   future rule's `ruleID` does not start with its macrocert id this
   matcher will silently miss; a `check-rules` audit could be added in
   a follow-up but is out of scope for this milestone.

3. **MØD strategy-side stereo enforcement remains MOD_ABORT.** This
   predicate is precisely the strategy-level workaround for the gap
   audited in `docs/mod_stereo_reference.md` §1.5, §5.2. Combined with
   Workstream F's `stereo_enforcement` switch
   (`spec.strategy.stereo_enforcement`), the E/Z gate is the only
   pre-LayerD mechanism that can reject Z-only products when MØD
   would otherwise materialise them as STEREONONE. The phase-1
   `is_intramolecular` + `ring_size_equals` predicates remain
   sufficient for ring-topology filtering; only E/Z requires the new
   path.

## Files modified (unstaged)

- `src/macrocert/spec/runspec.py` — added field, loader, validation.
- `src/macrocert/generate/strategies.py` — added factory, helper,
  strategy wiring, `PredicateSpec.is_empty` update.
- `src/macrocert/generate/build_dg.py` — forwarded the new field
  through the spec→generate translation.
- `tests/spec/test_generate_predicates.py` — seven new tests +
  extended `test_empty_predicate_spec_is_empty`.
- `docs/workstream_d_predicates.md` — appended §3 covering the new
  predicate.
- `docs/workstream_d_phase2.md` — this report.

No data files, rule GML, or RunSpec YAML were modified. The change is
purely additive at the spec/strategy layers.

## References cited (per the macrocert citation rule)

MØD source files (all under `external/mod/`):

- `libs/libmod/src/mod/Derivation.hpp:23-49` — Derivation C++ struct.
- `libs/libmod/src/mod/rule/Rule.hpp:129-133` — `Rule::getName`.
- `libs/libmod/src/mod/graph/Graph.hpp:118` — `Graph::getSmiles`.
- `libs/pymod/src/mod/py/Derivation.cpp:26-38` — Python attribute
  rename `r` → `rule`.
- `libs/pymod/src/mod/py/rule/Rule.cpp:123` — `rule.name` binding.
- `libs/pymod/src/mod/py/dg/Strategies.cpp:33,69,173-181` —
  `rightPredicate` binding.
- `libs/libmod/src/mod/lib/Stereo/Configuration/TrigonalPlanar.cpp:50-54`
  — the `MOD_ABORT` that motivates this whole predicate.
- `examples/py/020_dg/212_dgPredicate.py` — canonical `rightPredicate`
  usage pattern.

Macrocert files:

- `data/rules/rcm.gml:2` — `ruleID "rcm (...)"` shape that drives the
  prefix-match heuristic.
- `docs/mod_stereo_reference.md` §1.5, §5.2 — the audit establishing
  MØD's E/Z gap.
- `docs/workstream_d_predicates.md` §3 — user-facing reference for
  this predicate.

RDKit (no in-tree source; standard API):

- `rdkit.Chem.MolFromSmiles`, `rdkit.Chem.FindPotentialStereoBonds`,
  `rdkit.Chem.BondStereo`, `rdkit.Chem.BondType.DOUBLE`.
