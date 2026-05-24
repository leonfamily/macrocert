# Intramolecular Horner–Wadsworth–Emmons Olefination Rule — Chemistry Research Brief

**Workstream:** C (Rule library expansion)
**Target artifacts:** `data/rules/hwe_olefination.gml` + `.meta.yaml`, plus the panel case `haidle_myers_cytochalasin_b_2004/`
**Date:** 2026-05-24
**Author:** researcher agent (for Ivan / Workstream C)
**Driver:** The Haidle–Myers 2004 cytochalasin B panel case closes its 14-membered macrolactone *and* L-696,474's 11-membered macrocarbocycle via **intramolecular Horner–Wadsworth–Emmons (HWE) olefination**. Macrocert v0 has no HWE rule. Without one, the panel case has to be encoded as `transannular_diels_alder` (a biosynthetic stretch) or `infeasible`. This brief grounds the design of a fifth macrocyclization rule whose bond-level chemistry is `C=C + dialkyl phosphate` rather than `C–X + H–X` / `C–C(O)–O + H₂O` / `C=C + CH₂=CH₂`.

This brief mirrors the structure of `macroetherification_research.md`. The key chemistry distinction is that HWE is an **addition–collapse** mechanism producing **alkene + dialkyl phosphate dianion**, not a metathesis (no olefin redistribution) and not a condensation (no water). The byproduct is heavier than HF, HCl, or H₂O — but the rule still has high bond-level atom economy because both new sp² carbons of the alkene come from the substrate, and the only atoms lost are those of the phosphonate ester group (which never belonged to the target).

> **DOI correction up front.** The task brief gives Haidle–Myers 2004 as DOI `10.1073/pnas.0307711101`. CrossRef shows that DOI resolves to van Welie–van Hooft–Wadman 2004, *PNAS* 101:5123–5128, a neuroscience paper on hippocampal Iₕ channels — **not** the cytochalasin synthesis. The correct DOI is **`10.1073/pnas.0402111101`** (*PNAS* 101:12048–12053, 86 CrossRef citations, PMC PMC514432). The panel case `haidle_myers_cytochalasin_b_2004/notes.md` already documents this; this brief uses the correct DOI throughout. (Cross-verified against the open-access PMC full text.)

---

## Section 1 — Distinction from RCM and other macrocyclic alkene methods

### 1.1 The bond-level transformation

HWE is one of three mechanistic families that close a macrocyclic C=C bond:

| Method | Mechanism class | New C=C atoms come from | Byproduct(s) | Default geometry |
| --- | --- | --- | --- | --- |
| **HWE olefination** (this rule) | Addition–collapse (1,2-oxaphosphetane) | Phosphonate α-C + aldehyde C | Dialkyl phosphate dianion (RO)₂PO₂⁻ + H⁺ | **E (anti-oxaphosphetane preferred)** |
| **Wittig** | Addition–collapse (1,2-oxaphosphetane) | Phosphonium ylide C + aldehyde C | Triphenylphosphine oxide Ph₃P=O | Mixed (Z for unstabilized, E for stabilized) |
| **Ring-closing metathesis (RCM)** | Metathesis (4-membered metallocyclobutane) | Both alkene carbons of two terminal olefins | Ethylene (CH₂=CH₂) | Mixed (Z favored kinetically) |

**Mechanistically HWE shares its 4-membered cyclic intermediate with Wittig but uses a phosphonate (RO)₂P(O)–CHR'-anion as the nucleophile** instead of a phosphonium ylide R₃P⁺=CHR. The phosphonate carbanion is stabilized by a second carbonyl group (the "β" of "β-keto-phosphonate") — a `(RO)₂P(O)–CH₂–C(O)–R` or `(RO)₂P(O)–CH₂–CO₂R` system. Without that β-electron-withdrawing group the reaction stops at the β-hydroxy-phosphonate (no oxaphosphetane forms, no elimination); see [[Boutagy Thomas 1974 - Olefin Synthesis with Organic Phosphonate Carbanions|Boutagy & Thomas (1974)]] for the canonical statement of this requirement.

The mechanism in four steps (per [[Wadsworth Emmons 1961 - The Utility of Phosphonate Carbanions in Olefin Synthesis|Wadsworth & Emmons (1961)]] and refined by Bisceglia & Orelli 2015):

1. **Deprotonation.** Base removes the α-H (between P=O and the second EWG) to give a phosphonate-stabilized carbanion.
2. **Addition.** The carbanion adds to the aldehyde C=O carbon to give a β-alkoxide; this step is reversible and is the **rate-determining step** for HWE (unlike Wittig, where addition is fast and the betaine collapse is rate-determining).
3. **Oxaphosphetane formation.** The alkoxide oxygen attacks the P to close a 4-membered 1,2-oxaphosphetane (the "WE intermediate").
4. **Retro-[2+2] collapse.** The oxaphosphetane fragments: the C–P and O–C bonds break, the C=C and P=O bonds form. Products: alkene + dialkyl phosphate ion `(RO)₂PO₂⁻`. The base is consumed; one H is delivered from solvent or from a second equivalent of phosphonate to give neutral `(RO)₂P(O)OH` on workup.

The **anti-1,2-oxaphosphetane** is more stable than the syn isomer (the bulky `(RO)₂P=O` and `R''` substituents are antiperiplanar in the 4-ring), and because the addition step is reversible while the collapse is irreversible, the system equilibrates and collapses **predominantly through the anti-oxaphosphetane**, delivering the **E-alkene**. The default E/Z ratio for stabilized phosphonates on aliphatic aldehydes is **≥10:1 to >50:1 E:Z** (see Bisceglia & Orelli 2015 Table 1, citation 101).

### 1.2 Why HWE is not RCM

RCM and HWE both close a macrocyclic alkene, but they are mechanistically and bond-accountingly distinct:

- **RCM** (ene + ene → ene + ene): both alkene carbons of the product C=C come from two terminal vinyl carbons of the substrate (`–CH=CH₂` + `H₂C=CH–`). Byproduct is ethylene. There is no heteroatom byproduct; the catalyst is a Ru carbene that turns over.
- **HWE** (P-stabilized carbanion + aldehyde): one alkene carbon comes from the phosphonate α-C (formerly sp³), the other from the aldehyde C (formerly sp² of C=O). Byproduct is dialkyl phosphate. The phosphonate group is consumed stoichiometrically — it is **not** catalytic.

So the rule's atom accounting differs in three ways from RCM:

1. **Byproduct mass.** RCM expels CH₂=CH₂ (28.05 g/mol). HWE expels dialkyl phosphate `(RO)₂PO₂⁻` (canonical dimethyl: `(MeO)₂PO₂⁻` 125.04 g/mol; diethyl `(EtO)₂PO₂⁻` 153.10 g/mol).
2. **Heteroatoms.** RCM has no heteroatoms in the byproduct. HWE deposits a P-containing byproduct of mass 95–230 g/mol.
3. **Catalysis.** RCM uses a stoichiometric carbene → catalytic Ru. HWE uses a stoichiometric phosphonate → no catalyst; the phosphonate group is installed in a prior step (commercial phosphonate ester or Arbuzov reaction).

Bond-level AE comparison (target ring of 14 atoms, single alkene closure):

| Method | Byproduct mass (g/mol) | Bond-level AE (closure step) | Reagent activator mass |
| --- | --- | --- | --- |
| RCM | 28 (CH₂=CH₂) | very high | Grubbs-II (848.97) or Hoveyda-II (626.62), catalytic |
| HWE (dimethyl phosphonate) | 125 (HP(O)(OMe)₂ anion as `(MeO)₂PO₂⁻`) + base equivalent | moderate-to-high | base (NaH 24, KHMDS 199, NaOCH₂CF₃ 122, LiCl/DBU 195, KOtBu 112) |
| Wittig | 278 (Ph₃P=O) | low | none for ylide; PPh₃ is stoichiometrically debited |

**HWE is intermediate** between RCM (lightest byproduct, but Ru-expensive) and Wittig (heaviest byproduct, but no precious metal). For most macrolide chemistry HWE wins on cost (no Ru) and on **functional-group tolerance** because the phosphonate carbanion is softer than a Wittig ylide.

### 1.3 Why HWE matters for the panel

The cytochalasin B and L-696,474 macrocyclizations in [[Haidle Myers 2004 - An Enantioselective Modular and General Route to the Cytochalasins Synthesis of L-696474 and Cytochalasin B|Haidle & Myers (2004)]] are the only entries in the Workstream A expansion-2 panel that need HWE coverage. The panel cases currently slotted to other rules are:

- `corey_erythronolide_b_macrolactonization_1978` — macrolactonization (covered by `macrolactonization.gml`)
- `trost_bryostatin_analogue_rcm_2007` — RCM (covered by `rcm.gml`)
- `phoenix_reddy_cassaine_tda_2008` — Diels–Alder (covered by `transannular_diels_alder.gml`)
- `haidle_myers_cytochalasin_b_2004` — **HWE (no rule yet)**

So Workstream C should ship the HWE rule with this brief as the design document. The rule generalizes — the same mechanism closes lactimidomycin (Larsen, Sun, Nagorny 2013), lasonolide A, herboxidiene fragments, and many other natural-product macrocycles (Kobayashi, Tanaka, Kogen 2018 review).

### 1.4 What this rule does *not* cover

