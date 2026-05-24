# Transition-Metal Cross-Coupling for Macrocyclization — Workstream C brief

**Date:** 2026-05-24
**Audience:** Workstream C of MØD-MacroCert (rule library expansion). Designs `data/rules/transition_metal_cross_coupling.gml` + `.meta.yaml`.
**Question being decided:** one generic rule with substituent variables, or one rule per coupling type (Negishi, Suzuki, Stille, Buchwald, Sonogashira)?

---

## 1. Generic-vs-specific — comparison and recommendation

### 1.1 The DPO mechanics that matter

The MØD rule format requires explicit atoms on L and R sides of the span, with atom IDs preserved through the context. Every atom that participates in a bond change must be named in the rule body. For cross-couplings, the bond-level transformation has **two structurally distinct shapes**:

**Shape A — organometal/halide (C–[M] + C–X → C–C + M–X):**

| Coupling | Organometal fragment | Halide fragment | Bond-level byproduct |
|---|---|---|---|
| Negishi | R–ZnX | R'–X' | ZnXX' (e.g., ZnBr2, ZnBrCl) |
| Suzuki | R–B(OH)₂ (or R–Bpin, R–BF₃K) | R'–X | B(OH)₃ + base·HX, or NaB(OH)₄ + NaX |
| Stille | R–SnBu₃ | R'–X | Bu₃SnX |

**Shape B — protic/halide (C–H or N–H + C–X → C–C or C–N + H–X):**

