"""Build the post-TDA tricycle 5 from Phoenix-Reddy-Deslongchamps 2008.

The transannular Diels-Alder step in Phoenix, S.; Reddy, M. S.;
Deslongchamps, P. *J. Am. Chem. Soc.* **2008**, *130*, 13989-13995
(DOI 10.1021/ja805097s) closes a 14-membered macrocyclic *cis-trans-
trans* triene (compound 4) to give a 6-6-6 fused trans-decalin
tricycle (compound 5). TWO new sigma C-C bonds form in a single
pericyclic event; ONE in-ring alkene (the diene's middle 2=3 bond)
is retained in the product as a cyclohexene. Byproduct: NONE
(cycloaddition is byproduct-free; AE = 100%).

Compound 5 is then elaborated through ~6 further steps (stereoselective
reduction of the residual alkene, hydroboration, methyl cuprate 1,4-
addition, dimethylaminoethyloxycarbonyl tethering, C8 epimerization,
C3 deprotection) to give (+)-cassaine 1 (C24H39NO4, MW 405.288;
PubChem CID 5281267; ChEBI:3454). The panel encodes the TDA-immediate
product (compound 5) because that is the *actual* macrocyclization
event — the natural product itself has no residual cyclohexene for
the TDA rule to recognise on reverse synthesis.

Encoding choices for v0:
- Methyl ester side chain in place of the dimethylaminoethyl ester.
  The paper actually uses a tert-butyl ester at this stage; methyl
  is the panel convention (simpler, smaller).
- Free C3-OH (drop the silyl protecting group used in the paper).
- All 6 sp3 stereocenters retained: 4 new from TDA (C5, C8 junctions
  + C10, C13 quaternary methyl-bearing centres) + 2 pre-existing
  (C3-OH carbon and the α-methyl on the diene branch).
- One in-ring C=C alkene preserved (the TDA-residual diene 2=3
  alkene; cyclohexene fused to the trans-decalin).
- Exocyclic α,β-unsaturated ester preserved (the alkene was part of
  the diene system in compound 4; one end exits the cyclohexene as
  =C-COOR after TDA).

Stereo of the four new TDA-installed sp3 centres is NOT enforced by
the panel rule (Workstream F task #35 is queued but not yet done —
the v0 TDA rule has no stereo annotations). The encoded stereo is
the predicted Deslongchamps T4-transition-state product
(trans-decalin junctions, *endo* approach) but the campaign runs
without stereo enforcement on the TDA leg.

References:
- Phoenix, Reddy, Deslongchamps. JACS 2008, 130, 13989-13995.
  DOI 10.1021/ja805097s.
- Phoenix, Bourque, Deslongchamps. Org. Lett. 2000, 2, 4149-4152
  (earlier communication). DOI 10.1021/ol006670r.
- Lamothe, Ndibwami, Deslongchamps. Tet. Lett. 1988, 29, 1639/1641
  (14-membered TDA methodology, theoretical + experimental).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Tricycle 5 (post-TDA, pre-elaboration): 6-6-6 trans-decalin with a
# residual in-ring alkene (the TDA-preserved diene 2=3 bond) and an
# exocyclic alpha,beta-unsaturated methyl ester.
TRICYCLE5_SMILES = (
    "C[C@H]1/C(=C/C(=O)OC)CC[C@H]2[C@H]1C=C[C@H]1"
    "C(C)(C)[C@@H](O)CC[C@]21C"
)

TARGET_FORMULA = "C21H32O3"
TARGET_MW_EXACT = 332.2351   # Da
TARGET_RING_SIZES = [6, 6, 6]
TARGET_STEREO_COUNT = 6      # 4 from TDA + 2 pre-existing
TARGET_IN_RING_ALKENES = 1   # the TDA-residual cyclohexene C=C


def build_mol() -> Chem.Mol:
    m = Chem.MolFromSmiles(TRICYCLE5_SMILES)
    if m is None:
        raise SystemExit(f"RDKit failed to parse SMILES:\n  {TRICYCLE5_SMILES!r}")
    Chem.SanitizeMol(m)
    return m


def audit(mol: Chem.Mol) -> dict:
    """Panel-builder audit: formula, ring inventory, stereo, alkene set."""
    info: dict = {}
    info["formula"] = CalcMolFormula(mol)
    info["exact_mw"] = Descriptors.ExactMolWt(mol)
    info["smiles_canonical"] = Chem.MolToSmiles(
        mol, isomericSmiles=True, canonical=True
    )

    rings = mol.GetRingInfo()
    info["ring_sizes"] = sorted(len(r) for r in rings.AtomRings())
    info["num_rings"] = rings.NumRings()

    stereos = Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )
    info["all_stereocenters"] = stereos
    info["assigned_stereocenters"] = [s for s in stereos if s[1] in ("R", "S")]

    # Enumerate non-aromatic C=C double bonds and partition into in-ring
    # vs exocyclic.
    in_ring_alkenes = []
    exocyclic_alkenes = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetIsAromatic() or b.GetIsAromatic():
            continue
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        rec = {
            "atoms": (a.GetIdx(), b.GetIdx()),
            "stereo": str(bond.GetStereo()),
        }
        if bond.IsInRing():
            in_ring_alkenes.append(rec)
        else:
            exocyclic_alkenes.append(rec)
    info["in_ring_alkenes"] = in_ring_alkenes
    info["exocyclic_alkenes"] = exocyclic_alkenes
    return info


def write_v2000(mol_h: Chem.Mol, out_path: Path, title: str) -> None:
    """Write a strict V2000 Molfile via openbabel (matches panel convention)."""
    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        Chem.MolToMolFile(mol_h, str(tmp))
        subprocess.run(
            ["obabel", str(tmp), "-O", str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)
    # Patch obabel's title line so it carries the citation.
    text = out_path.read_text()
    lines = text.splitlines()
    if lines:
        lines[0] = title
    out_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    mol = build_mol()
    info = audit(mol)
    print(f"formula              : {info['formula']}   (expected {TARGET_FORMULA})")
    print(f"exact MW             : {info['exact_mw']:.4f}   "
          f"(expected ≈ {TARGET_MW_EXACT})")
    print(f"ring sizes           : {info['ring_sizes']}   "
          f"(expected {TARGET_RING_SIZES})")
    print(f"num rings            : {info['num_rings']}   (expected 3)")
    print(f"stereocenters (R/S)  : {len(info['assigned_stereocenters'])} assigned "
          f"(expected {TARGET_STEREO_COUNT})")
    for sc in info["assigned_stereocenters"]:
        print(f"   atom {sc[0]:>2d}  -> {sc[1]}")
    print(f"in-ring C=C alkenes  : {len(info['in_ring_alkenes'])} "
          f"(expected {TARGET_IN_RING_ALKENES})")
    for a in info["in_ring_alkenes"]:
        print(f"   {a['atoms'][0]:>2d}={a['atoms'][1]:<2d}  stereo={a['stereo']}")
    print(f"exocyclic C=C alkenes: {len(info['exocyclic_alkenes'])} "
          f"(expected 1; the α,β-unsat ester)")
    for a in info["exocyclic_alkenes"]:
        print(f"   {a['atoms'][0]:>2d}={a['atoms'][1]:<2d}  stereo={a['stereo']}")
    print(f"canonical SMILES     : {info['smiles_canonical']}")
    print()

    # Audit gates
    if info["formula"] != TARGET_FORMULA:
        raise SystemExit(
            f"formula mismatch: got {info['formula']}, expected {TARGET_FORMULA}"
        )
    if info["ring_sizes"] != TARGET_RING_SIZES:
        raise SystemExit(
            f"ring sizes mismatch: got {info['ring_sizes']}, "
            f"expected {TARGET_RING_SIZES}"
        )
    if info["num_rings"] != 3:
        raise SystemExit(
            f"expected 3 fused rings; got {info['num_rings']}"
        )
    if len(info["assigned_stereocenters"]) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"stereocenter count: got {len(info['assigned_stereocenters'])}, "
            f"expected {TARGET_STEREO_COUNT}"
        )
    if len(info["in_ring_alkenes"]) != TARGET_IN_RING_ALKENES:
        raise SystemExit(
            f"expected exactly {TARGET_IN_RING_ALKENES} in-ring C=C "
            f"(the TDA-residual cyclohexene); got {len(info['in_ring_alkenes'])}"
        )

    # 3D embed via ETKDG + MMFF
    mh = Chem.AddHs(mol)
    used_2d = False
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xCA55A1, useRandomCoords=True, maxAttempts=200,
    )
    if embed_ok != 0:
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.randomSeed = 0xDEC0DE
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        embed_ok = AllChem.EmbedMolecule(
            mh, randomSeed=0xBEEF, useRandomCoords=True, maxAttempts=2000,
            ignoreSmoothingFailures=True,
        )
    if embed_ok != 0:
        print("3D embedding failed; falling back to 2D coordinates.")
        AllChem.Compute2DCoords(mh)
        used_2d = True
    else:
        try:
            AllChem.MMFFOptimizeMolecule(mh, maxIters=2000)
        except Exception:
            AllChem.UFFOptimizeMolecule(mh, maxIters=2000)

    out_dir = (
        Path(__file__).resolve().parent.parent
        / "data" / "validation_panel" / "phoenix_reddy_cassaine_tda_2008"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"
    suffix = "2D-RDKit-fallback" if used_2d else "3D-RDKit"
    title = f"cassaine_tricycle5 PhoenixReddy2008 JACS130:13989 {suffix}"
    write_v2000(mh, out_path, title)
    print(f"wrote {out_path}  (used_2d={used_2d})")

    # Canonical SMILES audit alongside.
    audit_path = out_dir / "canonical_smiles.txt"
    audit_path.write_text(
        "# Canonical isomeric SMILES for Phoenix-Reddy-Deslongchamps\n"
        "# 2008 TDA-immediate intermediate (tricycle 5).\n"
        "#\n"
        "# 6-6-6 fused trans-decalin with one residual in-ring alkene\n"
        "# (the TDA-preserved diene 2=3 bond, retained as a cyclohexene)\n"
        "# and an exocyclic alpha,beta-unsaturated methyl ester.\n"
        "# Compound 5 is elaborated through ~6 further steps to (+)-cassaine\n"
        "# 1 (PubChem CID 5281267, C24H39NO4, MW 405.288). v0 uses the\n"
        "# methyl ester in place of the dimethylaminoethyl ester for panel\n"
        "# convention; the C3 hydroxyl is shown unprotected (the paper\n"
        "# uses a silyl protecting group at this stage).\n"
        "#\n"
        f"# formula:   {info['formula']}\n"
        f"# exact MW:  {info['exact_mw']:.4f}\n"
        f"# rings:     {info['ring_sizes']}\n"
        f"# stereocs:  {info['assigned_stereocenters']}\n"
        "# refs:      10.1021/ja805097s, 10.1021/ol006670r,\n"
        "#            10.1016/S0040-4039(00)82005-5 (theoretical),\n"
        "#            10.1016/S0040-4039(00)82006-7 (experimental).\n"
        f"{info['smiles_canonical']}\n"
    )
    print(f"wrote {audit_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
