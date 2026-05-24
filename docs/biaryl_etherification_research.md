# Biaryl Etherification Rule — Chemistry Research Brief

**Workstream:** C (Rule library expansion)
**Target artifacts:** `data/rules/biaryl_etherification.gml` + `.meta.yaml`, plus the vancomycin CDE-ring panel case (Workstream B)
**Date:** 2026-05-24
**Author:** researcher agent (for Ivan / Workstream C)
**Driver:** Workstream A's `macroetherification_research.md` §1.4 / §7.1 finding — vancomycin's CD and DE rings (and the K-13/OF4949/bouvardin/RA-VII/chloropeptin/complestatin family) close by **Ar–O–Ar SNAr**, not Ar–O–C(sp³) and not macrolactamization. The just-encoded `aryl_etherification.gml` covers the alkyl-aryl ether variant only. This sibling brief specifies the Ar–O–Ar rule.

Mirrors the structure of `macroetherification_research.md`. The bond chemistry is so close to `aryl_etherification` that this brief carries only what differs, plus the full proposed artifacts.

---

## Section 1 — Distinction from `aryl_etherification`

### 1.1 The single label change

Both rules expel HF (or HX) from an Ar–LG + HO– pair. They share the SNAr mechanism, the Meisenheimer intermediate, the leaving-group menu (F preferred, Cl/Br/NO₂ documented), and the activator stack. They differ in **exactly one atom-map property**: the hybridization of the alcohol's carbon partner.

| Property                       | `aryl_etherification`                | `biaryl_etherification` (this rule)   |
| ------------------------------ | ------------------------------------ | ------------------------------------- |
| Bond formed                    | Ar(sp²)–O–C(sp³)                     | Ar(sp²)–O–Ar′(sp²)                    |
| Atom 1 (electrophile C)        | aromatic sp² C bearing F             | aromatic sp² C bearing F              |
| Atom 5 (nucleophile O)         | sp³-bonded O of an aliphatic alcohol | sp²-bonded O of a phenol              |
| Atom-5 environment in context  | bonded to a C(sp³) in the substrate  | bonded to an aromatic C(sp²)          |
| Bond-level byproduct           | HF (20.006 g/mol)                    | HF (20.006 g/mol) — identical         |
| Mechanism                      | SNAr (Meisenheimer) / Ullmann / Pd   | SNAr (Meisenheimer) / Ullmann / Pd    |
| Dominant stereochemical issue  | retained alcohol C(sp³) stereo       | **atropisomerism** at the new biaryl-ether bridge |
| Sp³ stereocenter at the bridge | YES — preserved                      | NO — bridge is two sp² carbons        |

In the GML body the change is one node label: the `context` block declares atom 5 as the phenolic O of an aromatic ring rather than the aliphatic O of an alcohol. In MØD GML the way to enforce that distinction at rule-application time is to bind atom 5 to an aromatic neighbor — explicitly declaring an aromatic edge from O(5) to a new context atom 7 labelled "C" with `label ":"` (aromatic) or `"-"` (single, since phenolic C–O is conventionally drawn as a single bond to an aromatic C). See §2 for the chosen encoding.

### 1.2 Why this is a separate rule rather than a parameter

Three reasons:

1. **MØD rule application is structural.** The verifier matches the rule's L-graph against substrate subgraphs. If the rule only declares atom 5 as `O` with no aromatic neighbor, it will fire on *any* OH — phenolic or aliphatic. A single combined rule would over-fire on aliphatic substrates and lose the panel-case discrimination Workstream B needs (vancomycin CDE must select `biaryl_etherification`, ascomylactam A must select `aryl_etherification`).
2. **Stereo flags differ.** `aryl_etherification` declares `retains_alcohol_stereo` because the sp³ alcohol C is off-rule. `biaryl_etherification` has no sp³ stereocenter at the bridge and instead declares `can_generate_atropisomerism` as a primary stereo outcome (see §4).
3. **Panel classification.** Workstream B's panel uses `expected.yaml.literature_tactic` as the selection key. Vancomycin's CD/DE closures must report `biaryl_etherification`; conflating the two would let an aryl-ether-with-sp³-OH fire on the vancomycin CDE substrate and produce a false positive on M5.

### 1.3 What this rule does NOT cover

