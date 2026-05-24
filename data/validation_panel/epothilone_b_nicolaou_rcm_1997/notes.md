# epothilone_b_nicolaou_rcm_1997

**STATUS: Encoded.** structure.mol holds the post-RCM intermediate
(12,13-deepoxy epothilone B), authored by
`scripts/build_epothilone_b_rcm.py`. Seco-precursor authored by
`scripts/build_epothilone_seco.py`.

## Provenance

- Primary reference: Nicolaou, K. C.; Ninkovic, S.; Sarabia, F.;
  Vourloumis, D.; He, Y.; Vallberg, H.; Finlay, M. R. V.; Yang, Z.
  *J. Am. Chem. Soc.* **1997**, *119*, 7974–7991. DOI `10.1021/ja971110h`.
- Companion paper (epothilone A, RCM route):
  *J. Am. Chem. Soc.* **1997**, *119*, 7960–7973. DOI `10.1021/ja971109i`.
- *Nature* report (A + B): *Nature* **1997**, *387*, 268–272.
  DOI `10.1038/387268a0`.
- Structural reference (natural product): ChEBI:31550, LIPID MAPS
  LMPK04000041, NP-MRD NP0013985.

## Encoding choice — deepoxy intermediate, not natural product

The macrocyclization step (RCM) produces the **12,13-deepoxy
intermediate**, NOT epothilone B itself. The natural-product
C12–C13 epoxide is installed *after* RCM via a separate DMDO /
m-CPBA epoxidation. We encode the deepoxy form to match the actual
macrocyclization product whose closure the rule library is asked
to recognise.

Cyclized target (encoded in `structure.mol`):

- Formula: C27H41NO5S (MW exact 491.27, average 491.69)
- Rings: one 16-membered macrolactone + one 5-membered thiazole
- 5 sp3 stereocenters: C3 *S*, C6 *R*, C7 *S*, C8 *S*, C15 *S*
- In-ring C12=C13 alkene: **Z** (the desired RCM geometry)
- Exocyclic C16=C17 vinyl tether to thiazole: **E** (unchanged)
- Canonical isomeric SMILES (see `canonical_smiles.txt`):
  `C/C1=C/C[C@H](/C(C)=C/c2csc(C)n2)OC(=O)C[C@H](O)C(C)(C)[C@@H](O)[C@H](C)C(=O)[C@@H](C)CCC1`

The natural-product epothilone B itself (with epoxide) is
referenced for provenance but NOT the panel target — see
research_brief.md §5 (Option A vs. Option B) and §7.

## Seco-precursor

Authored by `scripts/build_epothilone_seco.py`. The cyclized
deepoxy alkene is opened at the C12=C13 bond and each side capped
with a terminal CH2=, giving the α,ω-diene that Grubbs G1
metathesises. The macrolactone ester (C1–O–C15) is retained
because the molecule does not fall apart on alkene cleavage —
Nicolaou's actual seco-acid is already esterified before RCM
(macrolactonization first, RCM second in their scheme).

Mass balance:

| Species   | Formula      | Exact MW    |
| --------- | ------------ | ----------- |
| Cyclized  | C27H41NO5S   | 491.2705    |
| Seco      | C29H45NO5S   | 519.3018    |
| Δ MW      | ─            | 28.0313     |
| Ethylene  | C2H4         | 28.0313     |

Δ MW matches ethylene exactly (verified in build script). Block
SMILES:

```
C=CC[C@@H](OC(=O)C[C@H](O)C(C)(C)[C@@H](O)[C@H](C)C(=O)[C@@H](C)CCCC(=C)C)/C(C)=C/c1csc(C)n1
```

Building block file: `data/building_blocks/epothilone_seco.yaml`.

## E/Z selectivity caveat

Nicolaou's actual RCM on the bare epothilone B substrate (with
the C8 methyl group corresponding to the B-series) gives ~1:1 Z:E.
The desired Z isomer is separated chromatographically before the
DMDO epoxidation that delivers the natural product. The panel rule
`rcm` is selectivity-agnostic in v0; the runspec's
`enforce_ez_geometry: {rcm: Z}` predicate (Workstream D phase 2)
constrains the certificate to the literature-favoured Z geometry
on the C12=C13 in-ring alkene. If this predicate filters out RCM
entirely on the first run (e.g. because the post-closure alkene
geometry is not detected), drop it and document the failure.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1021/ja971110h`, `10.1021/ja971109i`,
  `10.1038/387268a0`, `10.1002/anie.199701661`,
  `10.1002/anie.199623991`, `10.1021/ja971946k`).
- Structural data: ChEBI:31550, LIPID MAPS LMPK04000041,
  IUPHAR Guide to Pharmacology ligand 13600, NP-MRD NP0013985,
  Sigma-Aldrich E2656, PubChem CID 448799 — all mutually consistent
  on the natural-product structure.
- Selectivity data: Nicolaou JACS 119:7974 SI; corroborated in 2011
  Hoveyda/Schrock review (PMC3211109) — 23:77 Z:E for one Grubbs 2a
  variant of the substrate, 77% E with Grubbs 2a; original Grubbs G1
  in Nicolaou's hands gives ~1:1.

## Citation correction

The user task brief cited "JACS 1997, 119:7960" as the epothilone B
paper; that page is the *epothilone A* RCM paper. The B paper
follows immediately at p. 7974 in the same JACS issue
(DOI `10.1021/ja971110h`). The expected.yaml and runspec reference
the corrected B-paper citation.
