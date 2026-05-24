# Workstream F #36 — Stereo Policy Metadata + Chemistry-Aware Gate

**Status.** Landed. Pre-M5 gate's stereo check is no longer a naïve
text-grep for the literal string `stereo` in GML bodies — it reads each
rule's declared `stereo_treatment` and enforces a policy appropriate to
the chemistry at the bond site.

## Motivation

The previous gate failed 11 of 13 rules because cross-couplings, biaryl
ether, c–h, hwe, and rcm rules had no `stereo` token in their GML
bodies. But many of those rules **shouldn't** carry tetrahedral stereo —
the bond-forming atoms are sp², so there is no point chirality at the
bond site to enforce. Forcing fake stereo annotations to pass the gate
would be dishonest. Instead, each rule now declares the *kind* of
stereo policy that applies to its bond chemistry.

## The four categories — wait, three

The taxonomy is `STEREO_TREATMENTS` in `src/macrocert/spec/rules.py`:

| Treatment        | When it applies                                                                    | Gate behaviour                                                                          |
| ---------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `match_enforced` | Rule body carries tetrahedral stereo (sp³ stereocenter at bond site)               | GML body MUST contain a `stereo` token; otherwise fail.                                 |
| `n_a_sp2_only`   | Bond-forming atoms are sp² (sp²–sp², Ar–O, alkene C=C); no sp³ chirality at site   | Pass without grep. No stereo annotation required.                                       |
| `advisory_only`  | Chemistry-dependent stereo MØD can't enforce (atropisomerism, E/Z trigonalPlanar)  | Pass, but `stereo_advisory` field MUST be non-empty. Advisory flows into the cert.      |

A fourth category, `n_a_sp2_only_at_bond_site`, was considered for
`aryl_etherification` (Ar(sp²)–O–C(sp³)) where the alcohol C(sp³) is
off-rule. The decision was to collapse it into `n_a_sp2_only`: the
off-rule sp³ stereo is preserved automatically by DPO graph-
isomorphism, so no rule-body annotation is needed regardless.

## Per-rule policy assignment