- **Mitsunobu phenol-aryl** (DIAD activates the phenol's OH; rare for Ar–O–Ar because the resulting phenoxyphosphonium does not cleanly attack a second arene under macrocyclization conditions). Out of scope for the same reason it's out of scope for `aryl_etherification`.
- **Ullmann-type Ar–O–Ar with a non-fluoride leaving group**: covered as a `reagent_mass_alternatives` entry, not a separate rule. Atom map is identical; only LG identity and activator stack change.
- **Oxidative phenolic coupling** (laccase, FeCl₃, VOF₃, PhI(OAc)₂; this is the *biomimetic* Ar–O–Ar formation route — Pearson, Evans 1998 for the vancomycin AB ring; biosynthetic radical coupling in bacteria). Mechanistically distinct (radical or 2e⁻ oxidative), no SNAr leaving group expelled, no HF byproduct. **Separate future rule** `oxidative_phenol_etherification.gml` if a target requires it.
- **AB ring of vancomycin** (Ar–Ar biaryl bond, no oxygen bridge). This is `biaryl_coupling.gml` territory (Ni(0) reductive coupling or Pd Suzuki — see Boger 1999 JACS 121:10004, AB ring uses Ni-mediated biaryl).

---

## Section 2 — Atom-mapped DPO scheme

### 2.1 The bond-level chemistry

$$
\text{Ar}_1\!-\!\text{F} + \text{HO}\!-\!\text{Ar}_2 \;\longrightarrow\; \text{Ar}_1\!-\!\text{O}\!-\!\text{Ar}_2 + \text{HF}
$$

Identical to `aryl_etherification` at the mass-balance level. Both sp² aromatic carbons (atoms 1 and 7-in-substrate) are retained in the product; F (atom 2) and H (atom 6) leave together as HF (20.006 g/mol). Mechanism: Meisenheimer addition-elimination at $\text{Ar}_1$.

### 2.2 Atom numbering (mirrors `aryl_etherification.gml`)

| ID  | Element | Role                                                                                |
| --- | ------- | ----------------------------------------------------------------------------------- |
| 1   | C       | Aromatic C(sp²) bearing the leaving group F — retained, becomes Ar–O–Ar bridge C    |
| 2   | F       | Aromatic leaving group — expelled in HF                                             |
| 3   | —       | (unused, slot parity with macrolactonization)                                       |
| 4   | —       | (unused, slot parity with macrolactonization)                                       |
| 5   | O       | Phenolic O — retained, becomes the biaryl ether bridge O                            |
| 6   | H       | Phenolic OH proton — expelled in HF                                                 |

The atom IDs match `aryl_etherification.gml` IDs 1, 2, 5, 6 exactly so the verifier's BFS-from-`retained_root_atom: 1` traversal works identically across the two rules. The only structural change from `aryl_etherification` is the *environment* of atom 5: in this rule atom 5 must be bonded to an aromatic C of the second arene. There are two ways to enforce this:

**Option A (minimal — recommended):** declare atom 5 as `O` in `context`, same as `aryl_etherification`, and let the strategy file's predicate `alcohol_partner_C_must_be_aromatic` (sibling of the `aryl_etherification` predicate `alcohol_partner_C_must_be_sp3`) discriminate at strategy time. **This keeps the GML body identical to `aryl_etherification` except for the rule ID.** No new context atoms; verifier semantics unchanged.

**Option B (explicit):** add a context atom 7 (aromatic C, the phenolic C bonded to O(5)) and an explicit edge `5–7` so the rule only matches when O(5) is bonded to an aromatic C. Tighter at the rule layer, but requires updating the verifier's atom-slot conventions and breaks the slot-parity with `aryl_etherification`.

**Recommendation: Option A.** Keep the rule body as a near-copy of `aryl_etherification.gml` with only the `ruleID` string changed; encode the aromatic-O distinction in the strategy file. This minimizes code churn, makes the family relationship explicit, and lets the verifier reuse the same mass-recompute path. The trade-off is that the rule, alone, cannot distinguish phenolic from aliphatic O — Workstream D's strategy file must do the routing.

### 2.3 Bond changes (same as `aryl_etherification`)

**Broken (L):** 1–2 (Ar–F), 5–6 (phenol O–H).
**Preserved (context):** atom 1 (aromatic C, neighbors inherited from substrate), atom 5 (O, aromatic neighbor inherited from substrate).
**Formed (R):** 1–5 (new Ar–O bond, the biaryl ether bridge), 2–6 (new H–F).

### 2.4 Mass balance check

- L mass: Ar–F (Ar bears F at atom 2) + Ar′–OH (Ar′ bears OH at atom 5).
- R mass: Ar–O–Ar′ (atoms 1 and 5 now bonded) + HF (atoms 2 and 6 now bonded).
- Net mass: F + H leave as HF = 18.998 + 1.008 = **20.006 g/mol** ✓.

LG alternatives identical to `aryl_etherification`: Cl → HCl (36.461), Br → HBr (80.912), I → HI (127.912), NO₂ → HNO₂ (47.013).

### 2.5 Verifier sanity checks (identical to `aryl_etherification`)

- BFS from `retained_root_atom: 1` through R-edges reaches atoms 1, 5 (the Ar–O–Ar bridge, then onto both arene substructures via the substrate). Does **not** reach atoms 2, 6.
- Bond-mass delta: 2 broken, 2 formed. ✓
- Byproduct mass 20.006 g/mol. ✓

---

## Section 3 — Reagent + byproduct mass per mechanism

Identical activator menu to `aryl_etherification`, with the following adjustments specific to biaryl-ether substrates:

| Activator                                    | Coupling agent stack                                          | Auxiliaries (typical)                              | reagent_mass_g_per_mol | byproduct_mass_extra | Typical scope                                                                                                                                                                                                                                                                              | Reference DOI                                                                |
| -------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------- | ---------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **SNAr (electron-poor arene, no Cr) — CANONICAL** | (substrate-borne *ortho*-NO₂ or *ortho*-CO₂R activation)      | CsF or K₂CO₃ (138.21) or Cs₂CO₃ (325.82); DMF/DMSO | **326** (Cs₂CO₃)       | CsF (151.9) + CsHCO₃ (193.9) ≈ **346**           | The workhorse for vancomycin CD/DE rings (Boger 1997/1999), K-13/OF4949 (Janetka-Rich 1997 uses Ru-arene as alt), bouvardin/RA-VII (Boger 1993/1995), teicoplanin F-O-G (Zhu 1995). Substrate must carry ortho-NO₂ that is *removed reductively after macrocyclization* (NO₂ → Cl or NO₂ → H). | `10.1055/s-1997-722`, `10.1021/jo00098a010`, `10.1021/ja992577q`             |
| **SNAr (η⁶-arene-M) Cr or Ru activation**    | Cr(CO)₆ (220.06) or [Cp*Ru(MeCN)₃]PF₆ (~505) on the way in    | Cs₂CO₃ (325.82); CAN (548.22) decomplex for Cr     | **1094** (Cr) / ~830 (Ru) | Cr(CO)₃·L₃ + CAN ≈ **820** (Cr); RuCp* + PF₆ ≈ **500** (Ru)             | When the arene is not intrinsically electron-poor enough for direct SNAr. Janetka & Rich 1997 (`10.1021/ja970614c`) used Cp*Ru(MeCN)₃PF₆ for K-13/OF4949-III when the unactivated arene didn't reach Meisenheimer reactivity. Same η⁶-π-complex strategy as Uchiro 2017 (Cr) on GKK1032A₂.    | `10.1002/asia.201601728` (Cr), `10.1021/ja970614c` (Ru)                      |
| **Cu Ullmann C–O coupling**                  | CuI (190.45, 5–20 mol%)                                       | 1,10-phen (180.21) + Cs₂CO₃ (325.82); toluene 100–130 °C | **696**                | CsBr (212.81) or CsI (259.81) + CsHCO₃ (193.92) ≈ **407–453**           | Ar–OH + Ar′–Br/I → Ar–O–Ar′. Broader scope than SNAr (electron-rich arenes accessible); milder than older "stoichiometric Cu" Ullmann. The Boger group's Ni-mediated biaryl coupling on vancomycin AB ring uses different mechanism (no O bridge).                                          | `10.3390/catal10101103`                                                      |
| **Pd Buchwald diaryl ether**                 | Pd₂(dba)₃ (915.72, 2–5 mol%) + RockPhos/t-BuXPhos (~425–470)  | Cs₂CO₃ (325.82) or K₃PO₄ (212.27); toluene 90–110 °C | **1714** (nominal stoichiometric) | CsBr (212.81) + CsHCO₃ (193.92) ≈ **407**           | Mild, modern; Ar–OH + Ar′–Br/OTf → Ar–O–Ar′. The Aranyos/Old/Kiyomori/Wolfe/Sadighi/Buchwald 1999 paper (`10.1021/ja990324r`) is the canonical reference for diaryl ethers. Rarely used for natural-product macrocyclization vs intermolecular synthesis, but in scope.            | `10.1021/ja990324r`                                                          |

**Activator-choice notes specific to biaryl-ether substrates:**

- **The intrinsic *ortho*-NO₂ trick is the load-bearing biaryl-ether macrocyclization tactic.** Beugelmans 1994 (`10.1021/jo00098a010`) abstract verbatim: *"After serving as an activator, the nitro group ortho to the diaryl ether linkage is converted either into a chlorine or a hydrogen atom, thus achieving the substitution pattern found in the vancomycin family of glycopeptides."* The same trick recurs in Boger 1995 (bouvardin, `10.1016/0960-894x(95)00192-v`), Boger 1997 (CD/DE rings, `10.1021/jo970560p`), Boger 1999 vancomycin aglycon (`10.1021/ja992577q`), and Rao 1994 (`10.1016/S0040-4039(00)74434-0`). The NO₂ group serves a dual role: Meisenheimer activator during macrocyclization, then sacrificial substituent removed post-closure.
- **The Cr/Ru π-complex variant is the fallback** when intrinsic NO₂ activation is unavailable or undesired. Janetka & Rich's Ru-arene route (1997, JACS 119:6488) is the analog of Uchiro 2017's Cr-arene route — same principle (η⁶ metal-π complex withdraws ring electron density, enabling SNAr at an otherwise inert aryl-F), different metal. The Ru complex decomplexes photochemically or by ligand exchange; Cr decomplexes oxidatively (CAN, I₂) or photolytically.
- **Ullmann and Pd Buchwald are mass-cheaper at the *biaryl-ether* level than the Cr SNAr** because they avoid the η⁶-complexation step. They are not, however, the literature-canonical choice for vancomycin: nearly all reported vancomycin / K-13 / bouvardin syntheses use direct SNAr at a NO₂-activated arene. The Ullmann / Pd Buchwald alternatives are included for completeness and for substrates where the activator group cannot be installed.

**Process-AE intuition.** Identical to `aryl_etherification`: bond-level byproduct is 20 g/mol of HF, process-level activator stack is 326–1714 g/mol. The cheapest path (SNAr at NO₂-activated arene) is also the literature canonical for the vancomycin family — uncommon convergence of bond-AE and process-AE in the same activator choice.

---

## Section 4 — Stereochemistry: atropisomerism is the load-bearing chirality element

### 4.1 No sp³ stereocenter at the bridge

The biaryl ether bridge is **(sp²)–O–(sp²)**. Unlike `aryl_etherification`, this rule never creates or destroys an sp³ stereocenter at either of the bridge atoms. The phenol carbon (Ar′ side, atom 5's neighbor) and the aryl-F carbon (atom 1) are both sp² aromatic. The closure has no point-chirality effect at the bridge.

What it *does* generate is **axial chirality** (atropisomerism) at the new Ar–O–Ar bridge if the two arenes carry ortho substituents that hinder rotation around the C–O–C axis. For most vancomycin-family substrates, the ortho substituents are heavy enough (Cl, NO₂ → H/Cl post-removal, or large peptide side-chains) that the rotation barrier exceeds ~25 kcal/mol and the two atropisomers are isolable at room temperature.

### 4.2 Boger's "ordered atropisomer equilibrations" — what they mean

[[Boger Miyazaki Kim Wu Loiseleur Castle 1999 - Vancomycin Aglycon Atropisomer Equilibrations|Boger et al. (1999)]] (*J. Am. Chem. Soc.* 121:3226–3227, DOI `10.1021/ja990189i`) and the full paper [[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis|Boger et al. (1999)]] (*J. Am. Chem. Soc.* 121:10004–10011, DOI `10.1021/ja992577q`) report the following:

- The **CD ring closure** (16-membered biaryl ether between vancomycin's residue 4 and residue 6) proceeds with kinetic preference for one atropisomer, then **equilibrates thermally** to the natural atropisomer at elevated temperature (typically refluxing chlorobenzene or *o*-DCB, 130–180 °C). The energy difference between atropisomers is small enough that the equilibrium reaches the natural diastereomer within hours.
- The **DE ring closure** (16-membered biaryl ether between residue 6 and residue 2) proceeds with the *opposite* atropisomer preference kinetically, and equilibrates similarly.
- The "ordered" in the title refers to a strategic *sequence*: close the CD ring first, equilibrate, then close DE, equilibrate. If the CD ring is closed in the wrong atropisomer it can be corrected before the DE closure further constrains the geometry. The thermal equilibrations are reported in detail in [[Boger Castle Miyazaki Wu Beresis Loiseleur 1999 - Vancomycin CD DE Macrocyclization Atropisomerism|Boger et al. (1999)]] (*J. Org. Chem.* 64:70–80, DOI `10.1021/jo980880o`).

For MØD-MacroCert, the practical consequence is that **the rule firing does not pin down the atropisomer** — the substrate's 3D geometry at closure time partially determines kinetic selectivity, and post-closure thermal equilibration determines thermodynamic outcome. Workstream A's encoding strategy for vancomycin should either (a) accept both atropisomers as valid M5 outputs and rely on `chemistry-equivalent` comparison to match the natural product, or (b) declare a stereo flag `equilibrates_atropisomer_thermally` and let Workstream F's stereo machinery handle the post-cyclization correction.

### 4.3 Stereo flags to declare

```yaml
stereo_flags:
  - generates_atropisomerism                  # always — biaryl ether bridge with hindered rotation
  - equilibrates_atropisomer_thermally        # for vancomycin family; Boger 1999 ordered equilibrations
  - retains_arene_substituents                # SNAr/Ullmann/Buchwald all preserve ring substituents
  - no_sp3_stereocenter_at_bridge             # explicit non-claim — distinguishes from aryl_etherification
```

`generates_atropisomerism` replaces the `can_generate_atropisomerism` of `aryl_etherification`: in the alkyl-aryl rule atropisomerism is incidental and depends on ring size + substituents; here it is structurally guaranteed at any ring size where rotation is hindered. The flag `equilibrates_atropisomer_thermally` is biaryl-ether-specific and tells Workstream F's stereo machinery that post-closure equilibration is a documented tactic for this rule (Boger 1999).

### 4.4 No stereo from the rule itself

The DPO span does not specify atropisomer configuration. MØD's atom-map operates on connectivity; axial chirality is a 3D-geometric attribute that lives in the V2000/V3000 coordinates of the substrate and the product, not in the rule body. The rule fires identically on either substrate atropisomer; the *substrate's* 3D coordinates determine which product atropisomer the verifier emits.

---

## Section 5 — Boger vancomycin deep-dive (CDE rings)

The vancomycin aglycon has three macrocyclic rings:

- **AB ring** (12-membered, biaryl Ar–Ar): closed by **Ni(0)-mediated biaryl coupling** of an aryl-Cl with an aryl-boronate or aryl-stannane (`10.1021/ja992577q`, §AB). No oxygen bridge; not in scope for this rule. Belongs to a future `biaryl_coupling.gml` rule.
- **CD ring** (16-membered, Ar–O–Ar biaryl ether): closed by **intramolecular SNAr** of an *ortho*-nitro-activated aryl-F with a phenol (`10.1021/jo970560p`, `10.1021/ja992577q`). **In scope for this rule.**
- **DE ring** (16-membered, Ar–O–Ar biaryl ether): closed by **intramolecular SNAr** of an *ortho*-nitro-activated aryl-F with a phenol (`10.1021/jo970560p`, `10.1021/ja992577q`). **In scope for this rule.**

### 5.1 Ring sizes and counts

Both CD and DE are **16-membered**. The two rings share residue D (a central tyrosine derivative whose two ortho positions provide the two phenolic O atoms — one to C-ring, one to E-ring). The macrocycles are fused at residue D, giving the vancomycin aglycon's characteristic [[Boger Borzilleri Nukui Beresis 1997 - Vancomycin CD DE Ring Systems|"CDE tricyclic core"]].

### 5.2 Ring-by-ring closure conditions

[[Boger Borzilleri Nukui Beresis 1997 - Vancomycin CD DE Ring Systems|Boger, Borzilleri, Nukui, Beresis (1997)]] (*J. Org. Chem.* 62:4721–4736, DOI `10.1021/jo970560p`) is the primary reference. The conditions:

- **CD ring (16-membered SNAr)**: linear precursor with ortho-NO₂-aryl-F (residue 4) and free phenol (residue 6). Cs₂CO₃ or KF in DMF at 60–80 °C. Macrocycle yield: 65–80% on simplified substrates, lower on fully functionalized aglycon. The NO₂ is removed post-closure by reductive aromatization (Sn/HCl or H₂/Pd) and replaced with H or Cl.
- **DE ring (16-membered SNAr)**: linear precursor with ortho-NO₂-aryl-F (residue 6) and free phenol (residue 2). Same activator stack as CD. Macrocycle yield similar.
- **AB ring (12-membered, NOT this rule)**: Ni(0)-promoted aryl–aryl coupling. Different mechanism.

The full vancomycin aglycon ([[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis|Boger et al. (1999)]] *J. Am. Chem. Soc.* 121:10004–10011) closes the three rings in sequence: AB first (Ni biaryl), then CD (SNAr), then DE (SNAr), with thermal atropisomer equilibration steps interleaved.

### 5.3 CD vs DE differences

| Feature                  | CD ring                                        | DE ring                                        |
| ------------------------ | ---------------------------------------------- | ---------------------------------------------- |
| Ring size                | 16-membered                                    | 16-membered                                    |
| Mechanism                | Intramolecular SNAr                            | Intramolecular SNAr                            |
| Activator                | ortho-NO₂ on the aryl-F arene (residue 4)      | ortho-NO₂ on the aryl-F arene (residue 6)      |
| Leaving group            | F                                              | F                                              |
| Kinetic atropisomer pref | Non-natural M-atropo at the new bridge         | M (opposite-handed) at the DE bridge           |
| Equilibration            | Thermal, refluxing PhCl / o-DCB, hours         | Thermal, same conditions                       |
| Post-closure NO₂ fate    | Reductive removal → H or Cl (residue 4 → desired Cl) | Reductive removal → H (residue 6 → desired H) |

Both rings use the **same canonical activator (Cs₂CO₃/DMF + intrinsic ortho-NO₂)**. They differ in which residue carries the F leaving group and which carries the phenol nucleophile, and in their kinetic atropisomer preference (which Boger's "ordered equilibration" strategy exploits). For MØD-MacroCert purposes, both fire `biaryl_etherification` with the same rule body and same activator entry (`sn_ar_electron_poor_arene`). The CD/DE distinction lives in the substrate geometry, not the rule.

### 5.4 What this tells us about the rule

- **Both CD and DE close via the canonical SNAr-NO₂ path.** No metal-arene complexation needed (unlike Uchiro 2017's GKK1032A₂ Cr-SNAr). The intrinsic activation is sufficient.
- **Ring size 16 is comfortably within the SNAr macrocyclization range.** Boger 1995 reported "unusually facile" 14-ring SNAr on the bouvardin scaffold; 16 is similar. Below ~13 the macrocyclic strain becomes prohibitive (Workstream D predicate `ring_size >= 12`, inherited from `aryl_etherification`).
- **The NO₂ activator is removed post-closure.** This means a full reaction model needs *two* post-closure steps (NO₂ → NHR or NO₂ → Ar–H or NO₂ → Ar–Cl) that are not encoded by `biaryl_etherification`. The rule fires the *closure*; the subsequent NO₂ removal is a separate transformation Workstream F should track.
- **The atropisomer is fixed thermally, not at closure.** The rule emits both atropisomers as valid products; the verifier should not penalize either.

---

## Section 6 — Other family members (full panel coverage)

### 6.1 K-13 and OF4949 (Janetka & Rich, 1997)

- **K-13** and **OF4949-III**: 17-membered biaryl ether peptide macrocycles. Both contain the isodityrosine motif (two tyrosines bridged by an Ar–O–Ar ether). Source: [[Janetka Rich 1997 - K-13 OF4949 SNAr Ruthenium Arene Macrocyclization|Janetka & Rich (1997)]], *J. Am. Chem. Soc.* 119:6488–6495, DOI `10.1021/ja970614c`.
- **Activator**: [Cp*Ru(MeCN)₃]PF₆ η⁶-π-arene complex on the aryl-F partner. After macrocyclization, photolytic decomplexation in MeCN liberates the free macrocyclic peptide. **Ru-arene is the chemistry analog of Uchiro 2017's Cr-arene strategy.**
- **Why not direct SNAr?** Tyrosine-derived arenes are mildly electron-rich (ortho-OR/NR), so the Meisenheimer intermediate is not stable enough at room temperature. The η⁶-Ru complex withdraws electron density just as Cr(CO)₃ does, enabling the SNAr. Earlier syntheses (Boger Yohannes 1990, `10.1021/jo00311a019`) used direct SNAr with NO₂ activation; Janetka-Rich's Ru-arene route is the alternative.
- **In MØD-MacroCert**: K-13 and OF4949 are panel candidates for `biaryl_etherification` with activator `sn_ar_arene_M` (Ru variant). Atom-map identical.

### 6.2 Bouvardin, deoxybouvardin, RA-VII (Boger 1993, 1995)

- **Bouvardin**, **deoxybouvardin**, and **RA-VII**: 14-membered biaryl ether peptide macrocycles ("cycloisodityrosine" core). Bicyclic cyclic hexapeptides where the isodityrosine biaryl ether closure forms the 14-ring inner cycle.
- **Source for the macrocyclization**: [[Boger Borzilleri 1995 - SNAr Biaryl Ether Macrocyclization Bouvardin|Boger & Borzilleri (1995)]], *Bioorg. Med. Chem. Lett.* 5:1187–1190, DOI `10.1016/0960-894x(95)00192-v` — "An unusually facile SNAr 14-membered biaryl ether macrocyclization". Title is verbatim and load-bearing: 14-ring SNAr closure on the cycloisodityrosine subunit. Full synthesis: [[Boger Yohannes Zhou Patane 1993 - RA-VII Deoxybouvardin Cycloisodityrosine Total Synthesis|Boger, Yohannes, Zhou, Patane (1993)]], *J. Am. Chem. Soc.* 115:3420–3430, DOI `10.1021/ja00062a004`.
- **Activator**: ortho-NO₂ + Cs₂CO₃ / DMF (same as vancomycin CD/DE). Intrinsic activation; no η⁶-metal complex.
- **In MØD-MacroCert**: panel candidates for `biaryl_etherification` with activator `sn_ar_electron_poor_arene` and ring size 14. Activator stack identical to vancomycin CDE.

### 6.3 Chloropeptin and complestatin (Boger 2009)

- **Chloropeptin II / complestatin** and **chloropeptin I**: complex polycyclic peptides containing a biaryl C–C linkage *plus* a Trp-derived indole-aryl bond. The macrocyclic closure that defines the family is **not** a biaryl ether — Boger's 2009 total synthesis ([[Garfunkle Kimball Trzupek Takizawa Shimamura Tomishima Boger 2009 - Chloropeptin II Complestatin Total Synthesis|Garfunkle et al. (2009)]], *J. Am. Chem. Soc.* 131:16036–16038, DOI `10.1021/ja907193b`) uses a **macrolactamization** to form the peptide ring, with the biaryl and indole-aryl bonds installed before macrocyclization.
- **In MØD-MacroCert**: chloropeptin/complestatin are **NOT** straightforward `biaryl_etherification` panel candidates — they belong to the macrolactamization panel, with biaryl_coupling and indole-aryl-coupling rules used to set up the precursor. Note the original task brief listed them as family members; this is partially correct (they're vancomycin-family relatives in the broad sense) but the ring-defining closure differs. **Recommendation**: do NOT add chloropeptin/complestatin to the `biaryl_etherification` panel; flag them as a separate panel case requiring multi-rule composition.

### 6.4 Family summary table

| Compound      | Ring size (biaryl-ether ring) | Activator                                          | Reference DOI                                   | Panel role for `biaryl_etherification`           |
| ------------- | ------------------------------ | -------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| Vancomycin CD | 16                            | ortho-NO₂ + Cs₂CO₃ / DMF                           | `10.1021/jo970560p`, `10.1021/ja992577q`        | **PRIMARY** — drives this rule's design          |
| Vancomycin DE | 16                            | ortho-NO₂ + Cs₂CO₃ / DMF                           | `10.1021/jo970560p`, `10.1021/ja992577q`        | **PRIMARY**                                      |
| Bouvardin / RA-VII | 14                       | ortho-NO₂ + Cs₂CO₃ / DMF                           | `10.1016/0960-894x(95)00192-v`, `10.1021/ja00062a004` | Secondary panel case (smaller ring, simpler scaffold) |
| K-13 / OF4949-III | 17                         | Cp*Ru(MeCN)₃PF₆ η⁶-arene + base                    | `10.1021/ja970614c`                             | Tertiary panel case (Ru-activated variant)       |
| Teicoplanin F-O-G | 14                         | ortho-NO₂ + Cs₂CO₃ / DMF                           | `10.1021/jo00125a026`                           | Secondary panel case                             |
| Chloropeptin / complestatin | (peptide ring not biaryl ether) | (macrolactamization for the ring)        | `10.1021/ja907193b`                             | **OUT OF SCOPE** for this rule                   |

---

## Section 7 — Forbidden contexts for Workstream D

Most forbidden-context predicates from `aryl_etherification` carry over. Changes from the alkyl-aryl rule are flagged:

1. **Electron-rich arene without a DG or η⁶-metal activation.** Same as `aryl_etherification`. Predicate: `arene_partner_must_have_EWG_or_metal_complex`. (Note: NO₂ is the typical EWG; without it the Meisenheimer is too unstable.)
2. **Ortho-protic NH/OH/SH on the F-bearing arene.** New for this rule: a thiol or amine ortho to the F competes with the phenol O for SNAr (same risk as in `aryl_etherification`), and the *phenolic O itself* may be doubly deprotonated under Cs₂CO₃, slowing the rate. Predicate: `arene_partner_must_not_have_ortho_SH_or_NHR`.
3. **Ring size < 12.** Same as `aryl_etherification`; below 12 the macrocyclic strain dominates. Predicate: `ring_size >= 12`.
4. **Phenolic partner has free NHR or NH₂ on the same arene.** The amine is more nucleophilic than the phenoxide under basic SNAr conditions and will close to a biaryl amine (`biaryl_amination`, a sibling rule for Pd Buchwald-Hartwig). Predicate: `phenol_arene_must_not_have_free_amine`.
5. **Sp³ alcohol on the phenolic-O partner's tether** (would race with the phenolic-O for SNAr; if the sp³ alcohol wins, the closure is the `aryl_etherification` rule, not this one). Predicate: `alcohol_partner_O_must_be_phenolic` — this is the **inverse of `aryl_etherification`'s `alcohol_partner_C_must_be_sp3`** and is the load-bearing strategy-level discriminator between the two rules.
6. **Free primary amine elsewhere on the chain.** Same as `aryl_etherification` predicate `no_other_nucleophiles_on_tether`.

Predicate #5 is the new one specific to this rule. It encodes the routing decision: when Workstream D sees a substrate, it inspects the OH partner — if the O is bonded to an aromatic C, route to `biaryl_etherification`; if bonded to an sp³ C, route to `aryl_etherification`.

---

## Section 8 — Toy substrate proposal

**Recommendation: 14-membered biaryl ether closure of an *ortho*-nitro-aryl-F with a tyrosine-derived phenol**, parallel to the cycloisodityrosine subunit of bouvardin (Boger 1995, "unusually facile" 14-ring SNAr).

### 8.1 The surrogate

The simplest viable surrogate is a peptide-tethered pair of *para*-substituted phenols where one arene carries an *ortho*-NO₂ + *para*-F and the other carries a free OH. Structure (schematic):

```
                NO2        OH
                 |          |
   F-(arene-1)-CH2-NH-C(=O)-CH(NHR)-CH2-(arene-2)
                                            |
              [tether allowing 14-ring close]
```

Specifically: the cycloisodityrosine model — **a dipeptide N-Boc-Tyr-OMe coupled to an *ortho*-NO₂-*para*-F-phenylalanine derivative**, with the free phenol OH of Tyr being the SNAr nucleophile and the *para*-F of the activated arene being the leaving group. Macrocyclization forms a 14-membered biaryl ether ring.

Why this design:

- **14-ring matches Boger 1995's "unusually facile" 14-ring SNAr** on exactly this substrate class (DOI `10.1016/0960-894x(95)00192-v`). The chemistry is the cleanest reported in the biaryl-ether macrocyclization literature.
- **The ortho-NO₂ / para-F activation pattern is textbook for vancomycin-family SNAr.** No metal-arene complex needed.
- **Two amide bonds in the tether** create the dipeptide rigidity that promotes biaryl ether macrocyclization (Thorpe-Ingold via the amide planarity). Same effect Boger 1995 exploits.
- **Cs₂CO₃ / DMF at 25–60 °C** is the standard activator stack — among the mildest macrocyclization conditions in synthesis.
- **Generates atropisomerism**: the substituted bridge will give two atropisomers, exercising Workstream F's atropisomer-handling machinery. This is a *feature*, not a problem — it tests the stereo flag plumbing.

### 8.2 Panel files needed

```
data/validation_panel/biaryl_ether_14_cycloisodityrosine_model/
  structure.mol      # 14-membered macrocyclic biaryl ether (cycloisodityrosine analog)
  runspec.yaml       # mirrors aryl_ether_14 RunSpec, with rules: all_macrocyclization
  expected.yaml      # literature_tactic: biaryl_etherification, ring_size: 14
  notes.md           # cites Boger 1995 + Beugelmans 1994
```

### 8.3 Suggested `expected.yaml`

```yaml
literature_tactic: biaryl_etherification
literature_ring_size: 14
expected_witness: optimal
expected_top_rule_class: macrocyclization
ae_class: high
reference: |
  Cycloisodityrosine model — 14-membered biaryl ether closure of an
  ortho-nitro-para-fluoro-Phe with a Tyr OH. Mirrors Boger & Borzilleri
  1995 (DOI 10.1016/0960-894x(95)00192-v), "An unusually facile SNAr
  14-membered biaryl ether macrocyclization reaction suitable for
  preparation of the cycloisodityrosine subunit of bouvardin,
  deoxybouvardin and related agents." Activator: Cs2CO3, DMF, 25-60 C,
  no metal complexation needed. Substrate's intrinsic ortho-NO2 +
  para-F activation pattern matches the vancomycin family's SNAr
  workhorse. Designed to exercise biaryl_etherification on a smaller
  ring than the vancomycin CDE 16-rings (the harder canonical case).
```

### 8.4 Suggested `runspec.yaml`

```yaml
name: biaryl_ether_14_cycloisodityrosine_model
target:
  structure_path: structure.mol
  ring_size: 14

blocks:
  - ortho_nitro_para_fluoro_phenylalanine
  - tyrosine_dipeptide

rules: all_macrocyclization

strategy:
  max_steps: 1
  ring_close_only: true

solver:
  backend: scip
  top_n: 3
  time_budget_s: 30
  extra:
    activator: sn_ar_electron_poor_arene

energetics:
  enabled: false

notes: |
  Surrogate biaryl etherification case (14-ring biaryl ether).
  Closes via one firing of biaryl_etherification (SNAr fluoride
  on an ortho-nitro-activated arene). Cousin of aryl_ether_14
  panel; differs by sp2-aromatic alcohol partner (phenol) vs
  sp3 alcohol. Tests the SNAr "no metal" activator (cheapest
  path) and exercises atropisomer flagging.
```

### 8.5 Also update `data/rules/_index.yaml`

```yaml
sets:
  all_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification
    - biaryl_etherification    # new
    - rcm
    - transannular_diels_alder

  high_ae_macrocyclization:
    - macrolactamization
    - macrolactonization
    - aryl_etherification
    - biaryl_etherification    # new, HF byproduct (20 g/mol) — same as aryl_etherification
    - rcm
    - transannular_diels_alder

  glycopeptide_family:         # new set, suggested
    - biaryl_etherification    # for vancomycin CD/DE, K-13, OF4949, bouvardin, teicoplanin
    - macrolactamization       # for peptide backbone closures
```

---

## Section 9 — Proposed `meta.yaml` (full draft, ready to encode)

```yaml
# Biaryl etherification rule metadata (consumed by macrocert.spec.rules).
# Sibling of aryl_etherification.gml — same SNAr mechanism, same atom-map
# layout, same HF byproduct. Differs in atom-5 environment: phenolic O
# (bonded to aromatic C) instead of aliphatic alcohol O (bonded to sp3 C).
# The discrimination between the two rules is enforced at the strategy
# layer (predicate alcohol_partner_O_must_be_phenolic for this rule).
#
# Bond chemistry:
#   Ar1-F + HO-Ar2 -> Ar1-O-Ar2 + HF
#
# This rule covers the closure family that includes Boger's vancomycin
# CD and DE rings (DOI:10.1021/ja992577q, 1999), bouvardin/RA-VII
# cycloisodityrosine (DOI:10.1016/0960-894x(95)00192-v, Boger 1995),
# K-13/OF4949 (DOI:10.1021/ja970614c, Janetka-Rich 1997, Ru-arene
# variant), teicoplanin F-O-G (DOI:10.1021/jo00125a026, Zhu 1995),
# and the Beugelmans-Zhu vancomycin-model series (DOI:10.1021/jo00098a010,
# 1994).
#
# Scope INCLUDED:  SNAr (electron-poor arene with ortho-NO2 / CO2R / CN),
#                  eta6-arene-M activation (Cr or Ru), Cu Ullmann,
#                  Pd Buchwald diaryl ether.
# Scope EXCLUDED:  Oxidative phenolic coupling (separate radical/2e-
#                  mechanism, separate future rule); aryl-O-C(sp3)
#                  (see aryl_etherification.gml); biaryl Ar-Ar coupling
#                  (see future biaryl_coupling.gml).
#
# Refs (full list in refs: below):
#   - Boger et al. 1999, JACS 121:10004 (DOI:10.1021/ja992577q) —
#     vancomycin aglycon, the load-bearing primary reference.
#   - Beugelmans et al. 1994, JOC 59:5535 (DOI:10.1021/jo00098a010) —
#     first SNAr biaryl-ether macrocyclization; established ortho-NO2
#     activation as the workhorse.
#   - Zhu 1997, Synlett 133 (DOI:10.1055/s-1997-722) — SNAr biaryl-ether
#     macrocyclization review, 164 citations.

# Canonical activator: SNAr at electron-poor arene with ortho-NO2.
# = Cs2CO3 (325.82) base. (NO2 is intrinsic to the substrate, not a
# separate reagent.) DMF/DMSO solvent at 25-80 C.
# DOI:10.1021/jo00098a010, 10.1021/ja992577q
reagent_mass_g_per_mol: 326.0

# Bond-level byproduct: HF (atomic masses: F=18.998, H=1.008).
# Identical to aryl_etherification. LG alternatives (Cl, Br, NO2)
# in reagent_mass_alternatives below.
byproduct_mass_g_per_mol: 20.006

# BFS-from-1 anchor: aromatic carbon bearing the leaving group.
# Verifier walks R-side edges from atom 1; everything reachable
# is target product, the rest (atoms 2, 6 = HF) is byproduct.
retained_root_atom: 1

classes:
  - macrocyclization
  - biaryl_ether_closure
  - high_atom_economy_bond     # HF byproduct, 20 g/mol
  - glycopeptide_family        # vancomycin / teicoplanin / K-13 / OF4949 / bouvardin
  - phenolic_natural_product
  - sn_ar_compatible

# Stereo flags (per docs/biaryl_etherification_research.md §4):
# The bridge is sp2-O-sp2 — no sp3 stereocenter created or destroyed.
# Atropisomerism is the dominant stereochemical outcome: hindered
# rotation around the new C-O-C axis when ortho substituents (Cl, NO2,
# peptide side chains) are present. Thermal equilibration to the
# natural atropisomer is documented for vancomycin (Boger 1999).
stereo_flags:
  - generates_atropisomerism
  - equilibrates_atropisomer_thermally
  - retains_arene_substituents
  - no_sp3_stereocenter_at_bridge

refs:
  - "Boger, Miyazaki, Kim, Wu, Castle, Loiseleur, Jin 1999, JACS 121:10004 (DOI:10.1021/ja992577q) — vancomycin aglycon, full paper"
  - "Boger, Miyazaki, Kim, Wu, Loiseleur, Castle 1999, JACS 121:3226 (DOI:10.1021/ja990189i) — vancomycin aglycon, atropisomer equilibrations"
  - "Boger, Castle, Miyazaki, Wu, Beresis, Loiseleur 1999, JOC 64:70 (DOI:10.1021/jo980880o) — vancomycin CD/DE macrocyclization + atropisomerism"
  - "Boger, Borzilleri, Nukui, Beresis 1997, JOC 62:4721 (DOI:10.1021/jo970560p) — vancomycin CD and DE ring systems"
  - "Beugelmans, Singh, Bois-Choussy, Chastanet, Zhu 1994, JOC 59:5535 (DOI:10.1021/jo00098a010) — first SNAr biaryl-ether macrocyclization, vancomycin COD/DOE models"
  - "Zhu 1997, Synlett 1997:133 (DOI:10.1055/s-1997-722) — SNAr biaryl ether macrocyclization review (164 citations)"
  - "Boger, Borzilleri 1995, BMCL 5:1187 (DOI:10.1016/0960-894x(95)00192-v) — 14-ring SNAr biaryl ether for bouvardin cycloisodityrosine"
  - "Boger, Yohannes, Zhou, Patane 1993, JACS 115:3420 (DOI:10.1021/ja00062a004) — RA-VII / deoxybouvardin total synthesis"
  - "Janetka, Rich 1997, JACS 119:6488 (DOI:10.1021/ja970614c) — K-13 / OF4949-III via Cp*Ru η6-arene SNAr"
  - "Rao, Reddy, Rao 1994, Tet. Lett. 35:8465 (DOI:10.1016/S0040-4039(00)74434-0) — vancomycin DOE ring SNAr biphenyl ether"
  - "Aranyos, Old, Kiyomori, Wolfe, Sadighi, Buchwald 1999, JACS 121:4369 (DOI:10.1021/ja990324r) — Pd-catalyzed diaryl ethers"

# Activator alternatives — selectable per-RunSpec via solver.extra.
# Each carries its own reagent_mass + additional_byproduct.
reagent_mass_alternatives:
  - name: "SNAr_electron_poor_arene"
    reagent_mass_g_per_mol: 326.0
    additional_byproduct_mass_g_per_mol: 346.0  # CsF (152) + CsHCO3 (194)
    description: "Canonical for the vancomycin family. Substrate carries ortho-NO2 (or CO2R, CN) Meisenheimer activator + para-F LG. Cs2CO3 base, DMF, 25-80 C. NO2 is removed post-closure by reductive aromatization (Sn/HCl or H2/Pd) and replaced with H or Cl."
    refs: ["10.1021/jo00098a010", "10.1021/jo970560p", "10.1021/ja992577q"]
  - name: "SNAr_arene_Cr"
    reagent_mass_g_per_mol: 1094.0
    additional_byproduct_mass_g_per_mol: 820.0  # Cr(CO)3·L3 + spent CAN
    description: "Eta6-arene-Cr(CO)3 SNAr; Cr(CO)6 + CAN + Cs2CO3. For substrates without intrinsic activation. Atomic mass-expensive but mechanistically robust."
    refs: ["10.1002/asia.201601728"]
  - name: "SNAr_arene_Ru"
    reagent_mass_g_per_mol: 830.0
    additional_byproduct_mass_g_per_mol: 500.0  # Cp*Ru fragment + PF6
    description: "Eta6-arene-Cp*Ru SNAr; [Cp*Ru(MeCN)3]PF6 + Cs2CO3. Janetka-Rich 1997 used this for K-13/OF4949-III. Photolytic decomplexation."
    refs: ["10.1021/ja970614c"]
  - name: "Ullmann_Cu"
    reagent_mass_g_per_mol: 696.0
    additional_byproduct_mass_g_per_mol: 430.0  # CsX + CsHCO3
    description: "CuI + 1,10-phenanthroline + Cs2CO3, 100-130 C. Ar-OH + Ar-Br/I → Ar-O-Ar. Broader scope than SNAr (electron-rich arenes accessible) but rarely used for vancomycin family vs intrinsic-NO2 SNAr."
    refs: ["10.3390/catal10101103"]
  - name: "Pd_Buchwald"
    reagent_mass_g_per_mol: 1714.0
    additional_byproduct_mass_g_per_mol: 407.0  # CsBr + CsHCO3
    description: "Pd2(dba)3 + RockPhos/t-BuXPhos + Cs2CO3. Ar-OH + Ar-Br/OTf → Ar-O-Ar. Mild, broad scope; underused for natural-product macrocyclization."
    refs: ["10.1021/ja990324r"]
  # Leaving-group variants (canonical SNAr with electron-poor arene).
  - name: "SNAr_LG_Cl"
    reagent_mass_g_per_mol: 326.0
    additional_byproduct_mass_g_per_mol: 286.0  # CsCl heavier than CsF
    description: "SNAr with Cl leaving group (HCl = 36.461 g/mol byproduct). Override byproduct_mass_g_per_mol to 36.461."
    refs: ["10.1055/s-1997-722"]
  - name: "SNAr_LG_NO2"
    reagent_mass_g_per_mol: 326.0
    additional_byproduct_mass_g_per_mol: 280.0  # CsNO2
    description: "SNAr with NO2 leaving group (HNO2 = 47.013 g/mol). Used when para-NO2 is both activator and LG. Override byproduct_mass_g_per_mol to 47.013."
    refs: ["10.1055/s-1997-722"]

notes: |
  Biaryl ether (Ar-O-Ar) ring closure expelling HF. Sibling of
  aryl_etherification.gml — same SNAr mechanism, same atom-map IDs
  (1, 2, 5, 6), same bond-level byproduct (HF, 20 g/mol). Differs in
  atom-5 environment: phenolic O on an aromatic ring (sp2 neighbor)
  vs aliphatic alcohol O (sp3 neighbor).

  The discrimination between this rule and aryl_etherification is
  enforced at the strategy layer by predicate
  `alcohol_partner_O_must_be_phenolic` (vs `..._must_be_sp3` for
  aryl_etherification).

  The canonical activator for vancomycin / bouvardin / RA-VII is
  intrinsic ortho-NO2 + Cs2CO3 / DMF — the cheapest activator path
  in the whole rule library (326 g/mol). The η6-arene-M (Cr or Ru)
  variant exists for substrates whose arenes are not electron-poor
  enough for direct SNAr (e.g., K-13/OF4949 by Janetka-Rich 1997
  uses Ru).

  Stereochemistry: the bridge has NO sp3 stereocenter. Atropisomerism
  is the dominant stereo outcome — the new C-O-C axis is hindered
  by ortho substituents, giving two isolable atropisomers at room
  temperature. Boger 1999's vancomycin work demonstrates "ordered
  atropisomer equilibrations": each ring closure proceeds with a
  kinetic atropisomer preference, then equilibrates thermally
  (refluxing PhCl, hours) to the natural atropisomer.

  Vancomycin-specific note: the aglycon has THREE macrocycles —
  CD (16-membered, biaryl ether, this rule), DE (16-membered, biaryl
  ether, this rule), and AB (12-membered, biaryl Ar-Ar, future
  biaryl_coupling rule). The macrolactamization that closes the
  peptide backbone is yet a fourth closure. Vancomycin therefore
  exercises four rules across the panel; the CD and DE rings are
  this rule's responsibility.

  Chloropeptin / complestatin are vancomycin-family relatives but
  their macrocyclic closure is a macrolactamization, not a biaryl
  ether. Do NOT route those panel cases through this rule.
```

---

## Section 10 — Proposed GML structure

The proposed GML is **byte-identical to `aryl_etherification.gml`** except for the rule ID. The discrimination between phenolic and sp³ alcohol partners is enforced at the strategy layer, not in the rule body (per Option A in §2.2).

```
rule [
    ruleID "biaryl_etherification (SNAr Ar-O-Ar ring closure, -HF)"
    # L: aromatic C(1) bearing F(2) and phenolic O(5)-H(6).
    # Atom IDs match aryl_etherification (1, 2, 5, 6). The discrimination
    # vs aryl_etherification is that atom 5 must be bonded to an aromatic
    # C in the substrate (enforced by strategy predicate
    # `alcohol_partner_O_must_be_phenolic`, not by the rule body).
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
    # R: Ar(1)-O(5)-Ar' biaryl ether plus expelled HF (atoms 2, 6).
    right [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
    ]
]
```

**Key sections (identical to `aryl_etherification.gml`):**

- **`left`**: declares atoms F(2) and H(6) (the "to-be-expelled" pair) and the two bonds that break (Ar–F at 1–2 and phenol O–H at 5–6).
- **`context`**: declares the two atoms whose identity is preserved — aromatic C (1) and phenolic O (5). They bond to different partners across L → R but the atoms themselves are conserved.
- **`right`**: declares the new Ar(1)–O(5) biaryl ether bond and the new H(2)–F(6) bond of expelled HF.

**Variants** (per-LG; lives in `reagent_mass_alternatives`, not separate GML files):

- LG = Cl: `node [ id 2 label "Cl" ]`. Byproduct HCl, 36.461 g/mol.
- LG = Br: `node [ id 2 label "Br" ]`. Byproduct HBr, 80.912 g/mol.
- LG = NO₂: more complex (multi-atom LG) — handle in a strategy expansion, not as a single-node substitution.

**Recommendation: keep F as the canonical LG in the GML body.** Workstream D's `expand_leaving_groups` strategy predicate handles the alternative LGs, and the verifier recomputes byproduct mass from the actual element of atom 2 in the composed rule.

**Verifier sanity checks (identical to `aryl_etherification`):**

- BFS from `retained_root_atom: 1` reaches atoms 1, 5 (the Ar–O–Ar bridge). Does not reach atoms 2, 6. ✓
- Mass balance: 2 bonds broken (1–2, 5–6), 2 bonds formed (1–5, 2–6). Atoms conserved. ✓
- Byproduct mass: M(F) + M(H) = 18.998 + 1.008 = **20.006 g/mol**. ✓

---

## Open questions / followups for Ivan

1. **Routing predicate between the two rules.** Workstream D must add `alcohol_partner_O_must_be_phenolic` (this rule) and `alcohol_partner_C_must_be_sp3` (`aryl_etherification`). Without these the verifier will fire both rules on any substrate with an OH + Ar–F pair, and the panel discrimination breaks. This is the load-bearing follow-up.

2. **Vancomycin CDE panel case.** Workstream B's `B-validation-panel.md` should move vancomycin from `macrolactamization` to `biaryl_etherification` (specifically: CD and DE rings) and add the AB ring as a future `biaryl_coupling` case + a separate macrolactamization case for the peptide backbone. Vancomycin is now correctly understood as a **4-tactic target**.

3. **Atropisomer handling in M5/M6.** The `equilibrates_atropisomer_thermally` flag is new. Workstream F's stereo machinery should decide whether (a) accept both atropisomers as M5 outputs and compare via `chemistry-equivalent`, or (b) explicitly enumerate the thermal-equilibration step as a post-closure transformation. Recommend (a) for M5 (simpler); revisit for M6.

4. **Chloropeptin/complestatin reclassification.** These are NOT biaryl-ether macrocyclization targets despite being vancomycin-family. Their ring-defining closure is a macrolactamization with the biaryl/indole-aryl bonds pre-installed. Note this in the panel docs.

5. **Beugelmans 1994 corrections to upstream brief.** The task brief stated Beugelmans 1994 used η⁶-arene-Cr SNAr. **Correction**: Beugelmans 1994's actual chemistry is *intrinsic-NO₂ activation*, not Cr complexation. The Cr-arene variant is Uchiro 2017 (GKK1032A₂, alkyl-aryl) and the Ru-arene variant is Janetka-Rich 1997 (K-13/OF4949, biaryl). Beugelmans-Zhu used metal-free SNAr throughout the 1994/1996/1997 papers.

6. **Per-ring atropisomer pre-disposition.** The CD-ring kinetic atropisomer preference differs from the DE-ring preference (Boger 1999). If MØD-MacroCert ever encodes thermodynamic vs kinetic enumeration of macrocyclization products, the per-substrate kinetic preference is encoded in the substrate 3D geometry — not a rule attribute. Leave as substrate metadata.

---

## Cross-references in the vault

- [[Boger Miyazaki Kim Wu Castle Loiseleur Jin 1999 - Vancomycin Aglycon Total Synthesis]] — primary reference (`10.1021/ja992577q`)
- [[Boger Miyazaki Kim Wu Loiseleur Castle 1999 - Vancomycin Aglycon Atropisomer Equilibrations]] — atropisomer equilibrations communication (`10.1021/ja990189i`)
- [[Boger Castle Miyazaki Wu Beresis Loiseleur 1999 - Vancomycin CD DE Macrocyclization Atropisomerism]] — full atropisomer study (`10.1021/jo980880o`)
- [[Boger Borzilleri Nukui Beresis 1997 - Vancomycin CD DE Ring Systems]] — CD/DE ring synthesis details (`10.1021/jo970560p`)
- [[Beugelmans Singh Bois-Choussy Chastanet Zhu 1994 - SNAr Vancomycin Models]] — first SNAr biaryl-ether macrocyclization (`10.1021/jo00098a010`)
- [[Beugelmans Bois-Choussy Vergne Bouillon Zhu 1996 - Vancomycin CODOE Double SNAr]] — double SNAr bicyclic model (`10.1039/CC9960001029`)
- [[Zhu 1997 - SNAr Macrocyclization Biaryl Ether]] — field-defining review (`10.1055/s-1997-722`)
- [[Boger Borzilleri 1995 - SNAr Biaryl Ether Macrocyclization Bouvardin]] — 14-ring SNAr precedent (`10.1016/0960-894x(95)00192-v`)
- [[Boger Yohannes Zhou Patane 1993 - RA-VII Deoxybouvardin Cycloisodityrosine Total Synthesis]] — RA-VII / deoxybouvardin full paper (`10.1021/ja00062a004`)
- [[Janetka Rich 1997 - K-13 OF4949 SNAr Ruthenium Arene Macrocyclization]] — Ru-arene SNAr variant (`10.1021/ja970614c`)
- [[Garfunkle Kimball Trzupek Takizawa Shimamura Tomishima Boger 2009 - Chloropeptin II Complestatin Total Synthesis]] — chloropeptin/complestatin (`10.1021/ja907193b`)
- [[Rao Reddy Rao 1994 - Vancomycin DOE Biphenyl Ether Macrocyclisation]] — independent DOE ring synthesis (`10.1016/S0040-4039(00)74434-0`)
- [[Sugata Inagaki Ode Hayakawa Karoji Baba Kato Hasegawa Tsubogo Uchiro 2017 - GKK1032A2 SNAr Chromium Macrocyclization]] — sibling rule's canonical (Cr-arene SNAr, alkyl-aryl) (`10.1002/asia.201601728`)
- [[Research - Macroetherification Chemistry - 2026-05-24]] — the sibling rule's research brief
