# Toy target — 13-membered macrolactam from 12-aminododecanoic acid

A minimal viable target for exercising the Layer A → B → C pipeline
without depending on the gated ascomylactam A crystal structure.

- **Seco precursor**: 12-aminododecanoic acid, `H2N-(CH2)11-COOH`
  (SMILES `OC(=O)CCCCCCCCCCCN`).
- **Product**: 13-membered macrolactam, ring formed by N attacking C=O
  of the same molecule (`O=C1CCCCCCCCCCCN1`).
- **Byproduct**: H₂O.

This is exactly the kind of substrate that pre-1990 lactam-fiber
chemistry would have considered routine — but it serves as a clean
test case for the verifier's atom-balance arithmetic and for the M1
DG-visualization exit.

The "structure" file is a Molfile written by RDKit, not a deposited
X-ray. This is permissible *for the toy* because there is no novel
chemistry being claimed; for the real ascomylactam A target the source
must be the crystal data, per proposal §2.1.
