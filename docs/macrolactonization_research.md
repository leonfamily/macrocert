# Macrolactonization Rule — Chemistry Research Brief

**Workstream:** C (Rule library expansion)
**Target artifacts:** `data/rules/macrolactonization.gml` + `.meta.yaml`, plus a panel substrate
**Date:** 2026-05-24
**Author:** researcher agent (for Ivan / Workstream C)

This brief grounds the design of the macrolactonization rule. It mirrors the structural choices already made in `macrolactamization.gml/.meta.yaml` (the closest cousin — amide rather than ester) so the verifier and rule loader treat the two consistently, but it differs in two important places: the activator chemistry is more diverse (no single dominant reagent like HATU), and the literature panel (erythronolide B + a polyketide) sits directly on top of this rule, so the activator alternatives table has to be expressive enough to carry both Yamaguchi and Corey–Nicolaou for the same surrogate target.

---

## Section 1 — Atom-mapped reaction scheme

The bond-level chemistry is the textbook condensation

$$
\text{R--COOH} + \text{HO--R'} \;\longrightarrow\; \text{R--C(=O)--O--R'} + \text{H}_2\text{O}
$$

with H₂O the only byproduct. Atom-economy at the bond level is therefore identical to macrolactamization (only the expelled small molecule changes: H₂O here vs. H₂O for the amide too — the difference is process-level, not bond-level).

### Atom numbering (mirrors `macrolactamization.gml`)

| ID  | Element | Role                                                                            |
| --- | ------- | ------------------------------------------------------------------------------- |
| 1   | C       | Acid carbonyl carbon — **retained**, becomes ester C                            |
| 2   | O       | Acid carbonyl O (C=O) — **retained** in product                                 |
| 3   | O       | Acid hydroxyl O (C–OH) — **expelled** in H₂O                                    |
| 4   | H       | Acid OH proton — **expelled** in H₂O                                            |
| 5   | O       | Alcohol O — **retained**, becomes the C–O–C ester oxygen                        |
| 6   | H       | Alcohol OH proton — **expelled** in H₂O                                         |

(IDs 1–4 are identical to the macrolactamization rule; ID 5 is the alcohol O — same slot as the amine N in the lactam rule; ID 6 is the alcohol H — same slot as the amine H.)

### Bond changes

**Broken (in L):**
- 1–3 (C–OH single bond of the acid)
- 3–4 (O–H of the acid hydroxyl)
- 5–6 (O–H of the alcohol)

**Preserved (in context):**
- 1=2 (C=O of the carbonyl)
- The C–C bond from the seco-acid carbon (1) to its α-carbon (off-rule; lives in the substrate)
- The C–O bond from the alcohol carbon to atom 5 (off-rule; lives in the substrate)

**Formed (in R):**
- 1–5 (the new ester C–O bond, closing the ring)
- 3–4 and 3–6 (the two O–H bonds of the expelled H₂O)

### Mass balance check

- L mass: HO–C(=O)–R + R′–OH
- R mass: R–C(=O)–O–R′ + H₂O
- Net: −2 H, −1 O moves out as water (18.015 g/mol). Identical to the lactam rule.

### Where the H₂O comes from

Atoms 3 (acid hydroxyl O), 4 (acid OH H), and 6 (alcohol OH H) reassemble into the expelled water on the R side. The carbonyl oxygen (2) stays with the ester. This is the conventional, mechanism-agnostic depiction. The actual mechanism in a Yamaguchi/Shiina mixed-anhydride pathway expels a different oxygen atom in detail (the acid hydroxyl O leaves *with the activator*, not as water — water is liberated only at the workup or activator-hydrolysis step), but the **net** atom flow over the full process is exactly what the rule depicts, and the rule is consistent with the macrolactamization rule's idealization. This is fine and standard for MØD-style bond-graph rewriting: the rule encodes the **stoichiometric** outcome, and the process penalty captures the activator's mass cost separately.

---

## Section 2 — Canonical activator recommendation

**Recommendation: Yamaguchi (2,4,6-trichlorobenzoyl chloride, TCBC) + DMAP + Et₃N** as the canonical activator, with `reagent_mass_g_per_mol: 568.0` (= 1 × TCBC + 2 × Et₃N + 1 × DMAP).

### Justification

