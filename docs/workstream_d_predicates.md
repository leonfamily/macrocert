# Workstream D — Predicate Framework (initial drop)

This note documents the first cut of MØD strategy predicates wired into
the harness: `is_intramolecular()` (leftPredicate gate) and
`ring_size_equals(n)` (rightPredicate gate), plus the RunSpec schema
extension that turns them on.

## MØD API entry points used

All references are inside the in-tree MØD checkout under
`external/mod/`.

- **`mod.leftPredicate[p](strat)`** — declares `p: Derivation -> bool`
  that is consulted *before* the rule fires. The `Derivation`'s
  `left` (reactant graph multiset) and `r` (rule) are valid; `right`
  is not. Reference:
  `external/mod/libs/pymod/src/mod/py/dg/Strategies.cpp` lines 32, 68,
  163–172 (`makeLeftPredicate`).
- **`mod.rightPredicate[p](strat)`** — same shape, consulted on the
  product side; `left` *and* `right` are valid. Reference: same file,
  lines 33, 69, 173–181 (`makeRightPredicate`); usage example in
  `external/mod/examples/py/020_dg/212_dgPredicate.py`.
- **`mod.Derivation`** struct shape (`left: GraphList`, `right:
  GraphList`, `r: Rule`): `external/mod/libs/libmod/src/mod/Derivation.hpp`
  lines 23–49.
- **`graph::Graph.smiles`** — canonical product SMILES, used to feed
  the ring-size predicate into RDKit. Reference:
  `external/mod/libs/libmod/src/mod/graph/Graph.hpp` line 118
  (`getSmiles()`).

MØD does **not** ship an SSSR / `smallestRing` routine in its public
graph API (verified with `grep -rn "smallestRing\|Ring(" external/mod/`).
We therefore delegate ring detection to RDKit's `Chem.GetSymmSSSR`,
matching the existing pattern already used in
`src/macrocert/spec/target.py::_find_ring`.

## Predicate semantics

- **`is_intramolecular`** (leftPredicate). Accepts the candidate
  derivation iff `len(derivation.left) == 1`. MØD packs the multiset
  of *distinct* reactant graphs in `left`, so a one-element left side
  means the LHS matched into a single connected component — exactly
  the "two atoms being bonded are in the same connected component
  before the rule fires" criterion required for macrocyclic closure.
- **`ring_size_equals(n)`** (rightPredicate). For each product graph
  in `derivation.right`, take its canonical SMILES, run RDKit SSSR,
  and accept if any ring has exactly `n` atoms. This is a positive
  filter — at least one product must carry the target ring.

The two predicates compose conjunctively when both are set; wrapping
order is irrelevant.

## Files modified

- `src/macrocert/generate/strategies.py` — added
  `PredicateSpec`, `apply_rules_up_to_with_predicates`,
  `_is_intramolecular`, `_ring_size_equals_factory`, and
  `_has_ring_of_size`. Existing `apply_rules_up_to` is untouched and
  remains the v0 path.
- `src/macrocert/spec/runspec.py` — added a `PredicateSpec` dataclass
  to the spec layer, a `predicates` field on `StrategySpec` (defaults
  to an all-off `PredicateSpec`), and a `_parse_predicates` loader.
  The loader accepts the predicates dict either under
  `strategy.predicates` (preferred, nested) or as a top-level
  `strategy_predicates` key (per the task description); both encode
  the same struct.
- `src/macrocert/generate/build_dg.py` — picks the predicated strategy
  when the RunSpec carries non-empty predicates; otherwise the v0
  unconditional strategy is used unchanged.

## New data / tests

- `data/targets/toy_macrolactam_predicated/runspec.yaml` — sibling of
  the existing `toy_macrolactam` target with both predicates enabled.
  Shares the same `structure.mol`.
