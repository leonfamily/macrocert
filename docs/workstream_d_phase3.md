# Workstream D — Phase 3 Report

Adds the two predicates that discriminate `aryl_etherification` from
`biaryl_etherification` at strategy time. The two GML rules have
structurally identical bodies (`data/rules/aryl_etherification.gml`,
`data/rules/biaryl_etherification.gml`) because MØD's match operates on
element labels — sp²-aromatic vs sp³ context at atom 5 is invisible at
the GML level (`docs/macroetherification_research.md` §1.4,
`docs/biaryl_etherification_research.md` §1.2).

## Files modified

- `src/macrocert/spec/runspec.py` — extended `PredicateSpec` with two
  optional `dict[str, bool]` fields:
  `alcohol_partner_C_must_be_aromatic`,
  `alcohol_partner_C_must_be_sp3`. New `_parse_bool_map` helper rejects
  non-bool YAML values at load time. Both fields default to `None`,
  preserving v0 wiring for every existing RunSpec.
- `src/macrocert/generate/strategies.py` — matching optional fields on
  the strategy-layer `PredicateSpec` (and `is_empty()` updated). New
  factory `_alcohol_partner_aromaticity_factory(rule_to_bool, *, require_aromatic)`
  returns a rightPredicate that does the SMARTS substructure check.
  Both directions of the gate are produced by the same factory, keyed
  off `require_aromatic`. The factory is wired into
  `apply_rules_up_to_with_predicates` outside-in alongside the
  pre-existing EZ predicate.
- `src/macrocert/generate/build_dg.py` — forwards the two new fields
  through the spec→generate `PredicateSpec` translation as dict copies.
- `data/rules/aryl_etherification.meta.yaml`,
  `data/rules/biaryl_etherification.meta.yaml` — `notes:` sections now
  point RunSpec authors at the new predicates.
- `tests/spec/test_generate_predicates.py` — three required tests plus
  one extra YAML-roundtrip test; `test_empty_predicate_spec_is_empty`
  extended.
- `docs/workstream_d_predicates.md` — appended §4 documenting the
  predicates, the API path taken, and the validation results.

## API path taken: rightPredicate substructure match (fallback)

The task description's preferred path was a leftPredicate that walks the
L→substrate morph mapping to inspect the alcohol partner C *before* the
rule fires. **The MØD Python binding does not expose that mapping.**

- `external/mod/libs/pymod/src/mod/py/Derivation.cpp:8-39` binds the
  `Derivation` struct as `left: GraphList`, `rule: Rule`,
  `right: GraphList` only.
- `external/mod/libs/libmod/src/mod/Derivation.hpp:23-49` shows the C++
  struct itself is shape-identical: morph mappings live in
  `lib::DG::NonHyperBuilder` internals, not on `Derivation`.
- `external/mod/examples/py/020_dg/212_dgPredicate.py` consumes
  `derivation.right` (a list of `Graph`) and reads `g.numVertices` — no
  hint of a morph object.

So the implementation is the documented fallback: a *rightPredicate*
SMARTS substructure match on the product SMILES. The product carries
the freshly-formed Ar-O-X bond; RDKit can detect Ar-O-Ar vs Ar-O-C(sp³)
on the canonical product SMILES via `Graph.smiles`
(`external/mod/libs/libmod/src/mod/graph/Graph.hpp:118`).

Pre-compiled SMARTS:
- `require_aromatic=True`  → `c-O-c`     (Ar-O-Ar)
- `require_aromatic=False` → `c-O-[CX4]` (Ar-O-C(sp³))

`CX4` enforces four explicit connections on the alcohol-partner carbon,
which excludes aromatic carbons (those are `CX3` in RDKit's
atom-class accounting) and ensures sp³ hybridization.

### Trade-offs of the fallback

Positive filter on the product side: it requires the discriminator
SMARTS to be *present* in the product. For ether-closure rules this is
correct — the closure creates the bridge, so the bridge SMARTS appears
in the product iff the closure happened in the intended context. A
pathological substrate that already carries an Ar-O-C(sp³) bridge
before the rule fires would produce a false positive under
`alcohol_partner_C_must_be_sp3`, but panel substrates expose exactly
one new bridge per derivation; the existing `ring_size_equals`
predicate already disambiguates ring identity. If a future panel case
breaks the invariant, a substrate-pre-state diff is the principled fix
(and would have to wait on MØD upstream exposing the morph mapping or
the substrate left-graph through Python).

