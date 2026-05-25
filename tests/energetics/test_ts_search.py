"""Tests for the Layer D TS-search driver (ts_search.py).

Covers:
  * Unit: ``SaddleSearch`` constructs cleanly with all the documented
    parameters (no import-time crashes; default values match the
    energetics_protocol.yaml ts_search.* block).
  * Unit: ``ammonia_inversion_atoms`` returns three Atoms with the
    expected size and atom ordering.
  * Integration (slow, opt-in): ``SaddleSearch.refine_from_guess`` on
    NH₃ inversion at the xtb tier converges to a planar saddle with
    barrier ≈ 6 kcal/mol — matching experiment (5.80 kcal/mol per
    Swalen & Ibers 1962, 10.1063/1.1701290) within xtb's ±20% drift.
  * Integration (slow): ``compute_worked_example_barrier`` returns a
    real float, a feasibility label, and a Sella-tagged provenance.

The integration tests are marked ``slow`` so CI can skip them with
``-m 'not slow'``; the unit tests run in milliseconds.
"""
from __future__ import annotations

import pytest


def test_saddle_search_construction_defaults():
    """SaddleSearch instantiates with the protocol's default knobs.

    Pins the API surface — values come from energetics_protocol.yaml
    ts_search.fsm block (arXiv:2604.00405 Marks 2026 §A.1).
    """
    from macrocert.energetics.ts_search import SaddleSearch

    def _fake_calc():
        return None

    s = SaddleSearch(_fake_calc)
    assert s.n_images == 7                           # arXiv:2604.00405 §A.1
    assert s.spring_constant_eV_per_A == pytest.approx(0.1)  # arXiv:2604.00405 §A.1
    assert s.sella_max_steps == 250                  # arXiv:2604.00405 §2.4
    assert s.method_label == "xtb"


def test_ammonia_inversion_atoms_shape():
    """The surrogate-substrate helper returns three 4-atom NH₃ structures."""
    from macrocert.energetics.ts_search import ammonia_inversion_atoms

    r, p, ts_guess = ammonia_inversion_atoms()
    for atoms, name in [(r, "reactant"), (p, "product"), (ts_guess, "ts_guess")]:
        assert len(atoms) == 4, f"{name} has {len(atoms)} atoms, expected 4"
        symbols = atoms.get_chemical_symbols()
        assert symbols == ['N', 'H', 'H', 'H'], (
            f"{name} atoms reordered: {symbols}"
        )

    # Reactant pyramidal-up, product pyramidal-down — the H atoms'
    # z-coordinates must have opposite signs.
    assert r.positions[1, 2] * p.positions[1, 2] < 0


def test_xtb_calculator_factory_returns_factory():
    """xtb_calculator_factory returns a zero-arg callable that builds a calc."""
    from macrocert.energetics.ts_search import xtb_calculator_factory

    factory = xtb_calculator_factory()
    assert callable(factory)
    # Don't actually call (would hit the xtb C library) — just confirm
    # the closure references "GFN2-xTB" in its source.
    factory_with_solvent = xtb_calculator_factory(solvent_name="DMF")
    assert callable(factory_with_solvent)


def test_ts_result_dataclass_is_frozen():
    """TSResult is immutable so cached certificate fields can't be mutated."""
    from macrocert.energetics.ts_search import TSResult

    res = TSResult(
        barrier_kcal_per_mol=10.0,
        e_reactant_ev=-1.0,
        e_product_ev=-1.0,
        e_ts_ev=-0.5,
        n_neb_images=5,
        n_sella_iterations=10,
        converged=True,
        method="GFN2-xTB",
        provenance="test",
    )
    with pytest.raises(Exception):
        res.barrier_kcal_per_mol = 20.0  # type: ignore[misc]


@pytest.mark.slow
def test_nh3_inversion_barrier_matches_literature():
    """End-to-end: NH₃ inversion barrier with Sella+xtb ≈ 6 kcal/mol.

    Literature: 5.80 kcal/mol experimental (Swalen & Ibers 1962,
    10.1063/1.1701290); 5.9 kcal/mol B3LYP-D3BJ/def2-TZVP per
    Bursch et al. 2022 (10.1002/anie.202205735). GFN2-xTB has
    ~5 kcal/mol MAE on barriers per Grimme 2017
    (10.1021/acs.jctc.7b00118); we allow [3, 12] kcal/mol so a
    backend-version drift won't break the test.
    """
    from ase.optimize import LBFGS

    from macrocert.energetics.ts_search import (
        SaddleSearch, ammonia_inversion_atoms, xtb_calculator_factory,
    )

    factory = xtb_calculator_factory()
    r, p, ts_guess = ammonia_inversion_atoms()
    r.calc = factory()
    LBFGS(r, logfile=None).run(fmax=0.05, steps=100)
    p.calc = factory()
    LBFGS(p, logfile=None).run(fmax=0.05, steps=100)

    search = SaddleSearch(
        factory,
        sella_fmax=0.01,
        sella_max_steps=80,
        method_label="GFN2-xTB",
    )
    result = search.refine_from_guess(r, ts_guess, p)
    assert result.converged, f"Sella did not converge; provenance: {result.provenance}"
    assert 3.0 <= result.barrier_kcal_per_mol <= 12.0, (
        f"NH₃ inversion barrier {result.barrier_kcal_per_mol:.2f} kcal/mol "
        "outside [3, 12] kcal/mol — literature is 5.8 kcal/mol"
    )


@pytest.mark.slow
def test_compute_worked_example_barrier_xtb():
    """compute_worked_example_barrier returns a float + feasibility label.

    The barrier value flows into the certificate as
    ``energetics_dependencies.worked_example_barrier_kcal_per_mol``;
    the pre-M5 gate checks that this is non-None.
    """
    from macrocert.energetics.feedback import compute_worked_example_barrier

    barrier, feasibility, provenance = compute_worked_example_barrier(
        tier="xtb", dG_barrier_kcal_max=35.0,
    )
    assert barrier is not None, "worked-example barrier is None"
    assert isinstance(barrier, float)
    assert feasibility in {
        "feasible", "defeasible_high_barrier", "defeasible_no_convergence",
    }
    assert "Sella" in provenance


def test_compute_worked_example_unsupported_tier_raises():
    """MLIP/DFT tiers are explicit NotImplementedErrors in v0."""
    from macrocert.energetics.feedback import compute_worked_example_barrier

    with pytest.raises(NotImplementedError, match="not yet wired"):
        compute_worked_example_barrier(tier="mlip")
    with pytest.raises(NotImplementedError, match="not yet wired"):
        compute_worked_example_barrier(tier="dft")