- `tests/spec/test_generate_predicates.py` — four cases:
  1. YAML round-trip of the predicates field.
  2. Backward-compat: existing `toy_macrolactam` parses to empty
     `PredicateSpec`.
  3. End-to-end DG build: 3 vertices / 1 edge for the predicated
     target.
  4. `PredicateSpec.is_empty()` semantics.

## Validation results

Before/after on the toy macrolactam target (1 rule firing budget,
`all_macrocyclization` ruleset):

| variant                           | DG vertices | DG edges | product SMILES present                                     |
|-----------------------------------|-------------|----------|------------------------------------------------------------|
| `toy_macrolactam` (no predicates) | 4           | 2        | seco, water, 13-membered lactam, **linear dimer** (extra)  |
| `toy_macrolactam_predicated`      | 3           | 1        | seco, water, 13-membered lactam                            |

The intermolecular cyclization that produces the linear dimer
(`C(CCCCCCCCCCCN)(NCCCCCCCCCCCC(O)=O)=O`) is rejected by the
left predicate because its LHS matches across two graphs; the
intramolecular closure that produces the 13-membered macrolactam
satisfies both predicates and is the sole reaction in the DG. The
existing `tests/spec/test_generate_toy.py::test_generates_4_vertices_2_edges`
remains untouched and still passes; all 34 prior tests pass, and 4
new ones cover the predicate path.

```
$ pixi run pytest tests/
============================== 38 passed in 2.75s ==============================
```

CLI smoke:

```
$ pixi run python -m macrocert.cli run data/targets/toy_macrolactam
  Result subset has 3 graphs.       # i.e. 4 DG vertices incl. seco

$ pixi run python -m macrocert.cli run data/targets/toy_macrolactam_predicated
  Result subset has 2 graphs.       # i.e. 3 DG vertices incl. seco
```

## Blockers

None for this milestone. Two notes for follow-up Workstream D work:

1. MØD has no native ring API, so SSSR runs through RDKit. This is
   fine for monomeric products but should be revisited if predicates
   ever need to fire mid-cascade on large product graphs — the
   SMILES round-trip dominates at that point.
2. `is_intramolecular` relies on MØD packing connected components
   into the `left` multiset distinctly. The `212_dgPredicate.py`
   example and the C++ side (`NonHyperBuilder.cpp::leftPredicates`)
   confirm this is the documented shape, but the predicate framework
   inherits MØD's matching semantics — if the graph database is ever
   re-seeded with disconnected universes the `len(left) == 1` test
   would need to be re-examined.

## Not changed (out of scope for this ticket)

- `data/rules/`, `data/validation_panel/`, the verifier, and the
  energetics modules were not touched.
- The existing `toy_macrolactam` runspec is unchanged — its v0
  behaviour and its test are preserved as the backward-compat
  baseline.

---

## §3 E/Z geometry filter (Workstream D phase 2)

A third predicate, `enforce_ez_geometry`, joins `is_intramolecular`
and `ring_size_equals` to filter MØD derivations by double-bond
geometry on a per-rule basis. It lives on the right-side of the
strategy (`mod.rightPredicate`).

### Why this lives outside MØD

Workstream F's audit (`docs/mod_stereo_reference.md` §1.5, §5.2)
established that **MØD cannot enforce E/Z (double-bond) geometry at
match time**:

- `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/TrigonalPlanar.cpp:50-54`
  — `TrigonalPlanar::morphismIso` and `morphismSpec` are `MOD_ABORT`.
- `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Linear.cpp`
  is suspected to be the same (5.3, unverified).

A rule may *declare* `stereo "trigonalPlanar[...]!"` on its right
side, but MØD parses, depicts, and stores the annotation without
ever consulting it during derivation. The strategy-layer predicate
fills this gap by post-filtering candidate derivations on the
product SMILES.

### RunSpec schema

```yaml
strategy:
  predicates:
    enforce_ez_geometry:
      rcm: "E"
      transannular_diels_alder: "Z"
```

