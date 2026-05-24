# Workstream F α-C Stereo Overlays — Macrolactamization & Macrolactonization

Task #34: with the upstream MØD `MOD_ABORT` patch landed earlier this
session, runtime stereo enforcement (`LabelSettings(..., withStereo=true,
stereoRelation=Specialisation)`) is now reachable. This document records
the α-C stereo overlays added to `data/rules/macrolactamization.gml` and
`data/rules/macrolactonization.gml`, plus the one harness-default change
needed to keep the panel green under the new rule shape. All changes
unstaged.

## 1. Chemistry

Both rules fire the same acyl substitution at the carbonyl carbon:

    HO-C(=O)-CH(R)-... + H-X-...  →  X-C(=O)-CH(R)-... + H₂O

where `X = N` (lactam) or `X = O` (lactone). The α-carbon (the sp³ C
bonded to the carbonyl C) is untouched by the bond reorganisation —
classical retention. This is exactly the
`stereo_flags: retains_alpha_stereo` semantics declared in
`data/rules/macrolactamization.meta.yaml` and
`data/rules/macrolactonization.meta.yaml`, and confirmed by the
Workstream C briefs (`docs/macrolactonization_research.md` §4 and
`docs/macroetherification_research.md` §4).

The overlay declares the α-C as an sp³ tetrahedral stereocenter in
`context` with the **symmetric** (no brackets, no `!`) form, so the
rule matches either chirality on the substrate. Stereo on a `context`
vertex is shorthand for the same annotation on both `left` and `right`
(MØD DPO algebra: `L = left ∪ context`, `R = right ∪ context` — see
`docs/mod_stereo_reference.md` §2.1 / §5.6). Combined with retention,
this is the canonical "stereo preserved, not specified" pattern from
`docs/mod_stereo_reference.md` §4.1.

## 2. Encoded annotations (verbatim GML)

The α-carbon is given a fresh atom-map id `7` (the existing rule uses
ids `1–6` for the carbonyl C, the two carbonyl-region oxygens, the
acid hydroxyl H, the nucleophile heteroatom, and its H). MØD's
tetrahedral configuration requires the vertex to have degree 4 at
rule-load time (`external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp::finalizeVertex`),
so we expose the α-C's three remaining neighbours (`8`, `9`, `10`) as
wildcard atoms `label "*"`, single-bonded. This is the exact pattern
used by the canonical "Change" / "Generalize" rules in
`external/mod/examples/py/030_stereo/330_tartaric.py` and
`external/mod/test/py/papers/17_tetra_icgt/code/310_stereoDpo.py`
(cited in `docs/mod_stereo_reference.md` §1.6.2 and §1.6.3).

### 2.1 `macrolactamization.gml` (diff vs baseline)

Inserted into the `context` block:

```gml
context [
    node [ id 1 label "C" ]
    node [ id 5 label "N" ]
    # α-carbon (id 7): sp3 tetrahedral, symmetric (no brackets, no '!')
    # so the rule matches either chirality on the substrate. Acyl
    # substitution at C(1)=O does not touch the α-C, so identical
    # stereo on L and R — encoded as a single context annotation per
    # docs/mod_stereo_reference.md §2.1 / §5.6: L = left ∪ context and
    # R = right ∪ context, so stereo placed on context applies to both.
    # MØD requires the geometric vertex to have degree 4 at rule-load
    # time (Stereo/Inference.hpp::finalizeVertex), so we expose the
    # α-C's three additional neighbours (8, 9, 10) as wildcards. Same
    # pattern as the canonical Tartaric "Change" rule in
    # external/mod/examples/py/030_stereo/330_tartaric.py and
    # papers/17_tetra_icgt/code/310_stereoDpo.py (cited in
    # docs/mod_stereo_reference.md §1.6.2). retains_alpha_stereo per
    # meta.yaml — verified by Workstream C macroetherification /
    # macrolactonization research §4.
    node [ id 7 label "C" stereo "tetrahedral" ]
    node [ id 8 label "*" ]
    node [ id 9 label "*" ]
    node [ id 10 label "*" ]
    edge [ source 1 target 2 label "=" ]
    edge [ source 1 target 7 label "-" ]
    edge [ source 7 target 8 label "-" ]
    edge [ source 7 target 9 label "-" ]
    edge [ source 7 target 10 label "-" ]
]
```

