# Validation-panel literature cases — chemistry-team TODO

Per the proposal §4.1 and the user's confirmed scope decision
(Comprehensive — 10+ cases), the v0 panel ships with **surrogate**
cases that exercise the runner, and a parallel set of literature
cases that the panel must eventually validate against. **Seven**
literature cases now have research briefs and scaffolded directories
(three from the 2026-05-24-morning research session, four from the
2026-05-24-afternoon expansion session); three more still need
similar treatment to hit the ≥10 cases the proposal calls for.

For each case, the chemistry team needs to:

1. Locate the deposited crystal structure (or supplementary Molfile)
   for the cyclized product.
2. Drop it at `data/validation_panel/<case>/structure.mol`.
3. Author `runspec.yaml` (model on existing cases) — specify ring
   size, blocks (acyclic precursors before the disconnection), the
   rule set, `strategy_predicates`, and any energetics gating.
4. Author `expected.yaml` declaring the literature tactic, AE class,
   and `expected_witness`.
5. Add a `notes.md` with the DOI and any encoding caveats.
6. Author `research_brief.md` (3 pages) following the format used in
   the existing scaffolded cases.

---

## Cases now scaffolded with research (2026-05-24) — awaiting Ivan sign-off on structure encoding

| Case directory | Tactic class | Ring size | Status |
| --- | --- | --- | --- |
| `vancomycin_cde_ring_boger_snar/` | **aryl_etherification** (rule does NOT yet exist) | 16 (C-O-D ring) | Brief + scaffold complete; `structure.mol` is PLACEHOLDER |
| `epothilone_b_nicolaou_rcm_1997/` | rcm | 16 | Brief + scaffold complete; `structure.mol` is PLACEHOLDER |
| ~~`citreoviridin_suh_imda_1985/`~~ | ~~transannular_diels_alder~~ | n/a | **REMOVED 2026-05-24** — slot was unfillable (citreoviridin is not macrocyclic; "Suh 1985" doesn't exist). Phoenix-Reddy cassaine 2008 substitutes the TDA slot; see below. Detailed diagnosis preserved in git history. |
| **`phoenix_reddy_cassaine_tda_2008/`** *(new)* | transannular_diels_alder | 14 (macrocyclic-triene precursor → 6-6-6 tricycle) | Brief + scaffold complete; `structure.mol` is PLACEHOLDER. **Substitutes the citreoviridin slot per the prior recommendation.** |
| **`corey_erythronolide_b_macrolactonization_1978/`** *(new)* | macrolactonization (Corey–Nicolaou activator) | 14 | Brief + scaffold complete; `structure.mol` is PLACEHOLDER. **Exercises the `Corey_Nicolaou` activator alternative in macrolactonization.meta.yaml.** |
| **`trost_bryostatin_analogue_rcm_2007/`** *(new)* | rcm | **31** (synthetic ring-expanded *analogue*, NOT natural bryostatin) | Brief + scaffold complete; `structure.mol` is PLACEHOLDER. **The natural bryostatin macrocycle has never been closed by RCM; this is the only published bryostatin-family RCM macrocyclization.** Ring-size outlier (31 vs. all-other 12–16); confirm panel rules accept ≥30. |
| **`haidle_myers_cytochalasin_b_2004/`** *(new)* | **TBD by Ivan** — ships as `transannular_diels_alder` (biomimetic IMDA interpretation) but the published Haidle-Myers chemistry is HWE (no macrocert rule exists) | 14 (cytochalasin B macrolactone) | Brief + scaffold complete; `structure.mol` is PLACEHOLDER. **TWO chemistry-error caveats vs. task brief: (1) cytochalasins B/D/E/H have macrolactones not macrolactams; (2) Haidle-Myers uses HWE, not macrolactamization.** Three decision options for Ivan in `haidle_myers_cytochalasin_b_2004/notes.md`. |

### Findings from the 2026-05-24 research sessions

**Morning session (vancomycin / epothilone B / citreoviridin):**

1. **Vancomycin is misclassified in the original task brief under "macrolactamization."** Vancomycin's macrocyclizations are biaryl ether SNAr (C-O-D, D-O-E, 16-membered each) and biaryl Suzuki (AB ring). The peptide bonds are made by amide coupling, not macrolactamization. The case is now under `aryl_etherification` per the corrected scaffold. The `aryl_etherification` rule still needs to be implemented in the rule library — marked TODO in the scaffolded expected.yaml.
2. **Epothilone B Nicolaou citation in the previous TODO was correct** (*JACS* 119:7974) — that is the B paper. The companion *JACS* 119:7960 is the A paper. Updated note in the scaffolded case files.
3. **Citreoviridin TDA slot is unfillable as named.** Citreoviridin is not macrocyclic (C₂₃H₃₀O₆ with a pyranone + tetrahydrofuran connected by a tetraene; PubChem CID 6436023, MW 402.48). The "Suh 1985" citation does not exist (Suh-Wilcox citreoviridin is **1988**, DOI `10.1021/ja00210a026`, and uses no Diels-Alder). The "Trost 1985" citation also does not exist in CrossRef/PubMed. **Recommended substitution: (+)-cassaine via TDA (Phoenix-Reddy-Deslongchamps, *JACS* **2008**, *130*, 13989, DOI `10.1021/ja805097s`)** — now scaffolded at `phoenix_reddy_cassaine_tda_2008/`.

**Afternoon session (bryostatin / cytochalasin / erythronolide / cassaine):**

4. **Bryostatin RCM premise is partially wrong.** The task brief lists Wender 2008/2011, Trost 2008, and Keck 2011 as bryostatin-RCM total syntheses. None of them uses RCM at the macrocyclic ring level: Wender 2011 uses Yamaguchi + Prins (DOI `10.1021/ja203034k`); Trost 2008/2010 uses Ru–Pd–Au cascade (DOI `10.1038/nature07543` + `10.1021/ja105129p`); Keck 2011 uses Yamaguchi + Rainier. **The natural-product bryostatin macrocycle has never been closed by RCM** (the C16–C17 *trans*-trisubstituted alkene is too hindered). **The only published bryostatin-family RCM macrocyclization is the Trost-Yang-Thiel-Frontier-Brindle 2007 ring-expanded analogue (DOI `10.1021/ja067305j`, full paper 2011 *Chem. Eur. J.* DOI `10.1002/chem.201002932`)** — 31-membered, 80% yield, 1:1 E:Z, Grubbs-Hoveyda 2nd-gen. Scaffolded at `trost_bryostatin_analogue_rcm_2007/`.
5. **Cytochalasan macrolactam premise is wrong.** Cytochalasins B, D, E, H do NOT have macrolactam closures — their macrocycle is a 14-membered macrolactone (B, D) or 11-membered macrocarbocycle (E, H, L-696,474). The only lactam in any of these compounds is the 5-membered isoindolone γ-lactam, which is too small for macrocert's `macrolactamization` rule. Furthermore, **Haidle-Myers 2004 closes the cytochalasin B macrocycle by intramolecular HWE olefination, not by macrolactamization**, and macrocert v0 has NO HWE rule. The `haidle_myers_cytochalasin_b_2004/` scaffold ships with three decision options for Ivan (notes.md "Decision flag for Ivan").
6. **Skellam 2017 DOI correction.** Task brief cites `10.1039/c7np00045f`. CrossRef resolves that DOI to "Appreciation of symmetry in natural product synthesis" by Bai & Wang (a different 2017 *Nat. Prod. Rep.* paper). The actual Skellam 2017 cytochalasan biosynthesis review is at DOI `10.1039/c7np00036g`. Updated throughout.
7. **Erythronolide B Corey 1978 DOI correction.** Task brief cites `10.1021/ja00482a075`, which CrossRef cannot resolve. The correct DOI for Corey's erythronolide B macrolactonization paper is **`10.1021/ja00482a063`** (Part 4 of the erythromycin synthesis series, pp 4620–4622). The DOI `10.1021/ja00482a062` (Part 3, pp 4618–4620) is the *fragment-synthesis* paper, not the macrolactonization paper. The page "4618" from the brief is the first page of Part 3. Scaffolded at `corey_erythronolide_b_macrolactonization_1978/`. Exercises the `Corey_Nicolaou` activator alternative in `data/rules/macrolactonization.meta.yaml`.
8. **"Bérubé-Deslongchamps 1987" author attribution is wrong.** The 1987 *Tet. Lett.* 28:5249 paper is by **Baettig, Dallaire, Pitteloud, Deslongchamps** (cis-trans-trans 13-membered trienone). The *Bérubé*-Deslongchamps paper in the same issue is at pp 5255–5258 (DOI `10.1016/S0040-4039(00)96701-7`, tetrasubstituted enol-ether dienophile variant). Three back-to-back Deslongchamps-group TDA papers fill *Tet. Lett.* 28:5249–5258. Phoenix-Reddy 2008 was preferred over any of these methodology papers because it is a real natural-product total synthesis.

---

## Macrolactamization class (target: 3 cases) — corrected

- ~~**Vancomycin macrocyclic core**, Boger 1999 (SNAr-equivalent ring closure).~~ — **MOVED to `aryl_etherification` class**; this is not macrolactamization. See `vancomycin_cde_ring_boger_snar/` for the scaffolded version.
- **Epothilone B amide variant**, Nicolaou — note the natural product is a *lactone*, not a lactam. The amide variant exists as a class of epothilone *analogs* (ixabepilone is the FDA-approved amide variant). For a true macrolactamization case from the Nicolaou group, see *Angew. Chem. Int. Ed.* **1998**, *37*, 2014 family for the lactam-analog series.
- ~~**Cytochalasin B-class macrolactam**, biosynthesis-aligned. Reference: Skellam E. *Nat. Prod. Rep.* 2017.~~ — **PREMISE WRONG; see finding 5 above and `haidle_myers_cytochalasin_b_2004/research_brief.md`**. Cytochalasin B has a macrolactone (not macrolactam) and Haidle-Myers uses HWE (no macrocert rule). The slot is scaffolded under `transannular_diels_alder` (biomimetic IMDA interpretation per Skellam 2017), but Ivan must sign off on the tactic-class call.
- **(third macrolactamization slot)** — pick from the Acc. Chem. Res. 2021 review.

## Aryl-etherification class (NEW — proposed; rule library TODO)

- **Vancomycin C-O-D ring** — `vancomycin_cde_ring_boger_snar/` (scaffolded, awaiting Ivan).
- **Vancomycin D-O-E ring** (Boger 1999 second SNAr) — sibling case to encode next.
- **K-13 or OF4949-III** (Janetka & Rich 1997, DOI `10.1002/chin.199745228`) — SNAr biaryl ether macrocyclization, classic Boger/Zhu literature.

## RCM class (target: 2-3 cases)

- **Epothilone B (Nicolaou 1997 RCM)** — `epothilone_b_nicolaou_rcm_1997/` (scaffolded, awaiting Ivan).
- **Bryostatin RCM** — `trost_bryostatin_analogue_rcm_2007/` (scaffolded, awaiting Ivan). **Synthetic ring-expanded ANALOGUE, not natural bryostatin; 31-membered macrocycle (outlier).**
- **Curacin A** as an unsymmetric RCM substrate — *third RCM slot still needed.*

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

- ~~**Citreoviridin** TDA, Suh 1985 (*Tetrahedron Lett.* 26:1497).~~ — **REMOVED**: citreoviridin is not macrocyclic, no Suh 1985 paper exists, no citreoviridin synthesis uses TDA. See `citreoviridin_suh_imda_1985/research_brief.md` for the full diagnosis. Replaced by:
- **(+)-Cassaine via TDA** — `phoenix_reddy_cassaine_tda_2008/` (scaffolded, awaiting Ivan). 14-membered macrocyclic triene → trans-decalin steroid framework. DOI `10.1021/ja805097s`. **NB: "Bérubé" attribution in the original brief is wrong — the 1987 *Tet. Lett.* 28:5249 paper is by Baettig-Dallaire-Pitteloud-Deslongchamps (cis-trans-trans 13-mem trienone).**
- **Bérubé-Deslongchamps methodology** (Tet. Lett. **1987**, *28*, **5255–5258**, DOI `10.1016/S0040-4039(00)96701-7`) — 13-membered triene with *tetrasubstituted enol ether* dienophile. Sibling reference, not panel-worthy as a total-synthesis target.
- **Cytochalasin B (biomimetic IMDA interpretation)** — `haidle_myers_cytochalasin_b_2004/` (scaffolded, awaiting Ivan). Tactic-class interpretation requires Ivan's call (TDA, infeasible, or new-rule); see notes.md.
- **Norzoanthamine** TDA, Miyashita 2004.
- **FR901483** synthesis TDA, Snider 2001.

## Macrolactonization (target: 2 cases — proposal §2.2 includes the lactone class)

- **Erythronolide B macrolactonization** (Corey 1978) — `corey_erythronolide_b_macrolactonization_1978/` (scaffolded, awaiting Ivan). **Exercises the `Corey_Nicolaou` activator alternative in macrolactonization.meta.yaml.** DOI `10.1021/ja00482a063`.
- **Megalomicin macrolactone**, more recent Yamaguchi case (Evans, Martin, or Hung-Yi Lee group). *Still needed.*
- **Amphotericin macrolactone** (Nicolaou 1987 *Angew. Chem.* DOI `10.1002/anie.198708231`) — alternative third slot.

## Acceptance per case

Each case PASSES the panel if `pipeline.run` returns
`witness == optimal` with the literature `tactic` in the top-N route's
rule class, and the AE class matches the expected band. Failures are
diagnosed per the panel REPORT.md taxonomy.

Until the chemistry team encodes these, M5 (full ascomylactam run)
cannot claim retrodictive validation backed by these references — the
v0 surrogate cases calibrate the infrastructure but do not substitute
for the literature panel.

## Remaining work (≥ 3 cases to hit ≥10 literature panel)

After the seven scaffolded cases above are signed off by Ivan, the
panel still needs the following minimum coverage to claim retrodictive
validation:

1. **Vancomycin D-O-E ring** (sibling to the C-O-D case, Boger 1999) — aryl_etherification.
2. **K-13 / OF4949-III** (Janetka & Rich 1997, DOI `10.1002/chin.199745228`) — aryl_etherification.
3. **Curacin A RCM** OR another modern RCM total synthesis — rcm. Third RCM slot.
4. **Megalomicin macrolactone** OR Amphotericin macrolactone (Nicolaou 1987) — macrolactonization. Second macrolactonization slot.
5. **Norzoanthamine TDA** (Miyashita 2004) OR FR901483 TDA (Snider 2001) — third transannular_diels_alder slot.

Each one needs the same scaffold: research brief, runspec, expected, notes, structure.mol (placeholder + Ivan's audit).

## Citation graph nodes

The 2026-05-24 research sessions created the following external paper
nodes in the vault knowledge graph (`~/Obsidian/zen/.vault/vault.db`):

**Morning session (2026-05-24-AM):**

- `n_01kscgvfnz6fenj9ec18x7q5qm` — Boger et al. 1999, *JACS* 121:10004 (vancomycin aglycon)
- `n_01kscgvj761pr7fnq83ebqtx9t` — Nicolaou et al. 1997, *JACS* 119:7974 (epothilone B RCM)
- `n_01kscgvm8y95t0dvmb7g4pe49e` — Suh & Wilcox 1988, *JACS* 110:470 (citreoviridin — reference for the *misnamed* slot)
- `n_01kscgvn436cgvqjcx6knqq3t5` — Bérubé & Deslongchamps 1987, *Tet. Lett.* 28:5249 (TDA founding precedent; candidate replacement)

**Afternoon session (2026-05-24-PM):**

- `n_01kscj9znmrx4gzvj0c7e9mv9z` — Phoenix-Reddy-Deslongchamps 2008, *JACS* 130:13989 (cassaine TDA, replaces citreoviridin slot)
- `n_01kscja1wvz37mkdm33jaztqs8` — Corey et al. 1978, *JACS* 100:4620 (erythronolide B macrolactonization, Part 4)
- `n_01kscja37ye0jqwcxg4fz0hpdg` — Trost-Yang-Thiel-Frontier-Brindle 2007, *JACS* 129:2206 (bryostatin analogue RCM)
- `n_01kscja4dzajxxen5ag7rx0ye4` — Haidle-Myers 2004, *PNAS* 101:12048 (cytochalasin B / L-696,474 HWE macrocyclization)
- `n_01kscjaatg9mk3kby3tc38bcz4` — Skellam 2017, *Nat. Prod. Rep.* 34:1252 (cytochalasan biosynthesis review; **corrected DOI `10.1039/c7np00036g`**)
- `n_01kscjaav049j6kr32ze8cb6wg` — Corey-Nicolaou 1974, *JACS* 96:5614 (PySSPy/PPh₃ macrolactonization methodology paper)
- `n_01kscjaave1nkwfavrh65kp4gz` — Trost-Yang-Dong 2011, *Chem. Eur. J.* 17:9789 (bryostatin analogue full paper)
