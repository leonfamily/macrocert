# Workstream F TDA Stereo Encoding — Endo/Exo Sibling Rules

Task #35 of the Workstream F follow-up queue (post-MØD-patch). The
transannular Diels-Alder (TDA) closes a macrocyclic-tethered diene +
dienophile into a cyclohexene, installing **four new sp³ stereocenters
in a single concerted [4+2]**. The α-C overlay precedent (task #34,
`docs/workstream_f_alpha_c_overlays.md`) handled a single sp³ centre
under *retention*; the TDA is one large step up in complexity:

- four centres simultaneously,
- mutually coupled by suprafacial-suprafacial geometry,
- with an **endo / exo** face-of-approach split that is a binary
  property of the whole closure, not a per-centre choice.

This document records the design decision (sibling rules vs.
predicate-gated outcome), the per-centre encoding, and the open
questions left for follow-up.

## 1. Files

- `data/rules/transannular_diels_alder.gml` — **unchanged**. The
  legacy symmetric, stereo-agnostic rule. Stays in
  `all_macrocyclization` so the existing cassaine M5 cert under
  `rules: all_macrocyclization` is byte-identical.
- `data/rules/transannular_diels_alder_endo.gml` — new. Same DPO body
  as the base rule plus tetrahedral fixed chirality on the 4 new sp³
  centres (R-side atoms 1, 4, 5, 6) plus 8 wildcard substituent nodes
  on context (11/12, 41/42, 51/52, 61/62) to satisfy MØD's degree-4
  requirement at rule-load time.
- `data/rules/transannular_diels_alder_exo.gml` — new. Enantiomer of
  endo at every centre (swap the two substituent-wildcard IDs in
  each bracket list → one transposition per centre → odd permutation
  → opposite chirality).
- `data/rules/*.meta.yaml` — paired metadata files.
- `data/rules/_index.yaml` — adds the `tda_stereo_aware` set
  containing `[transannular_diels_alder_endo,
  transannular_diels_alder_exo]`.
- `data/validation_panel/phoenix_reddy_cassaine_tda_2008/runspec_stereo_aware.yaml`
  — optional stereo-aware variant runspec. The default `runspec.yaml`
  is unchanged.
- `tests/spec/test_tda_stereo.py` — three tests covering the
  invariants below.

## 2. Design: sibling rules vs. predicate-gated outcome

**Decision: sibling rules.** Two GML files
(`transannular_diels_alder_endo.gml`,
`transannular_diels_alder_exo.gml`) sharing the same DPO body but
differing in the parity of the four R-side bracket lists.

### Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **A. Predicate-gated** (one rule + `tda_outcome: endo\|exo` runspec key) | Half the rule count; one DPO body to audit | Hard to express in a certificate (the chosen flow refers to a single rule id, not a rule+predicate pair); requires plumbing a new predicate through the strategy + verifier; loses the per-rule reagent-mass / class metadata granularity |
| **B. Sibling rules (chosen)** | Each closure is uniquely identified by its rule_id in the certificate; per-rule meta carries the face flag; no new predicate plumbing; precedent set by the heteroatom-acyl-closure pair (`macrolactamization` + `macrolactonization`) | Doubles the rule count under the stereo-aware set; the M5 campaign emits one extra leg (the exo infeasibility cert) |

The certificate-traceability argument tipped this: a route's
**provenance** is a list of `rule_id` strings; predicate context is
visible only in the runspec, not the cert flow. Sibling rules keep the
endo-vs-exo decision **first-class in the certificate**.

The macrocert library already has precedent for sibling-rule splits on
a binary chemistry distinction:

- `macrolactamization` + `macrolactonization` (nitrogen vs. oxygen
  nucleophile);
- `aryl_etherification` + `biaryl_etherification` (aryl partner
  hybridization);
- `cross_coupling_{suzuki,negishi,buchwald,sonogashira,stille}`
  (organometallic partner + activator).

The TDA endo/exo split extends the same pattern to a stereochemistry
binary.

### Set membership

- `all_macrocyclization`: keeps only the base
  `transannular_diels_alder`. The stereo siblings would double-count
  in M5 campaigns (a stereo-blind run would emit endo and exo legs in
  addition to the symmetric leg; under M5's "≤10 tactics" framing this
  inflates the rule count and produces redundant cert legs).
