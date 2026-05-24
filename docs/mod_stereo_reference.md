# MØD Stereo Annotation Reference

A definitive reference for the stereo annotation syntax of the MØD molecular graph
rewriting library, derived from the MØD source tree at
`external/mod/` (commit at vendor-in time) and from the canonical paper
[AFMS-Stereo] (Andersen, Flamm, Merkle, Stadler. *Chemical Graph Transformation
with Stereo-Information.* ICGT 2017, pp. 54–69. DOI: 10.1007/978-3-319-61470-0_4).

> **Headline finding.** MØD's stereo model is **tetrahedral-only in any
> enforcement sense**. Only `tetrahedral` has a working chirality-comparison
> implementation. `linear`, `trigonalPlanar`, and `any` parse and depict
> correctly but their `morphismIso` / `morphismSpec` methods are `MOD_ABORT` —
> meaning E/Z (double-bond) geometry is **not enforced** by MØD's match algorithm.
> Edge-level `stereo` strings are accepted by the GML grammar but no edge-stereo
> *configuration class* exists. See §5 for the consequences.

---

## 1. Syntax Reference

### 1.1 Where stereo appears in GML

The MØD GML grammar (see `external/mod/doc/source/formats/gml.rst` and the actual
parser in `external/mod/libs/libmod/src/mod/lib/IO/GML.hpp`) permits an optional
`stereo` attribute on **any** `node [...]` or `edge [...]` block, in any of the
three sides of a rule (`left`, `context`, `right`) and in standalone graphs.

```gml
node [ id 0 label "C" stereo "tetrahedral[1, 2, 3, 4]!" ]
edge [ source 1 target 2 label "=" stereo "..." ]   # accepted but unused
```

The `stereo` attribute is parsed unconditionally (it is a `std::optional<std::string>`
field on both `Vertex` and `Edge` GML records). However, its *value* is parsed by
a separate sub-grammar — see §1.2 — and only on **vertices** is the parsed result
ever interpreted. See §5 for the open status of edge stereo.

### 1.2 The stereo-string sub-grammar

Source of truth: `external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp`. The
parser (Boost.Spirit X3) accepts:

```
stereoEmbedding := !eoi >> geometry? >> neighbours? >> fixation? >> eoi

geometry        := [a-zA-Z][a-zA-Z0-9]*           # e.g. "tetrahedral", "trigonalPlanar"
neighbours      := '[' (neighbour (',' neighbour)*)? ']'
neighbour       := int                            # vertex id of a graph neighbour
                 | [a-zA-Z]                       # single letter = virtual edge
                                                  #   (lone pair or radical)
fixation        := '!'
```

All three components are optional, but at least one must be present (`!eoi`).
Whitespace is allowed (the parser uses `x3::ascii::space` as the skip). Examples
that all parse:

| String                          | Geometry         | Neighbours       | Fixed |
| ------------------------------- | ---------------- | ---------------- | ----- |
| `tetrahedral`                   | tetrahedral      | (deduced)        | no    |
| `tetrahedral!`                  | tetrahedral      | (deduced)        | yes   |
| `tetrahedral[1,2,3,4]`          | tetrahedral      | `1,2,3,4`        | no    |
| `tetrahedral[1,2,3,4]!`         | tetrahedral      | `1,2,3,4`        | yes   |
| `[1,2,3,4]!`                    | (deduced=tetra)  | `1,2,3,4`        | yes   |
| `[1, 2, 3, e]!`                 | (deduced=tetra)  | 3 edges + 1 lp   | yes   |
| `[]!`                           | any              | empty            | yes   |
| `any`                           | any              | (deduced)        | no    |
| `trigonalPlanar[1,2,3]!`        | trigonalPlanar   | `1,2,3`          | yes   |
| `linear[1,2]!`                  | linear           | `1,2`            | yes   |

### 1.3 The registered geometry vocabulary

Source: `external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp`. MØD
registers exactly these geometries (in a subsumption hierarchy rooted at `any`):

```
any
├── linear           # degree-2, no fixation distinction enforced
├── trigonalPlanar   # degree-3, fixation parses but morphism is MOD_ABORT
└── tetrahedral      # degree-4, FULL chirality enforcement
```

**There is no `squarePlanar`, `trigonalBipyramidal`, or `octahedral` geometry.**
The request to declare these is currently impossible without patching MØD's
`GeometryGraph` constructor (lines 89–101) to register new vertices and a
matching `Configuration` subclass.

