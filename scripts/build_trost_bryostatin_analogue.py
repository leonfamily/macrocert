"""Build the Trost ring-expanded bryostatin analogue (2007 JACS) as a V2000 Molfile.

Trost-Yang-Thiel-Frontier-Brindle 2007 (J. Am. Chem. Soc. 129, 2206-2207;
DOI 10.1021/ja067305j; full paper Trost-Yang-Dong 2011 Chem. Eur. J. 17,
9789-9805, DOI 10.1002/chem.201002932). The 31-membered macrolactone
formed by Grubbs-Hoveyda 2nd-generation RCM on a diene-tethered seco
substrate; 80% yield, 1:1 E:Z mixture, benzene, 50-80 C, high dilution.
The only published bryostatin-family RCM macrocyclization — see
research_brief.md for the full literature diagnosis.

ENCODING CAVEAT — synthetic analogue, no public-database SMILES.

The analogue is NOT in PubChem/ChEBI/CCDC. Its structure is published
only in Trost 2007 JACS SI compound 3 and Trost 2011 Chem. Eur. J.
SI compounds 177-179, behind ACS/Wiley paywalls. The Jahan 2023
SynOpen review Scheme 19 (DOI 10.1055/s-0042-1751453, open access)
provides a redrawing without atomic-level resolution. We encode a
chemistry-faithful 31-membered macrolactone that captures the
essential features Macrocert's RCM rule cares about:

  - exactly 31 atoms in the macrocyclic ring (the predicate's outlier)
  - one in-ring C=C alkene (the RCM-formed bond, E in the encoded form)
  - one in-ring lactone ester C(=O)-O (the pre-formed macrolactone)
  - two embedded tetrahydropyran rings (the bryostatin A and C rings;
    each contributes 2 atoms to the macrocycle via a shared C-C edge)
  - a pendant methyl-(2E)-2-methyl-fumarate-style ester arm at one
    macrocycle carbon (the bryostatin "vinyl methyl ester"/cinnamate
    chromophore — captured as -O-C(=O)/C=C(C)/C(=O)OC)
  - two -OH groups on pyranose A and two OAc protecting groups
    (one on a macrocycle CH and one on pyranose C; matches the
    pattern of bryostatin's hydroxyl + acetate decoration)
  - 9 sp3 stereocenters (4 in pyranose ring atoms + 5 in the
    macrocyclic backbone/branch carbons) -- bryostatin natural has
    11; the encoding's 9 is a conservative subset consistent with
    the L-(natural)-configuration of bryostatin's chiral pool.

This is NOT the precise atom-by-atom structure of Trost compound 3
(that requires the SI). It IS a valid molecular skeleton that
exercises the same rule (rcm) on the same ring size (31) under the
same byproduct accounting (ethylene). The panel's claim is that
Macrocert's RCM rule fires correctly on a 31-membered diene seco
to produce a 31-membered cycloalkene macrocycle plus ethylene. That
claim is testable on this encoded molecule independent of the exact
side-chain identities.

Approach: parse the authored SMILES, audit formula/rings/stereo,
attempt 3D embed (likely fails for a 31-ring — fall back to 2D
coordinates), write strict V2000 via openbabel.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Trost ring-expanded bryostatin analogue encoded structure.
# 31-membered macrolactone with embedded pyranose A (with 2 OH) and
# pyranose C (with one OAc), pendant methyl-fumarate-style ester arm,
# and a backbone CH-OAc. See module docstring for the encoding contract.
CYCLIZED_SMILES = (
    "O=C1OCC[C@H](OC(=O)/C=C(\\C)/C(=O)OC)C"
    "[C@@H]3O[C@@H](O)C[C@@H](O)[C@H]3"
    "CCC[C@@H](OC(C)=O)"
    "/C=C/"
    "CCCC"
    "[C@@H]4OC[C@H](OC(C)=O)C[C@H]4"
    "CCCCCCCCCCC1"
)

TARGET_FORMULA = "C46H74O14"
TARGET_RING_SIZE = 31
TARGET_STEREO_COUNT = 9


def build_mol() -> Chem.Mol:
    m = Chem.MolFromSmiles(CYCLIZED_SMILES)
    if m is None:
        raise SystemExit(f"RDKit failed to parse SMILES:\n  {CYCLIZED_SMILES!r}")
    Chem.SanitizeMol(m)
    return m


def audit(mol: Chem.Mol) -> dict:
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

    # Locate the 31-membered macrocycle and the in-ring RCM alkene.
    macro = None
    for r in rings.AtomRings():
        if len(r) == TARGET_RING_SIZE:
            macro = set(r)
            break
    if macro is None:
        raise SystemExit(f"{TARGET_RING_SIZE}-membered ring missing")
    info["macrocycle_atom_ids"] = sorted(macro)

    # In-ring non-aromatic C=C alkenes — should be exactly one (the RCM bond).
    # The ester C=O is in-ring but C=O (not C=C); skip.
    bond_summary = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        ai, bi = mol.GetAtomWithIdx(a), mol.GetAtomWithIdx(b)
        if ai.GetIsAromatic() or bi.GetIsAromatic():
            continue
        in_macro = (a in macro) and (b in macro)
        is_cc = ai.GetSymbol() == "C" and bi.GetSymbol() == "C"
        stereo = bond.GetStereo()
        bond_summary.append({
            "atoms": (a, ai.GetSymbol(), b, bi.GetSymbol()),
            "in_macro": in_macro,
            "is_cc": is_cc,
            "stereo": str(stereo),
        })
    info["nonaromatic_double_bonds"] = bond_summary
    return info


def write_v2000(mol_h: Chem.Mol, out_path: Path, title: str) -> None:
    """Write strict V2000 Molfile via openbabel."""
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
    text = out_path.read_text()
    lines = text.splitlines()
    if lines:
        lines[0] = title
    out_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    mol = build_mol()
    info = audit(mol)
    print(f"formula              : {info['formula']}   (expected {TARGET_FORMULA})")
    print(f"exact MW             : {info['exact_mw']:.4f}")
    print(f"ring sizes           : {info['ring_sizes']}")
    print(f"stereocenters (R/S)  : {len(info['assigned_stereocenters'])} assigned "
          f"(expected {TARGET_STEREO_COUNT})")
    for sc in info["assigned_stereocenters"]:
        print(f"   atom {sc[0]:>3d}  -> {sc[1]}")
    print(f"canonical SMILES     : {info['smiles_canonical']}")
    print()
    print("non-aromatic double bonds:")
    for b in info["nonaromatic_double_bonds"]:
        a_idx, a_sym, b_idx, b_sym = b["atoms"]
        tag = ""
        if b["in_macro"] and b["is_cc"]:
            tag = "  <- in 31-ring (RCM alkene)"
        elif b["in_macro"]:
            tag = "  (in 31-ring, C=O of lactone)"
        else:
            tag = "  (exocyclic / pendant arm)"
        print(f"   {a_idx:>3d}{a_sym}={b_idx:>3d}{b_sym}  stereo={b['stereo']:>14s}{tag}")

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
    in_ring_cc = [
        b for b in info["nonaromatic_double_bonds"]
        if b["in_macro"] and b["is_cc"]
    ]
    if len(in_ring_cc) != 1:
        raise SystemExit(
            f"expected exactly one in-ring C=C (the RCM bond); got {len(in_ring_cc)}"
        )

    # 3D embed (likely to fail for 31-ring; fall back to 2D)
    mh = Chem.AddHs(mol)
    used_2d = False
    print("\nattempting 3D embedding (31-ring is large; may fall back to 2D)...")
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xC0FFEE, useRandomCoords=True, maxAttempts=200,
    )
    if embed_ok != 0:
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.randomSeed = 0xDEC0DE
        params.maxAttempts = 500
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        # 31-ring may exceed RDKit's distance-geometry resolver. Use 2D.
        print("3D embedding failed; falling back to 2D coordinates.")
        AllChem.Compute2DCoords(mh)
        used_2d = True
    else:
        try:
            AllChem.MMFFOptimizeMolecule(mh, maxIters=2000)
            print("MMFF optimization succeeded.")
        except Exception:
            AllChem.UFFOptimizeMolecule(mh, maxIters=2000)
            print("MMFF failed; UFF optimization succeeded.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "validation_panel" \
        / "trost_bryostatin_analogue_rcm_2007"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"
    suffix = "2D-RDKit-fallback" if used_2d else "3D-RDKit"
    title = f"trost_bryostatin_analogue Trost2007 JACS129:2206 {suffix}"
    write_v2000(mh, out_path, title)
    print(f"\nwrote {out_path}  (used_2d={used_2d})")

    audit_path = out_dir / "canonical_smiles.txt"
    audit_path.write_text(
        "# Canonical isomeric SMILES for the Trost ring-expanded\n"
        "# bryostatin analogue (2007 JACS 129:2206, full paper 2011\n"
        "# Chem. Eur. J. 17:9789). 31-membered macrolactone with two\n"
        "# embedded pyranose rings and an in-ring RCM-formed alkene.\n"
        "#\n"
        f"# formula        : {info['formula']}\n"
        f"# exact MW       : {info['exact_mw']:.4f}\n"
        f"# rings          : {info['ring_sizes']}\n"
        f"# stereocenters  : {len(info['assigned_stereocenters'])} assigned\n"
        f"# refs           : 10.1021/ja067305j, 10.1002/chem.201002932,\n"
        f"#                  10.1055/s-0042-1751453 (open-access redrawing)\n"
        f"# encoding note  : synthetic analogue, no public-DB SMILES;\n"
        f"#                  see scripts/build_trost_bryostatin_analogue.py\n"
        f"#                  docstring for the chemistry-faithful encoding contract.\n"
        f"{info['smiles_canonical']}\n"
    )
    print(f"wrote {audit_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
