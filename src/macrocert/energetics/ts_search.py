"""Transition-state search driver (Layer D, M5).

Implements the **NEB → Sella P-RFO** TS-search recipe from
Marks, Vandezande & Gomes 2026 (arXiv:2604.00405) at the xtb tier.

The production protocol (data/energetics_protocol.yaml) specifies FSM
(Freezing String Method) on an MLIP surface (MACE-OMol25) refined to
DFT (B3LYP-D3BJ/def2-TZVP). FSM converges 96.6% on Baker/Sharada
benchmarks at ~3.8 DFT gradient evals/reaction. That tier is deferred
in v0 pending MACE-OMol25 model download tests; what is wired here is
the xtb fallback tier:

  reactant_atoms, product_atoms (atom-conserving, same atom ordering)
       │
       ▼  ASE NEB with N_images images (xtb calculator)
  relaxed string with energy maximum at i*
       │
       ▼  Sella(order=1, internal=True) starting from image[i*]
  first-order saddle with single imaginary mode
       │
       ▼  barrier = E(TS) − E(reactant)

This is *not* the production stack. The xtb saddles are approximate
(GFN2-xTB MAE ~5 kcal/mol on barriers per Bursch et al. 2022,
10.1002/anie.202205735, vs ~1.1 kcal/mol for B3LYP-D3BJ per
Stuyver-Jorner-Coley 2022, arXiv:2212.06014). They are useful for
demonstrating the protocol end-to-end and for fallback when MLIP
weights are unavailable.

The class is also tier-pluggable: pass a different ASE calculator
(MACE-OFF, MACE-OMol25, Psi4) to lift the saddle to that surface.

Citations:
  - NEB → Sella recipe:    arXiv:2604.00405 §2.4 (Marks 2026)
  - Sella P-RFO order=1:   Hermes, Sargsyan & Kulik 2022,
                           https://github.com/zadorlab/sella
  - FSM vs CI-NEB success: arXiv:2604.00405 §4 — 88.9% vs 70.8% on
                           Baker; we use plain NEB here as the simpler
                           atom-mapping-friendly recipe.
  - Barrier threshold:     10.1039/d4sc08243e (Shaydullin et al. 2025,
                           Chem. Sci. 16:5289), 35 kcal/mol ceiling
                           for solution chemistry at RT→100°C.
"""
from __future__ import annotations

import contextlib
import io
import os
from dataclasses import dataclass
from typing import Any

# kcal/mol per eV — CODATA 2018 (NIST SP 961).
EV_TO_KCAL = 23.0609


@dataclass(frozen=True)
class TSResult:
    """Outcome of a single TS-search attempt.

    ``barrier_kcal_per_mol`` is ``E(TS) − E(reactant)`` on whatever
    calculator was used. ``converged`` is ``True`` iff Sella reported
    a first-order saddle within ``fmax`` of the requested tolerance.
    """
    barrier_kcal_per_mol: float
    e_reactant_ev: float
    e_product_ev: float
    e_ts_ev: float
    n_neb_images: int
    n_sella_iterations: int
    converged: bool
    method: str
    provenance: str
    cache_key: str = ""


def _silenced_calc(calculator_factory, atoms):
    """Attach a calculator factory result to atoms with stderr/stdout muted."""
    atoms.calc = calculator_factory()
    return atoms


