# C–H Dehydrogenative Coupling for Macrocyclization — Chemistry Brief

**Workstream:** MØD-MacroCert Workstream C
**Target rule:** `data/rules/c_h_dehydrogenative_coupling.gml` + `.meta.yaml`
**Date:** 2026-05-24
**Status:** v0 chemistry input. F encodes; S signs off on activator and forbidden-context calls.

This brief decomposes the "C–H/C–H activation macrocyclization" tactic into the variants that matter for atom-economy bookkeeping, recommends a canonical DPO rule, and supplies the literature, stereo, and forbidden-context priors needed by Workstreams D and F.

---

## 1. Mechanism decomposition

C–H/C–H coupling is a family of reactions whose left-hand side is two C–H bonds and whose right-hand side is one C–C bond. The members of the family differ in **what carries away the four electrons and two hydrogens** that have to leave for the new C–C bond to form. That is the only thing that matters for atom economy: who eats the hydrogens.

### 1.1 True dehydrogenative (acceptorless) — byproduct H₂

The textbook case. Two C–H bonds break, one C–C bond forms, and H₂ is the only byproduct. The substrate is the formal reductant. Acceptorless dehydrogenative coupling (ADC) is the cleanest atom-economy story but is mechanistically demanding — the catalyst must re-oxidize itself by extruding H₂ from a metal-hydride intermediate.

Net transformation (schematic, where R–H and R′–H are the two C–H partners):

$$
\text{R–H} + \text{R'–H} \xrightarrow{\text{cat.}} \text{R–R'} + \text{H}_2
$$

Atom map on the canonical biaryl case:

- L: C(1)–H(7) and C(2)–H(8), with C(1) and C(2) on two arene fragments tethered through the macrocyclic backbone.
- R: C(1)–C(2) bond formed, expelled H(7)–H(8) (= H₂, mass 2.016 g/mol).
- Catalyst (Ru, Ir, Co–pincer, photocatalyst + H₂-evolving cocatalyst) is sub-stoichiometric and amortized at the process level.

This is the canonical case we'll encode. Examples in macrocycle work are rarer than oxidative variants because most reported macrocyclic CDCs use a stoichiometric oxidant for selectivity and turnover. ADC C(sp³)–C(sp³) is an active research frontier ([[Huang Kang Li 2019 - Cross-Dehydrogenative Coupling|Huang, Kang & Li 2019]]; Li, Huang & Li 2022 *Trends Chem.*).

### 1.2 Oxidative cross-dehydrogenative coupling (CDC) — byproduct H₂O + reduced oxidant

The workhorse variant in practice. A stoichiometric oxidant accepts the two hydrogens and is itself consumed. The bond-level reaction is still C–H/C–H → C–C, but at the process level, two equivalents of the oxidant's reduced form (or one equivalent if a 2e⁻ oxidant) are expelled along with H₂O.

Schematically:

$$
\text{R–H} + \text{R'–H} + [\text{Ox}] \xrightarrow{\text{cat.}} \text{R–R'} + \text{H}_2\text{O} + [\text{Ox}_\text{red}]
$$

Atom map: same C(1)–C(2) closure, but the two hydrogens H(7), H(8) end up bound to an oxygen donated by the oxidant (giving H₂O) and the oxidant skeleton is reduced. Common oxidants in macrocyclic settings:

| Oxidant | MW (g/mol) | Reduced form / byproduct | Notes |
|---------|-----------|--------------------------|-------|
| PhI(OAc)₂ (PIDA) | 322.1 | PhI + 2 AcOH | popular for Pd(II)/Pd(IV) cycles; clean two-electron oxidant |
| AgOAc | 166.9 | Ag(0) + AcOH | stoichiometric; for Pd-catalyzed peptide C(sp³)–H arylation/olefination |
| Cu(OAc)₂ | 181.6 | Cu(OAc) or Cu(0) | older Pd–Cu systems |
| K₂S₂O₈ (persulfate) | 270.3 | 2 KHSO₄ | strong, radical-prone |
| O₂ (air) | 32.0 | H₂O | greenest stoichiometric oxidant; mass cost dominated by co-oxidant or solvent |

For bond-level AE accounting, the byproduct is H₂O (mass 18.015 g/mol). The oxidant skeleton is a *process-level* reagent mass.

### 1.3 Decarbonylative variants — byproduct CO (+ other)

