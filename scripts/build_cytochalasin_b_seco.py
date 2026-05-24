"""Derive the HWE seco-precursor for cytochalasin B (Haidle-Myers 2004).

The closure rule is `hwe_olefination`:
    (MeO)2P(O)-CH2-C(=O)-O-R'  +  R''-CHO  →
        R'-O-C(=O)-CH=CH-R''  +  (MeO)2P(O)OH

So the seco precursor is the cyclized cytochalasin B with the
HWE-formed in-ring alkene cleaved. In Haidle-Myers's Scheme 7 the
HWE bond closes the α,β-unsaturated ester portion of the macrolactone
(compound 3 -> macrolactone 40 at 65% yield, NaOCH2CF3/CF3CH2OH/DME,
23 C). After cleavage:
  - the side conjugated to the macrolactone C(=O) becomes
    -CH2-P(=O)(OCH3)2 (the phosphonoacetate ester moiety)
  - the other side becomes -CHO (the aldehyde end of the long tether)

The macrolactone ester (R'-O-C(=O)-) is preserved in the seco
precursor — only the C=C alkene is opened. The seco molecule does
NOT split into two fragments because the perhydroisoindolone core
connects the two halves of the broken macrocycle through a single
fused-bicycle path; opening the 14-ring leaves the molecule
connected via the 5-ring lactam and the 6-ring cyclohexane.

Mass balance (dimethyl phosphonate variant):
    seco MW = cyclized MW + 126.05 g/mol  (= (MeO)2P(O)OH, dimethyl
                                             phosphate conjugate acid)
i.e., the HWE byproduct is the same as the rule's
byproduct_mass_g_per_mol = 126.05.

Procedure (RDKit):
1. Parse the cyclized cytochalasin B SMILES (PubChem CID 5311281).
2. Identify the unique α,β-unsaturated-ester in-ring C=C (the
   HWE-formed bond — the C=C adjacent to the macrolactone C(=O)).
3. Break that C=C; on the carbonyl-adjacent side, append
   -CH2-P(=O)(OC)(OC) (dimethyl phosphonoacetate ester); on the other
   side, replace with =O to make an aldehyde -CHO.
4. Verify Δ MW = +126.05 g/mol (dimethyl phosphate conjugate acid).
5. Write `data/building_blocks/cytochalasin_b_seco.yaml`.

Refs:
- Haidle & Myers 2004 PNAS 101:12048, DOI:10.1073/pnas.0402111101
- docs/hwe_olefination_research.md §2, §5
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cyclized cytochalasin B (from scripts/build_cytochalasin_b.py /
# PubChem CID 5311281 isomeric SMILES).
CYCLIZED_SMILES = (
    "C[C@@H]1CCC[C@H](/C=C/C(=O)O[C@]23[C@@H](/C=C/C1)"
    "[C@@H](C(=C)[C@H]([C@H]2[C@@H](NC3=O)CC4=CC=CC=C4)C)O)O"
)

# (MeO)2P(O)OH dimethyl phosphate conjugate acid: 126.05 g/mol.
# See docs/hwe_olefination_research.md §2.4 and
# data/rules/hwe_olefination.meta.yaml `byproduct_mass_g_per_mol: 126.05`.
DIMETHYL_PHOSPHATE_MW_EXACT = 126.0082    # exact mass of (MeO)2P(O)OH = C2H7O4P
DIMETHYL_PHOSPHATE_MW_AVG = 126.05        # average MW


def _find_hwe_alkene_bond(mol: Chem.Mol) -> tuple[int, int, int]:
    """Find the C=C bond formed by HWE: the α,β-unsaturated-ester in-ring alkene.

    Returns (bond_idx, alpha_C_idx, beta_C_idx) where:
      - alpha_C: the alkene C bonded to the macrolactone C(=O); becomes
        the -CH2-P(=O)(OMe)2 side of the seco precursor.
      - beta_C: the alkene C bonded to the aliphatic tether; becomes
        the -CHO (aldehyde) end.

    The macrolactone has two in-14-ring C=C alkenes; the HWE one is the
    α,β-unsaturated ester (conjugated to the lactone C(=O)). The other
    in-ring alkene is the isolated C20=C21 trans-alkene from the seco
    precursor (already present before HWE).
    """
    target_ring_size = 14
    candidates = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        if bond.GetIsAromatic():
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        if not bond.IsInRingSize(target_ring_size):
            continue
        # Check if either end is alpha to an ester carbonyl in the
        # 14-ring: i.e., bonded to a carbon that is in turn doubly bonded
        # to an O *and* singly bonded to an O (the ester O of the lactone).
        for end_atom, other_atom in ((a, b), (b, a)):
            for nbr in end_atom.GetNeighbors():
                if nbr.GetIdx() == other_atom.GetIdx():
                    continue
                if nbr.GetSymbol() != "C":
                    continue
                if not nbr.IsInRingSize(target_ring_size):
                    continue
                # Check it's an ester carbonyl C: has =O and -O- substituents
                has_carbonyl_O = False
                has_ester_O = False
                for nn in nbr.GetNeighbors():
                    if nn.GetSymbol() != "O":
                        continue
                    bond_nn = mol.GetBondBetweenAtoms(nbr.GetIdx(), nn.GetIdx())
                    if bond_nn.GetBondType() == Chem.BondType.DOUBLE:
                        has_carbonyl_O = True
                    elif bond_nn.GetBondType() == Chem.BondType.SINGLE:
                        has_ester_O = True
                if has_carbonyl_O and has_ester_O:
                    candidates.append(
                        (bond.GetIdx(), end_atom.GetIdx(), other_atom.GetIdx())
                    )
                    break
    # Deduplicate (bond may appear twice if both ends look ester-conjugated,
    # which would be unusual but handle it).
    unique = list({c[0]: c for c in candidates}.values())
    if len(unique) != 1:
        raise RuntimeError(
            f"Expected exactly one α,β-unsaturated-ester in-14-ring alkene "
            f"(the HWE bond); found {len(unique)}: {unique}"
        )
    return unique[0]


def derive_seco_smiles(cyclized_smiles: str) -> tuple[str, dict]:
    """Return (seco_isomeric_smiles, info_dict)."""
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict[str, object] = {}
    info["cyclized_formula"] = CalcMolFormula(mol)
    info["cyclized_exact_mw"] = Descriptors.ExactMolWt(mol)
    info["cyclized_mol_wt"] = Descriptors.MolWt(mol)

    bond_idx, alpha_idx, beta_idx = _find_hwe_alkene_bond(mol)
    info["broken_bond"] = (alpha_idx, beta_idx)

    rw = Chem.RWMol(mol)
    # Break the in-ring C=C (this opens the macrocycle to a seco chain).
    rw.RemoveBond(alpha_idx, beta_idx)

    # On the alpha-C side (adjacent to the lactone C(=O)): bond alpha-C
    # *directly* to a new -P(=O)(OMe)(OMe). The alpha-C IS the phosphonate's
    # methylene α-C in the seco precursor (the substrate fragment is
    # R'-O-C(=O)-CH2-P(=O)(OMe)2, where the CH2 is the alpha-C); it goes
    # from sp2 alkene C in the cyclized to sp3 -CH2- in the seco (RDKit
    # adds the implicit H automatically when the bond count changes).
    phosphorus = rw.AddAtom(Chem.Atom("P"))
    p_double_o = rw.AddAtom(Chem.Atom("O"))       # the P=O
    p_o_me_1 = rw.AddAtom(Chem.Atom("O"))         # first -O-Me
    p_o_me_2 = rw.AddAtom(Chem.Atom("O"))         # second -O-Me
    me_1 = rw.AddAtom(Chem.Atom("C"))
    me_2 = rw.AddAtom(Chem.Atom("C"))

    rw.AddBond(alpha_idx, phosphorus, Chem.BondType.SINGLE)
    rw.AddBond(phosphorus, p_double_o, Chem.BondType.DOUBLE)
    rw.AddBond(phosphorus, p_o_me_1, Chem.BondType.SINGLE)
    rw.AddBond(phosphorus, p_o_me_2, Chem.BondType.SINGLE)
    rw.AddBond(p_o_me_1, me_1, Chem.BondType.SINGLE)
    rw.AddBond(p_o_me_2, me_2, Chem.BondType.SINGLE)

    # On the beta-C side (originally the aldehyde C of the seco): add =O
    # to make a -CHO aldehyde. beta-C is sp2 with =O and one H plus its
    # existing tether neighbour.
    cho_o = rw.AddAtom(Chem.Atom("O"))
    rw.AddBond(beta_idx, cho_o, Chem.BondType.DOUBLE)

    # Reset any stereo flags on the two former-sp2 carbons (the geometry
    # information no longer applies once one becomes sp3 and the other
    # becomes a planar aldehyde).
    for idx in (alpha_idx, beta_idx):
        atom = rw.GetAtomWithIdx(idx)
        atom.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)

    seco = rw.GetMol()
    Chem.SanitizeMol(seco)
    Chem.AssignStereochemistry(seco, cleanIt=True, force=True)

    info["seco_formula"] = CalcMolFormula(seco)
    info["seco_exact_mw"] = Descriptors.ExactMolWt(seco)
    info["seco_mol_wt"] = Descriptors.MolWt(seco)
    info["delta_mw_exact"] = info["seco_exact_mw"] - info["cyclized_exact_mw"]
    info["delta_mw_avg"] = info["seco_mol_wt"] - info["cyclized_mol_wt"]
    info["expected_delta_mw_avg"] = DIMETHYL_PHOSPHATE_MW_AVG
    info["expected_delta_mw_exact"] = DIMETHYL_PHOSPHATE_MW_EXACT

    seco_rings = sorted(len(r) for r in seco.GetRingInfo().AtomRings())
    info["seco_ring_sizes"] = seco_rings

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(CYCLIZED_SMILES)
    print(f"cyclized formula      : {info['cyclized_formula']}  "
          f"(MW {info['cyclized_mol_wt']:.4f}, exact {info['cyclized_exact_mw']:.4f})")
    print(f"seco formula          : {info['seco_formula']}  "
          f"(MW {info['seco_mol_wt']:.4f}, exact {info['seco_exact_mw']:.4f})")
    print(f"Δ MW avg (seco-cyc)   : {info['delta_mw_avg']:.4f}  "
          f"(expected (MeO)2P(O)OH ≈ {DIMETHYL_PHOSPHATE_MW_AVG})")
    print(f"Δ MW exact (seco-cyc) : {info['delta_mw_exact']:.4f}  "
          f"(expected (MeO)2P(O)OH exact ≈ {DIMETHYL_PHOSPHATE_MW_EXACT})")
    print(f"seco ring sizes       : {info['seco_ring_sizes']}  "
          f"(expect [5, 6, 6] — 14-ring opened, others remain)")
    print()
    print("seco SMILES:")
    print(seco_smiles)

    # Mass balance audit: the seco MW minus the cyclized MW must equal the
    # dimethyl phosphate conjugate acid byproduct (126.05 g/mol average,
    # 126.0082 exact).
    if abs(info["delta_mw_avg"] - DIMETHYL_PHOSPHATE_MW_AVG) > 0.05:
        raise SystemExit(
            f"Mass balance failed (avg): Δ = {info['delta_mw_avg']:.4f}, "
            f"expected ≈ {DIMETHYL_PHOSPHATE_MW_AVG}"
        )
    if abs(info["delta_mw_exact"] - DIMETHYL_PHOSPHATE_MW_EXACT) > 0.05:
        raise SystemExit(
            f"Mass balance failed (exact): Δ = {info['delta_mw_exact']:.4f}, "
            f"expected ≈ {DIMETHYL_PHOSPHATE_MW_EXACT}"
        )
    if info["seco_ring_sizes"] != [5, 6, 6]:
        raise SystemExit(
            f"Seco ring inventory unexpected: got {info['seco_ring_sizes']}, "
            "expected [5, 6, 6] (14-ring opened; perhydroisoindolone bicycle + phenyl stay)"
        )

    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "cytochalasin_b_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        "name: cytochalasin B seco-aldehyde phosphonoacetate (HWE precursor)\n"
        f"smiles: {seco_smiles}\n"
        "provenance: |\n"
        "  Seco-precursor for the Haidle-Myers 2004 intramolecular\n"
        "  Horner-Wadsworth-Emmons (HWE) closure of cytochalasin B's\n"
        "  14-membered macrolactone (PNAS 101:12048-12053,\n"
        "  DOI:10.1073/pnas.0402111101; PMC PMC514432, open access).\n"
        "  Derived programmatically from the cyclized natural-product\n"
        "  cytochalasin B (PubChem CID 5311281, ChEBI:23528,\n"
        "  C29H37NO5 MW 479.62) by breaking the in-ring α,β-unsaturated\n"
        "  ester C=C alkene (the bond formed by HWE in Scheme 7) and:\n"
        "    (a) attaching -CH2-P(=O)(OCH3)2 to the alpha-C (the\n"
        "        phosphonoacetate ester side), and\n"
        "    (b) attaching =O to the other side to make an aldehyde\n"
        "        (the ω-CHO end of the long aliphatic tether).\n"
        "  The macrolactone ester bond (R'-O-C(=O)-) is preserved in\n"
        "  the seco precursor — only the C=C alkene is opened. This\n"
        "  matches Haidle-Myers's actual route: the macrolactone is\n"
        "  pre-installed (compound 3 in Scheme 7; DCC coupling of\n"
        "  diethylphosphonoacetic acid in step e at 81% yield) and the\n"
        "  HWE closure (step f, NaOCH2CF3 in CF3CH2OH/DME at 23 C, 65%)\n"
        "  forms only the C13=C14 alkene that closes the macrocycle.\n"
        "notes: |\n"
        "  Mass balance verified by build script:\n"
        f"    cyclized MW (avg)    = {info['cyclized_mol_wt']:.4f}\n"
        f"    seco MW (avg)        = {info['seco_mol_wt']:.4f}\n"
        f"    Δ MW (avg)           = {info['delta_mw_avg']:.4f}\n"
        f"    (MeO)2P(O)OH MW avg  = {DIMETHYL_PHOSPHATE_MW_AVG:.4f}  ← dimethyl phosphate conjugate acid\n"
        f"\n"
        f"    cyclized MW (exact)  = {info['cyclized_exact_mw']:.4f}\n"
        f"    seco MW (exact)      = {info['seco_exact_mw']:.4f}\n"
        f"    Δ MW (exact)         = {info['delta_mw_exact']:.4f}\n"
        f"    (MeO)2P(O)OH exact   = {DIMETHYL_PHOSPHATE_MW_EXACT:.4f}\n"
        "\n"
        "  Stereocenters preserved: the seco retains all sp3 chiral\n"
        "  centres of the cyclized cytochalasin B EXCEPT the two\n"
        "  alkene-forming carbons (originally sp2 in cyclized; the\n"
        "  alpha-C becomes sp3 CH2 of phosphonate in the seco, and the\n"
        "  beta-C becomes the planar CHO of the aldehyde). The other\n"
        "  in-14-ring alkene (C20=C21, isolated trans-alkene retained\n"
        "  through HWE) is preserved with E geometry.\n"
        "\n"
        "  Phosphonate variant: dimethyl phosphonate (canonical;\n"
        "  matches data/rules/hwe_olefination.meta.yaml\n"
        "  reagent_mass_alternatives.canonical_NaH_dimethyl entry,\n"
        "  byproduct_mass_g_per_mol = 126.05 g/mol). The actual\n"
        "  Haidle-Myers 2004 paper uses the diethyl variant\n"
        "  ((EtO)2P(O)CH2C(O)O-) on a slightly different substrate, but\n"
        "  the rule body is variant-agnostic — the OR groups on P live\n"
        "  in off-rule substrate context. The seco YAML uses dimethyl\n"
        "  for the canonical-mass demonstration.\n"
        "\n"
        "  HWE conditions per Haidle-Myers 2004 (Scheme 7, step f):\n"
        "    NaOCH2CF3 (sodium 2,2,2-trifluoroethoxide) in\n"
        "    CF3CH2OH/DME, 23 °C, 65% yield, single (E) diastereomer.\n"
        "  These are the epimerization-suppressed Haidle-Myers\n"
        "  conditions; see hwe_olefination.meta.yaml\n"
        "  reagent_mass_alternatives.haidle_myers (DOI:10.1073/pnas.0402111101).\n"
        "refs:\n"
        "  - \"Haidle, A. M.; Myers, A. G. Proc. Natl. Acad. Sci. USA 2004, 101, 12048-12053 (DOI:10.1073/pnas.0402111101) — primary reference, HWE macrocyclization of cytochalasin B (compound 3 → 40, 65%) and L-696,474 (compound 11 → 36, 52%, 5:1 dr).\"\n"
        "  - \"Wadsworth, W. S.; Emmons, W. D. J. Am. Chem. Soc. 1961, 83, 1733 (DOI:10.1021/ja01468a042) — original HWE method.\"\n"
        "  - \"PubChem CID 5311281; ChEBI:23528 — cytochalasin B structural data, C29H37NO5 MW 479.62, CAS 14930-96-2.\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
