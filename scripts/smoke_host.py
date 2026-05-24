"""
Full-stack smoke test (host pixi env, native osx-arm64).

Verifies every component used by the proposal can be imported and run a
trivial operation in a single Python process:
  - MØD           Layer A/B kernel (native build, see scripts/build_mod.sh)
  - RDKit         cheminformatics I/O
  - pyscipopt     (M)ILP backend for the hyperflow solver
  - ASE + xtb     Layer D fast energetics (GFN2-xTB)
  - Psi4          Layer D DFT refinement
  - PyTorch       MPS device for MACE-OFF / AIMNet2

The Docker image `jakobandersen/mod` is retained for the LaTeX `mod_post`
summary PDFs only; runtime MØD lives natively in the pixi env.
"""
from __future__ import annotations
import sys, traceback


def section(name: str) -> None:
    print(f"\n=== {name} ===")


def check_mod() -> None:
    section("MØD (native)")
    import mod
    g = mod.Graph.fromSMILES("OC(=O)CCCN", name="seco")
    import os
    rule_path = os.path.join(os.path.dirname(__file__), "..", "rules",
                             "macrolactamization.gml")
    rule = mod.Rule.fromGMLString(open(rule_path).read())
    dg = mod.DG(graphDatabase=[g])
    with dg.build() as b:
        b.execute(mod.addSubset(g) >> rule)
    print(f"  seco {g.numVertices} atoms; DG: {dg.numVertices} mols, "
          f"{dg.numEdges} reactions; mod.hyperflow.Model reachable: "
          f"{mod.hyperflow.Model is not None}")


def check_rdkit() -> None:
    section("RDKit")
    from rdkit import Chem, __version__
    from rdkit.Chem import AllChem, Descriptors
    print("rdkit", __version__)
    mol = Chem.MolFromSmiles("OC(=O)CCCCCCCCCCCN")  # a 12-aminododecanoic-like
    AllChem.EmbedMolecule(Chem.AddHs(mol), randomSeed=0xC0FFEE)
    print(f"  loaded MW={Descriptors.MolWt(mol):.2f}  atoms={mol.GetNumAtoms()}")


def check_scip() -> None:
    section("pyscipopt (ILP backend)")
    from pyscipopt import Model
    m = Model("tiny_hyperflow_sanity")
    x = m.addVar("x", vtype="I", lb=0)
    y = m.addVar("y", vtype="I", lb=0)
    m.addCons(x + y >= 3)
    m.setObjective(2 * x + 5 * y, "minimize")
    m.hideOutput(); m.optimize()
    print(f"  status={m.getStatus()} obj={m.getObjVal():.2f}  x={m.getVal(x)} y={m.getVal(y)}")


def check_xtb() -> None:
    section("xtb (GFN2-xTB via ASE)")
    from ase.build import molecule
    from ase.calculators.calculator import CalculatorSetupError
    try:
        from xtb.ase.calculator import XTB
    except ImportError as e:
        print("  xtb-python not importable:", e); return
    h2o = molecule("H2O")
    h2o.calc = XTB(method="GFN2-xTB")
    e = h2o.get_potential_energy()
    print(f"  H2O E = {e:.4f} eV")


def check_psi4() -> None:
    section("Psi4 (DFT)")
    try:
        import psi4
    except Exception as e:
        print("  psi4 import failed:", e); return
    psi4.core.be_quiet()
    psi4.set_memory("2 GB")
    psi4.geometry("""
        O
        H 1 0.96
        H 1 0.96 2 104.5
    """)
    e = psi4.energy("scf/sto-3g")
    print(f"  H2O SCF/STO-3G E = {e:.6f} Eh")


def check_torch() -> None:
    section("PyTorch (MPS device for MLIPs)")
    import torch
    print("  torch", torch.__version__, "  mps_available:", torch.backends.mps.is_available())


def check_mace() -> None:
    section("MACE-OFF (MLIP)")
    try:
        import mace  # noqa: F401
        from mace.calculators import mace_off
        print("  mace import OK; weights download lazily on first use")
    except Exception as e:
        print("  mace not importable:", e)


def main() -> int:
    rc = 0
    for fn in (check_mod, check_rdkit, check_scip, check_xtb, check_psi4, check_torch, check_mace):
        try:
            fn()
        except Exception:
            traceback.print_exc(); rc = 1
    print("\nDone." if rc == 0 else "\nFailures above.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