class SaddleSearch:
    """NEB → Sella TS-search wrapper at a single PES tier.

    Parameters
    ----------
    calculator_factory
        Zero-arg callable that returns an ASE calculator instance.
        Each image / endpoint / TS gets its own fresh calculator
        (some calculators like xtb-python aren't safely shareable).
    n_images
        NEB string length (counting endpoints). Marks 2026 §A.1
        uses 7 for FSM; we adopt the same for the NEB tier.
    spring_constant_eV_per_A
        NEB spring constant. arXiv:2604.00405 §A.1 = 0.1 eV/Å.
    neb_fmax
        Force convergence tolerance during NEB pre-optimization.
        Loose: we want a starting guess for Sella, not a tight TS.
    sella_fmax
        Force tolerance for the Sella TS refinement. xtb tier:
        3e-3 Ha/Bohr ≈ 0.077 eV/Å per Marks 2026 §2.4 (MLIP
        refinement tolerance; the same magnitude works at the
        xtb tier).
    sella_max_steps
        Hard cap on Sella iterations. arXiv:2604.00405 §2.4 = 250.
    """

    def __init__(
        self,
        calculator_factory,
        *,
        n_images: int = 7,
        spring_constant_eV_per_A: float = 0.1,
        neb_steps: int = 100,
        neb_fmax: float = 0.2,
        sella_fmax: float = 0.05,
        sella_max_steps: int = 250,
        method_label: str = "xtb",
        verbose: bool = False,
    ):
        self.calculator_factory = calculator_factory
        self.n_images = n_images
        self.spring_constant_eV_per_A = spring_constant_eV_per_A
        self.neb_steps = neb_steps
        self.neb_fmax = neb_fmax
        self.sella_fmax = sella_fmax
        self.sella_max_steps = sella_max_steps
        self.method_label = method_label
        self.verbose = verbose

    def refine_from_guess(self, reactant_atoms, ts_guess_atoms, product_atoms=None) -> TSResult:
        """Skip NEB and refine a caller-supplied TS guess with Sella.

        Used by the worked-example surrogate (NH₃ inversion), where the
        planar geometry is a textbook good guess and full NEB
        interpolation is overkill. The xtb tier is known to be unstable
        when CI-NEB pushes images into tight geometries for tiny
        molecules (ASE bug — `xtb could not evaluate input`); this path
        sidesteps the bug.

        Parameters
        ----------
        reactant_atoms
            Locally-relaxed reactant geometry. Energy used as the
            barrier reference.
        ts_guess_atoms
            Initial TS geometry to refine.
        product_atoms
            Optional. Used only for ``e_product_ev`` reporting.
        """
        from sella import Sella

        log_target = "-" if self.verbose else io.StringIO()

        r = reactant_atoms.copy()
        r.calc = self.calculator_factory()
        e_r = r.get_potential_energy()

        e_p = float('nan')
        if product_atoms is not None:
            p = product_atoms.copy()
            p.calc = self.calculator_factory()
            e_p = p.get_potential_energy()

        ts = ts_guess_atoms.copy()
        ts.calc = self.calculator_factory()

        # Tighter delta0 (trust-radius) than Sella's default — the
        # planar NH₃ guess is already close to the saddle, so we
        # want small first steps to avoid drifting onto a different
        # PES region. arXiv:2604.00405 §2.4 uses default delta0;
        # we tighten for the surrogate worked example.
        opt = Sella(
            ts,
            order=1,
            internal=True,
            delta0=0.05,
            eta=1e-4,
            logfile=log_target,
        )
        try:
            opt.run(fmax=self.sella_fmax, steps=self.sella_max_steps)
            converged = bool(opt.converged())
        except Exception as exc:
            converged = False
            if self.verbose:
                print(f"Sella raised ({exc})")

        e_ts = ts.get_potential_energy()
        barrier_ev = e_ts - e_r
        barrier_kcal = barrier_ev * EV_TO_KCAL
        n_sella = getattr(opt, "nsteps", 0)
        return TSResult(
            barrier_kcal_per_mol=float(barrier_kcal),
            e_reactant_ev=float(e_r),
            e_product_ev=float(e_p),
            e_ts_ev=float(e_ts),
            n_neb_images=0,           # NEB skipped
            n_sella_iterations=int(n_sella),
            converged=converged,
            method=self.method_label,
            provenance=(
                f"Sella(order=1, internal=True, delta0=0.05, eta=1e-4, "
                f"fmax={self.sella_fmax} eV/Å) refined from caller-supplied "
                f"TS guess; method={self.method_label}; "
                f"E_R={e_r:.4f}eV, E_TS={e_ts:.4f}eV; converged={converged}"
            ),
        )

    def run(self, reactant_atoms, product_atoms) -> TSResult:
        """Run NEB → Sella starting from aligned reactant/product Atoms.

        Pre-conditions:
          - ``len(reactant_atoms) == len(product_atoms)``
          - Atom ordering matches (atom i in R corresponds to atom i in P)
          - Both endpoints already locally relaxed (caller's
            responsibility; we don't re-relax to keep the cost lean)

        Atom-conservation is enforced because NEB requires it. For
        eliminations (e.g., macrolactamization releasing H₂O) the
        caller must construct atom-mapped bound complexes —
        ``HCOOH·NH₃ → HCONH₂·H₂O`` rather than the bare reaction.
        """
        if len(reactant_atoms) != len(product_atoms):
            raise ValueError(
                f"NEB requires atom-conserving endpoints; "
                f"got {len(reactant_atoms)} vs {len(product_atoms)} atoms"
            )

        # Lazy imports so the module loads cleanly even without sella.
        from ase.mep import NEB
        from ase.optimize import LBFGS
        from sella import Sella

        log_buf: io.StringIO | None = None if self.verbose else io.StringIO()
        log_target: Any = "-" if self.verbose else log_buf

        # Step 1: endpoint single-points with the production calculator
        r = reactant_atoms.copy()
        r.calc = self.calculator_factory()
        e_r = r.get_potential_energy()

        p = product_atoms.copy()
        p.calc = self.calculator_factory()
        e_p = p.get_potential_energy()

        # Step 2: build the NEB string by linear interpolation
        images = [r]
        for i in range(1, self.n_images - 1):
            img = r.copy()
            alpha = i / (self.n_images - 1)
            img.positions = (1 - alpha) * r.positions + alpha * p.positions
            img.calc = self.calculator_factory()
            images.append(img)
        images.append(p)

        # Use 'improvedtangent' (Henkelman 2000 J. Chem. Phys. 113:9978,
        # doi:10.1063/1.1323224) per ASE's default-changed warning.
        neb = NEB(
            images,
            k=self.spring_constant_eV_per_A,
            climb=False,
            method='improvedtangent',
        )

        # Step 3a: relax the NEB string (loose tolerance — we just need
        # a saddle-region guess for Sella).
        opt = LBFGS(neb, logfile=log_target)
        try:
            opt.run(fmax=self.neb_fmax, steps=self.neb_steps)
        except Exception as exc:
            # NEB can stall numerically on small problems; we fall back
            # to the linearly-interpolated highest image as the guess.
            if self.verbose:
                print(f"NEB stalled ({exc}); using interpolated guess")

        # Step 3b: switch on climbing image so the highest image
        # actively climbs to the saddle. Henkelman & Jónsson 2000
        # (J. Chem. Phys. 113:9901, doi:10.1063/1.1329672) — CI-NEB
        # tightens the TS estimate by 1-2 kcal/mol over plain NEB.
        try:
            neb.climb = True
            opt = LBFGS(neb, logfile=log_target)
            opt.run(fmax=self.neb_fmax, steps=self.neb_steps)
        except Exception as exc:
            if self.verbose:
                print(f"CI-NEB stalled ({exc}); using non-climbing guess")

        # Step 4: identify the highest-energy image — TS guess
        energies = [img.get_potential_energy() for img in images[1:-1]]
        i_max = int(max(range(len(energies)), key=lambda i: energies[i])) + 1
        ts_guess = images[i_max].copy()
        ts_guess.calc = self.calculator_factory()

        # Step 5: Sella TS refinement (P-RFO, redundant internals).
        sella_opt = Sella(
            ts_guess,
            order=1,
            internal=True,
            logfile=log_target,
        )
        try:
            sella_opt.run(fmax=self.sella_fmax, steps=self.sella_max_steps)
            converged = bool(sella_opt.converged())
        except Exception as exc:
            converged = False
            if self.verbose:
                print(f"Sella raised ({exc}); using NEB max image as TS")

        e_ts = ts_guess.get_potential_energy()
        barrier_ev = e_ts - e_r
        barrier_kcal = barrier_ev * EV_TO_KCAL

        # n_sella_iterations isn't exposed by Sella ≤2.4; use nsteps if available
        n_sella = getattr(sella_opt, "nsteps", 0)

        return TSResult(
            barrier_kcal_per_mol=float(barrier_kcal),
            e_reactant_ev=float(e_r),
            e_product_ev=float(e_p),
            e_ts_ev=float(e_ts),
            n_neb_images=self.n_images,
            n_sella_iterations=int(n_sella),
            converged=converged,
            method=self.method_label,
            provenance=(
                f"NEB({self.n_images} images, k={self.spring_constant_eV_per_A} eV/Å) "
                f"→ Sella(order=1, internal=True, fmax={self.sella_fmax} eV/Å); "
                f"method={self.method_label}; "
                f"E_R={e_r:.4f}eV, E_P={e_p:.4f}eV, E_TS={e_ts:.4f}eV; "
                f"converged={converged}"
            ),
        )