### 2.2 `macrolactonization.gml` (diff vs baseline)

Same pattern; only the nucleophile heteroatom on id `5` differs (`O`
instead of `N`):

```gml
context [
    node [ id 1 label "C" ]
    node [ id 5 label "O" ]
    # α-carbon (id 7): sp3 tetrahedral, symmetric (no brackets, no '!')
    # so the rule matches either chirality on the substrate. Acyl
    # substitution at C(1)=O does not touch the α-C, so identical
    # stereo on L and R — encoded as a single context annotation per
    # docs/mod_stereo_reference.md §2.1 / §5.6: L = left ∪ context and
    # R = right ∪ context, so stereo placed on context applies to both.
    # MØD requires the geometric vertex to have degree 4 at rule-load
    # time (Stereo/Inference.hpp::finalizeVertex), so we expose the
    # α-C's three additional neighbours (8, 9, 10) as wildcards. Same
    # pattern as the canonical Tartaric "Change" rule in
    # external/mod/examples/py/030_stereo/330_tartaric.py (cited in
    # docs/mod_stereo_reference.md §1.6.2). retains_alpha_stereo per
    # meta.yaml — verified by Workstream C macrolactonization research §4.
    node [ id 7 label "C" stereo "tetrahedral" ]
    node [ id 8 label "*" ]
    node [ id 9 label "*" ]
    node [ id 10 label "*" ]
    edge [ source 1 target 2 label "=" ]
    edge [ source 1 target 7 label "-" ]
    edge [ source 7 target 8 label "-" ]
    edge [ source 7 target 9 label "-" ]
    edge [ source 7 target 10 label "-" ]
]
```

## 3. R/S → bracket interpretation

Per `docs/stereo_encoding_procedure.md`, MØD's bracket order is a
**local cyclic ordering of bonded neighbours up to even permutation**,
not a CIP descriptor. The α-C overlays here use the **symmetric** form
(geometry only, no brackets, no `!`): this is the "either chirality"
configuration — `TetrahedralSym` in MØD's `Configuration` hierarchy
(`external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp`).

The choice is deliberate, per the task brief and
`docs/mod_stereo_reference.md` §1.5 (Fixation):

- `stereo "tetrahedral"` → `TetrahedralSym` — a *pattern*: matches a
  vertex in either chirality.
- `stereo "tetrahedral[1,2,3,4]!"` → `TetrahedralFixed` — a *concrete
  configuration*: would pin a specific chirality, which is wrong here
  because:
  1. The rule must match both R- and S-configured substrates (the
     panel surrogates use ω-aminoacid α-CH₂, which is not even a
     stereocenter; the M5 target's α-C is a real stereocenter but the
     rule is generic to the chemistry, not target-specific).
  2. `retains_alpha_stereo` is a *conservation* statement (chirality
     preserved through the rule), not a *fixation* statement (chirality
     pinned to a specific value). The symmetric form on `context`
     encodes "same chirality on both sides" because L and R share the
     same vertex with the same neighbour ordering inherited from
     `context`.

