# MØD-MacroCert Research Proposal

**Audience.** The 4-role team named in `proposal.md` §5:

- **F** — graph-rewriting / formal-methods engineer
- **C** — computational chemist
- **I** — cheminformatics engineer
- **S** — synthetic-organic chemist (domain authority, human-in-the-loop)

**Scope.** The codebase at this commit
(`git log --oneline | head -1`) ships the entire mechanization
harness: Layers A–E, an independent verifier, dual ILP backends, a
content-addressed energetics cache, a validation-panel runner, and
report rendering. **What it lacks is chemistry domain content**: a
correctly encoded ascomylactam A target, a literature validation
panel, a finished rule library, properly designed strategies, a Layer
D protocol calibrated against real chemistry, and stereo annotations
on the rules. This document specifies that work as six concurrent
workstreams with named deliverables, owners, acceptance criteria, and
dependencies.

**What this proposal is not.** It is not a request to refactor or
extend the harness. The harness is the constant; the chemistry is the
variable. If a workstream finds a structural defect in the harness,
that becomes an engineering ticket on **F** / **I**, not a goal of this
proposal.

---

## Workstream A — Encode the ascomylactam A target

**Owner:** S (primary), I (supporting)
**Blocks:** every other workstream's M5 integration. Highest priority.
**Status:** placeholder at `data/targets/ascomylactam_a/` documents the
blocker; the encoder will refuse to run until `structure.mol` is in
place — this is intentional per proposal §2.1.

### Deliverable

`data/targets/ascomylactam_a/structure.mol` — strict V2000 Molfile
encoding the experimentally determined connectivity, stereochemistry,
and absolute configuration of ascomylactam A as deposited by Chen
et al. 2019.

Plus `data/targets/ascomylactam_a/ring_perimeter.txt` — auto-generated
by the encoder, **manually reviewed and signed** by S against Figure 2
and Table 1 of the paper, with one comment line per atom recording the
correspondence between MØD's atom index and the published atom label.

### Inputs the team must obtain

1. Chen, Y. *et al.*, *J. Nat. Prod.* **82**, 1752–1758 (2019).
   DOI: `10.1021/acs.jnatprod.8b00918`.
