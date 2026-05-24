"""GFN2-xTB (intermediate tier) and Psi4 DFT (refinement tier) drivers.

End-point ΔG only in v0 — barrier estimates from TS search land when
energetics/ts_search.py is wired (M5). The proposal allows this because
Layer D verdicts are advisory; barrier estimates lift the bar for
trusting a route, not for ruling one out, and a rule-tagged class can
still be screened on ΔG alone for the toy demonstration.
"""
from __future__ import annotations

from dataclasses import dataclass

# 1 Eh = 627.509 kcal/mol; 1 eV = 23.0609 kcal/mol
EV_TO_KCAL = 23.0609
HARTREE_TO_KCAL = 627.509


@dataclass(frozen=True)
class EnergyResult:
    e_kcal_per_mol: float
    method: str
    provenance: str


def smiles_to_atoms(smiles: str, *, random_seed: int = 0xC0FFEE):
    """SMILES → ASE Atoms with MMFF-optimized 3D coordinates."""
    from ase import Atoms
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES {smiles!r}")
    mol_h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol_h, randomSeed=random_seed) != 0:
        AllChem.EmbedMolecule(mol_h, randomSeed=random_seed, useRandomCoords=True)
    try:
        AllChem.MMFFOptimizeMolecule(mol_h, maxIters=500)
    except Exception:
        AllChem.UFFOptimizeMolecule(mol_h, maxIters=500)

    conf = mol_h.GetConformer()
    positions = [list(conf.GetAtomPosition(i)) for i in range(mol_h.GetNumAtoms())]
    symbols = [a.GetSymbol() for a in mol_h.GetAtoms()]
    return Atoms(symbols=symbols, positions=positions)


def xtb_single_point(smiles: str) -> EnergyResult:
    """GFN2-xTB single-point energy in kcal/mol."""
    from xtb.ase.calculator import XTB

    atoms = smiles_to_atoms(smiles)
    atoms.calc = XTB(method="GFN2-xTB")
    e_ev = atoms.get_potential_energy()
    return EnergyResult(
        e_kcal_per_mol=e_ev * EV_TO_KCAL,
        method="GFN2-xTB",
        provenance="xtb-python ASE calculator; MMFF-pre-optimized from SMILES",
    )


def psi4_single_point(smiles: str, basis: str = "STO-3G") -> EnergyResult:
    """Psi4 SCF single-point energy in kcal/mol.

    STO-3G default for cheap CI runs; production runs override to e.g.
    'b3lyp/def2-svp' via the RunSpec.energetics.extra dict in M5.
    """
    import psi4

    atoms = smiles_to_atoms(smiles)
    psi4.core.be_quiet()
    psi4.set_memory("2 GB")
    psi4_xyz = "".join(
        f"{a.symbol} {a.position[0]:.6f} {a.position[1]:.6f} {a.position[2]:.6f}\n"
        for a in atoms
    )
    psi4.geometry(psi4_xyz)
    e_eh = psi4.energy(f"scf/{basis}")
    return EnergyResult(
        e_kcal_per_mol=float(e_eh) * HARTREE_TO_KCAL,
        method=f"SCF/{basis}",
        provenance="Psi4 single-point; MMFF-pre-optimized geometry from SMILES",
    )


def reaction_dG(
    reactant_smiles: tuple[str, ...],
    product_smiles: tuple[str, ...],
    *,
    method: str = "xtb",
) -> tuple[float, str, str]:
    """Compute ΔG_rxn = ΣE(products) − ΣE(reactants) in kcal/mol.

    Returns (dG, method_label, provenance_blob).
    """
    sp = xtb_single_point if method == "xtb" else psi4_single_point

    method_label = ""
    provenance_parts = []
    e_react = 0.0
    for smi in reactant_smiles:
        r = sp(smi)
        e_react += r.e_kcal_per_mol
        method_label = r.method
        provenance_parts.append(f"R[{smi}]={r.e_kcal_per_mol:.3f}")
    e_prod = 0.0
    for smi in product_smiles:
        r = sp(smi)
        e_prod += r.e_kcal_per_mol
        provenance_parts.append(f"P[{smi}]={r.e_kcal_per_mol:.3f}")

    return e_prod - e_react, method_label, "; ".join(provenance_parts)
