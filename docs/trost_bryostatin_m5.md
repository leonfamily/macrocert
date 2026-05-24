# Trost Bryostatin Analogue — M5 Deliverable (2007 JACS RCM, 31-ring outlier)

**Case:** `data/validation_panel/trost_bryostatin_analogue_rcm_2007/`
**Tactic:** Ring-closing metathesis (`rcm`)
**Primary reference:** Trost, B. M.; Yang, H.; Thiel, O. R.; Frontier,
A. J.; Brindle, C. S. "Synthesis of a Ring-Expanded Bryostatin
Analogue." *J. Am. Chem. Soc.* **2007**, *129*, 2206–2207. DOI
[10.1021/ja067305j](https://doi.org/10.1021/ja067305j). Full paper:
Trost, B. M.; Yang, H.; Dong, G. *Chem. Eur. J.* **2011**, *17*,
9789–9805. DOI
[10.1002/chem.201002932](https://doi.org/10.1002/chem.201002932).
Open-access redrawing: Jahan, N. *et al.* *SynOpen* **2023**, *7*,
209–242, Scheme 19. DOI
[10.1055/s-0042-1751453](https://doi.org/10.1055/s-0042-1751453).

## 1. Summary

Trost's 2007 ring-expanded bryostatin analogue closes a **31-membered
macrolactone** by Grubbs–Hoveyda 2nd-generation RCM on a diene-tethered
seco-precursor (benzene, 50–80 °C, high dilution, 80% yield, 1:1 E:Z).
The natural-product bryostatin macrocycle (26-membered) has **never been
closed by RCM** in any published total synthesis — the C16–C17 trans-
trisubstituted alkene is too hindered for Grubbs catalysts at the natural
ring size. Trost's analogue inserts one extra –CH₂– into the seco-diene,
relocating the RCM alkene and expanding the macrocycle by 5 atoms to 31
members; this relieves the strain enough to let RCM proceed. This is the
**only published bryostatin-family RCM macrocyclization** in the
literature. See `research_brief.md` §1 for the full citation diagnosis.

The full M5 deliverable — encoded target, derived seco, runspec,
expected.yaml, and an M5 campaign over all 13 macrocyclization
tactics — is now in place:

| Metric                                  | Value                              |
| --------------------------------------- | ---------------------------------- |
| Cyclized target formula                 | C₄₆H₇₄O₁₄                          |
| Cyclized exact MW                       | 850.5079 Da                        |
| Seco-precursor formula                  | C₄₈H₇₈O₁₄                          |
| Seco-precursor exact MW                 | 878.5392 Da                        |
| Δ MW (seco − cyclized)                  | 28.0313 Da = C₂H₄                  |
| **Macrocycle ring size**                | **31 (panel outlier; range else 12–16)** |
| Embedded pyranose rings                 | 2 (the bryostatin A and C rings)   |
| sp³ stereocenters (cyclized)            | 9                                  |
| In-ring alkene (RCM-formed)             | 1, E (encoded)                     |
| Tactics evaluated in M5 campaign        | 13                                 |
| Verifier-clean certificates             | 13 / 13                            |
| Optimal tactics in shortlist            | 1 (`rcm`)                          |
| `rcm` objective (bond-level expelled)   | 28.054 g/mol (ethylene)            |
| Panel test (`pytest -k trost`)          | passes                             |
| 3D embed status                         | succeeded (RDKit ETKDG + MMFF)     |

## 2. Encoding decisions

### 2.1 31-ring outlier and predicate exercise

This case is the panel's **only ring-size outlier**. All other panel
cases close 12–16 membered macrocycles; the bryostatin analogue is
31-membered. The runspec sets `strategy.predicates.ring_size_equals: 31`,
exercising Macrocert's `ring_size_equals` predicate at the upper end of
its validated range. The RDKit SSSR (which Macrocert uses for ring
detection) is well-tested at all ring sizes; no upper cap was hit. The
RCM rule fired correctly on the seco-diene and produced an
optimal-witness certificate matching the literature tactic.

### 2.2 Synthetic analogue, no public-database structure

The analogue is **not in PubChem, ChEBI, or CCDC** (verified by name and
structural search 2026-05-24). Its precise atom-by-atom structure is
published only in the Trost 2007 *JACS* SI (compound **3**) and the
Trost 2011 *Chem. Eur. J.* SI (compounds 177–179 in Jahan 2023 review
numbering), both ACS/Wiley-paywalled. The Jahan 2023 *SynOpen* review
Scheme 19 (open access) provides a clean redrawing of the macrocycle
topology and substituent placement but not all stereochemistry.

The encoded `structure.mol` is therefore a **chemistry-faithful
representation** capturing the essential features Macrocert's RCM rule
discriminates on, NOT a precise reproduction of compound 3. Specifically
the encoding asserts:

- exactly 31 atoms in the macrocyclic ring (verified by SSSR)
- one in-ring C=C alkene (the RCM-formed bond, E in the encoded form)
- one in-ring lactone ester C(=O)–O (pre-formed before RCM in Trost's
  actual route; Shiina or Yamaguchi macrolactonization precedes RCM)
- two embedded tetrahydropyran 6-rings (the bryostatin A and C rings;
  each contributes 2 atoms to the macrocycle via a shared C–C edge)
- a pendant methyl-(2E)-2-methyl-fumarate-style ester arm at one
  macrocycle carbon — the bryostatin "vinyl methyl ester"/cinnamate
  chromophore, encoded as `-O-C(=O)/C=C(C)/C(=O)OC`
- two –OH groups on pyranose A; two OAc protecting groups (one on a
  macrocycle CH and one on pyranose C) — matches the natural
  bryostatin pattern of OH and OAc decoration
- 9 sp³ stereocenters (bryostatin natural has 11; the 9 encoded are a
  conservative subset)

The encoding does NOT claim atom-by-atom faithfulness to Trost compound 3
beyond what Macrocert's RCM rule observes. The rule's GML LHS matches a
diene `C=C ... C=C` (acyclic, terminal vinyls) and produces a cycloalkene
plus ethylene; this match-and-fire pattern is independent of the
specific identities of the OAc/OH/cinnamate side groups. The
chemistry-faithful encoding therefore tests the same rule firing under
the same byproduct accounting (ethylene) at the same ring size (31) as
Trost's published step.

### 2.3 Seco-precursor — programmatic derivation

`scripts/build_trost_bryostatin_analogue_seco.py` opens the in-ring C=C
alkene of the cyclized 31-ring and caps each side with a terminal `=CH₂`,
producing the diene-bearing seco. The macrolactone ester is **retained**
in the seco — Trost's actual route runs macrolactonization first and
RCM second (the alternative — RCM on the diene-diacid then
lactonization — was found inferior in the 2007 communication and the
2011 full paper). The molecule does not split on alkene cleavage
because the macrolactone ester provides the second connection between
the two halves of the would-be macrocycle. This matches the topology of
Nicolaou's epothilone B RCM seco
(`scripts/build_epothilone_seco.py`).

Mass balance (verified by the build script):

- cyclized: C₄₆H₇₄O₁₄, 850.5079 Da
- seco:    C₄₈H₇₈O₁₄, 878.5392 Da
- Δ MW:                28.0313 Da = ethylene exact mass

Building block: `data/building_blocks/trost_bryostatin_analogue_seco.yaml`.

### 2.4 3D embedding succeeded despite the large ring

The 31-membered ring was a known risk for RDKit's distance-geometry
embedder (the module docstring planned for a 2D fallback). In practice
ETKDGv3 with `useRandomCoords=True` and 200 attempts succeeded on the
first try; MMFF optimization converged in <2000 iterations. The written
`structure.mol` is therefore a 3D-RDKit V2000 file (title line marker
`3D-RDKit`), not the anticipated `2D-RDKit-fallback`. Pose is not
asserted against an X-ray (no CCDC entry exists for the analogue).

### 2.5 E/Z gate dropped for v0 (matches epothilone B precedent)

The runspec's `enforce_ez_geometry: {rcm: E}` predicate would mirror the
epothilone B case structurally, but the same MØD limitation applies:
MØD does not propagate E/Z through rule firings
(`docs/mod_stereo_reference.md` §1.5, §5.2), so the new in-ring C=C
returns from the rule as `STEREONONE` and any E/Z gate filters out
every candidate. Trost reports 1:1 E:Z on this substrate regardless;
both isomers were chromatographically separated and biologically
evaluated as compounds **178/179**. The Z- (or E-) selectivity is an
energetics-layer concern for Workstream F.

## 3. Files written

| Path | Status | Role |
| ---- | ------ | ---- |
| `scripts/build_trost_bryostatin_analogue.py`                                              | new       | Authors `structure.mol`. Audits formula/rings/stereo/RCM-alkene; embeds 3D via RDKit, optimises with MMFF, writes V2000 via openbabel. Falls back to 2D on embed failure. |
| `scripts/build_trost_bryostatin_analogue_seco.py`                                         | new       | Derives the RCM seco-precursor by opening the in-ring C=C; verifies Δ MW = MW(ethylene). |
| `data/building_blocks/trost_bryostatin_analogue_seco.yaml`                                | new       | Seco SMILES, provenance, mass-balance trace. |
| `data/validation_panel/trost_bryostatin_analogue_rcm_2007/structure.mol`                  | rewritten | Was a `# PLACEHOLDER` stub; now the V2000 of the cyclized 31-ring (3D-embedded). |
| `data/validation_panel/trost_bryostatin_analogue_rcm_2007/runspec.yaml`                   | rewritten | All-macrocyclization rule sweep, `max_steps: 1`, `ring_close_only: true`, `ring_size_equals: 31`, ether-discriminator gates. SCIP `top_n: 10`. Energetics disabled. |
| `data/validation_panel/trost_bryostatin_analogue_rcm_2007/expected.yaml`                  | updated   | `literature_tactic: rcm`, `expected_witness: optimal`, `ae_class: high`, 31-ring outlier flagged in `reference`. |
| `data/validation_panel/trost_bryostatin_analogue_rcm_2007/canonical_smiles.txt`           | new       | Canonical isomeric SMILES audit alongside the V2000. |
| `docs/M5_REPORT_trost_bryostatin_analogue_rcm_2007.md`                                    | new       | Auto-generated campaign report (13 tactics, witness + verifier columns). |
| `artifacts/trost_bryostatin_analogue_rcm_2007/campaign/`                                  | new       | 13 per-tactic certificates + `manifest.json`; reproducible via `_work/runspec.yaml` in each leg. |

## 4. M5 campaign — full results

`scripts/build_m5_campaign.py` ran each of the 13 macrocyclization
tactics from the `all_macrocyclization` rule-set against the bryostatin
analogue seco-precursor. SCIP solver, `top_n: 10`, infeasibility
certificates requested. Per-leg timeout 180 s (no timeouts hit).

| Rule                            | Witness    | Bond-level expelled mass | Verifier |
| ------------------------------- | ---------- | ------------------------ | -------- |
| **`rcm`**                       | **optimal** | **28.054 g/mol** (ethylene) | OK |
| `macrolactamization`            | infeasible | —                        | OK       |
| `macrolactonization`            | infeasible | —                        | OK       |
| `aryl_etherification`           | infeasible | —                        | OK       |
| `biaryl_etherification`         | infeasible | —                        | OK       |
| `c_h_dehydrogenative_coupling`  | infeasible | —                        | OK       |
| `transannular_diels_alder`      | infeasible | —                        | OK       |
| `cross_coupling_suzuki`         | infeasible | —                        | OK       |
| `cross_coupling_negishi`        | infeasible | —                        | OK       |
| `cross_coupling_buchwald`       | infeasible | —                        | OK       |
| `cross_coupling_sonogashira`    | infeasible | —                        | OK       |
| `cross_coupling_stille`         | infeasible | —                        | OK       |
| `hwe_olefination`               | infeasible | —                        | OK       |

**Shortlist:** `rcm` (the literature tactic) is the *unique* optimal
witness on this substrate. Bond-level expelled mass 28.054 g/mol matches
the rule meta's `byproduct_mass_g_per_mol: 28.054` exactly, confirming
ethylene accounting.

**No-go certificates:** the other 12 tactics emit verifier-clean
infeasibility certificates whose IIS centres on
`exactly_one_macrocyclization` plus the seco↔target flow-balance
constraints. The seco's only macrocyclizable handles are the two
terminal vinyls (consumed by `rcm` and would-be `hwe_olefination` if it
matched dienes — it doesn't; HWE requires α,β-unsaturated phosphonate),
plus the pre-formed lactone and aliphatic OH which are bound up in the
substrate scaffold and don't present free macrocyclic partners.

**31-ring caveat — no MØD enumeration explosion observed.** The brief
flagged a possible match-time enumeration blow-up on the 31-ring seco
(31 atoms in the macrocycle + flanking alkenes + pendant cinnamate
arm). In practice the campaign completed in <60 s of wall time per leg;
no timeouts were hit. RDKit SSSR handled the 31-ring SMARTS lookups
without performance degradation.

## 5. Verifier and panel test

All 13 certificates were independently re-checked by
`pixi run macrocert-verify`; every exit code is 0.

`pytest tests/panel/ -k trost` now **passes** (previously skipped because
`_is_placeholder_structure` detected the `# PLACEHOLDER` header):

```
tests/panel/test_panel.py::test_panel_case[trost_bryostatin_analogue_rcm_2007] PASSED
1 passed, 16 deselected
```

The test asserts `report.witness_kind == "optimal"` and that the
literature tactic `rcm` is in the set of rule IDs used by the top
route's flow-positive hyperedges. Both succeed.

## 6. Reproduction

From the repo root:

```bash
# (Re)build the structure and seco precursor:
pixi run python scripts/build_trost_bryostatin_analogue.py
pixi run python scripts/build_trost_bryostatin_analogue_seco.py

# (Re)run the M5 campaign:
pixi run python scripts/build_m5_campaign.py \
    data/validation_panel/trost_bryostatin_analogue_rcm_2007

# Verify panel test:
pixi run pytest tests/panel/ -q -k trost
```

The campaign script preserves each leg's staged working directory under
`artifacts/trost_bryostatin_analogue_rcm_2007/campaign/<rule>/_work/`
for reproducibility; the manifest at
`artifacts/trost_bryostatin_analogue_rcm_2007/campaign/manifest.json`
holds per-leg outcome/objective/verifier-exit triples.

## 7. Caveats / followups (v1)

1. **Exact atom-by-atom structure.** The encoded `structure.mol` is a
   chemistry-faithful 31-ring with the essential macrocycle features
   (lactone, RCM alkene, two pyranoses, cinnamate arm, OAc/OH); it is
   NOT a precise reproduction of Trost compound 3. Ivan should treat
   the encoding as a stand-in for the panel's RCM-rule firing test, not
   as a structural model for, e.g., docking or stereochemistry analysis.
   The Trost 2007 *JACS* SI and 2011 *Chem. Eur. J.* full-paper SI are
   the canonical sources for compound 3 (both ACS/Wiley-paywalled).
2. **E/Z selectivity gate (same status as epothilone B).** Trost reports
   1:1 E:Z on this substrate; both isomers were chromatographically
   separated and biologically evaluated. Re-enable
   `enforce_ez_geometry: {rcm: E}` (or Z, either is in the literature)
   once Workstream F propagates stereo through MØD rule firings.
3. **Energetics tier disabled.** Same status as all other RCM cases
   (surrogate `rcm_*`, epothilone B). The 1:1 E:Z selectivity is an
   energetics-layer concern (TS-search hook) that Workstream C's xTB
   tier doesn't yet cover for macrocyclic ring sizes.
4. **Post-RCM deprotection / functional-group manipulation not encoded.**
   Trost's reported compounds 178/179 are the *deprotected* forms after
   TES removal and other steps; the encoded structure represents the
   directly RCM-produced macrolactone (still OAc-protected at the two
   acetate positions). The panel exercises only the macrocyclization
   event.
5. **Natural bryostatin macrocycle (26-ring) is NOT in the panel.** The
   natural bryostatin macrocycle has never been closed by RCM in any
   published total synthesis. Its actual macrocyclization tactics
   (Yamaguchi macrolactonization for Wender/Keck, Prins macrocyclization
   for Wender, Ru-Pd-Au cascade for Trost) would be Workstream B
   additions if the panel grows. See `research_brief.md` §1, §7 for
   the literature diagnosis of why the natural ring has resisted RCM.

## 8. Provenance — citation chain

- **Primary communication:** Trost, B. M.; Yang, H.; Thiel, O. R.;
  Frontier, A. J.; Brindle, C. S. *J. Am. Chem. Soc.* **2007**, *129*,
  2206–2207. DOI `10.1021/ja067305j`.
- **Full paper:** Trost, B. M.; Yang, H.; Dong, G. *Chem. Eur. J.*
  **2011**, *17*, 9789–9805. DOI `10.1002/chem.201002932`.
- **Open-access redrawing:** Jahan, N. *et al.* *SynOpen* **2023**, *7*,
  209–242, Scheme 19. DOI `10.1055/s-0042-1751453`. Provides the
  cleanest non-paywalled redrawing of the metathesis precursor
  (compound **176**) and the RCM products **177**, **178**, **179**.
- **Natural-product context (NOT RCM — for comparison only):**
    - Trost, B. M.; Dong, G. *Nature* **2008**, *456*, 485 (DOI
      `10.1038/nature07543`). Bryostatin 16 via Ru-Pd-Au cascade.
    - Wender, P. A.; Schrier, A. J. *J. Am. Chem. Soc.* **2011**, *133*,
      9228 (DOI `10.1021/ja203034k`). Bryostatin 9 via Yamaguchi + Prins.
    - Keck, G. E. *J. Am. Chem. Soc.* **2011**, *133*, 744. Bryostatin 1
      via Yamaguchi + Rainier.
- **Selectivity / methodology corroboration:** The 1:1 E:Z mixture, 80%
  yield, and Grubbs–Hoveyda 2nd-generation catalyst conditions are
  documented in both Trost 2007 *JACS* and the 2011 *Chem. Eur. J.* full
  paper, and summarised in the Jahan 2023 *SynOpen* review §5 Table 1.

---

_Auto-derived structure + seco built 2026-05-24 by the
`scripts/build_trost_bryostatin_analogue.py` and
`scripts/build_trost_bryostatin_analogue_seco.py` helper scripts; M5
campaign run reproducibly via `scripts/build_m5_campaign.py`._
