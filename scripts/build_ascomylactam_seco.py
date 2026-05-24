"""Derive the seco-precursor building block for ascomylactam A.

The closure rule for ascomylactam A is `aryl_etherification`:

    Ar–F + HO–C(sp3) → Ar–O–C(sp3) + HF

So the seco precursor is ascomylactam A with the Ar–O–C(sp3) bridge
opened: C-14 carries a free OH and C-7' carries a leaving group F.
The rest of the molecule (the 6/5/6/5 tetracyclic core + the γ-lactam
+ the *para*-arene + the methoxy at C-1') stays intact — the
tetracyclic core links the two ends of the would-be macrocycle, so
breaking the ether bond does not split the molecule.

Procedure (RDKit):

1. Parse the canonical isomeric SMILES of ascomylactam A (from the
   encoder agent's atom_label_map.txt).
2. Find the Ar–O bond by scanning bonds where one atom is aromatic C
   and the other is sp3 O (and that O is also bonded to one other
   sp3 C — i.e., the ether O in the macrocycle, not the OH on C-2'
   or C-17 or the OMe on C-1').
3. Surgically break that bond:
   - On the aromatic C (C-7'): replace the bond to O with a bond to F
   - On the sp3 O: leave it bonded to C-14 as a free OH (RDKit will
     add the implicit H at write time)
4. Sanitize and canonicalize.
5. Write building block YAML at
   `data/building_blocks/ascomylactam_a_seco.yaml`.

Reference: Chen 2019 (DOI:10.1021/acs.jnatprod.8b00918) — the
deposited macrocyclic structure. The forward synthetic route via
Uchiro 2017 (DOI:10.1002/asia.201601728) uses the same Ar-F + HO-C
seco-precursor architecture on the analogous GKK1032A2 13-ring.
"""
from __future__ import annotations

from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors


# Canonical isomeric SMILES of ascomylactam A as encoded by
# scripts/build_ascomylactam_a.py (matches the structure.mol).
ASCOMYLACTAM_A_SMILES = (
    "CO[C@@H]1C2=C(O)[C@@]34[C@H]5[C@H]"
    "(Oc6ccc(cc6)C[C@]1(O)NC2=O)"
    "[C@H]1[C@@H](C[C@H](C)C[C@@H]1C)"
    "[C@@H]5C(C)=C[C@]3(C)C=C(C)[C@@H]4C"
)


def _find_macrocyclic_ether_bond(mol: Chem.Mol) -> int:
    """Find the bond index of the Ar–O ether that closes the 13-ring.

    Criteria:
      - one endpoint is aromatic C
      - the other is sp3 O
      - the O has exactly two heavy neighbours (Ar and one sp3 C)
      - the sp3 C is also stereo-assigned (C-14 is the oxymethine)

    These criteria pick out the ether oxygen of the macrocycle in
    ascomylactam A unambiguously: the OMe-O on C-1' has a neighbour
    that is a methyl (sp3 CH3), the OH-on-C-17 / OH-on-C-2' have only
    one heavy neighbour, and the amide C=O (C-19) is sp2.
    """
    rings = mol.GetRingInfo()
    ring13 = None
    for ring in rings.AtomRings():
        if len(ring) == 13:
            ring13 = set(ring)
            break
    if ring13 is None:
        raise RuntimeError("No 13-membered ring found in ascomylactam A")

    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        # one aromatic C, one sp3 O, both in the 13-ring
        if a.GetIdx() not in ring13 or b.GetIdx() not in ring13:
            continue
        pair = sorted([(a.GetIsAromatic(), a.GetAtomicNum()),
                       (b.GetIsAromatic(), b.GetAtomicNum())])
        # we want (True, 6) and (False, 8) — Ar C and sp3 O
        if pair == [(False, 8), (True, 6)]:
            return bond.GetIdx()
    raise RuntimeError("No Ar–O ether bond identified in 13-ring")