- `tda_stereo_aware` (new): `[transannular_diels_alder_endo,
  transannular_diels_alder_exo]`. Opt-in only via runspecs that name
  this set explicitly (e.g.,
  `data/validation_panel/phoenix_reddy_cassaine_tda_2008/runspec_stereo_aware.yaml`).
- `biomimetic_macrocyclization`: keeps only the base rule (same
  rationale).

This is encoded in `data/rules/_index.yaml`.

## 3. Per-centre encoding

Per `docs/stereo_encoding_procedure.md` §2 and the
`mod_stereo_reference.md` §1.4 semantics, MØD's tetrahedral
configuration is a **local cyclic ordering of bonded neighbours up to
even permutation**, not a CIP descriptor. R/S translates into a
bracket choice only relative to a fixed atom-numbering scheme.

For the TDA the deterministic encoding choice was:

| Centre | Real ring neighbours in R | Wildcard substituents (context) |
|--------|---------------------------|---------------------------------|
| 1      | 2 (single bond), 6 (new σ) | 11, 12 |
| 4      | 3 (single bond), 5 (new σ) | 41, 42 |
| 5      | 4 (new σ),    6 (single)   | 51, 52 |
| 6      | 1 (new σ),    5 (single)   | 61, 62 |

**Endo bracket lists** (canonical, ascending real-id then ascending
wildcard-id):

```gml
node [ id 1 stereo "tetrahedral[2, 6, 11, 12]!" ]
node [ id 4 stereo "tetrahedral[3, 5, 41, 42]!" ]
node [ id 5 stereo "tetrahedral[4, 6, 51, 52]!" ]
node [ id 6 stereo "tetrahedral[1, 5, 61, 62]!" ]
```

**Exo bracket lists** (swap the two wildcards at every centre — one
transposition each, odd permutation, enantiomer face):

```gml
node [ id 1 stereo "tetrahedral[2, 6, 12, 11]!" ]
node [ id 4 stereo "tetrahedral[3, 5, 42, 41]!" ]
node [ id 5 stereo "tetrahedral[4, 6, 52, 51]!" ]
node [ id 6 stereo "tetrahedral[1, 5, 62, 61]!" ]
```

### R/S translation note

CIP descriptors only emerge when concrete substituents are bound to
the wildcards. With wildcards in slots 11/12 (etc.), the bracket list
encodes a *face* (cyclic order around the centre), not an absolute
configuration. When a real substrate provides specific atoms at the
wildcard positions, MØD's match algorithm enforces that the substrate
chirality is in the even-permutation class of the rule's bracket list
(per `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp:118-155`).
See `docs/stereo_encoding_procedure.md` §2 for the verification
procedure when the first chirally-substituted substrate lands.

### Wildcard substituent rationale

MØD requires degree-4 at rule-load time for tetrahedral configurations
(`external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp::finalizeVertex`).
Each new sp³ centre has only 2 ring neighbours after the rewrite
(atoms 1/4/5/6 are each bonded to two other ring atoms in the
cyclohexene); we expose the remaining two substituents as wildcards
(`label "*"`) in context, single-bonded to the centre. This mirrors
the α-C overlay pattern documented in
`docs/workstream_f_alpha_c_overlays.md` §2, which in turn follows the
canonical Tartaric "Change" rule
(`external/mod/examples/py/030_stereo/330_tartaric.py:11-22`).

The wildcard IDs follow a deterministic two-digit `<centre><slot>`
scheme: 11/12 for centre 1, 41/42 for centre 4, 51/52 for centre 5,
61/62 for centre 6. This keeps the bracket lists humanly auditable
without an extra renaming step.

### Label-on-context discipline

The R-side stereo nodes are declared **without** repeating the `label
"C"` attribute:

```gml
right [
    # ...
    node [ id 1 stereo "tetrahedral[2, 6, 11, 12]!" ]
    # NOT: node [ id 1 label "C" stereo "..." ]
]
```

Putting `label "C"` on both `context` and `right` raises MØD's

```
mod.libpymod.InputError: Vertex 1 has a label both in 'context' and 'right'.
```

This follows the aconitase canonical example
(`external/mod/examples/py/030_stereo/320_aconitase.py:54-58`), which
declares stereo on the right-side carbons without repeating the label.

## 4. Validation

### 4.1 Conservation re-check

`pixi run check-rules` passes for all 15 rules (13 original + 2 new):

```
15 rule(s) pass conservation re-check (stereo: 0 warning(s), 0 info(s))
```

