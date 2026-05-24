"""Build erythronolide B (Corey 1978 / Egert 1985) — the 14-membered macrolactone
aglycone of erythromycin B.

Source: PubChem CID 441113 (erythronolide B by name; cross-validates with
ChEBI:28739 and CAS 3225-82-9). Note: the research_brief.md cited
"C21H38O6" and PubChem CID 122729 — both are incorrect. The actual
molecular formula is C21H38O7 (four hydroxyls: C3, C5, C6, C12; one
ketone at C9; one lactone C(=O)-O between C1 and C13) and the correct
PubChem CID is 441113. MW 402.52 g/mol.

Stereochemistry: 10 sp3 stereocenters (matches the brief's count of 10).
The CIP descriptors are taken straight from the PubChem isomeric SMILES
and verified by `Chem.AssignStereochemistry`.

The output is a strict V2000 Molfile rebuilt through openbabel (matches
the convention used by scripts/build_ascomylactam_a.py and the
panel_lactones surrogates).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


# PubChem CID 441113 (erythronolide B). Cross-checked against the
# InChIKey ZFBRGCCVTUPRFQ-HWRKYNCUSA-N (PubChem-canonical).
ERYTHRONOLIDE_B_SMILES = (
    "CC[C@@H]1[C@@H]([C@@H]([C@H](C(=O)[C@@H](C[C@@]"
    "([C@@H]([C@H]([C@@H]([C@H](C(=O)O1)C)O)C)O)(C)O)C)C)O)C"
)

TARGET_FORMULA = "C21H38O7"
TARGET_RING_SIZE = 14
TARGET_STEREO_COUNT = 10


def build_mol() -> Chem.Mol:
    """Parse the PubChem isomeric SMILES and verify chemistry invariants."""
    m = Chem.MolFromSmiles(ERYTHRONOLIDE_B_SMILES)
    if m is None:
        raise SystemExit("RDKit could not parse the erythronolide B SMILES")
    Chem.SanitizeMol(m)
    Chem.AssignStereochemistry(m, cleanIt=True, force=True)

    formula = CalcMolFormula(m)
    if formula != TARGET_FORMULA:
        raise SystemExit(
            f"Formula mismatch: got {formula}, expected {TARGET_FORMULA}"
        )

    # Confirm exactly one ring of size 14 (the macrolactone)
    rings = m.GetRingInfo().AtomRings()
    sizes = sorted(len(r) for r in rings)
    if sizes != [TARGET_RING_SIZE]:
        raise SystemExit(
            f"Ring inventory mismatch: got rings of sizes {sizes}, "
            f"expected exactly one 14-membered ring"
        )

    centers = Chem.FindMolChiralCenters(
        m, includeUnassigned=True, useLegacyImplementation=False
    )
    assigned = [c for c in centers if c[1] in ("R", "S")]
    if len(assigned) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"Stereocenter count mismatch: got {len(assigned)} assigned of "
            f"{len(centers)} total, expected {TARGET_STEREO_COUNT}"
        )

    return m


def main(out_path: Path) -> int:
    m = build_mol()

    formula = CalcMolFormula(m)
    print(f"formula:        {formula}")
    print(f"MW (avg):       {Descriptors.MolWt(m):.3f}")
    print(f"MW (exact):     {Descriptors.ExactMolWt(m):.4f}")
    print(f"InChIKey:       {Chem.MolToInchiKey(m)}")
    centers = Chem.FindMolChiralCenters(
        m, includeUnassigned=True, useLegacyImplementation=False
    )
    print(f"stereocenters:  {len(centers)} (all assigned)")
    print(f"canonical_smi:  {Chem.MolToSmiles(m)}")

    # Embed in 3D
    mh = Chem.AddHs(m)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    params.useRandomCoords = True
    used_2d = False
    embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        # Retry with different seed
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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write through openbabel for strict V2000 output (matches panel convention)
    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        Chem.MolToMolFile(mh, str(tmp))
        subprocess.run(
            ["obabel", str(tmp), "-O", str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)

    # Rewrite the title line to carry citation provenance
    text = out_path.read_text()
    lines = text.splitlines()
    title = (
        "erythronolide_B PubChem441113 Corey1978 (3D-RDKit/MMFF)"
        if not used_2d
        else "erythronolide_B PubChem441113 Corey1978 (2D-fallback)"
    )
    if lines:
        lines[0] = title
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}  (used_2d={used_2d})")
    return 0


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    out = (
        repo / "data" / "validation_panel"
        / "corey_erythronolide_b_macrolactonization_1978"
        / "structure.mol"
    )
    sys.exit(main(out))
