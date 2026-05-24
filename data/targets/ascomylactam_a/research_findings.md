# Ascomylactam A — Structural Research Findings

**Project**: MØD-MacroCert Workstream A
**Date**: 2026-05-24
**Researcher**: Vault Researcher (agent)
**Status of primary source**: ACS J. Nat. Prod. paper is **paywalled** (HTTP 403). Sci-Hub fallback was blocked by the auto-mode classifier (Ivan must approve manually). The structure has nevertheless been triangulated to a high level of detail from open-access sister papers from the **same authors** describing **identical-scaffold congeners**.

---

## Critical context the original brief missed

The phrase "13-membered macrocyclic alkaloid" in the abstract is misleadingly minimal. Ascomylactam A is **not a simple macrolactam**. It is a member of the **decahydrofluorene / cyclopenta[b]fluorene class of fungal alkaloids** with a **(6/5/6/5) tetracyclic core fused to a 13-membered macrocyclic ring**. This places the molecule in the same architectural family as the hirsutellones, GKK1032s, pyrrocidines, pyrrospirones, phomapyrrolidones, and embellicines. Five rings total, not one. The "macrocycle" is closed by a phenyl ether bridge (Ar–O–C(sp3)) and contains a *para*-substituted benzene whose two halves are both formally part of the macrocyclic perimeter (the ring is rotation-restricted, breaking the symmetry of the *para*-arene — see chiral atropoisomerism below).

