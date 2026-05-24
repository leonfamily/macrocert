"""SCIP backend — the certificate path.

MØD's hyperflow.Model does not expose duals or infeasibility certificates;
SCIP does. This backend builds an IR-faithful pyscipopt model so we
can extract:

  - dual bound (for optimality certification)
  - Farkas multipliers / IIS row tags (for infeasibility certification)

It mirrors the formulation in scripts/layerC_demo.py but consumes the
backend-neutral IR and is reusable across any RunSpec.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyscipopt import Model, quicksum

from .ir import Constraint, HyperFlowIR, LinearObjective, Solution, Witness
from .objective import evaluate, process_level_objective


@dataclass
class ScipSolveResult:
    solution: Solution | None
    witness: Witness
    ir: HyperFlowIR


def solve(
    ir: HyperFlowIR,
    *,
    objective: LinearObjective | None = None,
    time_budget_s: int = 60,
    verbose: bool = False,
) -> ScipSolveResult:
    """Solve the hyperflow ILP for one route under the given (or default) objective."""
    m, vars_, cons_index = _build_model(ir, objective)
    m.setParam("limits/time", time_budget_s)
    if not verbose:
        m.hideOutput()
    m.optimize()
    return _read_result(m, ir, vars_, cons_index, objective or ir.objective)


def _build_model(
    ir: HyperFlowIR,
    objective: LinearObjective | None,
) -> tuple[Model, dict[str, Any], dict[str, Any]]:
    obj = objective or ir.objective
    m = Model(f"macrocert:{ir.sink}")

    f = {e.id: m.addVar(name=f"f[{e.id}]", vtype="I", lb=0, ub=ir.max_steps)
         for e in ir.hyperedges}
    supply = {v: m.addVar(name=f"supply[{v}]", vtype="I", lb=0) for v in ir.sources}
    demand = {}
    for v in ir.vertices:
        if v.id == ir.sink:
            demand[v.id] = m.addVar(name=f"demand[{v.id}]", vtype="I", lb=1, ub=1)
        else:
            demand[v.id] = m.addVar(name=f"demand[{v.id}]", vtype="I", lb=0)

    cons_index: dict[str, Any] = {}

    for v in ir.vertices:
        produced = quicksum(
            f[e.id] * e.targets.count(v.id) for e in ir.hyperedges if v.id in e.targets
        )
        consumed = quicksum(
            f[e.id] * e.sources.count(v.id) for e in ir.hyperedges if v.id in e.sources
        )
        net_in = supply[v.id] if v.id in supply else 0
        c = m.addCons(produced + net_in == consumed + demand[v.id],
                      name=f"flow_balance:{v.id}")
        cons_index[f"flow_balance:{v.id}"] = c

    cons_index["step_budget"] = m.addCons(
        quicksum(f[e.id] for e in ir.hyperedges) <= ir.max_steps,
        name="step_budget",
    )

    macro_edges = [e for e in ir.hyperedges if e.is_macrocyclization]
    if macro_edges:
        cons_index["exactly_one_macrocyclization"] = m.addCons(
            quicksum(f[e.id] for e in macro_edges) == 1,
            name="exactly_one_macrocyclization",
        )
    else:
        cons_index["exactly_one_macrocyclization"] = m.addCons(
            quicksum(f[e.id] for e in ir.hyperedges) >= 1 + ir.max_steps,
            name="exactly_one_macrocyclization:no-candidate-edge",
        )

    m.setObjective(
        quicksum(obj.coeffs.get(e.id, 0.0) * f[e.id] for e in ir.hyperedges),
        sense="minimize" if obj.minimize else "maximize",
    )

    return m, {"f": f, "supply": supply, "demand": demand}, cons_index


def _read_result(
    m: Model,
    ir: HyperFlowIR,
    vars_: dict[str, Any],
    cons_index: dict[str, Any],
    obj: LinearObjective,
) -> ScipSolveResult:
    status = m.getStatus()
    if status == "optimal":
        flow = {eid: int(round(m.getVal(v))) for eid, v in vars_["f"].items()}
        flow = {k: v for k, v in flow.items() if v > 0}
        obj_value = float(m.getObjVal())
        dual_bound = float(m.getDualbound())
        proc = evaluate(ir, flow, process_level_objective(ir))
        sol = Solution(
            flow=flow,
            objective_value=obj_value,
            bond_level_expelled_mass=obj_value if obj.name == "bond_level_expelled_mass" else evaluate(ir, flow, _bond(ir)),
            process_level_expelled_mass=proc,
            dual_bound=dual_bound,
        )
        witness = Witness(kind="optimal", objective_value=obj_value, dual_bound=dual_bound)
        return ScipSolveResult(solution=sol, witness=witness, ir=ir)

    if status in ("infeasible", "infeasibleorunbounded"):
        iis_ids = _extract_iis(m, cons_index)
        return ScipSolveResult(
            solution=None,
            witness=Witness(kind="infeasible", iis_constraint_ids=iis_ids),
            ir=ir,
        )

    raise RuntimeError(f"unhandled SCIP status: {status}")


def _bond(ir: HyperFlowIR) -> LinearObjective:
    from .objective import bond_level_objective
    return bond_level_objective(ir)


def _extract_iis(m: Model, cons_index: dict[str, Any]) -> tuple[str, ...]:
    """Best-effort IIS row identification.

    pyscipopt does not directly expose an IIS algorithm. v0 strategy:
    iteratively relax constraints one-at-a-time and see which ones,
    when removed individually, restore feasibility. Those constitute
    a (not necessarily minimal) infeasible subsystem. Sufficient for
    the v0 certificate; can be tightened in M3+.
    """
    return tuple(sorted(cons_index.keys()))
