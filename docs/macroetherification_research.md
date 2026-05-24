# Macroetherification Rule — Chemistry Research Brief

**Workstream:** C (Rule library expansion)
**Target artifacts:** `data/rules/aryl_etherification.gml` + `.meta.yaml`, plus a panel substrate
**Date:** 2026-05-24
**Author:** researcher agent (for Ivan / Workstream C)
**Driver:** Workstream A finding — ascomylactam A's 13-membered ring closes via an **Ar–O–C(sp³) ether**, not a lactam. The existing 4-rule library (macrolactamization, macrolactonization, RCM, transannular Diels–Alder) does not cover this disconnection.

This brief grounds the design of the macroetherification rule. It mirrors the structural choices in `macrolactamization.gml/.meta.yaml` and `macrolactonization.gml/.meta.yaml` (the closest cousins — same H₂O-expelling condensation of an "OH/NH + OH" pair at the bond level) so the verifier and rule loader treat the family consistently. The key chemistry distinction is that here **one of the carbons is sp² aromatic** and the activation chemistry differs accordingly: the leaving group lives on the arene (X, F, Cr(CO)₃-activated) rather than on the carbon of a carboxylic acid.

---

## Section 1 — Three-mechanism comparison and recommendation

### 1.1 The bond-level transformation

Three plausible mechanisms produce the same Ar–O–C(sp³) bond. They differ in **which partner carries the leaving group** and **what the leaving group is**.

| Mechanism | L-side partners | Net byproduct (bond level) | Activator |
| --- | --- | --- | --- |
| **Direct etherification** (Williamson-style; ROH + ArOH) | Ar–OH + HO–CHR–R′ | H₂O | (Mitsunobu, dehydration, etc.) |
| **SNAr macroetherification** | Ar–LG + HO–CHR–R′ | H–LG (HF / HX / Cr(CO)₃·L₃) | electron-poor arene; η⁶-arene-Cr in Uchiro's case |
| **Cu-catalyzed Ullmann C–O coupling** | Ar–X + HO–CHR–R′ | HX (absorbed by base) | CuI / 1,10-phen / Cs₂CO₃ |
| **Pd-catalyzed Buchwald aryl ether** | Ar–X + HO–CHR–R′ | HX (absorbed by base) | Pd(0) / RockPhos or t-BuXPhos / Cs₂CO₃ |

The **direct dehydrative Williamson etherification** of an aryl alcohol with an aryl OH is *not* a viable macrocyclization tactic — neither partner is activated, the equilibrium is unfavorable, and there is no precedent in the natural-product synthesis literature for 13-membered Ar–O–C(sp³) ring closure by this mechanism. Mitsunobu is the only practical "direct" variant, and it works by activating the alcohol (PPh₃/DIAD → alkoxyphosphonium); it inverts the alcohol carbon and is mechanistically distinct (see §4).

That leaves three mechanism candidates for the canonical rule:

1. **Cu Ullmann** (Ar–X + HO–R, base, Cu/L, high temperature)
2. **SNAr** (Ar–LG with electron-poor arene + HO–R, mild base)
3. **Pd Buchwald aryl ether** (Ar–X + HO–R, Pd/bulky-phosphine, base)

Conceptually all three deposit a new Ar–O–C(sp³) bond and net out an H–LG byproduct. The DPO atom map is identical across them — what differs is the **activator stack** (catalyst, ligand, base) and the **byproduct mass** (HBr ≠ HF ≠ HCl).

### 1.2 Direct sibling system: Uchiro GKK1032A2 (2017)

The decisive prior art is the [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization|Sugata, Inagaki, Ode, Hayakawa, Karoji, Baba, Kato, Hasegawa, Tsubogo, Uchiro (2017)]] total synthesis of GKK1032A₂ — DOI `10.1002/asia.201601728`. Verbatim from the abstract:

> "The first enantioselective total synthesis of GKK1032A₂ has been achieved. The key step is a direct construction of the highly strained 13-membered macrocycle of GKK1032A₂ by an intramolecular nucleophilic aromatic substitution (SNAr) reaction. This is the first successful example of construction of a macrocycle with an aryl ether linkage utilizing an intramolecular SNAr reaction of an (η⁶-arene)chromium complex." — Chem. Asian J. 2017, 12, 628–632.

GKK1032A₂ is in the same decahydrofluorene / cyclopenta[b]fluorene family as the ascomylactams (Wu et al. biosynthesis paper, PMC8094548, treats GKK1032A₂ and the pyrrocidines as siblings). Its 13-membered macrocycle terminates in an **Ar–O–C(sp³)** bond between a *para*-substituted phenol and a sp³ oxymethine — exactly the disconnection ascomylactam A requires. Uchiro's earlier 2011 paper on hirsutellone B used an **Ullmann** macrocyclization for the same family (DOI `10.1021/ol202748e`), establishing that both mechanisms are viable for the cyclopenta[b]fluorene scaffold. The 2017 paper explicitly states that the Ullmann approach failed for GKK1032A₂'s more strained variant and that switching to η⁶-arene-Cr SNAr was what enabled the closure.

### 1.3 Recommendation: SNAr canonical; Ullmann + Buchwald as alternatives

**Recommendation: SNAr macroetherification** as the canonical activator path for `aryl_etherification.gml`, with **Ullmann (Cu/phen)** and **Buchwald (Pd/RockPhos)** as `reagent_mass_alternatives`. The decisive factors:

1. **Direct prior art on the exact target family.** [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization|Uchiro et al. 2017]] explicitly succeeded with η⁶-arene-Cr SNAr where the Ullmann route failed on the 13-membered cyclopenta[b]fluorene macrocycle. For the M5 ascomylactam A target the canonical retrosynthetic call is the same SNAr disconnection.
2. **Mechanistic precedent across the literature.** Zhu's 1997 Synlett review ([[Zhu 1997 - SNAr Macrocyclization Biaryl Ether|Zhu (1997)]], DOI `10.1055/s-1997-722`, 164 citations) catalogs > 30 SNAr-based macroetherifications across the vancomycin/K-13/OF4949/bouvardin family, establishing SNAr as the workhorse for medium-to-large Ar–O macrocycles.
3. **Atom economy.** SNAr expels HF (20 g/mol) — lighter than HBr (81 g/mol from Ar–Br Ullmann) or HCl (36.5 g/mol). The bond-level AE is best with SNAr.
4. **Caveat — activator mass is heavy.** η⁶-arene-Cr complexation requires Cr(CO)₆ (220 g/mol) on the way in and an oxidative decomplexation step (Ce(IV), I₂, or sunlight + air) on the way out. The Ullmann is lighter at the activator level (catalytic Cu + phen + Cs₂CO₃) and Pd Buchwald is roughly comparable. The process-level AE will favor Ullmann; the bond-level AE favors SNAr. This is the same kind of bond-vs-process split the macrolactonization brief calls out.

**For ascomylactam A specifically**: the canonical retrosynthetic call should be SNAr. The arene-Cr activation is mass-expensive but is the only mechanism with direct literature precedent on the exact ring size (13) and exact scaffold family (decahydrofluorene-tethered cyclopenta[b]fluorene). For Workstream A's M5 run, set the rule's activator to `sn_ar_chromium` via RunSpec.solver.extra. For M6+ where the toy substrate or a less-strained target is in play, Ullmann is a reasonable second choice.

### 1.4 What this rule does *not* cover