The bracket-order interpretation only enters if a downstream rule
*creates* or *changes* α-C stereo (it doesn't), or if a *target*
substrate is annotated with a fixed bracket (CCDC 1515168 absolute
configuration for ascomylactam A). The target-side encoding is the
substrate's responsibility, not the rule's.

If/when target substrates start carrying `tetrahedral[a,b,c,d]!`
annotations on their α-C, the symmetric pattern here is the correct
generalisation: under `LabelRelation.Specialisation`, a free (`Sym`)
pattern matches both `Sym` and `Fixed` substrates
(`Tetrahedral.cpp::localPredSpec`, line 102: *"if we are free, it's
fine, otherwise the other must be fixed"*).

## 4. Regression handled — `LabelType.Term` is now the default

### 4.1 Symptom

After the initial overlay (3 wildcard atoms `label "*"` on the α-C),
all 10 panel cases that exercise macrolactamization / macrolactonization
(`lactam_*`, `lactone_*`) failed with `infeasible` witnesses. MØD's
`Result subset has 0 graphs` confirmed the rule LHS was no longer
matching the seco substrate.

### 4.2 Root cause

MØD's GML label semantics depend on `LabelType`:

- `LabelType.String` (the 2-arg `LabelSettings` default, used by
  macrocert before this change) treats `"*"` as a literal label —
  the substrate would need to carry an atom labeled literally `*`,
  which it doesn't.
- `LabelType.Term` (used by all three canonical stereo examples in
  `external/mod/examples/py/030_stereo/`) treats `"*"` as a
  first-order term variable that unifies with any constant label
  during graph matching.

The canonical Tartaric rule (`330_tartaric.py:11-22`) only works
under `LabelType.Term`; macrocert was running under `LabelType.String`
by default and silently failing to match.

### 4.3 Fix

Switched the default `LabelSettings` in
`src/macrocert/generate/build_dg.py` to
`LabelSettings(LabelType.Term, LabelRelation.Specialisation)` (off-path,
`withStereo=false`). The on-path (stereo_enforcement=true) was already
`LabelSettings(LabelType.Term, LabelRelation.Specialisation,
LabelRelation.Specialisation)` — unchanged. Element labels (`"C"`,
`"O"`, `"N"`) are constants in Term mode, so other rules (which use
only element labels) continue to match identically.

The companion test
`tests/spec/test_generate_toy.py::test_stereo_enforcement_constructs_labelsettings_for_dg`
was updated to assert that the off-path now passes a 2-arg
`LabelSettings` with `withStereo=false` (rather than omitting
`labelSettings` entirely).

## 5. Test outcomes

### 5.1 `pixi run python -m macrocert.cli check-rules data/rules`

Before *and* after the overlay:

```
12 rule(s) pass conservation re-check (stereo: 0 warning(s), 0 info(s))
```

The α-C is added to `context`, so it is a `[no change]` atom for the
conservation re-check (atoms balance on both sides). The new wildcard
neighbours (8, 9, 10) are also in `context`. No stereo warnings/infos
are emitted by `check_rule_stereo_conservation` because:

- the symmetric form (no brackets, no `!`) carries no L↔R bracket
  pair to check for parity (invariant 1, `odd_permutation_inversion`);
- the same `Sym` form on both effective L and R precludes a
  `fixation_transition` (invariant 2);
- there are no edge-level stereo strings (invariant 3);
- the geometry is `tetrahedral`, the only fully-enforced geometry
  (invariant 4 fires only for `linear` / `trigonalPlanar` /
  `squarePlanar` *fixed* annotations).

### 5.2 `pixi run pytest tests/panel/ -q`

Before edits:
```
13 passed, 4 skipped
```

After edits:
```
13 passed, 4 skipped
```

The 4 skipped cases are pre-existing placeholders awaiting Ivan's CIF
audit (`citreoviridin_suh_imda_1985`,
`haidle_myers_cytochalasin_b_2004`,
`phoenix_reddy_cassaine_tda_2008`,
`trost_bryostatin_analogue_rcm_2007`) — unrelated to this task.

### 5.3 `pixi run pytest tests/ -q`

```
131 passed, 4 skipped
```

(One existing test —
`tests/spec/test_generate_toy.py::test_stereo_enforcement_constructs_labelsettings_for_dg`
— was updated to reflect the new default-on-Term-mode behaviour;
see §4.3.)

### 5.4 M5 ascomylactam with `stereo_enforcement: true`

Added `strategy.stereo_enforcement: true` to
`data/targets/ascomylactam_a/runspec.yaml` and re-ran:

```
$ pixi run python -m macrocert.cli run data/targets/ascomylactam_a
ascomylactam_a: witness=optimal
  bond-level expelled mass:    20.01 g/mol
  process-level expelled mass: 1114.01 g/mol
  certificate: artifacts/ascomylactam_a/certificate.json
```

The optimal certificate is preserved. The chosen rule is
`aryl_etherification` (the Uchiro 2017 Ar-O-C(sp3) closure tactic per
the runspec notes) — which has no α-C in its rule body, so the new
overlays don't affect it. Sanity-checked by also running with
`stereo_enforcement: false`: same witness (`optimal`, objective ≈
20.006), same chosen rule (`aryl_etherification`). Stereo enforcement
exercises the new rule LHSs but does not change the M5 optimum.

## 6. Open follow-ups

1. **Extend to other rules?** Per `docs/mod_abort_investigation.md` §7,
   the rule library breaks down as:
   - `macrolactamization`, `macrolactonization` — done in this task.
   - `transannular_diels_alder` — **task #35**, 4 new sp³
     stereocenters, much more complex (endo/exo as sibling rules,
     not a single parameterised rule per `mod_stereo_reference.md`
     §4.3). Out of scope here.
   - `rcm` — would need `trigonalPlanar` E/Z annotations, but MØD's
     `TrigonalPlanar::morphismIso` is `MOD_ABORT`
     (`mod_stereo_reference.md` §5.2). Advisory only; needs verifier-
     side enforcement (`stereo_conservation.py`).
   - `biaryl_etherification` — axial atropisomerism, not point
     chirality; MØD has no registered configuration for it (§5.8).
     Out of scope.
   - `aryl_etherification`, `c_h_dehydrogenative_coupling`,
     `cross_coupling_*` — aromatic / sp² couplings, no α-C stereo
     to encode.

2. **Verifier certificate stereo conservation hook.** The harness's
   `check_rule_stereo_conservation` already covers the four invariants
   from `mod_stereo_reference.md` §3.1, but it is currently a
   *pre-flight* check on the rule library, not a *post-DG* check on
   the emitted certificate. Wiring it into `verifier/verify.py` so
   that certificates produced with `stereo_enforcement=true` carry
   stereo-conservation proofs is the next Workstream F task after
   #34/#35.

3. **Target-side α-C bracket annotation.** Today the substrate
   `.mol` files do not carry MØD `stereo` annotations on their α-C
   vertices. The CCDC 1515168 absolute configuration for ascomylactam
   A could be encoded as `tetrahedral[a,b,c,d]!` on each of its 12
   sp³ centers (per the procedure in
   `docs/stereo_encoding_procedure.md` §2). Under
   `LabelRelation.Specialisation`, our `Sym` rule pattern would still
   match such a substrate, and downstream verifiers could then
   *check* that the chosen route preserves the published
   configuration. Currently the runtime enforcement is structural-
   only (asserts the α-C is sp³ tetrahedral); chirality-faithful
   enforcement awaits target-side fixation.

## 7. Citation manifest

Every encoding decision in §2 / §3 / §4 references one of:

- `docs/mod_stereo_reference.md` §1.4 (neighbour-list semantics),
  §1.5 (fixation `!`), §1.6.2 (Tartaric "Change" pattern),
  §2.1 / §5.6 (context-stereo = stereo on both L and R), §4.1
  (sp³ retention through a transformation pattern).
- `docs/stereo_encoding_procedure.md` §3.1 (lactam α-carbon worked
  example).
- `external/mod/examples/py/030_stereo/330_tartaric.py:11-22` (the
  reference implementation of `node label "*"` wildcards + `stereo
  "tetrahedral"`).
- `external/mod/examples/py/030_stereo/320_aconitase.py:54-58`
  (canonical 3-arg `LabelSettings(LabelType.Term, ...)` usage).
- `external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp`
  (`finalizeVertex` — the degree-4 enforcement at rule load).
- `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp`
  (`Good`/`Bad` partition; `localPredSpec` semantics).
- `external/mod/libs/libmod/src/mod/Config.hpp:82-118`
  (`LabelSettings` overload set).
- `docs/macrolactonization_research.md` §4 and
  `docs/macroetherification_research.md` §4
  (`retains_alpha_stereo` chemistry rationale).
- `docs/mod_abort_investigation.md` §6 (the worked-example draft this
  task implements) and §7 (the per-rule cost table).
