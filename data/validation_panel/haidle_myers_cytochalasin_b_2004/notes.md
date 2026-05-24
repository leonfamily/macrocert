# haidle_myers_cytochalasin_b_2004

**STATUS: Awaiting Ivan sign-off on tactic-class decision AND structure encoding.**

This case has two interpretive gaps that need Ivan's call. The
research_brief.md §7 documents them in detail; the short summary:

1. **Cytochalasins B, D, E, H do NOT have macrolactam closures.** Their macrocycle is a *macrolactone* (B, D) or *macrocarbocycle* (E, H, L-696,474). The only lactam is the 5-membered isoindolone γ-lactam, too small for macrocert's `macrolactamization` rule.
2. **The Haidle-Myers 2004 synthesis uses intramolecular HWE olefination** to close the macrocyclic alkene. Macrocert v0 does NOT have an HWE rule. Closest existing rule: `transannular_diels_alder` (interpreted as the biomimetic IMDA route per Skellam 2017's biosynthesis review), but this is a stretch.

## Provenance

- **Primary total synthesis:** Haidle, A. M.; Myers, A. G. *Proc. Natl. Acad. Sci. USA* **2004**, *101*, 12048–12053. DOI `10.1073/pnas.0402111101`. PMC: PMC514432 (open access). 24-step longest linear sequence (4.6% yield from aldehyde 7); macrocyclization by intramolecular HWE.
- **Cytochalasan biosynthesis review (corrected DOI):** Skellam, E. *Nat. Prod. Rep.* **2017**, *34*, 1252–1263. DOI `10.1039/c7np00036g`. **NOT `10.1039/c7np00045f` as in the task brief.** 157 citations per CrossRef snapshot.
- **Cytochalasin D Thomas synthesis:** Merifield, E.; Thomas, E. J. *J. Chem. Soc., Perkin Trans. 1* **1999**, 3269–3283. DOI `10.1039/a906412e`.
- **Cytochalasin H Thomas synthesis:** Thomas, E. J.; Whitehead, J. W. F. *J. Chem. Soc., Perkin Trans. 1* **1989**, 507–518. DOI `10.1039/p19890000507`.
- **Recent cytochalasan review:** Mohammed *et al.* *Nat. Prod. Rep.* **2025**. DOI `10.1039/D4NP00076E`.
- **Cytochalasin B structural data:** PubChem CID 5311281; ChEBI:23528; CAS 14930-96-2.

## Encoding caveats — long list

1. **Citation correction.** Skellam 2017 *Nat. Prod. Rep.* DOI: the correct DOI is `10.1039/c7np00036g`. The task brief and panel_TODO.md cite `10.1039/c7np00045f`, which CrossRef resolves to a different 2017 *Nat. Prod. Rep.* paper (Bai & Wang on symmetry in natural-product synthesis).
2. **Chemistry error in task brief 1:** "Cytochalasins B, D, E, H have macrolactam closures" — this is factually wrong. Cytochalasin B's macrocycle is a 14-membered *macrolactone*, not a macrolactam. The γ-lactam in the isoindolone is the only nitrogen-containing ring, and it is 5-membered (too small for macrocert's macrolactamization rule).
3. **Chemistry error in task brief 2:** "biomimetic macrolactam class flag in macrolactamization.meta.yaml was added for this family" — the flag is plausibly intended for the *biosynthetic* PKS-NRPS amide bond, but that bond is the 5-membered γ-lactam, not a macrolactam. To fire macrocert's macrolactamization rule, the substrate must be a >12-membered seco-amino-acid; the cytochalasan biosynthetic step is γ-lactamization. The class flag may need re-targeting (e.g., to the *macrolactam* products of related fungal natural products like the chaetoglobosin or aspochalasin subfamilies, which have larger amide-containing macrocyclic ring systems via additional ring fusion).
4. **Haidle-Myers 2004 macrocyclization mechanism:** intramolecular HWE olefination. Forms a C=C alkene, expels dialkyl phosphate anion (~125 g/mol for dimethyl phosphate). Macrocert v0 has no HWE rule.
5. **Recommended tactic class: `transannular_diels_alder`** (biomimetic IMDA interpretation per Skellam 2017's biosynthesis mechanism). This is consistent with the `biomimetic_macrocyclization` rule set in `data/rules/_index.yaml` (which lists `transannular_diels_alder` alongside `macrolactamization`).
6. **Alternative tactic class: mark as `infeasible`** (cf. citreoviridin diagnostic case) until a new HWE rule is added to macrocert.
7. **Ring size:** 14 (cytochalasin B macrolactone) is the largest cytochalasin macrocycle. L-696,474 is 11-membered.
8. **Stereocenters:** 7 sp³ stereocenters; full stereodescriptor (1*S*,5*S*,6*R*,7*R*,8*S*,11*S*,13*E*,15*S*,16*E*,18*R*) per PubChem CID 5311281.
9. **structure.mol is a PLACEHOLDER.** PubChem CID 5311281 Molfile is the recommended source. Ivan to audit before commit. McLaughlin 1974 X-ray (CCDC) is the canonical 3D structure if Ivan has CCDC access.

## Decision flag for Ivan

Pick one of:

- **(a) TDA interpretation:** `literature_tactic: transannular_diels_alder`, `expected_witness: optimal`, reference Skellam 2017 biosynthesis. The panel runs the TDA rule on a biomimetic macrocyclic-triene precursor (not Haidle-Myers's actual HWE substrate); justification = `biomimetic_macrocyclization` rule set.
- **(b) Infeasible interpretation (cf. citreoviridin):** `literature_tactic: macrolactamization` (per task brief), `expected_witness: infeasible`, document the chemistry mismatch (HWE vs. lactam closure, γ-lactam vs. macrolactam) and recommend that a new HWE rule be implemented in v1 OR that this slot be reassigned to a different cytochalasan-family compound where a macrocert-supported rule actually fires.
- **(c) New rule + later case:** defer this slot; implement an HWE rule in `data/rules/horner_wadsworth_emmons.{gml,meta.yaml}`; redo the case after the rule lands. This is the most honest option but slowest.

This scaffold ships with option **(a)** (TDA interpretation per the biomimetic class) so that the panel runner has something to run; Ivan can switch to (b) or (c) by editing `expected.yaml` and `runspec.yaml`.

## Sources cross-referenced

- DOI metadata: CrossRef (`10.1073/pnas.0402111101`, `10.1039/c7np00036g`, `10.1039/a906412e`, `10.1039/p19890000507`, `10.1039/p19890000525`, `10.1039/D4NP00076E`, `10.1002/ange.202102831`).
- Structural data: PubChem CID 5311281, ChEBI:23528 — mutually consistent (C₂₉H₃₇NO₅, MW 479.6 g/mol, CAS 14930-96-2).
- Mechanism (HWE in Haidle-Myers): PMC PMC514432 full text Fig. 2; Skellam 2017 §3 (biosynthesis mechanism); the more recent Mohammed 2025 *Nat. Prod. Rep.* review.
- Cytochalasin family ring-size table: Haidle-Myers 2004 Fig. 1 — macrolactone (14, cytochalasin B), macrocarbocycle (11, L-696,474), variant with carbonate (cytochalasin E).