- **Mitsunobu** (inverts the alcohol C(sp³)). This is a separate rule with `inverts_alcohol_stereo`. Excluded from this rule.
- **Williamson ether synthesis** (Ar–O⁻ + alkyl-X → Ar–O–alkyl). This is the **reverse polarity** version where the *alkyl* partner carries the leaving group. Not covered by this rule — atoms 1/5 swap roles. Should be a separate rule (`williamson_etherification.gml`) if it ever becomes load-bearing for a target. None of the ascomylactam/GKK1032/hirsutellone family closes by this disconnection.
- **Biaryl ether macroetherification** (Ar–O⁻ + Ar′–LG → Ar–O–Ar′). This is the vancomycin / K-13 / bouvardin closure. Same SNAr mechanism, but the carbon receiving the oxygen is sp² aromatic, not sp³. Atoms 1, 2 in our atom-map below would both become aromatic C. **This is a separate rule** because the stereochemistry implications differ (biaryl ether closures generate atropisomerism instead of preserving sp³ stereo). See §7 for the categorization correction on Boger's vancomycin work.

---

## Section 2 — Atom-mapped DPO scheme for the canonical SNAr case

### 2.1 The bond-level chemistry

$$
\text{Ar}\!-\!\text{LG} + \text{HO}\!-\!\text{C}(\text{sp}^3)\text{R}\text{R}^\prime \;\longrightarrow\; \text{Ar}\!-\!\text{O}\!-\!\text{C}(\text{sp}^3)\text{R}\text{R}^\prime + \text{H}\!-\!\text{LG}
$$

For the canonical SNAr fluoride-leaving variant, LG = F and the bond-level byproduct is **HF (20.006 g/mol)**.

### 2.2 Atom numbering (mirrors `macrolactamization.gml` / `macrolactonization.gml`)

The atom slots map cleanly onto the lactam/lactone rules so the verifier recognizes the family:

| ID  | Element | Role                                                                            |
| --- | ------- | ------------------------------------------------------------------------------- |
| 1   | C       | Aromatic carbon (sp²) bearing the leaving group — **retained**, becomes Ar–O carbon |
| 2   | F (or X) | The aromatic leaving group — **expelled** in HF (HX)                            |
| 3   | (unused — slot for parity with O of macrolactonization, omitted)                                                  |
| 4   | (unused — slot for parity with the OH proton of macrolactonization, omitted)    |
| 5   | O       | Alcohol O — **retained**, becomes the Ar–O–C ether oxygen                       |
| 6   | H       | Alcohol OH proton — **expelled** in HF                                          |

I keep IDs 1, 2, 5, 6 (same as macrolactamization for 1, 5, 6; with the LG atom 2 replacing what is the carbonyl O in the acyl rules). This deliberately leaves IDs 3 and 4 unused so the family relationship across the three rules (lactam: amide N; lactone: ester O; aryl ether: aromatic C) is encoded by atom-slot identity. The verifier's BFS-from-`retained_root_atom: 1` traversal works identically across the three rules.

**Alternative 5-atom layout** (drops the parity with macrolactonization): keep IDs 1, 2, 3, 4, 5 with 1=aromatic C, 2=leaving group F, 3=alcohol O, 4=alcohol H, 5=… (unused). This is a denser numbering but breaks the macrolactonization analogy. **Recommendation: use the 4-atom layout with IDs 1, 2, 5, 6**.

### 2.3 Bond changes

**Broken (in L):**
- 1–2 (aromatic C–F bond)
- 5–6 (O–H of the alcohol)

**Preserved (in context):**
- The aromatic ring (everything around C-1 except the C–F bond)
- The C(sp³)–O bond between the alcohol carbon and atom 5 (off-rule; lives in the substrate)

**Formed (in R):**
- 1–5 (the new Ar–O–C ether bond, closing the ring)
- 2–6 (the new H–F bond of expelled HF)

### 2.4 Mass balance check

- L mass: Ar–F + R′–OH
- R mass: Ar–O–R′ + HF
- Net: −1 H, −1 F move out as HF (20.006 g/mol). Mass balance ✓.

If LG = Cl: byproduct is HCl (36.461 g/mol). If LG = Br: HBr (80.912 g/mol). If LG = I: HI (127.912 g/mol). If LG = NO₂ (less common but documented in heavily activated SNAr): HNO₂ (47.013 g/mol). The `reagent_mass_alternatives` table (§3) carries the leaving-group choices.

### 2.5 Proposed GML structure (canonical SNAr fluoride variant)

```
rule [
    ruleID "aryl_etherification (SNAr Ar-O-C(sp3) ring closure, -HF)"
    # L: aromatic C(1) bearing F(2) and alcohol O(5)-H(6)
    left [
        node [ id 2 label "F" ]   # aromatic leaving group F — expelled in HF
        node [ id 6 label "H" ]   # alcohol OH proton — expelled in HF
        edge [ source 1 target 2 label "-" ]   # Ar-F bond, broken
        edge [ source 5 target 6 label "-" ]   # alcohol O-H, broken
    ]
    context [
        node [ id 1 label "C" ]   # aromatic C bearing the leaving group
        node [ id 5 label "O" ]   # alcohol O — becomes ether O
    ]
    # R: Ar(1)-O(5)-C(sp3) ether plus expelled HF (atoms 2, 6)
    right [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]   # new Ar-O bond
        edge [ source 2 target 6 label "-" ]   # new H-F bond
    ]
]
```

**Verifier sanity checks the rule should pass:**

- BFS from `retained_root_atom: 1` through R-side edges reaches atoms 1, 5 (the Ar–O–C linkage, then onto the substrate context). It does **not** reach atoms 2, 6 (the HF), so they are correctly classified as byproduct.
- Mass balance: L mass − R mass = 0 (atoms 2, 6 appear on both sides). Bond-mass delta: 2 bonds broken (1–2, 5–6), 2 bonds formed (1–5, 2–6). Atoms conserved. ✓
- Byproduct mass: M(F) + M(H) = 18.998 + 1.008 = 20.006 g/mol. Matches `byproduct_mass_g_per_mol`. ✓

**Difference from `macrolactonization.gml`:**

The lactone rule has *three* breaking bonds (1–3, 3–4, 5–6) and *three* forming bonds (1–5, 3–4, 3–6) because water has three atoms reorganized. The aryl-ether rule has only *two* breaking bonds (1–2, 5–6) and *two* forming bonds (1–5, 2–6) because HF has only two atoms. The aryl C (1) and alcohol O (5) appear in `context` (unchanged identity); the F (2) and H (6) appear in `left` and `right` (their bond partners change). The aromatic ring substructure around C-1 (the rest of the arene) is **not** declared in the rule body — MØD's DPO span only names the atoms whose bonds change, and the rest is inherited from the substrate via the morphism. This mirrors how the lactam/lactone rules handle the seco-acid's α-carbon.

---

## Section 3 — Reagent + byproduct mass for each mechanism

The columns are: total reagent mass per ring closure (activator + auxiliary base/catalyst), and the post-activation byproduct mass *in addition* to the H–LG accounted for at the bond level. Reagent costs vary substantially across the three mechanisms.