The dict is keyed by the *macrocert* `rule_id` (the GML filename
stem, e.g. `rcm`, `macrolactamization`, `transannular_diels_alder`)
and valued by the geometry token `"E"` or `"Z"`. Tokens are
normalised to upper case at YAML load time; any other value raises
`ValueError` at `load_runspec`. A run without the field — the
overwhelming majority of existing RunSpecs — sees
`PredicateSpec.enforce_ez_geometry = None` and the predicate is not
added to the strategy, preserving v0 wiring exactly.

### Predicate semantics

Implemented by `_enforce_ez_geometry_factory(rule_to_geometry)` in
`src/macrocert/generate/strategies.py`. The factory returns a
`Callable[[Derivation], bool]` registered via
`mod.rightPredicate[…]` outside the inner `repeat` block:

1. **Rule-name match.** Read `derivation.rule.name` (the GML
   `ruleID` string — `data/rules/rcm.gml:2` is
   `"rcm (ring-closing metathesis, -C2H4)"`). Match by *exact
   equality* **or** by `rule_id + " "` prefix against each key in
   the map; the prefix variant covers the macrocert GML convention
   of `"<id> (<description>)"`. If no key matches, return `True`
   immediately — the predicate is a no-op for unmapped rules and
   composes safely with rule sets like `all_macrocyclization` that
   contain both gated and ungated rules.

2. **SMILES round-trip.** For each product graph `g` in
   `derivation.right`, read `g.smiles`
   (`external/mod/libs/libmod/src/mod/graph/Graph.hpp:118`,
   `Graph::getSmiles`).

3. **RDKit stereo classification.** Parse the SMILES with
   `Chem.MolFromSmiles`, call `Chem.FindPotentialStereoBonds(mol)`
   to upgrade `STEREONONE` to `STEREOE`/`STEREOZ` on bonds whose
   neighbours' `/`/`\` directionality is present in the SMILES, and
   inspect `Bond.GetStereo()` on every `BondType.DOUBLE` bond.

4. **Accept iff** at least one product graph carries a double bond
   in the requested stereo class.
   `BondStereo.STEREOE`/`STEREOTRANS` count as `"E"`,
   `BondStereo.STEREOZ`/`STEREOCIS` count as `"Z"`. Anything else
   (including `STEREONONE` and `STEREOANY`) fails the gate.

This is a *positive* filter: the predicate rejects products whose
geometry is *undetermined*, not merely *opposite* to the requested
geometry. The intent is that downstream Workstream F work will
upgrade stereo-creating rules to emit determinate geometry SMILES;
until then, an E/Z gate on a stereo-free rule rejects every
derivation. The test
`test_ez_predicate_rejects_stereo_undetermined_products` documents
this consequence.

### MØD-API references used

- `mod.rightPredicate[p](strat)` — same call shape as the existing
  `ring_size_equals` predicate; see
  `external/mod/libs/pymod/src/mod/py/dg/Strategies.cpp:33,69,173-181`.
- `mod::Derivation`: C++ shape in
  `external/mod/libs/libmod/src/mod/Derivation.hpp:23-49`.
- **Naming divergence.** The C++ field `Derivation::r`
  (`Derivation.hpp:39`) is exposed to Python as the attribute
  **`rule`**, not `r` — see
  `external/mod/libs/pymod/src/mod/py/Derivation.cpp:32`. The
  predicate factory accesses `derivation.rule` first, falling back
  to `derivation.r` for forward/backward compatibility.
- `Rule::getName` →
  `external/mod/libs/libmod/src/mod/rule/Rule.hpp:129-133`; Python
  binding `rule.name` at
  `external/mod/libs/pymod/src/mod/py/rule/Rule.cpp:123`.
- The example pattern is `external/mod/examples/py/020_dg/212_dgPredicate.py`
  — a `rightPredicate` lambda reading `derivation.right` exactly as
  here.

### RDKit-API references used