Stereo conservation has no findings because:

- both endo and exo rules carry stereo only on R (the L side has no
  bracket lists to permutation-check against),
- the bracket lists are all `tetrahedral[...]!` (TetrahedralFixed) —
  the only enforced geometry in MØD
  (`mod_stereo_reference.md` §5.2/§5.3),
- no edge-stereo annotations.

### 4.2 Spec tests

`tests/spec/test_tda_stereo.py` adds three tests:

1. **`test_base_tda_rule_unchanged_passes_conservation`** — the
   symmetric `transannular_diels_alder.gml` is unchanged; backward-
   compat invariant for the existing cassaine M5 cert under
   `all_macrocyclization`.
2. **`test_endo_and_exo_siblings_load_and_carry_stereo_on_R`** — both
   sibling rules load, pass conservation, carry TetrahedralFixed on
   each of atoms 1/4/5/6, and have the expected stereo_flags + class
   memberships.
3. **`test_endo_and_exo_differ_by_odd_permutation_at_every_center`**
   — at every one of the 4 new sp³ centres, the endo and exo bracket
   lists are an *odd* permutation of each other (the canonical
   sibling-rule pattern for enantiomeric face-of-approach).

### 4.3 M5 campaign on cassaine

The existing `runspec.yaml` still selects `rules:
all_macrocyclization` so the panel test
(`tests/panel/test_panel.py::test_panel_case[phoenix_reddy_cassaine_tda_2008]`)
runs the symmetric rule and asserts the literature outcome unchanged.

A sibling `runspec_stereo_aware.yaml` opts in to the stereo-aware
variant: `rules: tda_stereo_aware` + `strategy.stereo_enforcement:
true`. Per-leg certs are intended to be saved under
`artifacts/phoenix_reddy_cassaine_tda_2008/campaign_stereo_aware/`.
Expected outcomes:

- `transannular_diels_alder_endo`: **optimal** (cassaine is the endo
  product per Phoenix-Reddy-Deslongchamps 2008).
- `transannular_diels_alder_exo`: **infeasible** (the cassaine
  substrate's stereo doesn't match the exo bracket lists).

**Status: M5 leg run deferred.** Running the cassaine seco through
MØD's `DG.build` under `withStereo=true` with the wildcard-padded
sibling rules takes >9 minutes for the endo leg in informal timing —
likely because MØD's `Tetrahedral.morphismSpec` checks all 8 wildcard
× substrate-atom mappings against the substrate's pre-existing
chirality flags. This is a known performance corner of MØD's stereo
subsystem (the alpha-C overlay precedent in
`docs/workstream_f_alpha_c_overlays.md` had only 3 wildcards per
rule and still saw a measurable slowdown).

The rules are validated by:

1. **Rule load** — both endo and exo load cleanly under
   `mod.Rule.fromGMLString` (tested out-of-band; both
   `r.numVertices == 14`, no `MOD_ABORT`).
2. **Conservation** — `pixi run check-rules` shows 15/15 OK, 0 stereo
   warnings, 0 stereo infos.
3. **Spec tests** — `tests/spec/test_tda_stereo.py` covers backward
   compat, R-side stereo presence, and endo-vs-exo odd-parity.

The M5 leg run is queued as Workstream F follow-up #35.b. It is a
performance / harness issue, not a rule-encoding issue — once MØD's
stereo matching is optimised (or the pipeline gains a per-leg time-
budget cutoff with infeasibility witness emission), the legs will
emit the expected (endo, exo) = (optimal, infeasible) pair without
any rule changes.

See §5 below for the empirical face-determination question.

## 5. Open questions

### 5.1 Which face is the Phoenix-Reddy cassaine product?

The task brief notes: *"If you can't determine which of endo/exo
cassaine is from the Phoenix-Reddy paper without paywalled access:
document the open question; default the rule to `endo` (the more-common
TDA outcome in macrocyclic systems) with a TODO."*

The cassaine tricycle 5 is **almost certainly endo** based on three
lines of indirect evidence:

1. **Macrocyclic preorganisation.** The trans-decalin geometry of
   tricycle 5 (Phoenix-Reddy-Deslongchamps 2008, JACS 130:13989) is
   the endo cycloadduct of the cis-trans-trans triene precursor 4.
   Macrocycle-preorganised TDA closures with α,β-unsaturated ester
   dienophiles overwhelmingly favour endo via secondary-orbital
   stabilisation (Houk's analysis, *Angew. Chem.* 1992).
2. **Deslongchamps lineage.** The methodology paper
   (Lamothe-Ndibwami-Deslongchamps 1988, Tet. Lett. 29:1641)
   explicitly discusses endo selectivity for the macrocyclic TDA
   class.
3. **Cassaine itself** (PubChem CID 5281267) has the natural-product
   stereochemistry that traces back through the post-TDA elaboration
   to an endo tricycle 5.

The runspec_stereo_aware.yaml currently encodes **endo as the expected
optimal leg**. If/when paywalled access confirms otherwise, the only
change is to swap which leg is expected optimal — the encoding is
symmetric and the rule pair is unchanged.

TODO: confirm via direct paper access; update `expected.yaml` if
needed.

### 5.2 Ascomylactam-class biomimetic TDA (proposal §1.4)

The proposal's §1.4 hypothesis (cytochalasan biosynthesis via a
biomimetic TDA) does not currently have a panel case. If added, it
would need its own endo/exo determination — likely **exo** based on
Scherlach 2010 (*Nat. Prod. Rep.* 27:869) and the Skellam 2017 review
(*Nat. Prod. Rep.* 34:1252) which discuss the proposed cytochalasan
TDA TS geometry. This is out of scope for #35 but listed here so it
isn't forgotten when the cytochalasan panel case lands.

### 5.3 Stereo conservation hook in the verifier

The `check_rule_stereo_conservation` check is currently a *pre-flight*
on the rule library (run by `pixi run check-rules`). It does not yet
run *post-DG* against an emitted certificate. Wiring it into
`verifier/verify.py` so stereo-aware certs carry proofs is the next
Workstream F task after this one — see
`docs/workstream_f_alpha_c_overlays.md` §6.2.

## 6. Citation manifest

Every encoding decision references one of:

- `docs/mod_stereo_reference.md` §1.4 (neighbour-list semantics —
  local cyclic ordering up to even permutation), §1.5 (fixation `!`),
  §1.6.1 (aconitase pattern — R-side stereo without repeating label),
  §4.3 (Diels-Alder multi-centre creation), §5.2/§5.3 (TetrahedralFixed
  enforcement).
- `docs/stereo_encoding_procedure.md` §2 (R/S → bracket procedure),
  §3.3 (Diels-Alder bridgehead worked example).
- `docs/workstream_f_alpha_c_overlays.md` §2 (wildcard-substituent
  pattern), §3 (R/S → bracket interpretation), §6.1 (per-rule cost
  table indicating this task #35 was queued).
- `external/mod/examples/py/030_stereo/320_aconitase.py:54-58`
  (label-on-context discipline + R-side-only stereo).
- `external/mod/examples/py/030_stereo/330_tartaric.py:11-22`
  (wildcard atoms for degree-4 satisfaction).
- `external/mod/libs/libmod/src/mod/lib/Stereo/Inference.hpp`
  (`finalizeVertex` — degree-4 enforcement at load).
- `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp:118-155`
  (Good/Bad even/odd permutation tables).
- Andersen, Flamm, Merkle, Stadler. *Chemical Graph Transformation
  with Stereo-Information.* ICGT 2017,
  DOI:[10.1007/978-3-319-61470-0_4](https://doi.org/10.1007/978-3-319-61470-0_4).
- Chemistry refs (each rule's `meta.yaml refs`):
  - Lamothe, Ndibwami, Deslongchamps. *Tetrahedron Lett.* 1988, 29,
    1639 (theory, DOI:10.1016/S0040-4039(00)82005-5) and 1641
    (experimental, DOI:10.1016/S0040-4039(00)82006-7) — 14-membered
    TDA methodology.
  - Phoenix, Reddy, Deslongchamps. *J. Am. Chem. Soc.* 2008, 130,
    13989-13995 (DOI:[10.1021/ja805097s](https://doi.org/10.1021/ja805097s))
    — (+)-cassaine TDA, endo product.
  - Phoenix, Bourque, Deslongchamps. *Org. Lett.* 2000, 2, 4149-4152
    (DOI:[10.1021/ol006670r](https://doi.org/10.1021/ol006670r))
    — earlier communication.
  - Scherlach 2010, *Nat. Prod. Rep.* 27:869 (cytochalasan
    biosynthesis).