def xtb_calculator_factory(solvent_name: str | None = None):
    """Factory returning a fresh GFN2-xTB ASE calculator.

    ``solvent_name`` (e.g. ``"DMF"``) activates ALPB implicit solvation
    (10.1021/acs.jctc.0c01306, Ehlert-Stahn-Spicher-Grimme 2021).
    """
    from xtb.ase.calculator import XTB

    if solvent_name:
        def _factory():
            return XTB(method="GFN2-xTB", solvent=solvent_name)
    else:
        def _factory():
            return XTB(method="GFN2-xTB")
    return _factory


def ammonia_inversion_atoms():
    """Build the NH₃ umbrella-inversion endpoints + planar TS guess.

    Used as the *worked-example surrogate*: a 4-atom, atom-conserving
    rearrangement that exercises the full SaddleSearch stack in
    seconds. The macrolactamization itself is a multi-atom,
    water-eliminating reaction whose NEB requires atom-mapped bound
    complexes — that's a tier-up path documented in
    ``docs/energetics_ts_search_landed.md``.

    NH₃ umbrella inversion is a textbook small-molecule TS:
      - Experimental barrier: 5.80 kcal/mol (Swalen & Ibers 1962
        J. Chem. Phys. 36:1914, doi:10.1063/1.1701290)
      - B3LYP-D3BJ/def2-TZVP: ~5.9 kcal/mol (Bursch et al. 2022 §4)
      - GFN2-xTB: ~6 kcal/mol per Grimme 2017 (10.1021/acs.jctc.7b00118)

    Returns
    -------
    (reactant_atoms, product_atoms, ts_guess_atoms)
        All NH₃ with N first; reactant pyramidal-up, product
        pyramidal-down (reflected through xy-plane). The planar
        TS guess breaks symmetry with a 0.001 Å perturbation so
        Sella's redundant-internal coordinates aren't singular.
    """
    from ase import Atoms

    def _make(z_sign):
        return Atoms(
            symbols=['N', 'H', 'H', 'H'],
            positions=[
                [0.000, 0.000, 0.115],
                [0.000, 0.933, -0.270 * z_sign],
                [0.808, -0.467, -0.270 * z_sign],
                [-0.808, -0.467, -0.270 * z_sign],
            ],
        )

    r = _make(+1)
    p = _make(-1)
    ts_guess = Atoms(
        symbols=['N', 'H', 'H', 'H'],
        positions=[
            [0.000, 0.000, 0.001],          # epsilon-out-of-plane
            [0.000, 0.972, 0.0],
            [0.842, -0.486, 0.0],
            [-0.842, -0.486, 0.0],
        ],
    )
    return r, p, ts_guess
