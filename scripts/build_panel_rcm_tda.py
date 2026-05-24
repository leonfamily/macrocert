"""Add RCM + TDA surrogate cases to the M4 panel."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


CASES = [
    {
        "name": "rcm_13_from_pentadecadiene",
        "ring_size": 13,
        "block_id": "pentadecadiene",
        "block_smiles": "C=CCCCCCCCCCCCC=C",       # 1,14-pentadecadiene; 15 atoms total
        "target_smiles": "C1CCCCCCCCCCCC=1",        # 13-membered cyclotridecenecycloalkene
        "block_name": "1,14-pentadecadiene",
        "block_note": "α,ω-diene for 13-ring RCM closure.",
        "tactic": "rcm",
        "ae_class": "high",                          # ethylene byproduct only
    },
    {
        "name": "rcm_15_from_heptadecadiene",
        "ring_size": 15,
        "block_id": "heptadecadiene",
        "block_smiles": "C=CCCCCCCCCCCCCCC=C",      # 1,16-heptadecadiene; 17 atoms total
        "target_smiles": "C1CCCCCCCCCCCCCC=1",       # 15-membered cyclo-pentadecene
        "block_name": "1,16-heptadecadiene",
        "block_note": "α,ω-diene for 15-ring RCM closure.",
        "tactic": "rcm",
        "ae_class": "high",
    },
    {
        "name": "tda_macrocyclic_triene_dienophile",
        "ring_size": 13,
        "block_id": "macrocyclic_dienedienophile",
        "block_smiles": "C=CC=CCCCCCCCCC=CC(=O)OC",
        "target_smiles": "C=CC1CCCCCCCCC1CC(=O)OC",
        "block_name": "macrocyclic diene-dienophile (linear precursor)",
        "block_note": "Intramolecular Diels-Alder precursor for a 13-ring carbocycle.",
        "tactic": "transannular_diels_alder",
        "ae_class": "high",                          # zero byproduct
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
        subprocess.run(["obabel", str(tmp_path), "-O", str(out_path)],
                       check=True, capture_output=True)
    finally:
        tmp_path.unlink(missing_ok=True)


def _write_block(case: dict, root: Path) -> None:
    p = root / "data" / "building_blocks" / f"{case['block_id']}.yaml"
    if p.exists():
        return
    p.write_text(
        f"name: {case['block_name']}\n"
        f"smiles: {case['block_smiles']}\n"
        f"provenance: |\n"
        f"  Surrogate panel building block — {case['block_note']}\n"
        f"notes: ''\n"
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
        f"  Surrogate {case['tactic']} case (ring size {case['ring_size']}).\n"
    )

    (case_dir / "expected.yaml").write_text(
        f"literature_tactic: {case['tactic']}\n"
        f"literature_ring_size: {case['ring_size']}\n"
        f"expected_witness: optimal\n"
        f"expected_top_rule_class: macrocyclization\n"
        f"ae_class: {case['ae_class']}\n"
        f"reference: |\n"
        f"  Surrogate panel case — generic substrate for the {case['tactic']}\n"
        f"  class. Real literature case from the Acc. Chem. Res. 2021 review\n"
        f"  pending chemistry-team encoding (see panel_TODO.md).\n"
    )

    (case_dir / "notes.md").write_text(
        f"# {case['name']}\n"
        f"\n"
        f"Surrogate panel case for the {case['tactic']} class, ring size "
        f"{case['ring_size']}.\n"
    )


def main(argv=None):
    repo_root = Path(__file__).resolve().parent.parent
    for case in CASES:
        print(f"writing {case['name']}...")
        _write_block(case, repo_root)
        _write_case(case, repo_root)
    print(f"\nwrote {len(CASES)} cases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