- **Intermolecular HWE** (used as a fragment-coupling C=C-forming step, not for macrocyclization). Same bond-level chemistry, but no ring is closed. If macrocert ever supports non-ring-closing C=C-forming rules, this rule's GML body can be re-used; for v1 macrocert focuses on intramolecular variants.
- **Wittig macrocyclization** (Ph₃P-ylide + aldehyde). Mechanistically similar (oxaphosphetane) but byproduct is Ph₃P=O (278 g/mol). Should be a separate rule (`wittig_macrocyclization.gml`) if a panel case requires it. Schinzer's epothilone A synthesis uses an aldol macrocyclization, not Wittig, so no panel case for Wittig is currently required.
- **Julia-Kocienski olefination**. Uses sulfonyl-stabilized carbanion + aldehyde, also closes via 4-membered intermediate, but byproduct is a sulfinate. Haidle–Myers uses Julia–Kocienski for the *intermolecular* fragment coupling (between sulfone **10**/**5** and aldehyde **4**/**9**) but **not for the macrocyclization step** — the macrocyclization is HWE. Julia–Kocienski is a separate rule (`julia_kocienski.gml`) if/when needed.
- **Peterson olefination** (β-hydroxy-silane elimination). Silicon-mediated. Out of scope.
- **Tebbe / Petasis methylenation**. Ti-carbene mediated. Out of scope.
- **Aldol-then-dehydration macrocyclization**. Used in Schinzer's epothilone A. Not the same bond-level chemistry (no P byproduct).

---

## Section 2 — Atom-mapped DPO scheme

### 2.1 The bond-level chemistry

For the canonical β-keto-phosphonate variant (the [[Haidle Myers 2004 - An Enantioselective Modular and General Route to the Cytochalasins Synthesis of L-696474 and Cytochalasin B|Haidle–Myers]] L-696,474 case, dimethyl phosphonate):

$$
\underbrace{(\text{MeO})_2\text{P(O)}}_{\text{P-side}}\!-\!\underbrace{\text{CH}_2}_{\text{α-C}}\!-\!\underbrace{\text{C(O)R}'}_{\text{β-carbonyl (kept)}} \;+\; \underbrace{\text{O}\!=\!\text{CH}}_{\text{aldehyde-C}}\!-\!\text{R}''
\;\xrightarrow{\text{base}}\;
\text{R}'\text{(O)C}\!-\!\text{CH}\!=\!\text{CH}\!-\!\text{R}'' \;+\; (\text{MeO})_2\text{P(O)O}^-\;+\;\text{H}^+
$$

The α-CH₂ becomes one of the new alkene sp² carbons (losing one H to the base and the other bond to P). The aldehyde carbon becomes the other alkene sp² carbon (losing its double bond to the carbonyl O). The aldehyde O migrates to P, forming the dialkyl phosphate byproduct.

For the **macrolactone variant** (the Haidle–Myers cytochalasin B case, diethyl phosphonate ester linked through an O–C(O)–CH₂–P chain), the β-EWG is an ester carbonyl rather than a ketone. The rule body is identical except for the identity of atoms beyond the rule's 6-atom core (those atoms are off-rule, lived in the substrate's context). **One GML file covers both variants.**

### 2.2 Atom numbering (mirrors `macrolactamization.gml` / `macrolactonization.gml` / `rcm.gml`)

I keep the convention that IDs **1 and 5 are the atoms forming the new bond on the retained ring side**, and **the byproduct atoms get higher IDs**. The HWE rule needs 6 atoms in the rule body:

| ID  | Element | Role                                                                                |
| --- | ------- | ----------------------------------------------------------------------------------- |
| 1   | C       | α-C of the phosphonate (sp³ in L, sp² in R) — **retained**, becomes one alkene C    |
| 2   | H       | α-H removed by base — **expelled** (as part of protonated phosphate)                |
| 3   | P       | Phosphorus of the phosphonate — **expelled** in dialkyl phosphate byproduct         |
| 4   | O       | One of the two P=O / P–OR oxygens — used to anchor the rest of the phosphonate via context (the second P=O and the two RO–P groups live in the off-rule substrate context) |
| 5   | C       | Aldehyde carbon (sp² in L, sp² in R) — **retained**, becomes the other alkene C     |
| 6   | O       | Aldehyde oxygen — **expelled**, migrates to P to form the new P=O of phosphate     |

This gives 6 atoms in the rule body: 1, 5 (retained, become the new C=C); 2, 3, 4, 6 (involved in bond reorganization on the byproduct side).

> **Design choice — atom 4 is included in the rule body** even though it is part of the byproduct, because it carries the substrate connection to the rest of the phosphonate (the two OR groups and the second P=O). Atoms in MØD's DPO formalism declared in `context` are preserved across L→R; declaring atom 4 in context (with edges to off-rule R groups in the substrate) lets the verifier track the full byproduct mass without expanding the rule. Alternative: omit atom 4 from the rule body and rely entirely on the substrate morphism — but then the verifier cannot reconstruct the dialkyl phosphate mass at the rule level. **Recommendation: keep atom 4 explicit**, matching the way macrolactonization keeps the carbonyl O (atom 2 there) explicit.

### 2.3 Bond changes

**Broken (in L):**
- 1–2 (α-C–H of phosphonate)
- 1–3 (α-C–P bond)
- 5=6 (aldehyde C=O double bond; one bond of the double bond breaks; the residual C–O sigma still exists transiently in the oxaphosphetane but breaks in step 4)