2. Either the ACS supplementary-information PDF (institutional access
   required; HTTP 403 confirmed without it), or the CCDC deposition
   associated with the paper (free "structure on request" form at
   <https://www.ccdc.cam.ac.uk/structures/>).
3. If only the published 2D figure is available: an independent
   cross-check of every ring atom against the X-ray-derived bond
   table; S signs off in `notes.md`.

### Acceptance

```bash
pixi run python -m macrocert.cli encode-target data/targets/ascomylactam_a
```

emits a 13-atom perimeter file, S countersigns it, and the file is
committed.

### Risks

- Misencoded perimeter silently corrupts every downstream certificate
  for this target. Verifier cannot catch this — it can only check
  internal consistency, not the encoder's correspondence to reality.
- S must verify *connectivity, ring size, heteroatom positions, and
  stereochemistry* independently of the SMILES.

---

## Workstream B — Literature validation panel

**Owner:** S (primary), C (energetics annotation), I (supporting)
**Tracked at:** `data/validation_panel/panel_TODO.md`
**Status:** 6 surrogate cases ship (ω-aminoacid lactams + α,ω-diene
RCMs). The literature cases that close the proposal §4.1 retrodictive-
validity claim are open.

### Deliverable

Ten or more cases under `data/validation_panel/<case>/` covering the
five tactic classes the rule library targets, drawn from the macrocyclization reviews cited in the proposal:

- Martí-Centelles *et al.*, *Chem. Rev.* (2015) — preorganization
- *Acc. Chem. Res.* (2021) DOI:10.1021/acs.accounts.0c00759 — post-cyclization strategies
- *ACS Cent. Sci.* (2020) DOI:10.1021/acscentsci.0c00599 — unconventional macrocyclizations
- *Nat. Prod. Rep.* (2019) DOI:10.1039/c8np00094h — stereoconfining macrocyclizations

For each case:

```
data/validation_panel/<case>/
    structure.mol         deposited crystallographic structure of the product
    runspec.yaml          declares ring_size, blocks, rules, AE threshold
    expected.yaml         declares literature_tactic + ae_class + reference DOI
    notes.md              encoding caveats, S sign-off
```

### Target case set (S to refine; *italics* = chemistry-team choice)

- **Macrolactamization (3 cases):** vancomycin macrocyclic core
  (Boger SNAr), epothilone B amide variant (Nicolaou), one
  cytochalasan family member (Skellam 2017 review).
- **RCM (3 cases):** Nicolaou's epothilone B closure
  (*JACS* 1997), bryostatin RCM segment, *and one more S-selected*.
- **Transannular / IM Diels–Alder (2 cases):** citreoviridin (Suh 1985),
  *and one more S-selected from norzoanthamine, FR901483, or
  endiandric acid*.
- **Macrolactonization (2 cases):** erythronolide B (Corey 1979 or
  Yamaguchi 1981), *and one more S-selected from the
  megalomicin / amphotericin family*.

### Acceptance

```bash
pixi run pytest tests/panel/      # ≥ 80% pass rate per the plan
pixi run python scripts/calibrate_panel.py
```

`data/validation_panel/REPORT.md` is regenerated with non-trivial AE
distributions per tactic. S signs off `notes.md` for each case.

Each non-passing case is triaged in `REPORT.md` per the taxonomy:
*rule-library gap* → C/F own; *strategy gap* → F owns;
*τ miscalibration* → revise threshold in the report;
*encoding error* → S owns.

### Dependency

Workstream C (macrolactonization rule) is a prerequisite for the
macrolactonization panel cases.

---

## Workstream C — Rule library expansion

**Owner:** S (chemistry), F (DPO encoding)
**Status:** v0 has macrolactamization, RCM, transannular_diels_alder.
Proposal §2.2 lists more tactics.

### Deliverable

Add to `data/rules/`:

1. `macrolactonization.gml` + `.meta.yaml` — Yamaguchi / Shiina /
   Corey–Nicolaou family. The bond-level rule is C–OH + HO–C′ → C–O–C′
   (ester) + H2O; the *process-level* reagent_mass varies by activator
   and is the place where the bond-vs-process AE split is most useful
   chemistry-wise. S decides which activator family is the canonical
   meta.yaml value; the others go in `reagent_mass_alternatives` (new
   field, F adds support if not already present).

2. `transition_metal_cross_coupling.gml` + `.meta.yaml` — generic
   Negishi/Suzuki-style halide + organometal closure with stoichiometric
   byproduct. S decides how generic vs how specific (one rule per
   coupling type, or one schema with substituent variables).

3. `c_h_dehydrogenative_coupling.gml` + `.meta.yaml` — C–H / C–H
   activation, byproduct H2 (or H2O for oxidative variants). Highest
   AE among C–C closures.

4. (optional, S to advise) `rcam.gml` — ring-closing *alkyne*
   metathesis, byproduct 2-butyne.

For each new rule:

- The GML must pass `pixi run check-rules` (conservation re-check).
- `meta.yaml` must declare `classes`, `byproduct_mass_g_per_mol`,
  `retained_root_atom`, and `reagent_mass_g_per_mol`. `stereo_flags`
  populated per Workstream F.
- A toy substrate in `data/validation_panel/` exercises it.

### Acceptance

```bash
pixi run check-rules           # all rules conserve
pixi run pytest tests/panel/   # new rules' panel cases pass
```

### Risk

Rule schemas are versioned and auditable, but a too-general schema
matches contexts the chemist didn't intend (e.g., a macrolactonization
rule firing on an intermolecular pair instead of the intended
intramolecular closure). Workstream D's predicates close this gap.

---

## Workstream D — Strategy and predicate library

**Owner:** F (primary), S (chemistry priors)
**Status:** v0 strategy applies rules unconditionally up to `max_steps`.
The toy macrolactam DG includes a linear-dimer competitor because no
intramolecular predicate suppresses it — this is the explosion warned
about in proposal §3.2.

### Deliverable

`src/macrocert/generate/strategies.py` gains predicates that S can
parameterize per RunSpec:

1. **`is_intramolecular`** — the new bond connects two atoms in the
   same connected component, *before* the rule fires. Required for
   macrocyclic closures.