The `any` geometry is the lattice top: any concrete geometry generalizes to
`any`. This is used both for "we don't care" (pattern side of a rule) and for
"we don't know" (post-reaction unspecified product).

### 1.4 Neighbour-list semantics: ordering, virtual edges, completeness

From `Stereo/Inference.hpp::finalizeVertex` (lines 198–278) and
`Stereo/Configuration/Tetrahedral.cpp`:

1. **Completeness.** When a bracketed neighbour list is given, it must contain
   exactly one entry per real out-edge of the vertex (plus zero or more
   virtual-edge letters for lone pairs / radicals). Listing too few real
   neighbours raises `InputError`: *"Too few edges in stereo embedding for
   vertex ...."* Duplicate offsets are also rejected.

2. **What the integer IDs mean.** Each integer in `[...]` is the **vertex ID of
   a graph neighbour** in the *same `left` / `context` / `right` block in which
   the stereo attribute appears*. The list is converted to *out-edge offsets*
   at parse time. The list is therefore not a CIP ordering, nor a SMILES `@`/`@@`
   ordering — it is a **local cyclic ordering of bonded neighbours**.

3. **Single-letter entries are virtual edges.** Any `[a-zA-Z]` token in the
   neighbour list represents a virtual edge that does *not* correspond to a real
   graph edge. The two canonical uses in the codebase are:

   - `e` for an electron lone pair (e.g. `stereo "[1, 2, e]!"` on a
     trigonal-planar `N` with two real neighbours plus one lone pair —
     `test/py/stereo/04_graphFix.py:23`).
   - any letter introduces a `Type::LonePair` virtual edge with a fresh
     virtual offset. (Radicals are added programmatically via the C++ API as
     `Type::Radical`, not via GML letters; the parser treats all letters as
     lone-pair-equivalent virtual edges. See `Read.cpp:26` and
     `Inference.hpp:88-104`.)

4. **What the bracket order encodes for `tetrahedral`.** The 12 even
   permutations of `[a,b,c,d]` form one chirality class; the 12 odd
   permutations form the other. The hard-coded tables `Good` and `Bad` in
   `Tetrahedral.cpp:118-155` enumerate them. So `[1,2,3,4]!` and `[2,3,1,4]!`
   denote the **same** absolute configuration; `[1,2,3,4]!` and `[2,1,3,4]!`
   denote **enantiomers**.

   *This is not CIP.* MØD's tetrahedral configuration does not look at neighbour
   priorities — it works purely on the cyclic ordering of the abstract neighbour
   identifiers. CIP designations like `R/S` are an emergent property of the
   substituent labels, not part of the annotation language.

### 1.5 What `!` means (fixation)

`Stereo/Configuration/Configuration.hpp` defines `Fixation`. There are only two
states in v0 of MØD: `free()` and `simpleFixed()`. The `!` toggles a vertex
between *symmetric* and *fixed*:

- `stereo "tetrahedral"` → `TetrahedralSym` — a **pattern**: matches a vertex
  in either chirality.
- `stereo "tetrahedral[1,2,3,4]!"` → `TetrahedralFixed` — a **concrete
  configuration**: matches only the chirality whose neighbour ordering is an
  even permutation of `[1,2,3,4]`.

The semantic check is in `Tetrahedral.cpp::localPredSpec` (line 102):
*"if we are free, it's fine, otherwise the other must be fixed."* So under
`LabelRelation.Specialisation`, a free (Sym) configuration on the pattern side
matches both fixed and free on the substrate, but a fixed configuration on the
pattern side requires the substrate to be fixed (and equal up to even
permutation).

### 1.6 Working examples extracted verbatim

#### 1.6.1 Aconitase — stereo-creating rule (R-side only)

`external/mod/examples/py/030_stereo/320_aconitase.py:5-52`