| Criterion | Yamaguchi (TCBC/DMAP/Et₃N) | Shiina (MNBA/DMAP) | Corey–Nicolaou (PySSPy/PPh₃) | Mukaiyama (CMPI/Et₃N) |
|---|---|---|---|---|
| First reported | 1979 | 2002 | 1974 | 1976 |
| Substrate scope | Very broad; the workhorse | Very broad, milder | Narrower; historic | Narrow; superseded |
| Conditions | High dilution, refluxing toluene | High dilution, rt–60 °C | High dilution, refluxing xylene | High dilution, refluxing CH₂Cl₂ |
| Reliability across complex substrates | Excellent | Excellent; better for base-sensitive | Sensitive to oligomerization; needs Ag⁺ for difficult cases | Mixed |
| Modern usage trend | **Still the most-cited macrolactonization method in total synthesis** ([[Parenty Moreau Niel Campagne 2013 - Macrolactonizations Update|Parenty et al. (2013)]] survey: dominant method in 2006–2012 syntheses) | Strong rising adoption since 2005, esp. for base-sensitive or epimerization-prone substrates | Historical importance (erythronolide B!) but now niche | Niche / superseded |
| Reagent + auxiliary mass | TCBC 243.9 + 2 Et₃N (~202) + DMAP 122 = **~568** g/mol | MNBA 344.3 + 2 DMAP 244 = **~588** g/mol | PySSPy 220.3 + PPh₃ 262.3 = **~483** g/mol (but byproducts add 280 g of TPPO!) | CMPI 255.5 + 2 Et₃N (~202) = **~458** g/mol |
| Byproduct mass (post-activation, beyond H₂O) | 2,4,6-Cl₃C₆H₂COOH 225 + Et₃N·HCl 137 | 2 × 2-Me-6-NO₂-C₆H₃COOH (= 2 × 181 = **362**) | 2-mercaptopyridine 111 + Ph₃P=O 278 = **389** | 1-Me-2-pyridone 109 + Et₃N·HI 230 |
| Comments | Industry-default; well-precedented for sterically demanding seco-acids; primary panel target erythronolide A used it ([[Hikota Tone Horita Yonemitsu 1990 - Erythronolide A Macrolactonization|Hikota et al. (1990)]]). | "Greener" — DMAP is catalytic; near-equimolar acid:alcohol; byproduct is innocuous aryl-acid. | The original method; Corey 1978 erythronolide B uses this. Will be needed for that panel case. | Largely of historical interest. |

Yamaguchi wins canonical status on **three** grounds:

1. **Frequency of use** — both Parenty reviews (2006 + 2013) confirm it as the single most-used macrolactonization method in modern total synthesis, and the [[Hikota Tone Horita Yonemitsu 1990 - Erythronolide A Macrolactonization|Hikota–Yonemitsu (1990)]] "modified Yamaguchi" protocol is the *de facto* default for sterically demanding macrolides. If the user does not override, Yamaguchi is the right prior.
2. **Reagent mass parity with macrolactamization** — Yamaguchi at ~568 g/mol is on the same order as HATU + 2 DIPEA (638 g/mol) in the lactam rule. The bond-vs-process AE message stays consistent: process penalty is ~30× the bond-level byproduct mass, regardless of whether the closure is C–N or C–O.
3. **Panel case coverage** — One of the two literature panel cases (Yamaguchi 1981 erythronolide A, or Hikota/Yonemitsu modified-Yamaguchi version) uses this activator directly. Choosing it as canonical means the panel runs without an activator override.

Corey–Nicolaou (for erythronolide B Corey 1978) and Shiina (for the second polyketide panel case, likely amphotericin/megalomicin family) should ride in `reagent_mass_alternatives` and be selected per-RunSpec.

---

## Section 3 — Activator alternatives table (for `reagent_mass_alternatives`)

The columns are: total reagent mass per ring closure (activator + auxiliary base/catalyst), and the post-activation byproduct mass *in addition* to the H₂O accounted for at the bond level. The byproduct mass is what gets debited against process-level atom economy *after* the rule has expelled its 18.015 g/mol of water.