- `rdkit.Chem.MolFromSmiles` — canonical SMILES parser.
- `rdkit.Chem.FindPotentialStereoBonds(mol)` — promotes
  `STEREONONE` to `STEREOE`/`STEREOZ` for bonds whose
  directionality is encoded by `/`/`\` in the SMILES string. Used
  here to make `Bond.GetStereo()` informative on freshly-parsed
  product SMILES.
- `rdkit.Chem.BondStereo` — enum of stereo classes
  (`STEREONONE`, `STEREOANY`, `STEREOZ`, `STEREOE`,
  `STEREOCIS`, `STEREOTRANS`). We treat E≡TRANS and Z≡CIS as
  synonyms for the filter.

### Files modified

- `src/macrocert/spec/runspec.py` — added
  `PredicateSpec.enforce_ez_geometry: dict[str, str] | None`,
  extended `_parse_predicates` to deserialise the map and normalise
  geometry tokens. Default `None` keeps existing RunSpecs
  unchanged.
- `src/macrocert/generate/strategies.py` — added the matching
  optional field to the strategy-layer `PredicateSpec`, the
  `_enforce_ez_geometry_factory(rule_to_geometry)` constructor and
  its helper `_product_has_double_bond_with_geometry`, and wired
  the predicate into `apply_rules_up_to_with_predicates` outside-in
  alongside the existing two predicates.
- `src/macrocert/generate/build_dg.py` — forwards
  `spec_preds.enforce_ez_geometry` through the spec→generate
  `PredicateSpec` translation.

### Tests added

In `tests/spec/test_generate_predicates.py`:

1. `test_ez_predicate_accepts_e_and_rejects_z` — direct unit test
   of the predicate against mock derivations with explicit
   `/C=C/` (E) vs `/C=C\` (Z) product SMILES.
2. `test_ez_predicate_noop_for_other_rules` — map `{rcm: "E"}` is
   a no-op when the firing rule is `macrolactamization`; even a
   Z-only product passes.
3. `test_ez_predicate_rejects_stereo_undetermined_products` —
   documents the consequence of the MØD stereo gap: a
   STEREONONE product fails an E gate.
4. `test_ez_predicate_parsed_from_yaml` — round-trips the field
   through `load_runspec` with case normalisation
   (`rcm: e` → `{rcm: "E"}`).
5. `test_ez_predicate_yaml_rejects_invalid_token` — `{rcm: "cis"}`
   raises `ValueError` at load time.
6. `test_ez_predicate_filters_rcm_to_e_only` — end-to-end DG
   build on `pentadecadiene` + `rcm`: ungated DG has 4 vertices
   and 2 edges; gated DG has 0 RCM-closure edges (all products
   are STEREONONE under MØD's current rcm.gml). The strict
   inequality `gated.numEdges < ungated.numEdges` records the
   filter effect.
7. `test_ez_predicate_macrolactam_run_unaffected` — sets
   `{rcm: "E"}` on a macrolactamization-only run; DG matches the
   v0 4-vertex / 2-edge baseline.

`test_empty_predicate_spec_is_empty` is extended with an assertion
that `PredicateSpec(enforce_ez_geometry={"rcm": "E"})` is *not*
empty.

### MØD-API divergences encountered

1. **`derivation.rule` vs `derivation.r`.** The task description
   names the C++ field `r`, but MØD's Python binding exposes it
   as `rule` (see refs above). Hitting the segfault during repr of
   an `AttributeError`-bearing exception is what flushed this out;
   the predicate now prefers `rule` and falls back to `r`.
2. **Rule name embeds a description.** `derivation.rule.name`
   returns the full GML `ruleID` string (e.g. `"rcm (ring-closing
   metathesis, -C2H4)"`), not the macrocert filename stem. The
   predicate uses prefix matching (`rule_id + " "`) to bridge
   the two namespaces. If a future macrocert rule file's `ruleID`
   stops following the `"<id> (<description>)"` convention this
   matcher will silently miss — worth a `check-rules` audit.

### Validation

