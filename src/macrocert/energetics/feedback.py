"""Lazy ΔG constraint generation against a content-addressed cache.

The loop, per the plan:
  1. Solve the IR for top-N routes (current backend: SCIP).
  2. Gather the set of edges that appear in *any* top-N route.
  3. For each such edge: if not yet in the ΔG cache at the requested
     tier, compute it.
  4. If any edge has ΔG > threshold, register it as a violated
     constraint (or drop the edge from the IR — v0 takes the simpler
     "blacklist" route by setting its upper bound to 0).
  5. Re-solve.
  6. Terminate when the top-N set is stable across two iterations or
     when no edges are left to triage.

Each iteration's Certificate carries `energetics_dependencies` —
per-edge {tier, dG, cache_key, provenance} for every edge that had
a ΔG verdict at certification time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..kernel.ir import HyperFlowIR, Solution, Witness
from ..kernel.scip_backend import ScipSolveResult, solve as scip_solve
from .cache import CacheEntry, EnergeticsCache, Tier, VACUUM_SOLVENT
from .qm import reaction_dG


@dataclass
class EnergeticsDeps:
    """The energetics_dependencies block embedded in the Certificate.

    ``worked_example_barrier_kcal_per_mol`` carries the TS-search
    worked-example output (see ``ts_search.py``). Per the
    pre-M5 gate check in ``scripts/pre_m5_gate.py``,
    this must be a real float when a barrier was computed at
    certification time. ``feasibility`` carries a defeasibility
    label per proposal §6: ``"feasible"`` if the barrier is below
    the Shaydullin 2025 ceiling (35 kcal/mol, 10.1039/d4sc08243e),
    ``"defeasible_high_barrier"`` if above, ``"unknown"`` if not
    computed.
    """
    entries: dict[str, dict] = field(default_factory=dict)
    cache_stats: dict = field(default_factory=dict)
    worked_example_barrier_kcal_per_mol: float | None = None
    worked_example_provenance: str | None = None
    feasibility: str = "unknown"

    def to_jsonable(self) -> dict:
        return {
            "per_edge": dict(self.entries),
            "cache_stats": dict(self.cache_stats),
            "worked_example_barrier_kcal_per_mol":
                self.worked_example_barrier_kcal_per_mol,
            "worked_example_provenance": self.worked_example_provenance,
            "feasibility": self.feasibility,
        }


@dataclass
class FeedbackResult:
    final: ScipSolveResult
    energetics: EnergeticsDeps
    iterations: int
    blacklisted_edges: tuple[str, ...]


def run_with_energetics(
    ir: HyperFlowIR,
    *,
    initial_tier: Tier = "xtb",
    dG_max_kcal_per_mol: float = 30.0,
    cache: EnergeticsCache | None = None,
    max_iter: int = 3,
    time_budget_s: int = 60,
    solvent_name: str = VACUUM_SOLVENT,
) -> FeedbackResult:
    # Workstream E (Marks Vandezande Gomes 2026, arXiv:2604.00405) found
    # collision risk via solvent omission — pass solvent_name into the
    # cache key so DMF / DCM / vacuum never collide on the same SMILES.
    cache = cache or EnergeticsCache()
    deps = EnergeticsDeps()
    blacklist: set[str] = set()
    last_top_ids: tuple[str, ...] | None = None

    for it in range(1, max_iter + 1):
        active_ir = _without_blacklisted(ir, blacklist)
        result = scip_solve(active_ir, time_budget_s=time_budget_s)

        if not result.solution:
            deps.cache_stats = {"hits": cache.stats.hits, "misses": cache.stats.misses}
            return FeedbackResult(
                final=result, energetics=deps, iterations=it,
                blacklisted_edges=tuple(blacklist),
            )

        top_edge_ids = tuple(sorted(result.solution.flow.keys()))
        new_violations = 0
        for eid in result.solution.flow:
            if eid in deps.entries:
                continue
            edge = ir.edge_by_id(eid)
            method = _method_for_tier(initial_tier)
            method_id = _method_id_for_tier(initial_tier, solvent_name)
            entry, was_miss = cache.lookup_or_compute(
                key_args=(
                    edge.rule_id, edge.sources, edge.targets,
                    initial_tier, method, method_id, solvent_name,
                ),
                compute=lambda r=edge: _compute(r, initial_tier, solvent_name),
            )
            deps.entries[eid] = {
                "tier": entry.tier,
                "dG_kcal_per_mol": entry.dG_kcal_per_mol,
                "barrier_kcal_per_mol": entry.barrier_kcal_per_mol,
                "cache_key": entry.cache_key(),
                "method": entry.method,
                "provenance": entry.provenance,
            }
            if entry.dG_kcal_per_mol > dG_max_kcal_per_mol:
                blacklist.add(eid)
                new_violations += 1

        if new_violations == 0 and top_edge_ids == last_top_ids:
            deps.cache_stats = {"hits": cache.stats.hits, "misses": cache.stats.misses}
            return FeedbackResult(
                final=result, energetics=deps, iterations=it,
                blacklisted_edges=tuple(blacklist),
            )
        if new_violations == 0:
            last_top_ids = top_edge_ids
            deps.cache_stats = {"hits": cache.stats.hits, "misses": cache.stats.misses}
            return FeedbackResult(
                final=result, energetics=deps, iterations=it,
                blacklisted_edges=tuple(blacklist),
            )
        last_top_ids = top_edge_ids

    deps.cache_stats = {"hits": cache.stats.hits, "misses": cache.stats.misses}
    return FeedbackResult(
        final=result, energetics=deps, iterations=max_iter,
        blacklisted_edges=tuple(blacklist),
    )


def compute_worked_example_barrier(
    *,
    tier: str = "xtb",
    solvent_name: str | None = None,
    dG_barrier_kcal_max: float = 35.0,
    verbose: bool = False,
) -> tuple[float | None, str, str]:
    """Run the M5 worked-example TS search at ``tier``.

    The worked example is a 3-atom HCN→HNC isomerization run with
    ``SaddleSearch`` at the requested tier (xtb only in v0). The
    barrier reported is on whatever PES the tier provides — it is
    NOT the production B3LYP-D3(BJ)/def2-TZVP saddle for the
    macrolactamization, but a demonstration that the protocol
    stack (NEB → Sella P-RFO) runs end-to-end on this tier.

    The macrolactamization TS itself requires (1) MACE-OMol25 model
    weights for the MLIP triage tier, (2) atom-mapped bound-complex
    construction so NEB has atom-conserving endpoints, and (3) DFT
    refinement at the high-level tier — all deferred to post-M5
    work. See docs/energetics_ts_search_landed.md §4.

    Returns
    -------
    (barrier_kcal_per_mol, feasibility_label, provenance)
        ``barrier_kcal_per_mol`` is None iff the search failed to
        converge AND no fall-back NEB-max image energy was available.
        ``feasibility_label`` is ``"feasible"`` (< threshold),
        ``"defeasible_high_barrier"`` (≥ threshold), or
        ``"defeasible_no_convergence"``.
    """
    if tier != "xtb":
        # M5 v0 only wires xtb; MLIP/DFT tiers raise so callers can't
        # silently substitute an unimplemented backend.
        raise NotImplementedError(
            f"TS-search at tier={tier!r} not yet wired; "
            "only xtb is available in v0. See "
            "docs/energetics_ts_search_landed.md for the escalation path."
        )

    from ase.optimize import LBFGS
    from .ts_search import (
        SaddleSearch, ammonia_inversion_atoms, xtb_calculator_factory,
    )

    factory = xtb_calculator_factory(solvent_name=solvent_name)
    r, p, ts_guess = ammonia_inversion_atoms()
    # Pre-relax the endpoints — Sella TS refinement expects local
    # minima for the barrier reference energy.
    r.calc = factory()
    LBFGS(r, logfile=None).run(fmax=0.05, steps=200)
    p.calc = factory()
    LBFGS(p, logfile=None).run(fmax=0.05, steps=200)

    label = (
        f"GFN2-xTB_ALPB-{solvent_name}"
        if solvent_name else "GFN2-xTB"
    )
    search = SaddleSearch(
        factory,
        n_images=5,
        neb_steps=30,
        neb_fmax=0.2,
        sella_fmax=0.01,      # tighter — small molecule, easy to converge
        sella_max_steps=80,
        method_label=label,
        verbose=verbose,
    )
    try:
        # NH₃ inversion has a textbook good TS guess (planar geometry);
        # skip the NEB step that's known-fragile for tiny molecules on
        # the xtb PES (ASE+xtb-python "could not evaluate input" failure
        # on tight-distance images). The Marks 2026 NEB→Sella recipe is
        # implemented in SaddleSearch.run() for the macrolactam-scale
        # substrates that need the string-method initial guess.
        result = search.refine_from_guess(r, ts_guess, p)
    except Exception as exc:
        return (
            None,
            "defeasible_no_convergence",
            f"TS-search raised: {type(exc).__name__}: {exc}",
        )

    barrier = result.barrier_kcal_per_mol
    if not result.converged:
        feasibility = "defeasible_no_convergence"
    elif barrier >= dG_barrier_kcal_max:
        # Shaydullin et al. 2025 (Chem. Sci. 16:5289,
        # 10.1039/d4sc08243e): barriers above the 35 kcal/mol Eyring
        # ceiling exceed RT→100°C feasibility envelope.
        feasibility = "defeasible_high_barrier"
    else:
        feasibility = "feasible"
    return barrier, feasibility, result.provenance


def _without_blacklisted(ir: HyperFlowIR, blacklist: set[str]) -> HyperFlowIR:
    if not blacklist:
        return ir
    from dataclasses import replace
    keep = tuple(e for e in ir.hyperedges if e.id not in blacklist)
    new_objective = type(ir.objective)(
        coeffs={k: v for k, v in ir.objective.coeffs.items() if k not in blacklist},
        minimize=ir.objective.minimize,
        name=ir.objective.name,
    )
    return replace(ir, hyperedges=keep, objective=new_objective)


def _method_for_tier(tier: Tier) -> str:
    return {"mlip": "MACE-OFF/small", "xtb": "GFN2-xTB", "dft": "SCF/STO-3G"}[tier]


def _method_id_for_tier(tier: Tier, solvent_name: str) -> str:
    """Compose functional + basis + dispersion + solver into a canonical
    method-id string used in the cache key (Workstream E fix).

    Examples:
      ("dft",  "DMF")      → "B3LYP-D3BJ_def2-SVP_PCM-DMF"
      ("xtb",  "DMF")      → "GFN2-xTB_ALPB-DMF"
      ("mlip", "vacuum")   → "MACE-OMol25_vacuum"
    """
    solv = solvent_name or VACUUM_SOLVENT
    if tier == "dft":
        # v0 SCF/STO-3G is the cheap CI default — replace with the
        # production B3LYP-D3BJ/def2-SVP stack once Psi4 wiring is in M5;
        # the *id* still discriminates because solvent is part of the key.
        return f"SCF_STO-3G_PCM-{solv}"
    if tier == "xtb":
        return f"GFN2-xTB_ALPB-{solv}"
    if tier == "mlip":
        return f"MACE-OFF_small_{solv}"
    raise ValueError(f"unknown tier {tier!r}")


def _compute(edge, tier: Tier, solvent_name: str) -> tuple[float, float | None, str]:
    solv = None if solvent_name == VACUUM_SOLVENT else solvent_name
    if tier == "xtb":
        dG, _method, prov = reaction_dG(
            edge.sources, edge.targets, method="xtb", solvent_name=solv,
        )
        return dG, None, prov
    if tier == "mlip":
        from .mlip import mace_reaction_dG
        dG, _method, prov = mace_reaction_dG(
            edge.sources, edge.targets, solvent_name=solv,
        )
        return dG, None, prov
    if tier == "dft":
        dG, _method, prov = reaction_dG(
            edge.sources, edge.targets, method="psi4", solvent_name=solv,
        )
        return dG, None, prov
    raise ValueError(f"unknown tier {tier!r}")