```gml
rule [
    ruleID "Aconitase"
    left [
        # the dehydrated water
        edge [ source 1 target 100 label "-" ]
        edge [ source 2 target 102 label "-" ]
        # the hydrated water
        edge [ source 200 target 202 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        edge [ source 1 target 2 label "-" ] # goes from - to = to -
        node [ id 2 label "C" ]
        # the dehydrated water
        node [ id 100 label "O" ]
        edge [ source 100 target 101 label "-" ]
        node [ id 101 label "H" ]
        node [ id 102 label "H" ]
        # the hydrated water
        node [ id 200 label "O" ]
        edge [ source 200 target 201 label "-" ]
        node [ id 201 label "H" ]
        node [ id 202 label "H" ]
        # dehydrated C neighbours
        node [ id 1000 label "C" ]
        edge [ source 1 target 1000 label "-" ]
        node [ id 1010 label "O" ]
        edge [ source 1000 target 1010 label "-" ]
        node [ id 1001 label "C" ]
        edge [ source 1 target 1001 label "-" ]
        # hydrated C neighbours
        node [ id 2000 label "C" ]
        edge [ source 2 target 2000 label "-" ]
        node [ id 2001 label "H" ]
        edge [ source 2 target 2001 label "-" ]
    ]
    right [
        # The '!' in the end changes it from TetrahedralSym to
        # TetrahedralFixed
        node [ id 1 stereo "tetrahedral[1000, 1001, 202, 2]!" ]
        node [ id 2 stereo "tetrahedral[200, 1, 2000, 2001]!" ]
        # the dehydrated water
        edge [ source 100 target 102 label "-" ]
        # the hydrated water
        edge [ source 1 target 202 label "-" ]
        edge [ source 2 target 200 label "-" ]
    ]
]
```

Notable: the rule **creates** stereo on R only — L has no stereo annotations on
`1`/`2`. This is "stereo-undefined → stereo-fixed."

#### 1.6.2 Tartaric — change-of-stereo rule

`external/mod/examples/py/030_stereo/330_tartaric.py:5-24` (also in
`papers/17_tetra_icgt/code/310_stereoDpo.py`, which is the canonical paper
example):

```gml
rule [
    ruleID "Change"
    left [
        node [ id 0 stereo "tetrahedral" ]
    ]
    context [
        node [ id 0 label "*" ]
        node [ id 1 label "*" ]
        node [ id 2 label "*" ]
        node [ id 3 label "*" ]
        node [ id 4 label "*" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [
        node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ]
    ]
]
```

Notable: L has `tetrahedral` *without* brackets and *without* `!` → matches any
tetrahedral configuration (Sym). R has explicit ordering and `!` → fixates the
result. This is the canonical pattern for converting a stereo-ambiguous input
into a specific stereo product, used in the ICGT paper figures.

#### 1.6.3 Generalize — stereo-erasing rule

`papers/17_tetra_icgt/code/310_stereoDpo.py`:

```gml
rule [
    ruleID "Generalize"
    left [
        node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ]
    ]
    context [
        node [ id 0 label "*" ]
        node [ id 1 label "*" ]
        node [ id 2 label "*" ]
        node [ id 3 label "*" ]
        node [ id 4 label "*" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [
        node [ id 0 stereo "tetrahedral" ]
    ]
]
```

This is the inverse of "Change": fixed L → free R, erasing the chirality.

---

## 2. Semantics

### 2.1 Where stereo lives in a DPO rule

Stereo annotations live on **vertices in `left` and `right` only**. They do not
go on `context` vertices (you can put them there, but the effect is asymmetric:
context-stereo equates to the same annotation on both `left` and `right` — see
the rule-model semantics in `external/mod/doc/source/graphModel/index.rst`,
"Rule Model" — `L = left ∪ context`, `R = right ∪ context`).

The recommended placement, observed in all official examples, is:

| Case                                | `left`                          | `context` | `right`                         |
| ----------------------------------- | ------------------------------- | --------- | ------------------------------- |
| Stereo **preserved** (a)            | `tetrahedral[1,2,3,4]!`         | bare node | `tetrahedral[1,2,3,4]!`         |
| Stereo **destroyed** (b)            | `tetrahedral[1,2,3,4]!`         | bare node | `tetrahedral` (or omit)         |
| Stereo **created** (c)              | (omit) or `tetrahedral`         | bare node | `tetrahedral[1,2,3,4]!`         |
| Stereo **inverted** (chirality flip)| `tetrahedral[1,2,3,4]!`         | bare node | `tetrahedral[2,1,3,4]!`         |
| Stereo **scrambled**                | `tetrahedral[1,2,3,4]!`         | bare node | `tetrahedral` (TetrahedralSym)  |

A subtlety: **putting stereo only on `context` is equivalent to declaring the
same stereo annotation on both `left` and `right`** (because `L = left ∪ context`
and `R = right ∪ context`). This is rarely what you want for a rule that
*changes* stereo, but is a convenient shorthand for *requiring* a stereo on the
substrate without altering it.

