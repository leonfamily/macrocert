"""Tests for ETKDG conformational pre-sampling in qm.py.

Closes docs/energetics_ts_search_landed.md §8 final follow-up:
conformer sampling matters for macrocycles. ``smiles_to_atoms_best_conformer``
embeds N conformers via ETKDG (Riniker-Landrum 2015) and picks the
lowest-MMFF-energy one. The fast-path ``smiles_to_atoms`` is unchanged
and still appropriate for small rigid molecules.
"""
from __future__ import annotations

import pytest


def test_best_conformer_returns_correct_atom_count():
    from macrocert.energetics.qm import smiles_to_atoms_best_conformer
    # 13-membered macrolactam: 14 heavy atoms (1 O + 1 C(=O) + 11 CH2 +
    # 1 NH) + 23 hydrogens (11×2 from CH2 + 1 from NH) = 37 atoms total.
    atoms = smiles_to_atoms_best_conformer("O=C1CCCCCCCCCCCN1", n_conformers=5)
    assert len(atoms) == 37


def test_best_conformer_symbols_match_smiles():
    from macrocert.energetics.qm import smiles_to_atoms_best_conformer
    atoms = smiles_to_atoms_best_conformer("CCO", n_conformers=3)
    symbols = atoms.get_chemical_symbols()
    # 2 C + 1 O + 6 H = 9 atoms
    assert sorted(symbols) == sorted(["C", "C", "O", "H", "H", "H", "H", "H", "H"])


def test_best_conformer_falls_back_on_tiny_molecule():
    """For very small molecules ETKDG may decline to produce N conformers
    (low torsional flexibility). The helper falls back to the
    single-conformer path rather than failing."""
    from macrocert.energetics.qm import smiles_to_atoms_best_conformer
    atoms = smiles_to_atoms_best_conformer("O", n_conformers=10)  # water
    assert len(atoms) == 3  # O + 2H


def test_best_conformer_deterministic_under_fixed_seed():
    """Same SMILES + same random_seed produces the same lowest-energy
    geometry across calls. Important for the reproducibility-hash gate."""
    from macrocert.energetics.qm import smiles_to_atoms_best_conformer
    a = smiles_to_atoms_best_conformer("CCCCO", n_conformers=5, random_seed=42)
    b = smiles_to_atoms_best_conformer("CCCCO", n_conformers=5, random_seed=42)
    # Positions equal to floating-point precision
    assert (a.positions == b.positions).all()


@pytest.mark.slow
def test_best_conformer_lower_energy_than_single_on_macrocycle():
    """The whole point: on a macrocycle, the best-of-N conformer has
    lower xtb energy than a single random ETKDG embedding.

    Threshold of 1 kcal/mol is conservative — the toy 13-macrolactam
    shows ~7 kcal/mol delta with n=10. The test fails if the new
    helper regresses to no better than the single path."""
    from macrocert.energetics.qm import smiles_to_atoms, smiles_to_atoms_best_conformer
    from xtb.ase.calculator import XTB

    smi = "O=C1CCCCCCCCCCCN1"
    a_single = smiles_to_atoms(smi)
    a_best = smiles_to_atoms_best_conformer(smi, n_conformers=10)
    a_single.calc = XTB(method="GFN2-xTB")
    a_best.calc = XTB(method="GFN2-xTB")
    e_single = a_single.get_potential_energy()
    e_best = a_best.get_potential_energy()
    # eV → kcal/mol = 23.0609
    delta_kcal = (e_single - e_best) * 23.0609
    assert delta_kcal > 1.0, (
        f"best-of-10 should be ≥ 1 kcal/mol lower than single conformer; "
        f"got delta={delta_kcal:.2f} kcal/mol"
    )
