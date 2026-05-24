"""Build the post-RCM intermediate for epothilone B (Nicolaou 1997).

The RCM step in Nicolaou's 1997 synthesis (JACS 1997, 119, 7974–7991;
DOI 10.1021/ja971110h; also Nature 1997, 387, 268, DOI 10.1038/387268a0)
closes the C12–C13 alkene of the seco-acid diene to give the
12,13-deepoxy-epothilone B intermediate. The natural-product epoxide
at C12–C13 is installed *after* the RCM by a separate DMDO/m-CPBA
epoxidation — so the macrocyclization product encoded for the panel
is the **(12Z)-12,13-didehydro-12,13-deoxy-epothilone B** (the
"deepoxy epothilone B" alkene intermediate, formula C27H41NO5S,
MW 491.27).

Stereo (deepoxy form):
- 5 sp3 stereocenters retained from epothilone B numbering:
  C3 (S), C6 (R), C7 (S), C8 (S), C15 (S)
- C12=C13 in-ring alkene: **Z** (Nicolaou's matched-Grubbs case;
  in the original 1997 paper the substrate gave ~1:1 E:Z and the
  Z isomer was chromatographically separated)
- C16=C17 exocyclic vinyl tether to the thiazole: E

Approach: author the cyclized SMILES from the research brief
(Option B), verify formula/rings/stereo, embed in 3D via RDKit,
optimise with MMFF, write strict V2000 via openbabel.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# 12,13-deepoxy epothilone B (post-RCM, before epoxidation).
# Derived from the natural-product epothilone B SMILES
# (ChEBI:31550, cross-validated against LIPID MAPS LMPK04000041,
# IUPHAR ligand 13600, NP-MRD NP0013985) by replacing the
# cis-(12R,13S) epoxide with the (12Z) alkene that the RCM step
# actually produces. See research_brief.md §5 (Option B).
DEEPOXY_SMILES = (
    "C[C@H]1CCC/C(C)=C\\C[C@@H](OC(=O)C[C@H](O)C(C)(C)[C@@H](O)"
    "[C@H](C)C1=O)/C(C)=C/c1csc(C)n1"
)

TARGET_FORMULA = "C27H41NO5S"
TARGET_MW_EXACT = 491.2705   # exact mass (Da)
TARGET_STEREO_COUNT = 5      # sp3 chiral centres after epoxide → alkene
TARGET_RING_SIZE = 16        # macrocycle (RCM closure)


def build_mol() -> Chem.Mol:
    m = Chem.MolFromSmiles(DEEPOXY_SMILES)
    if m is None:
        raise SystemExit(f"RDKit failed to parse SMILES:\n  {DEEPOXY_SMILES!r}")
    Chem.SanitizeMol(m)
    return m


def audit(mol: Chem.Mol) -> dict:
    """Run the panel-builder audit: formula, ring inventory, stereo."""
    info: dict = {}
    info["formula"] = CalcMolFormula(mol)
    info["exact_mw"] = Descriptors.ExactMolWt(mol)
    info["smiles_canonical"] = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)

    rings = mol.GetRingInfo()
    info["ring_sizes"] = sorted(len(r) for r in rings.AtomRings())

    stereos = Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )
    info["all_stereocenters"] = stereos
    info["assigned_stereocenters"] = [s for s in stereos if s[1] in ("R", "S")]

    # Identify the in-ring RCM alkene (Z) and the exocyclic thiazole vinyl (E).
    ring16 = None
    for r in rings.AtomRings():
        if len(r) == TARGET_RING_SIZE:
            ring16 = set(r)
            break
    if ring16 is None:
        raise SystemExit("16-membered ring missing in built structure")
    info["ring16_atom_ids"] = sorted(ring16)

    bond_summary = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        ai, bi = mol.GetAtomWithIdx(a), mol.GetAtomWithIdx(b)
        # Skip aromatic ring double-bonds inside the thiazole.
        if ai.GetIsAromatic() or bi.GetIsAromatic():
            continue
        in_ring16 = (a in ring16) and (b in ring16)
        stereo = bond.GetStereo()
        bond_summary.append({
            "atoms": (a, ai.GetSymbol(), b, bi.GetSymbol()),
            "in_ring16": in_ring16,
            "stereo": str(stereo),
        })
    info["nonaromatic_double_bonds"] = bond_summary
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
    print(f"exact MW             : {info['exact_mw']:.4f}   (expected ≈ {TARGET_MW_EXACT:.4f})")
    print(f"ring sizes           : {info['ring_sizes']}")
    print(f"stereocenters (R/S)  : {len(info['assigned_stereocenters'])} assigned "
          f"(expected {TARGET_STEREO_COUNT})")
    for sc in info["assigned_stereocenters"]:
        print(f"   atom {sc[0]:>2d}  -> {sc[1]}")
    print(f"canonical SMILES     : {info['smiles_canonical']}")
    print()
    print("non-aromatic double bonds:")
    for b in info["nonaromatic_double_bonds"]:
        a_idx, a_sym, b_idx, b_sym = b["atoms"]
        flag = "  ← in 16-ring (RCM alkene)" if b["in_ring16"] else "  (exocyclic / C=O)"
        print(f"   {a_idx:>2d}{a_sym}={b_idx:>2d}{b_sym}  stereo={b['stereo']:>10s}{flag}")

    # Audit gates
    if info["formula"] != TARGET_FORMULA:
        raise SystemExit(f"formula mismatch: got {info['formula']}, expected {TARGET_FORMULA}")
    if TARGET_RING_SIZE not in info["ring_sizes"]:
        raise SystemExit(f"no {TARGET_RING_SIZE}-ring in built structure")
    if len(info["assigned_stereocenters"]) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"stereocenter count: got {len(info['assigned_stereocenters'])}, "
            f"expected {TARGET_STEREO_COUNT}"
        )
    # Find ring-16 Z alkene
    ring16_alkenes = [
        b for b in info["nonaromatic_double_bonds"] if b["in_ring16"]
    ]
    if len(ring16_alkenes) != 1:
        raise SystemExit(
            f"expected exactly one in-ring alkene (the C12=C13 RCM bond); "
            f"got {len(ring16_alkenes)}"
        )
    # RDKit reports either STEREOZ or STEREOCIS for the cis (Z) configuration
    # depending on whether the descriptor was set by SMILES /...\\ markers
    # (→ STEREOZ) or by CIP analysis on neighbour priorities (→ STEREOCIS).
    # Both are valid Z designators; trans/E is the opposite.
    in_ring_stereo = ring16_alkenes[0]["stereo"]
    if "STEREOZ" not in in_ring_stereo and "STEREOCIS" not in in_ring_stereo:
        raise SystemExit(
            f"in-ring alkene stereo not Z (cis): {in_ring_stereo}"
        )

    # 3D embed
    mh = Chem.AddHs(mol)
    used_2d = False
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xC0FFEE, useRandomCoords=True, maxAttempts=200,
    )
    if embed_ok != 0:
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.randomSeed = 0xDEC0DE
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        # one more aggressive retry
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

    out_dir = Path(__file__).resolve().parent.parent / "data" / "validation_panel" \
        / "epothilone_b_nicolaou_rcm_1997"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"
    suffix = "2D-RDKit-fallback" if used_2d else "3D-RDKit"
    title = f"deepoxy_epothilone_B Nicolaou1997 JACS119:7974 {suffix}"
    write_v2000(mh, out_path, title)
    print()
    print(f"wrote {out_path}  (used_2d={used_2d})")

    # Also write canonical SMILES audit alongside.
    audit_path = out_dir / "canonical_smiles.txt"
    audit_path.write_text(
        "# Canonical isomeric SMILES for 12,13-deepoxy-epothilone B\n"
        "# (the post-RCM intermediate; epothilone B is reached by\n"
        "# subsequent DMDO epoxidation of the C12=C13 alkene).\n"
        "#\n"
        f"# formula: {info['formula']}\n"
        f"# exact MW: {info['exact_mw']:.4f}\n"
        f"# rings: {info['ring_sizes']}\n"
        f"# stereocenters: {info['assigned_stereocenters']}\n"
        f"# refs: 10.1021/ja971110h, 10.1038/387268a0\n"
        f"{info['smiles_canonical']}\n"
    )
    print(f"wrote {audit_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