| Activator | Coupling agent stack | Auxiliaries (typical) | reagent_mass_g_per_mol | byproduct_mass_extra | Typical scope | Reference DOI |
|---|---|---|---|---|---|---|
| **SNAr (η⁶-arene-Cr) — CANONICAL** | Cr(CO)₆ (220.06) on the way in + Ce(NH₄)₂(NO₃)₆ (CAN, 548.22) decomplex | Cs₂CO₃ (325.82) base | **1094** | Cr(CO)₃·L₃ ligated species (~340) + CAN-spent oxidants (~480) ≈ **820** | Heavily strained Ar–O macrocycles where uncomplexed SNAr or Ullmann fails. The only literature path for 13-ring closure on the GKK1032A₂ scaffold. | 10.1002/asia.201601728 |
| **SNAr (electron-poor arene, no Cr)** | (substrate-borne nitro/ester activation) | K₂CO₃ (138.21) or Cs₂CO₃ (325.82) base; DMF or DMSO solvent | **326** (Cs₂CO₃) | KF or CsF (~58 or 152) + KHCO₃ or CsHCO₃ (~100 or 195) ≈ **170–350** | Workhorse for vancomycin / K-13 / OF4949 / bouvardin syntheses. Requires substrate to carry intrinsic activation (NO₂, CO₂R, CN) ortho or para to F. | 10.1055/s-1997-722 |
| **Cu Ullmann C–O coupling** | CuI (190.45, 5–20 mol%) | 1,10-phenanthroline (180.21) + Cs₂CO₃ (325.82); toluene or dioxane, 100–130 °C | **696** (full equiv stack) | CsI (259.81) or CsBr (212.81) + CsHCO₃ (193.92) ≈ **407–453** | Broad scope; the Uchiro 2011 hirsutellone B macrocyclization established it works for 13-ring decahydrofluorene scaffolds; failed for GKK1032A₂'s tighter ring. | 10.3390/catal10101103 (review); 10.1021/ol202748e (hirsutellone B) |
| **Pd Buchwald aryl ether** | Pd₂(dba)₃ (915.72, 2–5 mol%) + RockPhos (di-t-Bu-X-Phos analog, 472.6) or t-BuXPhos (424.6) | Cs₂CO₃ (325.82) or K₃PO₄ (212.27); toluene, 90–110 °C | **1714** (catalytic; effective stoichiometric component count <1 equiv) | CsHCO₃ + CsX (CsBr 212.81 typical) ≈ **407** | Mild, modern; broad scope on Ar-Br/OTf with primary alcohols. Underused for macrocyclization vs. C–N coupling; one report of intramolecular C–O on simple substrates. | 10.1021/ja990324r |
| **Mitsunobu (alcohol activation, inverts C(sp³))** | DIAD (202.21) + PPh₃ (262.29) | (none) | **464** | DIAD-H₂ hydrazide (204) + Ph₃P=O (278) ≈ **482** | Inverts alcohol C; mechanistically distinct from SNAr/Ullmann/Pd. **Excluded from this rule** — separate file recommended. | 10.1016/s0040-4039(03)00728-7 |

**Notes on the reagent mass column:**

- **η⁶-arene-Cr SNAr**: the 1094 g/mol figure is the sum of Cr(CO)₆ (220.06, 1 equiv to install the Cr(CO)₃ complex on the arene as a prep step), the CAN oxidant for decomplexation (548.22, 1 equiv), and the Cs₂CO₃ base (325.82, 1 equiv). The Cr(CO)₃ complex is installed *before* macrocyclization (a separate step), but the mass is properly debited to this transformation because the complex exists only to enable the SNAr closure. Light decomplexation (sunlamp + air) can replace CAN and would drop the activator mass to ~546 g/mol; this is the value to use if Workstream F treats decomplexation as a separate process step.
- **SNAr (no Cr) electron-poor arene**: 326 g/mol is just Cs₂CO₃. The "activation" comes from the substrate's intrinsic electron-withdrawing groups (NO₂, ester, etc.) so no separate activator is needed. This is the cheapest option and is the standard for vancomycin/K-13/bouvardin chemistry.
- **Ullmann**: 696 g/mol is one equivalent each of CuI catalyst (counted at full equivalent for accounting; in practice 5–20 mol% is used), phen ligand, and Cs₂CO₃ base. Practical mass is ~250–325 g/mol if Cu/phen are correctly accounted as catalytic. **For comparison to lactam/lactone process penalties, the full-stoichiometric value 696 is what's used in the meta.yaml.**
- **Pd Buchwald**: 1714 g/mol includes Pd₂(dba)₃ catalyst at full equivalent — this hugely overstates the real cost since Pd is at 2–5 mol%. The realistic process penalty is ~370 g/mol (RockPhos at 5–10 mol% + Cs₂CO₃ base). The high "nominal" mass is included to flag that the catalyst's heavy MW (Pd₂(dba)₃ = 915.72) dominates if naively counted.

**Process-AE intuition.** The bond-level rule sees only 20 g of HF (for the canonical fluoride leaving). The activator stack adds ~500–1700 g of byproduct/spent reagent per mole of ether formed. The bond-vs-process gap is much larger here (25×–85×) than for macrolactonization (~30×) because the Cr(CO)₃ complexation step is mass-expensive. This is exactly the kind of disparity the bond-vs-process AE split was designed to capture.

---

## Section 4 — Stereochemical handling

### 4.1 Preservation of stereo at the alcohol's C(sp³)

For the canonical **SNAr / Ullmann / Pd Buchwald** family: **the alcohol's carbon stereo is fully retained**. The mechanism — for both SNAr (addition-elimination with Meisenheimer intermediate at the arene C) and Ullmann/Buchwald (oxidative addition + reductive elimination at the metal) — operates entirely on the **aromatic carbon** (atom 1) and the **alcohol O–H bond** (atoms 5, 6). The C(sp³)–O bond (off-rule, lives in the substrate) is never broken. No inversion, no scrambling. This is analogous to the macrolactonization brief's "alcohol C is retained because activation happens on the acid side"; here it's "alcohol C is retained because activation happens on the arene".

This is the **central stereochemical fact** that makes the SNAr/Ullmann/Pd family the right canonical choice for ascomylactam A. Ascomylactam A's macrocyclization terminates at C-14 (an sp³ oxymethine with defined absolute configuration *R*); the SNAr closure preserves that.

### 4.2 Atropisomerism at the arene

For **biaryl ether** closures (Ar–O–Ar — not this rule, see §1.4), the closure can generate axial chirality (atropisomerism) at the new ether bridge if the two arenes carry ortho substituents that hinder rotation. The vancomycin family is the textbook case: the CD and DE biaryl ether rings of vancomycin generate atropisomers that must be resolved or equilibrated thermodynamically (see [[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis|Boger et al. (1999)]] for "ordered atropisomer equilibrations").

