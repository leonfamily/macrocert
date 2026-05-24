# Stereo Encoding Procedure: R/S → MØD local-cyclic brackets

A practical recipe for encoding an X-ray-derived (or otherwise
authoritative) absolute configuration into a MØD GML rule. Companion
to [`mod_stereo_reference.md`](./mod_stereo_reference.md), which is the
specification; this document is the procedure.

## 1. Why R/S is not bracket order

CIP descriptors (`R`/`S`) sort the four substituents of a tetrahedral
center by CIP priority, view down the lowest-priority substituent, and
read off the clockwise/anticlockwise direction of the remaining three.

MØD does **not** look at substituent priorities. Its tetrahedral
configuration is the cyclic ordering of the four abstract neighbour
IDs: `[a, b, c, d]` and any *even* permutation of it denote the same
chirality class; an *odd* permutation denotes the enantiomer (see
`Tetrahedral.cpp:118-155` and `mod_stereo_reference.md` §1.4).

The implication: the same R-configured molecule has many valid bracket
lists, and the same bracket list applied to two molecules with
different substituents at corresponding IDs can mean different CIP
descriptors. The bracket is *local-cyclic*; R/S is *global-priority*.

The procedure below converts an authoritative R/S call into a bracket
list *for a specific atom-numbering choice* in your rule, then verifies
the result against a known case.

## 2. Procedure

**(a) Draw the molecule (or open the X-ray PDB).** Print the structure
with all four substituents of the stereocenter clearly labelled. Note
the absolute configuration as it appears in the source.

**(b) List the four neighbours with their MØD IDs.** Real neighbours
are integers; lone pairs / radicals are single-letter virtual edges
(see §1.4(3) of the reference). Record them as a 4-tuple keyed by
substituent identity, e.g.

| substituent | MØD ID |
| ----------- | ------ |
| `–H`        | 7      |
| `–NH₂`      | 5      |
| `–COOH`     | 1      |
| `–CH₃`      | 9      |

**(c) Pick an ordering criterion and write the *canonical* bracket.**
The bracket order is arbitrary up to even permutations, so use a
deterministic ordering. The macrocert convention is **ascending ID**:
sort the four IDs ascending → `[1, 5, 7, 9]`.

**(d) Verify against a known case (L-alanine).** L-alanine is *S* at
the α-carbon, with neighbours `–H`, `–NH₂`, `–COOH`, `–CH₃`. Pick MØD
IDs matching the table. Build the molecule in MØD with each candidate
annotation and print it with `GraphPrinter.withPrettyStereo = True`; the
correct bracket lists for L-alanine form one chirality class. If your
ascending-ID write-up is in that class you have S; otherwise you have R,
and swapping any two entries flips parity once, landing in S.

> The "build and print" verification is non-negotiable for the first
> stereocenter in each new chemical family. Subsequent centers in the
> same family can be transcribed by analogy.

**(e) Write the bracket with `!`.** The trailing `!` promotes the
configuration from `TetrahedralSym` (matches either chirality) to
`TetrahedralFixed` (matches this chirality class only):

```gml
node [ id 0 stereo "tetrahedral[1, 5, 7, 9]!" ]
```

Omit `!` only when you intend "this is sp3 with four substituents, but
I'm not committing to chirality" — the `Sym` form, used on the L side
of *create-stereo* rules.

## 3. Worked examples

### 3.1 Lactam α-carbon (retention in macrolactamization)

The α-amino acid's α-carbon does not change connectivity during
macrolactamization. Its bracket list must be identical on L and R (or
declared on `context` only):

```gml
left  [ node [ id 0 stereo "tetrahedral[1, 5, 7, 8]!" ] ]
right [ node [ id 0 stereo "tetrahedral[1, 5, 7, 8]!" ] ]
```

If the source is L (S-configured) and `[1, 5, 7, 8]` is verified per
§2.d to be in the L class, this encodes retention. Any odd-permutation
mismatch between L and R silently encodes inversion — the verifier's
`odd_permutation_inversion` error code catches it.

### 3.2 RCM new sp3 center