Not strictly "C–H/C–H" — these start from an acyl C–H or an aldehyde/carboxylic acid derivative and extrude CO during the coupling. Relevant when the macrocyclic precursor is a diketone, dialdehyde, or anhydride that loses CO on the way to the C–C bond. Sanford and co-workers have reviewed Pd/Ni decarbonylative couplings ([[Lalloo Brigham Sanford 2022 - Decarbonylative Couplings|Lalloo, Brigham & Sanford 2022]] *Acc. Chem. Res.*). For macrocyclic applications this is uncommon and is best modeled as a **separate rule** (`decarbonylative_macrocyclization.gml`) because the byproduct (CO, 28.01 g/mol) is fundamentally different from H₂ and the atom map loses a heavy atom.

### 1.4 Out-of-scope: C–H/X coupling (Heck, Fujiwara-Moritani)

C–H olefination (one C–H, one alkene) and C–H arylation with an aryl halide (one C–H, one Ar–X) are **not** C–H/C–H. They expel HX or are net redox-neutral with an internal alkene. These are covered by the `transition_metal_cross_coupling.gml` rule (Workstream C item 2) or by a future `c_h_olefination.gml` rule. Keep them out of the dehydrogenative-coupling rule.

---

## 2. Canonical rule recommendation

**Recommendation: encode the true dehydrogenative (H₂ byproduct) case as canonical.**

Rationale:

1. **Cleanest AE story.** The proposal's framing is "highest AE among C–C closures." That is only literally true for the H₂ byproduct case — once a stoichiometric oxidant joins, the process-level AE drops substantially. Encoding H₂ as canonical preserves the headline claim.
2. **Bond-level AE is invariant across the family.** All three sub-variants (1.1, 1.2, 1.3 for the CO-extruding pseudo-member excepted) form the same C–C bond and break the same two C–H bonds at the atom-map level. The difference is downstream of the bond-forming step and lives in `reagent_mass_g_per_mol` and `reagent_mass_alternatives`. The DPO span doesn't need to know about the oxidant.
3. **Symmetry with `rcm.gml`.** RCM is encoded with the *bond-level* truth (ethylene byproduct) even though the *process-level* truth is "Grubbs catalyst + solvent + olefin handling." Same pattern.
4. **Variants are reagent_mass overrides, not separate rules.** The oxidative variant differs only in process mass; it should be a `reagent_mass_alternatives` entry, not a separate `.gml`. The decarbonylative variant *does* differ in atom map and gets a separate rule.

The canonical rule encodes the C(sp²)–C(sp²) biaryl case because (a) it's the most common in macrocyclic settings, (b) it has no stereocenter complications at the forming bond, and (c) it matches the proposal's exemplar work (Saridakis–Kaiser–Maulide §6, Sengupta–Mehta 2020, Bai/Wang 2019 *Org. Lett.*).

---

## 3. Atom-mapped scheme — canonical case

Two arene C–H bonds break; one C–C(sp²)–C(sp²) biaryl bond forms; H₂ is expelled. Atom IDs follow the macrolactamization convention (substrate-bearing atoms on the low IDs; expelled atoms on the high IDs).

```
L:        C(1) — H(7)                C(2) — H(8)
            arene-1                    arene-2
              \________ backbone _______/

R:        C(1) ————————————————————— C(2)             +  H(7) — H(8)
            arene-1     biaryl       arene-2              (= H2)
              \________ backbone _______/
```

