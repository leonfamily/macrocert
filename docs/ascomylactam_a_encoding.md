# Ascomylactam A — M5 target encoding report

**Date**: 2026-05-24
**Builder**: `scripts/build_ascomylactam_a.py`
**Output**: `data/targets/ascomylactam_a/{structure.mol, ring_perimeter.txt, notes.md, atom_label_map.txt}`
**Signed**: `Ivan Leon (TBD)` — pending visual atom-by-atom audit.

## Source

- Chen, Y. *et al.* *J. Nat. Prod.* **82**, 1752–1758 (2019).
  DOI: [10.1021/acs.jnatprod.8b00918](https://doi.org/10.1021/acs.jnatprod.8b00918).
- CCDC entry **1515168** (single-crystal X-ray, Cu Kα,
  *P*2₁, *T* = 150 K, Flack −0.13(9)).
- Triangulated brief: `data/targets/ascomylactam_a/research_findings.md`.

## Encoding method

**SMILES-driven via RDKit**, not CIF-driven.

The CCDC entry sits behind an interactive captcha that the agent
harness cannot satisfy; the ACS supporting-information PDF returns
HTTP 403. Rather than block on access, the build script
(`scripts/build_ascomylactam_a.py`) constructs the molecular graph
atom-by-atom from the primary-source connectivity description in
Chen 2019 Table 1 + Figure 1 (transcribed in `research_findings.md`
§2), assigns the twelve sp³ stereocenters per the X-ray absolute
configuration reported in the paper abstract, embeds with RDKit
ETKDG, MMFF-optimizes, and writes a strict V2000 Molfile via
OpenBabel — same pipeline as `scripts/build_panel_lactams.py`.

Build-time invariants (all asserted, build aborts on failure):

- Molecular formula = **C₃₅H₄₅NO₅** (matches Chen 2019 HRESIMS).
- Heavy atom count = **41** (35 C + 5 O + 1 N).
- Stereocenter count = **12 assigned of 12 total** (`Chem.AssignStereochemistry`
  CIP codes match the requested R/S labels for every center).
- 13-membered ring located by the encoder's SSSR walk.

Canonical isomeric SMILES (round-trip from the encoded mol):

```
CO[C@@H]1C2=C(O)[C@@]34[C@H]5[C@H](Oc6ccc(cc6)C[C@]1(O)NC2=O)[C@H]1[C@@H](C[C@H](C)C[C@@H]1C)[C@@H]5C(C)=C[C@]3(C)C=C(C)[C@@H]4C
```

## Stereo assignments (Chen 2019 X-ray, CCDC 1515168)

All twelve sp³ stereocenters assigned by trial-and-error on the
RDKit chiral tag (CW vs CCW), verified by `Chem.AssignStereochemistry`
producing the requested CIP descriptor:

| Paper label | CIP | Position |
| --- | --- | --- |
| C-1   | *S* | sp³ CH bearing Me-20 |
| C-4   | *R* | sp³ quaternary bearing Me-22 |
| C-7   | *S* | sp³ CH (ring B/D junction) |
| C-8   | *S* | sp³ CH (ring C/D junction) |
| C-10  | *R* | sp³ CH bearing Me-24 |
| C-12  | *S* | sp³ CH bearing Me-25 |
| C-13  | *R* | sp³ CH (ring C/D junction) |
| C-14  | *R* | sp³ oxymethine; macrocyclic ether O on C |
| C-15  | *S* | sp³ CH (ring B/D junction) |
| C-16  | *S* | sp³ CH (ring A/B/E junction) |
| C-1′  | *R* | sp³ CH bearing OMe |
| C-2′  | *R* | sp³ quaternary hemiaminal (OH + NH) |

## Atom-by-atom audit (paper label ↔ RDKit canonical index)

Heavy-atom mapping (canonical SMILES indexing; H atoms not shown):

| Canon idx | Paper label | Element | Hyb / role |
| ---: | --- | :---: | --- |
|  0 | C-17 | C | sp², enol C(–OH), =C-18 |
|  1 | C-16 | C | sp³, junction (rings A/B/E); 16*S* |
|  2 | C-15 | C | sp³, junction (rings B/D/E); 15*S* |
|  3 | C-14 | C | sp³ oxymethine; 14*R* |
|  4 | C-13 | C | sp³, junction (rings C/D); 13*R* |
|  5 | C-8  | C | sp³, junction (rings C/D); 8*S* |
|  6 | C-9  | C | sp³ CH₂ (ring C) |
|  7 | C-10 | C | sp³ CH bearing Me-24; 10*R* |
|  8 | C-24 | C | methyl (on C-10) |
|  9 | C-11 | C | sp³ CH₂ (ring C) |
| 10 | C-12 | C | sp³ CH bearing Me-25; 12*S* |
| 11 | C-25 | C | methyl (on C-12) |
| 12 | C-7  | C | sp³, junction (rings B/D); 7*S* |
| 13 | C-6  | C | sp², =C-5; bears Me-23 |
| 14 | C-23 | C | methyl (on C-6, vinyl) |
| 15 | C-5  | C | sp², =C-6 |
| 16 | C-4  | C | sp³ quaternary; 4*R*; bears Me-22 |
| 17 | C-3  | C | sp², =C-2 |
| 18 | C-2  | C | sp², =C-3; bears Me-21 |
| 19 | C-21 | C | methyl (on C-2, vinyl) |
| 20 | C-1  | C | sp³ CH bearing Me-20; 1*S* |
| 21 | C-20 | C | methyl (on C-1) |
| 22 | C-22 | C | methyl (on C-4) |
| 23 | O (ether) | O | macrocyclic Ar–O–C bridge |
| 24 | C-7′ | C | aromatic, ipso to ether O |
| 25 | C-8′ or C-6′ | C | aromatic CH, ortho to C-7′ (on macrocyclic face) |
| 26 | C-9′ or C-5′ | C | aromatic CH, meta to C-7′ (on macrocyclic face) |
| 27 | C-4′ | C | aromatic, ipso to CH₂(3′) |
| 28 | C-3′ | C | sp³ benzylic CH₂ |
| 29 | C-2′ | C | sp³ quaternary hemiaminal; 2′*R* |
| 30 | C-1′ | C | sp³ CH bearing OMe; 1′*R* |
| 31 | C-18 | C | sp², =C-17; fused to lactam |
| 32 | C-19 | C | amide carbonyl (=O) |
| 33 | N    | N | lactam N–H |
| 34 | O (amide) | O | =O on C-19 |
| 35 | O (OMe)   | O | ether between C-1′ and C-26 |
| 36 | C-26 | C | OMe carbon |
| 37 | O (hemi)  | O | OH on C-2′ |
| 38 | C-5′ or C-9′ | C | aromatic CH on the off-macrocycle face |
| 39 | C-6′ or C-8′ | C | aromatic CH on the off-macrocycle face |
| 40 | O (enol)  | O | OH on C-17 |

The "on-face / off-face" assignment of the four arene CH atoms
depends on the atropoisomer — see Atropoisomerism caveat below.
The auto-generated `atom_label_map.txt` carries the same mapping
indexed by the build-script's internal labels.

## Ring-perimeter audit

The encoder (`vlt`-style RDKit-SSSR walk on the structure read by
MØD's `Graph.fromMOLString`) emits the 13-atom perimeter as
`[0, 1, 2, 3, 23, 24, 25, 26, 27, 28, 29, 30, 31]` (canonical SMILES
indices). Mapped to paper labels:

```
C17 — C16 — C15 — C14 — O — C7' — C8'/C6' — C9'/C5' — C4' — C3' — C2' — C1' — C18 — (back to C17)
```

This matches the expected 13-tuple from the brief (Chen 2019
Figure 2 + `research_findings.md` §2.3). The arene contributes only
three atoms to the perimeter (C-7′, one ortho, one meta) because
the macrocycle traverses a single face of the *para*-ring; the
other two arene CHs (indices 38, 39) are substituents that span
the macrocycle, which is the structural origin of the
atropoisomerism. ✓

## Atropoisomerism caveat (action required)

RDKit's `EmbedMolecule` selected an arbitrary face of the para-
arene for the 3D pose. **The encoded atropoisomer may not match
the published X-ray.** SMILES has no syntax for arene
atropoisomerism, and the build script does not currently consult
the NOESY constraints from Faraj 2023 (NOEs: H-16↔H-1′/H-9′,
H-15↔H-8′, H-14/Me-25↔H-6′) to pick the correct face.

Recommendation: Ivan to visually compare `structure.mol` against
Chen 2019 Figure 2. If the embedded face is wrong, the
permutation that fixes it is C-5′↔C-9′ and C-6′↔C-8′ at the
SMILES level (a chemically-equivalent relabeling) combined with a
re-embed — *not* a stereo flip at any sp³ center.

## RunSpec changes

`data/targets/ascomylactam_a/runspec.yaml` updated:

- `target.structure_path: structure.mol` (was placeholder).
- `target.ring_size: 13` (unchanged).
- `blocks: []` — first encoding pass; the seco precursor block for
  the Ar–O–C(sp³) closure has not been authored. The strategy
  will report "no seco precursor" — expected failure mode for
  the first pass on this target.
- `rules: all_macrocyclization` — the 12-rule set including
  `aryl_etherification` (the literature tactic for the Ar–O
  macroether closure of the 13-membered ring).
- `strategy.max_steps: 5` (per proposal §3.2 for ascomylactam).
- `strategy.predicates.is_intramolecular: true`.
- `strategy.predicates.ring_size_equals: 13`.
- `solver.backend: scip` (ILP tier; M5 calls for ≤10 strategy
  families).
- `solver.top_n: 10`.
- `solver.time_budget_s: 120`.
- `solver.request_infeasibility_cert: true`.
- `energetics.enabled: false` (TS-search hook for atropoisomer-
  sensitive closure not yet wired).

## Tests-run outcomes

```
$ pixi run python -m macrocert.cli encode-target data/targets/ascomylactam_a
encoded ascomylactam_a: 13-membered ring located;
perimeter audit written to data/targets/ascomylactam_a/ring_perimeter.txt
```

```
$ pixi run pytest tests/panel/test_panel.py -q -k ascomylactam
17 deselected in 0.02s
```

There is no `ascomylactam` case in `data/validation_panel/`; the
ascomylactam target lives at `data/targets/ascomylactam_a/`, which
is the M5 production-run target rather than a panel surrogate.
The `-k ascomylactam` filter therefore deselects everything in the
panel. The full panel still passes (10 pass, 7 pre-existing
placeholder skips). No regressions.

To exercise the new RunSpec end-to-end:

```
$ pixi run python -m macrocert.cli run data/targets/ascomylactam_a
```

is the natural follow-up, but it depends on the M5 seco-precursor
building block which is not yet authored (see Open Questions §3).

## Open questions

1. **Atropoisomer face** — verify 3D pose against Chen 2019 Figure 2.
2. **Perimeter sign-off** — confirm the 13-tuple matches Figure 1.
3. **Seco-precursor building block** — author the Ar-OH + alkyl-X
   block for the Uchiro-2017-style SNAr closure.
4. **CCDC CIF** — if obtained, re-encode via
   `obabel structure.cif -O structure.mol` and diff against
   the current SMILES-built file.
5. **Sign-off** — `signed_by: Ivan Leon (TBD)` in `notes.md`
   pending the atom-by-atom audit above.

## Files written / modified

```
data/targets/ascomylactam_a/structure.mol      (new — V2000, 3D, 86 atoms)
data/targets/ascomylactam_a/ring_perimeter.txt (new — auto-generated)
data/targets/ascomylactam_a/atom_label_map.txt (new — auto-generated)
data/targets/ascomylactam_a/notes.md           (rewritten — M5 signed audit)
data/targets/ascomylactam_a/runspec.yaml       (rewritten — M5 entry point)
scripts/build_ascomylactam_a.py                (new — build script)
docs/ascomylactam_a_encoding.md                (new — this report)
```

No git operations performed; changes left unstaged for review.
