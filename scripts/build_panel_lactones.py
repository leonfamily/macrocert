"""Generate the macrolactonization ring-size surrogate panel.

Companion to ``build_panel_lactams.py``. Each case is an ω-hydroxy acid
that cyclizes to a (n+1)-membered macrolactone in one firing of the
``macrolactonization`` rule. The 16-membered case (Exaltolide /
cyclopentadecanolide, CAS 106-02-5) is the literature anchor —
Mukaiyama 1976 (DOI:10.1246/cl.1976.49) tested HO(CH2)nCOOH for
n=10,11,14, expressly validating this series as a macrolactonization
substrate. The other ring sizes track the existing lactam_* panel so
that AE thresholds calibrate across heteroatom and ring-size axes
simultaneously.

References:

- Inanaga & Yamaguchi 1979, BCSJ 52:1989 (DOI:10.1246/bcsj.52.1989) —
  canonical Yamaguchi macrolactonization conditions used as the
  process-level activator for these surrogates.
- Mukaiyama, Usui & Saigo 1976, Chem. Lett. 49 (DOI:10.1246/cl.1976.49)
  — earliest series of HO(CH2)nCOOH lactonizations including n=14.
- Parenty, Moreau, Niel & Campagne 2013, Chem. Rev. — modern
  macrolactonization survey.

For each entry in CASES, writes::

  data/validation_panel/<name>/runspec.yaml
                          /expected.yaml
                          /notes.md
                          /structure.mol  (openbabel-strict V2000)
  data/building_blocks/<block>.yaml  (if missing)

Run once: ``pixi run python scripts/build_panel_lactones.py``.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


CASES = [
    {
        "name": "lactone_12_from_11_hydroxyundecanoic_acid",
        "ring_size": 12,
        "block_id": "hydroxyundecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCO",
        "target_smiles": "O=C1CCCCCCCCCCO1",
        "block_name": "11-hydroxyundecanoic acid",
        "block_note": (
            "12-membered macrolactone precursor (Mukaiyama 1976 n=10 series). "
            "DOI:10.1246/cl.1976.49"
        ),
        "ref": "Mukaiyama, Usui & Saigo 1976, Chem. Lett. 49 (DOI:10.1246/cl.1976.49)",
    },
    {
        "name": "lactone_14_from_13_hydroxytridecanoic_acid",
        "ring_size": 14,
        "block_id": "hydroxytridecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCO",
        "target_smiles": "O=C1CCCCCCCCCCCCO1",
        "block_name": "13-hydroxytridecanoic acid",
        "block_note": (
            "14-membered macrolactone precursor; series-coverage cousin of the "
            "lactam_14 surrogate."
        ),
        "ref": "Parenty, Moreau, Niel & Campagne 2013, Chem. Rev. — macrolactonization survey",
    },
    {
        "name": "lactone_16_from_15_hydroxypentadecanoic_acid",
        "ring_size": 16,
        "block_id": "hydroxypentadecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCCCO",
        "target_smiles": "O=C1CCCCCCCCCCCCCCO1",
        "block_name": "15-hydroxypentadecanoic acid",
        "block_note": (
            "Exaltolide / cyclopentadecanolide precursor (CAS 106-02-5); the "
            "canonical 16-membered musk macrolactone. Mukaiyama 1976 tested "
            "this n=14 substrate explicitly. DOI:10.1246/cl.1976.49"
        ),
        "ref": "Mukaiyama, Usui & Saigo 1976, Chem. Lett. 49 (DOI:10.1246/cl.1976.49)",
    },
    {
        "name": "lactone_20_from_19_hydroxynonadecanoic_acid",
        "ring_size": 20,
        "block_id": "hydroxynonadecanoic_acid",
        "block_smiles": "OC(=O)CCCCCCCCCCCCCCCCCCO",
        "target_smiles": "O=C1CCCCCCCCCCCCCCCCCCO1",
        "block_name": "19-hydroxynonadecanoic acid",
        "block_note": (
            "20-membered macrolactone precursor — large-ring stress test, "
            "cousin of lactam_20 surrogate."
        ),
        "ref": "Parenty, Moreau, Niel & Campagne 2013, Chem. Rev. — macrolactonization survey",
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
        f"notes: |\n"
        f"  Linear omega-hydroxy acid that cyclizes to a {case['ring_size']}-membered\n"
        f"  macrolactone in one rule firing (macrolactonization).\n"
        f"refs:\n"
        f"  - \"{case['ref']}\"\n"
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
        f"  predicates:\n"
        f"    is_intramolecular: true\n"
        f"    ring_size_equals: {case['ring_size']}\n"
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
        f"  Surrogate macrolactonization case (ring size {case['ring_size']}).\n"
        f"  Closes via one firing of the macrolactonization rule.\n"
        f"  Reference: {case['ref']}.\n"
    )

    (case_dir / "expected.yaml").write_text(
        f"literature_tactic: macrolactonization\n"
        f"literature_ring_size: {case['ring_size']}\n"
        f"expected_witness: optimal\n"
        f"expected_top_rule_class: macrocyclization\n"
        f"ae_class: high\n"
        f"reference: |\n"
        f"  {case['ref']}.\n"
        f"  omega-hydroxy acid macrolactonization is well-precedented for the\n"
        f"  musk-lactone series (Exaltolide, n=14); included to calibrate tau\n"
        f"  across ring sizes alongside the lactam_* surrogates.\n"
    )

    (case_dir / "notes.md").write_text(
        f"# {case['name']}\n"
        f"\n"
        f"Surrogate panel case — {case['ring_size']}-membered macrolactone from "
        f"`{case['block_smiles']}`.\n"
        f"\n"
        f"The structure here is the *target product* (cyclized macrolactone),\n"
        f"not the literature compound; the chemistry is real (Mukaiyama 1976\n"
        f"and the Parenty 2013 review describe the omega-hydroxy acid series\n"
        f"explicitly) but the substrate is simplified for panel calibration.\n"
        f"\n"
        f"**Reference:** {case['ref']}.\n"
        f"\n"
        f"Note: at production the canonical activator is Yamaguchi (TCBC + DMAP +\n"
        f"2 Et3N, ~568 g/mol). Per-substrate alternatives (Shiina/Corey-Nicolaou/\n"
        f"Mukaiyama/EDC/T3P) live in `data/rules/macrolactonization.meta.yaml`.\n"
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
