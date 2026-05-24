# Workstream F: Cross-Coupling Rules + Cache-Key Fix

**Date:** 2026-05-24
**Owner:** Workstream F (formal-methods/coding)
**Status:** Both tasks complete; tests pass; changes unstaged per instruction.

---

## Task 1 — SHA-256 cache-collision fix

### Bug

Workstream E (Marks Vandezande Gomes 2026, *arXiv:2604.00405*) found that
the v1 SHA-256 cache key in `src/macrocert/energetics/cache.py` did not
include the solvent name or a structured DFT composite identifier
(functional + basis + dispersion + solver). Two computations on the
same SMILES in different solvents — or with different functionals
under the same display `method` label — would collide and silently
return the wrong energy.

### Fix

- Extended `make_cache_key` (and the `CacheEntry` dataclass) to include
  `method_id` (composed string: functional + basis + dispersion + solver)
  and `solvent_name` (defaulting to `"vacuum"`).
- Added a `CACHE_VERSION = "v2"` constant. The on-disk layout is also
  namespaced by version (`.cache/energetics/v2/...`) so v1 entries can
  coexist on disk but are never served by a v2 lookup.
- Updated `EnergeticsCache.lookup_or_compute` to accept the 7-tuple
  `(rule_id, reactants, products, tier, method, method_id, solvent_name)`.
- Updated `qm.py` (`xtb_single_point`, `psi4_single_point`, `reaction_dG`)
  to accept a `solvent_name` parameter, configure the underlying calculator
  for implicit solvent, and stamp the solvent into the result's method
  label.
- Updated `mlip.py` (`mace_off_single_point`, `mace_reaction_dG`) to thread
  `solvent_name` through to the result's method label.
- Updated `feedback.py` (`run_with_energetics`) to accept
  `solvent_name: str = VACUUM_SOLVENT` and pass the full 7-tuple to the
  cache.
- Added a one-line comment near the key function pointing to the
  Workstream E source (`arXiv:2604.00405`).

### Files modified

- `src/macrocert/energetics/cache.py` — full rewrite of key schema; added
  `CACHE_VERSION`, `VACUUM_SOLVENT`; expanded `CacheEntry` and
  `lookup_or_compute`.
- `src/macrocert/energetics/qm.py` — `solvent_name` threaded through both
  drivers and `reaction_dG`.
- `src/macrocert/energetics/mlip.py` — `solvent_name` threaded through.
- `src/macrocert/energetics/feedback.py` — `solvent_name` parameter on
  `run_with_energetics`; new `_method_id_for_tier` helper.
- `src/macrocert/verifier/conservation.py` — atomic-mass table extended
  with Sn (118.710) and Li (6.94) to support the Stille rule's BFS
  mass recomputation.

### Files created

- `tests/energetics/__init__.py`
- `tests/energetics/test_cache_key.py` — 8 tests pinning the v2 key
  invariants (different solvents → different keys; different
  `method_id` → different keys; same inputs → same key; cross-pollution
  through `EnergeticsCache.lookup_or_compute` regression).

### Before/after demonstration

Same SMILES (`c1ccccc1Br` → `c1ccc(-c2ccccc2)cc1`), same rule
(`suzuki`), same tier (`dft`), same display `method` (`SCF/STO-3G`),
DMF vs DCM:

| Variant | DMF key | DCM key | Collision? |
|---|---|---|---|
| v1 (before fix) | `67fab89141742e4525ce269486e88a2a` | `67fab89141742e4525ce269486e88a2a` | **YES — same key, wrong energy returned silently** |
| v2 (after fix)  | `8769f767c744cc20812b4742d533a56c` | `7ec9ab31cdddbeb9039f5e2673c47a9f` | no |

---

## Task 2 — Cross-coupling rules

Five rule pairs (GML + meta.yaml) encoded under the flat
`cross_coupling_*` prefix per the loader's flat-file convention.
All five pass `pixi run check-rules` (10/10 rules including the
existing four macrocyclization rules and `c_h_dehydrogenative_coupling`).

### Files created

| Rule | GML | meta.yaml |
|---|---|---|
| `cross_coupling_suzuki` | `data/rules/cross_coupling_suzuki.gml` | `data/rules/cross_coupling_suzuki.meta.yaml` |
| `cross_coupling_negishi` | `data/rules/cross_coupling_negishi.gml` | `data/rules/cross_coupling_negishi.meta.yaml` |
| `cross_coupling_buchwald` | `data/rules/cross_coupling_buchwald.gml` | `data/rules/cross_coupling_buchwald.meta.yaml` |
| `cross_coupling_sonogashira` | `data/rules/cross_coupling_sonogashira.gml` | `data/rules/cross_coupling_sonogashira.meta.yaml` |
| `cross_coupling_stille` | `data/rules/cross_coupling_stille.gml` | `data/rules/cross_coupling_stille.meta.yaml` |

### Files modified

- `data/rules/_index.yaml` — added all five to `all_macrocyclization`,
  added a new `cross_coupling` set, and noted (in comments) why none
  belong to `high_ae_macrocyclization`. Stille is gated by the
  `toxic_byproduct` class flag.

### Reagent + byproduct mass table

All byproduct masses are the **strict atom-conserving** value computed
by BFS over the right-side graph from the `retained_root_atom`, summing
the atomic masses of the unreachable atoms (the same convention
macrolactamization uses for its H₂O byproduct). The verifier confirms
each value to within ±0.01 g/mol:

| Rule | reagent_mass (g/mol) | Reagent stack | byproduct_mass (g/mol) | Byproduct (strict) | Verifier-recomputed | Toxic? |
|---|---|---|---|---|---|---|
| `cross_coupling_suzuki` | 306.0 | Pd(PPh₃)₄ (30 amortized) + 2·K₂CO₃ (276) | **141.73** | B(OH)₂O + HBr | 141.735 | no |
| `cross_coupling_negishi` | 30.0 | Pd(PPh₃)₄ (30 amortized; no base) | **225.19** | ZnBr₂ | 225.188 | no |
| `cross_coupling_buchwald` | 300.0 | Pd₂(dba)₃ + XPhos + Cs₂CO₃ (amortized) | **80.91** | HBr | 80.912 | no |
| `cross_coupling_sonogashira` | 427.0 | Pd(PPh₃)₂Cl₂ + CuI + 2·Et₃N | **80.91** | HBr | 80.912 | no |
| `cross_coupling_stille` | 263.0 | Pd(PPh₃)₄ + CuI + LiCl | **198.61** | Sn + Br (opaque-Sn) | 198.614 | **yes** (`toxic_byproduct` class) |

### Stereo flags (per research §4)

| Rule | stereo_flags |
|---|---|
| Suzuki | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `may_set_atropisomer`, `risk_protodeboronation_on_basic_substrates`, `sp3_coupling_outside_v0_scope` |
| Negishi | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `risk_alpha_carbonyl_racemization`, `risk_beta_hydride_elimination_sp3`, `stereospecific_sp3_with_ni_jarvo` |
| Buchwald | `retains_sp3_stereo_distal`, `risk_alpha_acidic_racemization`, `aryl_amine_only_v0` |
| Sonogashira | `retains_sp3_stereo_distal`, `retains_alkyne_linearity`, `risk_glaser_homocoupling_byproduct` |
| Stille | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `tin_residue_toxicity_flag` |

### Stille special handling

Per instruction: Stille is included in v0 but **not** in
`high_ae_macrocyclization`. It carries a `toxic_byproduct` class flag
and an explicit `tin_residue_toxicity_flag` stereo flag. The
`notes:` section of `cross_coupling_stille.meta.yaml` carries an
extended discussion of (a) the organotin regulatory concern, (b) the
heaviest-byproduct status of Stille among the five couplings, and
(c) the opaque-Sn encoding rationale (strict 198.61 g/mol bond-level
vs chemically realistic Bu₃SnBr 326.94 g/mol).

### Strict-atom-conservation discussion

The Workstream C research brief proposed the chemically natural neutral
byproducts (B(OH)₃ + HBr for Suzuki, 142.74 g/mol; Bu₃SnBr for Stille,
326.94 g/mol). The task directive overrode this with the
strict-atom-conserving convention to match macrolactamization. The
deltas are:

- Suzuki: 141.73 (strict, B(OH)₂O + HBr) vs 142.74 (neutral, B(OH)₃ +
  HBr). The 1.008 g/mol H⁺ that neutralizes the boronate comes from
  base/water and is accounted at the process level in
  `reagent_mass_g_per_mol` (K₂CO₃).
- Stille: 198.61 (strict, Sn + Br) vs 326.94 (chemical, Bu₃SnBr). The
  Bu₃ groups stay on Sn throughout but the strict encoding does not
  enumerate them in the rule body. The chemical value is preserved in
  `byproduct_mass_alternatives.Bu3SnBr_real`.
- Negishi/Buchwald/Sonogashira: strict and chemical values coincide
  (no proton-transfer fiction, no opaque metal).

### Citations

Every rule's `refs:` block carries ≥ 3 DOIs (original method paper +
modern macrocyclic example + recent review) per the task contract.
Activator-stack masses and byproduct identities are each backed by
≥ 3 sources cross-referenced in the research doc §3.

---

## Test results

`pixi run pytest tests/ -q` (full suite):

- **38 baseline tests pass.**
- **8 new tests pass** in `tests/energetics/test_cache_key.py` (cache
  collision fix regression suite).
- **21 additional existing tests pass** (spec, verifier, panel for
  non-placeholder cases).
- **3 failures pre-date this session**, unrelated to either task. All
  are placeholder MOL files (literal text "PLACEHOLDER — DO NOT TREAT
  AS A VALID V2000 MOLFILE" or "STRUCTURE NOT ENCODABLE", awaiting
  Ivan to encode from cited CIF data):
  - `tests/panel/test_panel.py::test_panel_case[epothilone_b_nicolaou_rcm_1997]`
  - `tests/panel/test_panel.py::test_panel_case[vancomycin_cde_ring_boger_snar]`
  - `tests/panel/test_panel.py::test_panel_case[citreoviridin_suh_imda_1985]`

  These are data-pending failures, not logic failures, and not part of
  the Workstream F deliverable. Non-panel tests (59 tests) all pass.

`pixi run check-rules` (data/rules/):

- **10/10 rules pass conservation re-check**, including all 5 new
  cross-coupling rules.

---

## Changes left unstaged

Per instruction, no commit was created. All modifications and new
files are present in the working tree. Summary:

**Modified (tracked):**
- `data/rules/_index.yaml`
- `src/macrocert/energetics/cache.py`
- `src/macrocert/energetics/qm.py`
- `src/macrocert/energetics/mlip.py`
- `src/macrocert/energetics/feedback.py`
- `src/macrocert/verifier/conservation.py`

**Created (untracked):**
- `data/rules/cross_coupling_{suzuki,negishi,buchwald,sonogashira,stille}.gml`
- `data/rules/cross_coupling_{suzuki,negishi,buchwald,sonogashira,stille}.meta.yaml`
- `tests/energetics/__init__.py`
- `tests/energetics/test_cache_key.py`
- `docs/cross_coupling_and_cache_fix.md` (this file)
