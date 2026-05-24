"""Derive the seco-precursor building block for the vancomycin C-O-D ring.

The closure rule is `biaryl_etherification` (Boger 1999 SNAr biaryl ether):

    Ar1-F + HO-Ar2  -->  Ar1-O-Ar2 + HF

So the seco-precursor opens the macrocyclic Ar1-O-Ar2 bridge:
  - Ar1 (residue D, the electrophile arene with ortho-NO2 activator):
    bond to O removed, capped with F.
  - Ar2 (residue C, the nucleophile arene): bond to O becomes a free
    phenolic OH (RDKit adds the implicit H at write time).
The rest of the tripeptide tether stays intact -- the linear sequence
of three amide bonds links the two ends of the would-be macrocycle, so
breaking the ether bond does not split the molecule.

Mass balance: seco MW = cyclized MW + HF (20.006 g/mol exact).

References:
- Boger et al., J. Am. Chem. Soc. 1999, 121, 10004. DOI:10.1021/ja992577q.
- Boger et al., J. Org. Chem. 1999, 64, 70. DOI:10.1021/jo980880o.
- Beugelmans et al., J. Org. Chem. 1994, 59, 5535. DOI:10.1021/jo00098a010
  (the earliest published SNAr macrocyclization with intrinsic ortho-NO2
   activation on a vancomycin-style model arene).
"""
from __future__ import annotations

from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cyclized CD-ring model SMILES (must match build_vancomycin_cd.py).
CYCLIZED_SMILES = (
    "O1c2ccc(C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C(=O)NC)"
    "c3cc(Cl)cc([N+](=O)[O-])c31)cc2"
)


def _find_macrocyclic_biaryl_ether_bond(mol: Chem.Mol) -> tuple[int, int, int]:
    """Find the Ar-O bond of the 16-ring on the electrophile (D-arene) side.

    Criteria:
      - one endpoint is an aromatic C in the 16-ring
      - the other is an sp3 O (the bridge ether) in the 16-ring
      - of the two aromatic C neighbours of the bridge O, the "electrophile"
        side is the one with an ortho NO2 group on the arene (residue D).

    Returns (bond_idx, ar_idx_to_F, o_idx) where ar_idx_to_F is the arene
    carbon that should receive the F leaving group, and o_idx is the
    oxygen that becomes a free OH on the other arene side.
    """
    rings = mol.GetRingInfo()
    ring16 = None
    for ring in rings.AtomRings():
        if len(ring) == 16:
            ring16 = set(ring)
            break
    if ring16 is None:
        raise RuntimeError("No 16-membered ring found")

    # Find the bridge O (aromatic-bonded sp3 O with two aromatic neighbours, in 16-ring)
    bridge_o = None
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() != 8:
            continue
        if atom.GetIdx() not in ring16:
            continue
        neighs = atom.GetNeighbors()
        if len(neighs) != 2:
            continue
        if not all(n.GetIsAromatic() for n in neighs):
            continue
        bridge_o = atom
        break
    if bridge_o is None:
        raise RuntimeError("No Ar-O-Ar bridge oxygen in 16-ring")
    o_idx = bridge_o.GetIdx()

    # Choose which arene neighbour gets the F: the one with ortho-NO2.
    def _has_ortho_no2(ar_c_idx: int) -> bool:
        """Check if ar_c_idx has any aromatic neighbour bonded to a nitro N."""
        ar_atom = mol.GetAtomWithIdx(ar_c_idx)
        for n in ar_atom.GetNeighbors():
            if not n.GetIsAromatic():
                continue
            for nn in n.GetNeighbors():
                if nn.GetIdx() == ar_c_idx:
                    continue
                if nn.GetAtomicNum() == 7 and nn.GetFormalCharge() == 1:
                    # Confirm it's NO2: N+(=O)(-O-) pattern
                    has_o_minus = any(
                        x.GetAtomicNum() == 8 and x.GetFormalCharge() == -1
                        for x in nn.GetNeighbors()
                    )
                    has_o_double = any(
                        x.GetAtomicNum() == 8 and x.GetFormalCharge() == 0
                        and mol.GetBondBetweenAtoms(nn.GetIdx(), x.GetIdx()).GetBondType()
                        == Chem.BondType.DOUBLE
                        for x in nn.GetNeighbors()
                    )
                    if has_o_minus and has_o_double:
                        return True
        return False

    ar_with_no2 = None
    ar_other = None
    for n in bridge_o.GetNeighbors():
        if _has_ortho_no2(n.GetIdx()):
            ar_with_no2 = n.GetIdx()
        else:
            ar_other = n.GetIdx()
    if ar_with_no2 is None:
        raise RuntimeError("No ortho-NO2 found on either bridge arene")
    if ar_other is None:
        raise RuntimeError("Could not identify nucleophile-side arene")

    bond = mol.GetBondBetweenAtoms(ar_with_no2, o_idx)
    return bond.GetIdx(), ar_with_no2, o_idx