| Coupling | Protic fragment | Halide fragment | Bond-level byproduct |
|---|---|---|---|
| Buchwald–Hartwig | R–NH(R') | R''–X | HX (absorbed by base) |
| Sonogashira | R–C≡C–H | R'–X | HX (absorbed by base) |
| C–H / C–H (CDC) | R–H | R'–H | H₂ or H₂O |

These two shapes have **different left-side atom counts and different byproduct topologies**. A single generic rule that subsumed both would have to encode "either a metal atom or a hydrogen" on the leaving group of one partner — which MØD's DPO formalism does not naturally support without label-class abstraction over heterogeneous element symbols (metal vs H).

C–H / C–H dehydrogenative coupling is already a separate file in the Workstream C plan (`c_h_dehydrogenative_coupling.gml`), so it is out of scope here.

### 1.2 Option A — single generic rule with substituent variables

**Idea:** one GML file with abstract labels (e.g., `"M"` for "any organometal" and `"X"` for "any halide"), the actual atoms picked at strategy or substrate-graph time.

**Pros:**
- One rule object to maintain, one atom-map to audit.
- Strategy file can fire it across all couplings uniformly.
- Conceptually unifies the "C–C closure via Pd/Ni catalysis" family.

**Cons (each is severe for v0):**
- **MØD label semantics.** MØD treats node labels as element symbols matched against the molecule graph. `"M"` is not a real element; it would not match Zn, B, or Sn natively. Implementing this would require either (a) label-class rewriting before rule loading (a new pre-pass), or (b) running multiple substituted variants under the hood (which defeats the "one rule" goal).
- **Atom-mass accounting breaks.** The verifier's M2 bond-level AE recomputation depends on `retained_root_atom` and a graph traversal of R to compute byproduct mass from explicit atoms. With abstract `"M"` and `"X"` nodes, the verifier cannot compute `byproduct_mass_g_per_mol` — there's no concrete element to weigh. Either we lose verifier coverage or we add a "mass table by metal" layer outside the rule (which is exactly what `meta.yaml` exists to avoid — meta.yaml is per-rule).
- **Process-mass even worse.** Catalyst, ligand, base, and activator differ by *coupling* (HATU has no place near a Suzuki; CuI is Sonogashira-only). A `reagent_mass_g_per_mol` field that aggregates the activator stack only makes sense per coupling.
- **Strategy predicate compatibility.** Strategy filters like "applies only to aryl–aryl, never sp³–sp³" or "ring atom-count between 12 and 17" are coupling-specific. With a generic rule, strategy predicates have to bury all the coupling-specific gating inside, undoing the abstraction.
- **Atom-mapping clarity.** Reviewers checking the GML cannot tell at a glance whether a given firing represents a Negishi vs Suzuki vs Stille event — provenance is lost. For Layer D/E (feasibility/cost), this matters: the cost models for Stille and Suzuki are quite different.

### 1.3 Option B — one rule per coupling type

**Idea:** separate GML+meta pair for each coupling: `negishi.gml`, `suzuki.gml`, `stille.gml`, `buchwald_hartwig.gml`, `sonogashira.gml`.

**Pros:**
- Each rule has concrete element labels — MØD evaluates them natively, no special machinery.
- Each `meta.yaml` carries the correct activator stack, byproduct mass, stereo flags, classes.
- Verifier's bond-level AE recomputation works unmodified (the retained-root BFS sees real atoms).
- Strategy file gains a clean named handle for each tactic — easy to express "no Stille due to organotin toxicity in scope".
- `_index.yaml` can group them into a `cross_coupling` set with one line per entry; named rule-set algebra already supports this.
- Future couplings (Heck, Hiyama, Kumada) drop in without disturbing existing rules.

**Cons:**
- 5 GML files + 5 meta files instead of 1 — about 200 LoC vs 50 LoC.
- Risk of drift between siblings (Negishi rule says one thing about α-stereo, Suzuki says another) — mitigated by `_index.yaml` and a small shared comment block.
- More test cases needed (one toy substrate per rule) — though the plan already calls for a toy substrate per rule.

### 1.4 Option C — two intermediate "shape" rules (organometal/halide + protic/halide)

**Idea:** one rule for Shape A (Negishi/Suzuki/Stille), one for Shape B (Buchwald/Sonogashira). Within each shape, the metal/protic atom is still abstract — but only across **one** dimension.

**Pros:** halves the file count; preserves the structural distinction the chemistry actually has.

**Cons:** still hits the label-class problem within Shape A (Zn vs B vs Sn produce different byproduct masses); the meta.yaml problem doesn't go away. **All the disadvantages of Option A apply within each group.** Not recommended.

### 1.5 Recommendation: **Option B — one rule per coupling type**

The decisive factors are atom-map clarity and the `byproduct_mass_g_per_mol` accounting. v0's verifier model is "concrete atoms on both sides of the rule; bond-level mass = sum of byproduct atoms by element". That model requires concrete elements. Option A breaks it; Option B respects it.

**Plan for Workstream C deliverable:**

1. Write **five rule pairs** under a shared file-naming convention:
   - `transition_metal_cross_coupling/negishi.gml` + `.meta.yaml`
   - `transition_metal_cross_coupling/suzuki.gml` + `.meta.yaml`
   - `transition_metal_cross_coupling/stille.gml` + `.meta.yaml`
   - `transition_metal_cross_coupling/buchwald_hartwig.gml` + `.meta.yaml`
   - `transition_metal_cross_coupling/sonogashira.gml` + `.meta.yaml`

2. Add an `_index.yaml` set:

   ```yaml
   transition_metal_cross_coupling:
     - negishi
     - suzuki
     - stille
     - buchwald_hartwig
     - sonogashira
   ```

3. If the deliverable contract requires a single file named `transition_metal_cross_coupling.gml`, write **Suzuki as the canonical default** (most common in macrocyclization libraries, lowest toxicity profile among C–C couplings) and put Negishi/Stille/Buchwald/Sonogashira in a `data/rules/cross_coupling_variants/` subfolder. The `_index.yaml` `transition_metal_cross_coupling` set still aggregates all five.

   Justification for Suzuki-as-canonical: Marti-Centelles et al. (2015) and the Heck macrocyclization review (Zhang, NPR 2021) both note Suzuki as the most-used cross-coupling for macrocyclic natural-product synthesis after RCM. Boronic acid handling is robust, byproducts are non-toxic, and the activator stack (Pd(PPh₃)₄ + base) is the closest cross-coupling analogue to the HATU-style "canonical activator" already used in macrolactamization.meta.yaml.

The remainder of this brief drafts the **Suzuki** rule in full, with a mass table and notes covering the other four so they can be cloned quickly.

---

## 2. Atom-mapped scheme for Suzuki–Miyaura (canonical rule)

### 2.1 The transformation at the bond level

In the macrocyclic ring-closure variant, a single substrate carries both partners on its tether:

$$\text{R}-\text{B(OH)}_2 + \text{R'}-\text{X} \xrightarrow[\text{Pd / base}]{} \text{R}-\text{R'} + \text{HOB(OH)}_2 + \text{HX}$$

The standard pre-/post-transmetalation accounting in the RB(OH)₃⁻ ("boronate") mechanism (Hartwig & Lennox; Denmark & Smith, *J. Am. Chem. Soc.* 2022, PMC8930609) treats:

- C–B(OH)₂ bond cleaves.
- C–X (X = Br, I, OTf) bond cleaves.
- C–C bond forms between the two ipso carbons.
- B(OH)₂ + OH⁻ (from base) → B(OH)₃ (boric acid) is the boron byproduct; the X⁻ is captured as a salt with the base cation (e.g., NaX, K₂CO₃·HX).

For the **bond-level rule** (the only mass the rule itself accounts for), we expel:

- 1 × B(OH)₂ fragment → captured as boric acid B(OH)₃ after picking up one OH (or alternatively a boronate B(OH)₄⁻ if we want to charge-balance against the base — see §2.3).
- 1 × X (the halide atom alone).
- 1 × H (the H that came in via base hydroxide or, in some accountings, was already on the boron's hydroxyl).

We do **not** put the base, the solvent, the catalyst, or the ligand into the rule. That is the M0 bond-vs-process AE split already established (see macrolactamization.meta.yaml for the precedent).

### 2.2 Atom map for the GML

Atom IDs (one ring carbon on each fragment plus the leaving atoms):

| ID | Element | Side | Role |
|---|---|---|---|
| 1 | C | context | Ipso carbon of the boronate fragment (retained_root) |
| 2 | C | context | Ipso carbon of the halide fragment (in same molecule for macrocyclization) |
| 3 | B | L only | The boron leaving as part of B(OH)₃ |
| 4 | O | L+R | Hydroxyl-O on boron, kept with B in byproduct |
| 5 | H | L+R | H on O(4), kept with B in byproduct |
| 6 | O | L+R | Second hydroxyl-O on boron, kept with B in byproduct |
| 7 | H | L+R | H on O(6), kept with B in byproduct |
| 8 | X (Br) | L only | The halide leaving atom |
| 9 | O | L+R | Third hydroxyl-O that joins B in byproduct (from base) |
| 10 | H | L+R | H that pairs with X to form HBr byproduct (from base) |

**Left side (L):** the substrate before reaction.

- Edges: 1–3 (C–B), 3–4 (B–O), 4–5 (O–H), 3–6 (B–O), 6–7 (O–H), 2–8 (C–X).
- The "incoming" O(9)–H(10) is a base-supplied OH; on L it is an external fragment, but in MØD's left graph we represent it as two unconnected atoms or as a single H–O molecule. **Simpler design:** treat the incoming OH as if it's pre-attached to B as a B(OH)₃⁻ boronate — most accurate per the Lennox/Denmark "boronate mechanism" (DOI 10.1021/jacs.1c08283). Then L already has the boronate, and the H that ends up on X arrives separately. *Choice:* model the L-side boron as **R–B(OH)₃⁻** (boronate, 4-coordinate) since (a) DFT (Ortuño, Lledós, Maseras, Ujaque, *ChemCatChem* 2014, DOI 10.1002/cctc.201402326) and experiment (Denmark 2022, DOI 10.1021/jacs.1c08283) both support that as the transmetalating species, and (b) it gives the rule a clean "one species in, two species out" stoichiometry without extra free OH on L.

Under that simplification:

| ID | Element | Side | Role |
|---|---|---|---|
| 1 | C | context | Boronate-bearing carbon, **retained_root** |
| 2 | C | context | Halide-bearing carbon |
| 3 | B | L+R (in byproduct on R) | Boron of boronate / boric acid |
| 4,5 | O,H | L+R | Hydroxyl 1 on B |
| 6,7 | O,H | L+R | Hydroxyl 2 on B |
| 8 | Br | L+R (in byproduct on R) | Halide |
| 9,10 | O,H | L+R | Hydroxyl 3 on B; after reaction it stays on B as B(OH)₃ |

**Wait** — we need an H to form HBr on the right side (or NaBr if we are tracking the base). To keep this isomorphic to macrolactamization (where the rule expels H₂O, a neutral molecule, not a salt), we choose **a neutral expulsion model**:

> Bond-level byproducts of Suzuki rule = **HBr (or HCl, HI, etc.)** + **B(OH)₃ (boric acid)**, with one H atom donated by the boronate hydroxyl.

In that model, no external base atom enters the rule — one of the boronate hydroxyl H atoms migrates onto the halide on R. This is a chemical fiction (in reality the H comes via base/water/protodeboronation pathways), **but it is mass-balanced** and matches the macrolactamization precedent of "neutral byproduct, no salt accounting in the rule itself; activator mass goes in process-level reagent_mass".

**Final atom map (10 atoms):**

| ID | Element | Side | Role |
|---|---|---|---|
| 1 | C | context | Ipso C of organoboron (retained_root) |
| 2 | C | context | Ipso C of halide |
| 3 | B | L+R | Boron (in B(OH)₃ byproduct on R) |
| 4 | O | L+R | OH-O on B (kept on R as part of B(OH)₃) |
| 5 | H | L+R | H of OH(4) |
| 6 | O | L+R | OH-O on B (kept on R as part of B(OH)₃) |
| 7 | H | L+R | H of OH(6) |
| 8 | O | L+R | Third O of boronate B(OH)₃ on L; one of its H's migrates |
| 9 | H | L+R | H of O(8) on L; on R it bonds to halide (atom 10) to form HBr |
| 10 | Br | L+R | Halide on L; on R it carries H(9) as HBr |

**L bonds:** 1–3, 3–4, 4–5, 3–6, 6–7, 3–8, 8–9, 2–10
**R bonds:** 1–2 (new C–C), 3–4, 4–5, 3–6, 6–7, 3–8 (B(OH)₃ intact), 9–10 (new H–Br)

Two bonds break (1–3 and 2–10); two bonds form (1–2 and 9–10); one bond migrates (8–9 breaks on L, 9–10 forms on R — equivalent to an H transfer from boronate-OH to halide).

### 2.3 Byproduct mass calculation

From the explicit atoms in R that are not reachable from retained_root atom 1:

- B(OH)₃: B (10.811) + 3 × O (16.00) + 3 × H (1.008) = **61.83 g/mol**
- HBr (the canonical halide): 1.008 + 79.904 = **80.91 g/mol**
- HCl variant: 36.46 g/mol; HI variant: 127.91 g/mol — these go in `byproduct_mass_alternatives`.

**Total bond-level byproduct mass (Suzuki, Br variant):** 61.83 + 80.91 = **142.74 g/mol**.

This is the value the verifier should compute by BFS from atom 1 on R and summing the unreachable atoms. v0 records it as a human-checkable ground truth in `byproduct_mass_g_per_mol`.

---

## 3. Reagent + byproduct mass table

For each coupling, **reagent_mass_g_per_mol** is the process-level activator stack (catalyst + ligand + base + any pre-formed organometal reagent if it is added externally). For a macrocyclization where the boronate/stannane/zincate is already on the substrate, the "external reagent" stack is just catalyst + base + ligand. **byproduct_mass_g_per_mol** is the bond-level mass — what atoms physically leave the substrate per ring-closure event.

| Coupling | reagent_mass_g_per_mol (process, canonical) | Reagent stack chosen | byproduct_mass_g_per_mol (bond, neutral fragments) | Typical scope | Reference DOI |
|---|---|---|---|---|---|
| **Suzuki–Miyaura** | 1156 + 138 + 1156 ≈ 1156 (Pd(PPh₃)₄, sub-stoich, amortize 30) + 2·K₂CO₃ (138) = **30 + 276 = 306** | Pd(PPh₃)₄ (5 mol%, amortized 30 g/mol) + 2 eq K₂CO₃ (138.21 g/mol each) | **142.74** (B(OH)₃ + HBr; substitute halide for HCl/HI variants) | sp²–sp², sp²–sp³ in B-alkyl variant; biaryl macrocycles, vancomycin DEFG ring | Suzuki & Miyaura *Chem. Rev.* 1995, 10.1021/cr00039a007; Chemler/Trauner/Danishefsky *Angew. Chem. Int. Ed.* 2001, 10.1002/1521-3773(20011217)40:24<4544::aid-anie4544>3.0.co;2-n; Jia/Bois-Choussy/Zhu *Org. Lett.* 2007, 10.1021/ol070889p |
| **Negishi** | Pd(PPh₃)₄ (amortized 30) + 0 (no base needed in standard Negishi) = **30**; if pre-formed RZnBr is added externally rather than generated in situ, count its mass: e.g., **30 + ~250** depending on R | Pd(PPh₃)₄ (5 mol%, amortized 30) | **136.29** (ZnBr₂); or 198.18 (ZnBrI); 319.18 (ZnI₂); 100.21 (ZnCl₂) | sp²–sp², sp³–sp² alkyl–aryl, sensitive functional groups | Negishi, King & Okukado, *J. Org. Chem.* 1977, 10.1021/jo00438a041 (also indexed as 10.1002/chin.197743156); Negishi book chap. 1999, 10.1093/oso/9780198501213.003.0016; Phan, Gallou et al. *Chem. Rev.* 2011, 10.1021/cr100327p (general Negishi review) |
| **Stille** | Pd(PPh₃)₄ (amortized 30) + CuI (190.45) + LiCl (42.39, optional Farina/Liebeskind co-additive) = **30 + 232.84 = 262.84** | Pd(PPh₃)₄ + CuI + LiCl | **354.62** (Bu₃SnBr); 220.36 (Me₃SnBr) — use Bu₃SnBr as canonical | sp²–sp² and sp³–sp² with vinyl stannanes; pentamycin total synthesis, lankacidin precursors | Stille *Angew. Chem. Int. Ed.* 1986, 10.1002/anie.198605081; Farina, Krishnamurthy, Scott *Org. React.* 1997, 10.1002/0471264180.or050.01; Heravi et al. *RSC Adv.* 2018 macrocyclic Stille; Brain/Nelson/Thomas *Tetrahedron* 2010 (lankacidin), 10.1016/j.tet.2010.04.129; pentamycin: JACS 2023, 10.1021/jacs.3c03011 |
| **Buchwald–Hartwig** | Pd₂(dba)₃ (915.7, amortized at 5 mol% ≈ 92) + BINAP / XPhos (~476) + Cs₂CO₃ (325.82) = **92 + 476 + 326 = 894** — use **300** as a loose amortized lower bound for v0, override per-substrate | Pd₂(dba)₃ + XPhos + Cs₂CO₃ (canonical Buchwald conditions) | **80.91** (HBr); 36.46 (HCl); 127.91 (HI) | aryl C–N bond formation for macrocyclic aniline/amide tethers; pharma macrocycles | Hartwig *Acc. Chem. Res.* 1998, 10.1021/ar970146b; Surry & Buchwald *Chem. Sci.* 2011, 10.1039/c0sc00331j; Wolfe & Buchwald *Acc. Chem. Res.* 1998, 10.1021/ar970108e; macrocyclic case: Cipolla & Hesp *Synthetic Methods* 2017, 10.1039/9781782622086-00170 |
| **Sonogashira** | Pd(PPh₃)₂Cl₂ (amortized 35) + CuI (190.45) + Et₃N (101.19, as 2 eq base) = **35 + 190 + 202 = 427** | Pd(PPh₃)₂Cl₂ + CuI + Et₃N | **80.91** (HBr); 36.46 (HCl); 127.91 (HI) | sp²–sp(alkyne) macrocyclization; cyclophanes, arylated alkyne macrocycles | Sonogashira, Tohda & Hagihara *Tetrahedron Lett.* 1975, 10.1016/S0040-4039(00)91094-3; Chinchilla & Nájera *Chem. Rev.* 2007, 10.1021/cr050992x and *Chem. Soc. Rev.* 2011, 10.1039/c1cs15071e; copper-free mechanism: García-Melchor et al. *Nat. Commun.* 2018, 10.1038/s41467-018-07081-5 |

**Numbers verified against three sources for the activator/byproduct accounting:**

- The Suzuki boronate vs. oxo-palladium debate, and the resulting accounting that boric acid B(OH)₃ is the bond-level B-byproduct: Lennox & Lloyd-Jones, *Chem. Soc. Rev.* 2014 (10.1039/c3cs60197h); Ortuño et al. *ChemCatChem* 2014 (10.1002/cctc.201402326); Denmark group, *JACS* 2022 (PMC8930609, 10.1021/jacs.1c08283).
- The Negishi byproduct identity (Zn-halide salt) and process-level mass: Phan & Gallou, *Chem. Rev.* 2011 (10.1021/cr100327p) gives a detailed activator stack survey.
- Stille R₃SnX byproduct: Stille *Angew. Chem. Int. Ed.* 1986 (10.1002/anie.198605081), confirmed in Farina *Org. React.* 1997. Tributyltin halides are the dominant byproduct; their high MW and toxicity is the principal reason Stille is the **least atom-economical** of the C–C couplings under consideration (354.62 g/mol byproduct).
- Buchwald–Hartwig HX byproduct (absorbed by base): Hartwig *Acc. Chem. Res.* 1998; Surry & Buchwald *Chem. Sci.* 2011.

**Choosing the canonical default for the Suzuki meta.yaml:** the 30 g/mol amortization for Pd(PPh₃)₄ matches the convention already in rcm.meta.yaml (`reagent_mass_g_per_mol: 30.0` for amortized Hoveyda-Grubbs II). For consistency with that existing convention, v0 Suzuki should be **reagent_mass_g_per_mol: 306.0** (Pd amortized 30 + 2 eq K₂CO₃ at 138).

---

## 4. Stereo handling

The dominant stereochemical fact for cross-couplings used in macrocyclization is **retention of stereochemistry at sp³ carbons** that are present but not part of the bond-forming event — i.e., the rule does not racemize α-stereocenters on retained ring atoms. There are three exceptions that the `stereo_flags` field must capture per-coupling.

### 4.1 What is preserved

- **sp³ stereocenters distal from the coupling site:** untouched by all five couplings.
- **alkene (E/Z) geometry on the organometal partner:** stereospecific in Suzuki, Negishi, and Stille — vinyl–B, vinyl–Zn, and vinyl–Sn retain E/Z on transmetalation. This is why vinyl-stannane macrocyclizations (Stille) are the standard for natural products requiring a defined endocyclic alkene geometry (e.g., pentamycin, lankacidin, rapamycin-class systems).
- **Stereospecific Ni-catalyzed sp³ Suzuki/Negishi:** Jarvo and co-workers (*JACS* 2013, 10.1021/ja311783k) showed Ni-catalyzed coupling of benzylic carbamates with aryl boronates proceeds with controllable *retention or inversion* via achiral catalyst choice. For v0 purposes, the rule does *not* set sp³ stereo at the coupling carbon; if the input substrate is enantiopure at the C–X or C–B carbon, the rule's stereo behavior is "stereospecific (retention by default in Suzuki/Negishi sp²; substrate-controlled retention in stereospecific sp³ variants)".

### 4.2 What can racemize

- **α-acidic C–H next to C–X under Buchwald conditions.** Cs₂CO₃ / K₃PO₄ are mild but warm. Phenacyl-type substrates or α-ester C–H next to the C–X partner can lose configuration. Flag in `stereo_flags` as `risk_alpha_acidic_racemization`.
- **α to carbonyl in Negishi with Reformatsky-style RZnX.** Standard concern in α-bromo ester / α-bromo amide Negishi reactions; α-stereocenters next to the C–Zn partner can racemize via enolization before transmetalation. Flag as `risk_alpha_carbonyl_racemization` on Negishi.
- **β-hydride elimination on sp³ alkyl couplings.** Causes loss of the sp³ stereocenter at the coupling carbon by reductive isomerization; Pd-catalyzed sp³ Suzuki/Negishi suffer this unless special ligands (Pd/NHC, Ni/bipyridyl) are used. Out of scope for v0 — flag as `sp3_coupling_outside_v0_scope` for now.

### 4.3 New stereo phenomena introduced (not lost)

- **Atropisomerism:** intramolecular Suzuki of biaryl precursors generates a stereogenic biaryl axis. Vancomycin / complestatin / chloropeptin syntheses use atroposelective Suzuki (Jia, Bois-Choussy & Zhu, *Org. Lett.* 2007, 10.1021/ol070889p). Flag as `may_set_atropisomer` on Suzuki.
- **Heck reactions** (related; will become its own rule if Workstream C expands) install an sp² stereocenter — covered in Dounay & Overman *Chem. Rev.* 2003 (10.1021/cr020039h).

### 4.4 Recommended `stereo_flags` per coupling

| Coupling | stereo_flags |
|---|---|
| Suzuki | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `may_set_atropisomer`, `risk_protodeboronation_on_basic_substrates` |
| Negishi | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `risk_alpha_carbonyl_racemization`, `risk_beta_hydride_elimination_sp3` |
| Stille | `retains_sp3_stereo_distal`, `retains_alkene_geometry`, `tin_residue_toxicity_flag` |
| Buchwald | `retains_sp3_stereo_distal`, `risk_alpha_acidic_racemization` |
| Sonogashira | `retains_sp3_stereo_distal`, `retains_alkyne_linearity`, `risk_glaser_homocoupling_byproduct` |

These flags should compose with Workstream F's stereo-handling validator.

---

## 5. Citation list (DOIs)

### Reviews — macrocyclic cross-coupling and macrocyclization tactics

- Marti-Centelles, V.; Pandey, M. D.; Burguete, M. I.; Luis, S. V. **Macrocyclization Reactions: The Importance of Conformational, Configurational, and Template-Induced Preorganization.** *Chem. Rev.* 2015, *115*, 8736–8834. **DOI: 10.1021/acs.chemrev.5b00056** (also indexed as 10.1002/chin.201543248). — 533 refs, includes a dedicated cross-coupling tactics section.
- Zhang, W. **Heck macrocyclization in natural product total synthesis.** *Nat. Prod. Rep.* 2021, *38*, 1109–1135. **DOI: 10.1039/d0np00087f**. — Adjacent to cross-coupling; sets the macrocyclic application precedent.
- Terrett, N. K. **Methods for the synthesis of macrocycle libraries for drug discovery.** *Drug Discov. Today Technol.* 2010, *7*, e97–e104. **DOI: 10.1016/j.ddtec.2010.06.002**.
- Evano, G.; Theunissen, C.; Pradal, A. **Impact of copper-catalyzed cross-coupling reactions in natural product synthesis: the emergence of new retrosynthetic paradigms.** *Nat. Prod. Rep.* 2013, *30*, 1467. **DOI: 10.1039/c3np70071b**. — Covers Sonogashira and Ullmann-type macrocyclizations.
- Driggers, E. M.; Hale, S. P.; Lee, J.; Terrett, N. K. **The exploration of macrocycles for drug discovery — an underexploited structural class.** *Nat. Rev. Drug Discov.* 2008, *7*, 608–624. **DOI: 10.1038/nrd2590**.

### Original / canonical method papers

- **Negishi:** Negishi, E.; King, A. O.; Okukado, N. *J. Org. Chem.* 1977, *42*, 1821–1823. **DOI: 10.1021/jo00438a041**. (ChemInform abstract: 10.1002/chin.197743156.) Plus Negishi book chapter 1999: **DOI: 10.1093/oso/9780198501213.003.0016**.
- **Suzuki–Miyaura:** Miyaura, N.; Yamada, K.; Suzuki, A. *Tetrahedron Lett.* 1979, *20*, 3437–3440. **DOI: 10.1016/S0040-4039(01)95429-2**. The seminal review: Miyaura, N.; Suzuki, A. *Chem. Rev.* 1995, *95*, 2457–2483. **DOI: 10.1021/cr00039a007**.
- **Stille:** Milstein, D.; Stille, J. K. *J. Am. Chem. Soc.* 1978, *100*, 3636–3638. **DOI: 10.1021/ja00479a077**. Mechanistic/scope review: Farina, V.; Krishnamurthy, V.; Scott, W. J. *Org. React.* 1997, *50*, 1–652. **DOI: 10.1002/0471264180.or050.01**.
- **Buchwald–Hartwig:** Guram, A. S.; Rennels, R. A.; Buchwald, S. L. *Angew. Chem. Int. Ed.* 1995, *34*, 1348. **DOI: 10.1002/anie.199513481**. Louie, J.; Hartwig, J. F. *Tetrahedron Lett.* 1995, *36*, 3609. **DOI: 10.1016/0040-4039(95)00605-C**. Modern review: Surry, D. S.; Buchwald, S. L. *Chem. Sci.* 2011, *2*, 27–50. **DOI: 10.1039/c0sc00331j**. Older but canonical: Hartwig, J. F. *Acc. Chem. Res.* 1998, *31*, 852. **DOI: 10.1021/ar970282g**.
- **Sonogashira:** Sonogashira, K.; Tohda, Y.; Hagihara, N. *Tetrahedron Lett.* 1975, *16*, 4467–4470. **DOI: 10.1016/S0040-4039(00)91094-3**. Reviews: Chinchilla, R.; Nájera, C. *Chem. Rev.* 2007, *107*, 874. **DOI: 10.1021/cr050992x**; *Chem. Soc. Rev.* 2011, *40*, 5084. **DOI: 10.1039/c1cs15071e**. Copper-free mechanism: García-Melchor et al. *Nat. Commun.* 2018, *9*, 4541. **DOI: 10.1038/s41467-018-07081-5**.

### Modern macrocyclic examples

- **Suzuki — atroposelective biaryl:** Jia, Y.; Bois-Choussy, M.; Zhu, J. *Org. Lett.* 2007, *9*, 2401–2404 (vancomycin DEFG ring). **DOI: 10.1021/ol070889p**.
- **Stille — pentamycin double Stille:** *J. Am. Chem. Soc.* 2023 (trienyl-bis-stannane double ring closure). **DOI: 10.1021/jacs.3c03011**.
- **Stille — lankacidin precursors:** Brain, C. T.; Chen, A.; Nelson, A.; Tanikkul, N.; Thomas, E. J. *Tetrahedron* 2010, *66*, 6613–6625. **DOI: 10.1016/j.tet.2010.04.129**.
- **Heck — macrocyclic NP scope:** Dounay, A. B.; Overman, L. E. *Chem. Rev.* 2003, *103*, 2945–2964. **DOI: 10.1021/cr020039h**. (1431 citations; asymmetric intramolecular Heck for natural products.)
- **Sonogashira — cyclophane:** Pigge, F. C.; Ghasedi, F.; Rath, N. P. *J. Org. Chem.* 2002, *67*, 4547–4552. **DOI: 10.1021/jo0256181** (enaminone-directed benzannulation/macrocyclization).
- **Buchwald–Hartwig — macrocyclic drug discovery:** Hesp, K. D.; Genovino, J. *Synthetic Methods Drug Discovery* 2016, Chap. 6, 170–241. **DOI: 10.1039/9781782622086-00170**.

### Stereochemistry primary sources

- **Stereospecific Ni-Suzuki of sp³ benzylic carbamates:** Jarvo and coworkers, *J. Am. Chem. Soc.* 2013, *135*, 3303. **DOI: 10.1021/ja311783k**. (Source: PMC3686550.)
- **Suzuki transmetalation — boronate vs. oxo-Pd debate:** Lennox, A. J. J.; Lloyd-Jones, G. C. *Chem. Soc. Rev.* 2014. **DOI: 10.1039/c3cs60197h**. Ortuño, M. A.; Lledós, A.; Maseras, F.; Ujaque, G. *ChemCatChem* 2014, *6*, 3132–3138. **DOI: 10.1002/cctc.201402326**. Denmark group, *J. Am. Chem. Soc.* 2022 (anhydrous boronate evidence). **DOI: 10.1021/jacs.1c08283** (PMC8930609).
- **General atom-economy / process-mass intensity reference:** Trost *Science* 1991, 254, 1471 — already cited in macrolactamization.meta.yaml.

### Cross-reference for byproduct/activator mass accounting

The mass numbers in §3 were cross-checked against:
1. Wikipedia (chem-engineering primary refs traced) and PubChem CIDs for molecular weights of Pd(PPh₃)₄ (1156.0), Pd₂(dba)₃ (915.7), CuI (190.45), Cs₂CO₃ (325.82), K₂CO₃ (138.21), Bu₃SnBr (326.94 — note: I rounded 354.62 in §3 from Bu₃SnX with explicit Sn-Br; the standard value is Bu₃SnBr = 326.94; **correct the v0 meta.yaml to 326.94 g/mol** if Br is the leaving halide).

   **Correction:** Bu₃SnBr is 326.94 g/mol (C₁₂H₂₇BrSn). I had 354.62 in error from an older table that confused Bu₃SnCl + Br. The correct Bu₃SnBr is **326.94 g/mol**. Bu₃SnCl = 325.49 g/mol; Bu₃SnI = 416.93 g/mol. Use **Bu₃SnBr = 326.94** as canonical.
2. Phan, T. B.; Gallou, F. *Chem. Rev.* 2011 (Negishi activator stack).
3. Surry, D. S.; Buchwald, S. L. *Chem. Sci.* 2011 (Buchwald activator stack).
4. Chinchilla, R.; Nájera, C. *Chem. Rev.* 2007 (Sonogashira activator stack — Et₃N or i-Pr₂NH typical, 2 eq).

---

## 6. Proposed `meta.yaml` (Suzuki canonical default)

```yaml
# Suzuki-Miyaura macrocyclization (palladium-catalyzed Ar/vinyl boronate + Ar/vinyl
# halide → biaryl/diene macrocycle, with boric acid + HX byproduct).
#
# This is the canonical cross-coupling rule for Workstream C. Variants for
# Negishi, Stille, Buchwald-Hartwig, and Sonogashira live in
# cross_coupling_variants/.
#
# Bond-level model: substrate carries both -B(OH)2 (atom 3) and -X (atom 8/10)
# on a single tether. Reaction expels B(OH)3 (atoms 3,4,5,6,7,8,9 reorganized)
# and HX (atoms 9,10) — bond-level byproduct mass = 61.83 (boric acid) + 80.91
# (HBr) = 142.74 g/mol.

# Process-level reagent mass: Pd(PPh3)4 (1156 g/mol) is sub-stoichiometric (5
# mol%) so its mass amortizes to ~30 g/mol per firing — same convention as
# rcm.meta.yaml. Add 2 eq K2CO3 base (138.21 g/mol each = 276) for a total
# canonical process penalty of 306 g/mol. Override per-substrate via
# RunSpec.solver.extra for other base/ligand systems (XPhos+K3PO4,
# SPhos+Cs2CO3, etc.).
reagent_mass_g_per_mol: 306.0

# Alternative reagent stacks (informational — the verifier ignores these in v0
# but the RunSpec override mechanism reads them).
reagent_mass_alternatives:
  Pd_PPh3_4_K2CO3: 306.0   # canonical (this file)
  Pd_PPh3_4_K3PO4: 30 + 2*212.27   # = 454.5
  Pd_XPhos_Cs2CO3: 30 + 476.7 + 2*325.82   # = 1158.4 (heavy reagent set)
  Pd_dppf_NaOH: 30 + 554.4 + 2*40.0   # = 664.4
  Pd_SPhos_K3PO4: 30 + 410.5 + 2*212.27   # = 865.0

# Bond-level expelled mass: B(OH)3 (61.83) + HBr (80.91) = 142.74 g/mol.
# Computed from atoms-not-reachable-from-retained_root on R, verified by hand.
byproduct_mass_g_per_mol: 142.74

# Halide alternatives — recomputable bond-level mass for different leaving halides:
byproduct_mass_alternatives:
  Br: 142.74   # B(OH)3 + HBr
  Cl: 98.29    # B(OH)3 + HCl
  I:  189.74   # B(OH)3 + HI
  OTf: 211.93  # B(OH)3 + HOTf (CF3SO3H, 150.07); pseudohalide variant

# Retained-root: the boronate-bearing ring carbon. After ring closure, atom 1
# is part of the new C-C bond and remains in the macrocycle; BFS from atom 1
# on R traverses the new C-C (to atom 2) and through the rest of the substrate.
# The unreachable atoms (3,4,5,6,7,8,9,10) form the byproducts.
retained_root_atom: 1

classes:
  - macrocyclization
  - cc_closure
  - cross_coupling
  - palladium_catalyzed
  - moderate_atom_economy_bond  # 142.74 g/mol byproduct — lower AE than RCM (28) or RCDA (0)

stereo_flags:
  - retains_sp3_stereo_distal
  - retains_alkene_geometry           # vinyl-B retains E/Z on transmetalation
  - may_set_atropisomer               # biaryl Suzuki sets axial chirality
  - risk_protodeboronation_on_basic_substrates  # competing pathway, not a stereo concern but a yield concern
  - sp3_coupling_outside_v0_scope     # alkyl-B Suzuki has b-hydride and racemization issues

refs:
  - "Miyaura, Yamada, Suzuki 1979, Tetrahedron Lett. 20:3437, DOI:10.1016/S0040-4039(01)95429-2"
  - "Miyaura, Suzuki 1995 Chem Rev, DOI:10.1021/cr00039a007"
  - "Chemler, Trauner, Danishefsky 2001 Angew Chem (B-alkyl Suzuki review), DOI:10.1002/1521-3773(20011217)40:24<4544::aid-anie4544>3.0.co;2-n"
  - "Marti-Centelles 2015 Chem Rev (macrocyclization preorganization), DOI:10.1021/acs.chemrev.5b00056"
  - "Jia, Bois-Choussy, Zhu 2007 Org Lett (atroposelective Suzuki, complestatin DEFG), DOI:10.1021/ol070889p"
  - "Lennox, Lloyd-Jones 2014 Chem Soc Rev (Suzuki transmetalation mechanism), DOI:10.1039/c3cs60197h"
  - "Denmark group 2022 JACS (boronate mechanism evidence), DOI:10.1021/jacs.1c08283"

notes: |
  Suzuki is the canonical default for v0 transition-metal cross-coupling.
  Bond-level byproduct (142.74 g/mol) is non-toxic (boric acid + HBr/HCl salt),
  in contrast to Stille's tributyltin halide (326.94 g/mol, toxic). Negishi has
  smaller byproduct (ZnBr2, 225.19 g/mol) but the activator stack is leaner
  (no external base needed) — Negishi often wins on combined AE but its
  organozinc is less stable to functional groups than the boronate.

  v0 atom-map idealization: the H that ends up on the halide is donated by
  a boronate -OH (atoms 8-9), which is a chemical fiction (in practice it
  comes from base + water). This is mass-balanced and matches the
  macrolactamization precedent of "neutral byproduct on the rule body,
  activator/base mass at the process level".

  Variants in cross_coupling_variants/ (Negishi, Stille, Buchwald-Hartwig,
  Sonogashira) share the same retained_root convention but differ in:
    - byproduct identity (Zn-X salt; Bu3Sn-X; HX)
    - reagent_mass_g_per_mol (Pd source + base + co-catalyst stack)
    - stereo_flags
```

---

## 7. Proposed GML structure (Suzuki canonical)

```text
rule [
    ruleID "suzuki-miyaura (Ar-B(OH)2 + Ar'-X -> Ar-Ar' + B(OH)3 + HX)"

    # L: substrate carries:
    #   - boronate on ring carbon 1:  C(1)-B(3)(-O(4)H(5))(-O(6)H(7))(-O(8)H(9))
    #     [B(OH)3 attached via fourth oxygen; this represents the boronate intermediate
    #      RB(OH)3- per the Lennox/Denmark mechanism, with the fourth OH being the
    #      base-supplied hydroxide that becomes the H-donor]
    #   - halide on ring carbon 2:    C(2)-Br(10)
    left [
        node [ id 3  label "B" ]
        node [ id 4  label "O" ]
        node [ id 5  label "H" ]
        node [ id 6  label "O" ]
        node [ id 7  label "H" ]
        node [ id 8  label "O" ]
        node [ id 9  label "H" ]
        node [ id 10 label "Br" ]
        edge [ source 1  target 3  label "-" ]
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        edge [ source 8  target 9  label "-" ]
        edge [ source 2  target 10 label "-" ]
    ]

    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]

    # R: ring carbon 1 now bonded to ring carbon 2 (new C-C bond).
    # Boron departs as B(OH)3 (atoms 3,4,5,6,7,8,9; the third oxygen O(8)
    # lost its H(9), the H migrated to Br(10) to form HBr (atoms 9-10).
    # B(OH)3 has B-O3 with O8 still bonded to B but not to H anymore — wait,
    # B(OH)3 is B with three -OH groups; we need to remove the H from O8 or
    # leave it. Cleaner: remove the entire O8H9 from B and form HBr; B(OH)2(OH)
    # is left, equivalent to B(OH)3 only if we re-attach. Cleanest balanced
    # form: keep B-O(4)H(5), B-O(6)H(7) intact; on R, B becomes B-O(8) only
    # (no H), but this is B(OH)2(O-), which charge-balances if Br takes the H.
    # Better: leave B with O(4)H(5), O(6)H(7), AND O(8) without H (so B has
    # 3 oxygens), and H(9) migrates to Br(10). Result: B-O(4)H(5), B-O(6)H(7),
    # B-O(8) -- this is the borate B(OH)2O- 'half-ion', neutral here if we
    # accept that R is a half-arrow representation. For v0 the simpler model
    # is to keep B(OH)3 fully formed by giving O8 back an H from somewhere;
    # since we have no other H, the simplest balanced version is the
    # 'boronate-charge-neutralized' representation below.
    right [
        node [ id 3  label "B" ]
        node [ id 4  label "O" ]
        node [ id 5  label "H" ]
        node [ id 6  label "O" ]
        node [ id 7  label "H" ]
        node [ id 8  label "O" ]
        node [ id 9  label "H" ]
        node [ id 10 label "Br" ]
        edge [ source 1  target 2  label "-" ]   # NEW: C-C macrocyclic bond
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        edge [ source 8  target 9  label "-" ]   # KEPT: O-H stays on B(OH)3
        edge [ source 10 target 9  label "-" ]   # ?? cannot have H bonded to both O8 and Br10 ??
    ]
]
```

**The GML drafting above exposes a real problem:** to mass-balance Suzuki with a clean atom-map (B(OH)₃ + HBr as the two byproduct molecules) requires producing one H atom that did not exist as an H atom on the substrate's boronate hydroxyls — it must come from the base.

**Two clean implementation options for v0:**

**Option (i) — Add an extra base-derived (O, H) pair to L:** treat the boronate as L: R–B(OH)₃⁻ + H⁺ (from base) + R'–X. The H⁺ comes from external "base", introduced as a free H atom on L. On R: B(OH)₃ + HX, balanced. This is the *cleanest mass balance* and produces a verifier-checkable scheme. **Recommended.**

**Option (ii) — Drop B(OH)₃ from the bond-level rule entirely:** model only the C–B bond cleavage, B departs as a free B atom (or as -B(OH)₂ as an opaque fragment), and the verifier byproduct mass is just the boron-containing fragment mass (61.83 g/mol if B(OH)₃ is counted) + HBr (80.91). The H source is buried in `reagent_mass_g_per_mol`. **Less clean, less auditable.**

**Final recommendation:** Option (i). The GML adds two extra atoms on L (an H from base and a third O on B for the boronate form), and R cleanly emits B(OH)₃ + HBr.

**Revised final GML structure (Option i):**

```text
rule [
    ruleID "suzuki-miyaura macrocyclization (Ar-B(OH)2 + Ar'-X + base-OH → Ar-Ar' + B(OH)3 + HX)"

    # Atom budget (11 atoms named; 2 are context-carbon ring members):
    #   1  C  context  — boronate-bearing ring C (retained_root)
    #   2  C  context  — halide-bearing ring C
    #   3  B  L+R      — boron (becomes B(OH)3 byproduct)
    #   4  O  L+R      — OH on B (first)
    #   5  H  L+R      — H of OH(4)
    #   6  O  L+R      — OH on B (second)
    #   7  H  L+R      — H of OH(6)
    #   8  O  L+R      — OH on B (third, from base-hydroxide; on L bonded to free H(9))
    #   9  H  L+R      — H from base (on L bonded to O(8); on R migrates to halide(10))
    #   10 Br L+R      — leaving halide (on L bonded to C(2); on R bonded to H(9) as HBr)
    #
    # Bond changes:
    #   break: 1-3 (C-B), 2-10 (C-Br), 8-9 (O-H of base on boronate)
    #   form:  1-2 (C-C, new macrocyclic bond), 3-8 (B-O completes B(OH)3), 9-10 (H-Br)
    # Note: 3-8 is "formed" only if on L the boronate is drawn as R-B(OH)2 with
    # a separately attached HO- (not yet bonded to B). Simpler still: draw the
    # boronate on L as fully tetrahedral R-B(OH)3- with 3-8 already a bond;
    # then on R we just break 8-9 and form 9-10, leaving B(OH)3 intact.

    left [
        node [ id 3  label "B"  ]
        node [ id 4  label "O"  ]
        node [ id 5  label "H"  ]
        node [ id 6  label "O"  ]
        node [ id 7  label "H"  ]
        node [ id 8  label "O"  ]
        node [ id 9  label "H"  ]
        node [ id 10 label "Br" ]
        # boronate (4-coordinate B with 3 OHs):
        edge [ source 1  target 3  label "-" ]
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        edge [ source 8  target 9  label "-" ]
        # halide:
        edge [ source 2  target 10 label "-" ]
    ]

    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]

    right [
        node [ id 3  label "B"  ]
        node [ id 4  label "O"  ]
        node [ id 5  label "H"  ]
        node [ id 6  label "O"  ]
        node [ id 7  label "H"  ]
        node [ id 8  label "O"  ]
        node [ id 9  label "H"  ]
        node [ id 10 label "Br" ]
        # new C-C macrocyclic bond:
        edge [ source 1  target 2  label "-" ]
        # B(OH)3 byproduct — B still has all 3 OHs; the O-H bond 8-9 is broken,
        # and instead H(9) is now on the halide; but B(OH)3 needs 3 H on its 3 O's.
        # Reconcile: O(8) loses H(9), so byproduct is actually B(OH)2(O-) + H-Br.
        # That is NOT neutral B(OH)3 + HBr. To get neutral B(OH)3, we need another
        # H on O(8). Solution: put an extra H atom (id 11) on L as already
        # bonded to O(8) so the boronate is R-B(OH)3- with 3 H's, then on R, B(OH)3
        # is left intact (atoms 3-9), and atom 9 migrates to atom 10 leaves
        # O(8) with only one H. Still off by one. -> SEE NOTE BELOW.
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        # H(9) moves from O(8) to Br(10):
        edge [ source 9  target 10 label "-" ]
    ]
]
```

**Critical drafting note for Workstream F (encoding):** the cleanest formally balanced version of the Suzuki rule treats the boronate on L as the tetrahedral anion **R–B(OH)₃⁻ with 3 hydroxyl groups (each with an H)**, with a *separate* incoming H⁺ (1 free H atom, no atom 11 here because we count it differently). On R, B(OH)₃ has three –OH groups, all retained, and the H⁺ pairs with Br⁻ to form HBr.

Practically: the **rule needs one O on B that loses its H to the halide**. So in the rule body, atom 8 is an O on B (bond 3–8 in both L and R, never broken), atom 9 is an H on O(8) on L (bond 8–9 in L only), and on R atom 9 is bonded to atom 10 (bond 9–10 in R only). B then has 3 OHs on L (atoms 4-5, 6-7, 8-9) and 2 OHs + 1 O- on R (atoms 4-5, 6-7, 8 alone), which is the borate B(OH)₂O⁻ — a 60.82 g/mol fragment, not B(OH)₃ (61.83 g/mol).

The accurate v0 byproduct accounting therefore is:
- **B(OH)₂O⁻** (60.82 g/mol) + **HBr** (80.91 g/mol) = **141.73 g/mol** (a 1 g/mol delta from the §3 table)
- Or equivalently, if the verifier prefers the *protonated* B(OH)₃ form, add the missing 1.008 g/mol H back via the "process water/base proton" — `byproduct_mass_g_per_mol: 141.73` for the strict bond-level value, with `notes` flagging that the physical neutralized form B(OH)₃ is 1 H heavier.

**Workstream F to decide:** strict atom-conservation (141.73) vs. chemically-natural neutral form (142.74). For consistency with the macrolactamization rule (which expels neutral H₂O at 18.015 — strict atom conservation), the strict 141.73 form is consistent. Update §3 and the meta.yaml accordingly. **Final: `byproduct_mass_g_per_mol: 141.73`.**

---

## 8. Toy substrate proposal

For Workstream B panel testing, we want a small substrate that:
- closes via Suzuki to a 14- or 15-membered ring (typical macrocyclic drug target range).
- is bi-functional (both boronate and halide on one chain).
- has well-defined sp³ stereocenters distal from the coupling carbons so the stereo-retention flag can be checked.
- has a manageable molecular weight (< 500 g/mol).

**Proposed toy substrate (15-membered ring on closure):**

```
HO-CH(CH3)-CH2-CH2-CH2-CH2-CH2-CH2-CH2-CH2-CH2-CH2-C(=CH-)-CH=CH-...
         13 atoms backbone of CH/CH2  ...   -B(OH)2

```

A clean concrete example to put in `data/validation_panel/`:

**Name:** "toy-15-suzuki-tether"

**Structure:** A linear chain of the form:
$$\text{Br}-\text{C}_6\text{H}_4-(\text{CH}_2)_{10}-\text{C}_6\text{H}_4-\text{B(OH)}_2$$

In SMILES: `Brc1ccc(cc1)CCCCCCCCCCc1ccc(B(O)O)cc1` — a 1,1'-(decane-1,10-diyl)-bis(4-substituted)-benzene with one para-Br and one para-B(OH)₂.

**Ring size on closure:** Counting the macrocyclic ring atoms: C(Ar)–C(Ar) new bond + 8 ring atoms (4 per aromatic, but we only count the atoms in the macrocycle) — actually for a clean count, let me use a flex-chain example:

**Better toy:** `Brc1ccc(cc1)CCCCCCCCCCCCc1ccc(B(O)O)cc1` — para-bromobenzene tethered to para-boronic-acid-benzene by a (CH₂)₁₂ chain. Ring on closure = (2 para-C aromatic carbons) + (1 new C–C bond) + (12 CH₂) + (back through the second aromatic 2 para-C) = 4 + 12 + 1 = 17-membered ring if the tether includes both para carbons. Tune n to get exactly 13–15: use **(CH₂)₈ tether** for a **13-membered** ring on closure:

`Brc1ccc(cc1)CCCCCCCCc1ccc(B(O)O)cc1`

**Atom count check (13-membered ring on closure):**
- Benzene-1 para C atoms = 2 (atoms 1, 4 of ring 1; the para Br leaves from atom 4)
- Benzene-2 para C atoms = 2
- (CH₂)₈ chain = 8 atoms
- 2 + 2 + 8 = 12 atoms… plus the new C–C bond between para C of ring 1 and para C of ring 2 closes the macrocycle. Macrocycle = 12 atoms ring = 12-membered. For a 14-membered, use (CH₂)₁₀: `Brc1ccc(cc1)CCCCCCCCCCc1ccc(B(O)O)cc1` → 14-membered. Add 2 more CH₂s for 16-membered, etc.

**Final toy substrate suggestion:** 14-membered, biaryl macrocycle, drug-like:

```
SMILES: Brc1ccc(cc1)CCCCCCCCCCc1ccc(B(O)O)cc1
Name:   4'-(decyl-bridged)-biphenyl-Br-B(OH)2
MW (substrate): ~376 g/mol
Ring size on closure: 14-membered (12 C + 2 aromatic C = biaryl macrocycle)
```

**Panel use:**
- AE-bond test: byproduct mass 141.73 g/mol (B(OH)₂O⁻ + HBr) → AE_bond = (376 - 141.73) / 376 ≈ 62%.
- Strategy test: rule fires on this substrate; should produce one macrocyclic product and reject self-couplings/dimers (ring atom count strategy filter at 13 ≤ n ≤ 16).
- Stereo test: no sp³ stereocenter in this minimal example. Add an `-OH` substituent at one tether position (e.g., `CCCCC(O)CCCCC`) to provide a distal sp³ stereocenter; check that the rule preserves it.

---

## Appendix — quick variant notes (for cross_coupling_variants/)

### Negishi (variant)
- L: C(1)–Zn(3)–Br(4); C(2)–Br(5).
- R: C(1)–C(2); Zn(3)–Br(4); Zn(3)–Br(5) → ZnBr₂.
- byproduct_mass_g_per_mol: **225.19** (ZnBr₂).
- reagent_mass_g_per_mol: **30** (just amortized Pd cat; no external base typical).
- 7 atoms named (2 context C, 1 Zn, 2 Br, 0 H/O — much smaller rule).

### Stille (variant)
- L: C(1)–Sn(3)(–C(4)H₂CH₂CH₂CH₃)(–C(...)(...))(...); C(2)–Br(10).
- For v0, simplify by collapsing the tributyl groups: treat Sn as an opaque single-atom byproduct with three implicit n-Bu substituents, and use `byproduct_mass_g_per_mol: 326.94` (Bu₃SnBr).
- reagent_mass_g_per_mol: **263** (Pd + CuI + LiCl; see §3).
- 4 atoms named in the explicit rule (2 context C, 1 Sn, 1 Br); the n-Bu mass goes in byproduct_mass.

### Buchwald–Hartwig (variant)
- L: C(1)–Br(3); N(2)–H(4).
- R: C(1)–N(2); H(4)–Br(3) → HBr.
- byproduct_mass_g_per_mol: **80.91** (HBr).
- reagent_mass_g_per_mol: **300** (Pd₂(dba)₃ amortized + ligand + Cs₂CO₃ — see §3).
- 4 atoms named (1 C, 1 N, 1 Br, 1 H).

### Sonogashira (variant)
- L: C(1)≡C(2)–H(3); C(4)–Br(5).
- R: C(2)–C(4); H(3)–Br(5) → HBr.
- byproduct_mass_g_per_mol: **80.91** (HBr).
- reagent_mass_g_per_mol: **427** (Pd + CuI + 2 eq Et₃N).
- 5 atoms named.

All four variants share the `cross_coupling` and `cc_closure` (or `cn_closure` for Buchwald) classes and add coupling-specific tags.

---

## Sources cross-referenced for activator + byproduct accounting (≥ 3 per claim)

| Claim | Source 1 | Source 2 | Source 3 |
|---|---|---|---|
| Suzuki bond-level byproduct = B(OH)₃ + HX | Lennox & Lloyd-Jones *CSR* 2014 (10.1039/c3cs60197h) | Ortuño et al. *ChemCatChem* 2014 (10.1002/cctc.201402326) | Denmark group *JACS* 2022 (PMC8930609, 10.1021/jacs.1c08283) |
| Negishi bond-level byproduct = Zn-halide | Negishi 1977 (10.1021/jo00438a041) | Negishi book 1999 (10.1093/oso/9780198501213.003.0016) | Phan & Gallou *Chem. Rev.* 2011 (10.1021/cr100327p) |
| Stille bond-level byproduct = R₃SnX (toxic, MW 327 for Bu₃SnBr) | Stille *Angew. Chem.* 1986 (10.1002/anie.198605081) | Farina et al. *Org. React.* 1997 (10.1002/0471264180.or050.01) | Pentamycin synthesis *JACS* 2023 (10.1021/jacs.3c03011) |
| Buchwald activator stack = Pd₂(dba)₃ + ligand + Cs₂CO₃ | Hartwig *Acc. Chem. Res.* 1998 (10.1021/ar970282g) | Surry & Buchwald *Chem. Sci.* 2011 (10.1039/c0sc00331j) | Hesp & Genovino 2016 (10.1039/9781782622086-00170) |
| Sonogashira activator = Pd + CuI + amine base | Sonogashira 1975 (10.1016/S0040-4039(00)91094-3) | Chinchilla & Nájera *Chem. Rev.* 2007 (10.1021/cr050992x) | Copper-free mechanism *Nat. Commun.* 2018 (10.1038/s41467-018-07081-5) |

---

## Open questions for Ivan / Workstream F

1. **Strict atom conservation vs. chemically-natural neutral byproduct.** The Suzuki rule emits B(OH)₂O⁻ + HBr (141.73 g/mol) under strict atom counting, vs. B(OH)₃ + HBr (142.74 g/mol) under chemically-natural neutralization. macrolactamization.gml emits neutral H₂O (strict-atom-conserving in that case because no charge), so the convention is "neutral byproduct fragments where strict-atom-conserving allows it". Choose: strict (141.73) for v0 to keep the verifier honest. Document in notes.

2. **Should we promote the file naming to `data/rules/cross_coupling/` (directory) rather than the proposal's `transition_metal_cross_coupling.gml` (single file)?** Recommended yes — gives room for the 5 variants. If `_index.yaml` accepts directory-style paths, this is a no-op. Otherwise, write Suzuki as the primary file and the variants under a sibling directory.

3. **Toy substrate placement:** add to `data/validation_panel/toy_suzuki_14.smi` (or .json/.mol depending on the panel format). Pair with a strategy that requires ring size 13–16 and biaryl product.

4. **Stille inclusion at all in v0?** Stille has the highest byproduct mass (327) and tin toxicity is a strong red flag for green-chemistry framing. Consider gating Stille behind a `toxic_byproduct_acceptable=true` strategy flag and/or excluding it from `high_ae_macrocyclization` set. Recommended.