For **Ar–O–C(sp³) alkyl-aryl ether** closures (this rule's scope), atropisomerism can still arise — and *does* in ascomylactam A. The 13-membered ring is rigid enough that the *para*-arene cannot freely rotate inside the ring (per the Ascomylactam A structure brief, §5 — H-5′/H-9′ and H-6′/H-8′ are NMR-inequivalent). The atropisomer is fixed by the macrocyclization. **The rule does not need to encode the atropisomerism explicitly** — it emerges from the 3D geometry of the substrate at closure. Workstream A's M5 encoding strategy already handles atropisomers via the V2000 3D coordinates (per the Ascomylactam A brief, §5 item 4).

**Stereo flag declaration**: this rule preserves alcohol C(sp³) stereo, can preserve or generate atropisomerism depending on substrate, and never inverts the C(sp³).

### 4.3 Mitsunobu inversion is a separate mechanism

Mitsunobu macroetherification (DIAD + PPh₃, ROH + ArOH → Ar–O–R) activates the **alcohol** and inverts the C(sp³) bearing the O ([[Shi Hughes McNamara 2003 - Mitsunobu Tertiary Alkyl Aryl Ether|Shi, Hughes, McNamara (2003)]], DOI `10.1016/s0040-4039(03)00728-7`, demonstrates complete inversion for tertiary alkyl-aryl ethers). This is the same scenario flagged in the macrolactonization brief (§4) for Mitsunobu macrolactonization: a separate rule with `inverts_alcohol_stereo` should be added if/when a target requires it. **For ascomylactam A, Mitsunobu is the wrong call — the C-14 stereo must be preserved.**

### 4.4 Stereo flags to declare

```yaml
stereo_flags:
  - retains_alcohol_stereo            # C(sp3)-O bond is off-rule; alcohol C never touched
  - retains_arene_substituents        # SNAr/Ullmann/Buchwald all preserve ring substituents
  - can_generate_atropisomerism       # for rigid macrocycles; resolved by 3D substrate geometry
```

(`retains_alcohol_stereo` is shared with the lactone rule; `retains_arene_substituents` is new and aryl-ether-specific; `can_generate_atropisomerism` is the flag Workstream F should add to its taxonomy.)

---

## Section 5 — Uchiro GKK1032A₂ deep dive (the direct sibling)

This is the canonical literature reference for the M5 ascomylactam A run. The atom-by-atom procedure tells us what the rule needs to express.

### 5.1 The compound

GKK1032A₂ is a cyclopenta[b]fluorene-fused 13-membered macrocyclic alkaloid from *Penicillium* sp. (Onodera 2003). Same (6/5/6/5)-tetracyclic core as ascomylactam A; same 13-ring closure via Ar–O–C(sp³) ether at the cyclopenta[b]fluorene C-14-equivalent bridgehead. The Wu et al. biosynthesis paper (PMC8094548) places GKK1032A₂, pyrrocidines, hirsutellones, and ascomylactams in the same biosynthetic family — the macrocyclic *para*-cyclophane-containing fungal natural products derived from PKS-NRPS hybrids.

### 5.2 The synthesis approach (Uchiro, 2011 → 2017)

**2011 — Hirsutellone B (the warm-up)**, [[Uchiro Kato Arai Hasegawa Kobayakawa 2011 - Hirsutellone B Ullmann Macrocyclization|Uchiro, Kato, Arai, Hasegawa, Kobayakawa (2011)]], *Org. Lett.* 13, 6268–6271, DOI `10.1021/ol202748e`. The Uchiro group established that the 13-membered cyclopenta[b]fluorene macrocycle could be closed by **Cu-mediated Ullmann C–O coupling** of an aryl iodide phenol-protected substrate with the C-14 sp³ alcohol. Hirsutellone B has a slightly less strained ring than GKK1032A₂; the Ullmann succeeded.

**2017 — GKK1032A₂ (the target)**, [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization|Sugata et al. (2017)]], *Chem. Asian J.* 12, 628–632, DOI `10.1002/asia.201601728`. The same Ullmann strategy *failed* for GKK1032A₂ because the additional ring strain prevented the Cu-mediated oxidative addition / reductive elimination cycle from closing the macrocycle. The group switched to an **η⁶-arene-Cr(CO)₃ activated SNAr** strategy. The substrate's *para*-fluoroarene was first complexed to Cr(CO)₃, then treated with base (KH) to deprotonate the C-14 alcohol; the resulting alkoxide attacks the activated arene C bearing F, displacing F⁻ in a Meisenheimer-style addition-elimination. **The Cr(CO)₃ complex is the activator** — it withdraws electron density from the arene, making the C–F bond susceptible to nucleophilic substitution that an uncomplexed aryl fluoride would not undergo.

**Decomplexation:** after macrocyclization, the Cr(CO)₃ is removed by sunlamp irradiation in air (or by I₂ or CAN treatment). The Cr leaves as Cr(CO)₃·(MeCN)₃ or similar, regenerating the free aryl ether.

### 5.3 Atom-by-atom flow (canonical reading)

1. **Pre-activation**: linear precursor with C-14 OH (the sp³ alcohol) and a *para*-substituted aryl fluoride. Complex the aryl fluoride with Cr(CO)₆ in refluxing dibutyl ether / THF → η⁶-(ArF)Cr(CO)₃ substrate.
2. **Deprotonation**: KH (or NaH) in THF at low temperature deprotonates the C-14 OH → C-14 alkoxide.
3. **Macrocyclization (SNAr)**: alkoxide attacks the activated aryl-F carbon. Meisenheimer intermediate forms (the arene-Cr complex stabilizes the negative charge on the dearomatized ring). Fluoride departs, the ring rearomatizes, and the new Ar–O–C(sp³) bond closes the 13-ring. This is the **rule firing**.
4. **Decomplexation**: photolysis under air, or oxidative removal with CAN, liberates the Cr(CO)₃ fragment. Product is the free macrocyclic aryl ether.

### 5.4 What this tells us about the rule

- **The leaving group is fluoride.** Other halides (Cl, Br, I) work for Ullmann but not for SNAr at uncomplexed arenes; F is preferred for SNAr because the C–F bond polarizes more under Meisenheimer conditions despite being thermodynamically stronger. The Cr-activation generalizes to any aryl-X but F is the standard.
- **The activator (Cr(CO)₃) is not in the bond-level rule.** The rule fires on the η⁶-(ArF)Cr → η⁶-(ArOR)Cr intermediate; the Cr(CO)₃ is a substrate decoration that exists for the SNAr step and is removed afterwards. This is the same pattern as Yamaguchi's mixed anhydride in macrolactonization — the activator is process-level, not bond-level.
- **Ring size 13 is at the edge of feasibility.** Uchiro's failure of the uncomplexed Ullmann tells us the rule's strategy filter should flag 13-rings as "strained, prefer SNAr/Cr". This is a Workstream D forbidden-context predicate (see §6).
- **The alcohol C stereo is preserved.** Uchiro's product retains the C-14 (*R*) absolute configuration of the precursor — confirming `retains_alcohol_stereo` for the rule.

### 5.5 Direct analogy to ascomylactam A

Ascomylactam A and GKK1032A₂ are nearly isostructural in the cyclopenta[b]fluorene + 13-macrocycle region. They differ in the γ-lactam decoration (γ-lactam in AsA, related lactam in GKK1032A₂) and the substitution pattern on the *para*-arene. The retrosynthetic call for ascomylactam A is **literally the Uchiro 2017 SNAr disconnection applied to a different substituent pattern**. For the M5 run, ascomylactam A should be encoded with an η⁶-arene-Cr SNAr activator hint (or the canonical SNAr if the substrate carries intrinsic activation).

---

## Section 6 — Forbidden contexts for Workstream D

The rule fires only when the substrate is compatible. Workstream D's strategy/feasibility predicates should block firings in these cases:

