# Ascomylactam A — target encoding (M1 placeholder, full encoding in M5)

## Source

**Primary**: Chen, Y. *et al.* *J. Nat. Prod.* **82**, 1752–1758 (2019).
DOI: [10.1021/acs.jnatprod.8b00918](https://doi.org/10.1021/acs.jnatprod.8b00918).

Per proposal §2.1, the structure (specifically the **exact ring membership of
the 13-membered perimeter**, including heteroatom positions and absolute
configuration set by the deposited X-ray) must come from the crystal data,
not from the cytochalasan class.

## Status

`structure.mol` is **not yet written**. The ACS supporting-information PDF
and the deposited CCDC entry are both behind paywalls (verified
`HTTP 403` on `pubs.acs.org/doi/suppl/.../np8b00918_si_001.pdf` and the
CCDC search interface gating the actual CIF download). Two paths to
resolve in time for the M5 ascomylactam run:

1. **Institutional access** to the ACS SI PDF: extract the embedded CIF
   block (Chen 2019 reports single-crystal X-ray and customarily attaches
   the .cif as ASCII text in the SI). Convert to `structure.mol` via
   `obabel ascomylactam_a.cif -O structure.mol`.
2. **CCDC direct request**: the CSD deposition number associated with
   this paper, once located, can be requested via the CCDC web form
   even without a subscription (free for "structure on request").
   Reference: <https://www.ccdc.cam.ac.uk/structures/search?DOI=10.1021/acs.jnatprod.8b00918>.

Once `structure.mol` is in place, run

```
pixi run encode-target data/targets/ascomylactam_a
```

which writes `ring_perimeter.txt` listing the 13-ring atoms for the
synthetic-chemist team member to sign off against Figure 2 / Table 1 of
the paper.

## Why this is a hard block, not a "we'll figure it out"

A misencoded perimeter (e.g., a 12-ring instead of 13, or an O where N
sits) will silently corrupt every certificate the pipeline emits for
this target. The ground-truth structure is the formal "goal" in the
proposal's Lean analogy — getting it wrong is equivalent to stating the
wrong theorem.

## Surrogate for M1 exit

For the M1 exit criterion ("generated network for one disconnection
family, visualized"), see `data/targets/toy_macrolactam/`. The toy is a
13-membered lactam built from one amine arm + one carboxylic-acid arm —
sufficient for end-to-end DG generation without depending on the gated
ascomylactam structure.