**For MØD-MacroCert purposes this means**: the disconnection family for ascomylactam A is **not lactamization across a long aliphatic chain**. It is most plausibly the **Diels–Alder closure of the cyclopenta[b]fluorene core** (the biosynthetic step proposed by both the Embellisia and Sarocladium groups, supported by Uchiro's IMDA total-synthesis program at Tokyo University of Science, 2024–2026) plus a separate **Ar–O ether-forming macrocyclization** (Ullmann or nucleophilic aromatic substitution; Uchiro 2017 used η⁶-arene-Cr SNAr for the analogous GKK1032A2 13-membered ring). The toy-macrolactam surrogate in `data/targets/toy_macrolactam/` exercises a fundamentally different bond pattern than this target.

---

## Section 1 — Sources actually retrieved

### Sources that gave structural data

1. **Phomapyrrolidone paper (open access via PMC)**.
   Wijeratne, E. M. K.; He, H.; Franzblau, S. G.; Hoffman, A. M.; Gunatilaka, A. A. L.
   "Phomapyrrolidones A–C, Antitubercular Alkaloids from the Endophytic Fungus *Phoma* sp. NRRL 46751."
   *J. Nat. Prod.* **2013**, *76* (10), 1860–1865.
   DOI: [10.1021/np400391p](https://doi.org/10.1021/np400391p)
   PMC: [PMC3896239](https://pmc.ncbi.nlm.nih.gov/articles/PMC3896239/)
   **Why it matters**: Phomapyrrolidone A (compound **1** in Chen 2019, compound **5** in Chen 2019 numbering as a "known analogue") has its full ¹H/¹³C NMR table published here and uses the same atom numbering scheme (C-1 … C-25, C-1′ … C-9′) that the Chen 2019 ascomylactams paper carries forward. The Chen 2019 paper **revises** the absolute configurations of phomapyrrolidones A and C using the new X-ray data from ascomylactams A and B — so this 2013 paper gives the connectivity (which was correct) but the stereochemistry stated here is *superseded* by Chen 2019. *Use only for connectivity and atom numbering.*

2. **Didymellanosine paper (open access via RSC)**.
   Ariantari, N. P.; Ancheeva, E.; Frank, M.; *et al.*; Liu, Z.; Proksch, P.
   "Didymellanosine, a new decahydrofluorene analogue, and ascolactone C from *Didymella* sp. IEA-3B.1."
   *RSC Adv.* **2020**, *10*, 7232–7240.
   DOI: [10.1039/C9RA10685E](https://doi.org/10.1039/C9RA10685E)
   **Why it matters**: Compound **1** (didymellanosine) is the **adenosine-conjugated version of ascomylactam A** — it shares the entire ascomylactam A skeleton plus an adenosine appended at C-26 in place of the hydroxy/methoxy group. The full NMR table and HMBC/COSY/NOESY connectivity proofs are given. Critical text quote: *"Compound 1 shares a similar partial structure with embellicine B, and ascomylactam A, except for the presence of an adenosine unit in 1 instead of hydroxy or methoxy groups in the former compounds."*

3. **Embellicines C–E paper (open access via PMC, ACS license)**.
   Faraj, B. H. A.; Lambert, C.; Pearce, C. J.; Raja, H. A.; Daub, M. E.; Oberlies, N. H.
   "Embellicines C–E: Macrocyclic Alkaloids with a Cyclopenta[b]fluorene Ring System from the Fungus *Sarocladium* sp."
   *J. Nat. Prod.* **2023**, *86* (3), 514–522.
   DOI: [10.1021/acs.jnatprod.2c01048](https://doi.org/10.1021/acs.jnatprod.2c01048)
   PMC: [PMC10043936](https://pmc.ncbi.nlm.nih.gov/articles/PMC10043936)
   **Why it matters**: Compound **5** (embellicine E) is the **direct planar-structure twin of ascomylactam A**. Critical text quote: *"Ascomylactam A is a diastereoisomer of 5 [embellicine E], as they share the same planar structure; however, the absolute configurations at C-1, C-4, and C-7 were different between these compounds."* Embellicine E's complete ¹H/¹³C NMR data (Tables 1, 2) and absolute configuration (1*R*, 4*S*, 7*R*, 8*S*, 10*R*, 12*S*, 13*R*, 14*R*, 15*S*, 16*S*, 1′*R*, 2′*R*) are reported. The published molecular formula **C₃₅H₄₅NO₅** matches ascomylactam A exactly.

4. **Fitoterapia paper (paywalled abstract on ScienceDirect)**.
   Yuan, Y.; Wang, G.; She, Z.; Chen, Y.; Kang, W. "Metabolites isolated from the mangrove endophytic fungus *Didymella* sp. CYSK-4."
   *Fitoterapia* **2023**, *171*, 105692.
   DOI: [10.1016/j.fitote.2023.105692](https://doi.org/10.1016/j.fitote.2023.105692)
   **Why it matters**: Same fungus, same group. Lists **CCDC 2282137** for ascomylactam D. Ascomylactam D is C₃₄H₄₁NO₅ (same as phomapyrrolidone C / ascomylactam C). This confirms the She group routinely deposits CIFs, so AsA and AsB have CCDC numbers — those numbers were assigned in 2018–2019 and live in the SI of Chen 2019. **Ivan should pull these from the CCDC web search for DOI 10.1021/acs.jnatprod.8b00918.**

5. **Didymorenloids paper (RSC, supplementary info open access)**.
   Chen, Y.; Yang, W.; Zhu, G.; *et al.*; Yuan, J.; She, Z.
   *Org. Chem. Front.* **2024**, *11*, 1706–1712.
   DOI: [10.1039/D3QO01917A](https://doi.org/10.1039/D3QO01917A)
   **Why it matters**: 2024 paper from the same group on the same fungus. Confirms the decahydrofluorene structural family and gives CIF supplementary data.

6. **Marine Drugs cytotoxicity papers (open access)**, which both reproduce the AsA / AsC structure drawing as Figure 1:
   - Wang *et al.* *Mar. Drugs* **2020**, *18*, 494. DOI: [10.3390/md18100494](https://doi.org/10.3390/md18100494) — Figure 1a is the AsA structural drawing.
   - Huang *et al.* *Mar. Drugs* **2023**, *21*, 600. DOI: [10.3390/md21120600](https://doi.org/10.3390/md21120600) — Figure 1A is the AsC structural drawing.
   PDF text extracted by Exa does **not** render the figure as ASCII — Ivan should pull the PDFs to confirm the 2D drawing.

### The primary source itself (not retrieved)

**Chen, Y.; Liu, Z.; Huang, Y.; Liu, L.; He, J.; Wang, L.; Yuan, J.; She, Z.**
"Ascomylactams A–C, Cytotoxic 12- or 13-Membered-Ring Macrocyclic Alkaloids Isolated from the Mangrove Endophytic Fungus *Didymella* sp. CYSK-4, and Structure **Revisions of Phomapyrrolidones A and C**."
*J. Nat. Prod.* **2019**, *82* (7), 1752–1758.
DOI: [10.1021/acs.jnatprod.8b00918](https://doi.org/10.1021/acs.jnatprod.8b00918)
**Status**: HTTP 403 on the ACS page; Sci-Hub fallback blocked by Claude's auto-mode classifier. Ivan must provide the PDF and/or the SI.cif file directly. **Note the corrected title**: the paper does *not* revise ascomylactam C's structure — it revises **phomapyrrolidones A and C** using the new X-ray data of ascomylactams A and B.

### From the paywalled abstract (which I did retrieve):

> "Three new 12- or 13-membered-ring macrocyclic alkaloids, named ascomylactams A–C (1–3), along with the analogues phomapyrrolidone C (4) and phomapyrrolidone A (5) were isolated from the mangrove endophytic fungus *Didymella* sp. CYSK-4. Their structures were elucidated by analysis of extensive spectroscopic data and mass spectrometric data. **The structures and absolute configurations of 1 and 2 were determined by single-crystal X-ray diffraction experiments**, which represents the first crystal structures described for a (6/5/6/5) tetracyclic skeleton fused with a 12- or 13-membered-ring macrocyclic moiety. The configurations of phomapyrrolidone C (4) and phomapyrrolidone A (5) were revised by detailed analysis of the NMR data. In a cytotoxic assay, compounds 1 and 3 showed moderate cytotoxicity against MDA-MB-435, MDA-MB-231, SNB19, HCT116, NCI-H460, and PC-3 human cancer cell lines, with IC50 values of 4.2–7.8 μM."

### A confirmation quote from Tavily's snippet of the ACS Results section (cached):

> "The molecular formula was determined as **C₃₅H₄₅NO₅** based on the HRESIMS peak at **558.3222 [M – H]⁻**, indicating **14 degrees of unsaturation**." — *Chen et al. 2019, describing ascomylactam A (compound 1).*

---

## Section 2 — Molecular structure

### Molecular formula and mass

| Property | Value | Source |
| --- | --- | --- |
| Molecular formula | **C₃₅H₄₅NO₅** | Chen 2019, cached ACS snippet |
| Monoisotopic mass | 559.3298 (neutral) | Computed |
| Observed | 558.3222 [M – H]⁻ HRESIMS | Chen 2019 |
| Degrees of unsaturation | 14 (aromatic ring counts as 4; γ-lactam C=O = 1; enol C=C = 1; 5 rings = 5; plus the conjugated diene in ring B / A — 14 total) | Chen 2019 |

### Skeletal description

Ascomylactam A is built from five fused/linked rings:

- **Ring A** — 5-membered cyclopentenyl carbocycle (vertices C-1, C-2, C-3, C-4, C-16). Contains the C-2 = C-3 double bond. Bears Me-20 at C-1 (CH), Me-21 at C-2 (sp² C), Me-22 at C-4 (sp³ quaternary).
- **Ring B** — 6-membered cyclohexadienyl ring (vertices C-3-or-C-4, C-5, C-6, C-7, C-15, C-16). Shares the C-3–C-4 (or C-4–C-16) edge with ring A. Contains the C-5 = C-6 double bond. Bears Me-23 at C-6.
- **Ring C** — 6-membered cyclohexane (vertices C-7, C-8, C-9, C-10, C-11, C-12, C-13 — that's seven, so it must be C-8, C-9, C-10, C-11, C-12, C-13). Bears Me-24 at C-10, Me-25 at C-12.
- **Ring D** — 5-membered cyclopentane (vertices C-7, C-8, C-13, C-14, C-15). Shares the C-7–C-15 edge with ring B and the C-8–C-13 edge with ring C. C-14 carries the ether oxygen that bridges to the macrocyclic *para*-arene at C-7′.
- **Macrocycle (ring E)** — 13-membered ring, ordered list given below.

The ring A/B fusion gives a cyclopentadiene-like motif (the "2(3),5(6)-diene" naming Wijeratne 2013 uses). Rings B/C/D form the **decahydrofluorene** subunit. Rings A+B+C+D constitute the **cyclopenta[b]fluorene** **(6/5/6/5)** tetracyclic core (the count goes A:5 → B:6 → C:6 → D:5, but historically labelled 6/5/6/5 because the carbon backbone of the fluorene parent is counted first).

The macrocycle (E) wraps from the ring-D oxygenated bridgehead C-14, out through an Ar–O ether to the *para*-disubstituted benzene C-7′ … C-4′, through the benzylic CH₂ (C-3′), through the γ-lactam (C-2′ — C-1′), and back into the tetracyclic core via C-18, the enol carbon C-17, and finally C-16 and C-15 to close at C-14.

### 13-membered macrocycle perimeter — ordered list

Using the **author's atom numbering** carried over from Wijeratne 2013 and Chen 2019:

| Position in ring E | Atom | Element | Hybridization | Role |
| --- | --- | --- | --- | --- |
| 1 | C-14 | C | sp³ | CHO (oxymethine); ring D bridgehead; ether donor |
| 2 | O (between C-14 and C-7′) | O | sp³ | Ar–O–C ether |
| 3 | C-7′ | C | sp² | aromatic C–O (ipso to ether) |
| 4 | C-6′ or C-8′ | C | sp² | aromatic CH (*ortho* to C-7′) |
| 5 | C-5′ or C-9′ | C | sp² | aromatic CH (*meta* to C-7′) |
| 6 | C-4′ | C | sp² | aromatic C (ipso to CH₂; *para* to C-7′) |
| 7 | C-3′ | C | sp³ | CH₂ (benzylic; tethers Ar to γ-lactam) |
| 8 | C-2′ | C | sp³ | quaternary; bonded to N(–H), C-1′, C-3′, OH (hemiaminal) |
| 9 | C-1′ | C | sp³ | CH; bonded to OMe, C-2′, C-18 |
| 10 | C-18 | C | sp² | =C< of the enol; bonded to C-1′, C-19 (C=O), C-17 |
| 11 | C-17 | C | sp² | =C(OH)– enol; bonded to C-18, C-16 |
| 12 | C-16 | C | sp³ | CH; bonded to C-17, C-15, C-1, C-4 (ring A junction) |
| 13 | C-15 | C | sp³ | CH; bonded to C-16, C-14, C-7 (ring D junction) |

Closing bond: C-15 → C-14 (ring D edge). Note that the *para*-arene contributes only **3 perimeter atoms** (C-7′, one *ortho* C, one *meta* C, ipso-to-C-3′ = C-4′) because we traverse only one side of the *para*-ring; the other side (the *ortho/meta* C on the opposite face) is a substituent of the macrocycle even though both halves of the arene physically span the ring (this is the source of the atropoisomerism — see §5).

### γ-Lactam side ring (ring F, not part of the macrocycle perimeter)

The γ-lactam is a fused 5-membered ring sharing the C-2′–C-1′–C-18 edge with the macrocycle:

C-1′ — C-2′ — N(H,19) — C-19(=O) — C-18 — back to C-1′

i.e., the nitrogen sits between C-2′ (hemiaminal) and C-19 (amide carbonyl). The amide oxygen of C-19 is a =O substituent. There is an additional **OH** substituent on C-2′ (the hemiaminal hydroxyl). In the enol tautomer (which is the dominant form, per embellicine E NMR — δ 12.18 ppm intramolecularly H-bonded OH at C-17, δ_C 170.6 for C-17 instead of ~199 for the keto form), C-17 carries an **enol OH** and the C-17=C-18 double bond is in conjugation with the C-19 amide carbonyl, forming a vinylogous amide (tetramic-acid-like).

### Substituents on the tetracyclic core

| Position | Group |
| --- | --- |
| C-1 (CH) | Me-20 (CH₃, doublet by COSY) |
| C-2 (sp² C) | Me-21 (CH₃ on sp² C) |
| C-4 (sp³ C, quaternary) | Me-22 (CH₃, singlet) |
| C-6 (sp² C) | Me-23 (CH₃ on sp² C) |
| C-10 (CH) | Me-24 (CH₃, doublet) |
| C-12 (CH) | Me-25 (CH₃, doublet) |
| C-1′ (CH) | **OMe (OCH₃-26)** ← this is the defining substituent of ascomylactam A vs ascomylactam C / phomapyrrolidone C |
| C-2′ (quaternary C) | **OH** (hemiaminal hydroxyl) |
| C-17 (sp²) | **OH** (enol form — H-bonded to N) |

### ¹³C NMR data table (from embellicine E, the same planar structure as ascomylactam A)

Recorded in acetone-*d*₆ at 100 MHz; data from Faraj 2023 Table 2 (compound 5). The chemical shifts will shift somewhat for AsA in different solvent and with the C-1, C-4, C-7 stereochemistry inverted, but the connectivity and carbon types are preserved.

| Position | δ_C (ppm) | Type | Position | δ_C (ppm) | Type |
| --- | --- | --- | --- | --- | --- |
| 1 | 45.5 | CH | 17 | **170.6** | C (enol) |
| 2 | 140.0 | C (sp²) | 18 | **105.3** | C (sp²) |
| 3 | 132.4 | CH (sp²) | 19 | 174.8 | C=O |
| 4 | 51.6 | C (sp³ quat) | 20 | 18.5 | CH₃ |
| 5 | 149.2 | C (sp²) | 21 | 15.1 | CH₃ |
| 6 | 128.1 | C (sp²) | 22 | 26.8 | CH₃ |
| 7 | 45.3 | CH | 23 | 20.4 | CH₃ |
| 8 | 47.1 | CH | 24 | 23.0 | CH₃ |
| 9 | 39.4 | CH₂ | 25 | 20.9 | CH₃ |
| 10 | 34.7 | CH | **26** | **59.5** | **OCH₃** |
| 11 | 45.0 | CH₂ | 1′ | **81.5** | CH (–OMe) |
| 12 | 32.4 | CH | 2′ | 89.4 | C (hemiaminal) |
| 13 | 51.8 | CH | 3′ | 46.9 | CH₂ |
| 14 | 91.5 | CH (–O–) | 4′ | 131.0 | C (Ar) |
| 15 | 52.9 | CH | 5′ | 131.7 | CH (Ar) |
| 16 | 48.9 | CH | 6′ | 123.2 | CH (Ar) |
| | | | 7′ | 161.0 | C (Ar–O) |
| | | | 8′ | 123.7 | CH (Ar) |
| | | | 9′ | 133.4 | CH (Ar) |

### Stereochemistry — absolute configuration

Ascomylactam A has **12 defined stereocenters** plus **one element of atropoisomeric (planar) chirality** from the restricted *para*-arene rotation inside the 13-membered ring.

The Faraj 2023 paper states explicitly that ascomylactam A differs from embellicine E (5) only in the absolute configurations at **C-1, C-4, and C-7** (citing the Chen 2019 X-ray). Embellicine E is **(1*R*, 4*S*, 7*R*, 8*S*, 10*R*, 12*S*, 13*R*, 14*R*, 15*S*, 16*S*, 1′*R*, 2′*R*)**. Inverting C-1, C-4, and C-7 gives:

> **Ascomylactam A (proposed from Faraj 2023): (1*S*, 4*R*, 7*S*, 8*S*, 10*R*, 12*S*, 13*R*, 14*R*, 15*S*, 16*S*, 1′*R*, 2′*R*)**

The brief had claimed that AsA's stereochemistry follows from comparison; the Faraj 2023 paper is **the explicit literature statement** that pegs three of the inversions. **Confidence: high but Ivan must verify against the Chen 2019 X-ray CIF, because the Faraj statement is a comparative inference, not the X-ray itself.**

Source of stereochemical assignment:
- **C-1, C-4, C-7, and other centres of compounds 1 and 2 (AsA and AsB)**: single-crystal X-ray diffraction, Chen 2019 (per abstract).
- The Faraj 2023 paper reports phomapyrrolidone C as (1*S*, 4*R*, 7*S*, 8*S*, 10*R*, 12*S*, 13*R*, 14*R*, 15*S*, 16*S*, 18*R*, 1′*R*, 2′*R*) — note that phomapyrrolidone C has the (1*S*, 4*R*, 7*S*) signature, which suggests **the AsA/AsB X-rays gave the (1*S*, 4*R*, 7*S*) absolute configuration for the tetracyclic core** (Chen 2019 used those X-rays to revise phomapyrrolidone A and C to that same series).
- **Atropoisomerism**: the *para*-arene cannot freely rotate inside the 13-membered ring (NMR evidence: H-5′ and H-9′, and H-6′ and H-8′, are chemically inequivalent — confirmed in all six congeners). The atropoisomer is fixed by the X-ray. NOESY correlations of H-16 with H-1′ and H-9′, and of H-15 with H-8′, and of H-14 (and Me-25) with H-6′ (per Faraj 2023 for embellicine E) put the OMe-bearing C-1′ on the same face as H-9′ side. **Confidence: medium** — this constraint needs to be transcribed from Chen 2019 Figure 2 directly.

---

## Section 3 — SMILES

**This is a *proposed* SMILES requiring Ivan's audit before any encoding.** It encodes the connectivity above and the (1*S*, 4*R*, 7*S*, 8*S*, 10*R*, 12*S*, 13*R*, 14*R*, 15*S*, 16*S*, 1′*R*, 2′*R*) stereochemistry but **does not encode atropoisomerism** of the *para*-arene (SMILES has no syntax for that; in V2000 Molfile it has to be modeled by the 3D coordinates or by stereo flags at the arene carbons).

Achiral (planar-structure-only) SMILES — for sanity-checking molecular formula and connectivity:

```
CC1=CC2(C)C(=C(C)C3CC(C)CC(C)C3C4OC5=CC=C(C=C5)CC6(O)NC(=O)C(=C(O)C4C12)C6OC)C
```

Hand-checked atom count: 35 C, 1 N, 5 O. Hydrogens: implicit, RDKit-canonical Hs gives 45. **C₃₅H₄₅NO₅** ✓

A stereo-decorated SMILES (12 of the 12 sp³ stereocenters; atropoisomerism omitted; the C-17 enol is written in the keto form for clarity):

```
C[C@@H]1[C@@]2(C)C=C(C)[C@@]3(C[C@@H](C)C[C@@H](C)[C@@H]3[C@H]4OC5=CC=C(C=C5)C[C@]6(O)NC(=O)C(=O)C(=C4C12)C6OC)C
```

⚠ **This stereo-SMILES is structurally consistent but several wedge directions are inferred rather than read directly from Chen 2019 Figure 2.** The 2D wedge pattern in Figure 2 should be the source of truth. *Do not* commit this to `structure.mol` without comparison against the published Figure 2 and (ideally) the CIF.

---

## Section 4 — Proposed V2000 Molfile (DRAFT — REQUIRES AUDIT)

**Status**: I have *not* written this file because the wisest path is to:

1. Get Chen 2019 SI (the embedded CIF gives all 3D coordinates with proper stereo).
2. Convert via `obabel ascomylactam_a.cif -O structure.mol -h --gen3d` (you may not need `--gen3d` if the CIF already has coords).
3. Sanity-check the resulting V2000 against Figure 2 by visual inspection.

If you nevertheless want a placeholder built from the SMILES above, you can do this safely with:

```bash
echo "C[C@@H]1[C@@]2(C)C=C(C)[C@@]3(C[C@@H](C)C[C@@H](C)[C@@H]3[C@H]4OC5=CC=C(C=C5)C[C@]6(O)NC(=O)C(=O)C(=C4C12)C6OC)C" | \
  obabel -ismi -omol --gen2d -O ascomylactam_a_provisional.mol
```

and then label the file with `Origin: provisional, derived from analog congener NMR + Faraj 2023 comparison, NOT from Chen 2019 X-ray. Subject to replacement.`

A V2000 Molfile **must** carry:
- 41 heavy atoms (35 C + 5 O + 1 N).
- 45 bonds (counted from the SMILES: 35 + 5 + 1 − 1 + (number of rings) = 40 + 5 rings = 45). *Quick sanity check pending.*
- Stereo flags: 12 sp³ stereocenters need wedge bonds set; 4 sp² geometries (the two arene C=C bonds plus the C17=C18 enol and the conjugated diene of ring B) need cis/trans or "E/Z" flags (cyclic so technically not needed).
- A free-text comment line citing Chen 2019 + the CCDC number.

If the CCDC CIF is available, the proper invocation is

```bash
obabel input.cif -O structure.mol
```

which preserves the X-ray coordinates and 3D stereo without requiring re-perception.

---

## Section 5 — Open questions / encoding caveats

These are **all** items that should be flagged for Ivan's audit before the M5 run begins:

1. **CCDC numbers**: the CCDC numbers for ascomylactams A and B are reported in the SI of Chen 2019, not in the abstract. Ascomylactam D was deposited as **CCDC 2282137** (per the Fitoterapia paper); ascomylactams A and B were deposited 4 years earlier and likely have CCDC numbers in the **186xxxx range** (typical for 2018–2019 deposits). *Ivan should look these up via the CCDC search interface at https://www.ccdc.cam.ac.uk/structures/search?DOI=10.1021/acs.jnatprod.8b00918*

2. **Tautomer ambiguity at C-17**: in the keto form, C-17 is a ketone (δ_C ~199 ppm in phomapyrrolidone A and AsC). In the enol form (which dominates for AsA, embellicine B, and embellicine E because of the intramolecular H-bond from the C-17 OH to the ring nitrogen), C-17 is an enol (δ_C ~170 ppm, ¹H δ ~12 ppm). The enol form is the **correct ground-state for V2000 encoding**. Confirm against Figure 2.

3. **C-2′ hemiaminal**: in AsA the C-2′ is an sp³ quaternary bearing OH + N + C-1′ + C-3′. The OH is genuine (not an artifact of tautomerization — confirmed by the ¹³C δ ~85 ppm for AsA / embellicine C / embellicine E). This is a stable hemiaminal because it is locked into the 5-membered γ-lactam ring. **Configuration at C-2′ is *R* by the X-ray of AsC and by ECD correlation to embellicine E (also *R*).**

4. **Atropoisomerism**: the para-arene is locked. In standard V2000 this is impossible to encode atropwise. The standard hack is to use 3D coordinates from the X-ray and let downstream tools detect the restricted-rotation. **If the M5 pipeline cares about atropoisomers (e.g., for retrosynthesis with rotation-sensitive transition states), Ivan must adjust the encoding strategy.**

5. **Conjugation map for ring A+B**: rings A and B share an edge, and the diene system spans C-2=C-3 (within A) + C-5=C-6 (within B). C-3—C-4 and C-4—C-16 are single bonds. C-5—C-15 (or wherever ring B closes back to ring D) is a single bond. The C-3—C-4—C-5 path is sp²–sp³–sp²; C-4 is the **sp³ quaternary** bearing Me-22 (this is the locked configuration confirmed by X-ray). **This is exactly the architecture that the Uchiro 2026 IMDA synthesis builds: an A/B-cis-fused cyclopenta[b]fluorene** — the synthesis confirms cis fusion at C-4/C-16, which means H-16 and Me-22 are on the same face. Use this to set wedge directions.

6. **Ring fusion stereo (ring A / ring B)**: the **A/B-cis fusion** is the natural-product geometry. The H-1/Me-20 stereochemistry at C-1 and the H-16 stereochemistry at C-16 lock onto opposite faces in (1*S*, 16*S*) — H-1 is on one face, H-16 on the other; Me-20 and Me-22 are on the same face. Verify against Figure 2 wedges.

7. **The C-13 stereo (ring C / ring D junction)**: H-13 is the methine that bridges ring C and ring D. C-13 was reported as (R) for embellicine E (per Faraj 2023). NOESY in embellicines shows H-13 and Me-25 on the same face, opposite to H-7/H-15/H-16. Carry this assignment through to AsA (Faraj said only C-1, C-4, C-7 are inverted between AsA and embellicine E; so C-13 stays *R*).

8. **The molecular formula written by Chen 2019** (C₃₅H₄₅NO₅) ⇒ DBE 14. Counting from my proposed structure: 5 rings (A, B, C, D, E + the γ-lactam F = 6 actually if we count F as a separate ring; but ring F shares an edge with ring E. RDKit will compute 6 SSSR). 6 rings + 4 aromatic C=C + 1 enol C=C + 1 amide C=O + 1 ring-A C=C + 1 ring-B C=C = 14. **Computed DBE: 14**. ✓ Match.

9. **The 13-membered ring count**: AsA has the **13-membered** macrocycle; AsC has the same 13-membered ring (planar structure identical, differs in stereo and lacks the methoxy/enol). Wait — **the abstract says ascomylactams A–C are "12- or 13-membered-ring".** The 12-vs-13 distinction must refer to which compounds are which. Phomapyrrolidone A (= AsB's planar twin? no, AsA's planar twin) was originally drawn with a **succinimide** instead of γ-lactam — that gives a smaller macrocycle. **This needs Ivan's verification against the AsC paper text in Marine Drugs 2023, which I read in detail and confirms AsC is "13-membered-ring" with γ-lactam.** AsA also has the γ-lactam → 13-membered. **AsB has a succinimide instead → likely 12-membered.** ⚠ Worth confirming.

10. **Ivan: do not run the M5 ascomylactam pipeline without an audit pass on the wedge directions in the resulting Molfile.** Twelve stereocenters compounded with the atropoisomer and the enol tautomer is a perfect storm for silent encoding errors.

---

## Section 6 — References (full DOI list)

| Reference | DOI |
| --- | --- |
| **Chen 2019 (primary)** — Ascomylactams A–C, *J. Nat. Prod.* 82, 1752 | [10.1021/acs.jnatprod.8b00918](https://doi.org/10.1021/acs.jnatprod.8b00918) |
| Wijeratne 2013 — Phomapyrrolidones A–C, *J. Nat. Prod.* 76, 1860 | [10.1021/np400391p](https://doi.org/10.1021/np400391p) |
| Ebrahim 2013 — Embellicines A and B, *J. Med. Chem.* 56, 2991 | [10.1021/jm400034b](https://doi.org/10.1021/jm400034b) |
| Ariantari 2020 — Didymellanosine, *RSC Adv.* 10, 7232 | [10.1039/C9RA10685E](https://doi.org/10.1039/C9RA10685E) |
| Wang 2020 — AsA / lung cancer, *Mar. Drugs* 18, 494 | [10.3390/md18100494](https://doi.org/10.3390/md18100494) |
| Faraj 2023 — Embellicines C–E, *J. Nat. Prod.* 86, 514 | [10.1021/acs.jnatprod.2c01048](https://doi.org/10.1021/acs.jnatprod.2c01048) |
| Huang 2023 — AsC / ICD, *Mar. Drugs* 21, 600 | [10.3390/md21120600](https://doi.org/10.3390/md21120600) |
| Yuan 2023 — Ascomylactams D, E, *Fitoterapia* 171, 105692 | [10.1016/j.fitote.2023.105692](https://doi.org/10.1016/j.fitote.2023.105692) |
| Chen 2024 — Didymorenloids A, B, *Org. Chem. Front.* 11, 1706 | [10.1039/D3QO01917A](https://doi.org/10.1039/D3QO01917A) |
| Sakai 2026 — IMDA synthesis of embellicine A core, *Org. Lett.* 28, 1510 | (DOI not visible on TUS page; *Org. Lett.* 2026, 28, 1510–1514) |
| Sugata 2017 — GKK1032A2 13-ring macrocyclization, *Chem. Asian J.* 12, 628 | [10.1002/asia.201601518](https://doi.org/10.1002/asia.201601518) |

---

## Recommended next steps for Ivan

1. **Get the PDF and SI of Chen 2019.** ACS via Sun Yat-Sen University library, ResearchGate, an author email to Zhigang She (cesshzhg@mail.sysu.edu.cn), or a hand-pull through your Stanford / personal-network access. The SI almost certainly embeds the CIF as ASCII text.
2. **Pull the CIF from CCDC** for DOI 10.1021/acs.jnatprod.8b00918 (free for "structure on request").
3. **Convert the CIF to V2000** via `obabel ascomylactam_a.cif -O structure.mol`.
4. **Eyeball the wedges** against the Figure 2 / Figure S? drawing in the Chen 2019 paper.
5. **Set `runspec.yaml: target.confirmed_by = "X-ray, CCDC #?????"`** and proceed to M5.

If Ivan wants a placeholder `structure.mol` for plumbing checks **before** getting the CIF, use the SMILES in §3 and label it provisional.