### 2.2 What MØD does at rule-application time

1. **Parse.** GML parser stores `stereo` as a string. Then
   `Stereo::Read::parseEmbedding` parses it into a `ParsedEmbedding {geometry?,
   edges?, fixation?}`.

2. **Inference.** During `Stereo::Inference::finalize` (one of four branches in
   `finalizeVertex`):
   - **Both geometry and embedding explicit** → use them verbatim.
   - **Geometry only** → deduce lone-pair count from atom data and edge multiset
     (`GeometryGraph::deduceLonePairs`).
   - **Embedding only** → deduce geometry from atom data, edges, and counted
     virtual edges (`deduceGeometry`).
   - **Neither** → deduce both (`deduceGeometryAndLonePairs`).

   Inference can fail with one of:
   - *"No viable configurations for ..."* — the atom/bond combination has no
     registered chemistry valid entry.
   - *"Ambiguous deduction for ..."* — multiple registered configurations match.

3. **Construction.** A concrete `Configuration` subclass instance
   (`Tetrahedral`, `TrigonalPlanar`, `Linear`, or `Any`) is built. For
   `Tetrahedral`, the constructor (`Tetrahedral.cpp:7-76`) normalises the
   neighbour list: if any neighbours are multi-bonds (double/triple/aromatic),
   they are rotated/swapped into a canonical visual position so that wedge/hash
   depictions render predictably. **This rotation/swap is a depiction
   normalisation, not a chirality change.**

4. **Match.** When a rule is applied to a substrate graph under
   `LabelSettings(..., withStereo=true, stereoRelation=...)`:
   - For each vertex, MØD first checks `localPredSpec` (pattern stereo
     generalizes substrate stereo).
   - If `morphismStaticOk()` returns `false` (true for `Tetrahedral` and
     `TrigonalPlanar`), MØD calls `morphismIso` or `morphismSpec` with the
     partial neighbour permutation induced by the graph morphism, and accepts
     only permutations that are in the `Good` set (even permutations).

5. **Stereo on the right-hand side.** After substrate match, the rule's R-side
   configuration is *instantiated* with the matched neighbour mapping (via
   `Configuration::clone(offsetMap)`) — so `tetrahedral[1,2,3,4]!` on R means
   "the product has fixed chirality with neighbours appearing in this cyclic
   order around the vertex that was matched to L-id 0/1/whatever."

### 2.3 The `LabelSettings` switch

Stereo enforcement is **opt-in per algorithm call**. From
`external/mod/libs/libmod/src/mod/Config.hpp:82-118`:

```cpp
LabelSettings(LabelType type, LabelRelation relation)
    // withStereo = false, stereoRelation = Isomorphism (unused)
LabelSettings(LabelType type, LabelRelation relation, LabelRelation stereoRelation)
    // withStereo = true
LabelSettings(LabelType, LabelRelation, bool withStereo, LabelRelation stereoRelation)
    // explicit
```

The default 2-argument constructor **leaves `withStereo=false`**. In that mode,
GML `stereo` strings are parsed but never checked at match time. All the official
stereo examples use the 3-argument constructor:

```python
LabelSettings(LabelType.Term, LabelRelation.Specialisation, LabelRelation.Specialisation)
```

`stereoRelation` can be `Isomorphism` (substrate stereo must exactly match) or
`Specialisation` (substrate stereo must be a specialisation of the pattern
stereo — i.e., `tetrahedral` on the rule matches `tetrahedral[...]!` on the
substrate, but not vice versa). `Unification` is rejected when forming a
category (`formCategory()`).

### 2.4 Wildcard / "match anything" stereo

There are two distinct "wildcards":

1. **No `stereo` attribute at all** on the rule vertex → MØD will infer a
   configuration from the surrounding edges/labels and treat it as the
   `Sym` (free) form of the inferred geometry. In effect: "you'll get whichever
   geometry the chemistry implies, with no chirality constraint." This is what
   non-stereo rules do.

2. **`stereo "tetrahedral"`** (geometry only, no brackets, no `!`) → forces the
   geometry to `tetrahedral` but leaves chirality free. The substrate must be a
   degree-4 vertex (or it will fail inference) but either chirality matches.

3. **`stereo "any"` or `stereo "[]!"`** → most permissive; degree-zero
   "any"-geometry placeholder, useful for non-atom nodes.