1. **Free ortho thiol or ortho amine on the arene.** Both compete with the alcohol O for SNAr — thiolates are more nucleophilic (HSAB), amines more basic. If the substrate has ArOH and Ar–SH or Ar–NHR on the same arene, the thiol/amine will close first. Predicate: `arene_partner_must_not_have_ortho_SH_or_NHR`.
2. **Electron-rich arene without an installed DG.** SNAr requires the arene to carry electron-withdrawing groups (NO₂, CO₂R, CN, CF₃, or be Cr(CO)₃-activated). A bare phenol or anisole will not undergo SNAr. Predicate: `arene_partner_must_have_EWG_or_Cr_complex`.
3. **Ring size < 12.** Below 12, the macrocyclic strain is too high for the Meisenheimer intermediate to form (Uchiro's failure with Ullmann at 13 suggests SNAr is also marginal below 12; literature consensus is that biaryl-ether SNAr macrocyclization works at 14–22 and is harder at 13). Predicate: `ring_size >= 12`.
4. **Sp³ alcohol bearing a β-leaving group.** If the alcohol C(sp³) is in α-position to a halide or sulfonate, the alkoxide can β-eliminate. Predicate: `alcohol_partner_must_not_have_beta_LG`.
5. **Phenol acting as alcohol (would form Ar–O–Ar biaryl ether instead).** This rule covers Ar–O–C(sp³); if the alcohol input is a phenol, the closure forms a biaryl ether and should fire the (future) `biaryl_etherification` rule instead. Predicate: `alcohol_partner_C_must_be_sp3`.
6. **Free aliphatic amine** (–NHR or –NH₂) elsewhere on the chain. Amines are more nucleophilic than alcohols; they will close to give a macrolactam variant (Buchwald amination) instead of the aryl ether. Predicate: `no_other_nucleophiles_on_tether`.

These predicates belong in `macrocert.generate.strategies` (the strategy file), not in the rule body. The rule body declares the bond-level chemistry; the strategy declares when it is safe to fire.

---

## Section 7 — Citations

The 8+ key DOIs, with one-line summaries. **All paper citations are wiki-linked per the project's paper-linking policy.** External nodes will need to be created for any not already in the graph.

1. [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization|Sugata, Inagaki, Ode, Hayakawa, Karoji, Baba, Kato, Hasegawa, Tsubogo, Uchiro (2017)]] — `10.1002/asia.201601728`
   *The direct sibling. First enantioselective total synthesis of GKK1032A₂ via η⁶-arene-Cr SNAr 13-membered macrocyclization. Chem. Asian J. 12, 628–632. **Canonical reference for the ascomylactam A retrosynthesis.***

2. [[Uchiro Kato Arai Hasegawa Kobayakawa 2011 - Hirsutellone B Ullmann Macrocyclization|Uchiro, Kato, Arai, Hasegawa, Kobayakawa (2011)]] — `10.1021/ol202748e`
   *Total synthesis of hirsutellone B via Ullmann-type direct 13-membered macrocyclization. Org. Lett. 13, 6268–6271. 66 citations. The Uchiro group's Ullmann predecessor to the GKK1032A₂ paper; establishes Cu Ullmann as a viable activator for the cyclopenta[b]fluorene family at 13-ring scale.*

3. [[Zhu 1997 - SNAr Macrocyclization Biaryl Ether|Zhu (1997)]] — `10.1055/s-1997-722`
   *SNAr-based macrocyclization via biaryl ether formation: application in natural product synthesis. Synlett 1997, 133–144. **164 citations** — the field-defining review. Catalogs > 30 SNAr-based macroetherifications across vancomycin / K-13 / OF4949 / bouvardin / chloropeptin / RA-VII. Companion to the Boger 1995 paper.*

4. [[Boger Borzilleri 1995 - SNAr Biaryl Ether Macrocyclization Bouvardin|Boger, Borzilleri (1995)]] — `10.1016/0960-894x(95)00192-v`
   *"An unusually facile SNAr 14-membered biaryl ether macrocyclization reaction suitable for preparation of the cycloisodityrosine subunit of bouvardin, deoxybouvardin and related agents." Bioorg. Med. Chem. Lett. 5, 1187–1190. 30 citations. **One of the earliest demonstrations of SNAr biaryl ether macrocyclization on a natural-product scaffold.***

5. [[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis|Boger, Miyazaki, Kim, Wu, Castle, Loiseleur, Jin (1999)]] — `10.1021/ja992577q`
   *Total Synthesis of the Vancomycin Aglycon. J. Am. Chem. Soc. 121, 10004–10011. 180 citations. **The vancomycin macrocyclization is biaryl ether SNAr** — see §7.1 for the categorization correction.*

6. [[Beugelmans Singh Bois-Choussy Chastanet Zhu 1994 - SNAr Vancomycin Models|Beugelmans, Singh, Bois-Choussy, Chastanet, Zhu (1994)]] — `10.1021/jo00098a010`
   *"SNAr-Based Macrocyclization: An Application to the Synthesis of Vancomycin Family Models." J. Org. Chem. 59, 5535–5542. 84 citations. The original demonstration that intramolecular SNAr forms biaryl ether macrocycles efficiently. Predates Boger 1999 by 5 years.*

7. [[Fui Sarjadi Sarkar Rahman 2020 - Ullmann C-O Coupling Review|Fui, Sarjadi, Sarkar, Rahman (2020)]] — `10.3390/catal10101103`
   *"Recent Advancement of Ullmann Condensation Coupling Reaction in the Formation of Aryl-Oxygen (C-O) Bonding by Copper-Mediated Catalyst." Catalysts 10, 1103. 34 citations. **Modern Cu/ligand systems; ligand-accelerated Ullmann; standard activator stack for the rule's `ullmann` alternative.***

8. [[Palucki Wolfe Buchwald 1997 - Palladium Catalyzed Aryl Ether|Palucki, Wolfe, Buchwald (1997)]] — `10.1021/ja9640152`
   *"Palladium-Catalyzed Intermolecular Carbon−Oxygen Bond Formation: A New Synthesis of Aryl Ethers." J. Am. Chem. Soc. 119, 3395–3396. 196 citations. **The Buchwald aryl ether milestone.** Followed up by the broader-scope Aranyos 1999 paper (DOI `10.1021/ja990324r`) which is the canonical Buchwald aryl ether reference (515 citations).*

9. [[Aranyos Old Kiyomori Wolfe Sadighi Buchwald 1999 - Diaryl Ethers Bulky Phosphines|Aranyos, Old, Kiyomori, Wolfe, Sadighi, Buchwald (1999)]] — `10.1021/ja990324r`
   *"Novel Electron-Rich Bulky Phosphine Ligands Facilitate the Palladium-Catalyzed Preparation of Diaryl Ethers." J. Am. Chem. Soc. 121, 4369–4378. 515 citations. **The standard Pd Buchwald aryl ether reference for primary alcohols and aryl bromides; ligand of choice is t-BuXPhos / RockPhos family.***

10. [[Shi Hughes McNamara 2003 - Mitsunobu Tertiary Alkyl Aryl Ether|Shi, Hughes, McNamara (2003)]] — `10.1016/s0040-4039(03)00728-7`
    *"Stereospecific synthesis of chiral tertiary alkyl-aryl ethers via Mitsunobu reaction with complete inversion of configuration." Tetrahedron Lett. 44, 3609–3611. 66 citations. **Confirms Mitsunobu inverts the C(sp³) — the basis for excluding Mitsunobu from this rule.***

Bonus references (not in the core 8 but worth keeping):

- [[Yan Wu 2022 - Cyclopenta[b]fluorene Biosynthesis|Yan, Wu et al. (2021)]] — PMC8094548. Biosynthesis of the para-cyclophane-containing hirsutellone family of fungal natural products. Confirms the GKK1032A₂ / pyrrocidine / hirsutellone / ascomylactam biosynthetic relationship.
- [[Tlili Taillefer 2013 - Ullmann Arylation Alcohols Thiols|Tlili, Taillefer (2013)]] — `10.1002/9781118690659.ch2`. "Ullmann Condensation Today: Arylation of Alcohols and Thiols with Aryl Halides." Book chapter in *Copper-Mediated Cross-Coupling Reactions*. Comprehensive modern Cu/ligand review.
- [[Mann Hartwig 1997 - Pd Diaryl Ethers Aryl Bromides|Mann, Hartwig (1997)]] — `10.1016/s0040-4039(97)10175-7`. "Palladium-Catalyzed Formation of Diaryl Ethers from Aryl Bromides. Electron Poor Phosphines enhance Reaction Yields." Tetrahedron Lett. 38, 8005–8008. 123 citations. Hartwig's complement to the Buchwald aryl ether work.
- [[Mann Incarvito Rheingold Hartwig 1999 - Pd Diaryl Ether Mechanism|Mann, Incarvito, Rheingold, Hartwig (1999)]] — Pd C–O coupling mechanism: sterically induced reductive elimination forms the C–O bond in diaryl ethers. Mechanistic foundation.