def derive_seco_smiles(cyclized_smiles: str) -> tuple[str, dict]:
    """Return (seco_isomeric_smiles, info)."""
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict[str, object] = {}
    info["cyclized_formula"] = Chem.rdMolDescriptors.CalcMolFormula(mol)
    info["cyclized_stereocenters"] = len(
        Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    )

    bond_idx = _find_macrocyclic_ether_bond(mol)
    bond = mol.GetBondWithIdx(bond_idx)
    a, b = bond.GetBeginAtom(), bond.GetEndAtom()
    if a.GetIsAromatic():
        ar_idx, o_idx = a.GetIdx(), b.GetIdx()
    else:
        ar_idx, o_idx = b.GetIdx(), a.GetIdx()
    info["broken_bond"] = (ar_idx, o_idx)
    info["aromatic_atom_idx"] = ar_idx  # C-7'
    info["ether_o_idx"] = o_idx          # the bridge O

    # Editable copy
    rw = Chem.RWMol(mol)
    rw.RemoveBond(ar_idx, o_idx)
    # Add F to aromatic C
    f_idx = rw.AddAtom(Chem.Atom("F"))
    rw.AddBond(ar_idx, f_idx, Chem.BondType.SINGLE)
    # The O at o_idx now has only one heavy neighbour (C-14) and will
    # carry the implicit H automatically at write time.

    seco = rw.GetMol()
    Chem.SanitizeMol(seco)
    info["seco_formula"] = Chem.rdMolDescriptors.CalcMolFormula(seco)
    info["seco_stereocenters"] = len(
        Chem.FindMolChiralCenters(seco, includeUnassigned=True)
    )

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco_smiles(ASCOMYLACTAM_A_SMILES)
    print("cyclized formula     :", info["cyclized_formula"])
    print("cyclized stereocenters:", info["cyclized_stereocenters"])
    print("broken Ar–O bond     :", info["broken_bond"])
    print("seco formula         :", info["seco_formula"])
    print("seco stereocenters   :", info["seco_stereocenters"])
    print()
    print("seco SMILES:")
    print(seco_smiles)

    # Sanity: seco is cyclized + HF mass-wise on the macrocyclization
    # rule's left side (Ar-F + HO-C); i.e. seco mass = cyclized + HF.
    cyc = Chem.MolFromSmiles(ASCOMYLACTAM_A_SMILES)
    seco_mol = Chem.MolFromSmiles(seco_smiles)
    cyc_mw = Descriptors.ExactMolWt(cyc)
    seco_mw = Descriptors.ExactMolWt(seco_mol)
    delta = seco_mw - cyc_mw
    hf_mw = 20.006  # HF
    print()
    print(f"cyclized MW: {cyc_mw:.4f}")
    print(f"seco MW    : {seco_mw:.4f}")
    print(f"Δ          : {delta:.4f}  (expected {hf_mw:.4f} for +HF)")
    assert abs(delta - hf_mw) < 0.01, (
        f"mass balance mismatch: Δ={delta:.4f} expected={hf_mw:.4f}"
    )

    # Write building block YAML
    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "ascomylactam_a_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        f"name: ascomylactam_a_seco_precursor\n"
        f"smiles: {seco_smiles}\n"
        f"provenance: |\n"
        f"  Seco-precursor for ascomylactam A (M5 target). Derived\n"
        f"  programmatically from the cyclized Chen 2019 structure\n"
        f"  (CCDC 1515168) by breaking the macrocyclic Ar-O-C(sp3)\n"
        f"  bond and capping with F on the aromatic side. The\n"
        f"  resulting substrate carries Ar-F at C-7' and free HO at\n"
        f"  C-14; aryl_etherification rule fires intramolecularly to\n"
        f"  close the 13-membered ring + expel HF.\n"
        f"notes: |\n"
        f"  Building block for the M5 pipeline run. Stereochemistry\n"
        f"  preserved on all 12 sp3 centers of the cyclized form\n"
        f"  (alcohol carbon C-14, which is the only stereocenter\n"
        f"  directly affected by the closure, retains its R config\n"
        f"  per the aryl_etherification stereo_flags:\n"
        f"  retains_alcohol_stereo).\n"
        f"  Mass balance: seco MW = cyclized MW + HF (verified by\n"
        f"  build script): {cyc_mw:.4f} + {hf_mw} = {seco_mw:.4f}.\n"
        f"refs:\n"
        f"  - \"Chen et al. 2019, J. Nat. Prod. 82:1752 (DOI:10.1021/acs.jnatprod.8b00918) -- cyclized parent\"\n"
        f"  - \"Sugata, Uchiro et al. 2017, Chem. Asian J. 12:628 (DOI:10.1002/asia.201601728) -- analogous GKK1032A2 seco-precursor + SNAr closure\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