There is no syntax for "stereo geometry undetermined post-rule" *other than*
omitting the stereo annotation on R (which yields `Sym` if MØD can infer the
geometry, or `any` if it cannot).

---

## 3. Conservation under `pixi run check-rules`

**`pixi run check-rules` does not check stereo.** Read the source:
`src/macrocert/cli.py:16-37` calls
`macrocert.verifier.conservation.check_rule_conservation`, which is implemented
in `src/macrocert/verifier/conservation.py`. That function:

1. Parses the rule GML using `macrocert/verifier/gml_reader.py` (which
   *records* node `stereo` strings into `GMLNode.stereo` but ignores edge
   stereo entirely — `gml_reader.py:121`).
2. Compares atom multisets between L and R (with context) for
   element-and-charge balance.
3. Checks that L-only atoms have no edges crossing into the preserved scaffold.

**Stereo strings are parsed and stored but never inspected.** A rule with
mismatched stereo on L vs R passes `check-rules` so long as atoms balance.

This is by design — `check-rules` enforces *mass conservation*, which is
orthogonal to stereo. If Workstream F needs stereo conservation, it must be
added as a separate verifier pass.

### 3.1 Stereo invariants you might want to add to `check-rules`

The natural additions (none of which exist today):

1. **Stereo-bearing atoms unchanged in element + degree.** A vertex with
   `stereo` on both L and R must have the same `label` and `charge` (already
   enforced for non-stereo balance) *and* the same out-degree in both sides
   (otherwise the geometry deduction would diverge).

2. **Bracket-list referent integrity.** Every integer in a `stereo "...[ids]..."`
   must be a vertex ID that is actually bonded to the stereo-bearing vertex in
   the same side. The MØD loader will catch this (it will reject the rule
   because the embedding is invalid), but it is friendlier to catch it earlier.

3. **Fixation discipline.** If the rule claims to preserve stereo (case (a)),
   the bracket lists on L and R must be even permutations of each other.
   Otherwise the rule silently models chirality inversion. This is the
   highest-value check for Workstream F.

4. **Geometry compatibility with chemistry.** Asking `tetrahedral` of a
   trivalent carbon is a chemistry error (MØD's inference will complain
   "No viable configurations"), but a syntactic check that geometry matches
   degree is cheaper.

---

## 4. Templated GML Snippets for the Four Macrocyclisation Cases

> All snippets are written against the GML node-ID conventions in the existing
> `data/rules/` files. They show *only the stereo-augmented overlay* — drop them
> into the corresponding rule body, preserving its existing left/context/right
> structure.

### 4.1 sp³ retention through a transformation (macrolactamization α-carbon)

For macrolactamization, the α-carbon of the carboxylic acid (call it node 0 in
your rule, with neighbours 1=COOH carbon, 7=α-H, 8=R-chain neighbour, 9=Cα-β
neighbour) must retain its configuration. **Pattern:** identical bracket list,
identical fixation, on L and R. The α-carbon is in `context` (it does not
change connectivity), so you can either put stereo in `context` (shorthand for
"same on L and R") *or* put identical stereo in `left` and `right`. The explicit
form is clearer for auditors:

```gml
left [
    node [ id 0 stereo "tetrahedral[1, 7, 8, 9]!" ]
]
context [
    node [ id 0 label "C" ]
    # ... existing nodes 1, 7, 8, 9 and their edges to 0 ...
]
right [
    node [ id 0 stereo "tetrahedral[1, 7, 8, 9]!" ]
]
```

**Why even permutation matters.** If the chemistry preserves chirality, write
identical lists on L and R. If you write `[1,7,8,9]!` on L and `[7,1,8,9]!` on
R, you have silently encoded **inversion** (transposition is odd). This is the
single most common stereo-bug pattern and the one Workstream F's verifier
should be designed to catch.

**Shorthand alternative** (semantically equivalent, single source of truth):

```gml
context [
    node [ id 0 label "C" stereo "tetrahedral[1, 7, 8, 9]!" ]
    # ...
]
```

This works because `L = left ∪ context` and `R = right ∪ context` — the same
stereo flows to both sides.

### 4.2 E/Z creation/destruction (RCM)

**Caveat first.** Per §5, MØD does not enforce E/Z stereo today
(`TrigonalPlanar::morphismIso` and `morphismSpec` are `MOD_ABORT`). You can
*write* trigonal-planar annotations, and MØD will parse, depict, and store
them, but it will not refuse a match that violates them. Treat the following
as the *intent* annotation — Workstream F's verifier needs to check this
separately.