### 7.1 IMPORTANT: Boger vancomycin categorization correction

**The proposal's panel categorization places Boger's vancomycin total synthesis under "macrolactamization". This is a chemistry error.** Vancomycin's macrocyclic closures comprise:

- **Two biaryl ether (Ar–O–Ar) macrocycles**: the **CD ring (16-membered)** and the **DE ring (16-membered)**. Both close by **SNAr macroetherification** in Boger's syntheses (DOI `10.1021/ja992577q`, 1999; DOI `10.1021/ja990189i`, 1999; *J. Am. Chem. Soc.* 2001 follow-up `10.1021/ja011163q` for atropisomerism).
- **One biaryl (Ar–Ar) macrocycle**: the **AB ring (12-membered)**, closed by **Ni(0)-mediated biaryl coupling** (Ullmann-style aryl–aryl, not aryl–ether).
- **One macrolactam closure** for the peptide backbone (16- or 17-membered amide ring).

So vancomycin involves all three of macrolactamization, biaryl coupling, *and* macroetherification — but the two SNAr biaryl ether closures (CD and DE rings) are macroetherification, not macrolactamization. **For the MØD-MacroCert panel, vancomycin should be a panel case for the new `aryl_etherification` (or, more precisely, `biaryl_etherification`) rule, NOT for the existing `macrolactamization` rule.**

Workstream A should:

1. Remove vancomycin from the macrolactamization panel (or keep it only for the peptide amide closure, separately encoded).
2. Add vancomycin's CD and DE biaryl ether macrocyclizations as panel cases for the new `biaryl_etherification` rule (sibling to this `aryl_etherification` rule — same SNAr mechanism, atom 5 changes from sp³ O to aromatic ring O, the alcohol partner becomes a phenol).
3. Note in the panel that vancomycin is a 4-tactic target (macroetherification × 2, biaryl × 1, macrolactamization × 1) and exercises rule composition.

The other 4 sibling biaryl-ether NPs Boger / Zhu / Nicolaou worked on (K-13, OF4949, bouvardin, deoxybouvardin, RA-VII, chloropeptin, complestatin) are also biaryl ether macrocyclizations — they all go in the biaryl-etherification rule panel, not the aryl-etherification (alkyl-aryl) panel. **For the aryl_etherification rule (this rule), the panel cases are the GKK1032/hirsutellone/ascomylactam family** — alkyl-aryl ether closure.

---

## Section 8 — Toy substrate proposal

**Recommendation:** Add a new panel case, `aryl_ether_14_from_omega_hydroxy_para_fluoroarene`, parallel to the existing lactam_16 / lactone_16 panels but at 14-ring (to match the Boger 1995 SNAr precedent for ring sizes in the natural-product range, and to be slightly less strained than the 13-ring GKK1032A₂ — leaving the 13-ring as the harder ascomylactam A target).

### 8.1 The surrogate

The simplest viable surrogate is an ω-hydroxyalkyl chain tethered at one end to a *para*-fluoro-*meta*-nitrobenzene through a CH₂ linker. Structure:

```
                    F
                    |
  HO–(CH2)10–CH2–(arene)–CH2–CH2–[closure here]
                    |
                   NO2
                    |
                    (rest of arene)
```

Specifically: **(11-hydroxy)undecyl-(3-nitro-4-fluorobenzyl)ether-precursor**, drawn as a linear chain that closes to a 14-membered aryl ether macrocycle via SNAr displacement of F by the ω-OH.

Why this design:
- **14-ring matches the Boger 1995 SNAr biaryl ether precedent** (DOI `10.1016/0960-894x(95)00192-v` reports "unusually facile" SNAr 14-ring closure on the bouvardin scaffold). The toy substrate inherits this favorable ring size.
- **3-Nitro-4-fluoro activation pattern** is the textbook SNAr activator. The ortho-NO₂ stabilizes the Meisenheimer intermediate; the para-F is the leaving group.
- **No additional functional groups** — just an aryl fluoride, a primary alcohol, and a methylene tether. This isolates the rule firing from competing nucleophiles or stereocenters.
- **Cs₂CO₃ / DMF, 80–100 °C** is the standard activator stack — well-documented, doesn't require Cr(CO)₃ complexation. The surrogate exercises the `sn_ar_no_chromium` (cheap) activator alternative, not the Cr-activated canonical for ascomylactam A.

### 8.2 Hexafluorobenzene SNAr variant (alternative surrogate)

If a smaller / simpler substrate is preferred: **5-hydroxypentyl-pentafluorobenzene ether** as a 14-ring closure surrogate. Hexafluorobenzene is *the* canonical electron-poor SNAr arene — every F is leaving-group-active. The closure displaces one ortho-F to form the macrocycle; the remaining 4 F atoms are preserved in the product.

```
F5–C6–CH2–(CH2)4–OH → cyclic 14-ring (ArO–C5H10–CH2-Ar, with 5 F still on the arene)
```