def derive_seco_smiles(cyclized_smiles: str) -> tuple[str, dict]:
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict[str, object] = {}
    info["cyclized_formula"] = CalcMolFormula(mol)
    info["cyclized_stereocenters"] = len(
        Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    )

    bond_idx, ar_idx, o_idx = _find_macrocyclic_biaryl_ether_bond(mol)
    info["broken_bond"] = (ar_idx, o_idx)
    info["electrophile_aromatic_idx"] = ar_idx  # gets F
    info["nucleophile_o_idx"] = o_idx           # becomes free OH

    rw = Chem.RWMol(mol)
    rw.RemoveBond(ar_idx, o_idx)
    f_idx = rw.AddAtom(Chem.Atom("F"))
    rw.AddBond(ar_idx, f_idx, Chem.BondType.SINGLE)

    seco = rw.GetMol()
    Chem.SanitizeMol(seco)
    info["seco_formula"] = CalcMolFormula(seco)
    info["seco_stereocenters"] = len(
        Chem.FindMolChiralCenters(seco, includeUnassigned=True)
    )

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(CYCLIZED_SMILES)
    print("cyclized formula     :", info["cyclized_formula"])
    print("cyclized stereocenters:", info["cyclized_stereocenters"])
    print("broken Ar-O bond     :", info["broken_bond"])
    print("seco formula         :", info["seco_formula"])
    print("seco stereocenters   :", info["seco_stereocenters"])
    print()
    print("seco SMILES:")
    print(seco_smiles)

    # Mass balance check
    cyc = Chem.MolFromSmiles(CYCLIZED_SMILES)
    seco_mol = Chem.MolFromSmiles(seco_smiles)
    cyc_mw = Descriptors.ExactMolWt(cyc)
    seco_mw = Descriptors.ExactMolWt(seco_mol)
    delta = seco_mw - cyc_mw
    hf_mw = 20.006
    print()
    print(f"cyclized MW: {cyc_mw:.4f}")
    print(f"seco MW    : {seco_mw:.4f}")
    print(f"delta      : {delta:.4f}  (expected {hf_mw:.4f} for +HF)")
    assert abs(delta - hf_mw) < 0.01, (
        f"mass balance mismatch: delta={delta:.4f} expected={hf_mw:.4f}"
    )

    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "vancomycin_cd_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        f"name: vancomycin_cd_seco_precursor\n"
        f"smiles: {seco_smiles}\n"
        f"provenance: |\n"
        f"  Seco-precursor for the vancomycin C-O-D ring (Boger 1999 SNAr\n"
        f"  biaryl ether macrocyclization). Derived programmatically from\n"
        f"  the encoded CD-ring model substrate (16-membered macrocycle,\n"
        f"  C22H22ClN5O7) by breaking the macrocyclic Ar-O-Ar bridge:\n"
        f"  the F leaving group is restored on the residue-D arene\n"
        f"  (the electrophile, identified by its retained ortho-NO2\n"
        f"  activator), and a free phenolic OH is left on the residue-C\n"
        f"  arene (the nucleophile partner).\n"
        f"  biaryl_etherification rule fires intramolecularly on this\n"
        f"  substrate to close the 16-ring with HF expulsion.\n"
        f"notes: |\n"
        f"  CD-ring model compound; not the full vancomycin aglycon\n"
        f"  (C53H53Cl2N9O20, MW 1144.93). The model captures the SNAr\n"
        f"  disconnection (Ar-F + Ar-OH -> Ar-O-Ar + HF) and 16-ring\n"
        f"  size with a simplified tripeptide tether (Ala-Ala-CalphaD).\n"
        f"  All three Calpha atoms carry L-amino-acid stereochemistry.\n"
        f"  Mass balance: seco MW = cyclized MW + HF (verified):\n"
        f"  {cyc_mw:.4f} + {hf_mw} = {seco_mw:.4f}.\n"
        f"refs:\n"
        f"  - \"Boger et al. 1999, JACS 121:10004 (DOI:10.1021/ja992577q) -- vancomycin aglycon CD+DE SNAr\"\n"
        f"  - \"Boger et al. 1999, JOC 64:70 (DOI:10.1021/jo980880o) -- CD/DE model methodology\"\n"
        f"  - \"Beugelmans et al. 1994, JOC 59:5535 (DOI:10.1021/jo00098a010) -- earliest intrinsic-NO2 SNAr macroetherification\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