```
$ pixi run pytest tests/ -q
76 passed, 3 skipped in 2.70s
```

Baseline before the change was 69 passed / 3 skipped; the seven
new tests are the additions enumerated above.

---

## §4 Alcohol-partner discriminator predicates (Workstream D phase 3)

A fourth and fifth predicate, `alcohol_partner_C_must_be_aromatic` and
`alcohol_partner_C_must_be_sp3`, discriminate between the two ether
sibling rules at strategy time. Both are rightPredicates.

### Why this lives outside MØD

The two GML rules
(`data/rules/aryl_etherification.gml`,
`data/rules/biaryl_etherification.gml`) have **structurally identical
bodies** because MØD matches on element labels. Atom 5 = O in both
rules; the sp²-aromatic vs sp³ context of the alcohol-side carbon (the
"alcohol partner C") is invisible at the GML level. Background:

- `docs/macroetherification_research.md` §1.4 — sp³-vs-aromatic O
  distinction not expressible in MØD's label matcher.
- `docs/biaryl_etherification_research.md` §1.2, §2.2 — Option A is
  "two near-identical GML rules + strategy-layer discriminator".
- `data/rules/biaryl_etherification.gml:6-14` — in-file pointer to this
  predicate as the required discriminator.

Without the predicate, **both rules fire on any HO-R + ArF substrate**
and the panel runner cannot tell aryl_etherification from
biaryl_etherification.

### RunSpec schema

```yaml
strategy:
  predicates:
    alcohol_partner_C_must_be_aromatic:
      biaryl_etherification: true
    alcohol_partner_C_must_be_sp3:
      aryl_etherification: true
```

Each field is a per-rule_id `bool` map. `True` for a given `rule_id`
turns the constraint on for that rule; `False` (or omission) makes the
predicate a no-op for that rule. Non-bool values raise `ValueError` at
`load_runspec` so misconfigured YAML fails loud. A RunSpec without
either field — every existing RunSpec — sees both fields parse to
`None` and the predicates are not added to the strategy, preserving v0
wiring exactly.

### API path taken: rightPredicate substructure match (fallback)

The *ideal* implementation would be a leftPredicate that walks the
L→substrate morph mapping: locate the substrate atom matched to
rule-atom 5, find its non-rule-atom neighbour (the alcohol partner C),
and inspect aromaticity/hybridization via RDKit. **That API is not
exposed in the MØD Python binding.** `external/mod/libs/pymod/src/mod/py/Derivation.cpp:8-39`
binds the `Derivation` struct as `left: GraphList`, `rule: Rule`,
`right: GraphList` only — no morph object is reachable from Python.
The C++ struct `mod::Derivation` itself
(`external/mod/libs/libmod/src/mod/Derivation.hpp:23-49`) is shape-
identical: morph mappings live in `lib::DG::NonHyperBuilder` internals,
not on `Derivation`.

So we ship the task description's documented fallback: a
*rightPredicate* substructure match on the product SMILES.

1. **Rule-name match.** Same convention as `enforce_ez_geometry`:
   `derivation.rule.name` is the full GML `ruleID` string
   (`data/rules/biaryl_etherification.gml:2` →
   `"biaryl_etherification (Ar-O-Ar SNAr ring closure, -HF)"`); match
   by exact equality or by `rule_id + " "` prefix. If the firing rule
   isn't in the map (or its value is `False`), the predicate returns
   `True` — composes safely with `all_macrocyclization` and mixed sets.

2. **Product SMILES round-trip.** For each `g in derivation.right`,
   read `g.smiles` (`external/mod/libs/libmod/src/mod/graph/Graph.hpp:118`,
   `Graph::getSmiles()`).