| Activator | Coupling agent | Auxiliaries (typical) | reagent_mass_g_per_mol | byproduct_mass_g_per_mol (in addition to H₂O) | Typical scope | Reference DOI |
|---|---|---|---|---|---|---|
| **Yamaguchi (canonical)** | 2,4,6-Cl₃C₆H₂COCl (TCBC), 244 | 2 Et₃N (202) + DMAP (122) | **568** | 2,4,6-Cl₃C₆H₂COOH (225) + Et₃N·HCl (137) ≈ **362** | Workhorse; broad scope; preferred for sterically demanding seco-acids; minor epimerization risk for some α-stereocenters | 10.1246/bcsj.52.1989 |
| **Shiina (MNBA)** | 2-Me-6-NO₂-C₆H₃-C(O)-O-C(O)-2-Me-6-NO₂-C₆H₃ (MNBA), 344 | DMAP (122, catalytic, but practically 1 equiv for macrolactonization) | **466** | 2 × 2-Me-6-NO₂-C₆H₃COOH (181 each) = **362** | Mild; near-equimolar; excellent for base-sensitive substrates (Shiina report says no isomerization where Yamaguchi gave 50% isomerization on enals) | 10.1016/s0040-4039(02)01819-1 |
| **Corey–Nicolaou** | 2,2′-dipyridyl disulfide (PySSPy), 220 | PPh₃ (262); xylene reflux; AgBF₄ for difficult cases | **482** | 2-mercaptopyridine (111) + Ph₃P=O (278) ≈ **389** | Historic; the canonical method for erythronolide B (Corey 1978); requires high temperature; oligomerization risk on long chains | 10.1021/ja00824a073 |
| **Mukaiyama (CMPI)** | 2-chloro-1-methylpyridinium iodide (CMPI / Mukaiyama's salt), 256 | 2 Et₃N (202) | **458** | 1-methyl-2-pyridone (109) + Et₃N·HI (230) ≈ **339** | Largely of historical interest; still occasionally used; mild but narrow scope | 10.1246/cl.1976.49 |
| **EDC/DMAP (Keck–Boden Steglich variant)** | EDC·HCl (192) | DMAP (122) + DMAP·HCl (159) | **473** | EDU (1-ethyl-3-(3-dimethylaminopropyl)urea, 173) | Mild and reliable but oligomerization is a risk; high dilution mandatory; preferred for small lactones | 10.1021/jo00213a044 |
| **T3P** | Propanephosphonic acid anhydride trimer (T3P, 318) | Et₃N (101) + (optional) DMAP (122) | **541** | Open-chain propanephosphonic acid trimer (water-soluble, ≈ 372) | Modern, green-chemistry option; very clean workup; underused in classical macrolactonization but emerging | 10.1016/j.tetlet.2013.08.082 |

**Notes on the byproduct column.** All values are *additional* to the 18.015 g/mol of water expelled by the bond-level rule. They represent the activator-derived waste that the process must dispose of. For Yamaguchi, the 225 g comes from the aryl part of TCBC ending up as 2,4,6-trichlorobenzoic acid; the 137 g is the Et₃N·HCl salt that forms from the chloride leaving group. For Shiina, MNBA cleaves symmetrically and both arms leave as the free acid (2 × 181). For Corey–Nicolaou, the PPh₃ ends up as TPPO (the famously hard-to-remove byproduct flagged in [[Scientific Update 2024 - Triphenylphosphine Oxide Waste|Scientific Update review]]), and one 2-pyridyl unit ends up as 2-mercaptopyridine. For EDC, the urea byproduct (EDU) is the canonical Steglich coupling waste.

**Process-AE intuition.** Yamaguchi closes ~250 g of byproduct + ~310 g of "spent activator equivalent" per mole of ester formed; the bond-level rule sees only 18 g. The bond-vs-process gap is ~30×, in keeping with the macrolactamization rule's HATU example.

---

## Section 4 — Stereochemical handling

### Preservation of stereo at the alcohol's carbon

For the canonical Yamaguchi/Shiina/Corey–Nicolaou/Mukaiyama/EDC family: **the alcohol's carbon stereo is fully retained**. None of these activators do anything to the C–O bond of the alcohol; the activator works only on the acid side. The alcohol attacks the activated acyl species in a standard $\text{S}_\text{N}$ acyl addition–elimination, with no inversion or scrambling at the alcohol's α-carbon. This is identical to macrolactamization at the amine N.

### Preservation of stereo at the acid's α-carbon

**Mostly retained**, but with two important caveats:

1. **Mild epimerization risk under Yamaguchi conditions.** The mixed-anhydride intermediate is electrophilic enough that an enolizable α-stereocenter (especially one with a β-carbonyl, β-aryl, or strongly enolizing motif) can racemize. Et₃N is a mild base, but DMAP-catalyzed acyl transfer goes through a tetrahedral intermediate that can deprotonate. In total-synthesis practice this is rare but documented — the [[Parenty Moreau Niel Campagne 2013 - Macrolactonizations Update|Parenty 2013 update]] flags several cases where Yamaguchi caused undesired epimerization and Shiina was the rescue.
2. **Shiina is cleaner on epimerization-prone substrates** because the basic site (DMAP) is catalytic and the byproduct (the aryl carboxylate) is itself the proton trap, so the local pH is gentler. The [[Modern Macrolactonization Techniques - Xingwei Li PDF|Xingwei Li review]] notes a 50% isomerization mass-balance loss under Yamaguchi vs. essentially none under acyl-enamide on a base-sensitive enal seco-acid.

### Inversion modes

**Yes — the Mitsunobu macrolactonization inverts the alcohol's carbon.** This is the major exception to the "retains everything" story. Mitsunobu (DIAD/DEAD + PPh₃) activates the **alcohol** rather than the acid; the carboxylate attacks the alcohol's carbon in an $\text{S}_\text{N}2$ fashion, giving **clean inversion** at that center. This is a distinct mechanistic class from the canonical activators above. If the rule library ever supports an `inversion_modes` annotation, Mitsunobu macrolactonization should appear as a separate rule (or a `mitsunobu_variant` flag) — not in the alternatives table for the standard rule.

For v0, we list Mitsunobu only in `notes:` and not in the alternatives table, because mixing retentive and inverting modes under one rule will mislead the verifier. Workstream F (stereo) should later add an explicit `mitsunobu` boolean to enable the inversion variant.

### Stereo flags to declare

For the canonical rule:

```yaml
stereo_flags:
  - retains_alpha_stereo
  - retains_alcohol_stereo
  - mild_alpha_epimerization_risk    # Yamaguchi/DMAP-mediated; Shiina rescues
```

(`retains_alpha_stereo` is the same flag the lactam rule uses; `retains_alcohol_stereo` is new and analogous; `mild_alpha_epimerization_risk` is an honest declaration of the well-documented edge case.)

---

## Section 5 — Citation list

The 10 key DOIs, with one-line summaries:

1. [[Inanaga Hirata Saeki Katsuki Yamaguchi 1979 - Mixed Anhydride Macrolactonization|Inanaga, Hirata, Saeki, Katsuki, Yamaguchi (1979)]] — `10.1246/bcsj.52.1989`
   *The original Yamaguchi paper. Mixed-anhydride method using 2,4,6-trichlorobenzoyl chloride + DMAP for esterification and macrolactonization. Bull. Chem. Soc. Jpn. 52, 1989–1993. 2087 citations — canonical reference.*

2. [[Shiina Kubota Ibuka 2002 - MNBA Macrolactonization|Shiina, Kubota, Ibuka (2002)]] — `10.1016/s0040-4039(02)01819-1`
   *Introduces MNBA (2-methyl-6-nitrobenzoic anhydride) as a dehydration condensing agent for macrolactonization. Tetrahedron Lett. 43, 7535–7539. Modern alternative when DMAP basicity is a problem.*

3. [[Corey Nicolaou 1974 - Macrolactonization|Corey, Nicolaou (1974)]] — `10.1021/ja00824a073`
   *The double-activation method. 2,2′-Dipyridyl disulfide + PPh₃ generates an acyl-2-pyridyl thioester that closes via intramolecular proton transfer. JACS 96, 5614–5616. 471 citations.*

4. [[Mukaiyama Usui Saigo 1976 - CMPI Lactonization|Mukaiyama, Usui, Saigo (1976)]] — `10.1246/cl.1976.49`
   *The original Mukaiyama macrolactonization with 2-chloro-1-methylpyridinium iodide. Chem. Lett. 5, 49–50. Useful because it explicitly tested ω-hydroxyacids n = 5, 7, 10, 11, 14 — directly relevant for our toy substrate.*

5. [[Boden Keck 1985 - EDC DMAP Macrolactonization|Boden, Keck (1985)]] — `10.1021/jo00213a044`
   *The Steglich–Boden–Keck variant: EDC + DMAP + DMAP·HCl. Proton-transfer steps clarified. J. Org. Chem. 50, 2394–2395. 416 citations.*

6. [[Parenty Moreau Campagne 2006 - Macrolactonizations Review|Parenty, Moreau, Campagne (2006)]] — `10.1021/cr0301402`
   *Comprehensive Chem. Rev. on macrolactonization in total synthesis up to ~2005. Chem. Rev. 106, 911–939. 470 citations. The reference for "which method got used where".*

7. [[Parenty Moreau Niel Campagne 2013 - Macrolactonizations Update|Parenty, Moreau, Niel, Campagne (2013)]] — `10.1021/cr300129n`
   *2013 update of the 2006 review. Chem. Rev. 113, PR1–PR40. Critical for Shiina adoption trend and modern method comparison.*

8. [[Corey Kim Yoo Nicolaou Melvin Brunelle Falck Trybulski Lett Sheldrake 1978 - Erythronolide B Total Synthesis|Corey et al. (1978)]] — `10.1021/ja00482a063`
   *Corey's total synthesis of erythronolide B (JACS 100, 4620–4622). The canonical Corey–Nicolaou macrolactonization application; will be the panel case for "panel_TODO" erythronolide B.*

9. [[Hikota Tone Horita Yonemitsu 1990 - Erythronolide A Modified Yamaguchi|Hikota, Tone, Horita, Yonemitsu (1990)]] — `10.1021/jo00288a004`
   *The "modified Yamaguchi" with DMAP·HCl additive. Achieves extremely efficient erythronolide A macrolactonization. J. Org. Chem. 55, 7–9. The reference for Yamaguchi-on-erythromycins.*

10. [[Cordes Heretsch 2025 - Macrolactonizations Comprehensive Organic Synthesis|Cordes, Heretsch (2025)]] — `10.1016/b978-0-323-96025-0.00024-7`
    *2025 chapter in Comprehensive Organic Synthesis covering macrolactonizations in total synthesis. The most recent survey; use as the modern reference review.*

Bonus reference (not in the 10 but worth keeping):
- [[Saigo Usui Kikuchi Shimada Mukaiyama 1977 - Carboxylic Esters|Saigo et al. (1977)]] — `10.1246/bcsj.50.1863`. The follow-up Mukaiyama paper extending the method to general esterification.

---

## Section 6 — Proposed `meta.yaml` (full draft, ready for review)

```yaml
# Macrolactonization rule metadata (consumed by macrocert.spec.rules).
# See data/rules/macrolactonization.gml for the DPO span. Application
# conditions (ring closure on a single component, ring-size membership in
# the macrocyclic range, etc.) live in macrocert.generate.strategies,
# not here.

# Process-level reagent mass: activator + auxiliaries per firing.
# Canonical activator: Yamaguchi (2,4,6-trichlorobenzoyl chloride, TCBC).
# Mass: 1 x TCBC (244) + 2 x Et3N (101 each) + 1 x DMAP (122) = ~568 g/mol.
# This is the default; per-substrate overrides in RunSpec.solver.extra
# can select an alternative from `reagent_mass_alternatives` below.
reagent_mass_g_per_mol: 568.0

# Bond-level expelled mass: water, from the rule's atom-map (atoms 3, 4, 6
# form the H2O byproduct on the R side). Recomputed by the verifier in
# M2 from the composed rule; kept here as a human-checkable ground truth.
byproduct_mass_g_per_mol: 18.015

# Which atom ID in the rule body anchors the *retained* product side on R.
# Used by the verifier's bond-level AE recomputation: BFS from this atom
# through R's edges; everything reachable is target, the rest is byproduct.
retained_root_atom: 1

classes:
  - macrocyclization
  - ester_closure
  - high_atom_economy_bond  # H2O byproduct only
  - polyketide              # erythronolide / megalomicin / amphotericin family

# Activator alternatives. Each entry overrides reagent_mass_g_per_mol
# at the RunSpec layer. byproduct_mass_extra is the *additional* mass
# beyond the bond-level 18.015 g/mol of water; the verifier adds it to
# the H2O byproduct when computing process-AE under that activator.
reagent_mass_alternatives:
  yamaguchi:
    reagent_mass_g_per_mol: 568.0
    byproduct_mass_extra: 362.0   # 2,4,6-Cl3C6H2COOH (225) + Et3N.HCl (137)
    description: "TCBC + 2 Et3N + DMAP; the canonical workhorse"
    doi: "10.1246/bcsj.52.1989"
  shiina:
    reagent_mass_g_per_mol: 466.0
    byproduct_mass_extra: 362.0   # 2 x 2-Me-6-NO2-C6H3COOH (181 each)
    description: "MNBA + DMAP; milder, near-equimolar, less epimerization"
    doi: "10.1016/s0040-4039(02)01819-1"
  corey_nicolaou:
    reagent_mass_g_per_mol: 482.0
    byproduct_mass_extra: 389.0   # 2-mercaptopyridine (111) + Ph3P=O (278)
    description: "2,2'-Dipyridyl disulfide + PPh3; double-activation; erythronolide B"
    doi: "10.1021/ja00824a073"
  mukaiyama:
    reagent_mass_g_per_mol: 458.0
    byproduct_mass_extra: 339.0   # 1-Me-2-pyridone (109) + Et3N.HI (230)
    description: "2-Cl-1-Me-pyridinium iodide + 2 Et3N; historic"
    doi: "10.1246/cl.1976.49"
  edc_dmap:
    reagent_mass_g_per_mol: 473.0
    byproduct_mass_extra: 173.0   # EDU
    description: "Steglich-Boden-Keck variant; EDC + DMAP + DMAP.HCl"
    doi: "10.1021/jo00213a044"
  t3p:
    reagent_mass_g_per_mol: 541.0
    byproduct_mass_extra: 372.0   # propanephosphonic acid trimer (water-soluble)
    description: "T3P + Et3N; modern, green, clean workup"
    doi: "10.1016/j.tetlet.2013.08.082"

stereo_flags:
  - retains_alpha_stereo
  - retains_alcohol_stereo
  - mild_alpha_epimerization_risk   # Yamaguchi/DMAP can scramble alpha-CH next to enolizable groups; Shiina rescues

refs:
  - "Trost 1991, Science 254:1471 (atom economy)"
  - "Inanaga, Hirata, Saeki, Katsuki, Yamaguchi 1979, Bull. Chem. Soc. Jpn. 52:1989, DOI:10.1246/bcsj.52.1989 (canonical Yamaguchi)"
  - "Shiina, Kubota, Ibuka 2002, Tetrahedron Lett. 43:7535, DOI:10.1016/s0040-4039(02)01819-1 (MNBA)"
  - "Corey, Nicolaou 1974, J. Am. Chem. Soc. 96:5614, DOI:10.1021/ja00824a073 (Corey-Nicolaou double activation)"
  - "Parenty, Moreau, Niel, Campagne 2013, Chem. Rev. 113:PR1, DOI:10.1021/cr300129n (modern review)"

notes: |
  Ester-bond ring closure expelling H2O at the bond level. Process-level AE
  is docked by the activator -- Yamaguchi (TCBC + DMAP + 2 Et3N, ~568 g/mol)
  is assumed canonical, with Shiina / Corey-Nicolaou / Mukaiyama / EDC-DMAP /
  T3P available as alternatives via reagent_mass_alternatives. This is the
  proposal section 3.3 bond-vs-process AE split materialized; the choice of
  activator is the place where the split is most visible since reagent mass
  varies by ~25% across the family while byproduct mass varies by ~2x.

  Mitsunobu macrolactonization (DIAD/DEAD + PPh3, activates the alcohol
  instead of the acid, inverts the carbon bearing OH) is NOT covered by this
  rule -- it is a stereo-inverting variant and should be a separate rule
  if/when added (Workstream F).

  Erythronolide B (Corey 1978, DOI:10.1021/ja00482a063) and erythronolide A
  (Hikota-Yonemitsu 1990 modified Yamaguchi, DOI:10.1021/jo00288a004) are
  the panel cases.
```

---

## Section 7 — Proposed GML structure

The GML file should mirror `macrolactamization.gml` almost exactly, with O substituted for N at ID 5. Here is the structural description (not valid MØD syntax, but ready for transcription):

```
rule [
    ruleID "macrolactonization (ester ring closure, -H2O)"
    # L: carboxylic acid carbon (1)=O(2) / -O(3)-H(4)  and alcohol O(5)-H(6)
    left [
        node [ id 2 label "O" ]   # acid carbonyl O -- retained
        node [ id 3 label "O" ]   # acid hydroxyl O -- expelled in H2O
        node [ id 4 label "H" ]   # acid OH proton -- expelled in H2O
        node [ id 6 label "H" ]   # alcohol OH proton -- expelled in H2O
        edge [ source 1 target 3 label "-" ]   # acid C-O(H) bond, broken
        edge [ source 3 target 4 label "-" ]   # acid O-H, broken
        edge [ source 5 target 6 label "-" ]   # alcohol O-H, broken
    ]
    context [
        node [ id 1 label "C" ]   # acid carbonyl C
        node [ id 5 label "O" ]   # alcohol O -- becomes ester O
        edge [ source 1 target 2 label "=" ]   # C=O preserved
    ]
    # R: ester C(1)(=O(2))-O(5) plus expelled H2O (atoms 3, 4, 6)
    right [
        node [ id 2 label "O" ]
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]   # new ester C-O bond
        edge [ source 3 target 4 label "-" ]   # H2O O-H
        edge [ source 3 target 6 label "-" ]   # H2O O-H
    ]
]
```

**Key sections:**

- **`left`**: declares the four "to-be-expelled or rearranged" atoms (the two H's, the soon-to-be-water O, and the carbonyl O which is just listed for completeness because it appears in both L and R), and the three bonds that break (C–O(H) of the acid; O–H of the acid; O–H of the alcohol).
- **`context`**: the two atoms whose identity and existence don't change — the acid carbonyl C (1) and the alcohol O (5). The C=O double bond is also in context because it survives unchanged into the ester. Note that we keep node 2 (carbonyl O) in L and R but not in context, mirroring the macrolactamization rule's convention. The C=O edge is declared in context.
- **`right`**: declares the new ester bond (1–5) and the two O–H bonds that reconstruct water from atoms 3, 4, 6.

**Difference from `macrolactamization.gml`:**

The only line that changes is node 5's label: `"N"` becomes `"O"`. Everything else is structurally identical (same IDs, same bond-pattern, same atom count in L/R/context). This is by design — the verifier should be able to recognize the two rules as "siblings" of an abstract `heteroatom_closure` family.

**Verifier sanity checks the rule should pass:**

- BFS from `retained_root_atom: 1` through R-side edges reaches atoms 1, 2, 5 (the C=O–O ester triplet, then onto the substrate context). It does **not** reach atoms 3, 4, 6 (the H₂O), so they are correctly classified as byproduct.
- Mass balance: L mass − R mass = 0 (atoms 3, 4, 6 appear on both sides). Bond-mass delta: 3 bonds broken (1–3, 3–4, 5–6), 3 bonds formed (1–5, 3–4, 3–6). Atoms conserved. ✓
- Byproduct mass: M(O) + 2·M(H) = 15.999 + 2·1.008 = 18.015 g/mol. Matches `byproduct_mass_g_per_mol`. ✓

---

## Section 8 — Toy substrate proposal

**Recommendation:** Add a single new panel case, `lactone_16_from_15_hydroxypentadecanoic_acid`, parallel to the existing `lactam_16_from_15_aminopentadecanoic_acid` lactam panel.

### Why this substrate

- **Direct cousin of the existing lactam panel.** The existing lactam panel uses ω-aminoacid surrogates of size 12, 14, 16, 20. The natural ester cousin replaces the ω-amino with ω-hydroxy. We pick 15-hydroxypentadecanoic acid (C₁₅H₃₀O₃, MW 258.40) because it closes to a **16-membered ring**, matching the 16-membered lactam panel case exactly and giving the τ-calibration code a clean ester-vs-amide comparison at the same ring size.
- **The product is Exaltolide® (cyclopentadecanolide / 15-pentadecanolide, CAS 106-02-5)** — a commercially valuable musk fragrance ingredient (MW 240.39). Its industrial synthesis is well-precedented, including direct macrolactonization of 15-hydroxypentadecanoic acid by depolymerization-cyclization and (in research-lab settings) by Mukaiyama-type activation. So the surrogate has industrial credibility, parallel to the polyamide-fiber justification for the lactam surrogates.
- **Historical Mukaiyama precedent.** [[Mukaiyama Usui Saigo 1976 - CMPI Lactonization|Mukaiyama, Usui, Saigo (1976)]] explicitly tested ω-hydroxyacids with n = 5, 7, 10, 11, 14. The n = 14 case is exactly 15-hydroxypentadecanoic acid → 16-membered lactone. So the substrate has a citation-supported precedent in the original macrolactonization literature, not just by analogy.

### Panel files needed

```
data/validation_panel/lactone_16_from_15_hydroxypentadecanoic_acid/
  structure.mol      # 16-membered cyclopentadecanolide product (Exaltolide)
  runspec.yaml       # mirrors lactam_16 RunSpec, with rules: all_macrocyclization
  expected.yaml      # literature_tactic: macrolactonization, ring_size: 16
  notes.md           # cites Mukaiyama 1976 + Exaltolide industrial context
```

### Suggested `expected.yaml`

```yaml
literature_tactic: macrolactonization
literature_ring_size: 16
expected_witness: optimal
expected_top_rule_class: macrocyclization
ae_class: high
reference: |
  Surrogate macrolactonization case (16-membered ring, Exaltolide /
  cyclopentadecanolide). 15-hydroxypentadecanoic acid (n = 14 in the
  series HO(CH2)nCOOH) closes to the 16-membered musk lactone. Originally
  demonstrated by Mukaiyama, Usui, Saigo, Chem. Lett. 1976, 5, 49 (n = 14
  among the series); industrially produced as a fragrance ingredient.
  Included here to calibrate tau against the parallel lactam_16 case,
  pending the literature panel (erythronolide B / amphotericin family)
  from panel_TODO.md.
```

### Suggested `runspec.yaml`

```yaml
name: lactone_16_from_15_hydroxypentadecanoic_acid
target:
  structure_path: structure.mol
  ring_size: 16

blocks:
  - hydroxypentadecanoic_acid

rules: all_macrocyclization

strategy:
  max_steps: 1
  ring_close_only: true

solver:
  backend: scip
  top_n: 3
  time_budget_s: 30

energetics:
  enabled: false

notes: |
  Surrogate macrolactonization case (ring size 16).
  Closes via one firing of the macrolactonization rule.
  Cousin of lactam_16_from_15_aminopentadecanoic_acid.
  Real-world product: Exaltolide (musk fragrance ingredient).
```

### Also update `data/rules/_index.yaml`

The `all_macrocyclization` and `high_ae_macrocyclization` sets should both include the new `macrolactonization` rule:

```yaml
sets:
  all_macrocyclization:
    - macrolactamization
    - macrolactonization      # new
    - rcm
    - transannular_diels_alder

  high_ae_macrocyclization:
    - macrolactamization
    - macrolactonization      # new, H2O byproduct, same AE class as lactam
    - rcm
    - transannular_diels_alder

  polyketide_macrocyclization:    # new set, suggested
    - macrolactonization
    - rcm
    - transannular_diels_alder
```

---

## Open questions / followups for Ivan

1. **`reagent_mass_alternatives` field name and structure.** I have proposed a nested dict (one key per named alternative, each carrying `reagent_mass_g_per_mol`, `byproduct_mass_extra`, `description`, `doi`). Workstream F needs to add loader support. If a flatter representation is preferred (e.g., one list of dicts), the structure can be adjusted; the chemistry content is unchanged.
2. **Mitsunobu as a separate rule.** This brief explicitly excludes Mitsunobu macrolactonization from the standard rule because it inverts the alcohol carbon. Recommend a future `macrolactonization_mitsunobu.gml` with the same atom map but a `stereo_flags: [inverts_alcohol_stereo]` declaration. Not blocking for Workstream C completion.
3. **`byproduct_mass_extra` semantics in the verifier.** Right now `byproduct_mass_g_per_mol` is checked against the rule's bond-level expelled mass. The `byproduct_mass_extra` field is process-level only and never composed into the rule's bond graph. Workstream F should make sure the verifier reads it correctly (additive to H₂O for AE, but invisible to the bond-graph balance check).
4. **Panel choice for the second literature case (Workstream A).** The proposal asks for "one more S-selected from the megalomicin / amphotericin family." A natural fit using the Shiina activator would be Shiina's own MNBA macrolactonization of the erythronolide A aglycon ([[Shiina Katoh Nagai Hashizume 2010 - MNBA Erythromycin A Aglycon|Shiina et al. (2010)]], DOI: pending lookup — see ChemInform 41/23). This would give the panel a clean (Yamaguchi, Corey-Nicolaou, Shiina) coverage across the three canonical methods.

---

## Cross-references in the vault

- [[Modern Macrolactonization Techniques - Xingwei Li PDF]] — most useful comparative overview
- [[Parenty Moreau Campagne 2006 - Macrolactonizations Review]]
- [[Parenty Moreau Niel Campagne 2013 - Macrolactonizations Update]]
- [[Inanaga Hirata Saeki Katsuki Yamaguchi 1979 - Mixed Anhydride Macrolactonization]]
- [[Shiina Kubota Ibuka 2002 - MNBA Macrolactonization]]
- [[Corey Nicolaou 1974 - Macrolactonization]]
- [[Mukaiyama Usui Saigo 1976 - CMPI Lactonization]]
- [[Boden Keck 1985 - EDC DMAP Macrolactonization]]
- [[Hikota Tone Horita Yonemitsu 1990 - Erythronolide A Modified Yamaguchi]]
- [[Corey Kim Yoo Nicolaou Melvin Brunelle Falck Trybulski Lett Sheldrake 1978 - Erythronolide B Total Synthesis]]
- [[Cordes Heretsch 2025 - Macrolactonizations Comprehensive Organic Synthesis]]

(These are wiki-link placeholders — if the vault doesn't have `external.paper` nodes for them yet, they should be created with `vlt graph node add --type external.paper`. Standard procedure per [[Wiki-link Papers|the project's paper-linking policy]].)