2. **`ring_size_equals(n)`** — the new bond closes a ring of exactly
   `n` atoms in the product graph. Required for ascomylactam (n=13)
   and for the panel cases.

3. **`forbidden_context(...)`** — chemistry-prior blacklist. S writes
   these from the macrocyclization reviews (e.g., RCM forbidden when
   the alkenes are part of a conjugated diene that would compete with
   metathesis; Diels–Alder forbidden when the dienophile is too
   electron-rich; etc.).

4. **`depth_bound`** — already in v0 via `max_steps`. S decides per
   target whether to allow multi-step coupling before the closure.

### Acceptance

The toy macrolactam DG, with `is_intramolecular + ring_size_equals(13)`
active, drops from 4 vertices (incl. linear dimer) to 3 (seco + water
+ macrolactam). The literature panel cases (Workstream B) pass with
fewer spurious top-N alternatives.

### Risk

Predicates that are too aggressive prune a literature closure and
make the panel look worse than it is. **D depends on B**: panel
cases are how predicate tuning is judged.

---

## Workstream E — Layer D protocol calibration

**Owner:** C (primary), S (experimental priors), F (cache plumbing)
**Status:** v0 has GFN2-xTB + Psi4 SCF/STO-3G + MACE-OFF drivers and a
working lazy-feedback loop. The *protocol* — when to use which tier,
what threshold τ to apply, what TS-search method, what implicit-solvent
model — has not been calibrated against real macrocycles.

### Deliverable

`data/energetics_protocol.yaml` — a configuration file consumed by
`RunSpec.energetics.extra` that pins:

1. **Tier escalation policy.** When does a route promote from xtb to
   MLIP to DFT? The plan suggested xtb → MLIP triage → DFT survivors;
   C decides the per-edge cost ceiling that triggers each step.

2. **MLIP model choice.** MACE-OFF small / medium / large; AIMNet2;
   or an OMol25-trained model. C runs a small benchmark on the
   surrogate panel and reports MAE vs Psi4 reference.

3. **DFT functional and basis.** STO-3G is a placeholder. C picks
   the production setting (likely B3LYP/def2-SVP or ωB97X-D/def2-SVP
   per the 2026 TS-search benchmark cited in proposal §2.5) and
   documents the trade-off.

4. **TS search method.** Wire `src/macrocert/energetics/ts_search.py`
   with CI-NEB or FSM (ASE drivers exist). C decides the convergence
   criteria and produces *one worked example* end-to-end for the
   macrolactamization closure of toy_macrolactam.

5. **Implicit-solvent model.** For Psi4: PCM (water? DMF?). For xtb:
   ALPB or GBSA. C decides — the AE-optimal macrolactamization at
   process scale is solvent-dependent.

6. **Barrier threshold.** Current default `dG_kcal_max = 30.0` was a
   guess. C calibrates it from the panel and reports a defensible
   ceiling with citation.

### Acceptance

- `data/energetics_protocol.yaml` committed with C's sign-off.
- `pixi run python -m macrocert.cli run data/targets/toy_macrolactam_energetics`
  uses the production protocol; certificate's `energetics_dependencies`
  shows the right tier per edge.
- The TS-search worked example writes a `barrier_kcal_per_mol` value
  to the certificate (currently always `None`).

### Risk

Per proposal §2.5, MLIPs on novel reaction networks have MAE > 5
kcal/mol. C must report this honestly in the certificate's
`provenance` field; the verifier already enforces the layer is
labelled defeasible.

---

## Workstream F — Stereo annotations on the rule library

**Owner:** S (chemistry decisions), F (GML encoding)
**Status:** `meta.yaml` for each rule has `stereo_flags` declaring
*what the rule does* to stereochemistry (e.g., `sets_alkene_geometry`,
`retains_alpha_stereo`). The GML body has no stereo annotations.

### Deliverable

Each rule in `data/rules/` annotated per MØD's stereo-information
syntax ([Andersen 2017]; see `external/mod/examples/py/030_stereo/`):

- `node [ id N stereo "tetrahedral[a,b,c,d]!" ]` for sp3 stereo centers
  involved in the transformation.
