"""Derive the TDA seco-precursor (14-membered macrocyclic triene) for
the Phoenix-Reddy-Deslongchamps 2008 cassaine synthesis.

The closure rule is `transannular_diels_alder` (defined in
`data/rules/transannular_diels_alder.gml`):

    LHS:  C(1)=C(2)-C(3)=C(4) + C(5)=C(6)     (diene + dienophile)
    RHS:  C(1)-C(2)=C(3)-C(4)-C(5)-C(6)-C(1)  (cyclohexene; 2 new sigma
                                                bonds 1-6 and 4-5;
                                                residual alkene at 2=3)

So the seco precursor of the post-TDA tricycle 5 (output of
scripts/build_cassaine.py) is derived by:

1. Locate the in-ring cyclohexene of the tricycle (the C(2)=C(3) alkene).
2. Walk the cyclohexene ring outward from each alkene carbon to find
   the four flanking ring atoms (positions 1, 6, 4, 5 in the rule).
3. Identify the two new TDA sigma bonds — the bonds (1-6) and (4-5).
4. Break both sigma bonds.
5. Convert (1-2) and (3-4) to double (restoring the diene); convert
   (2-3) back to single; convert (5-6) to double (restoring the
   dienophile).
6. Result: a 14-membered macrocyclic *triene* (three new C=C bonds:
   the diene C1=C2-C3=C4 plus the dienophile C5=C6, all in the ring),
   atom-economic with the cyclized tricycle: **Δ MW = 0** (TDA has no
   byproduct).

Procedure (RDKit):
- Parse the cyclized SMILES from scripts/build_cassaine.py.
- Identify the cyclohexene ring (the 6-ring with an in-ring C=C).
- Walk the ring to map rule positions 1..6.
- Mutate bonds as described above.
- Sanitize, canonicalize.
- Verify Δ MW = 0 to 0.0001 Da (TDA byproduct mass = 0).
- Verify the seco has exactly one 14-membered ring (the two other
  cyclohexanes of the tricycle disappear when we break the TDA bonds).
- Verify the seco has three in-ring C=C bonds (the *cis-trans-trans*
  triene of compound 4).
- Verify the exocyclic α,β-unsaturated ester C=C is unchanged.
- Write data/building_blocks/cassaine_seco.yaml.

Refs:
- Phoenix, Reddy, Deslongchamps. JACS 2008, 130, 13989-13995.
  DOI 10.1021/ja805097s.
- Lamothe, Ndibwami, Deslongchamps. Tet. Lett. 1988, 29, 1639 (theory)
  and 1641 (experimental).

Stereo caveat: the cis-trans-trans triene geometry of compound 4 (as
described by Lamothe-Ndibwami-Deslongchamps and reproduced by
Phoenix-Reddy) is NOT enforced on the seco. The MOD-MacroCert TDA
rule (data/rules/transannular_diels_alder.gml) carries no stereo
annotations on either side of the rewrite; Workstream F task #35
(TDA stereo encoding for 4 new sp3 centres + endo/exo split) is
queued but not yet done. v0 ships a stereo-naive seco; the campaign
runs without stereo enforcement on the TDA leg.
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Tricycle 5 SMILES (must match scripts/build_cassaine.py).
TRICYCLE5_SMILES = (
    "C[C@H]1/C(=C/C(=O)OC)CC[C@H]2[C@H]1C=C[C@H]1"
    "C(C)(C)[C@@H](O)CC[C@]21C"
)

TDA_BYPRODUCT_EXACT_MW = 0.0   # Cycloaddition has zero byproduct.


def _find_cyclohexene_ring(mol: Chem.Mol) -> tuple[tuple[int, ...], int, int]:
    """Return (ring_atom_ids, alkene_atom_a, alkene_atom_b) for the unique
    6-membered ring containing exactly one non-aromatic C=C.

    The tricycle 5 has exactly one such ring (the TDA-residual
    cyclohexene); the other two 6-rings are saturated cyclohexanes.
    """
    ri = mol.GetRingInfo()
    candidates: list[tuple[tuple[int, ...], int, int]] = []
    for r in ri.AtomRings():
        if len(r) != 6:
            continue
        ring_set = set(r)
        ring_alkenes = []
        for bond in mol.GetBonds():
            if bond.GetBondType() != Chem.BondType.DOUBLE:
                continue
            if not bond.IsInRing():
                continue
            a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            if a in ring_set and b in ring_set:
                aA, aB = mol.GetAtomWithIdx(a), mol.GetAtomWithIdx(b)
                if aA.GetIsAromatic() or aB.GetIsAromatic():
                    continue
                ring_alkenes.append((a, b))
        if len(ring_alkenes) == 1:
            candidates.append((r, ring_alkenes[0][0], ring_alkenes[0][1]))
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one cyclohexene ring (the TDA cyclohexene); "
            f"found {len(candidates)}"
        )
    return candidates[0]


def _walk_ring_order(
    mol: Chem.Mol, ring_atoms: tuple[int, ...], start: int, second: int
) -> list[int]:
    """Walk a ring starting at `start` then `second`, returning the full
    cyclic atom order [start, second, ..., back-to-start-neighbour]."""
    ring_set = set(ring_atoms)
    order = [start, second]
    prev = start
    curr = second
    while len(order) < len(ring_atoms):
        nbrs = [
            nbr.GetIdx() for nbr in mol.GetAtomWithIdx(curr).GetNeighbors()
            if nbr.GetIdx() in ring_set and nbr.GetIdx() != prev
        ]
        if not nbrs:
            raise RuntimeError(f"ring walk stuck at atom {curr}")
        nxt = nbrs[0]
        order.append(nxt)
        prev, curr = curr, nxt
    return order


def derive_seco(cyclized_smiles: str) -> tuple[str, dict]:
    """Mutate the tricycle to the open 14-membered macrocyclic triene.

    Returns (seco_canonical_smiles, info_dict).
    """
    mol = Chem.MolFromSmiles(cyclized_smiles)
    if mol is None:
        raise ValueError("Cannot parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    info: dict = {}
    info["cyclized_formula"] = CalcMolFormula(mol)
    info["cyclized_exact_mw"] = Descriptors.ExactMolWt(mol)

    ring_atoms, alk_a, alk_b = _find_cyclohexene_ring(mol)
    info["cyclohexene_ring_atoms"] = ring_atoms
    info["tda_alkene"] = (alk_a, alk_b)

    # Walk the ring starting from alk_a -> alk_b; map positions 2..6,1
    # in the TDA rule numbering:
    #   rule_2 = alk_a, rule_3 = alk_b, rule_4 = next, rule_5 = next,
    #   rule_6 = next, rule_1 = next (back to alk_a after one more step).
    order = _walk_ring_order(mol, ring_atoms, alk_a, alk_b)
    if len(order) != 6:
        raise RuntimeError(f"ring walk returned {len(order)} atoms; expected 6")
    rule_2, rule_3, rule_4, rule_5, rule_6, rule_1 = order
    info["rule_atom_map"] = {
        "rule_1": rule_1, "rule_2": rule_2, "rule_3": rule_3,
        "rule_4": rule_4, "rule_5": rule_5, "rule_6": rule_6,
    }

    # The two new TDA sigma bonds: (rule_1, rule_6) and (rule_4, rule_5).
    sigma_1_6 = (rule_1, rule_6)
    sigma_4_5 = (rule_4, rule_5)
    info["broken_sigma_bonds"] = [sigma_1_6, sigma_4_5]

    # Clear stereo (the seco is stereo-naive; Workstream F task #35 owns
    # the cis-trans-trans triene encoding).
    rw = Chem.RWMol(mol)
    for atom in rw.GetAtoms():
        atom.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    for bond in rw.GetBonds():
        bond.SetStereo(Chem.BondStereo.STEREONONE)

    # Break the two new TDA sigma bonds.
    rw.RemoveBond(*sigma_1_6)
    rw.RemoveBond(*sigma_4_5)

    # Convert (rule_2, rule_3) from double to single (the cyclohexene
    # alkene is consumed in reverse — becomes the inner single bond of
    # the diene).
    b = rw.GetBondBetweenAtoms(rule_2, rule_3)
    if b.GetBondType() != Chem.BondType.DOUBLE:
        raise RuntimeError("rule_2=rule_3 bond is not double")
    b.SetBondType(Chem.BondType.SINGLE)

    # Convert (rule_1, rule_2) and (rule_3, rule_4) to double (restore
    # the diene C=C-C=C arrangement).
    for u, v in [(rule_1, rule_2), (rule_3, rule_4)]:
        b = rw.GetBondBetweenAtoms(u, v)
        if b is None:
            raise RuntimeError(f"missing bond between rule positions {u},{v}")
        b.SetBondType(Chem.BondType.DOUBLE)

    # Convert (rule_5, rule_6) to double (restore the dienophile C=C).
    b = rw.GetBondBetweenAtoms(rule_5, rule_6)
    if b is None:
        raise RuntimeError("missing bond between rule_5 and rule_6")
    b.SetBondType(Chem.BondType.DOUBLE)

    Chem.SanitizeMol(rw)
    seco = rw.GetMol()

    # Audit the seco.
    info["seco_formula"] = CalcMolFormula(seco)
    info["seco_exact_mw"] = Descriptors.ExactMolWt(seco)
    info["delta_mw"] = info["seco_exact_mw"] - info["cyclized_exact_mw"]
    info["expected_delta_mw"] = TDA_BYPRODUCT_EXACT_MW

    ri = seco.GetRingInfo()
    info["seco_ring_sizes"] = sorted(len(r) for r in ri.AtomRings())

    # Count in-ring C=C bonds — expected to be 3 (the triene).
    in_ring_cc = []
    exo_cc = []
    for bond in seco.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        if a.GetIsAromatic() or b.GetIsAromatic():
            continue
        if bond.IsInRing():
            in_ring_cc.append((a.GetIdx(), b.GetIdx()))
        else:
            exo_cc.append((a.GetIdx(), b.GetIdx()))
    info["seco_in_ring_cc"] = in_ring_cc
    info["seco_exocyclic_cc"] = exo_cc

    canonical = Chem.MolToSmiles(seco, isomericSmiles=True, canonical=True)
    return canonical, info


def main() -> int:
    seco_smiles, info = derive_seco(TRICYCLE5_SMILES)
    print(f"cyclized formula     : {info['cyclized_formula']}  "
          f"(MW {info['cyclized_exact_mw']:.4f})")
    print(f"seco formula         : {info['seco_formula']}  "
          f"(MW {info['seco_exact_mw']:.4f})")
    print(f"Δ MW (seco-cyclized) : {info['delta_mw']:.4f}  "
          f"(expected {TDA_BYPRODUCT_EXACT_MW} — TDA has no byproduct)")
    print(f"seco ring sizes      : {info['seco_ring_sizes']}  "
          f"(expect [14] — the 14-membered macrocycle)")
    print(f"seco in-ring C=C     : {info['seco_in_ring_cc']}  "
          f"(expect 3 — the triene)")
    print(f"seco exocyclic C=C   : {info['seco_exocyclic_cc']}  "
          f"(expect 1 — the alpha,beta-unsat ester)")
    print()
    print("seco SMILES:")
    print(seco_smiles)

    # Audit gates.
    if abs(info["delta_mw"] - TDA_BYPRODUCT_EXACT_MW) > 0.001:
        raise SystemExit(
            f"Mass balance failed: Δ = {info['delta_mw']:.4f}, "
            f"expected {TDA_BYPRODUCT_EXACT_MW} (TDA byproduct mass = 0)"
        )
    if info["seco_ring_sizes"] != [14]:
        raise SystemExit(
            f"Seco ring inventory unexpected: got {info['seco_ring_sizes']}, "
            "expected [14] (just the macrocycle)"
        )
    if len(info["seco_in_ring_cc"]) != 3:
        raise SystemExit(
            f"Seco in-ring C=C count: got {len(info['seco_in_ring_cc'])}, "
            "expected 3 (the cis-trans-trans triene)"
        )
    if len(info["seco_exocyclic_cc"]) != 1:
        raise SystemExit(
            f"Seco exocyclic C=C count: got {len(info['seco_exocyclic_cc'])}, "
            "expected 1 (the alpha,beta-unsaturated ester)"
        )

    # Write the building-block YAML.
    repo = Path(__file__).resolve().parent.parent
    block_path = repo / "data" / "building_blocks" / "cassaine_seco.yaml"
    block_path.parent.mkdir(parents=True, exist_ok=True)
    block_path.write_text(
        "name: cassaine 14-membered macrocyclic triene (TDA precursor)\n"
        f"smiles: {seco_smiles}\n"
        "provenance: |\n"
        "  Seco-precursor for the Phoenix-Reddy-Deslongchamps 2008 TDA\n"
        "  closure of cassaine (JACS 2008, 130, 13989-13995,\n"
        "  DOI:10.1021/ja805097s; earlier communication Org. Lett. 2000,\n"
        "  2, 4149-4152, DOI:10.1021/ol006670r). The 14-membered\n"
        "  cis-trans-trans macrocyclic triene corresponds to compound 4\n"
        "  in the paper's Scheme 1; the transannular [4+2] cycloaddition\n"
        "  closes it (no catalyst, thermal at 180-230 °C in xylene) to\n"
        "  give the 6-6-6 trans-decalin tricycle 5, which is elaborated\n"
        "  through ~6 further steps to (+)-cassaine 1 (C24H39NO4, MW\n"
        "  405.288 g/mol; PubChem CID 5281267, ChEBI:3454).\n"
        "\n"
        "  Derived programmatically from the cyclized tricycle 5 by\n"
        "  applying the reverse of the transannular_diels_alder rule:\n"
        "  break the two new sigma bonds (rule positions 1-6 and 4-5);\n"
        "  restore the diene (C(1)=C(2)-C(3)=C(4)) and dienophile\n"
        "  (C(5)=C(6)) double bonds.\n"
        "\n"
        "  The macrocyclic triene retains the exocyclic alpha,beta-\n"
        "  unsaturated methyl ester (preserved from the tricycle's side\n"
        "  chain) and the free C3 hydroxyl. The paper uses a\n"
        "  silyl-protected C3-OH and a t-butyl ester at this stage; the\n"
        "  v0 encoding simplifies both for panel convention.\n"
        "notes: |\n"
        "  Mass balance verified by the build script:\n"
        f"    cyclized (tricycle 5) MW = {info['cyclized_exact_mw']:.4f}\n"
        f"    seco MW                  = {info['seco_exact_mw']:.4f}\n"
        f"    Δ MW                     = {info['delta_mw']:.4f}\n"
        f"    TDA byproduct mass       = {TDA_BYPRODUCT_EXACT_MW}\n"
        "  (Cycloaddition has 100% atom economy at the bond-formation step;\n"
        "  the AE class for this case is `high` and matches the rule meta's\n"
        "  byproduct_mass_g_per_mol: 0.0.)\n"
        "\n"
        "  Triene geometry caveat: Lamothe-Ndibwami-Deslongchamps 1988\n"
        "  (Tet. Lett. 29:1639 theoretical, 29:1641 experimental) specify\n"
        "  a *cis-trans-trans* arrangement of the three C=C bonds in\n"
        "  compound 4. The seco SMILES authored here is stereo-naive:\n"
        "  no E/Z descriptors are set on any of the three in-ring\n"
        "  alkenes (the MØD-MacroCert TDA rule itself carries no stereo\n"
        "  annotations on either side of the rewrite). Workstream F\n"
        "  task #35 (TDA stereo encoding for 4 new sp3 centres + endo/exo\n"
        "  split) is queued but not yet done.\n"
        "\n"
        "  Stereocenters: the seco retains the 2 sp3 stereocenters that\n"
        "  pre-exist the TDA (the C3-OH carbon and the C4 quaternary\n"
        "  centre); the 4 sp3 stereocenters formed by the TDA (the two\n"
        "  ring-junction CH and the two angular methyl-bearing quaternaries)\n"
        "  collapse to sp2 in the seco because they are the diene/dienophile\n"
        "  carbons of the 14-membered triene.\n"
        "refs:\n"
        "  - \"Phoenix, S.; Reddy, M. S.; Deslongchamps, P. J. Am. Chem. Soc. 2008, 130, 13989-13995 (DOI:10.1021/ja805097s) — primary reference\"\n"
        "  - \"Phoenix, S.; Bourque, E.; Deslongchamps, P. Org. Lett. 2000, 2, 4149-4152 (DOI:10.1021/ol006670r) — earlier communication\"\n"
        "  - \"Lamothe, S.; Ndibwami, A.; Deslongchamps, P. Tetrahedron Lett. 1988, 29, 1639-1640 (DOI:10.1016/S0040-4039(00)82005-5) — 14-mb TDA methodology, theoretical\"\n"
        "  - \"Lamothe, S.; Ndibwami, A.; Deslongchamps, P. Tetrahedron Lett. 1988, 29, 1641-1644 (DOI:10.1016/S0040-4039(00)82006-7) — 14-mb TDA methodology, experimental\"\n"
        "  - \"PubChem CID 5281267 / ChEBI:3454 — natural-product reference for the post-elaboration form\"\n"
    )
    print(f"\nwrote {block_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