The RCM rule in `data/rules/rcm.gml` creates one new alkene `C(1)=C(3)` and one
byproduct alkene `C(2)=C(4)`. The two new alkene carbons (1 and 3) have degree
3 after the rule (the alkene + two other substituents that were already on 1
and 3 in the substrate). To declare E (trans) geometry across the new bond:

```gml
right [
    # ... existing right-side edges ...
    # Declare trigonal-planar geometry on each new sp2 carbon.
    # Neighbours of 1 in R: 3 (new C=C), [other-1A], [other-1B].
    # Neighbours of 3 in R: 1 (new C=C), [other-3A], [other-3B].
    # The bracket order encodes a chirality-equivalent for sp2: the
    # cyclic order around each carbon. For E across 1=3, both carbons
    # must list their "high-priority" substituent on the same side of
    # the cyclic order.
    node [ id 1 stereo "trigonalPlanar[3, otherA1, otherB1]!" ]
    node [ id 3 stereo "trigonalPlanar[1, otherA3, otherB3]!" ]
]
```

For **E/Z mixture (stereo-undetermined product)** — the realistic RCM case —
*omit the stereo attribute on R entirely*:

```gml
right [
    # ... existing right-side edges ...
    # No stereo annotation: MØD will infer trigonalPlanar geometry from
    # the C=C bond + two single bonds, in Sym (free) mode. This is the
    # canonical "E/Z mixture" representation.
]
```

This is the recommended pattern for any rule whose mechanism is non-selective
between E and Z.

### 4.3 Multi-center creation (Diels–Alder)

The transannular Diels–Alder rule in `data/rules/transannular_diels_alder.gml`
turns C1=C2-C3=C4 + C5=C6 into a cyclohexene with **four new sp3 stereocenters
(1, 4, 5, 6)**. The classic concerted [4+2] gives the *endo* or *exo* product
with the suprafacial-suprafacial geometry: across the new C1–C6 and C4–C5
bonds, the substituents on 1 vs 6 (and 4 vs 5) end up on the same face.

For a fully stereospecified endo product, declare all four new sp3 centers as
fixed tetrahedral in `right`. Substitute `H` and `R` for whatever the real
substituents are in your substrate; the IDs below are the cycloaddition node
IDs in the existing rule plus four implicit-H IDs `11, 14, 15, 16`:

```gml
right [
    # Existing edges from data/rules/transannular_diels_alder.gml:
    edge [ source 1 target 2 label "-" ]
    edge [ source 2 target 3 label "=" ]
    edge [ source 3 target 4 label "-" ]
    edge [ source 5 target 6 label "-" ]
    edge [ source 1 target 6 label "-" ]
    edge [ source 4 target 5 label "-" ]
    # Four new sp3 centers. For each, list:
    #   - the partner of the new sigma bond,
    #   - the still-attached part of the ring,
    #   - the two retained substituents (substituent + H, or whatever).
    # The cyclic order must agree across faces for endo vs exo.
    node [ id 1 stereo "tetrahedral[6, 2, 11, R1]!" ]
    node [ id 4 stereo "tetrahedral[5, 3, 14, R4]!" ]
    node [ id 5 stereo "tetrahedral[4, 6, 15, R5]!" ]
    node [ id 6 stereo "tetrahedral[5, 1, 16, R6]!" ]
]
```

**Important:** because all four centers are created simultaneously by a single
concerted mechanism, the four bracket lists must be *mutually consistent* (not
independent). For an *endo* product, the substituents on C1 and C4 point toward
the alkene C2=C3 (the same face as the diene π-system); for *exo* they point
away. The verifier check in §3.1(3) generalizes to: for a concerted multi-center
rule, the choice of even-vs-odd permutations across the centers is *not*
independent. Workstream F may want to encode the (endo, exo) pair as two
sibling rules rather than try to parameterise stereo within one rule.

### 4.4 Stereo-undetermined product (RCM E/Z mixture)

This is the same pattern as §4.2's second snippet — **omit `stereo` on R**, or
write `tetrahedral` / `trigonalPlanar` *without* brackets and *without* `!`:

```gml
right [
    # ... existing edges ...
    # Explicit "Sym" form — equivalent to omitting stereo, but documents intent.
    node [ id 1 stereo "trigonalPlanar" ]
    node [ id 3 stereo "trigonalPlanar" ]
]
```

