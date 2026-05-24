"""Derive the seco-acid precursor for erythronolide B (Corey 1978).

The closure rule for erythronolide B is `macrolactonization`:

    HO-C(=O)-R + HO-C(sp3)-R' -> R-C(=O)-O-C(sp3)-R' + H2O

So the seco-acid is erythronolide B with the C1-O13 ester bond opened.
The acyl side (C1) gains a free carboxylic acid -COOH (i.e. the new O
in the COOH was the C13-O of the ring, but we cap it as an explicit
OH to keep mass balance: the cyclized form had C(=O)-O-C(sp3), and the
seco form has HO-C(=O) on one side + HO-C(sp3) on the other; net atom
change is +H2O on the seco side).

Procedure (RDKit):

1. Parse the canonical isomeric SMILES of erythronolide B.
2. Find the ester C(=O)-O bond in the 14-ring: the C is the acyl
   carbon (sp2, double-bonded to one O, single-bonded to the ring O);
   the O is the ester oxygen (sp3, two-coordinate, both neighbours in
   the ring).
3. Surgically break the C(sp2)-O(sp3) bond:
   - On the acyl C side: add a new -OH (this becomes the -COOH).
   - On the C13 side: the alcohol O is already there; it just becomes
     a free secondary alcohol (RDKit adds the implicit H at write
     time).
4. Sanitize and canonicalize.
5. Verify mass balance: seco MW = cyclized MW + H2O (18.015 g/mol).
6. Write building block YAML at
   `data/building_blocks/erythronolide_b_seco.yaml`.

Reference: Corey, E. J. et al. 1978, JACS 100:4620 (DOI:
10.1021/ja00482a063) — the macrolactonization paper.
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Canonical isomeric SMILES of erythronolide B (matches structure.mol;
# PubChem CID 441113; InChIKey ZFBRGCCVTUPRFQ-HWRKYNCUSA-N).
ERYTHRONOLIDE_B_SMILES = (
    "CC[C@@H]1[C@@H]([C@@H]([C@H](C(=O)[C@@H](C[C@@]"
    "([C@@H]([C@H]([C@@H]([C@H](C(=O)O1)C)O)C)O)(C)O)C)C)O)C"
)

H2O_EXACT_MW = 18.0106


def _find_lactone_ester_bond(mol: Chem.Mol) -> tuple[int, int, int]:
    """Find the ring-internal C(=O)-O ester bond.

    Returns (acyl_C_idx, ester_O_idx, bond_idx).

    Criteria for the ester O: sp3 oxygen, two heavy neighbours, both
    in the 14-ring; one neighbour is the acyl C (sp2, has a =O), the
    other is the C13 carbon (sp3, the alcohol-side ring carbon).
    """
    rings = mol.GetRingInfo()
    ring14 = None
    for ring in rings.AtomRings():
        if len(ring) == 14:
            ring14 = set(ring)
            break
    if ring14 is None:
        raise RuntimeError("No 14-membered ring found in erythronolide B")

    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() != 8:
            continue
        if atom.GetIdx() not in ring14:
            continue
        # Two heavy neighbours, both in the ring, both carbons
        nbrs = [n for n in atom.GetNeighbors() if n.GetAtomicNum() == 6]
        if len(nbrs) != 2:
            continue
        if not all(n.GetIdx() in ring14 for n in nbrs):
            continue
        # Identify which neighbour is the acyl C (has a =O substituent
        # exocyclic to this O)
        acyl_c = None
        for n in nbrs:
            for nb in n.GetNeighbors():
                if nb.GetIdx() == atom.GetIdx():
                    continue
                if nb.GetAtomicNum() == 8:
                    bond = mol.GetBondBetweenAtoms(n.GetIdx(), nb.GetIdx())
                    if bond.GetBondType() == Chem.BondType.DOUBLE:
                        acyl_c = n
                        break
            if acyl_c is not None:
                break
        if acyl_c is None:
            continue
        bond = mol.GetBondBetweenAtoms(acyl_c.GetIdx(), atom.GetIdx())
        return acyl_c.GetIdx(), atom.GetIdx(), bond.GetIdx()
    raise RuntimeError("No lactone ester bond identified in 14-ring")


def derive_seco_smiles(cyclized_smiles: str) -> tuple[str, dict]:
    """Return (seco_isomeric_smiles, info_dict)."""
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict[str, object] = {}
    info["cyclized_formula"] = CalcMolFormula(mol)
    info["cyclized_stereocenters"] = len(
        Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    )
    info["cyclized_exact_mw"] = Descriptors.ExactMolWt(mol)

    acyl_c_idx, ester_o_idx, _ = _find_lactone_ester_bond(mol)
    info["acyl_C_idx"] = acyl_c_idx
    info["ester_O_idx"] = ester_o_idx

    rw = Chem.RWMol(mol)
    rw.RemoveBond(acyl_c_idx, ester_o_idx)
    # Cap the acyl C with a new -OH
    new_o = rw.AddAtom(Chem.Atom("O"))
    rw.AddBond(acyl_c_idx, new_o, Chem.BondType.SINGLE)
    # The former ester O at ester_o_idx now has only one heavy
    # neighbour (the C13 alcohol carbon) and gets implicit H.

    seco = rw.GetMol()
    Chem.SanitizeMol(seco)
    Chem.AssignStereochemistry(seco, cleanIt=True, force=True)
    info["seco_formula"] = CalcMolFormula(seco)
    info["seco_stereocenters"] = len(
        Chem.FindMolChiralCenters(seco, includeUnassigned=True)
    )
    info["seco_exact_mw"] = Descriptors.ExactMolWt(seco)

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(ERYTHRONOLIDE_B_SMILES)
    print("cyclized formula      :", info["cyclized_formula"])
    print("cyclized stereocenters:", info["cyclized_stereocenters"])
    print("cyclized exact MW     :", f"{info['cyclized_exact_mw']:.4f}")
    print("acyl C idx            :", info["acyl_C_idx"])
    print("ester O idx           :", info["ester_O_idx"])
    print("seco formula          :", info["seco_formula"])
    print("seco stereocenters    :", info["seco_stereocenters"])
    print("seco exact MW         :", f"{info['seco_exact_mw']:.4f}")
    print()
    print("seco SMILES:")
    print(seco_smiles)

    delta = info["seco_exact_mw"] - info["cyclized_exact_mw"]
    print()
    print(f"delta exact MW = {delta:.4f}  (expected {H2O_EXACT_MW:.4f} for +H2O)")
    if abs(delta - H2O_EXACT_MW) > 0.01:
        raise SystemExit(
            f"mass balance mismatch: delta={delta:.4f} expected={H2O_EXACT_MW:.4f}"
        )
    print("mass balance: OK (seco = cyclized + H2O)")

    # Write building block YAML
    repo = Path(__file__).resolve().parent.parent
    block_path = (
        repo / "data" / "building_blocks" / "erythronolide_b_seco.yaml"
    )
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        "name: erythronolide_b_seco_acid\n"
        f"smiles: {seco_smiles}\n"
        "provenance: |\n"
        "  Seco-acid precursor for erythronolide B (Corey 1978;\n"
        "  J. Am. Chem. Soc. 100:4620, DOI:10.1021/ja00482a063).\n"
        "  Derived programmatically from the cyclized PubChem CID 441113\n"
        "  structure by breaking the macrocyclic C(=O)-O ester bond and\n"
        "  capping the acyl side with -OH; the C13 alcohol side retains\n"
        "  its free secondary -OH. Macrolactonization fires intramolecularly\n"
        "  to close the 14-membered ring and expel H2O.\n"
        "notes: |\n"
        "  Building block for the Corey-Nicolaou macrolactonization M5 leg.\n"
        "  Stereochemistry preserved on all 10 sp3 centers of the cyclized\n"
        "  form (the macrolactonization rule's stereo_flags include\n"
        "  retains_alpha_stereo and retains_alcohol_stereo, so the alpha\n"
        "  carbon C2 and the alcohol carbon C13 keep their configuration\n"
        "  under Corey-Nicolaou conditions).\n"
        f"  Mass balance: seco exact MW = cyclized exact MW + H2O:\n"
        f"  {info['cyclized_exact_mw']:.4f} + {H2O_EXACT_MW} = "
        f"{info['seco_exact_mw']:.4f} (verified by build script).\n"
        "refs:\n"
        '  - "Corey, E. J.; Kim, S.; Yoo, S.-E.; Nicolaou, K. C.; Melvin, L. S.;\n'
        '     Brunelle, D. J.; Falck, J. R.; Trybulski, E. J.; Lett, R.;\n'
        '     Sheldrake, P. W. JACS 1978, 100, 4620. DOI:10.1021/ja00482a063 -- macrolactonization paper"\n'
        '  - "Corey, E. J.; Nicolaou, K. C. JACS 1974, 96, 5614.\n'
        '     DOI:10.1021/ja00824a073 -- PySSPy/PPh3 activator methodology"\n'
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
