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
from .cache import CacheEntry, EnergeticsCache, Tier
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
) -> FeedbackResult:
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
            entry, was_miss = cache.lookup_or_compute(
                key_args=(edge.rule_id, edge.sources, edge.targets, initial_tier, _method_for_tier(initial_tier)),
                compute=lambda r=edge: _compute(r, initial_tier),
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


def _compute(edge, tier: Tier) -> tuple[float, float | None, str]:
    if tier == "xtb":
        dG, _method, prov = reaction_dG(
            edge.sources, edge.targets, method="xtb",
        )
        return dG, None, prov
    if tier == "mlip":
        from .mlip import mace_reaction_dG
        dG, _method, prov = mace_reaction_dG(edge.sources, edge.targets)
        return dG, None, prov
    if tier == "dft":
        dG, _method, prov = reaction_dG(
            edge.sources, edge.targets, method="psi4",
        )
        return dG, None, prov
    raise ValueError(f"unknown tier {tier!r}")
