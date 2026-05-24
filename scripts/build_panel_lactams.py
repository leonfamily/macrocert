"""Generate the M4 macrolactam ring-size surrogate panel.

For each entry in CASES, writes
  data/validation_panel/<name>/runspec.yaml
                          /expected.yaml
                          /notes.md
                          /structure.mol (openbabel-strict V2000)
  data/building_blocks/<block>.yaml (if missing)

Run once: `pixi run python scripts/build_panel_lactams.py`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


CASES = [
    {
        "name": "lactam_12_from_11_aminoundecanoic_acid",
        "ring_size": 12,
        "block_id": "aminoundecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCN",
        "target_smiles": "O=C1CCCCCCCCCCN1",
        "block_name": "11-aminoundecanoic acid",
        "block_note": "laurolactam precursor (CAS 2432-99-7).",
    },
    {
        "name": "lactam_14_from_13_aminotridecanoic_acid",
        "ring_size": 14,
        "block_id": "aminotridecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCN",
        "target_smiles": "O=C1CCCCCCCCCCCCN1",
        "block_name": "13-aminotridecanoic acid",
        "block_note": "14-membered macrolactam precursor.",
    },
    {
        "name": "lactam_16_from_15_aminopentadecanoic_acid",
        "ring_size": 16,
        "block_id": "aminopentadecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCCCN",
        "target_smiles": "O=C1CCCCCCCCCCCCCCN1",
        "block_name": "15-aminopentadecanoic acid",
        "block_note": "16-membered macrolactam precursor.",
    },
    {
        "name": "lactam_20_from_19_aminononadecanoic_acid",
        "ring_size": 20,
        "block_id": "aminononadecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCCCCCCCN",
        "target_smiles": "O=C1CCCCCCCCCCCCCCCCCCN1",
        "block_name": "19-aminononadecanoic acid",
        "block_note": "20-membered macrolactam precursor — large ring stress test.",
    },
]


def _embed_to_mol(smiles: str, out_path: Path) -> None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse {smiles!r}")
    mh = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mh, randomSeed=0xC0FFEE, useRandomCoords=True)
    try:
        AllChem.MMFFOptimizeMolecule(mh, maxIters=500)
    except Exception:
        AllChem.UFFOptimizeMolecule(mh, maxIters=500)

    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tf:
        tmp_path = Path(tf.name)
    try:
        Chem.MolToMolFile(mh, str(tmp_path))
        subprocess.run(
            ["obabel", str(tmp_path), "-O", str(out_path)],
            check=True, capture_output=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def _write_block(case: dict, root: Path) -> None:
    path = root / "data" / "building_blocks" / f"{case['block_id']}.yaml"
    if path.exists():
        return
    path.write_text(
        f"name: {case['block_name']}\n"
        f"smiles: {case['block_smiles']}\n"
        f"provenance: |\n"
        f"  Surrogate panel building block — {case['block_note']}\n"
        f"  Commercially available; not from a CASP run.\n"
        f"notes: |\n"
        f"  Linear ω-aminoacid that cyclizes to a {case['ring_size']}-membered\n"
        f"  macrolactam in one rule firing (macrolactamization).\n"
    )


def _write_case(case: dict, root: Path) -> None:
    case_dir = root / "data" / "validation_panel" / case["name"]
    case_dir.mkdir(parents=True, exist_ok=True)

    _embed_to_mol(case["target_smiles"], case_dir / "structure.mol")

    (case_dir / "runspec.yaml").write_text(
        f"name: {case['name']}\n"
        f"target:\n"
        f"  structure_path: structure.mol\n"
        f"  ring_size: {case['ring_size']}\n"
        f"\n"
        f"blocks:\n"
        f"  - {case['block_id']}\n"
        f"\n"
        f"rules: all_macrocyclization\n"
        f"\n"
        f"strategy:\n"
        f"  max_steps: 1\n"
        f"  ring_close_only: true\n"
        f"\n"
        f"solver:\n"
        f"  backend: scip\n"
        f"  top_n: 3\n"
        f"  time_budget_s: 30\n"
        f"\n"
        f"energetics:\n"
        f"  enabled: false\n"
        f"\n"
        f"notes: |\n"
        f"  Surrogate macrolactamization case (ring size {case['ring_size']}).\n"
        f"  Closes via one firing of the macrolactamization rule.\n"
    )

    (case_dir / "expected.yaml").write_text(
        f"literature_tactic: macrolactamization\n"
        f"literature_ring_size: {case['ring_size']}\n"
        f"expected_witness: optimal\n"
        f"expected_top_rule_class: macrocyclization\n"
        f"ae_class: high\n"
        f"reference: |\n"
        f"  Surrogate ring-size case (not a literature total synthesis).\n"
        f"  ω-aminoacid macrolactamization is industrially well-precedented\n"
        f"  for the polyamide-fiber series; included here to calibrate τ\n"
        f"  across ring sizes pending the literature panel from panel_TODO.md.\n"
    )

    (case_dir / "notes.md").write_text(
        f"# {case['name']}\n"
        f"\n"
        f"Surrogate panel case — {case['ring_size']}-membered macrolactam from "
        f"`{case['block_smiles']}`.\n"
        f"\n"
        f"The structure here is the *target product* (cyclized macrolactam),\n"
        f"not the literature compound; the chemistry is real (industrial\n"
        f"caprolactam-series lactamizations) but the substrate is\n"
        f"simplified for v0 panel calibration.\n"
    )


def main(argv=None):
    repo_root = Path(__file__).resolve().parent.parent
    for case in CASES:
        print(f"writing {case['name']}...")
        _write_block(case, repo_root)
        _write_case(case, repo_root)
    print(f"\nwrote {len(CASES)} cases under {repo_root / 'data' / 'validation_panel'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