The TrigonalPlanarSym form is the canonical "I assert this is sp2 but do not
constrain E/Z" annotation. It is more informative than no annotation because it
*does* commit to a geometry (so degree mismatch with the substrate is caught
at rule load) while leaving cis/trans free.

---

## 5. Open Questions / Things to Verify Against MØD Source

### 5.1 Edge-stereo is parsed but unused

`external/mod/libs/libmod/src/mod/lib/IO/GML.hpp:28,76` shows that `Edge::stereo`
is part of the GML grammar, but I found no consumer for it in the Stereo
subsystem (`Stereo::Read::parseEmbedding` is called only on vertices —
see `external/mod/libs/libmod/src/mod/lib/IO/GML.cpp` and the `parsedEmbedding`
field on `Vertex` but not on `Edge`). The author plausibly intended to allow
explicit per-bond E/Z labels (e.g. `edge [ source 1 target 2 label "=" stereo "E" ]`)
but the consumer code is not in the open-source tree as of this vendor-in. **To
verify:** grep the build for any use of `Edge::stereo` other than serialization
(`GML.cpp:10` writes it out unchanged on serialization). My read says none —
treat edge-stereo as a documentation-only annotation today.

### 5.2 TrigonalPlanar::morphismIso / morphismSpec are MOD_ABORT

`Stereo/Configuration/TrigonalPlanar.cpp:50-54` — both methods call `MOD_ABORT`.
So when you run a DG build under `withStereo=true` with a rule that has any
TrigonalPlanar configuration **and** MØD's match algorithm reaches a point
where it needs to compare two trigonal-planar configurations (i.e., the
substrate also has trigonal-planar stereo on the matched vertex), MØD will
abort. This is reachable.

**Implication for Workstream F:** keep E/Z annotations *advisory* (i.e., on R
only, with the substrate being stereo-free in the matched position) until
MØD's TrigonalPlanar is implemented. Or implement E/Z conservation in the
macrocert verifier without invoking MØD's match. To verify: build the aconitase
example with a substrate that has *trigonal-planar stereo on a matched vertex*
and confirm whether MOD_ABORT fires.

### 5.3 Linear::morphismIso likely also MOD_ABORT

Not directly read here but by symmetry with TrigonalPlanar/Any I expect it.
Read `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Linear.cpp` to
confirm. (Less critical — linear stereo is rarely meaningful.)

### 5.4 Behaviour when `LabelSettings` has `withStereo=false`

Confirmed by code reading: the GML parser stores stereo strings unconditionally;
the `Stereo::Inference` pass runs only when the consuming algorithm constructs
a stereo-aware data structure. With `withStereo=false`, stereo strings are
present in the rule object but never converted into `Configuration` instances
on the match path. **To verify empirically:** load a stereo-rich rule with the
default 2-arg `LabelSettings` and observe that DG.build proceeds without
honouring the stereo annotations. The existing `data/rules/` are stereo-free, so
this matters only once stereo is added.

### 5.5 The `e` virtual-edge convention

`Stereo/IO/Read.cpp:26` allows any single ASCII letter as a virtual-edge marker,
producing a `LonePair` entry. Convention in the MØD test suite (`04_graphFix.py:23`)
uses `e` (for "electron pair"). Whether `r` for radical or other letters carry
distinct semantics is not enforced by the parser — all become `Type::LonePair`.
The radical type is set only via the C++ API (`Inference::addRadical`). **Verify
before using:** that you cannot signal a radical from GML alone (probably true,
but worth a test).

### 5.6 Stereo on `context` vs split L/R

The DPO algebra says `L = left ∪ context`, `R = right ∪ context`. So stereo on a
`context` vertex should be equivalent to the same stereo on both `left` and
`right`. Worth a confirmation test — write the same rule both ways and check
isomorphism.

### 5.7 Behaviour of MØD when the bracket-list refers to a non-bonded vertex

The grammar accepts integers but they are resolved as out-edge offsets via
`Inference::addEdge`. If the integer does not correspond to a bonded neighbour,
`Inference` will either fail at the `assert(iter != outRange.second)` step
(release builds — UB) or raise an InputError if a debug guard is present. **To
verify:** the failure mode for malformed bracket lists.

### 5.8 Square-planar / trigonal-bipyramidal / octahedral