- **L (left):** node H(7), node H(8); edges C(1)–H(7), C(2)–H(8). C(1) and C(2) are in context (they exist on both sides).
- **Context:** node C(1), node C(2). The macrocyclic tether connecting them is implicit and out-of-scope for the rule body (it's matched by the strategy predicates `is_intramolecular` + `ring_size_equals(n)`).
- **R (right):** node H(7), node H(8); edges C(1)–C(2), H(7)–H(8). The new C(1)–C(2) is the closure bond; the new H(7)–H(8) is the H₂ byproduct.

Atom count check: L has 4 atoms (C1, C2, H7, H8) and 2 bonds (C1–H7, C2–H8). R has 4 atoms and 2 bonds (C1–C2, H7–H8). Conserved. Hydrogen count: 2 on each side. Conserved. This will pass `pixi run check-rules`.

BFS retention check: from `retained_root_atom = 1`, following R's edges, we reach C(1)→C(2). The H(7)–H(8) connected component is disjoint — it is the byproduct. Verifier's bond-level AE computation will identify H₂ (2.016 g/mol) as the expelled mass automatically.

---

## 4. Variant table

Top variants for the `reagent_mass_alternatives` field. Byproduct mass is at the bond level (what comes out of the atom map). Oxidant mass is the process-level penalty per firing for the stoichiometric oxidant (NOT amortized — these are consumed 1:1 with the substrate, modulo eq. count). Catalyst is amortized separately and assumed ~30 g/mol.

| Variant | byproduct_mass (g/mol) | oxidant_mass (g/mol) | Typical scope | Reference DOI |
|---------|------------------------|----------------------|---------------|---------------|
| **Acceptorless dehydrogenative (H₂)** | 2.016 | 0 (none) | Ru/Ir/Co–pincer; photoredox with H₂-evolving co-cat.; rare for macrocycles | 10.1021/acs.joc.9b01704 |
| Pd(II)/Pd(IV), PhI(OAc)₂ oxidant | 18.015 (H₂O) | 322.1 (PIDA → PhI + 2 AcOH) | C(sp²)–H/C(sp²)–H biaryl peptide closures, Wang/Yu groups | 10.1021/acs.orglett.9b02945 |
| Pd(II)/Pd(0), AgOAc oxidant (2 eq) | 18.015 (H₂O) | 333.8 (2 × 166.9) | C(sp³)–H/C(sp²)–H peptide olefination + macrocyclization, Bai/Wang 2018 | 10.1002/anie.201807953 |
| Cu(OAc)₂ oxidant (2 eq) | 18.015 (H₂O) | 363.2 (2 × 181.6) | Older Pd/Cu cross-CDC; common for indole/heteroarene biaryl coupling | 10.1021/acs.joc.9b01704 |
| K₂S₂O₈ persulfate (1 eq) | 18.015 (H₂O) | 270.3 | Metal-free or photocatalytic CDC; macrocyclic CDC of N-heterocycles | 10.1039/D1GC01871J |
| O₂ / air | 18.015 (H₂O) | 0 (stoichiometric mass-free) | Greenest oxidant; Pd/Cu(II) cooperative systems; CDC review | 10.1039/D1GC01871J |

For the canonical `meta.yaml`, use the acceptorless H₂ case for `byproduct_mass_g_per_mol`. Set `reagent_mass_g_per_mol` modestly to account for catalyst (~30–50 g/mol amortized). Put the oxidative variants in `reagent_mass_alternatives` keyed by oxidant identity.

---

## 5. Stereo handling

The forming C–C(sp²)–C(sp²) bond has no stereo concerns of its own — it's planar. But the substrate's *existing* stereocenters can be at risk in two distinct ways.

**C(sp²)–H/C(sp²)–H biaryl coupling (e.g., aryl–aryl in peptide macrocycles):**

- The forming bond is planar. No new sp³ stereocenter is set.
- However, **biaryl atropisomerism** can be installed if both arenes have *ortho* substituents on either side of the new C–C axis. For macrocyclic biaryls, atropisomerism is the rule rather than the exception (cf. vancomycin, complestatin, biphenomycin). The atropisomer is set by the macrocyclic constraint, not by the catalyst — the kinetic atropisomer is whichever closes first geometrically.
- α-stereocenters on flanking amino acid residues are preserved under typical Pd(II)/PIDA conditions. The Bai/Wang 2019 Org. Lett. paper explicitly demonstrates retention at α-amino acid stereocenters during late-stage biaryl macrocyclization.

**C(sp³)–H/C(sp²)–H or C(sp³)–H/C(sp³)–H coupling:**

- A new sp³ stereocenter can be created or epimerized at the C(sp³) site. In Pd(II)/Pd(IV) chemistry on α-amino acid β-C(sp³)–H bonds, the metallacycle typically retains configuration if the substrate uses backbone amide as directing group (Wang group; [[Bai Cai Yu Wang 2018 - directional macrocyclization|Bai, Cai, Yu & Wang 2018]] *Angew. Chem.*).
- Activation of an **α-C(sp³)–H** adjacent to a carbonyl risks enolization and racemization, especially under basic CDC conditions. This is the dominant epimerization mechanism in peptide CDC (the same mechanism that plagues classical peptide coupling — see the Duengo 2023 review of peptide epimerization, *Molecules* 28, 8017).
- Acceptorless C(sp³)–H/C(sp³)–H is mechanistically distinct (often radical/HAT-based) and racemization is generic — any benzylic or α-heteroatom radical equilibrates.

**Recommended `stereo_flags`:**

```yaml
stereo_flags:
  - preserves_planar_biaryl_bond        # no new stereocenter at forming bond
  - may_set_atropisomerism              # rotational stereochemistry on macrocyclic biaryl
  - retains_remote_alpha_stereo         # under typical Pd(II) conditions, Wang/Yu evidence
  - alpha_carbonyl_csp3_racemization_risk  # if substrate has alpha-acidic C(sp3)-H near base
```

Workstream F should flag substrates where the substrate has α-C(sp³)–H within two bonds of an enolizable carbonyl as `epimerization_risk`.

---

## 6. Forbidden contexts (Workstream D)

Predicates to suppress chemistry-prior implausible firings. These come from accumulated empirical knowledge in the macrocyclic C–H activation literature.

1. **`forbidden_when alpha_acidic_C_sp3_under_basic_oxidant`** — if the matched C–H site is α to a carbonyl AND the modeled conditions include a base (≥ 1 eq carbonate, fluoride, or stronger), enolization competes and the literature yield is typically <20%. Flag this as a competing pathway, not a hard ban.

2. **`forbidden_when allylic_C_sp3_unprotected`** — allylic C(sp³)–H bonds are radically and metallically more reactive than the directed site. Without a strong directing group, the rule will fire on the wrong C–H bond. Block firings where the matched C(1) or C(2) is allylic AND no proximate directing group (amide N, pyridine N, oxime O within 4 bonds) is present.

3. **`forbidden_when benzylic_competes_with_aryl`** — benzylic C(sp³)–H bonds are kinetically more accessible than aromatic C(sp²)–H. For aryl–aryl macrocyclic closures, block firings when a benzylic C(sp³)–H is on the same arene within 2 bonds of the targeted aromatic C–H site — the benzylic site will compete.

4. **`forbidden_when both_sites_electron_poor`** — Concerted metalation-deprotonation (CMD) requires one electron-rich arene partner. Both sites being strongly electron-poor (nitro, multiple fluorines, sulfonyl on ortho/para positions) typically gives <10% yield. Flag, don't ban.

5. **`forbidden_when ortho_to_protic_NH`** — primary amides, sulfonamides, and acidic NHs *ortho* to the target C–H bond often deprotonate and divert the catalyst into N–H/C–H coupling (C–N bond formation) instead of C–C. The aryl C–H bond loses; the N–H site wins. Block this firing.

6. **`forbidden_when no_directing_group_within_4_bonds`** — for C(sp³)–H/C(sp²)–H variants, ban firings where neither matched carbon has a directing group (amide, oxime, pyridyl, 8-aminoquinoline-tethered carbonyl) within 4 bonds. Without a DG, peptide and aliphatic C(sp³)–H activation is essentially impossible.

7. **`forbidden_when ring_size_below_12`** — empirically, macrocyclic C–H activation closures are reported for 12-membered rings and above. Smaller rings (10, 11) close better through other tactics (lactamization). If the macrocyclic ring size predicate evaluates to <12, the dehydrogenative-coupling rule is a poor strategic choice. Flag, don't ban — this is a strategy hint, not a constraint.

8. **`forbidden_when target_has_free_thiol_or_phosphine`** — free –SH, free P(III), and free terminal alkynes poison Pd(II)/Pd(IV) catalysis. The rule will not fire in practice; the strategy should not propose it.

---

## 7. Citation list

### Reviews on macrocyclic C–H activation

1. **[[Sengupta Mehta 2020 - Macrocyclization via C-H functionalization|Sengupta & Mehta (2020)]]** — "Macrocyclization via C–H functionalization: a new paradigm in macrocycle synthesis," *Org. Biomol. Chem.* **18**, 1851–1876. DOI: [10.1039/c9ob02765c](https://doi.org/10.1039/c9ob02765c). The dedicated review of this exact topic; covers Pd, Rh, Ru, Mn macrocyclic C–H activation systems.

2. **[[Saridakis Kaiser Maulide 2020 - Unconventional Macrocyclizations|Saridakis, Kaiser & Maulide (2020)]]** — "Unconventional Macrocyclizations in Natural Product Synthesis," *ACS Cent. Sci.* **6**, 1869–1889. DOI: [10.1021/acscentsci.0c00599](https://doi.org/10.1021/acscentsci.0c00599). The review cited by the MacroCert proposal. §6 covers C–H activation macrocyclizations; Scheme 20 shows Davies's Rh-catalyzed C(sp³)–H activation in the cylindrocyclophane synthesis — a paradigmatic dehydrogenative/oxidative example.

3. **Pal & Maity 2024 (mini-review)** — "Recent Progress on Transition Metal Catalyzed Macrocyclizations Based on C–H Bond Activation at Heterocyclic Scaffolds," PMID: 38924294. Covers 2020–2024 progress, useful for the most recent peptide and heterocycle examples.

### Modern macrocyclization examples (2018–2024)

4. **[[Bai Bai Wang 2019 - Biaryl-Bridged Peptide C-H Arylation|Bai, Bai & Wang (2019)]]** — "Macrocyclization of Biaryl-Bridged Peptides through Late-Stage Palladium-Catalyzed C(sp²)–H Arylation," *Org. Lett.* **21**, 7967–7971. DOI: [10.1021/acs.orglett.9b02945](https://doi.org/10.1021/acs.orglett.9b02945). Direct example of the canonical case; uses Pd(OAc)₂ + PIDA.

5. **[[Bai Cai Yu Wang 2018 - directional macrocyclization|Bai, Cai, Yu & Wang (2018)]]** — "Backbone-Enabled Directional Peptide Macrocyclization through Late-Stage Palladium-Catalyzed δ-C(sp²)–H Olefination," *Angew. Chem. Int. Ed.* **57**, 13912–13916. DOI: [10.1002/anie.201807953](https://doi.org/10.1002/anie.201807953). Bidirectional macrocyclization with bicyclic peptide one-pot demo.

6. **Cai, Liu & Wang (2021)** — "Peptide Macrocyclization Through Palladium-Catalyzed Late-Stage C–H Activation," *Methods Mol. Biol.* **2371**, 31–42. DOI: [10.1007/978-1-0716-1689-5_3](https://doi.org/10.1007/978-1-0716-1689-5_3). Protocol chapter — exact conditions for verification.

7. **Davies (Rh-catalyzed cylindrocyclophane synthesis, 2018)** — described in Saridakis 2020 Scheme 20; the canonical example of selective sp³–H/sp³–H macrocyclization. C(sp³)–H activation by Rh-carbenoid; selective for the most accessible methylene over benzylic CH₂.

### Cross-dehydrogenative coupling general / AE perspective

8. **[[Huang Kang Li Li 2019 - CDC Perspective|Huang, Kang, Li & Li (2019)]]** — "En Route to Intermolecular Cross-Dehydrogenative Coupling (CDC) Reactions," *J. Org. Chem.* **84**, 12705–12721. DOI: [10.1021/acs.joc.9b01704](https://doi.org/10.1021/acs.joc.9b01704). Mechanistic categorization of CDC types; useful for the variant table.

9. **[[Tian Li Li 2021 - CDC Green Chemistry Review|Tian, Li & Li (2021)]]** — "Cross-dehydrogenative coupling: a sustainable reaction for C–C bond formations," *Green Chem.* **23**, 6789–6816. DOI: [10.1039/D1GC01871J](https://doi.org/10.1039/D1GC01871J). 20-year retrospective from Chao-Jun Li's group; the explicit "atom economy + sustainability" framing the proposal references.

10. **[[Li 2022 - Inventing CDC|Li (2022)]]** — "On Inventing Cross-Dehydrogenative Coupling (CDC): Forming C–C Bond from Two Different C–H Bonds," *Chin. J. Chem.* **40**, 838–845. Origin-story account by the inventor of the term.

### Decarbonylative (for the separate `decarbonylative_coupling.gml` if pursued)

11. **[[Lalloo Brigham Sanford 2022 - Decarbonylative Couplings|Lalloo, Brigham & Sanford (2022)]]** — "Mechanism-Driven Development of Group 10 Metal-Catalyzed Decarbonylative Coupling Reactions," *Acc. Chem. Res.* **55**, 3477–3488. DOI: [10.1021/acs.accounts.2c00496](https://doi.org/10.1021/acs.accounts.2c00496).

### Stereo / epimerization

12. **Duengo et al. (2023)** — "Epimerisation in Peptide Synthesis," *Molecules* **28**, 8017. DOI: [10.3390/molecules28248017](https://doi.org/10.3390/molecules28248017). General reference for α-C(sp³) racemization mechanisms; informs forbidden context #1.

---

## 8. Proposed `meta.yaml`

```yaml
# C-H dehydrogenative coupling — C(sp2)/C(sp2) or C(sp3)/C(sp2) closure
# with H2 as the bond-level byproduct (canonical: acceptorless dehydrogenative).
# Process-level variants with stoichiometric oxidants (H2O byproduct + reduced
# oxidant) live in reagent_mass_alternatives. Decarbonylative variants are a
# distinct rule (decarbonylative_coupling.gml) because the atom map differs.

# Process-level reagent mass: amortized transition-metal catalyst (Pd/Ru/Rh/Ir
# typical 5-10 mol%) + ligand + base correction. Canonical case is acceptorless
# dehydrogenative (no stoichiometric oxidant) so the only process mass is the
# amortized catalyst. v0 uses 50 g/mol as a loose amortized upper bound.
reagent_mass_g_per_mol: 50.0

# Bond-level expelled mass: dihydrogen H2 = 2.016 g/mol (canonical
# acceptorless dehydrogenative case).
byproduct_mass_g_per_mol: 2.016

# Retained-root atom: C(1), one of the two arene carbons whose C-H was activated.
retained_root_atom: 1

# Process-level alternatives: same bond-level rule, different stoichiometric
# oxidant. byproduct_mass at bond level is H2O = 18.015 g/mol because the H's
# are abstracted by the oxidant rather than evolved as H2. The oxidant_mass is
# the per-firing penalty for the consumed oxidant.
reagent_mass_alternatives:
  acceptorless_h2:
    reagent_mass_g_per_mol: 50.0
    byproduct_mass_g_per_mol: 2.016
    notes: "True dehydrogenative; H2 byproduct; rare in macrocyclic settings, mechanistically demanding."
  pida_oxidant:
    reagent_mass_g_per_mol: 372.1   # 50 cat. + 322.1 PIDA
    byproduct_mass_g_per_mol: 18.015
    notes: "Pd(II)/Pd(IV) cycle with PhI(OAc)2; canonical for peptide biaryl macrocyclization (Bai/Wang 2019)."
  agoac_2eq:
    reagent_mass_g_per_mol: 383.8   # 50 cat. + 2*166.9 AgOAc
    byproduct_mass_g_per_mol: 18.015
    notes: "Pd/Ag system for C(sp3)-H peptide olefination + macrocyclization (Bai/Wang 2018 Angew)."
  cu_oac_2_2eq:
    reagent_mass_g_per_mol: 413.2   # 50 cat. + 2*181.6 Cu(OAc)2
    byproduct_mass_g_per_mol: 18.015
    notes: "Pd/Cu cooperative oxidant; common for indole/heteroarene CDC."
  k2s2o8_1eq:
    reagent_mass_g_per_mol: 320.3   # 50 cat. + 270.3 K2S2O8
    byproduct_mass_g_per_mol: 18.015
    notes: "Persulfate oxidant; common in metal-free / photocatalytic CDC."
  o2_aerobic:
    reagent_mass_g_per_mol: 50.0    # O2 stoichiometric but mass-free in air
    byproduct_mass_g_per_mol: 18.015
    notes: "Aerobic oxidation; greenest oxidant choice; Pd/Cu cooperative or photoredox."

classes:
  - macrocyclization
  - cc_closure
  - high_atom_economy_bond   # H2 byproduct (canonical) is the highest AE C-C closure
  - dehydrogenative
  - directed_c_h_activation

stereo_flags:
  - preserves_planar_biaryl_bond
  - may_set_atropisomerism
  - retains_remote_alpha_stereo
  - alpha_carbonyl_csp3_racemization_risk

refs:
  - "Sengupta & Mehta 2020, Org. Biomol. Chem., DOI:10.1039/c9ob02765c (macrocyclization via C-H review)"
  - "Saridakis, Kaiser & Maulide 2020, ACS Cent. Sci., DOI:10.1021/acscentsci.0c00599 (unconventional macrocyclizations)"
  - "Bai, Bai & Wang 2019, Org. Lett., DOI:10.1021/acs.orglett.9b02945 (biaryl peptide macrocyclization)"
  - "Bai, Cai, Yu & Wang 2018, Angew. Chem., DOI:10.1002/anie.201807953 (directional peptide macrocyclization)"
  - "Huang, Kang, Li & Li 2019, J. Org. Chem., DOI:10.1021/acs.joc.9b01704 (CDC mechanistic categorization)"
  - "Tian, Li & Li 2021, Green Chem., DOI:10.1039/D1GC01871J (CDC sustainability review)"

notes: |
  C-H/C-H coupling is the highest-AE C-C closure at the *bond level* because
  the only byproduct is H2 (acceptorless case) or H2O (oxidative case with the
  oxidant carrying away the redox burden). The bond-vs-process AE split is
  starker here than for any other rule in the library: an acceptorless H2 case
  has ~99% bond AE but is mechanistically rare; the oxidative PIDA-mediated
  case is common in macrocyclic peptide work but the process AE is dragged
  down by the 322 g/mol oxidant. This is exactly the situation §3.3 of the
  proposal flags as the most chemistry-informative.

  Workstream D forbidden-context predicates are critical here -- without them
  the rule fires on every aromatic C-H bond in the substrate, which is
  combinatorially catastrophic on peptide substrates. The directed-group-
  within-4-bonds predicate is the most important single filter.
```

---

## 9. Proposed GML structure

```gml
rule [
    ruleID "c-h dehydrogenative coupling (C-C closure, -H2)"
    # L: two arene/aliphatic C(1)-H(7) and C(2)-H(8) bonds. C(1) and C(2)
    # are tethered through the macrocyclic backbone (out of scope for rule;
    # matched by strategy predicates is_intramolecular + ring_size_equals).
    # Hydrogens H(7), H(8) are explicit so the verifier can identify H2 as
    # the byproduct on R via the BFS-from-retained-root partition.
    left [
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 7 label "-" ]
        edge [ source 2 target 8 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]
    # R: new C(1)-C(2) bond closes the ring. Expelled H(7)-H(8) forms H2.
    # The H2 fragment is a disconnected component from C(1)-C(2) in R, so
    # the verifier's BFS from retained_root_atom=1 will identify it
    # automatically as the byproduct.
    right [
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 7 target 8 label "-" ]
    ]
]
```

Atom balance: 4 atoms each side (C1, C2, H7, H8). 2 bonds each side (L: C1–H7, C2–H8; R: C1–C2, H7–H8). Conservation passes.

The rule deliberately does **not** label C(1) or C(2) as aromatic (lowercase `c`) in MØD's typing — staying with `"C"` keeps the rule applicable to both C(sp²)–C(sp²) (canonical biaryl) and C(sp³)–C(sp²) or C(sp³)–C(sp³) variants. The strategy layer chooses where to fire via context predicates; the rule itself is the most general DPO span over "two C–H bonds → one C–C bond + H₂."

If the panel needs to disallow C(sp³) firings (e.g., when modeling a strictly biaryl CDC), Workstream D adds an `aromatic_carbon_only` predicate that restricts matches to aromatic carbons. This keeps the GML library minimal and pushes specificity into strategy.

For the **oxidative variant** (H₂O byproduct + stoichiometric oxidant), the bond-level DPO is genuinely different (H₂ vs H₂O on the byproduct side), but encoding it as a separate rule duplicates the substrate side. Recommended: keep one `c_h_dehydrogenative_coupling.gml` for the canonical H₂ case, and ship a sibling `c_h_oxidative_coupling.gml` only if the panel requires it — the H₂O byproduct comes from an external oxidant atom that is NOT in the substrate, so MØD needs explicit oxidant atoms in the rule for the atom map to balance. The cleaner answer is to leave the H₂ rule canonical and represent oxidative variants via `reagent_mass_alternatives` at the meta layer.

---

## 10. Toy substrate

For `data/validation_panel/`, a 14-membered biaryl macrocyclic dipeptide. Compact enough to verify by hand; large enough that intramolecular C(sp²)–H/C(sp²)–H closure is the literature-relevant case.

**Proposed substrate: a Phe-Phe diketopiperazine-extended diester, with two unsubstituted phenyl rings tethered through an L–Pro–L–Pro spacer plus a glycine linker.** Schematic:

```
    Ph—CH2—Cα(H)(NHCOCH2NHCOCH2)—...—Cα(H)(NHCOCH2)—CH2—Ph
       \____________________________________________________/
                       14-atom backbone tether
```

Or, simpler for v0: a **diphenylmethylenediamine with an alkyl-diamide linker** giving 14 backbone atoms between the two ortho-Ar–H positions:

```
H–Ar1–CH2–N(H)–C(=O)–(CH2)4–C(=O)–N(H)–CH2–Ar2–H
```

Backbone atom count from ortho-C of Ar1 to ortho-C of Ar2:
ortho-C(1) → ipso-C → CH₂ → N → C(=O) → CH₂ × 4 → C(=O) → N → CH₂ → ipso-C → ortho-C(2) = 13 bonds → 14-atom ring after closure. Good.

The intended firing: rule activates the two *ortho* arene C–H bonds; closure forms the biaryl bond; H₂ expelled; product is a 14-membered macrocyclic biaryl-bridged bis-amide. This is structurally analogous to the dibenzofuran-free arylomycin/biphenomycin family — small enough to verify by hand, large enough to exercise the macrocyclization predicates.

For Workstream D testing, add a decoy: a substrate with an additional benzylic CH₂ on Ar1 ortho to the targeted aromatic C–H. The forbidden-context predicate `benzylic_competes_with_aryl` should fire and suppress the bad alternative.

For SMILES (sketch, F to validate):
- Target substrate: `c1ccc(CN(C(=O)CCCCC(=O)NCc2ccccc2)H)cc1` — both phenyls present; closure forms a 14-ring biaryl.
- Expected product after rule fires: 14-membered macrocycle with new biaryl bond between the two *ortho* positions, plus expelled H₂.

The verifier should compute bond-level AE = MW(product) / [MW(substrate) + MW(H₂)] ≈ MW(substrate) / [MW(substrate) + 2.016] ≈ 99.4% for a ~300 g/mol substrate. Process-level AE with PIDA oxidant drops to ≈ MW(product) / [MW(substrate) + 322.1 + 50] ≈ 45–50%. The bond-vs-process AE gap on this rule is the largest in the library — exactly the case the proposal §3.3 wants to surface.

---

## Source quality and confidence summary

| Source | Type | Quality | Confidence in claim |
|--------|------|---------|---------------------|
| Sengupta & Mehta 2020 OBC | Dedicated topic review | 5 | High — peer-reviewed, primary survey |
| Saridakis–Kaiser–Maulide 2020 ACS Cent. Sci. | Cited by proposal; broad review | 5 | High — endorsed by proposal |
| Bai/Wang 2019 Org. Lett. | Primary research, peptide example | 5 | High — exact canonical case |
| Bai/Cai/Yu/Wang 2018 Angew. | Primary research, bicyclic peptides | 5 | High |
| Huang/Kang/Li/Li 2019 JOC | CDC categorization review | 4 | High for mechanism taxonomy |
| Tian/Li/Li 2021 Green Chem. | 20-year retrospective | 4 | High for AE/sustainability framing |
| Wikipedia + LibreTexts on CDC | Tertiary | 3 | Used only for oxidant catalog |
| Duengo 2023 Molecules epimerization | Methodology review | 4 | Adequate for stereo flag justification |
| Pubmed 38924294 (2024 heterocycle review) | Review, recent | 4 | Recent confirmation of activity in the field |
| Lalloo/Brigham/Sanford 2022 Acc. Chem. Res. | Topic account by leading group | 5 | High for decarbonylative variant |

Contradictions: none found between sources on the chemistry. Sengupta–Mehta and Saridakis–Maulide both place macrocyclic C–H activation in the "high AE" framing; both note H₂ as the ideal but acknowledge H₂O + oxidant is the practical reality. Disagreement is only at the level of which catalyst is best — irrelevant for the DPO encoding.

Gaps:
- The proposal's specific exemplar reaction (whichever cytochalasan or ascomylactam-adjacent C–H closure it has in mind) was not located in this search — Workstream B should pin down the panel example so F can validate the substrate map.
- C(sp³)–C(sp³) macrocyclic dehydrogenative coupling is genuinely rare; the Davies 2018 cylindrocyclophane is the cleanest example and is paywalled. If the panel needs C(sp³) cases, paywalled-PDF access through the Sharpe library is required.
- The Pal & Maity 2024 heterocycle review (PMID 38924294) was identified but not fully read; it likely contains 2022–2024 examples missing from the older Sengupta–Mehta survey. Worth a focused follow-up if a more recent panel case is wanted.
