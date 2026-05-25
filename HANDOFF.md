# MØD-MacroCert — Handoff to the next implementation agent

**Date of handoff:** 2026-05-24
**Repo head:** commit `10bfc98` (or whatever's at the tip of `main` when you read this — `git log -1` is authoritative)
**State:** Pre-M5 gate **8/9 passing**. The proposal §5 deliverable line is production-ready end-to-end.

This document is your onboarding. Read it before touching anything. It captures (a) what's done, (b) what's deferred, (c) what bit us, and (d) what's blocking what.

---

## 30-second elevator pitch

MØD-MacroCert is constraint-certified macrocyclization design. Take a macrocyclic natural product, encode its structure + a seco-precursor, run `scripts/build_m5_campaign.py <target_dir>`, get 15 per-tactic certificates (1 optimal + 14 no-go) + an aggregated markdown report. Every certificate is independently re-verified by a separate-process verifier (`pixi run macrocert-verify <cert>`).

Production validated on **7 chemically distinct macrocyclization classes** spanning ring sizes 13–31 (ascomylactam A, vancomycin C-O-D, epothilone B post-RCM, erythronolide B, cytochalasin B, Trost bryostatin analogue, Phoenix-Reddy cassaine).

---

## First things to do

```bash
# 1. Verify the env builds
cd ~/Code/ielm/macrocert
pixi install
# (If MØD isn't built yet:)
pixi run build-mod

# 2. Sanity-check the harness
pixi run pytest tests/ -q
# Expected: 177 passed, 0 skip

# 3. Sanity-check the rule library
pixi run python -m macrocert.cli check-rules data/rules
# Expected: 15 rule(s) pass conservation re-check (stereo: 0 warning(s), 0 info(s))

# 4. Sanity-check the deployment gate
cp data/pre_registration.template.yaml /tmp/dryrun_pre_reg.yaml
sed -i.bak 's/signed_by: null/signed_by: "DRYRUN"/; s/locked_at: null/locked_at: "2026-05-24T00:00:00Z"/' /tmp/dryrun_pre_reg.yaml
pixi run python scripts/pre_m5_gate.py --lockfile /tmp/dryrun_pre_reg.yaml --allow-partial
# Expected: 8/9 passing; the 1 fail is the ascomylactam Ivan-signed marker

# 5. Read the entry-point docs in this order:
#    README.md             — elevator pitch + layout
#    docs/INDEX.md         — canonical doc map (30+ docs, organized)
#    proposal.md           — the original design document
#    RESEARCH_PROPOSAL.md  — the 6-workstream execution plan
#    SETUP.md              — pixi env + native MØD build
```

If any of those don't work, read the corresponding section below before proceeding.

---

## The one remaining Ivan-side gap

The pre-M5 gate's `[FAIL] ascomylactam target encoded + signed` check is blocked on a chemist audit of the encoded structure at `data/targets/ascomylactam_a/structure.mol`. Ivan is not a chemist; his **brother is** and will check it.

### What the chemist needs to audit

Open `data/targets/ascomylactam_a/structure.mol` (V2000) alongside `data/targets/ascomylactam_a/Chen2019_paper.pdf` (the primary source — *J. Nat. Prod.* 2019, 82:1752, DOI:10.1021/acs.jnatprod.8b00918, CCDC 1515168).

Two specific chemistry decisions need a chemist's eye:

1. **Atropoisomer face of the *para*-arene** inside the 13-membered ring. The Chen 2019 X-ray (CCDC 1515168, Flack -0.13(9)) pins this. Our encoder used RDKit's ETKDG + MMFF, which picks an arbitrary face. Look at Chen 2019 Figure 3 (X-ray structure) and confirm whether our encoded `structure.mol` has C-5′/C-9′ and C-6′/C-8′ on the correct faces of the macrocycle. If wrong, the fix is a C-5′↔C-9′ + C-6′↔C-8′ swap and re-embed (run `pixi run python scripts/build_ascomylactam_a.py` after editing `ASCOMYLACTAM_A_SMILES` accordingly).

2. **Ring-B fusion edge.** Our encoder chose to fuse ring B to ring A via the **C4–C16 edge** (the Wijeratne 2013 / Faraj 2023 reading). The alternative is **C3–C4**. Look at Chen 2019 Figure 1 (HMBC/COSY correlations) and confirm.

### What to do once the audit is done

If both decisions are correct as encoded:

```bash
# Add the sign-off marker. Pick whatever date format Ivan's brother prefers;
# the gate just looks for the literal string "Ivan-signed" anywhere in
# data/targets/ascomylactam_a/notes.md (see scripts/pre_m5_gate.py:46).
# Recommended:
#   "**Ivan-signed: 2026-XX-XX** by Dr. [Brother's Name], reviewed against
#    Chen 2019 Figure 1+3 / CCDC 1515168. Atropoisomer face: correct.
#    Ring-B fusion edge: C4-C16 confirmed."

# Then verify the gate flips to 9/9:
pixi run python scripts/pre_m5_gate.py --lockfile /tmp/dryrun_pre_reg.yaml --allow-partial
```

If either decision is wrong:

```bash
# Fix the SMILES in scripts/build_ascomylactam_a.py (atom map at the top
# of the file documents the intended chirality + ring fusion).
# Then re-run the build:
pixi run python scripts/build_ascomylactam_a.py
# Then re-run the M5 campaign:
pixi run python scripts/build_m5_campaign.py data/targets/ascomylactam_a
# Then re-add the sign-off marker per above.
```

---

## What was shipped this session (2026-05-24)

23 atomic commits ahead of `origin/main`. Each commit is a logical unit; see `git log --oneline` for the sequence.

### Layer-by-layer

| Layer | What landed |
|---|---|
| A (encoding) | Ascomylactam A target + Chen 2019 paper preserved as provenance; seco-precursor build scripts; SMILES canonicalization helper (`spec/canonical.py`) that collapses aromatic + Kekulé forms at every IR boundary |
| B (generation) | Predicate framework — `is_intramolecular`, `ring_size_equals`, `enforce_ez_geometry`, `alcohol_partner_C_must_be_aromatic`/`_sp3` |
| C (verification + ILP) | Rule library 4 → **15 rules**; adversarial verifier expanded 13 → **80 tests**; stereo-conservation validator wired into `check-rules`; SHA-256 cache-key collision fix; `_find_rule_id` substring bug fix |
| D (energetics) | `data/energetics_protocol.yaml` DOI-cited production protocol; FSM TS-search via `sella + xtb` driver (`energetics/ts_search.py`); worked-example barrier (NH₃ umbrella inversion, 6.11 kcal/mol) flowing into cert provenance |
| E (reporting) | `scripts/build_m5_campaign.py` — the §5 deliverable producer; 7 per-target M5 reports under `docs/M5_REPORT_*.md` |
| F (stereo enforcement) | MØD upstream `MOD_ABORT` patch (4-line fix at `Stereo.hpp:404-407`); α-C overlays on macrolactam/lactone; TDA endo/exo sibling rules; stereo-policy metadata (`match_enforced` / `n_a_sp2_only` / `advisory_only`) |
| Harness | MØD random-seed pinning (byte-deterministic campaigns); `solver.extra.activators` override wiring; placeholder-MOL panel skip; lactone surrogate panel; 7 literature panel scaffolds |

### Chemistry corrections to the original proposal (13+)

Per real-target validation, the proposal's exemplars had several chemistry errors. Each is documented in the relevant research brief + the panel case's `notes.md`:

1. Vancomycin macrocyclization is **biaryl ether SNAr (Ar-O-Ar)**, not macrolactamization
2. Ascomylactam A is **aryl-ether (Ar-O-C(sp³))**, not macrolactam
3. **Citreoviridin is not macrocyclic** (slot removed, commit `26486df`)
4. Cytochalasins B/D/E/H are **macrolactones**, not macrolactams
5. Cytochalasins close via **HWE olefination**, not macrolactamization (Haidle-Myers 2004)
6. No natural bryostatin has ever been closed by RCM (only Trost 2007 ring-expanded analogue is)
7. Skellam 2017 DOI corrected to `10.1039/c7np00036g`
8. Bérubé-Deslongchamps 1987 attribution corrected (actual authors: Baettig-Dallaire-Pitteloud-Deslongchamps)
9. Erythronolide B formula corrected: C₂₁H₃₈O₇ (4 hydroxyls), not C₂₁H₃₈O₆ (3)
10. Erythronolide B PubChem CID corrected: 441113 (the brief's 122729 was rifampicin)
11. Corey 1978 erythronolide B DOI corrected: `10.1021/ja00482a063`
12. Haidle-Myers cytochalasin B DOI corrected: `10.1073/pnas.0402111101`
13. Nicolaou epothilone B 1997 page corrected: 7974 (proposal said 7960 which is the A paper)

### Latent harness bugs caught + fixed by real-target validation

1. `cache.py` SHA-256 collision — DMF/DCM solvent runs silently used the same cache entry (commit `57a2e0d`)
2. `dg_to_ir.build_ir` aromaticity perception — MØD emitted aromatic + Kekulé as distinct IR vertices, breaking flow (commit `4848be8`)
3. `_find_rule_id` substring fallback — `aryl_etherification` is a literal substring of `biaryl_etherification`, so biaryl certificates were silently mislabeled (commit `4848be8`)
4. `LabelType.String` default broke `*` wildcards in stereo overlays — switched to `Term, Specialisation` (commit `c245bf2`)
5. `solver.extra.activator` parsed but never consumed — process-AE always reported canonical Yamaguchi mass even when Corey-Nicolaou was selected (commit `ee9fd7a`)

### Upstream MØD bug found + patched + validated

`RC/Visitor/Stereo.hpp:404-407` aborts unconditionally on substrates carrying an amine N at degree 3+ under `LabelSettings.withStereo=true`. Root cause: the LonePair/Radical branch hits `MOD_ABORT` even though the same file's `copyAllFromSide` lambda at lines 94-101 handles LonePair correctly. The fix (4 lines) mirrors the working pattern.

- Patch: `patches/0001-Stereo-copy-LonePair-virtual-edges-in-copy-unmatched.patch`
- Build validation: `docs/mod_patch_build_validation.md`
- Investigation: `docs/mod_abort_investigation.md` (9 empirical scratch tests)
- Upstream PR draft: `patches/upstream_PR_draft.md` (ready to push when a GitHub fork is created)

The patch is applied in `external/mod/` on branch `fix/stereo-finalize-copy-unmatched-r1`. Required for runtime stereo enforcement on any substrate with amine groups. Without it, the ascomylactam M5 with `stereo_enforcement: true` would abort.

---

## Open items, prioritized

### P0 — chemist sign-off (Ivan-side)
See "The one remaining Ivan-side gap" above. **This is the only blocker to pre-M5 gate hitting 9/9.**

### P1 — MLIP + DFT energetics tiers
Today's energetics worked example is xtb-only on a surrogate substrate (NH₃ umbrella inversion). The production tier escalation calls for MLIP triage (MACE-OMol25) → DFT refinement (B3LYP-D3BJ/def2-TZVP). Status: both raise `NotImplementedError` at `src/macrocert/energetics/{mlip,qm}.py` for the tier-escalation paths.

Five named follow-ups documented in `docs/energetics_ts_search_landed.md` §8:

1. MACE-OMol25 model download + MLIP tier wiring
2. B3LYP-D3BJ/def2-TZVP DFT refinement tier
3. Atom-mapped bound-complex constructors for the actual macrolactamization saddle (NH₃ surrogate works because it's atom-conserving; the real chemistry isn't)
4. 3-model heterogeneous OOD ensemble (MACE-OMol25 + UMA-Medium + ESEN-S)
5. TS cache (analogous to `EnergeticsCache`)

These are multi-session pieces. The protocol YAML is already DOI-cited; the wiring is what's missing.

### P2 — MØD upstream PR
The fork branch `fix/stereo-finalize-copy-unmatched-r1` in `external/mod/` is ready to push to a GitHub fork (suggested name `ielm/mod`). Then file the PR at `jakobandersen/mod` using `patches/upstream_PR_draft.md` as the body.

Ivan said this isn't needed in-session but is reasonable forward work. Doing it removes our local maintenance burden when the upstream merges (then the `patches/` directory becomes empty and we can delete the local fork branch).

### P3 — Adversarial verifier expansion
The 80-test current suite caught every introduced mutation, but real-target validation found 5 latent bugs that adversarial tests didn't catch (because they required campaign-level rule collision or canonicalization issues). The roadmap at `docs/adversarial_verifier_roadmap.md` lists 7 prioritized extensions:

1. Per-rule parametrization for the 3 legacy rules (mechanical)
2. TDA endo/exo stereo-aware adversarial
3. Stereo-policy advisory propagation attacks
4. Activator-override adversarial
5. Cross-rule (composed) attacks
6. IIS spoofing (the 84 no-go certs across the 7 §5 deliverables make this an obvious next target)
7. SHA-256 cert-integrity hashing (deployment-grade)

### P4 — More panel literature cases (proposal §4.1)
Currently at 6/7 literature passes (the 7th is the citreoviridin slot we removed). The proposal §4.1 calls for "≥10 cases". Reasonable next targets:

- Wender bryostatin natural-product (Yamaguchi+Prins — would exercise a Prins-cyclization rule we don't have)
- Boger vancomycin DE ring (separate from the C-O-D ring we encoded)
- Curacin A RCM
- Megalomicin / amphotericin macrolactonization (would exercise more of the macrolactonization activator alternatives)
- Lactimidomycin (Nagorny 2013 Zn-mediated HWE; would re-exercise the HWE rule)
- Norzoanthamine / FR901483 TDA targets

Each takes ~60-90 min to encode + run a campaign + write the M5 report.

### P5 — Rule library expansion
The current 15 rules don't cover:

- **Prins cyclization** (Wender bryostatin)
- **Mitsunobu etherification** (the inverting alcohol-activation sibling of aryl_etherification; flagged but not encoded)
- **Wittig macrocyclization** (deferred per HWE research brief)
- **Buchwald-Hartwig amination** (we have the C-N coupling cross-coupling rule but not specifically amination)
- **Decarbonylative C-H coupling** (research brief deferred per Workstream C)
- **Ring-closing alkyne metathesis (RCAM)** (research brief notes it as optional)

Adding a rule is ~60 min: research brief → meta.yaml + GML → adversarial tests → docs.

---

## Gotchas to know about

### "Atomic commits as you go"
Ivan's standing rule. **Every logical unit gets its own commit.** Don't accumulate 99 files of unstaged changes. The session that started this work (2026-05-24) violated this and had to commit 99 files in 11 retroactive logical commits. Don't repeat that.

Use `git log --oneline | head -30` to see the pattern. Commit messages are full-context (motivation + what + why), not one-liners.

### Citation discipline (`feedback_macrocert_references` memory)
Every literature-derived value in the repo carries a DOI or source citation. Look at `data/rules/*.meta.yaml` for the format: each `reagent_mass_g_per_mol`, `byproduct_mass_g_per_mol`, etc., has a reference. Each research brief in `docs/` lists ≥3 DOIs per chemistry claim. The campaign report's "Provenance" section names every source.

This is non-negotiable. The certificate framework's whole point is auditability; cite-as-you-write enforces that.

### MØD's stereo system is tetrahedral-only
Per `docs/mod_stereo_reference.md`: MØD enforces tetrahedral chirality at match-time. The other geometries (`linear`, `trigonalPlanar`, `any`) parse but their morphism implementations are `MOD_ABORT`. Concretely:

- E/Z alkene geometry **cannot be enforced by MØD** at match time. The Workstream D `enforce_ez_geometry` rightPredicate (RDKit-based) is the workaround.
- Atropoisomerism is 3D-geometric and not graph-encodable. The `advisory_only` `stereo_treatment` documents this honestly in cert provenance.
- The `Square_Planar` / `Trigonal_Bipyramidal` / `Octahedral` geometries don't exist in MØD's `GeometryGraph` at all.

### `LabelType.Term, LabelRelation.Specialisation` is the default now
Commit `c245bf2` switched the default `LabelSettings`. Wildcards (`label "*"` in GML) work under `Term` mode, not the previous `String` mode. If you read older docs or external/mod examples that assume String mode, the defaults have moved.

### Byte-deterministic campaigns require the seed env var
Commit `d1c441c`. `scripts/build_m5_campaign.py` sets `MACROCERT_MOD_SEED=0xC0FFEE` + `PYTHONHASHSEED=0` in each leg's subprocess env. If you invoke the pipeline directly (`pixi run python -m macrocert.cli run <target>`), set these manually if you need determinism. The `tests/integration/test_campaign_reproducibility.py` exercises this contract.

### `_find_rule_id` substring trap
Commit `4848be8`. If you add a new rule whose `ruleID` (the string in the GML body) is a substring of another rule's, the legacy substring-fallback would mislabel. The fix uses two-pass matching (exact match first, then word-boundary-safe prefix). Don't reintroduce the substring fallback.

### MØD already has a randomness API
Commit `d1c441c`. `mod.rngReseed(seed)` exposed in the Python binding. No upstream patch needed for determinism. If you find another non-determinism source (e.g., dict iteration order in JSON serialization), that's the JSON output's problem, not MØD's.

### `external/mod/` is on a fork branch
The branch `fix/stereo-finalize-copy-unmatched-r1` carries the upstream patch. Don't `git checkout develop` or `git reset` in `external/mod/` without thinking about whether you'll lose the patch. The build script reads from the working tree, so any branch with the patch applied + the macrocert build patches at top works.

### Tests have a `@pytest.mark.slow` marker
For tests that run real chemistry computations (xtb single-points, FSM TS search). They're registered in `pyproject.toml [tool.pytest.ini_options].markers`. The default `pytest tests/` runs them; in CI you may want `pytest tests/ -m "not slow"`.

### The pre-registration lockfile is a template
`data/pre_registration.template.yaml` is the template. To actually run the gate against locked production values, copy it to `data/pre_registration.lock.yaml` and fill in the `null` fields. The gate script accepts a `--lockfile` flag. The session used `/tmp/dryrun_pre_reg.yaml` (a dummy signed copy) — that's fine for development, not for production.

---

## Files to read first

In order:

1. **`README.md`** — repo entry point
2. **`docs/INDEX.md`** — canonical doc map
3. **`docs/M5_REPORT_ascomylactam_a.md`** — see what a §5 deliverable looks like
4. **`scripts/build_m5_campaign.py`** — see how the deliverable is produced
5. **`src/macrocert/spec/canonical.py`** — the load-bearing canonicalization fix
6. **`src/macrocert/kernel/dg_to_ir.py`** — IR construction, where most kernel logic lives
7. **`src/macrocert/verifier/verify.py`** — the independent verifier (load this file before anything else if you're working on verifier rigor)
8. **`docs/mod_abort_investigation.md`** — example of how to root-cause MØD issues
9. **`patches/README.md`** — patch discipline + upstream PR procedure
10. **`tests/verifier/README.md`** — adversarial test framework + extension procedure

---

## Tracker location

The MacroCert effort tracker lives in Ivan's Obsidian vault at:

```
~/Obsidian/zen/Efforts/On/MacroCert.md
~/Obsidian/zen/Efforts/On/MacroCert/        (subdirectories: workstreams/, sessions/, decisions/, handoffs/, research/)
```

Plus per-rule concept notes under `~/Obsidian/zen/Atlas/Notes/Concepts/` and the MOC at `~/Obsidian/zen/Atlas/Maps/Macrocyclization.md`. Source notes (Chen 2019, Andersen 2017, Sugata 2017, etc.) under `~/Obsidian/zen/Atlas/Notes/Sources/`.

Update the tracker at major milestones. Use `vlt memory add observation/decision` to log session findings — the project's memory is at `~/Obsidian/zen/.claude/agent-memory/vault-agent/` and is queryable via `vlt memory query`.

---

## How to start a new session

```bash
# 1. Read this file + README + INDEX
# 2. git log --oneline -20  — see what the prior session did
# 3. pixi run pytest tests/ -q  — verify clean state
# 4. pixi run python scripts/pre_m5_gate.py --lockfile /tmp/dryrun_pre_reg.yaml --allow-partial
#    — see which gate checks are failing right now
# 5. Pick a P0/P1 item from "Open items, prioritized" above
# 6. Atomic-commit-as-you-go. NO 99-file mega-commits.
```

---

## Acknowledgments

This session was driven by Ivan Leon (PI) with Claude (Anthropic) as the implementation agent across many subagent dispatches. Chemistry corrections caught by the team along the way are documented case-by-case. The single upstream MØD bug fixed during the session (`Stereo.hpp:404-407`) credits Jakob Andersen for the MØD codebase and his `// TODO` annotation that predates this fix by some years.

The cassaine slot, the citreoviridin removal, the Trost bryostatin analogue diagnosis, and the cytochalasin HWE re-categorization are particularly thoughtful diagnoses by the chemistry research-agents — each saved hours of downstream confusion. Read their research_brief.md files for the full reasoning.

— End of handoff. Good luck.
