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
    """SMILES → ASE Atoms with MMFF-optimized 3D coordinates.

    Single-conformer fast path. For macrocycles (≥ 8-membered rings)
    use :func:`smiles_to_atoms_best_conformer` instead — a single
    random embedding picks an arbitrary conformer, which on a flexible
    ring biases the downstream energy by 5–20 kcal/mol vs the local
    minimum (Cao & Wales 2014, DOI:10.1021/ct500522r).
    """
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


def smiles_to_atoms_best_conformer(
    smiles: str,
    *,
    n_conformers: int = 20,
    random_seed: int = 0xC0FFEE,
):
    """SMILES → ASE Atoms picking the lowest-MMFF-energy conformer
    out of ``n_conformers`` ETKDG embeddings.

    Closes docs/energetics_ts_search_landed.md §8 final follow-up
    (conformational sampling). For macrocycles the cheapest reasonable
    pre-sample is RDKit's ETKDG (Riniker & Landrum 2015,
    DOI:10.1021/acs.jcim.5b00654) which uses experimental torsion-angle
    preferences plus knowledge-based corrections — substantially
    cheaper than CREST/CENSO and adequate as the *input* to a Sella
    refinement on a higher tier.

    Falls back to UFF if MMFF parameterization fails (typical for
    transition metals or unusual coordination); falls back further to
    the single-conformer fast path if multi-conformer embedding fails
    entirely (typical for tiny molecules where ETKDG over-samples).
    """
    from ase import Atoms
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES {smiles!r}")
    mol_h = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    params.useRandomCoords = True
    params.numThreads = 0  # all cores
    conf_ids = AllChem.EmbedMultipleConfs(mol_h, numConfs=n_conformers, params=params)
    if len(conf_ids) == 0:
        return smiles_to_atoms(smiles, random_seed=random_seed)

    # MMFF-optimize each conformer and pick the lowest-energy one.
    energies: list[tuple[float, int]] = []
    for cid in conf_ids:
        try:
            res = AllChem.MMFFOptimizeMoleculeConfs(
                mol_h, mmffVariant="MMFF94s", maxIters=500,
            )
            # MMFFOptimizeMoleculeConfs returns [(not_converged, energy), ...]
            # indexed by conformer id. Break after one call — it processes all.
            for cid_local, (_not_converged, energy) in enumerate(res):
                energies.append((float(energy), cid_local))
            break
        except Exception:
            energies = []
            break

    if not energies:
        # Fall back to UFF per-conformer
        for cid in conf_ids:
            try:
                if AllChem.UFFOptimizeMolecule(mol_h, confId=cid, maxIters=500) == 0:
                    ff = AllChem.UFFGetMoleculeForceField(mol_h, confId=cid)
                    if ff is not None:
                        energies.append((float(ff.CalcEnergy()), cid))
            except Exception:
                continue
    if not energies:
        return smiles_to_atoms(smiles, random_seed=random_seed)

    best_energy, best_cid = min(energies, key=lambda pair: pair[0])
    conf = mol_h.GetConformer(best_cid)
    positions = [list(conf.GetAtomPosition(i)) for i in range(mol_h.GetNumAtoms())]
    symbols = [a.GetSymbol() for a in mol_h.GetAtoms()]
    return Atoms(symbols=symbols, positions=positions)


def xtb_single_point(smiles: str, *, solvent_name: str | None = None) -> EnergyResult:
    """GFN2-xTB single-point energy in kcal/mol.

    ``solvent_name`` (e.g. ``"DMF"``, ``"DCM"``) enables the GFN2-xTB
    ALPB implicit solvent and becomes part of the result's ``method``
    label so downstream cache keys (Workstream E fix) discriminate runs
    across solvents.
    """
    from xtb.ase.calculator import XTB

    atoms = smiles_to_atoms(smiles)
    if solvent_name:
        atoms.calc = XTB(method="GFN2-xTB", solvent=solvent_name)
        method_label = f"GFN2-xTB_ALPB-{solvent_name}"
    else:
        atoms.calc = XTB(method="GFN2-xTB")
        method_label = "GFN2-xTB"
    e_ev = atoms.get_potential_energy()
    return EnergyResult(
        e_kcal_per_mol=e_ev * EV_TO_KCAL,
        method=method_label,
        provenance="xtb-python ASE calculator; MMFF-pre-optimized from SMILES",
    )


def psi4_single_point(
    smiles: str, basis: str = "STO-3G", *, solvent_name: str | None = None
) -> EnergyResult:
    """Psi4 SCF single-point energy in kcal/mol.

    STO-3G default for cheap CI runs; production runs override to e.g.
    'b3lyp/def2-svp' via the RunSpec.energetics.extra dict in M5.
    ``solvent_name`` is recorded in the method label so the energetics
    cache key (Workstream E fix) tells DMF / DCM / vacuum runs apart.
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
    if solvent_name:
        psi4.set_options({"pcm": True, "pcm_scf_type": "total"})
        psi4.pcm_helper(
            f"Units = Angstrom\nMedium {{ SolverType = IEFPCM; Solvent = {solvent_name} }}\n"
            "Cavity { Type = GePol; Area = 0.3 }"
        )
        method_label = f"SCF/{basis}_PCM-{solvent_name}"
    else:
        method_label = f"SCF/{basis}"
    e_eh = psi4.energy(f"scf/{basis}")
    return EnergyResult(
        e_kcal_per_mol=float(e_eh) * HARTREE_TO_KCAL,
        method=method_label,
        provenance="Psi4 single-point; MMFF-pre-optimized geometry from SMILES",
    )


def reaction_dG(
    reactant_smiles: tuple[str, ...],
    product_smiles: tuple[str, ...],
    *,
    method: str = "xtb",
    solvent_name: str | None = None,
) -> tuple[float, str, str]:
    """Compute ΔG_rxn = ΣE(products) − ΣE(reactants) in kcal/mol.

    Returns (dG, method_label, provenance_blob). ``solvent_name`` (e.g.
    ``"DMF"``) is forwarded to the underlying single-point driver and
    encoded into ``method_label``; the cache key (Workstream E fix)
    includes the solvent name as a first-class field so DMF/DCM never
    collide silently.
    """
    sp = xtb_single_point if method == "xtb" else psi4_single_point

    method_label = ""
    provenance_parts = []
    e_react = 0.0
    for smi in reactant_smiles:
        r = sp(smi, solvent_name=solvent_name)
        e_react += r.e_kcal_per_mol
        method_label = r.method
        provenance_parts.append(f"R[{smi}]={r.e_kcal_per_mol:.3f}")
    e_prod = 0.0
    for smi in product_smiles:
        r = sp(smi, solvent_name=solvent_name)
        e_prod += r.e_kcal_per_mol
        provenance_parts.append(f"P[{smi}]={r.e_kcal_per_mol:.3f}")

    return e_prod - e_react, method_label, "; ".join(provenance_parts)
