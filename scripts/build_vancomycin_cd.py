"""Build the vancomycin C-O-D ring model substrate (Boger 1999) as a V2000 Molfile.

The full vancomycin aglycon (C53H53Cl2N9O20, MW 1144.93) is too sterically
demanding for clean 3D embedding via RDKit/MMFF. For the M5 panel case we
encode the **CD-ring model compound** in the style of Boger's JOC 1999
(64, 70-80) substrates — a 16-membered biaryl ether macrocycle that
captures the SNAr disconnection without the full heptapeptide.

Topology of the cyclized 16-membered macrocycle:
    O - 4 atoms Ar(C) (para-linked: Hpg surrogate, OH was para to C-alpha)
      - C(=O) - N - C-alpha(C) - C(=O) - N - C-alpha(B)
      - C(=O) - N - C-alpha(D) - 2 atoms Ar(D) (ortho-linked: phenylglycine,
        was Ar-F with ortho-NO2 before SNAr)
      - back to O

  Side chains / substituents (not in ring):
    - C-alpha(C, B, A): methyl (alanine simplification; vancomycin's true side
      chains are Hpg/Cl-Tyr/N-Me-leu but the rule-firing test doesn't depend
      on side chain identity)
    - Ar(C): meta methyl pair removed; just the para-O bridge.
    - Ar(D): ortho-NO2 retained (the SNAr activator — Boger 1999 reduces it
      AFTER macrocyclization; the cyclized intermediate carries the NO2).
    - Ar(D): meta Cl in vancomycin position-corresponding placement.
    - C-alpha(D): pendant C(=O)NHMe to mimic the C-terminal amide cap.

Stereochemistry: all three C-alpha atoms are L-amino-acid configured
(SS configuration on the natural backbone; the C-terminal CalphaD comes
out R via CIP because of the pendant amide priority).

References:
- Boger, Miyazaki, Kim, Wu, Castle, Loiseleur, Jin. J. Am. Chem. Soc.
  1999, 121, 10004-10011. DOI:10.1021/ja992577q (vancomycin aglycon).
- Boger, Castle, Miyazaki, Wu, Beresis, Loiseleur. J. Org. Chem.
  1999, 64, 70-80. DOI:10.1021/jo980880o (CD/DE model methodology).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# Cyclized CD-ring model substrate SMILES (16-membered biaryl ether macrocycle).
# Ring perimeter:
#   O - Ar(C) ipso - Ar(C) - Ar(C) - Ar(C) para - C(=O) - N - C-alpha(C)
#   - C(=O) - N - C-alpha(B) - C(=O) - N - C-alpha(D) - Ar(D) ortho - Ar(D) ipso - O
CYCLIZED_SMILES = (
    "O1c2ccc(C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C(=O)NC)"
    "c3cc(Cl)cc([N+](=O)[O-])c31)cc2"
)

TARGET_FORMULA = "C22H22ClN5O7"
TARGET_STEREO_COUNT = 3  # 3 C-alpha atoms
RING_SIZE = 16


def main(out_dir: Path) -> None:
    mol = Chem.MolFromSmiles(CYCLIZED_SMILES)
    if mol is None:
        raise SystemExit(f"Failed to parse cyclized SMILES")
    Chem.SanitizeMol(mol)

    formula = CalcMolFormula(mol)
    if formula != TARGET_FORMULA:
        raise SystemExit(f"Formula mismatch: got {formula}, expected {TARGET_FORMULA}")

    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    stereos = Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )
    assigned = [s for s in stereos if s[1] in ("R", "S")]
    if len(assigned) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"Stereo count mismatch: got {len(assigned)} ({stereos}), "
            f"expected {TARGET_STEREO_COUNT}"
        )

    # Verify 16-ring is present.
    ring_sizes = sorted([len(r) for r in mol.GetRingInfo().AtomRings()], reverse=True)
    if RING_SIZE not in ring_sizes:
        raise SystemExit(
            f"No {RING_SIZE}-membered ring found; rings = {ring_sizes}"
        )

    iso_smi = Chem.MolToSmiles(mol)
    print(f"formula:        {formula}")
    print(f"MW (exact):     {Descriptors.ExactMolWt(mol):.4f}")
    print(f"ring sizes:     {ring_sizes}")
    print(f"stereocenters:  {assigned}")
    print(f"canonical_smi:  {iso_smi}")

    mh = Chem.AddHs(mol)
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xC0FFEE, useRandomCoords=True, maxAttempts=200
    )
    used_2d = False
    if embed_ok != 0:
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.maxAttempts = 500
        params.randomSeed = 0xDEC0DE
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        print("3D embedding failed; falling back to 2D coordinates.")
        AllChem.Compute2DCoords(mh)
        used_2d = True
    else:
        try:
            AllChem.MMFFOptimizeMolecule(mh, maxIters=2000)
        except Exception:
            AllChem.UFFOptimizeMolecule(mh, maxIters=2000)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"

    # Write through obabel for strict V2000 output.
    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        Chem.MolToMolFile(mh, str(tmp))
        # Replace title block.
        text = tmp.read_text()
        lines = text.splitlines()
        lines[0] = (
            "vancomycin_CD_ring_model Boger1999 JACS121:10004 (3D-RDKit)"
            if not used_2d else
            "vancomycin_CD_ring_model Boger1999 JACS121:10004 (2D-fallback)"
        )
        tmp.write_text("\n".join(lines) + "\n")
        subprocess.run(
            ["obabel", str(tmp), "-O", str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)

    # Patch the obabel-written title line again (obabel rewrites it).
    text = out_path.read_text()
    lines = text.splitlines()
    if lines:
        lines[0] = (
            "vancomycin_CD_ring_model Boger1999 JACS121:10004 3D-RDKit"
            if not used_2d
            else "vancomycin_CD_ring_model Boger1999 JACS121:10004 2D-RDKit-fallback"
        )
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}  (used_2d={used_2d})")

    # Audit dump
    audit = out_dir / "atom_label_map.txt"
    rows = []
    for i, a in enumerate(mol.GetAtoms()):
        rows.append(f"idx={i:>3d}  element={a.GetSymbol()}  arom={a.GetIsAromatic()}")
    audit.write_text(
        "# RDKit atom indices for vancomycin CD-ring model (heavy atoms only)\n"
        f"# canonical_isomeric_smiles: {iso_smi}\n"
        f"# formula: {formula}; exact MW: {Descriptors.ExactMolWt(mol):.4f}\n"
        + "\n".join(rows) + "\n"
    )
    print(f"wrote {audit}")


if __name__ == "__main__":
    target_dir = (
        Path(__file__).resolve().parent.parent
        / "data" / "validation_panel" / "vancomycin_cde_ring_boger_snar"
    )
    main(target_dir)