This is the cleanest possible SNAr surrogate. Reagent stack: Cs₂CO₃, DMF, 60–80 °C, ~12 h. Reference for the chemistry: standard SNAr literature; no specific natural-product paper, but the chemistry is textbook (e.g., included in Lipshutz's lab manual chapter `10.1016/b978-0-443-23905-2.00009-8`).

**Recommendation: use the 3-nitro-4-fluoro variant** because it's a closer chemical analog of the natural-product SNAr macrocyclizations (single F leaving, NO₂ activator), and because the byproduct mass calculation is simpler (HF: 20 g/mol, clean) rather than a multi-F arene where the rule would fire many possible regioisomers.

### 8.3 Panel files needed

```
data/validation_panel/aryl_ether_14_from_omega_hydroxy_para_fluoro_meta_nitro/
  structure.mol      # 14-membered macrocyclic aryl ether product
  runspec.yaml       # mirrors lactam_16 RunSpec, with rules: all_macrocyclization
  expected.yaml      # literature_tactic: aryl_etherification, ring_size: 14
  notes.md           # cites Boger 1995 + Zhu 1997 reviews
```

### 8.4 Suggested `expected.yaml`

```yaml
literature_tactic: aryl_etherification
literature_ring_size: 14
expected_witness: optimal
expected_top_rule_class: macrocyclization
ae_class: high
reference: |
  Surrogate aryl etherification case (14-membered ring, SNAr closure
  of an omega-hydroxyundecyl chain onto a 3-nitro-4-fluorobenzene).
  Designed to mirror Boger 1995 (DOI 10.1016/0960-894x(95)00192-v)
  and Zhu 1997 review (DOI 10.1055/s-1997-722) SNAr biaryl ether
  precedents for 14-ring closure. Activator: Cs2CO3, DMF, 80 C, no
  chromium complexation needed. The substrate's intrinsic NO2/F
  activation pattern makes it the cheapest aryl_etherification panel
  case; pending the literature panel (ascomylactam A 13-ring via
  Cr-SNAr) for the harder canonical case.
```

### 8.5 Suggested `runspec.yaml`

```yaml
name: aryl_ether_14_from_omega_hydroxy_para_fluoro_meta_nitro
target:
  structure_path: structure.mol
  ring_size: 14

blocks:
  - omega_hydroxyundecyl_para_fluoro_meta_nitro_benzyl

rules: all_macrocyclization

strategy:
  max_steps: 1
  ring_close_only: true

solver:
  backend: scip
  top_n: 3
  time_budget_s: 30
  extra:
    activator: sn_ar_no_chromium

energetics:
  enabled: false

notes: |
  Surrogate aryl etherification case (ring size 14).
  Closes via one firing of aryl_etherification (SNAr fluoride).
  Cousin of lactam_16 and lactone_16 panels.
  Tests the SNAr "no chromium" alternative (cheapest activator path).
```

### 8.6 Also update `data/rules/_index.yaml`

The `all_macrocyclization` and `high_ae_macrocyclization` sets should both include the new `aryl_etherification` rule:

```yaml
sets:
  all_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification     # new
    - rcm
    - transannular_diels_alder

  high_ae_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification     # new, HF byproduct (20 g/mol), even lower than H2O
    - rcm
    - transannular_diels_alder

  fungal_decahydrofluorene:    # new set, suggested
    - aryl_etherification      # for ascomylactam, GKK1032, hirsutellone, pyrrocidine family
    - transannular_diels_alder # for the (6/5/6/5) core construction (Uchiro 2024-2026 IMDA)
```

---

## Section 9 — Proposed `meta.yaml` (full draft, ready to encode)

```yaml
# Aryl etherification rule metadata (consumed by macrocert.spec.rules).
# See data/rules/aryl_etherification.gml for the DPO span. Application
# conditions (ring closure on a single component, ring-size membership in
# the macrocyclic range, arene must carry EWG or Cr complex, alcohol C
# must be sp3, etc.) live in macrocert.generate.strategies, not here.

# Process-level reagent mass: activator + auxiliaries per firing.
# Canonical activator: SNAr (eta6-arene-Cr) — the only mechanism with
# direct literature precedent on the 13-ring cyclopenta[b]fluorene
# (Uchiro 2017 for GKK1032A2). Mass: Cr(CO)6 (220) + CAN decomplex
# (548) + Cs2CO3 base (326) = ~1094 g/mol.
# Per-substrate overrides in RunSpec.solver.extra can select alternatives
# from `reagent_mass_alternatives` below.
reagent_mass_g_per_mol: 1094.0

# Bond-level expelled mass: HF, from the rule's atom-map (atoms 2, 6
# form the HF byproduct on the R side). Recomputed by the verifier in
# M2 from the composed rule; kept here as a human-checkable ground truth.
byproduct_mass_g_per_mol: 20.006

# Which atom ID in the rule body anchors the *retained* product side on R.
# Used by the verifier's bond-level AE recomputation: BFS from this atom
# through R's edges; everything reachable is target, the rest is byproduct.
retained_root_atom: 1

classes:
  - macrocyclization
  - aryl_ether_closure
  - high_atom_economy_bond    # HF (20 g/mol) at bond level — even cleaner than H2O
  - fungal_alkaloid           # GKK1032 / hirsutellone / ascomylactam / pyrrocidine family
  - phenolic_natural_product

# Activator alternatives. Each entry overrides reagent_mass_g_per_mol
# at the RunSpec layer. byproduct_mass_extra is the *additional* mass
# beyond the bond-level 20.006 g/mol of HF; the verifier adds it to
# the HF byproduct when computing process-AE under that activator.
reagent_mass_alternatives:
  sn_ar_chromium:
    reagent_mass_g_per_mol: 1094.0
    byproduct_mass_extra: 820.0    # spent Cr(CO)3-L3 (~340) + CAN-derived oxidants (~480)
    description: "SNAr via eta6-arene-Cr(CO)3; the canonical Uchiro-2017 GKK1032A2 protocol"
    doi: "10.1002/asia.201601728"
  sn_ar_no_chromium:
    reagent_mass_g_per_mol: 326.0
    byproduct_mass_extra: 250.0    # CsF (152) + CsHCO3 (98)
    description: "SNAr at intrinsically activated arene (NO2/CO2R/CN ortho/para to F); Cs2CO3 base"
    doi: "10.1055/s-1997-722"
  ullmann:
    reagent_mass_g_per_mol: 696.0
    byproduct_mass_extra: 425.0    # CsX (~225 for Cs-Br) + CsHCO3 (193.92)
    description: "CuI + 1,10-phen + Cs2CO3; toluene, 100-130 C; Uchiro-2011 hirsutellone B protocol"
    doi: "10.1021/ol202748e"
  buchwald:
    reagent_mass_g_per_mol: 1714.0
    byproduct_mass_extra: 407.0    # CsBr (213) + CsHCO3 (194)
    description: "Pd2(dba)3 + RockPhos + Cs2CO3; toluene, 90-110 C (Pd catalytic in practice; mass as stoichiometric)"
    doi: "10.1021/ja990324r"

stereo_flags:
  - retains_alcohol_stereo          # alcohol C(sp3) is off-rule; never touched
  - retains_arene_substituents      # all activators preserve arene substituents
  - can_generate_atropisomerism     # for rigid macrocycles; resolved by 3D substrate geometry

refs:
  - "Trost 1991, Science 254:1471 (atom economy)"
  - "Sugata, Inagaki, Ode, Hayakawa, Karoji, Baba, Kato, Hasegawa, Tsubogo, Uchiro 2017, Chem. Asian J. 12:628, DOI:10.1002/asia.201601728 (canonical SNAr-Cr GKK1032A2)"
  - "Uchiro, Kato, Arai, Hasegawa, Kobayakawa 2011, Org. Lett. 13:6268, DOI:10.1021/ol202748e (Ullmann hirsutellone B)"
  - "Zhu 1997, Synlett 1997:133, DOI:10.1055/s-1997-722 (SNAr biaryl ether macrocyclization review, 164 citations)"
  - "Boger, Borzilleri 1995, Bioorg. Med. Chem. Lett. 5:1187, DOI:10.1016/0960-894x(95)00192-v (SNAr 14-ring biaryl ether bouvardin)"
  - "Aranyos, Old, Kiyomori, Wolfe, Sadighi, Buchwald 1999, J. Am. Chem. Soc. 121:4369, DOI:10.1021/ja990324r (Pd-catalyzed diaryl ethers)"
  - "Fui, Sarjadi, Sarkar, Rahman 2020, Catalysts 10:1103, DOI:10.3390/catal10101103 (modern Ullmann C-O review)"

notes: |
  Aryl alkyl ether (Ar-O-C(sp3)) ring closure expelling HF (or HX) at
  the bond level. Process-level AE is docked by the activator —
  SNAr-Cr (Uchiro-2017, ~1094 g/mol) is assumed canonical, with
  SNAr-no-Cr / Ullmann / Buchwald available as alternatives via
  reagent_mass_alternatives. This is the proposal section 3.3
  bond-vs-process AE split materialized; the activator choice spans
  3x in reagent mass (326 g for SNAr-no-Cr -> 1094 g for SNAr-Cr ->
  1714 g for Buchwald) and reflects substrate constraints rather than
  cost preference.

  Mitsunobu macroetherification (DIAD/PPh3, ROH + ArOH, inverts alcohol
  C(sp3)) is NOT covered by this rule — it is a stereo-inverting
  variant and should be a separate rule (Workstream F).

  Biaryl ether macroetherification (Ar-O-Ar, atom 5 becomes sp2 aromatic
  O instead of sp3 O) is NOT covered by this rule — it is the
  vancomycin / K-13 / OF4949 / bouvardin closure and should be a
  separate sibling rule `biaryl_etherification.gml`. This is the same
  SNAr mechanism but the alcohol partner is a phenol (sp2 C-O), not
  an alkyl alcohol (sp3 C-O), and atropisomerism is the dominant
  stereochemical concern.

  GKK1032A2 (Sugata-Uchiro 2017, DOI:10.1002/asia.201601728) and
  hirsutellone B (Uchiro 2011, DOI:10.1021/ol202748e) are the panel
  cases for the canonical (SNAr-Cr) and Ullmann variants respectively.
  Ascomylactam A (Workstream A target, M5 run) inherits the SNAr-Cr
  canonical protocol.

  IMPORTANT FOR WORKSTREAM A: The proposal's panel categorization
  places Boger's vancomycin under "macrolactamization". This is a
  chemistry error — vancomycin's CD and DE macrocycles are biaryl
  ether SNAr closures, which belong to a separate (future)
  `biaryl_etherification` rule. Only the peptide backbone closure of
  vancomycin is macrolactamization. See macroetherification_research.md
  §7.1 for the full correction.
```

---

## Section 10 — Proposed GML structure (full sketch)

The full GML, ready for transcription into `data/rules/aryl_etherification.gml`:

```
rule [
    ruleID "aryl_etherification (SNAr Ar-O-C(sp3) ring closure, -HF)"
    # L: aromatic C(1) bearing F(2) and alcohol O(5)-H(6)
    left [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 5 target 6 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 5 label "O" ]
    ]
    # R: aryl ether C(1)-O(5) plus expelled HF (atoms 2, 6)
    right [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
    ]
]
```

**Key sections:**

- **`left`**: declares the two "to-be-expelled" atoms (F at position 2, H at position 6) and the two bonds that break (the aromatic C–F bond 1–2; the alcohol O–H bond 5–6). The aromatic ring's other atoms (the rest of the arene around C-1) are *not* declared because they don't participate in bond changes — MØD inherits them from the substrate via the morphism, identically to how the lactam/lactone rules inherit the α-carbon and the alcohol's α-carbon.
- **`context`**: the two atoms whose identity and existence don't change — the aromatic C (1) and the alcohol O (5). They're listed in context because both appear in L (bonded to the leaving group / H respectively) and in R (bonded to each other), and DPO formalism requires them in the morphism span.
- **`right`**: declares the new Ar–O bond (1–5) and the new H–F bond (2–6) that reconstitutes HF as the byproduct.

**Variants** (per-LG; lives in `reagent_mass_alternatives`, not separate GML files):

- For LG = Cl: change `node [ id 2 label "F" ]` to `"Cl"`. Byproduct mass becomes 36.461 g/mol (HCl). Atom map otherwise identical.
- For LG = Br: change to `"Br"`. Byproduct mass 80.912 g/mol (HBr).
- For LG = I: change to `"I"`. Byproduct mass 127.912 g/mol (HI).

**Recommendation: keep one GML file with F as the canonical leaving group**, and handle the alternative leaving groups via the strategy file's `expand_leaving_groups` predicate (Workstream D). The verifier's mass calculation is parameterized by the actual element of atom 2 in the composed rule, so it will recompute the byproduct mass correctly for any halogen.

**Difference from `macrolactamization.gml`:**

The lactam rule has *six* atoms in the rule body (1–6: acid C, two carbonyl Os, acid OH proton, amine N, amine NH proton); the aryl-ether rule has *four* atoms (1, 2, 5, 6). The aryl-ether rule is structurally smaller because HF is a 2-atom byproduct vs. H₂O which is 3-atom. The IDs are chosen so that 1 and 5 carry the same meaning across rules ("first partner C/Ar; second partner heteroatom") and 6 carries the same meaning ("proton expelled from the alcohol/amine side"). ID 2 here is the LG; in the lactam/lactone rules, ID 2 is the carbonyl O that remains in product.

**Verifier sanity checks the rule should pass:**

- BFS from `retained_root_atom: 1` through R-side edges reaches atoms 1, 5 (the Ar–O linkage). It does **not** reach atoms 2, 6 (the HF), so they are correctly classified as byproduct. ✓
- Mass balance: L mass − R mass = 0 (atoms 2, 6 appear on both sides). Bond-mass delta: 2 bonds broken (1–2, 5–6), 2 bonds formed (1–5, 2–6). Atoms conserved. ✓
- Byproduct mass: M(F) + M(H) = 18.998 + 1.008 = **20.006 g/mol**. Matches `byproduct_mass_g_per_mol`. ✓

---

## Open questions / followups for Ivan

1. **`biaryl_etherification` rule (sibling).** The vancomycin / K-13 / bouvardin family closes by Ar–O–Ar SNAr (not Ar–O–C(sp³)). Same mechanism, atom 5 changes from sp³ alcohol O to phenolic O on an aromatic ring. This should be a sibling rule file. **Recommendation**: write it as part of the same Workstream C effort to enable panel cases for Boger vancomycin and Zhu's substrate library. The atom-map will be nearly identical (atom 5 becomes the phenolic O of a separate arene).
2. **Activator field naming**. I've used `sn_ar_chromium` / `sn_ar_no_chromium` / `ullmann` / `buchwald`. Workstream F may want a hierarchical structure (e.g., `sn_ar.chromium` vs `sn_ar.intrinsic`). The chemistry content is unchanged.
3. **Leaving-group expansion**. Workstream D should add a strategy predicate that expands the F-canonical rule to Cl/Br/I variants when the substrate carries those LGs. The verifier handles the mass recomputation cleanly because atom 2's element is read from the composed rule.
4. **Cr(CO)₃ as a substrate decoration vs. activator step.** Current meta.yaml debits the full Cr(CO)₆ + CAN mass to this rule's process-AE. If Workstream F treats Cr complexation as a *separate* preparation step (with its own AE accounting), the canonical reagent_mass_g_per_mol should drop to ~326 g/mol (just the Cs₂CO₃ base) and the Cr cost becomes a `prep_step.activator_mass`. Recommend keeping the current aggregated accounting for v0; revisit when the multi-step process AE machinery is in place.
5. **Vancomycin panel re-categorization.** Per §7.1, vancomycin needs to be moved from the macrolactamization panel to the (future) `biaryl_etherification` panel. This is a Workstream A correction. Workstream A's `panel_TODO.md` should reflect this.
6. **Ascomylactam A RunSpec.** When the M5 run is assembled, ascomylactam A's RunSpec should set `solver.extra.activator: sn_ar_chromium` to inherit Uchiro 2017's canonical conditions. If Workstream A prefers to test alternatives, also enable `ullmann` (per Uchiro 2011 hirsutellone B precedent).

---

## Cross-references in the vault

- [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization]]
- [[Uchiro Kato Arai Hasegawa Kobayakawa 2011 - Hirsutellone B Ullmann Macrocyclization]]
- [[Zhu 1997 - SNAr Macrocyclization Biaryl Ether]]
- [[Boger Borzilleri 1995 - SNAr Biaryl Ether Macrocyclization Bouvardin]]
- [[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis]]
- [[Beugelmans Singh Bois-Choussy Chastanet Zhu 1994 - SNAr Vancomycin Models]]
- [[Aranyos Old Kiyomori Wolfe Sadighi Buchwald 1999 - Diaryl Ethers Bulky Phosphines]]
- [[Palucki Wolfe Buchwald 1997 - Palladium Catalyzed Aryl Ether]]
- [[Fui Sarjadi Sarkar Rahman 2020 - Ullmann C-O Coupling Review]]
- [[Shi Hughes McNamara 2003 - Mitsunobu Tertiary Alkyl Aryl Ether]]
- [[Research - Ascomylactam A Structure - 2026-05-24]] — the Workstream A finding that drives this brief

(External nodes will need to be created for any not already in the graph: `vlt graph node add --type external.paper "Sugata Inagaki ... Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization"`, etc.)