| Rule                            | Treatment        | Rationale                                                                                          |
| ------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------- |
| `macrolactamization`            | `match_enforced` | α-C tetrahedral stereo carried in GML (Workstream F #34)                                           |
| `macrolactonization`            | `match_enforced` | α-C tetrahedral stereo, sibling of macrolactamization                                              |
| `transannular_diels_alder_endo` | `match_enforced` | Four sp³ stereocenters pinned on R-side (Workstream F #35)                                         |
| `transannular_diels_alder_exo`  | `match_enforced` | Four sp³ stereocenters pinned on R-side (Workstream F #35)                                         |
| `aryl_etherification`           | `n_a_sp2_only`   | Bond is Ar(sp²)–O; alcohol C(sp³) is off-rule, preserved by graph-isomorphism                      |
| `c_h_dehydrogenative_coupling`  | `n_a_sp2_only`   | Ar–C(sp²) bond                                                                                     |
| `cross_coupling_buchwald`       | `n_a_sp2_only`   | Ar(sp²)–N coupling (v0 aryl-amine scope)                                                           |
| `cross_coupling_negishi`        | `n_a_sp2_only`   | sp²–sp² C–C                                                                                        |
| `cross_coupling_sonogashira`    | `n_a_sp2_only`   | Ar(sp²)–C(sp) alkyne                                                                               |
| `cross_coupling_stille`         | `n_a_sp2_only`   | sp²–sp² C–C                                                                                        |
| `cross_coupling_suzuki`         | `n_a_sp2_only`   | sp²–sp² biaryl C–C (atropisomerism is downstream geometry, not point chirality)                    |
| `transannular_diels_alder`      | `n_a_sp2_only`   | Base rule: bond-forming atoms are sp² diene/dienophile; endo/exo siblings carry the stereo overlay |
| `biaryl_etherification`         | `advisory_only`  | Atropisomerism is 3D-geometric (Boger 1999, DOI:10.1021/ja990189i)                                 |
| `hwe_olefination`               | `advisory_only`  | E/Z is alkene geometry, not point chirality; activator-dependent inversion                         |
| `rcm`                           | `advisory_only`  | MØD's `trigonalPlanar::morphismIso/morphismSpec` are `MOD_ABORT` (see citations below)             |

## Certificate provenance flow

When `certify.emit()` assembles a certificate, it walks the IR's
hyperedges (and the composed rule's `rule_ids_traced` if available),
looks up each rule's `stereo_treatment`, and copies the
`stereo_advisory` text of every `advisory_only` rule into:

```json
{
  "provenance": {
    "stereo_advisories": [
      {"rule_id": "rcm", "advisory": "..."},
      {"rule_id": "hwe_olefination", "advisory": "..."}
    ]
  }
}
```

The list is sorted by `rule_id` for hash-stable certificates. Rules
with `match_enforced` or `n_a_sp2_only` treatment contribute nothing
(their stereo handling is either enforced upstream by MØD or trivially
N/A).

`certify.emit()` accepts an optional `library=` keyword. When `None`
(legacy callers), the provenance block is still present but
`stereo_advisories` is empty — backward-compatible inert default.

## Pre-M5 gate per-rule diagnostic

The gate now prints a per-rule table:

```
    stereo policy per rule:
      - aryl_etherification             [n_a_sp2_only  ] sp²-only bond site
      - biaryl_etherification           [advisory_only ] advisory present
      - macrolactamization              [match_enforced] stereo present
      - rcm                             [advisory_only ] advisory present
      ...
[PASS] stereo policy declared — 15 rules, policy honored
```

This makes the gate's diagnostic actionable: if a new rule lands
without a treatment declaration, you see immediately whether the gate
applied the implicit `match_enforced` default and whether that's the
intended chemistry.

## Citations supporting the `advisory_only` advisories

- **RCM `trigonalPlanar` MOD_ABORT.**
  `external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/TrigonalPlanar.cpp:50-54`
  — both `morphismIso` and `morphismSpec` call `MOD_ABORT`. Cross-referenced
  in `docs/mod_stereo_reference.md` §5.2 and `docs/workstream_f_harness.md`
  §Divergence. Original RCM substrate-side stereo strategy described by
  Gradillas & Pérez-Castells (2006) *Angew. Chem. Int. Ed.* 45:6086,
  DOI:10.1002/anie.200600641.
- **HWE Still-Gennari Z-inversion.** Still & Gennari (1983)
  *Tetrahedron Lett.* 24:4405, DOI:10.1016/S0040-4039(00)85909-2.
- **HWE Ando diaryl-phosphonate Z-inversion.** Ando (1997) *J. Org. Chem.*
  62:1934, DOI:10.1021/jo970057c.
- **Biaryl-ether atropisomer equilibration.** Boger et al. (1999)
  *JACS* 121:3226, DOI:10.1021/ja990189i (ordered atropisomer
  equilibrations on vancomycin CD/DE).

## Open: validating `advisory_only` chemistry post-firing

The advisory text says *what* the chemistry does, but the certificate
cannot prove the substrate exhibits the asserted outcome. The path
forward is Workstream D's `enforce_ez_geometry` predicate (partial
answer for RCM/HWE):

- **RCM/HWE.** A panel-time RDKit check on `Bond.GetStereo()` against
  the asserted E/Z (in the runspec) — runs after MØD constructs the
  product graph, before the cert is emitted. This converts a
  documentation-only advisory into a panel-time enforcement.
- **Biaryl atropisomerism.** No graph-level enforcement is possible
  without a 3D conformer search. Defer to Layer D (energetics) — the
  atropisomer barrier separates kinetic vs thermodynamic products and
  is the natural enforcement layer. Track as a future ticket.

## Tests

- `tests/spec/test_rules.py` — 7 new tests covering default, all three
  treatments, advisory required, unknown value rejection, taxonomy
  cardinality, and end-to-end library loading.
- `tests/spec/test_pre_m5_gate.py` — 8 tests covering the four
  categories in the gate, lock-toggle skip path, and a live-library
  smoke test that the 15 shipped rules all pass.
- `tests/kernel/test_certify_provenance.py` — 4 tests covering the
  cert provenance flow: advisory propagation, no-op for non-advisory
  treatments, and the library-less backward-compat path.

## Backward compatibility

- Rules without a `stereo_treatment` field parse as `match_enforced`
  (the existing macrolactam/macrolactone semantics).
- Lockfiles with `stereo_annotations_required: false` short-circuit
  the check entirely (pre-#36 lockfiles).
- `certify.emit()` called without `library=` keeps the provenance
  block present but inert.
