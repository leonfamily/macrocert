# Upstream PR draft — jakobandersen/mod

Draft for the PR to upstream once Ivan has a GitHub fork (suggested:
`ielm/mod` or `iv4nh4t3s/mod`). Submit against the `develop` branch.

---

## Title

`Stereo: copy LonePair virtual edges in "copy unmatched from R1" branch`

## Body

The `RC::Visitor::Stereo::handleBoth` visitor's "second-to-first
subgraph" case at `libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:388-422`
walks unmatched virtual edges from R1's stereo embedding into the
result. The LonePair / Radical branch at lines 404-407 hits
`MOD_ABORT` unconditionally, but the same file's `copyAllFromSide`
lambda at lines 94-101 already handles LonePair correctly:

```cpp
case lib::Stereo::EmbeddingEdge::Type::LonePair:
    // offsets should be corrected somewhere else
    data.edges.emplace_back(-1, lib::Stereo::EmbeddingEdge::Type::LonePair, emb.cat);
    break;
```

Mirroring that pattern here unblocks any substrate carrying an amine N
at degree 3+:

1. `Stereo::Inference::finalize` runs on every substrate `Graph` when
   `LabelSettings.withStereo=true`.
2. For the N in `Graph.fromSMILES("CCN")`, the entry
   `V(N, 0, false, 3, 0, 0, 0, 1, tetrahedral)` at
   `Stereo/GeometryGraph.cpp:132` matches and assigns 1 lone pair.
3. `Inference.hpp:276` calls `addLonePairs(v, 1)`, appending a
   `Type::LonePair` virtual edge to the N's stereo embedding.
4. The DG `Rule` strategy at `Rule.cpp:166-172` wraps the substrate as
   a one-sided rule, composing it with the user rule via `RC::Super`
   on every rule application -- not only under explicit
   `rcParallel` / `rcSub`.
5. The visitor reaches the LonePair branch on the N's embedding entry
   at line 404 and aborts.

The Radical case keeps its `MOD_ABORT` TODO comment but now carries
the symmetric dead-code `emplace_back` below it, matching the pattern
in `copyAllFromSide` at lines 99-101.

## Reproducer (fails on `develop` at `c13e570`, passes with this patch)

```python
import mod

mod.config.io.useLabelSettings = True
ls = mod.LabelSettings(mod.LabelType.Term,
                       mod.LabelRelation.Specialisation,
                       mod.LabelRelation.Specialisation)

# Minimal amine-N substrate
g = mod.Graph.fromSMILES("CCN")

# Any rule whose LHS matches the N - macrolactamization works
rule = mod.Rule.fromGMLString("""
rule [
    ruleID "test"
    left  [ node [ id 5 label "N" ] node [ id 6 label "H" ]
            edge [ source 5 target 6 label "-" ] ]
    context [ node [ id 1 label "C" ] ]
    right [ node [ id 5 label "N" ] node [ id 6 label "H" ]
            edge [ source 1 target 5 label "-" ]
            edge [ source 1 target 6 label "-" ] ]
]
""")

dg = mod.DG(graphDatabase=[g], labelSettings=ls)
b = dg.build()
b.execute(mod.addSubset(g) >> mod.repeat[1]([rule]))
print("dg built; numVertices =", dg.numVertices)
```

Output without patch: `MOD_ABORT` at `Stereo.hpp:406`.
Output with patch: `dg built; numVertices = N`.

## Test plan

- [ ] All existing `examples/py/030_stereo/` examples still run
- [ ] The reproducer above completes without abort
- [ ] No regressions in MØD's test suite (`make test`)

## Provenance

Bug surfaced by an external user (MØD-MacroCert,
constraint-certified macrocyclization design via DPO graph rewriting).
The user's investigation (linked in our project docs) empirically
reproduced the abort across 9 hypothesis-testing scripts and isolated
the chain of causation through `Stereo/Inference.hpp`, `Rule.cpp`, and
the `RC::Super` composition pipeline.

cc @jakobandersen
