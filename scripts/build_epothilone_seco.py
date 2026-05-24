"""Derive the RCM seco-precursor for epothilone B (Nicolaou 1997).

The closure rule is `rcm`:
    Cα=CH2  +  H2C=Cβ   →   Cα=Cβ  +  H2C=CH2 (ethylene)

So the seco precursor is the deepoxy-epothilone B alkene-macrocycle
with the C12=C13 in-ring bond cleaved and each fragment terminated by
a vinyl (-CH=CH2) group. The macrolactone ester bond (C1-O-C15) is
already established in Nicolaou's seco-acid — RCM closes only the
C12-C13 alkene. The molecule does NOT split into two fragments
because the macrolactone ester provides the second connection
between the two halves of the would-be macrocycle.

Procedure (RDKit):

1. Parse the cyclized SMILES (deepoxy epothilone B; from
   scripts/build_epothilone_b_rcm.py, also written to
   data/validation_panel/.../canonical_smiles.txt).
2. Identify the unique in-ring non-aromatic C=C bond — that is the
   C12=C13 alkene produced by RCM.
3. Break that double bond and add a terminal =CH2 to each side
   (Cα=Cβ  →  Cα=CH2 + H2C=Cβ).
4. Sanitize, canonicalize, verify mass balance:
   Δ MW = MW(seco) − MW(cyclized) = MW(ethylene) ≈ 28.0314 Da.
5. Write `data/building_blocks/epothilone_seco.yaml`.

Refs:
- Nicolaou et al. JACS 1997, 119, 7974 (DOI 10.1021/ja971110h)
- Nicolaou et al. Nature 1997, 387, 268 (DOI 10.1038/387268a0)
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cyclized 12,13-deepoxy epothilone B (output of build_epothilone_b_rcm.py).
DEEPOXY_SMILES = (
    "C[C@H]1CCC/C(C)=C\\C[C@@H](OC(=O)C[C@H](O)C(C)(C)[C@@H](O)"
    "[C@H](C)C1=O)/C(C)=C/c1csc(C)n1"
)

ETHYLENE_EXACT_MW = 28.0313   # C2H4 exact mass (Da)


def _find_rcm_alkene_bond(mol: Chem.Mol) -> int:
    """Return the bond index of the in-ring non-aromatic C=C alkene.

    The cyclized deepoxy-epothilone-B macrocycle has exactly one such
    bond: the C12=C13 alkene produced by RCM. Aromatic ring bonds
    (thiazole) and exocyclic alkenes (the C16-C17 vinyl tether) are
    excluded.
    """
    ri = mol.GetRingInfo()
    ring16 = None
    for r in ri.AtomRings():
        if len(r) == 16:
            ring16 = set(r)
            break
    if ring16 is None:
        raise RuntimeError("No 16-membered ring found in cyclized structure")

    candidates = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetIsAromatic() or b.GetIsAromatic():
            continue
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        if a.GetIdx() in ring16 and b.GetIdx() in ring16:
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
    # Break the in-ring C=C, then add a new CH2 terminus to each side.
    rw.RemoveBond(a_idx, b_idx)
    new_a = rw.AddAtom(Chem.Atom("C"))
    new_b = rw.AddAtom(Chem.Atom("C"))
    rw.AddBond(a_idx, new_a, Chem.BondType.DOUBLE)
    rw.AddBond(b_idx, new_b, Chem.BondType.DOUBLE)

    # Reset any leftover stereo flags on the two former-sp2 carbons
    # (the original alkene geometry no longer makes sense once both
    # sides are terminal vinyls). RDKit's sanitizer will recompute
    # everything from scratch on output.
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

    # Sanity: opening the macrocycle should remove exactly one ring;
    # the 5-membered thiazole stays. Cyclized has two rings (16, 5);
    # seco should have just the 5.
    seco_rings = sorted(len(r) for r in seco.GetRingInfo().AtomRings())
    info["seco_ring_sizes"] = seco_rings

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(DEEPOXY_SMILES)
    print(f"cyclized formula   : {info['cyclized_formula']}  "
          f"(MW {info['cyclized_exact_mw']:.4f})")
    print(f"seco formula       : {info['seco_formula']}  "
          f"(MW {info['seco_exact_mw']:.4f})")
    print(f"Δ MW (seco-cyclized): {info['delta_mw']:.4f}  "
          f"(expected ethylene ≈ {ETHYLENE_EXACT_MW})")
    print(f"seco ring sizes    : {info['seco_ring_sizes']}  "
          f"(expect just the 5-ring thiazole)")
    print()
    print("seco SMILES:")
    print(seco_smiles)

    if abs(info["delta_mw"] - ETHYLENE_EXACT_MW) > 0.01:
        raise SystemExit(
            f"Mass balance failed: Δ = {info['delta_mw']:.4f}, "
            f"expected ≈ {ETHYLENE_EXACT_MW}"
        )
    if info["seco_ring_sizes"] != [5]:
        raise SystemExit(
            f"Seco ring inventory unexpected: got {info['seco_ring_sizes']}, "
            "expected [5] (thiazole only — the 16-ring should be open)"
        )

    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "epothilone_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        "name: epothilone B seco-acid diene (RCM precursor)\n"
        f"smiles: {seco_smiles}\n"
        "provenance: |\n"
        "  Seco-precursor for the Nicolaou 1997 RCM closure of\n"
        "  epothilone B (JACS 1997, 119, 7974, DOI:10.1021/ja971110h;\n"
        "  Nature 1997, 387, 268, DOI:10.1038/387268a0). Derived\n"
        "  programmatically from the cyclized 12,13-deepoxy\n"
        "  epothilone B alkene (formula C27H41NO5S, MW 491.27) by\n"
        "  breaking the in-ring C12=C13 alkene and capping each\n"
        "  side with a terminal CH2= group. The macrolactone ester\n"
        "  (C1-O-C15) is already established in this seco substrate,\n"
        "  matching Nicolaou's actual route: macrolactonization\n"
        "  precedes RCM in their scheme. The two terminal alkenes\n"
        "  at C12 and C13 are the dienes consumed by Grubbs G1 in\n"
        "  CH2Cl2 at 25 °C (0.001 M), expelling ethylene as the\n"
        "  RCM byproduct.\n"
        "notes: |\n"
        "  Mass balance verified by build script:\n"
        f"    cyclized (deepoxy) MW = {info['cyclized_exact_mw']:.4f}\n"
        f"    seco MW              = {info['seco_exact_mw']:.4f}\n"
        f"    Δ MW                 = {info['delta_mw']:.4f}\n"
        f"    ethylene (C2H4) MW   = {ETHYLENE_EXACT_MW:.4f}\n"
        "\n"
        "  Stereocenters preserved: the seco retains all 5 sp3 chiral\n"
        "  centres of the deepoxy macrocycle (C3 S, C6 R, C7 S, C8 S,\n"
        "  C15 S, in Nicolaou's macrocycle numbering). The exocyclic\n"
        "  C16=C17 (E)-vinyl tether to the thiazole is unchanged.\n"
        "  The two terminal CH2= termini at former-C12 and former-C13\n"
        "  carry no stereo (sp2, terminal).\n"
        "\n"
        "  E/Z selectivity caveat: Nicolaou's actual RCM produces a\n"
        "  ~1:1 Z:E mixture on this substrate; the desired Z isomer\n"
        "  is separated chromatographically before epoxidation to\n"
        "  epothilone B. The panel rule `rcm` is selectivity-agnostic\n"
        "  in v0, so the runspec's enforce_ez_geometry: {rcm: Z}\n"
        "  predicate filters the post-closure product to the Z isomer.\n"
        "refs:\n"
        "  - \"Nicolaou, K. C. et al. J. Am. Chem. Soc. 1997, 119, 7974-7991 (DOI:10.1021/ja971110h) — primary reference\"\n"
        "  - \"Nicolaou, K. C. et al. Nature 1997, 387, 268-272 (DOI:10.1038/387268a0) — companion\"\n"
        "  - \"ChEBI:31550 (epothilone B); LIPID MAPS LMPK04000041 — natural-product reference for the post-epoxidation form\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