- `edge [ ... stereo "E" | "Z" ]` for alkene geometry where the rule
  pins or breaks it.
- For the macrolactamization rule: the α-carbon to the amide should
  retain stereo through the closure → preserved in `context`.
- For RCM: alkene geometry post-closure is `E/Z`-undetermined; the
  rule must reflect that (no stereo annotation on the new bond) and
  the strategy emits an E-or-Z product pair.
- For TDA: four new stereocenters; rule annotates `endo` vs `exo` if
  the chemistry pins it; otherwise the strategy emits the pair.

### Acceptance

- `pixi run check-rules` continues to pass (stereo doesn't break
  conservation).
- A toy stereo-aware substrate (S-selected) runs through the pipeline
  and the report shows the configured stereocenters in the composed
  rule's atom-mapped output.

### Risk

Per proposal §1.4, medium-ring closures live or die on preorganization.
Stereo annotations are how Layer C *certifies* that a route sets the
right configuration; without them, the bond-level AE optimum can be
recommended over a route the chemist actually wants because the AE-optimal
one sets the wrong stereo. This workstream is what makes the
certificate trustworthy on a stereochemically dense target.

---

## Coordination

### Sequencing

```
   A (target)
       │
       ├─────────────┐
       ▼             ▼
   B (panel)     C (rules)
       │             │
       ▼             ▼
   D (strategy) ────┘
       │
       ▼
   F (stereo)
       │
       ▼
   E (protocol) ── continuous in parallel
       │
       ▼
   M5 ascomylactam run
```

A unblocks B and is on the critical path. B and C can proceed in
parallel once A is roughly drafted (B doesn't strictly need A
finished). D depends on B for tuning. F can begin any time after
C lands. E runs continuously in parallel and converges with the rest
at M5.

### Cadence

Weekly sync (F + C + I + S) reviewing:

- Panel pass rate (B): target 100% by week 4.
- Open `panel_TODO.md` entries (B): target 0 by week 6.
- New rules and their panel coverage (C): one new rule per fortnight.
- Strategy predicate hit rate on the panel (D).
- Layer D protocol benchmark (E): one calibration table per month.

### Acceptance for M5 ascomylactam run

The following must all be green before invoking
`pixi run python -m macrocert.cli run data/targets/ascomylactam_a`:

1. **A:** `data/targets/ascomylactam_a/structure.mol` exists, perimeter audit signed.
2. **B:** ≥ 10 panel cases pass; τ frozen in `REPORT.md`.
3. **C:** `data/rules/` includes ≥ 5 macrocyclization tactics; all pass conservation re-check.
4. **D:** ring-size and intramolecular predicates active by default.
5. **F:** stereo annotations on every rule.
6. **E:** Layer D protocol committed; one worked TS example.

When all six are signed off, the ascomylactam run produces the
deliverable proposal §5 M5 calls for:

> shortlist of ≤ 10 strategy families with certificates; no-go
> certificates for ruled-out classes; report rendered; verifier-
> clean on every emitted certificate.

---

## What the team is *not* responsible for

- The harness itself (Layers A–E, verifier, IR, both ILP backends,
  cache, report renderer). Maintained by F as engineering tickets.
- Bench feasibility, yield prediction, scale-up, regulatory.
  Per proposal §6 these are explicitly out of scope.
- Inventing new macrocyclization chemistry. The proposal is a
  *constraint-certified design assistant*, not a synthesis-prediction
  model. The team's job is to encode existing chemistry into the
  harness, not to discover it.

---

## Estimated effort

Rough order-of-magnitude, per role, over ~3 calendar months:

| role | time | concentration |
|------|------|---------------|
| S    | ~40% FTE | A, B, C, F (chemistry decisions throughout) |
| C    | ~30% FTE | E primarily, B/F supporting |
| I    | ~10% FTE | A supporting, panel encoding, harness tickets if any |
| F    | ~25% FTE | C/D/F GML encoding, predicate implementation, harness tickets |

The proposal calendar in `proposal.md` §5 (M1 weeks 1–4, …, M5 weeks 16–22)
assumes the harness and the chemistry land roughly in parallel. We're
in a different regime: harness ships in week 1; the rest of the
calendar is this proposal.