Ring-closing metathesis on a substituted diene can create a new sp3
center at the allylic position (not at the alkene carbon). For a stereo
created by an E-selective RCM, declare the bracket on the **right**
only — there is no pre-existing chirality to compare:

```gml
right [ node [ id 12 stereo "tetrahedral[3, 11, 13, 17]!" ] ]
```

The verifier emits a `fixation_transition` warning (Sym → Fixed) but
no error — this is the "stereo created" pattern from §2.1 of the
reference.

### 3.3 Diels–Alder bridgehead (concerted multi-center creation)

[4+2] cycloaddition creates four new sp3 stereocenters simultaneously;
their stereochemistry is *coupled* (endo vs. exo). Encode each
bridgehead with a bracket on R, walking the cyclohexene ring in a
consistent rotational sense:

```gml
right [
    node [ id 1 stereo "tetrahedral[6, 2, 11, R1]!" ]
    node [ id 4 stereo "tetrahedral[5, 3, 14, R4]!" ]
    node [ id 5 stereo "tetrahedral[4, 6, 15, R5]!" ]
    node [ id 6 stereo "tetrahedral[5, 1, 16, R6]!" ]
]
```

The rotational sense (clockwise vs. counterclockwise viewed from above
the diene π-face) is your endo/exo choice. Document it in the rule's
`meta.yaml`. For both endo and exo, write two sibling rules rather
than a parameterised one.

## 4. Pitfalls

**Atropisomerism.** Biaryl axial chirality is not tetrahedral; MØD has
no registered configuration for it. Document in `meta.yaml` and treat
the rule as stereo-erasing for now (adding support requires patching
MØD's `GeometryGraph` — see reference §5.8).

**Lone-pair virtual edges.** A trigonal nitrogen with two real
neighbours and one lone pair uses a letter token: `stereo "[1, 2, e]!"`.
Any single ASCII letter becomes a `LonePair` virtual edge
(`Stereo/IO/Read.cpp:26`). Do not also count the lone pair as an integer
neighbour — that double-counts. The verifier skips the even-permutation
check when either side contains letters, because parity is no longer
well-defined relative to the integer indices alone.

**`tetrahedral` without brackets means "either chirality".** On L it
matches any chirality (used by stereo-erasing rules); on R it asserts
the product is stereo-undefined (used by non-selective mechanisms only).
For stereospecific products always use `!` and an explicit bracket.

**Edge stereo (`stereo "E"` on a `=` bond) is ignored.** MØD parses but
never enforces edge-level stereo (reference §5.1). E/Z geometry must
be encoded as `trigonalPlanar` *vertex* stereo, not `E`/`Z` edge
stereo. The Workstream F verifier emits an `edge_stereo_ignored` info
for any such annotation.

**`trigonalPlanar` enforcement is a `MOD_ABORT`.** `trigonalPlanar` and
`linear` configurations parse and depict, but their `morphismIso` /
`morphismSpec` are `MOD_ABORT` (reference §5.2/§5.3). Asserting a fixed
`trigonalPlanar[...]` annotation on a matched substrate vertex crashes
MØD at runtime. The verifier emits `unenforced_geometry_fixed`. Until
MØD implements them, treat E/Z stereo as **advisory**: write on R only,
ensure substrate has no stereo on the matched vertex.

## 5. References

- Andersen, Flamm, Merkle, Stadler. *Chemical Graph Transformation
  with Stereo-Information.* ICGT 2017, pp. 54–69. DOI:
  [10.1007/978-3-319-61470-0_4](https://doi.org/10.1007/978-3-319-61470-0_4).
  Formal definition of geometry-graph stereo, even-permutation
  semantics, and DPO with stereo.
- MØD canonical examples:
  `external/mod/examples/py/030_stereo/{320_aconitase,330_tartaric,340_tree}.py`.
- Companion spec: [`docs/mod_stereo_reference.md`](./mod_stereo_reference.md).
- Source files most relevant when in doubt:
  - `external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp` — sub-grammar parser.
  - `external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp` — registered geometries.
  - `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp` — `Good`/`Bad` permutation tables.
  - `external/mod/libs/libmod/src/mod/Config.hpp` — `LabelSettings`, `withStereo`.
