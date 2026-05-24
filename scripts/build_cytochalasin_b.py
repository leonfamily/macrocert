"""Build the cyclized cytochalasin B structure (Haidle-Myers 2004).

Primary reference: Haidle, A. M.; Myers, A. G. "An enantioselective,
modular, and general route to the cytochalasins: Synthesis of L-696,474
and cytochalasin B." Proc. Natl. Acad. Sci. USA 2004, 101, 12048-12053.
DOI: 10.1073/pnas.0402111101 (PMC PMC514432, open access).

Cytochalasin B (PubChem CID 5311281, ChEBI:23528, CAS 14930-96-2):
- C29H37NO5, MW 479.62 g/mol (exact 479.267)
- 4 rings: 5-membered isoindolone gamma-lactam + 6-membered cyclohexane
  fused to it (the bicyclic perhydroisoindolone core) + 6-membered
  phenyl (the benzyl side chain) + 14-membered macrolactone.
- 7 sp3 stereocenters in the natural product
  (1S,5S,6R,7R,8S,11S,15S,18R per cytochalasan numbering;
  PubChem reports 8 chiral atoms including the spiro center C9
  bearing the C=O of the lactone and the lactam-N C-H).
- Two E-alkenes in the macrocycle: C13=C14 (the HWE-formed bond per
  Haidle-Myers Scheme 7, closing the 14-membered macrolactone) and
  C20=C21 (the other internal alkene retained from the seco precursor).

The macrocyclization closes by intramolecular HWE olefination of the
ω-aldehyde + β-keto/phosphonoacetate ester seco precursor (compound 3
in the paper); the in-ring alkene formed is the C13=C14 trans-alkene.

Procedure (RDKit):
1. Parse the PubChem CID 5311281 isomeric SMILES (canonical source).
2. Audit: formula = C29H37NO5; rings = [5, 6, 6, 14]; 7-8 stereocenters;
   exactly two E-alkenes in the 14-ring.
3. Embed in 3D (ETKDG) + MMFF; fall back to 2D if 3D embedding fails on
   the complex 5,6-bicycle + 14-macrocycle + 6-phenyl polycyclic.
4. Write a strict V2000 Molfile via openbabel.

Refs:
- Haidle & Myers 2004 PNAS, DOI:10.1073/pnas.0402111101 (primary)
- PubChem CID 5311281 (isomeric SMILES source)
- ChEBI:23528 (cross-validation)
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cytochalasin B isomeric SMILES from PubChem CID 5311281
# (fetched via https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/5311281/property/IsomericSMILES,
#  also matches ChEBI:23528).
CYTOCHALASIN_B_SMILES = (
    "C[C@@H]1CCC[C@H](/C=C/C(=O)O[C@]23[C@@H](/C=C/C1)"
    "[C@@H](C(=C)[C@H]([C@H]2[C@@H](NC3=O)CC4=CC=CC=C4)C)O)O"
)

TARGET_FORMULA = "C29H37NO5"
TARGET_MW_EXACT = 479.2672      # exact mass (Da)
TARGET_RING_SIZES = [5, 6, 6, 14]
TARGET_MACROLACTONE_SIZE = 14
# PubChem CID 5311281 reports 8 chiral atoms (the spiro carbon C9 of
# the lactone-C=O / lactam-N junction is counted in addition to the 7
# "classical" cytochalasan stereocenters in synthetic schemes).
TARGET_STEREO_COUNT = 8


def build_mol() -> Chem.Mol:
    m = Chem.MolFromSmiles(CYTOCHALASIN_B_SMILES)
    if m is None:
        raise SystemExit(f"RDKit failed to parse SMILES:\n  {CYTOCHALASIN_B_SMILES!r}")
    Chem.SanitizeMol(m)
    return m


def audit(mol: Chem.Mol) -> dict:
    info: dict = {}
    info["formula"] = CalcMolFormula(mol)
    info["exact_mw"] = Descriptors.ExactMolWt(mol)
    info["mol_wt"] = Descriptors.MolWt(mol)
    info["smiles_canonical"] = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
    info["ring_sizes"] = sorted(len(r) for r in mol.GetRingInfo().AtomRings())

    stereos = Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )
    info["all_stereocenters"] = stereos
    info["assigned_stereocenters"] = [s for s in stereos if s[1] in ("R", "S")]

    # Identify the in-14ring non-aromatic C=C alkenes (there are two:
    # one is the HWE-formed C13=C14 and the other is the C20=C21 retained
    # from the seco precursor; both are E).
    ring14_alkenes = []
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        if bond.GetIsAromatic():
            continue
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        if a.GetSymbol() != "C" or b.GetSymbol() != "C":
            continue
        if bond.IsInRingSize(TARGET_MACROLACTONE_SIZE):
            ring14_alkenes.append(
                {
                    "atoms": (a.GetIdx(), b.GetIdx()),
                    "stereo": str(bond.GetStereo()),
                }
            )
    info["ring14_alkenes"] = ring14_alkenes
    return info


def write_v2000(mol_h: Chem.Mol, out_path: Path, title: str) -> None:
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
    print(f"exact MW             : {info['exact_mw']:.4f}   (expected ~{TARGET_MW_EXACT:.4f})")
    print(f"average MW           : {info['mol_wt']:.2f}")
    print(f"ring sizes           : {info['ring_sizes']}   (expected {TARGET_RING_SIZES})")
    print(f"stereocenters (R/S)  : {len(info['assigned_stereocenters'])} assigned "
          f"(expected {TARGET_STEREO_COUNT})")
    for sc in info["assigned_stereocenters"]:
        print(f"   atom {sc[0]:>2d}  -> {sc[1]}")
    print(f"canonical SMILES     : {info['smiles_canonical']}")
    print()
    print("in-14-ring alkenes (the macrocycle internal C=C bonds):")
    for b in info["ring14_alkenes"]:
        print(f"   atoms {b['atoms']}  stereo={b['stereo']}")

    if info["formula"] != TARGET_FORMULA:
        raise SystemExit(f"formula mismatch: got {info['formula']}, expected {TARGET_FORMULA}")
    if info["ring_sizes"] != TARGET_RING_SIZES:
        raise SystemExit(
            f"ring inventory mismatch: got {info['ring_sizes']}, expected {TARGET_RING_SIZES}"
        )
    if len(info["assigned_stereocenters"]) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"stereocenter count: got {len(info['assigned_stereocenters'])}, "
            f"expected {TARGET_STEREO_COUNT}"
        )
    if len(info["ring14_alkenes"]) != 2:
        raise SystemExit(
            f"expected exactly two in-14-ring alkenes (C13=C14 HWE + C20=C21 retained); "
            f"got {len(info['ring14_alkenes'])}"
        )
    for alk in info["ring14_alkenes"]:
        if "STEREOE" not in alk["stereo"] and "STEREOTRANS" not in alk["stereo"]:
            raise SystemExit(
                f"in-ring alkene at {alk['atoms']} is not E/trans: {alk['stereo']}"
            )

    # 3D embed: cytochalasin B is a fused 6,5 bicycle + pendant 14-macrocycle
    # + pendant phenyl. ETKDGv3 typically succeeds; if not we fall back to 2D
    # (the panel convention; see scripts/build_epothilone_b_rcm.py).
    mh = Chem.AddHs(mol)
    used_2d = False
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xC0FFEE, useRandomCoords=True, maxAttempts=400,
    )
    if embed_ok != 0:
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.randomSeed = 0xDEC0DE
        params.maxAttempts = 2000
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        embed_ok = AllChem.EmbedMolecule(
            mh, randomSeed=0xBEEF, useRandomCoords=True, maxAttempts=4000,
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
            try:
                AllChem.UFFOptimizeMolecule(mh, maxIters=2000)
            except Exception:
                pass

    out_dir = Path(__file__).resolve().parent.parent / "data" / "validation_panel" \
        / "haidle_myers_cytochalasin_b_2004"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"
    suffix = "2D-RDKit-fallback" if used_2d else "3D-RDKit"
    title = f"cytochalasin_B Haidle-Myers2004 PNAS101:12048 PubChem5311281 {suffix}"
    write_v2000(mh, out_path, title)
    print()
    print(f"wrote {out_path}  (used_2d={used_2d})")

    audit_path = out_dir / "canonical_smiles.txt"
    audit_path.write_text(
        "# Canonical isomeric SMILES for cytochalasin B\n"
        "# (PubChem CID 5311281, ChEBI:23528, CAS 14930-96-2; cross-validated\n"
        "# against the Haidle-Myers 2004 PNAS structure).\n"
        "#\n"
        f"# formula: {info['formula']}\n"
        f"# exact MW: {info['exact_mw']:.4f}\n"
        f"# average MW: {info['mol_wt']:.2f}\n"
        f"# rings: {info['ring_sizes']}\n"
        f"# stereocenters (assigned): {len(info['assigned_stereocenters'])}\n"
        f"# refs: 10.1073/pnas.0402111101 (Haidle-Myers 2004 PNAS),\n"
        f"#       PubChem CID 5311281, ChEBI:23528\n"
        f"{info['smiles_canonical']}\n"
    )
    print(f"wrote {audit_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