**Preserved (in context):**
- 3=4 (the P=O of the original phosphonate; this becomes one of the two P=O of dialkyl phosphate after rearrangement)
- The other off-rule connections: 1–C(β-carbonyl) and 5–C(R'') are substrate-context bonds and inherited by the morphism. The two RO–P groups of the phosphonate are also off-rule (live as substrate decorations on atom 3, with two `O–C` edges that don't change).

**Formed (in R):**
- 1=5 (the new C=C double bond — the alkene; this *replaces* both the broken 1–3 σ-bond and the broken π-bond of 5=6, with the σ-bond between 1 and 5 newly formed and a π-bond on top)
- 3–6 (new P–O bond — the former aldehyde O migrates to P)

> **Subtle point — atom 2 (the α-H).** It is technically deprotonated by the base before the addition step, so strictly the α-H is gone before the C=C forms and the phosphate "captures" a proton from solvent or workup. In the rule body, treating atom 2 as part of the byproduct (P–OH of the eventual dialkyl phosphate) is cleanest: in R, declare 2–4 or 2 attached to the protonated phosphate. The verifier will see the mass balance: atoms 2, 3, 4, 6 + the two OR groups (off-rule context) form the dialkyl phosphate byproduct `(RO)₂P(O)OH`, which on workup is the conjugate acid of `(RO)₂PO₂⁻`. Recommendation: in R, declare 2–4 (the α-H becomes an O–H of the dialkyl phosphate); the verifier mass-checks atom count.

### 2.4 Mass balance check

For the canonical dimethyl phosphonate case (the L-696,474 substrate **11**):

- L mass: `(MeO)₂P(O)–CH₂–[β-carbonyl substrate]` + `O=CH–[tether]–` (closing ring)
- R mass: `[β-carbonyl substrate]–CH=CH–[tether]–` + `(MeO)₂P(O)–OH`
- Atoms in byproduct (atoms 2, 3, 4, 6 + 2× OMe): 1 H + 1 P + 2 O + 1 C-from-OMe...

Wait — atoms 2, 3, 4, 6 + the two OMe groups (off-rule context). Let me lay out the byproduct atom-by-atom: the dialkyl phosphate `(MeO)₂P(O)OH` is `CH₃O–P(=O)(OH)–OCH₃` = C₂H₇O₄P = 110.05 g/mol *neutral acid*. As anion `(MeO)₂PO₂⁻` = 125.04 g/mol when bound to Na⁺ (NaH(MeO)₂PO₂ = 148.02; sodium dimethyl phosphate = 148.02 g/mol). The exact byproduct mass depends on whether you book the proton:

- **Bond level (mass leaving the target ring atoms):** `(MeO)₂P(O)O⁻` + `H⁺` from the α-CH → from the rule perspective, total mass leaving target = 125.04 g/mol (the anion mass). The proton is consumed by the base on the way out.
- **Salt level (what you actually filter or wash out):** sodium dimethyl phosphate `Na(MeO)₂PO₂` = 148.02 g/mol if NaH was the base; potassium dimethyl phosphate = 164.13 if KHMDS.
- **Protonated/conjugate-acid level:** dimethyl phosphate `(MeO)₂P(O)OH` = 126.05 g/mol.

**Recommendation for `byproduct_mass_g_per_mol`: use the anion mass at the bond level (125.04 g/mol for dimethyl).** This mirrors how macrolactonization books H₂O (18.015 g/mol, the bare leaving group) rather than NaOH (which is the activator base). The activator mass is booked separately in `reagent_mass_g_per_mol`.

For other phosphonate variants:
- Diethyl `(EtO)₂PO₂⁻` = 153.10 g/mol (anion). The α-H still goes with the byproduct, so add 1 H = 154.10 for the conjugate acid.
- Diisopropyl `(iPrO)₂PO₂⁻` = 181.15 g/mol (anion).
- Still–Gennari `[CF₃CH₂O]₂PO₂⁻` = 261.04 g/mol (anion, MW of the dianion divided by 2 — actually `(CF₃CH₂O)₂P(O)O⁻` = mw 261.04).
- Ando `(PhO)₂PO₂⁻` = 249.16 g/mol (anion).

### 2.5 Proposed GML structure (canonical β-keto-phosphonate variant)

```
rule [
    ruleID "hwe_olefination (intramolecular Horner-Wadsworth-Emmons, beta-keto phosphonate + aldehyde -> alkene + dialkyl phosphate)"
    # L: phosphonate alpha-C(1) bearing H(2) and P(3); aldehyde C(5)=O(6)
    left [
        node [ id 2 label "H" ]   # alpha-H, expelled
        edge [ source 1 target 2 label "-" ]    # alpha-C-H bond, broken
        edge [ source 1 target 3 label "-" ]    # alpha-C-P bond, broken
        edge [ source 5 target 6 label "=" ]    # aldehyde C=O double bond, broken (becomes C=C and P-O after collapse)
    ]
    context [
        node [ id 1 label "C" ]   # alpha-C of phosphonate (sp3 -> sp2)
        node [ id 3 label "P" ]   # phosphorus (stays in byproduct)
        node [ id 4 label "O" ]   # P=O of phosphonate (stays in byproduct as one of the P=O of phosphate)
        node [ id 5 label "C" ]   # aldehyde C (sp2 -> sp2 alkene C)
        node [ id 6 label "O" ]   # aldehyde O (migrates to P)
        edge [ source 3 target 4 label "=" ]    # P=O of phosphonate, preserved
    ]
    # R: new C=C alkene (1=5) and new P-O of phosphate (3-6); alpha-H attaches to byproduct oxygen
    right [
        node [ id 2 label "H" ]
        edge [ source 1 target 5 label "=" ]    # new C=C alkene
        edge [ source 3 target 6 label "-" ]    # new P-O bond (former aldehyde O migrates to P)
        edge [ source 2 target 6 label "-" ]    # alpha-H ends up on phosphate O (the OH of (RO)2P(O)OH on workup)
    ]
]
```

**Verifier sanity checks the rule should pass:**

- **Mass balance.** L atoms: 1 (C), 2 (H), 3 (P), 4 (O), 5 (C), 6 (O). R atoms: same six. ✓ (atom count conserved). The two OR groups attached to atom 3 in the substrate context are preserved across L → R as off-rule decorations. ✓
- **BFS from `retained_root_atom: 1` through R-side edges** reaches atoms 1, 5 (the C=C of the new alkene). It does **not** reach atoms 2, 3, 4, 6 via the C=C path (those are connected only through the broken 1–3 bond on the L side, which no longer exists in R). The byproduct atoms (2, 3, 4, 6 + off-rule OR groups) form a disconnected component in R, correctly classified as byproduct.
- **Byproduct mass for dimethyl variant.** M(H) + M(P) + 2·M(O) + 2·M(OMe substrate context) = 1.008 + 30.974 + 2·15.999 + 2·31.034 = 126.05 g/mol (conjugate acid dimethyl phosphate). Match `byproduct_mass_g_per_mol`. ✓
- **The C=C forms between atoms that were retained on the ring**, not between byproduct atoms. ✓

**Variants** (per-phosphonate; lives in `reagent_mass_alternatives`, not separate GML files):
- For diethyl: substrate context has two `OEt` groups on atom 3 instead of two `OMe`. Verifier mass recompute: 1 + 30.974 + 32 + 2·45.06 = 154.10 g/mol (conjugate acid diethyl phosphate).
- For Still–Gennari `(CF₃CH₂O)₂`: 1 + 30.974 + 32 + 2·99.04 = 262.05 g/mol (conjugate acid).
- For Ando `(PhO)₂`: 1 + 30.974 + 32 + 2·93.10 = 250.17 g/mol (conjugate acid).

**Difference from `macrolactonization.gml`**: macrolactonization has 6 atoms (acid C, two carbonyl Os, acid OH proton, alcohol O, alcohol H) and expels H₂O; HWE has 6 atoms (phosphonate α-C, α-H, P, one P=O, aldehyde C, aldehyde O) and expels dialkyl phosphate. Both rules form a single new bond on the ring (C–O for lactone; C=C for HWE) while reorganizing several side-bonds. The HWE rule additionally needs to track the P, which has no analog in lactonization.

**Difference from `rcm.gml`**: RCM has 4 atoms (the two alkene Cs that survive + ethylene's two Cs that depart). HWE has 6. RCM byproduct is C₂H₄ (28); HWE byproduct is `(RO)₂P(O)OH` (~126 for dimethyl). RCM has a catalyst; HWE does not.

---

## Section 3 — Reagent + byproduct mass for each phosphonate variant

Mass per ring closure. The "activator" is the *base* + *solvent* (no transition-metal catalyst, no Lewis-acid additive in the canonical case; LiCl or NaI is added in the Masamune–Roush / Ando-macro variants). The "phosphonate mass" is the off-rule substrate group `(RO)₂P(O)–CH₂–C(O)R'` that is installed on the substrate in a prior step but is **debited to this rule** as part of the process AE.

| Variant | Phosphonate group | Base (typical) | Solvent | reagent_mass_g_per_mol | byproduct (anion) mass | E:Z default | Reference DOI |
|---|---|---|---|---|---|---|---|
| **Dimethyl HWE — CANONICAL** | `(MeO)₂P(O)CH₂COR'` | NaH (24.00), KHMDS (199.45), or NaOCH₂CF₃ (122.04) | THF, DME, or CH₂Cl₂ | **~150** (base + counterion) | **125.04** ((MeO)₂PO₂⁻) | ≥10:1 to 50:1 E | `10.1021/ja01468a042` (Wadsworth–Emmons 1961) |
| **Diethyl HWE** | `(EtO)₂P(O)CH₂COR'` | NaH, KHMDS, NaOCH₂CF₃ | THF, DME | **~150** | **153.10** ((EtO)₂PO₂⁻) | ≥10:1 to 50:1 E | `10.1021/cr60287a005` (Boutagy–Thomas 1974) |
| **Masamune–Roush** | `(EtO)₂P(O)CH₂CO₂R'` (or dimethyl) | LiCl (42.39) + iPr₂NEt (Hünig, 129.24) or DBU (152.24) | MeCN, THF | **~322** | **125–153** | ≥10:1 E | `10.1016/S0040-4039(01)80205-7` (Masamune–Roush 1984) |
| **Still–Gennari (Z-SELECTIVE)** | `(CF₃CH₂O)₂P(O)CH₂CO₂R'` | KHMDS (199.45) + 18-crown-6 (264.32) | THF | **~464** | **261.04** ((CF₃CH₂O)₂PO₂⁻) | **1:20 to 1:50 Z** | `10.1016/S0040-4039(00)85909-2` (Still–Gennari 1983) |
| **Ando (Z-SELECTIVE)** | `(PhO)₂P(O)CH₂CO₂R'` | NaH or KHMDS + NaI (149.89) | THF or DME | **~349** | **249.16** ((PhO)₂PO₂⁻) | **1:10 to 1:50 Z** | `10.1021/jo970057c` (Ando 1997); `10.1016/0040-4039(95)00726-S` (Ando 1995) |
| **Ando-macrocyclic Z (NaI/DBU)** | `(o-Tol-O)₂P(O)CH₂CO₂R'` (or ArOPh variants) | NaI (149.89) + DBU (152.24) | THF | **~302** | **~290** (variant Ar₂PO₂⁻) | **1:6 to 1:20 Z**, 13–18 membered rings | `10.1021/ol100071d` (Ando, Narumiya, Takada, Teruya 2010); `10.1016/j.tetlet.2011.01.043` (Ando, Sato 2011) |
| **Haidle–Myers (NaOCH₂CF₃/CF₃CH₂OH)** | `(MeO)₂` or `(EtO)₂` β-keto-phosphonate or phosphonoacetate | NaOCH₂CF₃ (122.04) | CF₃CH₂OH (100) / DME | **~222** (base + solvent stabilization) | **125–153** | **E** (consistent with default; cyt B and L-696,474 both *trans*) | `10.1073/pnas.0402111101` (Haidle–Myers 2004) |
| **Nagorny–lactimidomycin (Zn-mediated)** | `(MeO)₂P(O)CH₂COR'` | Zn(OTf)₂ (363.50) + iPr₂NEt (129.24) | toluene/THF | **~493** | **125** | E (≥20:1) | `10.1021/ol401186f` (Larsen, Sun, Nagorny 2013) |

**Notes on the reagent mass column:**

- **Canonical dimethyl/diethyl HWE.** The "~150 g/mol" reagent mass is just the base equivalent (NaH 24 or KHMDS 199, averaged). The phosphonate group itself (`(RO)₂P(O)CH₂–`) is part of the substrate and is debited as substrate mass elsewhere in the macrocert AE calculation. For consistency with macrolactonization (which books the base/coupling agent in `reagent_mass_g_per_mol`), use the base + minor additives mass.
- **Masamune–Roush.** LiCl + Hünig's base / DBU. Adds ~322 g/mol because two co-additives are needed. The advantage is **mild base, tolerates base-sensitive (α-stereogenic) aldehydes**; this is the workhorse for natural-product macrocyclization. *Citations: 855* on the Masamune–Roush 1984 paper.
- **Still–Gennari Z-selective.** The CF₃CH₂O groups on P make the phosphonate carbanion harder; the syn-oxaphosphetane forms reversibly but the anti-oxaphosphetane's collapse becomes rate-limiting and slow, so the syn pathway "wins" → Z-alkene. Requires K⁺ + 18-crown-6 in THF for optimal selectivity. **The phosphonate must be pre-synthesized** (`(CF₃CH₂O)₂P(O)CH₂CO₂Et` is commercial, *Org. Synth.* 73:152, `10.15227/orgsyn.073.0152`).
- **Ando Z-selective.** Diphenyl phosphonates with NaH/NaI or KHMDS. Cheaper than Still–Gennari (no fluorinated alcohol needed). **Ando's macrocyclic variants** (2010 *Org. Lett.* 12:1460; 2011 *Tetrahedron Lett.* 52:1284) explicitly demonstrate Z-selective HWE on 13–18 membered ring closures with NaI/DBU as the base system — directly relevant if a panel case ever needs a *Z*-macrocyclic alkene from HWE.
- **Haidle–Myers conditions (NaOCH₂CF₃ in CF₃CH₂OH/DME).** Discovered in the cytochalasin paper *as a means to minimize α-epimerization of the aldehyde* (the substrate has labile sp³ stereocenters adjacent to the aldehyde C). This is a **Masamune–Roush-like mild non-amine condition** using trifluoroethoxide as the base. Critical for the cytochalasin B 14-membered macrolactone (65% yield) and the L-696,474 11-membered macrocarbocycle (52% yield, 5:1 dr).
- **Nagorny Zn(II)-mediated.** Adds Zn(OTf)₂ as a Lewis acid; the Zn chelates the phosphonate β-carbonyl O and the aldehyde O, organizing the transition state, *and* the LA-organized addition step proceeds without strong amine base. Demonstrated for lactimidomycin's strained macrolide; useful for very base-sensitive substrates.

**Process-AE intuition.** The bond-level rule sees only ~125 g of dimethyl phosphate (the canonical case). The base + solvent + workup add ~150 g for plain NaH; ~322 g for Masamune–Roush; ~464 g for Still–Gennari; ~493 g for Nagorny Zn. Process-AE is dominated by the phosphonate ester (which is substrate-borne and debited elsewhere) and the base/additive choice. The bond-vs-process gap is moderate (1.2× to 4×) — much smaller than for macroetherification (25×–85×) because HWE doesn't need a transition-metal catalyst. This makes HWE a relatively *high-AE* macrocyclization at the process level despite the heavy P-byproduct at the bond level.

---

## Section 4 — Stereochemical handling

### 4.1 E vs Z selectivity — the default and its modifications

**Default (dimethyl/diethyl phosphonate, standard base):** **E-selective**, typically 10:1 to >50:1 E:Z for stabilized phosphonates (α-EWG = ester, ketone, or amide) on aliphatic aldehydes. The selectivity comes from the **reversibility of the addition step** and the **irreversibility of oxaphosphetane collapse**: the anti-oxaphosphetane is thermodynamically more stable (large groups antiperiplanar), addition equilibrates, and the system funnels through the anti pathway to deliver the E-alkene. See Bisceglia & Orelli (2015) for the canonical mechanistic statement.

For non-stabilized phosphonates (the α-EWG is missing), the addition step becomes irreversible and the system stops at the β-hydroxy-phosphonate — **no olefination occurs**. This is the Boutagy–Thomas requirement.

**Z-selective modifications:**

- **Still–Gennari (1983).** `(CF₃CH₂O)₂P(O)CH₂CO₂R'` + KHMDS + 18-crown-6 + THF at −78 °C. Z:E up to 50:1 for primary aliphatic aldehydes. Mechanism: the CF₃CH₂O groups make the oxaphosphetane collapse rate-limiting; the syn-oxaphosphetane (smaller barrier under these conditions) collapses faster and dominates. [[Still Gennari 1983 - Direct Synthesis of Z-Unsaturated Esters Useful Modification Horner Emmons|Still & Gennari (1983)]], 976 citations.
- **Ando (1995, 1997).** `(PhO)₂P(O)CH₂CO₂Et` + KHMDS or NaH + NaI + THF. Z:E up to 30:1. Cheaper, less moisture-sensitive than Still–Gennari. [[Ando 1995 - Practical Synthesis Z-Unsaturated Esters Ethyl Diphenylphosphonoacetate|Ando (1995)]] 180 citations; [[Ando 1997 - Highly Selective Z-Unsaturated Esters Diarylphosphono Acetates|Ando (1997)]] 295 citations.
- **Ando macrocyclic (2010, 2011).** Diphenyl or diaryl phosphonoacetates + NaI/DBU. **Demonstrated for 13–18 membered macrocyclic alkenes.** This is the closest literature precedent to macrocert's intramolecular Z-HWE case.

**The rule's GML body does not encode E/Z.** Geometry is determined by the activator + phosphonate combination, which is selected at the RunSpec / activator level (i.e., `reagent_mass_alternatives` in `meta.yaml`). The verifier's `enforce_ez_geometry` predicate from Workstream D's `workstream_d_predicates.md` is the right mechanism to lock the geometry per substrate.

### 4.2 Preservation of α-stereocenters on the aldehyde

The aldehyde carbon (atom 5) of the substrate is sp² and **achiral** at that position. But the α-carbon of the aldehyde (off-rule, lives in the substrate context one bond away from atom 5) can carry a stereogenic sp³ center. This α-stereocenter is base-labile: under strong base + the carbanion conditions of HWE, it can epimerize via enolization. The Haidle–Myers paper is explicit about this:

> "It was recognized at the outset that both ring closures (see Fig. 2, structures 3 and 11) were potentially complicated beyond the issues that typically confront medium and large ring-closure reactions by the fact that the aldehydic components of each substrate were epimerizable, a concern that in one case did prove to be valid but ultimately did not present an insolvable problem." — Haidle & Myers (2004) PMC PMC514432

The cytochalasin B case (substrate **3** → **40**) gave the desired E-macrolactone in 65% yield with the α-stereocenter preserved under NaOCH₂CF₃/CF₃CH₂OH/DME at 23 °C. The L-696,474 case (substrate **11** → **36**) gave a 5:1 mixture of C-18 diastereomers (43% yield of the diastereomerically pure desired isomer after HPLC) under the same conditions at 80 °C — i.e., partial epimerization occurred at the higher temperature.

**Stereo flags for the rule:**
- `forms_new_alkene_geometry` (E or Z, set by activator)
- `preserves_alpha_stereocenter` (under mild base conditions; Masamune–Roush and NaOCH₂CF₃ are designed for this; strong base / high temp may epimerize)
- `risk_alpha_epimerization` (boolean; true under default NaH/KHMDS conditions if substrate has α-sp³ stereocenter next to the aldehyde)

### 4.3 Preservation of stereo at all other ring atoms

For the canonical HWE: the α-C of the phosphonate (atom 1) is sp³ → sp² (becomes alkene), so it cannot retain stereo (it's becoming planar). The aldehyde C (atom 5) is sp² → sp² (stays planar). All other ring atoms are off-rule and not touched by the mechanism. So the rule:

- **Destroys** stereo information at atom 1 (no flag needed — sp² product is achiral at that position).
- **Preserves** stereo at all sp³ stereocenters not adjacent to atoms 1, 2 in the substrate. (Adjacent stereocenters need the `preserves_alpha_stereocenter` flag from §4.2.)

### 4.4 Stereo flags to declare in `meta.yaml`

```yaml
stereo_flags:
  - forms_new_alkene_geometry        # E by default; Z with Still-Gennari or Ando phosphonate
  - alpha_C_becomes_sp2              # atom 1 loses any pre-existing chirality
  - preserves_other_sp3_stereo       # all other ring atoms untouched
  - risk_alpha_epimerization         # if substrate has alpha-sp3 stereocenter, use Masamune-Roush or Haidle-Myers conditions
```

---

## Section 5 — Haidle–Myers cytochalasin B deep dive

The canonical literature reference for this rule. From the PMC PMC514432 full text (Haidle & Myers 2004, *PNAS* 101:12048–12053, DOI `10.1073/pnas.0402111101`), I extract the atom-by-atom mechanism for both ring closures.

### 5.1 The two macrocyclization variants

The Haidle–Myers paper demonstrates a single late-stage macrocyclization strategy applied to two cytochalasin substrates of different sizes:

- **Cytochalasin B (target 1): 14-membered macrolactone.** Substrate **3** (Scheme 7) bears a *diethyl phosphonoacetate* ester `(EtO)₂P(O)–CH₂–C(O)–O–CR(R')H` attached via the ester O to a tertiary alcohol on the bicyclic isoindolone core, and an aldehyde at the other end of a long aliphatic tether. The β-EWG of the phosphonate is the ester carbonyl, *and* the resulting C=C forms a C13–C14 *trans*-alkene that is part of the macrolactone ring. Yield: 65% under NaOCH₂CF₃/CF₃CH₂OH/DME at 23 °C.
- **L-696,474 (target 2): 11-membered macrocarbocycle.** Substrate **11** (Scheme 6) bears a *dimethyl methyl-phosphonate ketone* `(MeO)₂P(O)–CH₂–C(O)–R` (i.e., a β-keto-phosphonate; installed by addition of `(MeO)₂P(O)CH₂Li` to a methyl ester) and an aldehyde at the other end. The β-EWG is a ketone (the C=O of the ring); the product macrocyclization yields an enone closing the 11-ring. Yield: 52% (5:1 dr at C-18) under NaOCH₂CF₃/CF₃CH₂OH/DME at 80 °C.

Both go through the same intramolecular HWE mechanism. The macrolactone variant has the phosphonate tied to a *para*-attached ester (so the C=C closes the ring through an ester chain); the macrocarbocycle variant has the phosphonate tied to a *para*-attached ketone (so the C=C closes the ring through a C–C bond chain). The rule body is identical for both; the off-rule substrate context differs in whether atom 1's neighbor is a `C(=O)–O–` ester or a `C(=O)–C` ketone.

### 5.2 The atom-by-atom mechanism (from the paper)

**For substrate 3 → macrolactone 40 (cytochalasin B route):**

1. Substrate **3** has two reactive sites: an aldehyde at the C-13 end of a long aliphatic tether, and a `(EtO)₂P(O)–CH₂–CO₂–` ester on the bicyclic isoindolone's tertiary alcohol at the other end (formed in step e of Scheme 7, "diethylphosphonoacetic acid, DCC, CH₂Cl₂, 23°C, 81%"). The aldehyde was installed by HF·pyridine cleavage of a TBS ether followed by Dess–Martin oxidation.
2. **Treat with NaOCH₂CF₃ (sodium 2,2,2-trifluoroethoxide) in CF₃CH₂OH/DME at 23 °C.** The base deprotonates the α-CH₂ of the phosphonoacetate (the most acidic site, pKa ≈ 13 owing to both the P=O and the ester carbonyl).
3. The resulting carbanion attacks the *intramolecular* aldehyde C (closure of the 14-ring). The β-alkoxide forms; closes to oxaphosphetane; collapses to E-alkene + diethyl phosphate anion (`(EtO)₂PO₂⁻`).
4. Product: macrolactone **40** with a *trans*-C13–C14 alkene (the C=C of cytochalasin B's 14-membered macrolactone ring). Yield 65%.

**For substrate 11 → macrocarbocycle 36 (L-696,474 route):**

1. Substrate **11** has an aldehyde at the C-15 end and a `(MeO)₂P(O)–CH₂–C(=O)–C` β-keto phosphonate at the C-18 end (installed by adding `(MeO)₂POCH₂Li` to a methyl ester, then deprotecting and oxidizing).
2. **Treat with NaOCH₂CF₃ in CF₃CH₂OH/DME at 80 °C.** Higher temperature is needed for 11-ring closure (greater ring strain → larger barrier).
3. α-Deprotonation, intramolecular addition to the aldehyde, oxaphosphetane closure and collapse, expelling `(MeO)₂PO₂⁻` and forming the C=C as an enone (because the β-EWG is a ketone, not an ester).
4. Product: 11-membered macrocyclic ketone **36** with C13=C14 *trans*-alkene, 5:1 dr at C-18 (the α-sp³ stereocenter adjacent to the new alkene is partly epimerized at 80 °C). 43% yield diastereomerically pure after HPLC separation, or 52% as the 5:1 mixture.

### 5.3 The chosen base/solvent system

Haidle & Myers explicitly call out the development of NaOCH₂CF₃/CF₃CH₂OH/DME as the optimal conditions for epimerization-suppressed macrocyclization:

> "We discovered conditions for macrocyclization that greatly reduced epimerization. These conditions entailed the use of sodium 2,2,2-trifluoroethoxide as base in hot dimethoxyethane (80°C) containing 2,2,2-trifluroroethanol and led to macrocyclization of **11** to form **36** and its C-18 epimer in a ratio of 5:1 (52% yield)." — Haidle & Myers 2004

The trifluoroethoxide is **a mild, non-amine, oxygen-centered base** that minimizes α-deprotonation of the aldehyde (the side reaction that causes epimerization). The CF₃CH₂OH co-solvent stabilizes the carbanion as a tight ion pair. This is conceptually a **Masamune–Roush descendant** (the Masamune 1984 paper used LiCl + iPr₂NEt or DBU for the same purpose — minimizing base-induced epimerization), but with a fluorinated alkoxide replacing the amine base. For macrocert, this discovery is **a fourth canonical activator** alongside Masamune–Roush, Still–Gennari, and Ando.

### 5.4 What this tells us about the rule

- **The β-EWG can be a ketone or an ester.** Same rule, different substrate context. The β-EWG identity is off-rule.
- **The phosphonate can be dimethyl or diethyl.** Same rule, different substrate context on the OR groups. Byproduct mass differs (125 vs 153 g/mol).
- **Ring size 11 is at the edge of feasibility.** The 11-ring required higher temperature (80 °C vs 23 °C for the 14-ring) and gave lower yield (52% vs 65%) plus partial epimerization. Macrocyclizations below 11 ring atoms are likely infeasible; 11–14 is the medium-ring difficulty range; ≥14 is "large ring", easier.
- **The α-stereocenter adjacent to the aldehyde matters.** The L-696,474 case has C-18 (the α of the aldehyde C-17) as an sp³ stereocenter; it partially epimerizes under base. The rule's forbidden-context predicate should flag this risk.
- **NaOCH₂CF₃/CF₃CH₂OH/DME is the Haidle–Myers signature condition.** It belongs in `reagent_mass_alternatives` as `haidle_myers` activator.

### 5.5 Direct analogy to other cytochalasan syntheses

Haidle–Myers is the *only* HWE macrocyclization of a cytochalasin in the literature; Thomas's earlier syntheses (cytochalasin D, H) used IMDA-type intramolecular Diels–Alder. So the panel case is a singleton for the cytochalasin family but generalizes to lactimidomycin, lasonolide, and other natural-product targets where the macrocyclic alkene is the disconnection (see §6).

---

## Section 6 — Other family members the rule would cover

HWE macrocyclization has been used for many natural-product macrocycles. The following list cites the **most-cited** examples that would be valid future panel cases:

1. **Lactimidomycin (Larsen, Sun, Nagorny 2013).** Zn(II)-mediated intramolecular HWE for a strained 12-membered macrolide. Demonstrates the **Nagorny Zn-HWE activator** as the canonical example for very strained / base-sensitive macrolides. DOI `10.1021/ol401186f`, *Org. Lett.* 15:2998. [[Larsen Sun Nagorny 2013 - Lactimidomycin Zn(II) Mediated HWE Macrocyclization|Larsen, Sun, Nagorny (2013)]] — 26 CrossRef citations.

2. **Cytochalasin B / L-696,474 (Haidle, Myers 2004).** Already discussed in §5.

3. **Modern Z-selective HWE macrocyclization (Ando, Sato 2011).** Demonstrates 13–18 membered Z-cyclic alkenes from diaryl phosphonates with NaI/DBU. Not a natural product target, but the canonical methodology demonstration for **Z-HWE macrocyclization** as a panel test case if needed. DOI `10.1016/j.tetlet.2011.01.043`. [[Ando Sato 2011 - Z-Selective Intramolecular HWE for Macrocyclic Alkenes|Ando & Sato (2011)]] — 17 CrossRef citations.

4. **Ando 2010 macrolactones.** Intramolecular HWE on Ando phosphonates with NaI/DBU for 12–14 membered macrolactones. DOI `10.1021/ol100071d`, *Org. Lett.* 12:1460. [[Ando Narumiya Takada Teruya 2010 - Z-Selective Intramolecular HWE Macrocyclic Lactones|Ando, Narumiya, Takada, Teruya (2010)]] — 41 CrossRef citations.

5. **Kobayashi, Tanaka, Kogen 2018 review.** *Tetrahedron Lett.* 59:568, DOI `10.1016/j.tetlet.2017.12.076`, 54 citations. Surveys recent (2010–2017) HWE applications in natural-product synthesis, including several intramolecular macrocyclizations. Worth scanning for panel-case candidates beyond the Haidle–Myers and Ando cases.

6. **Bisceglia & Orelli 2015 review.** *Curr. Org. Chem.* 19:744, DOI `10.2174/1385272819666150311231006`, 101 citations. Comprehensive HWE review covering mechanism, stereoselectivity, modifications, and natural-product applications.

### NOT covered (corrections from the task brief):

- **Epothilone B is NOT closed by HWE.** Nicolaou's epothilone A and B total syntheses (DOI `10.1002/anie.199705251` for *Angew. Chem.* 36:525, and `10.1002/chem.19970031212` for *Chem. Eur. J.* 3:1971) use **Yamaguchi macrolactonization** + intermolecular Wittig (not intramolecular HWE) for the macrocyclic ring. Schinzer's epothilone A (DOI `10.1002/anie.199705231` for *Angew. Chem.* 36:523) uses an **aldol macrocyclization** (not HWE). Some later epothilone analogs may use HWE in fragment couplings, but **the canonical Nicolaou and Schinzer epothilone macrocyclizations are not HWE.** The task brief is wrong to list epothilone as an HWE-family panel candidate.
- **Bryostatin is NOT closed by HWE.** Wender's bryostatin syntheses use macrolactonization or RCM; no HWE macrocyclization of a *natural* bryostatin has been reported (per the prior agent's research_macrocert_panel_expansion_2.md memory). The task brief's mention of "some Wender routes" using HWE is unsupported.
- **Erythromycin macrocyclizations are NOT HWE.** Corey 1978 used macrolactonization (already a separate macrocert rule); Woodward 1981 used Wittig (closely related but separate). HWE is not a documented erythromycin macrocyclization tactic.

So the family the HWE rule covers is **lactimidomycin, cytochalasin B and L-696,474, and the Ando macrocyclic series** — not epothilone, not bryostatin, not erythromycin.

---

## Section 7 — Forbidden contexts for Workstream D

The rule fires only when the substrate is compatible. Workstream D's strategy/feasibility predicates should block firings in these cases:

1. **Substrate has multiple aldehydes.** HWE is chemoselective for *one* aldehyde at a time; if the substrate has two aldehydes, the rule needs disambiguation. The strategy predicate should flag substrates with `count(aldehyde_C) > 1` and require a `target_aldehyde` hint or refuse to fire. Predicate: `substrate_must_have_exactly_one_aldehyde`.

2. **Substrate's aldehyde is enolizable AND has α-sp³ stereocenter.** Under base (especially strong base like KHMDS), the aldehyde's α-C–H can be deprotonated, leading to (a) enolization side reactions (aldol-like attack by aldehyde-enolate on the other aldehyde — but only if there's another aldehyde) or (b) **epimerization of the α-stereocenter**, leading to loss of stereochemical integrity. This is the Haidle–Myers concern. Predicate: `if_aldehyde_alpha_C_is_sp3_stereocenter_then_use_haidle_myers_or_masamune_roush_activator`. Macrocert's expected_witness should set `risk: alpha_epimerization` and prefer NaOCH₂CF₃ or LiCl/DBU activator.

3. **Substrate's phosphonate α-C is tertiary.** If `(RO)₂P(O)–CR'R''–C(O)R'''` (α-C is bearing two substituents already), the α-H is single and the resulting carbanion is sterically hindered. The addition step slows dramatically, and the macrocyclization may fail. Predicate: `phosphonate_alpha_C_must_be_secondary_or_primary`.

4. **Substrate's phosphonate lacks an α-EWG.** Without a β-EWG (ester, ketone, amide, sulfone, or other π-acceptor) directly on the α-C, the carbanion is not stabilized, no oxaphosphetane forms, and **no olefination occurs** — the reaction stops at the β-hydroxy-phosphonate. This is the Boutagy–Thomas requirement. Predicate: `phosphonate_alpha_C_must_have_beta_EWG`.

5. **Substrate has a competing α-acidic site.** If the substrate has another α-acidic C–H (e.g., a 1,3-dicarbonyl elsewhere on the chain, or a methylene next to a sulfone), the base may deprotonate the wrong site, leading to a wrong-regiochemistry reaction. Predicate: `no_other_alpha_acidic_sites_below_pKa_threshold_15`.

6. **Ring size < 11.** Below 11 atoms, macrocyclic HWE becomes very strained (Haidle–Myers's 11-ring required 80 °C and gave 52% yield; below 11, no literature precedent). Predicate: `ring_size >= 11`.

7. **Ring size > 25.** Above 25 atoms, the entropic cost of intramolecular collisions makes the closure slower than intermolecular HWE; dimer or oligomer formation becomes a serious side reaction. Predicate: `ring_size <= 25`.

8. **Phosphonate is a phosphonamide or phosphine oxide (not a phosphonate).** Phosphonamides `(R₂N)₂P(O)CR₂'-` give the Horner variant; phosphine oxides `R₃P(O)CR₂'-` give the Horner–Wittig variant. Both have similar mechanisms but different byproducts (R₂N–H + phosphate-like, or R₃P=O respectively). **Out of scope for this rule** — handle as separate rules `horner_olefination.gml` and `horner_wittig_olefination.gml` if/when needed.

9. **The β-EWG is the same as the macrocycle's intended ring carbonyl.** Subtle: if the phosphonate's β-EWG is `–C(=O)–O–` (an ester, as in the Haidle–Myers cytochalasin B case), the C=O of the ester is preserved across the rule and ends up *in the product ring* as the macrolactone's C=O. This is fine. But if the β-EWG were the *ring-closing functional group itself*, the rule body's atom map would need adjustment. **Recommendation: treat the β-EWG as off-rule context** — it lives in the substrate decoration of atom 1, and its identity (ester C=O vs ketone C=O vs amide C=O) is not part of the rule. The rule fires regardless.

10. **Workstream D's `enforce_ez_geometry`** predicate should set the alkene geometry per substrate. For E-selective (canonical), no flag needed. For Z-selective (Still–Gennari or Ando activator), set `target_alkene_Z`.

These predicates belong in `macrocert.generate.strategies` (the strategy file), not in the rule body.

---

## Section 8 — Toy substrate proposal

**Recommendation:** Add a new panel case, `hwe_13_from_omega_aldehyde_beta_keto_phosphonate`, parallel to the existing `lactam_16` / `lactone_16` / `rcm_13` panels. This is a small linear keto-aldehyde tether that closes to a 13-membered ring via canonical β-keto-phosphonate HWE.

### 8.1 The surrogate

The simplest viable surrogate is an ω-aldehyde tethered to a β-keto-phosphonate through a long methylene chain. Structure (target ring is 13-membered):

```
                 O    O
                 ||   ||
   (MeO)2P-CH2-C-CH2-(CH2)8-CH2-CHO
              α
                 |____________|
                  closes to 13-ring
                  (alkene + ring-C(O))
```

Specifically: **11-oxo-13-((dimethoxyphosphoryl)methyl)tridecanal** with explicit linear structure:

`(MeO)₂P(O)–CH₂–C(=O)–(CH₂)₉–CHO`

— a 13-atom linear chain (counting: P-α-C(C1), β-C(C2) ketone, then 9 × CH₂ (C3–C11), then CHO (C12) → wait, that's only 12 atoms in the ring. Let me re-count.

Substrate explicit: P–C1H₂–C2(=O)–C3H₂–C4H₂–C5H₂–C6H₂–C7H₂–C8H₂–C9H₂–C10H₂–C11H₂–C12H₂–C13HO. After HWE: C1=C13 alkene closes the ring containing C1–C2(=O)–C3–...–C12–C13–C1 (going around): that's 13 atoms in the ring (C1, C2, C3, ..., C13 — 13 ring atoms). Yes — a 13-membered ring ketone-alkene.

The product is **(E)-cyclotrideca-2-en-1-one**:

```
ring of 13 atoms:
   C2(=O) — C1=C13 — C12 — C11 — C10 — C9 — C8 — C7 — C6 — C5 — C4 — C3 — C2
                                                                         |________|
```

(C2 is the carbonyl carbon, C1 is now the α-sp² C bonded to it, C1=C13 is the new alkene, C13 was the aldehyde C, and C3–C12 are the aliphatic tether.)

Molecular formula of the product: C₁₃H₂₂O (194.32 g/mol). The byproduct is dimethyl phosphate `(MeO)₂P(O)OH` (126.05 g/mol).

Why this design:
- **Ring size 13** mirrors L-696,474 (11-ring would also be a valid choice but is harder).
- **No additional functional groups** — just the phosphonate, ketone, and aldehyde. This isolates the rule firing from competing nucleophiles or stereocenters.
- **No α-sp³ stereocenter on the aldehyde** — the C12 is a methylene, so no epimerization risk; tests the canonical (NaH or NaOCH₂CF₃) activator. If a future panel case needs to test α-epimerization, the substrate can be modified to put a methyl on C12.
- **Dimethyl phosphonate** is the lightest/cheapest activator — most common in textbook HWE.

### 8.2 Stereochemistry expected

Product is **E-cyclotridecenone** (E:Z ≥ 10:1 expected under any standard HWE conditions on dimethyl phosphonate). The rule should set `enforce_ez_geometry: E` in the runspec.

### 8.3 Reagent stack proposed

- Base: NaH (24.0 g/mol) or NaOCH₂CF₃ (122.0 g/mol).
- Solvent: THF or DME.
- Temperature: 23 °C.
- Estimated yield: 60–75% for a 13-ring with this geometry (consistent with the Ando 2010 *Org. Lett.* macrolactone 13-ring closures at 50–80% yield).

### 8.4 Panel files needed

```
data/validation_panel/hwe_13_from_omega_aldehyde_beta_keto_phosphonate/
  structure.mol      # 13-membered cycloalkenone product (E-cyclotridec-2-en-1-one)
  runspec.yaml       # mirrors lactam_16 RunSpec, with rules: all_macrocyclization
  expected.yaml      # literature_tactic: hwe_olefination, ring_size: 13
  notes.md           # cites Wadsworth-Emmons 1961, Boutagy-Thomas 1974, Haidle-Myers 2004
```

### 8.5 Suggested `expected.yaml`

```yaml
literature_tactic: hwe_olefination
literature_ring_size: 13
expected_witness: optimal
expected_top_rule_class: macrocyclization
ae_class: high
reference: |
  Surrogate HWE macrocyclization case (13-membered cycloalkenone,
  intramolecular HWE closure of an omega-aldehyde tethered beta-keto
  phosphonate). Designed to mirror Haidle-Myers 2004 (DOI
  10.1073/pnas.0402111101) L-696,474 11-ring closure and Ando 2010
  (DOI 10.1021/ol100071d) macrolactone series. Activator: NaH or
  NaOCH2CF3, THF or DME, 23 C. Bond-level byproduct: dimethyl phosphate
  anion (125.04 g/mol). Expected geometry: E (default HWE).
```

### 8.6 Update `data/rules/_index.yaml`

The `all_macrocyclization` set should include `hwe_olefination`:

```yaml
sets:
  all_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification
    - rcm
    - transannular_diels_alder
    - hwe_olefination          # new

  high_ae_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification
    - rcm
    - transannular_diels_alder
    - hwe_olefination          # new, byproduct ~125 g/mol (dimethyl phosphate) — moderate AE

  alkene_forming_macrocyclization:    # new set, suggested
    - rcm
    - hwe_olefination          # both form a macrocyclic C=C, but with different mechanisms
```

---

## Section 9 — Proposed `meta.yaml` (full draft, ready to encode)

```yaml
# HWE olefination rule metadata (consumed by macrocert.spec.rules).
# See data/rules/hwe_olefination.gml for the DPO span. Application
# conditions (ring closure on a single component, ring-size membership
# in the macrocyclic range, phosphonate must have beta-EWG on alpha-C,
# substrate must have exactly one aldehyde, no other alpha-acidic sites,
# etc.) live in macrocert.generate.strategies, not here.

# Process-level reagent mass: base + co-solvent + activator per firing.
# Canonical activator: NaH in THF or DME (the textbook conditions; mass
# ~24 g/mol for the base + ~72 g/mol average for the co-solvent
# accounted at 1 equiv = ~96 g/mol total, but base is debited at 1 equiv
# which is ~24 g/mol). Per-substrate overrides in RunSpec.solver.extra
# can select alternatives from `reagent_mass_alternatives` below.
reagent_mass_g_per_mol: 24.0

# Bond-level expelled mass: dialkyl phosphate anion, from the rule's
# atom-map. For the canonical dimethyl phosphonate variant, the byproduct
# is (MeO)2PO2- = 125.04 g/mol (anion); the conjugate acid is 126.05
# g/mol (with the alpha-H added). The rule's GML uses the conjugate-acid
# form (alpha-H added to phosphate O on R-side), giving a 126.05 g/mol
# byproduct. Verifier recomputes this in M2 from the composed rule.
byproduct_mass_g_per_mol: 126.05

# Which atom ID in the rule body anchors the *retained* product side on R.
# Used by the verifier's bond-level AE recomputation: BFS from this atom
# through R's edges; everything reachable is target, the rest is byproduct.
# Atom 1 = the alpha-C (now sp2 alkene C on the ring). Atom 5 (aldehyde C,
# now the other sp2 alkene C) is reached via the new 1=5 bond.
retained_root_atom: 1

classes:
  - macrocyclization
  - alkene_forming
  - high_atom_economy_bond    # dimethyl phosphate (~125 g/mol) at bond level
  - cytochalasan_family       # Haidle-Myers cytochalasin B, L-696,474
  - macrolide_family          # lactimidomycin (Nagorny 2013), Ando 2010 series

# Activator alternatives. Each entry overrides reagent_mass_g_per_mol
# at the RunSpec layer. byproduct_mass_extra is the *additional* mass
# beyond the bond-level 126.05 g/mol of dimethyl phosphate (or whatever
# the phosphonate's variant gives); the verifier adds it to the
# byproduct when computing process-AE under that activator.
reagent_mass_alternatives:
  canonical_NaH_dimethyl:
    reagent_mass_g_per_mol: 24.0
    byproduct_mass_extra: 0.0      # bare base, byproduct = (MeO)2P(O)OH
    description: "Canonical HWE: NaH in THF, dimethyl phosphonate, E-selective; the textbook Wadsworth-Emmons 1961 protocol"
    doi: "10.1021/ja01468a042"
  canonical_KHMDS_dimethyl:
    reagent_mass_g_per_mol: 199.45
    byproduct_mass_extra: 0.0
    description: "KHMDS in THF, dimethyl phosphonate, E-selective; standard alternative for less acidic phosphonates"
    doi: "10.1021/cr60287a005"     # Boutagy-Thomas review
  masamune_roush:
    reagent_mass_g_per_mol: 322.0  # LiCl (42.39) + DBU (152.24) + MeCN (41.05) + some margin
    byproduct_mass_extra: 0.0
    description: "Masamune-Roush conditions: LiCl + DBU or iPr2NEt in MeCN; mild, avoids alpha-epimerization"
    doi: "10.1016/S0040-4039(01)80205-7"
  haidle_myers:
    reagent_mass_g_per_mol: 222.0  # NaOCH2CF3 (122.04) + CF3CH2OH (100.04) co-solvent
    byproduct_mass_extra: 0.0
    description: "Haidle-Myers conditions: NaOCH2CF3 in CF3CH2OH/DME; epimerization-suppressed, used for cytochalasin B and L-696,474 macrocyclization"
    doi: "10.1073/pnas.0402111101"
  still_gennari:
    reagent_mass_g_per_mol: 464.0  # KHMDS (199.45) + 18-crown-6 (264.32)
    byproduct_mass_extra: 136.0    # (CF3CH2O)2 vs (MeO)2 mass differential
    description: "Still-Gennari conditions: bis(trifluoroethyl) phosphonate + KHMDS + 18-crown-6; Z-SELECTIVE (1:20 to 1:50 Z)"
    doi: "10.1016/S0040-4039(00)85909-2"
  ando:
    reagent_mass_g_per_mol: 349.0  # KHMDS (199.45) + NaI (149.89)
    byproduct_mass_extra: 124.0    # (PhO)2 vs (MeO)2 mass differential
    description: "Ando conditions: diphenyl phosphonate + KHMDS or NaH + NaI; Z-SELECTIVE (1:10 to 1:50 Z), cheaper than Still-Gennari"
    doi: "10.1021/jo970057c"
  ando_macrocyclic:
    reagent_mass_g_per_mol: 302.0  # NaI (149.89) + DBU (152.24)
    byproduct_mass_extra: 165.0    # diaryl phosphonate vs dimethyl
    description: "Ando macrocyclic conditions: NaI + DBU; Z-SELECTIVE 13-18 membered cyclic alkenes; directly relevant to intramolecular Z-HWE"
    doi: "10.1016/j.tetlet.2011.01.043"
  nagorny_zn:
    reagent_mass_g_per_mol: 493.0  # Zn(OTf)2 (363.50) + iPr2NEt (129.24)
    byproduct_mass_extra: 0.0
    description: "Zn(II)-mediated HWE: Zn(OTf)2 + iPr2NEt; for strained / base-sensitive macrolides (e.g., lactimidomycin)"
    doi: "10.1021/ol401186f"

stereo_flags:
  - forms_new_alkene_geometry      # E by default; Z with Still-Gennari, Ando, or Ando-macrocyclic activator
  - alpha_C_becomes_sp2            # atom 1 of rule body (phosphonate alpha-C) becomes sp2 alkene C; pre-existing chirality is lost
  - preserves_other_sp3_stereo     # all ring atoms not adjacent to atoms 1, 5 are untouched
  - risk_alpha_epimerization       # if aldehyde alpha-C is sp3 stereocenter, prefer haidle_myers or masamune_roush activator

refs:
  - "Trost 1991, Science 254:1471 (atom economy)"
  - "Wadsworth & Emmons 1961, J. Am. Chem. Soc. 83:1733, DOI:10.1021/ja01468a042 (original HWE paper)"
  - "Boutagy & Thomas 1974, Chem. Rev. 74:87, DOI:10.1021/cr60287a005 (mechanism review)"
  - "Still & Gennari 1983, Tetrahedron Lett. 24:4405, DOI:10.1016/S0040-4039(00)85909-2 (Z-selective HWE)"
  - "Masamune, Roush, Blanchette 1984, Tetrahedron Lett. 25:2183, DOI:10.1016/S0040-4039(01)80205-7 (LiCl/amine mild HWE)"
  - "Ando 1995, Tetrahedron Lett. 36:4105, DOI:10.1016/0040-4039(95)00726-S (Z-selective diphenyl phosphonate)"
  - "Ando 1997, J. Org. Chem. 62:1934, DOI:10.1021/jo970057c (Z-selective HWE expanded scope)"
  - "Haidle & Myers 2004, Proc. Natl. Acad. Sci. USA 101:12048, DOI:10.1073/pnas.0402111101 (cytochalasin B + L-696,474 intramolecular HWE, NaOCH2CF3 conditions)"
  - "Ando, Narumiya, Takada, Teruya 2010, Org. Lett. 12:1460, DOI:10.1021/ol100071d (Z-selective macrolactone HWE)"
  - "Ando & Sato 2011, Tetrahedron Lett. 52:1284, DOI:10.1016/j.tetlet.2011.01.043 (Z-selective 13-18 membered macrocyclic HWE)"
  - "Larsen, Sun, Nagorny 2013, Org. Lett. 15:2998, DOI:10.1021/ol401186f (Zn-mediated HWE macrocyclization, lactimidomycin)"
  - "Bisceglia & Orelli 2015, Curr. Org. Chem. 19:744, DOI:10.2174/1385272819666150311231006 (101-citation HWE review)"
  - "Kobayashi, Tanaka, Kogen 2018, Tetrahedron Lett. 59:568, DOI:10.1016/j.tetlet.2017.12.076 (recent HWE in NP synthesis)"
  - "Janicki & Kielbasinski 2020, Adv. Synth. Catal. 362:2552, DOI:10.1002/adsc.201901591 (Still-Gennari review)"

notes: |
  Intramolecular Horner-Wadsworth-Emmons olefination of a beta-keto
  phosphonate (or phosphonoacetate ester) with a tethered aldehyde,
  closing a macrocyclic C=C alkene and expelling dialkyl phosphate
  at the bond level. Process-level AE is dominated by the choice of
  base + co-additives — Masamune-Roush (LiCl/DBU) or Haidle-Myers
  (NaOCH2CF3/CF3CH2OH) are the workhorse mild conditions for
  natural-product macrocyclization on substrates with base-labile
  alpha-stereocenters. Still-Gennari (CF3CH2O)2P and Ando (PhO)2P
  invert the default E-selectivity to Z-selective. The rule body is
  identical across all phosphonate variants; the byproduct mass and
  E/Z selectivity are configured at the activator level via
  reagent_mass_alternatives.

  Wittig macrocyclization (Ph3P=CR2 + aldehyde) is NOT covered by this
  rule — same mechanism class (oxaphosphetane), but byproduct is
  Ph3P=O (278 g/mol) and the phosphonium ylide must be pre-formed from
  PPh3 + alkyl halide. Should be a separate sibling rule
  wittig_macrocyclization.gml if a panel case requires it.

  Julia-Kocienski olefination (sulfonyl-stabilized carbanion + aldehyde)
  is NOT covered by this rule — same oxaphosphetane-like 4-ring
  intermediate, but byproduct is a sulfinate. The Haidle-Myers paper
  uses Julia-Kocienski for the *intermolecular* fragment coupling step
  but HWE for the *macrocyclization* step.

  Panel case: haidle_myers_cytochalasin_b_2004 (cytochalasin B 14-ring
  macrolactone + L-696,474 11-ring macrocarbocycle). After this rule
  lands, that case should switch from `transannular_diels_alder` (the
  TDA biomimetic interpretation per the current notes.md) to
  `hwe_olefination` with literature_ring_size: 14 and the canonical
  Haidle-Myers activator.

  Surrogate panel case: hwe_13_from_omega_aldehyde_beta_keto_phosphonate
  (13-ring cycloalkenone from a simple linear keto-aldehyde-phosphonate).
  Mirrors lactam_16 / lactone_16 / rcm_13 panels; tests the canonical
  (NaH + dimethyl phosphonate) activator with no stereochemistry
  considerations.
```

---

## Section 10 — Proposed GML structure (full sketch)

The full GML, ready for transcription into `data/rules/hwe_olefination.gml`:

```
rule [
    ruleID "hwe_olefination (intramolecular Horner-Wadsworth-Emmons, beta-keto phosphonate + aldehyde -> alkene + dialkyl phosphate)"
    # L: phosphonate alpha-C(1)-H(2)-P(3) with P=O(4); aldehyde C(5)=O(6)
    left [
        node [ id 2 label "H" ]                # alpha-H of phosphonate
        edge [ source 1 target 2 label "-" ]    # C-H bond of alpha-CH, broken (deprotonated by base)
        edge [ source 1 target 3 label "-" ]    # C-P bond of phosphonate, broken (the C=C forms in its place)
        edge [ source 5 target 6 label "=" ]    # C=O of aldehyde, broken (becomes C=C and P-O after collapse)
    ]
    context [
        node [ id 1 label "C" ]                # alpha-C of phosphonate (sp3 -> sp2)
        node [ id 3 label "P" ]                # P of phosphonate (stays in byproduct)
        node [ id 4 label "O" ]                # P=O of phosphonate (preserved across L->R)
        node [ id 5 label "C" ]                # aldehyde C (sp2, becomes alkene C)
        node [ id 6 label "O" ]                # aldehyde O (migrates to P in R)
        edge [ source 3 target 4 label "=" ]    # P=O bond, preserved (the original P=O stays put)
    ]
    # R: new C=C alkene (1=5) and new P-O of dialkyl phosphate (3-6); alpha-H bonds to phosphate O
    right [
        node [ id 2 label "H" ]
        edge [ source 1 target 5 label "=" ]    # new C=C alkene (the new ring bond)
        edge [ source 3 target 6 label "-" ]    # new P-O bond (former aldehyde O migrates to P)
        edge [ source 2 target 6 label "-" ]    # alpha-H ends up on phosphate O (the OH of (RO)2P(O)OH on workup)
    ]
]
```

**Key sections:**

- **`left`**: declares the to-be-broken bonds: α-C–H (1–2), α-C–P (1–3), and the aldehyde C=O (5=6). Only one explicit atom (H, ID 2) — the others are in context because they appear on both sides.
- **`context`**: the five atoms whose identity is preserved across L → R: C (1, sp³ → sp²), P (3, stays put), O (4, P=O preserved), C (5, stays sp²), O (6, migrates). The P=O bond (3=4) is explicit context.
- **`right`**: declares the new bonds: C=C alkene (1=5) for ring closure, P–O (3–6) for phosphate formation, H–O (2–6) for the proton on the phosphate.

**Off-rule substrate decorations** (preserved across morphism, not declared in rule body):
- The two `OR` groups attached to atom 3 (e.g., two `OMe` for dimethyl phosphonate) — these stay attached to P in the byproduct.
- The β-EWG attached to atom 1 (e.g., `C(=O)CR'` or `C(=O)OR'`) — this stays attached to atom 1 in the product alkene.
- The substrate tether between atoms 1 and 5 (the ring-forming chain) — this becomes the macrocyclic ring.
- The substituent attached to atom 5 (e.g., `CHR''–`) — this stays attached to atom 5 in the product alkene.

**Verifier sanity checks the rule should pass:**

- **Atom conservation.** L atoms: 1, 2, 3, 4, 5, 6. R atoms: 1, 2, 3, 4, 5, 6. ✓
- **BFS from `retained_root_atom: 1` through R-side edges** reaches atoms 1, 5 (the C=C of the new alkene) via the new 1=5 edge. It does **not** reach atoms 2, 3, 4, 6 through the C=C path (there is no edge from 1 or 5 to those atoms in R), so they form a disconnected byproduct component. ✓
- **Byproduct mass for dimethyl variant** (atoms 2, 3, 4, 6 + 2× OMe substrate context): 1 (H) + 30.974 (P) + 15.999 (O atom 4) + 15.999 (O atom 6) + 2 × 31.034 (OMe groups) = 126.04 g/mol. Match `byproduct_mass_g_per_mol`. ✓

**Variants** (per-phosphonate; lives in `reagent_mass_alternatives`, not separate GML files):

- For diethyl phosphonate: substrate context has two `OEt` groups on atom 3 instead of two `OMe`. Verifier byproduct mass recompute: 1.008 + 30.974 + 15.999 + 15.999 + 2 × 45.06 = 154.10 g/mol.
- For Still–Gennari `(CF₃CH₂O)₂`: substrate context has two `OCH₂CF₃` groups on atom 3. Recompute: 1 + 30.974 + 16 + 16 + 2 × 99.04 = 262.05 g/mol.
- For Ando `(PhO)₂`: substrate context has two `OPh` groups. Recompute: 1 + 30.974 + 16 + 16 + 2 × 93.10 = 250.17 g/mol.

The verifier handles this cleanly because the OR groups on atom 3 are read from the composed substrate, not from the rule body. The rule body is agnostic to the phosphonate variant.

**Difference from `rcm.gml`**: RCM has 4 atoms (the two retained alkene Cs + the two ethylene Cs that leave). HWE has 6 atoms (one retained C from each partner + the H, P, P=O-O, and aldehyde-O that all go into the byproduct). RCM's byproduct is C₂H₄ (28 g/mol); HWE's is `(RO)₂P(O)OH` (~126 g/mol for dimethyl). RCM's mechanism passes through a metallocyclobutane on a Ru catalyst; HWE's passes through a 4-membered oxaphosphetane and uses no transition metal.

**Difference from `macrolactonization.gml`**: macrolactonization has 6 atoms but the new bond is C–O (ester); HWE's new bond is C=C (alkene). Both have similar atom counts but the elements are different (no P in macrolactonization).

---

## Open questions / followups for Ivan

1. **Whether the rule's `byproduct_mass_g_per_mol` should be the canonical-acid form (126.05 for dimethyl) or the anion (125.04).** I've chosen the acid form because it matches the rule body (atom 2 = α-H ends up on the phosphate O in R, giving `(RO)₂P(O)OH`). The salt form (e.g., `Na(MeO)₂PO₂` 148.02) is the actual workup product and the form that gets filtered/washed. For consistency with macrolactonization (which books bare H₂O at 18.015 g/mol, not NaOH 39.997), I recommend the acid form. **Workstream F to confirm.**

2. **Whether to model the β-keto-phosphonate-ester variant separately from the β-keto-phosphonate-ketone variant.** Both fire the same rule body. The Haidle–Myers paper demonstrates both in one paper. I've recommended *not* splitting — both variants share the rule. The difference (ester C=O vs ketone C=O) lives in the off-rule substrate context. **Recommendation: one rule, two activator entries if needed.**

3. **Whether to expose the phosphonate's identity via `solver.extra` (`phosphonate: dimethyl|diethyl|still_gennari|ando`) or via `reagent_mass_alternatives` activator key.** I've used the activator-key approach in this brief because it parallels macroetherification's `sn_ar_chromium` vs `sn_ar_no_chromium` choice. **Recommendation: keep the activator-key approach** to maintain a single dispatch pattern across rules.

4. **Whether macrocert v0's `enforce_ez_geometry` predicate** (Workstream D) is wired up to read the activator key and select E or Z. If not, the panel case `expected.yaml` should explicitly set `expected_geometry: E` or `expected_geometry: Z`. **Workstream D to verify and Workstream F to expose.**

5. **Panel case re-categorization for `haidle_myers_cytochalasin_b_2004/`.** After this rule lands:
   - `expected.yaml` should change `literature_tactic: transannular_diels_alder` → `literature_tactic: hwe_olefination`.
   - `literature_ring_size: 14` stays (cytochalasin B is the 14-membered macrolactone case).
   - `expected_witness: optimal` stays.
   - `ae_class: high` becomes `ae_class: moderate` (byproduct ~125 g/mol is heavier than H₂O/HF but still moderate AE).
   - Add a sibling case `haidle_myers_l696474_2004/` for the 11-ring (or merge into a single case with two ring sizes per the Workstream A pattern).
   - Remove the TDA-fallback rationale from `notes.md` "Decision flag for Ivan" — option **(d) Add HWE rule and re-encode** becomes the chosen path.

6. **Whether to ship a `wittig_macrocyclization.gml` sibling rule.** No current panel case requires it. Recommendation: defer to v2 unless a target appears that requires Wittig macrocyclization.

7. **The Haidle–Myers paper uses HWE in two contexts: (a) intermolecular** (fragment coupling, `(EtO)₂P(O)CH(Me)C(O)Me` + α-amino aldehyde **7** with Ba(OH)₂; for the warm-up step in the synthesis), and (b) intramolecular (the macrocyclization). The rule we're encoding is only the intramolecular variant. Macrocert is currently focused on macrocyclization rules; intermolecular C=C-forming rules are out of scope for v1. **Recommendation: defer intermolecular HWE to v2.**

---

## Cross-references in the vault

- [[Haidle Myers 2004 - An Enantioselective Modular and General Route to the Cytochalasins Synthesis of L-696474 and Cytochalasin B|Haidle & Myers (2004)]] — the direct panel case
- [[Wadsworth Emmons 1961 - The Utility of Phosphonate Carbanions in Olefin Synthesis|Wadsworth & Emmons (1961)]] — original HWE paper
- [[Boutagy Thomas 1974 - Olefin Synthesis with Organic Phosphonate Carbanions|Boutagy & Thomas (1974)]] — mechanism review
- [[Still Gennari 1983 - Direct Synthesis of Z-Unsaturated Esters Useful Modification Horner Emmons|Still & Gennari (1983)]] — Z-selective modification
- [[Masamune Roush Blanchette 1984 - Horner Wadsworth Emmons LiCl Amine Base Sensitive|Masamune, Roush, Blanchette (1984)]] — LiCl/amine mild conditions
- [[Ando 1995 - Practical Synthesis Z-Unsaturated Esters Ethyl Diphenylphosphonoacetate|Ando (1995)]] — Ando diphenyl phosphonate
- [[Ando 1997 - Highly Selective Z-Unsaturated Esters Diarylphosphono Acetates|Ando (1997)]] — Ando Z-selective expanded scope
- [[Ando Narumiya Takada Teruya 2010 - Z-Selective Intramolecular HWE Macrocyclic Lactones|Ando, Narumiya, Takada, Teruya (2010)]] — macrolactone Z-HWE
- [[Ando Sato 2011 - Z-Selective Intramolecular HWE for Macrocyclic Alkenes|Ando & Sato (2011)]] — 13-18 membered Z-cyclic alkenes
- [[Larsen Sun Nagorny 2013 - Lactimidomycin Zn(II) Mediated HWE Macrocyclization|Larsen, Sun, Nagorny (2013)]] — Zn-mediated HWE macrocyclization
- [[Bisceglia Orelli 2015 - Recent Progress in the Horner Wadsworth Emmons Reaction|Bisceglia & Orelli (2015)]] — 101-citation HWE review
- [[Kobayashi Tanaka Kogen 2018 - Recent Topics Natural Product Synthesis HWE Reaction|Kobayashi, Tanaka, Kogen (2018)]] — recent NP synthesis review
- [[Janicki Kielbasinski 2020 - Still-Gennari Olefination Applications in Organic Synthesis|Janicki & Kiełbasiński (2020)]] — Still-Gennari modern review

(External nodes have been created in the graph for each of the papers above that did not already exist. Run `vlt graph query sql "SELECT name FROM graph_nodes WHERE name LIKE '%HWE%' OR name LIKE '%Horner%' OR name LIKE '%Phosphonate%' OR name LIKE '%Wadsworth%' OR name LIKE '%Ando%' OR name LIKE '%Still%Gennari%'"` to verify.)
