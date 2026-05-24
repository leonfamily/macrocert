# MØD `MOD_ABORT` Root-Cause Investigation

Author: Workstream F investigator
Date: 2026-05-24
Status: complete; recommendation calls for an upstream MØD patch (not a rule-authoring change)

## Executive summary

The `Stereo.hpp:406` abort previously attributed to "stereo-free rules under
`Repeat`/`Parallel`" is **substrate-driven, not rule-driven**. It fires whenever
all three of the following hold:

1. `LabelSettings.withStereo == true` (the 3-arg `LabelSettings` form, i.e.
   stereo enforcement is on);
2. The DG strategy invokes the `Rule` strategy on a graph (every `addSubset
   >> repeat[…](rule)` does this); and
3. The substrate molecule (or any other graph in the universe that the
   rule's left-component-1 binds to) contains a *trivalent neutral
   nitrogen* (or any other atom whose `chemValids` entry in
   `GeometryGraph.cpp` carries `lonePair > 0`).

There is **no rule-authoring discipline that avoids the abort.** The
lone-pair virtual edges that trip the abort are deduced by MØD from the
substrate's atom labels via the `chemValids` table during `Graph` stereo
inference; the user has no GML-level control over them. Even annotating
every node of the rule with `stereo "any"` does not help (verified
empirically; see §2.3).

The fix is a four-line MØD source patch that closes the `MOD_ABORT; //
TODO` at `RC/Visitor/Stereo.hpp:404-406` by mirroring the already-correct
handling of the same `EmbeddingEdge::Type::LonePair` case in the
`copyAllFromSide` lambda at lines 94-97 of the same file.

For Workstream F the practical answer is:

- **Short-term:** keep `stereo_enforcement = false` (default off, already
  wired in `build_dg.py:76-81`). All 12 rules continue to work.
- **Medium-term:** apply the four-line MØD patch in §5 to enable runtime
  stereo enforcement. After the patch, the *existing* `data/rules/*.gml`
  files remain valid (no rule edits required for the abort fix; the rules
  still need stereo annotations added before they enforce anything, but
  that is a separate task addressed by `docs/stereo_encoding_procedure.md`).
- **Cost (re-authoring for stereo enforcement):** 6 of the 12 rules need
  per-vertex `tetrahedral[...]!` annotation overlays to actually enforce
  chirality; 4 are stereo-irrelevant aromatic-ring couplings; 2 (RCM and
  trans-annular Diels-Alder) carry the additional caveat that MØD does not
  enforce `trigonalPlanar` configurations even after the patch (the
  `morphismIso`/`morphismSpec` methods are `MOD_ABORT` for that geometry
  — `Stereo/Configuration/TrigonalPlanar.cpp:50-54`, already noted in
  `mod_stereo_reference.md` §5.2).

## 1. What the MØD `030_stereo/` examples do (extracted verbatim)

The three examples are at
`external/mod/examples/py/030_stereo/{320_aconitase,330_tartaric,340_tree}.py`.

### 1.1 Annotation pattern

None of the three examples annotates *every* atom with stereo. The
pattern is:

- The **rule** carries stereo only on the chirality-creating vertex on
  its `right` side (the new sp³ center). Aconitase's rule annotates two
  vertices on `R` (`node [ id 1 stereo "tetrahedral[1000, 1001, 202, 2]!" ]`
  and `node [ id 2 stereo "tetrahedral[200, 1, 2000, 2001]!" ]`); tartaric and
  tree annotate one vertex on `L` with `stereo "tetrahedral"` (the
  free/Sym form — pattern matches any chirality) and the same vertex on
  `R` with `stereo "tetrahedral[1, 2, 3, 4]!"` (the fixed form). All
  other vertices have no stereo string.
- **All hydroxyl / water oxygens carry NO stereo annotation.** The
  aconitase rule has six O atoms (IDs 100, 200, 1010) and not one of them
  has a `stereo "..."` attribute. The same is true of `330_tartaric.py`
  (`*`-labelled context nodes only) and `340_tree.py`.
- **All three examples use the 3-arg `LabelSettings`:**
  `LabelSettings(LabelType.Term, LabelRelation.Specialisation, LabelRelation.Specialisation)`
  (aconitase line 54-58; tartaric line 27-30; tree line 24-27).

### 1.2 Atom inventory of the official substrates

The examples are deliberately constructed from carbon-oxygen-hydrogen
substrates plus, in `340_tree.py`, sulfur and phosphorus. Crucially:

| Substrate                                                | Atoms      |
| -------------------------------------------------------- | ---------- |
| `Cit` = `C(C(=O)O)C(CC(=O)O)(C(=O)O)O`                    | C, O, H   |
| `D-ICit` = `C([C@@H]([C@H](C(=O)O)O)C(=O)O)C(=O)O`        | C, O, H   |
| `H_2O` = `O`                                              | O, H      |
| `Tartaric acid` and its stereoisomers                    | C, O, H   |
| `340_tree`'s `N[C@](O)([C@](S)(P)(O))([C@](S)(P)(O))`     | C, N, O, P, S, H |

The only example with N is `340_tree`, and it uses N at **degree 1**
(only one bond, to a stereo C). N at degree 1 has no entry in
`GeometryGraph.cpp`'s `chemValids` table, so MØD's stereo inference
returns the `any` geometry with `0` lone pairs (see
`Stereo/GeometryGraph.cpp:296-303`: when no viable entry is found,
`deduceGeometryAndLonePairs` returns `Res{any, 0}` after emitting a
warning, **not** an error). That is why the example runs.

Similarly, the P and S in `340_tree` have no `chemValids` entries for
degree 3 / degree 1 either (the few P entry at line 139 is `P, 0, false,
3, 1, ...`, which requires one double bond — not the case for the
phosphine in `340_tree`).

So **MØD's official stereo examples never feed the geometry inference an
atom that produces a non-zero lone-pair count.** This is the
load-bearing observation.

### 1.3 The warnings are benign

When I ran `aconitase`, `tartaric`, and `tree` under
`pixi`'s mod CLI, each emitted the exact warning that
`workstream_f_harness.md` flagged on macrolactamization
("`WARNING: No viable geometries for O with bonds D = 1.`"). Each then
completed the DG build successfully:

```
$ /…/pixi/envs/default/bin/mod --nopost -f external/mod/examples/py/030_stereo/320_aconitase.py
WARNING: No viable geometries for O with bonds D = 1.
WARNING: No viable geometries for O with bonds S = 2.
…
End of code from '…/320_aconitase.py'

$ … mod --nopost -f external/mod/examples/py/030_stereo/330_tartaric.py
… same warnings …
Repeat, limit = 2147483647
  Round 1: Result subset has 2 graphs.
  Round 2: Result subset has 0 graphs.
End of code from '…/330_tartaric.py'

$ … mod --nopost -f external/mod/examples/py/030_stereo/340_tree.py
… same warnings + 'No viable geometries for S/P …' …
End of code from '…/340_tree.py'
```

The "No viable geometries for O / S / P" warnings come from
`GeometryGraph.cpp:296-302`. They are emitted from
`deduceGeometryAndLonePairs` when an exact `chemValids` match cannot be
found, immediately before the function returns `Res{any, 0}` as a
fallback. They do **not** propagate as errors. The handler-level message
emitted by `macrocert` (cited in `workstream_f_harness.md`) is the same
warning, and it is equally harmless on its own.

## 2. Empirical results

All tests run under `/Users/…/Code/ielm/macrocert/.pixi/envs/default/bin/mod --nopost -f <script>`
from `/tmp/macrocert_stereo_test/` (scratch only; no files in `data/rules/`
were modified).

### 2.1 Reproduction: macrolactamization + acid/amine substrate + `withStereo=true`

Script: `/tmp/macrocert_stereo_test/test_macrolactam_stereo.py`. Loads
the live `data/rules/macrolactamization.gml`, creates two substrates
(`CCC(=O)O`, `CCN`), builds a DG under the 3-arg `LabelSettings`. Result:

```
MØD FatalError: Aborting from operator()
    /…/RC/Visitor/Stereo.hpp:406
```

Stacktrace (cleaned, top-to-bottom):

```
…/DG/Strategies/Sequence::executeImpl
  …/DG/Strategies/Repeat::executeImpl
    …/DG/Strategies/Rule::executeImpl                        ← Rule.cpp:166
      …/RC/composeFromMatchMaker
        …/RC/composeFromMatchMakerImpl<Super>
          …/RC/detail/handleMapToTerm
            …/RC/detail/handleMapToStereo
              …/RC/composeLabelled
                …/RC/compose
                  …/RC/detail/CompositionHelper::operator()
                    …/RC/Visitor/Stereo::finalize           ← Stereo.hpp:406
```

The DG `Rule` strategy uses `RC::Super` composition under the hood to
fire the rule against each substrate graph (`Rule.cpp:166-172`,
`const lib::rule::Rule &rFirst = graphAsRuleCache.getBindRule(g)->getRule();
… lib::RC::composeFromMatchMaker(rFirst, rSecond, mm, reporter, …);`).
Every rule application therefore runs `RC::Visitor::Stereo` when
`withStereo==true`. The prior agent's "`Repeat`/`Parallel`" attribution
was correct in symptom (those strategies are above the abort in the
stack) but misleading in cause: the abort happens **per rule
application**, not per composition of two user rules.

### 2.2 The minimum reproducer is a single trivial rule + ammonia

Script: `/tmp/macrocert_stereo_test/test_ammonia.py`. A degree-1
H-shuffle rule fired against the substrate `Graph.fromSMILES("N")`
aborts at the same line. So the abort has nothing to do with
macrolactamization specifically; it is triggered by any N-containing
substrate.

### 2.3 Annotating every rule node with `stereo "any"` does NOT help

Script: `/tmp/macrocert_stereo_test/test_explicit_any.py`. Same rule
body as `macrolactamization.gml`, with `stereo "any"` added to every
single `left`, `context`, and `right` node. Same substrates as 2.1.
Result: identical abort at `Stereo.hpp:406`. Hypothesis (a) from the
task brief is disproved.

### 2.4 Removing explicit H atoms from the rule does NOT help

Script: `/tmp/macrocert_stereo_test/test_no_explicit_h.py`. A rule that
merely creates a C-N bond with no H references at all, fired against
the same acid/amine substrates. Same abort. Hypothesis (b) is disproved.

### 2.5 Substrate WITHOUT N (methane) does NOT abort

Script: `/tmp/macrocert_stereo_test/test_no_N_substrate_with_macrolactam.py`.
Loads the live `macrolactamization.gml` rule, fires it against `methane`
under `withStereo=true`. No abort: the DG builds (rule cannot match,
zero new vertices, but the build completes cleanly). The same rule, the
same `LabelSettings`, with a substrate that does not contain any
nitrogen — clean. This isolates the trigger to the **substrate atom
table**, not the rule.

### 2.6 `LabelRelation.Isomorphism` for the stereo relation does NOT help

Script: `/tmp/macrocert_stereo_test/test_iso_relation.py`. With
`LabelSettings(Term, Specialisation, Isomorphism)` the abort moves to a
*different* line (`RC/MatchMaker/LabelledMatch.hpp:79`) but still
aborts. Worse.

### 2.7 `LabelType.String` does NOT help

Script: `/tmp/macrocert_stereo_test/test_string_label.py`. Same abort at
`Stereo.hpp:406`.

### 2.8 The 4-arg `LabelSettings(…, withStereo=False, …)` form WORKS

Script: `/tmp/macrocert_stereo_test/test_4arg_falsestereo.py`. This is
just the existing default-off path; the test confirms that the existing
non-stereo regime is unchanged when reached via the 4-arg form.

## 3. Root cause (confirmed)

Hypothesis (d) from the task brief is correct, with one refinement: the
abort is not at a single `LabelSettings` config — it is intrinsic to the
combination of `withStereo=true` and any substrate atom whose
`chemValids` entry assigns a non-zero lone-pair count.

The chain of events is:

1. `Graph.fromSMILES("CCN")` constructs an internal `lib::graph::Graph`
   whose stereo property is computed by
   `lib::Stereo::Inference::finalize`
   (`Stereo/Inference.hpp:114-169`). For the N vertex (degree 3, all
   single bonds), `finalizeVertex` falls through to the "no explicit
   geometry, no explicit embedding" branch
   (`Inference.hpp:271-275`), which calls
   `GeometryGraph::deduceGeometryAndLonePairs`. The `chemValids` entry
   `V(N, 0, false, 3, 0, 0, 0, 1, tetrahedral)` (`GeometryGraph.cpp:132`)
   matches exactly: geometry `tetrahedral`, lone-pair count `1`.

2. Back in `finalizeVertex`, line 276 calls
   `addLonePairs(v, numLonePairs=1)`, which appends one
   `EmbeddingEdge` of `Type::LonePair` to the N vertex's stereo
   embedding (`Inference.hpp:189-196`). The substrate now carries one
   virtual lone-pair edge on its N.

3. When the DG `Rule` strategy executes (`DG/Strategies/Rule.cpp:166`),
   it wraps the substrate as a rule via
   `graphAsRuleCache.getBindRule(g)` (a `Bind` rule has the substrate's
   atoms only on its `right` side; see
   `Rule/GraphAsRuleCache.cpp:11`) and composes it with the macrocert
   rule using `RC::Super` (Rule.cpp:168-172).

4. The composition routine ultimately calls
   `RC::Visitor::Stereo::finalize`
   (`RC/Visitor/Stereo.hpp:70-…`). For every vertex in the result that
   is shared between R1 (the substrate's R, i.e., the substrate itself)
   and R2 (the rule's R), the `handleBoth` lambda fires
   (`Stereo.hpp:184-…`). For the case "substrate-R is a subgraph of
   rule-L's image in the result and the rule's stereo changes" (i.e.,
   `secondInContext == false`, `secondToFirstSubgraph == true`,
   `firstToSecondSubgraph == false` for atoms in the substrate that the
   rule does not touch), MØD enters the "copy unmatched from R1" branch
   at `Stereo.hpp:388-422`.

5. That branch iterates the substrate vertex's embedding
   (`Stereo.hpp:402: for(const auto &emb: conf)`) and switches on
   `emb.type`. The `Edge` case is handled correctly. The `LonePair` and
   `Radical` cases are both fatal:

   ```cpp
   case lib::Stereo::EmbeddingEdge::Type::LonePair:
   case lib::Stereo::EmbeddingEdge::Type::Radical:
       MOD_ABORT;
       break;
   ```

   (`Stereo.hpp:404-407`)

6. The N's lone-pair virtual edge from step 2 hits this switch and
   aborts.

The relevant `chemValids` entries that carry `lonePair > 0` are
(`GeometryGraph.cpp:113-145`):

- `V(N, 0, false, 1, 1, 0, 0, 1, trigonalPlanar)` — N with 1 single + 1 double bond, 1 lone pair
- `V(N, 0, false, 0, 0, 0, 2, 1, trigonalPlanar)` — N with 2 aromatic bonds, 1 lone pair
- `V(N, 0, false, 3, 0, 0, 0, 1, tetrahedral)` — **R₃N (the amine case, hits every amine substrate)**
- `V(P, 0, false, 3, 1, 0, 0, 0, tetrahedral)` — P with 3 single + 1 double, 0 lone pairs (OK, no trigger)

Oxygen has **zero** entries in `chemValids` (lines 135-137 are all
commented out), so degree-1 and degree-2 oxygens always fall back to
`any` geometry with `0` lone pairs. That is why the "No viable
geometries for O" warning is benign: the warning is emitted but no
lone-pair virtual edge is added. (The hydroxyl/water O atoms in
`macrolactamization.gml` are not the cause of the abort.)

The aconitase rule (`320_aconitase.py`) does not abort because **none of
its substrates contain N, P, or S in a chemValids-matching
configuration**. The same is true of tartaric and tree. The MØD authors
appear to have deliberately constructed examples that avoid the
unimplemented lone-pair copy path.

## 4. Proposed rule-authoring discipline

There is none for the abort itself.

A defensible rule-authoring discipline for stereo *correctness* (after
the abort is fixed by §5) is:

- Annotate each created or preserved sp³ stereocenter on the rule's
  `right` side with `tetrahedral[…]!` and a neighbour list that is a
  local cyclic ordering (per `mod_stereo_reference.md` §1.4). For
  preservation rules (sp³ retained from L to R), put the identical
  bracket list on `left` and `right`, or in `context` for the
  shorthand.
- Do not annotate aromatic carbons, sp² carbons, oxygens, or hydrogens.
  MØD's `trigonalPlanar` morphism methods are `MOD_ABORT`
  (`TrigonalPlanar.cpp:50-54`); annotating sp² carbons can therefore
  introduce a *different* abort once the rule fires against a substrate
  whose corresponding atom also carries a trigonal-planar
  configuration.
- Leave nitrogens unannotated. Substrate-derived N's will still carry
  one lone-pair virtual edge after the §5 patch, but the patched copy
  code preserves the lone pair through composition (mirroring the
  already-correct lambda at `Stereo.hpp:94-97`); the rule does not need
  to declare it.
- Do not annotate edges. MØD parses edge `stereo` strings but never
  consumes them (`mod_stereo_reference.md` §5.1, confirmed in source).

## 5. The minimal MØD source patch (the actual fix)

File: `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp`,
lines 401-407 (the "copy unmatched from R1" branch).

Current code:

```cpp
const auto &conf = *get_stereo(glSide)[vInput];
for(const auto &emb: conf) {
    switch(emb.type) {
    case lib::Stereo::EmbeddingEdge::Type::LonePair:
    case lib::Stereo::EmbeddingEdge::Type::Radical:
        MOD_ABORT;
        break;
    case lib::Stereo::EmbeddingEdge::Type::Edge:
        … (correct handling) …
```

Patched code (mirrors the already-working pattern in the
`copyAllFromSide` lambda at the top of the same file, lines 92-102):

```cpp
const auto &conf = *get_stereo(glSide)[vInput];
auto &data = vDataRight[get(boost::vertex_index_t(), gResult, vResult)];
for(const auto &emb: conf) {
    switch(emb.type) {
    case lib::Stereo::EmbeddingEdge::Type::LonePair:
        // offsets corrected during finalization (matches Stereo.hpp:94-97)
        data.edges.emplace_back(-1, lib::Stereo::EmbeddingEdge::Type::LonePair, emb.cat);
        break;
    case lib::Stereo::EmbeddingEdge::Type::Radical:
        // TODO: radical handling is not exercised by macrocert; mirror LonePair
        // to be safe, or keep MOD_ABORT here if you want a louder failure.
        data.edges.emplace_back(-1, lib::Stereo::EmbeddingEdge::Type::Radical, emb.cat);
        break;
    case lib::Stereo::EmbeddingEdge::Type::Edge:
        … (unchanged) …
```

Rationale: the `copyAllFromSide` lambda at `Stereo.hpp:80-151` is the
"easy" case where the input rule's R is being copied wholesale; it
already handles `LonePair` correctly by emplacing a virtual-offset
embedding entry that gets corrected downstream. The "copy unmatched
from R1" branch at line 388 needs to do the same thing for the *subset*
of R1's vertices that aren't covered by R2 — there is no semantic
reason that these particular vertices should be treated differently.
Both branches feed `vDataRight` (the result-side embedding data); both
get the same "offsets corrected during finalization" treatment. The
`MOD_ABORT; // TODO` comment at line 99 in the working branch is a
hint that the MØD authors themselves recognised the gap and never
filled it for the symmetric branch.

There is an analogous gap for the "copy unmatched from L1" branch
elsewhere in `Stereo.hpp` (not yet hit empirically — would surface only
if the rule destroys stereo on a multi-component left side). I have not
patched that here.

After applying this patch, rebuild MØD:

```
cd external/mod
mkdir -p build && cd build
cmake .. -DBUILD_PY_MOD=on
make -j8
# then re-link pixi env or copy build/lib/libmod.* into .pixi/envs/default/lib/
```

## 6. Worked example — `macrolactamization.gml` after the patch

No edits to the rule are required by the patch itself. The existing
content already satisfies the "minimal annotation" stance described in
§4. For Workstream F's *eventual* runtime enforcement of α-carbon
chirality during ring closure, the rule would be augmented per
`mod_stereo_reference.md` §4.1, but that is independent of the abort fix
and was not in scope here.

A draft annotation overlay (do not commit; for reference only):

```gml
rule [
    ruleID "macrolactamization (amide ring closure, -H2O) — α-C stereo retained"
    # … add the α-carbon (call it id 10) and its three other neighbours
    # (id 11, 12, 13) to context if they are not already there …
    left [
        node [ id 2 label "O" ]
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 3 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 5 target 6 label "-" ]
        # Retain α-carbon chirality: identical bracket list on L and R.
        node [ id 10 stereo "tetrahedral[1, 11, 12, 13]!" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 5 label "N" ]
        node [ id 10 label "C" ]   # α-carbon
        node [ id 11 label "C" ]
        node [ id 12 label "H" ]
        node [ id 13 label "C" ]
        edge [ source 1 target 2 label "=" ]
        edge [ source 1 target 10 label "-" ]
        edge [ source 10 target 11 label "-" ]
        edge [ source 10 target 12 label "-" ]
        edge [ source 10 target 13 label "-" ]
    ]
    right [
        node [ id 2 label "O" ]
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 3 target 6 label "-" ]
        node [ id 10 stereo "tetrahedral[1, 11, 12, 13]!" ]
    ]
]
```

The actual neighbour IDs and cyclic ordering should be determined per
target by the procedure in `docs/stereo_encoding_procedure.md` §2.

## 7. Cost estimate — re-authoring rules for stereo enforcement

This is the cost *after* the §5 patch is in place. It is independent of
the abort fix itself.

| Rule                                  | Stereo relevance              | Annotation cost                                                       |
| ------------------------------------- | ----------------------------- | --------------------------------------------------------------------- |
| `macrolactamization.gml`              | α-C retention                 | Low: add 4 nodes (10, 11, 12, 13) and 4 edges to `context`; 2 stereo annotations on `left`/`right`. ~10 lines. |
| `macrolactonization.gml`              | α-C retention (mirrors above) | Low: same shape as macrolactamization. ~10 lines.                     |
| `transannular_diels_alder.gml`        | **Four new sp³ centers**      | High: 4 `tetrahedral[…]!` annotations on `right`; endo/exo *not* parameterisable in a single rule (`mod_stereo_reference.md` §4.3 recommends sibling rules). Estimate: 2× ~20 lines = 40 lines. |
| `rcm.gml`                             | New sp² (E/Z) — unenforced    | Caveat-only: `trigonalPlanar` morphism is `MOD_ABORT` so MØD will not enforce E/Z. Either omit (E/Z mixture, current behaviour) or use the macrocert stereo-conservation verifier (`stereo_conservation.py`) for advisory enforcement. ~0 GML lines; ~30 lines of post-DG verifier logic. |
| `aryl_etherification.gml`             | None (aromatic Sp² coupling)  | Zero.                                                                 |
| `biaryl_etherification.gml`           | Possible atropisomerism       | Caveat: atropisomerism is configurational, not point-chirality. MØD's tetrahedral configuration cannot encode it directly. Out of scope for the abort fix; needs separate research. |
| `c_h_dehydrogenative_coupling.gml`    | None (aromatic)               | Zero.                                                                 |
| `cross_coupling_buchwald.gml`         | None (sp²-N coupling)         | Zero.                                                                 |
| `cross_coupling_negishi.gml`          | Possible sp³-sp³ retention    | Medium: depends on substrate. For the M5 target, Negishi is used on an sp² center → zero. |
| `cross_coupling_sonogashira.gml`      | None (sp-sp² coupling)        | Zero.                                                                 |
| `cross_coupling_stille.gml`           | None (sp²-sp² coupling)       | Zero.                                                                 |
| `cross_coupling_suzuki.gml`           | None (sp²-sp² coupling)       | Zero.                                                                 |

**Summary:** 2 rules (`macrolactamization`, `macrolactonization`) need
~10-line overlays each. 1 rule (`transannular_diels_alder`) needs ~40
lines and probably an endo/exo split. 2 rules (`rcm`,
`biaryl_etherification`) hit MØD limitations (`trigonalPlanar` morphism
abort; atropisomerism not modellable) and require advisory verifier
logic instead. The remaining 7 rules need no edits.

For Workstream M5 specifically (ascomylactam A — 12 sp³ stereocenters +
atropisomerism), the critical rules are `macrolactamization` (1
α-center) and `transannular_diels_alder` (potentially 4 new sp³
centers if it appears in the synthetic plan; needs confirmation from
the M5 retrosynthesis). The remaining 11 sp³ centers are *substrate*
stereo — they enter the DG via the building-block SMILES and need no
rule annotations as long as they are not touched by any reactive site
in any fired rule.

## 8. Open questions

1. **Does the §5 patch interact badly with `RC::Visitor::Stereo`'s
   `handleBoth` "merge virtuals" branch (Stereo.hpp:222-226)?** That
   branch is also a `MOD_ABORT`, hit only if both R1 and R2 carry
   virtual edges on the matched vertex. For macrocert today, R2 (the
   rule's R) carries no lone pairs because no rule annotates N's
   explicitly, so this branch is unreachable. If a future rule
   annotates an N with an explicit lone pair (which would only be
   necessary for some specialty nitrogen geometries), the merge branch
   would need a separate patch.

2. **Are there other `MOD_ABORT` calls in the RC stereo pipeline that
   the §5 patch makes reachable?** I have grepped for all
   `MOD_ABORT`'s in `RC/Visitor/Stereo.hpp`: lines 99 (Radical in
   `copyAllFromSide`, unreached today), 143 (partial-fixation
   fallback), 225 (virtual-merge), 272/275/297/299/302/351 (various
   non-subgraph fallbacks in `handleBoth`), 406/407 (this fix), 766
   (Radical in printing). Of these, 99, 143, 766 are routinely
   unreachable for current macrocert rules; the `handleBoth` aborts at
   272-351 are hit only if a rule produces a *non-subgraph* of the
   substrate, which RC's match generator avoids by construction for
   simple cases. We should plan an additional empirical pass once §5
   is in: build the full panel under `withStereo=true` and grep the
   stack for any `RC/Visitor/Stereo.hpp` line number that is not 406.

3. **Should we vendor a patched `libmod` or maintain a `.patch` file?**
   The MØD vendored tree is committed under `external/mod/`. If we patch
   in place, the change will be visible in `git diff` but lost if we
   re-vendor. A `patches/mod_rc_stereo_lonepair.patch` plus a
   `pixi run vendor-mod` hook is the cleaner long-term shape, but
   in-place patch with a clear comment in
   `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp` is
   acceptable for M5 timelines. **This is an Ivan decision.**

4. **Upstream PR?** The patch is small, the diagnosis is clean, and the
   fix mirrors the already-working pattern in the same file. Opening a
   PR against `jakobandersen/mod` would benefit the wider MØD
   community. **This is also an Ivan decision** — out of M5 critical
   path either way.

## Appendix A: source files cited

| Path                                                                                  | Role                                                |
| ------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:94-102`                   | Working `LonePair` copy in `copyAllFromSide`        |
| `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:401-422`                  | Broken `LonePair` handling in "copy unmatched from R1" |
| `external/mod/libs/libmod/src/mod/lib/RC/RuleComposition.hpp:18`                      | `composeRules` entry point                          |
| `external/mod/libs/libmod/src/mod/lib/DG/Strategies/Rule.cpp:166-172`                 | DG `Rule` strategy invokes `RC::Super`              |
| `external/mod/libs/libmod/src/mod/lib/Rule/GraphAsRuleCache.cpp:11`                   | Substrate is wrapped as a `Bind` rule (R-only)      |
| `external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp:103-146`               | `chemValids` table — N entries are the trigger      |
| `external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp:262-303`               | `deduceGeometryAndLonePairs` — falls back to `any`  |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp:189-196`                   | `addLonePairs` adds the virtual edges               |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp:271-276`                   | `finalizeVertex` calls `addLonePairs` automatically |
| `external/mod/libs/libmod/src/mod/Config.hpp:82-118`                                  | `LabelSettings` constructors                        |
| `external/mod/examples/py/030_stereo/{320,330,340}*.py`                               | Working stereo examples (no N-degree-3 substrates)  |

## Appendix B: scratch test scripts

All under `/tmp/macrocert_stereo_test/`:

- `test_macrolactam_stereo.py` — full reproducer (aborts).
- `test_no_n_substrate.py` — methane + trivial C-H rule (OK).
- `test_ammonia.py` — minimal reproducer (aborts on `Graph.fromSMILES("N")`).
- `test_explicit_any.py` — `stereo "any"` on every node (still aborts).
- `test_no_explicit_h.py` — rule without explicit H atoms (still aborts).
- `test_no_N_substrate_with_macrolactam.py` — live rule + methane only (OK).
- `test_iso_relation.py` — `LabelRelation.Isomorphism` for stereo (different abort).
- `test_string_label.py` — `LabelType.String` (still aborts).
- `test_4arg_falsestereo.py` — 4-arg `withStereo=False` (OK, default-off path).