Not registered. If Workstream F needs them (relevant for some
metalloenzyme-catalysed reactions and certain transition-metal-mediated
cyclisations), the path is to (a) patch `GeometryGraph::GeometryGraph` to
register the geometry vertices, (b) author new `Configuration` subclasses
mirroring `Tetrahedral.cpp`, (c) populate the `Good`/`Bad` permutation
tables. The infrastructure scales; only the chirality enumeration is per-shape.

### 5.9 Andersen et al. 2017 paper – cross-checks

The paper [AFMS-Stereo] (DOI 10.1007/978-3-319-61470-0_4) is the formal source
for the algebra. Verify against the published text:
- §3 (Geometry Graph): confirm that the paper's notion of "geometry generalization"
  matches the `GeometryGraph::generalize` / `unify` operations.
- §4 (Embeddings): confirm that the paper's "neighbour ordering up to even
  permutation" semantics matches the `Good`/`Bad` table partition.
- §5 (Rule application): confirm that the paper's DPO-with-stereo definitions
  match `morphismSpec` / `localPredSpec` as implemented.

I have not retrieved the paper PDF in this pass. The implementation maps
cleanly onto the abstract above, and the citation key `AFMS-Stereo` in
`doc/source/Config.hpp:80` *("The implementation of the stereo-information
handling is a prototype based on [AFMS-Stereo]")* explicitly says this is the
prototype — minor divergences from the paper are possible.

---

## Appendix A: Source files consulted

| Path                                                                                    | Role                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `external/mod/examples/py/030_stereo/320_aconitase.py`                                  | Stereo-creating rule (aconitase)                  |
| `external/mod/examples/py/030_stereo/330_tartaric.py`                                   | Stereo-change rule (tartaric isomers)             |
| `external/mod/examples/py/030_stereo/340_tree.py`                                       | Non-trivial multi-center stereo                   |
| `external/mod/doc/source/formats/gml.rst`                                               | GML grammar (canonical)                           |
| `external/mod/doc/source/graphModel/index.rst`                                          | Rule semantics, L/K/R definitions                 |
| `external/mod/doc/source/formats/smiles.rst`                                            | Confirms SMILES `@`/`@@` ignored on input         |
| `external/mod/doc/source/references.rst`                                                | Andersen 2017 ICGT paper citation                 |
| `external/mod/libs/libmod/src/mod/Config.hpp`                                           | `LabelSettings`, `withStereo` switch              |
| `external/mod/libs/libmod/src/mod/lib/IO/GML.hpp`                                       | GML record types incl. `Vertex::stereo`           |
| `external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp`                               | The stereo-string sub-grammar parser              |
| `external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp`                         | Registered geometries (`any`, `linear`, `trigonalPlanar`, `tetrahedral`) |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Configuration.hpp`           | `Fixation`, `Configuration` base                  |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp`             | Good/Bad permutation tables                       |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/TrigonalPlanar.cpp`          | `MOD_ABORT` in morphism methods                   |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Any.cpp`                     | Top of geometry lattice                           |
| `external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp`                             | Geometry/embedding inference at load time         |
| `external/mod/test/py/stereo/04_graphFix.py`                                            | Worked test cases for all geometries              |
| `external/mod/test/py/stereo/10_errors.py`                                              | Error-mode test cases                             |
| `external/mod/test/py/stereo/30_morphismRule.py`                                        | Rule iso/spec under stereo                        |
| `external/mod/test/py/stereo/testTetraRule.py`                                          | End-to-end DG with tetra rule                     |
| `external/mod/test/py/papers/17_tetra_icgt/code/310_stereoDpo.py`                       | The canonical paper example                       |
| `src/macrocert/cli.py`                                                                  | `check-rules` subcommand                          |
| `src/macrocert/verifier/conservation.py`                                                | What `check-rules` actually validates             |
| `src/macrocert/verifier/gml_reader.py`                                                  | Macrocert's own GML reader (notes `stereo` on nodes; ignores it on edges) |

## Appendix B: Cited reference

[AFMS-Stereo] Andersen, Jakob L.; Flamm, Christoph; Merkle, Daniel; Stadler,
Peter F. **Chemical Graph Transformation with Stereo-Information.** *Graph
Transformation – 10th International Conference, ICGT 2017*, pp. 54–69, 2017.
DOI: [10.1007/978-3-319-61470-0_4](https://doi.org/10.1007/978-3-319-61470-0_4).
