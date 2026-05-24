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
    """The energetics_dependencies block embedded in the Certificate."""
    entries: dict[str, dict] = field(default_factory=dict)
    cache_stats: dict = field(default_factory=dict)

    def to_jsonable(self) -> dict:
        return {
            "per_edge": dict(self.entries),
            "cache_stats": dict(self.cache_stats),
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