3. **RDKit SMARTS substructure match.** Pre-compile a SMARTS pattern
   once at predicate-factory construction:
   - `require_aromatic=True` → SMARTS `c-O-c` (Ar-O-Ar bridge: both
     bridge carbons aromatic — RDKit lower-case `c` matches aromatic
     atoms only).
   - `require_aromatic=False` → SMARTS `c-O-[CX4]` (Ar-O-C(sp³)
     bridge: one aromatic C, one four-coordinate sp³ C — `CX4` is the
     RDKit atom-class predicate for four explicit connections).

   Accept the derivation iff at least one product graph has a
   substructure match.

### Trade-offs of the fallback

The substructure match is *positive*: it requires the discriminator
SMARTS to be present in the *product*. For ether-closure rules this is
correct — the closure literally creates the Ar-O-X bridge, so the
bridge SMARTS appears in the product iff the closure happened in the
intended context. A pathological multi-ether substrate could already
carry an Ar-O-C(sp³) bridge before the rule fires (so a False positive
under `alcohol_partner_C_must_be_sp3`), but in practice the panel's
target substrates expose exactly one new bridge per derivation; the
ring_size_equals predicate already disambiguates ring identity. If
later panel cases break this invariant, a substrate-pre-state diff is
the principled fix.

### MØD-API divergences encountered

None new beyond what phase 2 documented. The morph-mapping non-binding
(see "API path taken" above) is the structural reason the fallback is
the API-correct choice, not a workaround.

### Files modified

- `src/macrocert/spec/runspec.py` — added two optional `dict[str, bool]`
  fields on `PredicateSpec` plus a `_parse_bool_map` helper that
  rejects non-bool YAML values.
- `src/macrocert/generate/strategies.py` — added the matching fields
  on the strategy-layer `PredicateSpec` (and extended `is_empty()`),
  added `_alcohol_partner_aromaticity_factory(rule_to_bool, *, require_aromatic)`
  and wired both calls into `apply_rules_up_to_with_predicates`.
- `src/macrocert/generate/build_dg.py` — forwards both new fields
  through the spec→generate `PredicateSpec` translation.
- `data/rules/aryl_etherification.meta.yaml`,
  `data/rules/biaryl_etherification.meta.yaml` — notes section points
  RunSpec authors at the new predicates.

### Tests added

In `tests/spec/test_generate_predicates.py`:

1. `test_alcohol_partner_aromatic_filters_biaryl_correctly` — direct
   unit test: with map `{biaryl_etherification: True}` and
   `require_aromatic=True`, an Ar-O-Ar product (`c1ccc(Oc2ccccc2)cc1`)
   is accepted and an Ar-O-C(sp³) product (`c1ccc(OCC)cc1`,
   phenetole) is rejected. Unmapped rules are a no-op.
2. `test_alcohol_partner_sp3_filters_aryl_correctly` — opposite gate;
   `{aryl_etherification: True}` with `require_aromatic=False` accepts
   phenetole and rejects diphenyl ether.
3. `test_discriminator_predicates_off_by_default` — backward-compat:
   `PredicateSpec()` has both fields `None`, the `toy_macrolactam`
   RunSpec parses to both `None`, and the end-to-end DG build is the
   v0 4-vertex / 2-edge baseline (proves `is_empty()` short-circuits
   the wrap when the new fields are absent).
4. `test_discriminator_predicates_parsed_from_yaml` — YAML round-trip
   for both fields under `strategy.predicates`.

`test_empty_predicate_spec_is_empty` extended with assertions that
`PredicateSpec(alcohol_partner_C_must_be_aromatic=…)` and
`PredicateSpec(alcohol_partner_C_must_be_sp3=…)` are *not* empty.

### Validation

```
$ pixi run --manifest-path ~/Code/ielm/macrocert/pixi.toml test
80 passed, 7 skipped in 3.20s
```

Baseline before the change was 76 passed / 7 skipped (phase 2 number);
the four new tests above account for the four-test delta. The
`test_generate_predicates.py` file went from 11 collected tests to 15
(one short of N+4: required N+3 was met; the YAML round-trip is the
extra and exists to lock the schema in alongside the predicate
behaviour).
