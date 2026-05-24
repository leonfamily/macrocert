"""Derive the RCM seco-precursor for the Trost ring-expanded bryostatin analogue.

The closure rule is `rcm`:
    Calpha=CH2  +  H2C=Cbeta  ->  Calpha=Cbeta  +  H2C=CH2 (ethylene)

The macrolactone ester (C(=O)-O) of the 31-ring is already established
in the seco precursor — Trost-Yang-Thiel-Frontier-Brindle 2007 macro-
lactonize the seco-acid BEFORE the RCM step (the alternative — RCM on
the diene-diacid then lactonization — was found inferior; see
research_brief.md and the Jahan 2023 review Scheme 19). So we open the
in-ring C=C and cap each side with =CH2 to recover the seco diene.

The molecule does NOT split into two fragments because the macrolactone
ester provides the second connection between the two halves; this matches
the topology of Nicolaou's epothilone B RCM seco (see
scripts/build_epothilone_seco.py).

Procedure:
1. Parse the cyclized SMILES authored in scripts/build_trost_bryostatin_analogue.py.
2. Find the unique in-ring non-aromatic C=C bond inside the 31-ring
   (the C16-C17 RCM bond; the in-ring lactone C=O is excluded by the
   C=C constraint).
3. Break that double bond; cap each side with a terminal =CH2.
4. Sanitize, canonicalize, verify mass balance:
   delta MW(seco - cyclized) = MW(ethylene) ~ 28.0313 Da.
5. Verify that the 31-ring is gone and only the two pyranose 6-rings
   remain in the seco.
6. Write data/building_blocks/trost_bryostatin_analogue_seco.yaml.

Refs:
- Trost, B. M.; Yang, H.; Thiel, O. R.; Frontier, A. J.; Brindle, C. S.
  J. Am. Chem. Soc. 2007, 129, 2206 (DOI 10.1021/ja067305j).
- Trost, B. M.; Yang, H.; Dong, G. Chem. Eur. J. 2011, 17, 9789
  (DOI 10.1002/chem.201002932).
- Jahan, N. et al. SynOpen 2023, 7, 209 (DOI 10.1055/s-0042-1751453,
  open-access redrawing of compounds 175-179).
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cyclized 31-membered Trost analogue (output of build_trost_bryostatin_analogue.py).
CYCLIZED_SMILES = (
    "O=C1OCC[C@H](OC(=O)/C=C(\\C)/C(=O)OC)C"
    "[C@@H]3O[C@@H](O)C[C@@H](O)[C@H]3"
    "CCC[C@@H](OC(C)=O)"
    "/C=C/"
    "CCCC"
    "[C@@H]4OC[C@H](OC(C)=O)C[C@H]4"
    "CCCCCCCCCCC1"
)

ETHYLENE_EXACT_MW = 28.0313  # C2H4 exact mass (Da)
MACROCYCLE_SIZE = 31


def _find_rcm_alkene_bond(mol: Chem.Mol) -> int:
    """Return the bond index of the in-ring non-aromatic C=C alkene.

    The cyclized Trost analogue has exactly one such bond in the
    31-ring (the C16-C17 RCM bond; the lactone in-ring C=O is excluded
    by requiring both endpoints to be carbon).
    """
    ri = mol.GetRingInfo()
    macro = None
    for r in ri.AtomRings():
        if len(r) == MACROCYCLE_SIZE:
            macro = set(r)
            break
    if macro is None:
        raise RuntimeError(f"No {MACROCYCLE_SIZE}-membered ring found in cyclized structure")

    candidates = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetIsAromatic() or b.GetIsAromatic():
            continue
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        if a.GetIdx() in macro and b.GetIdx() in macro:
            candidates.append(bond.GetIdx())
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one in-ring C=C alkene (the RCM bond); "
            f"got {len(candidates)} candidates: {candidates}"
        )
    return candidates[0]


def derive_seco_smiles(cyclized_smiles: str) -> tuple[str, dict]:
    """Return (seco_isomeric_smiles, info_dict)."""
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict[str, object] = {}
    info["cyclized_formula"] = CalcMolFormula(mol)
    info["cyclized_exact_mw"] = Descriptors.ExactMolWt(mol)

    bond_idx = _find_rcm_alkene_bond(mol)
    bond = mol.GetBondWithIdx(bond_idx)
    a_idx, b_idx = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
    info["broken_bond"] = (a_idx, b_idx)

    rw = Chem.RWMol(mol)
    rw.RemoveBond(a_idx, b_idx)
    new_a = rw.AddAtom(Chem.Atom("C"))
    new_b = rw.AddAtom(Chem.Atom("C"))
    rw.AddBond(a_idx, new_a, Chem.BondType.DOUBLE)
    rw.AddBond(b_idx, new_b, Chem.BondType.DOUBLE)

    # Clear chirality on former-alkene carbons (now terminal vinyls).
    for idx in (a_idx, b_idx):
        atom = rw.GetAtomWithIdx(idx)
        atom.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)

    seco = rw.GetMol()
    Chem.SanitizeMol(seco)
    Chem.AssignStereochemistry(seco, cleanIt=True, force=True)

    info["seco_formula"] = CalcMolFormula(seco)
    info["seco_exact_mw"] = Descriptors.ExactMolWt(seco)
    info["delta_mw"] = info["seco_exact_mw"] - info["cyclized_exact_mw"]
    info["expected_delta_mw"] = ETHYLENE_EXACT_MW

    seco_rings = sorted(len(r) for r in seco.GetRingInfo().AtomRings())
    info["seco_ring_sizes"] = seco_rings

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(CYCLIZED_SMILES)
    print(f"cyclized formula      : {info['cyclized_formula']}  "
          f"(MW {info['cyclized_exact_mw']:.4f})")
    print(f"seco formula          : {info['seco_formula']}  "
          f"(MW {info['seco_exact_mw']:.4f})")
    print(f"delta MW (seco-cyclized): {info['delta_mw']:.4f}  "
          f"(expected ethylene ~ {ETHYLENE_EXACT_MW})")
    print(f"seco ring sizes       : {info['seco_ring_sizes']}  "
          f"(expect just the two pyranose 6-rings)")
    print()
    print("seco SMILES:")
    print(seco_smiles)

    if abs(info["delta_mw"] - ETHYLENE_EXACT_MW) > 0.01:
        raise SystemExit(
            f"Mass balance failed: delta = {info['delta_mw']:.4f}, "
            f"expected ~ {ETHYLENE_EXACT_MW}"
        )
    if info["seco_ring_sizes"] != [6, 6]:
        raise SystemExit(
            f"Seco ring inventory unexpected: got {info['seco_ring_sizes']}, "
            "expected [6, 6] (two pyranoses; the 31-ring should be open)"
        )

    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "trost_bryostatin_analogue_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        "name: Trost bryostatin analogue seco-diene (RCM precursor)\n"
        f"smiles: {seco_smiles}\n"
        "provenance: |\n"
        "  Seco-precursor for the Trost-Yang-Thiel-Frontier-Brindle 2007\n"
        "  RCM closure of the ring-expanded bryostatin analogue\n"
        "  (J. Am. Chem. Soc. 129, 2206-2207, DOI 10.1021/ja067305j;\n"
        "  full paper Chem. Eur. J. 2011, 17, 9789-9805, DOI\n"
        "  10.1002/chem.201002932; open-access redrawing in Jahan 2023\n"
        "  SynOpen 7, 209-242 Scheme 19, DOI 10.1055/s-0042-1751453).\n"
        "  Derived programmatically from the cyclized 31-membered\n"
        "  macrolactone (formula C46H74O14, MW 850.51) by breaking the\n"
        "  in-ring C=C alkene of the macrocycle and capping each side\n"
        "  with a terminal CH2= group.\n"
        "\n"
        "  The macrolactone ester (C(=O)-O) is RETAINED in the seco --\n"
        "  Trost's actual route runs macrolactonization (Shiina or\n"
        "  Yamaguchi) BEFORE the RCM step. The two terminal alkenes\n"
        "  at former-C16 and former-C17 are the dienes consumed by\n"
        "  Grubbs-Hoveyda 2nd-generation catalyst in benzene at\n"
        "  50-80 C and high dilution, expelling ethylene as the RCM\n"
        "  byproduct (80% yield, 1:1 E:Z mixture chromatographically\n"
        "  separated downstream).\n"
        "notes: |\n"
        "  Mass balance verified by build script:\n"
        f"    cyclized MW         = {info['cyclized_exact_mw']:.4f}\n"
        f"    seco MW             = {info['seco_exact_mw']:.4f}\n"
        f"    delta MW            = {info['delta_mw']:.4f}\n"
        f"    ethylene (C2H4) MW  = {ETHYLENE_EXACT_MW:.4f}\n"
        "\n"
        "  31-MEMBERED RING OUTLIER: this case exercises Macrocert's\n"
        "  ring_size_equals(31) predicate at the upper end of the\n"
        "  panel's ring-size range. All other panel cases are 12-16\n"
        "  membered; the bryostatin natural macrocycle is 26-membered.\n"
        "  Trost's seco-precursor inserts one extra -CH2- versus the\n"
        "  natural seco, relocating the RCM alkene to a less-strained\n"
        "  position and expanding the ring to 31 members. The RDKit\n"
        "  SSSR perimeter walk recovers exactly 31 atoms in the macro-\n"
        "  cycle of the cyclized form.\n"
        "\n"
        "  E/Z selectivity caveat: Trost reports 1:1 E:Z; both isomers\n"
        "  were chromatographically separated and biologically evaluated\n"
        "  (compounds 178/179 in Jahan 2023 numbering). The panel rule\n"
        "  rcm is selectivity-agnostic in v0; the encoded cyclized\n"
        "  structure carries E geometry on the new alkene by convention\n"
        "  (the E isomer happens to be the more abundant in many bryo-\n"
        "  family RCMs; either is a valid panel target).\n"
        "\n"
        "  ENCODING CAVEAT: the analogue is NOT in PubChem/ChEBI/CCDC.\n"
        "  The cyclized structure is a chemistry-faithful encoding\n"
        "  capturing the essential macrocyclic features that Macrocert\n"
        "  cares about (31-ring, RCM C=C, lactone, two pyranoses,\n"
        "  characteristic OAc/OH/cinnamate substituents). It is NOT a\n"
        "  precise atom-by-atom reproduction of Trost compound 3 --\n"
        "  see scripts/build_trost_bryostatin_analogue.py docstring for\n"
        "  the full encoding contract.\n"
        "\n"
        "  Topology check: the seco retains the two pyranose 6-rings\n"
        f"  (ring inventory {info['seco_ring_sizes']}) and is acyclic at\n"
        "  the macrocycle level; the macrolactone tether keeps the\n"
        "  molecule connected after breaking the alkene.\n"
        "refs:\n"
        "  - \"Trost, B. M.; Yang, H.; Thiel, O. R.; Frontier, A. J.; Brindle, C. S. J. Am. Chem. Soc. 2007, 129, 2206-2207 (DOI:10.1021/ja067305j) -- primary\"\n"
        "  - \"Trost, B. M.; Yang, H.; Dong, G. Chem. Eur. J. 2011, 17, 9789-9805 (DOI:10.1002/chem.201002932) -- full paper\"\n"
        "  - \"Jahan, N. et al. SynOpen 2023, 7, 209-242, Scheme 19 (DOI:10.1055/s-0042-1751453) -- open-access redrawing\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