## Rule-name matching

Same convention as the EZ predicate. `derivation.rule.name` is the full
GML `ruleID` string (e.g.
`"biaryl_etherification (Ar-O-Ar SNAr ring closure, -HF)"` from
`data/rules/biaryl_etherification.gml:2`). The factory matches by exact
equality OR by `rule_id + " "` prefix. If the firing rule isn't in the
map (or its value is `False`), the predicate returns `True` — composes
safely with the `all_macrocyclization` rule-set's mixed contents.

## Tests

Counts (`pixi run --manifest-path ~/Code/ielm/macrocert/pixi.toml test`):

| stage                | tests collected | predicates file |
|----------------------|-----------------|-----------------|
| before phase 3       | 83              | 11              |
| after phase 3        | 87              | 15              |
| delta                | +4              | +4              |

Net result of the run after phase 3:

```
80 passed, 7 skipped in 3.20s
```

The 7 skips are the pre-existing placeholder-CIF panel cases; no
regression introduced.

Required tests delivered:

1. `test_alcohol_partner_aromatic_filters_biaryl_correctly` — direct
   unit test of `_alcohol_partner_aromaticity_factory({biaryl_etherification:
   True}, require_aromatic=True)`: accepts diphenyl ether
   (`c1ccc(Oc2ccccc2)cc1`), rejects phenetole (`c1ccc(OCC)cc1`),
   no-ops on unmapped rules.
2. `test_alcohol_partner_sp3_filters_aryl_correctly` — opposite gate:
   accepts phenetole, rejects diphenyl ether, no-ops on unmapped rules.
3. `test_discriminator_predicates_off_by_default` — `PredicateSpec()`
   leaves both fields `None`; the `toy_macrolactam` RunSpec parses to
   both `None`; end-to-end DG matches the v0 4-vertex / 2-edge
   baseline.

Extra test added (locks the schema):

4. `test_discriminator_predicates_parsed_from_yaml` — YAML round-trip
   for both fields under `strategy.predicates`.

`test_empty_predicate_spec_is_empty` extended to cover the two new
not-empty cases.

## Edge cases handled

- **Both fields can coexist** on one PredicateSpec — they wrap
  independent rightPredicates outside the inner `repeat` block, so the
  filter is conjunctive on the same candidate-derivation set.
- **`False` entries are explicit opt-outs.** The factory keeps only
  rule_ids whose bool flag is `True`; a `False` entry leaves the
  predicate a no-op for that rule (so a YAML author can document "this
  rule was considered" without enforcing).
- **Empty active set short-circuits.** When `rule_to_bool` is empty
  after filtering (every value `False`), the predicate returns `True`
  for every derivation. This matches the EZ predicate's behaviour with
  an empty map.
- **Mis-typed YAML fails loud.**
  `alcohol_partner_C_must_be_aromatic: {biaryl_etherification: "yes"}`
  raises `ValueError` at `load_runspec` rather than silently producing
  an always-False predicate.
- **`derivation.rule` vs `derivation.r`.** Same fallback as the EZ
  predicate — Python binding uses `rule`, C++ uses `r`; factory tries
  `rule` first, then `r`.
- **`Graph.smiles` returning None / unparsable.** The factory falls
  through invalid SMILES with `continue` so one bad product doesn't
  reject the whole derivation; only RDKit-parseable products contribute
  to the substructure match.

## Backward compatibility

Verified by `test_discriminator_predicates_off_by_default`:
`PredicateSpec()` has both new fields `None`, `is_empty()` still
returns `True`, and `apply_rules_up_to_with_predicates` short-circuits
to the unconditional inner `repeat` block. No existing RunSpec carries
the new fields, so existing pipelines see no behavioural change.

## Not changed (out of scope)

- No new `data/building_blocks/` aryl-fluoride blocks were authored
  (no end-to-end DG test with the actual ether rules was therefore
  added). The substructure-match predicates are exercised at the unit
  level with hand-crafted SMILES, which is the same test pattern the
  phase-2 EZ predicate uses for the same reason (MØD's stereo gap;
  here, MØD's missing morph-binding gap).
- No changes to `data/rules/_index.yaml`, the verifier, or the
  energetics modules.
- The two ether `.gml` rule bodies were not edited — the predicates
  live entirely in the strategy layer.
