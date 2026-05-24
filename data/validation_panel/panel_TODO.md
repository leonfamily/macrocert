# Validation-panel literature cases — chemistry-team TODO

Per the proposal §4.1 and the user's confirmed scope decision
(Comprehensive — 10+ cases), the following literature macrocyclizations
need to be encoded by the synthetic-organic-chemistry team member
before the M5 ascomylactam run. The v0 panel ships with surrogate
cases that exercise the runner; these are the literature targets the
panel must eventually validate against.

For each case the chemistry team needs to:
1. Locate the deposited crystal structure (or supplementary Molfile)
   for the cyclized product.
2. Drop it at `data/validation_panel/<case>/structure.mol`.
3. Author `runspec.yaml` (model on existing cases) — specify ring size,
   blocks (acyclic precursors before the disconnection), the rule set,
   and any energetics gating.
4. Author `expected.yaml` declaring the literature tactic, AE class,
   and `expected_witness`.
5. Add a `notes.md` with the DOI and any encoding caveats.

## Macrolactamization class (target: 3 cases)

- **Vancomycin macrocyclic core**, Boger 1999 (SNAr-equivalent ring
  closure). Reference: Evans D. A. & Boger D. L.
- **Epothilone B macrolactamization variant**, Nicolaou. Reference:
  Nicolaou K. C., *Angew. Chem. Int. Ed.* 1998.
- **Cytochalasin B-class macrolactam**, biosynthesis-aligned.
  Reference: Skellam E. *Nat. Prod. Rep.* 2017.

## RCM class (target: 2-3 cases)

- **Epothilone B (Nicolaou 1997 RCM)**, *J. Am. Chem. Soc.* 119:7974.
- **Bryostatin RCM closure**, Trost group ca. 2008.
- **Curacin A** as an unsymmetric RCM substrate.

## Transannular / intramolecular Diels–Alder (target: 2-3 cases)

> **v0 status**: No surrogate TDA case ships in the v0 panel. A first
> attempt (`tda_macrocyclic_triene_dienophile` substrate
> `C=CC=CCCCCCCCCC=CC(=O)OC`) was removed because the TDA rule
> intramolecularly produced a fused bicyclic 6/n product rather than
> the expected macrocyclic ring closure — designing a substrate whose
> intramolecular [4+2] *cleanly* closes a 13-membered carbocycle
> requires chemistry-team input on diene/dienophile geometry,
> preorganization, and tether length. v0 panel calibrates τ on the
> H₂O- and ethylene-byproduct classes only; the zero-byproduct TDA
> class is calibrated when a literature substrate lands here.


- **Citreoviridin** TDA, Suh 1985 (*Tetrahedron Lett.* 26:1497).
- **Norzoanthamine** TDA, Miyashita 2004.
- **FR901483** synthesis TDA, Snider 2001.

## Macrolactonization (target: 2 cases — proposal §2.2 includes the lactone class)

- **Erythronolide B macrolactonization** (Corey 1979 or Yamaguchi 1981).
- **Megalomicin macrolactone**, more recent Yamaguchi case.

## Acceptance per case

Each case PASSES the panel if `pipeline.run` returns
`witness == optimal` with the literature `tactic` in the top-N route's
rule class, and the AE class matches the expected band. Failures are
diagnosed per the panel REPORT.md taxonomy.

Until the chemistry team encodes these, M5 (full ascomylactam run)
cannot claim retrodictive validation backed by these references — the
v0 surrogate cases calibrate the infrastructure but do not substitute
for the literature panel.
