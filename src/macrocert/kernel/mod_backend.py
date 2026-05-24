"""MØD hyperflow backend — fast top-N enumeration path.

MØD's bundled CBC solver enumerates the top-N solutions natively via
findSolutions(maxNumSolutions=N). This is the "ranked shortlist" half
of the M2/M5 output. Infeasibility certificates and dual bounds are
NOT available through this façade — see kernel.scip_backend for those.

Inputs: the *same* HyperFlowIR consumed by scip_backend, plus the
original mod.DG (because the MØD façade addresses vertices by graph
identity, not by string ID).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import mod  # noqa: F401

from .ir import HyperFlowIR, LinearObjective, Solution, Witness
from .objective import bond_level_objective, evaluate, process_level_objective


@dataclass
class ModSolveResult:
    solutions: list[Solution]
    witnesses: list[Witness]
    ir: HyperFlowIR


def solve_top_n(
    dg: "mod.DG",
    ir: HyperFlowIR,
    *,
    top_n: int = 10,
    objective: LinearObjective | None = None,
) -> ModSolveResult:
    import mod

    obj = objective or ir.objective
    model = mod.hyperflow.Model(dg)

    smiles_to_vertex = {v.graph.smiles: v for v in dg.vertices}

    for src in ir.sources:
        if src in smiles_to_vertex:
            model.addSource(smiles_to_vertex[src].graph)
    for v in ir.vertices:
        if v.id != ir.sink and v.id not in ir.sources and v.id in smiles_to_vertex:
            model.addSink(smiles_to_vertex[v.id].graph)
    if ir.sink in smiles_to_vertex:
        sink_vertex = smiles_to_vertex[ir.sink]
        model.addSink(sink_vertex.graph)
        model.addConstraint(mod.outFlow[sink_vertex.graph] == 1)

    macro_edges = [e for e in ir.hyperedges if e.is_macrocyclization]
    if macro_edges:
        smi_to_dg_edge = _index_dg_edges(dg)
        terms: Any = None
        for e in macro_edges:
            dg_edge = smi_to_dg_edge.get(_dg_edge_key(e))
            if dg_edge is None:
                continue
            t = mod.edgeFlow[dg_edge]
            terms = t if terms is None else terms + t
        if terms is not None:
            model.addConstraint(terms == 1)

    coeff_terms: Any = None
    smi_to_dg_edge = _index_dg_edges(dg)
    for e in ir.hyperedges:
        c = obj.coeffs.get(e.id, 0.0)
        if c == 0.0:
            continue
        dg_edge = smi_to_dg_edge.get(_dg_edge_key(e))
        if dg_edge is None:
            continue
        term = c * mod.edgeFlow[dg_edge]
        coeff_terms = term if coeff_terms is None else coeff_terms + term

    if coeff_terms is not None:
        model.objectiveFunction = coeff_terms
    else:
        model.objectiveFunction = mod.edgeFlow

    model.findSolutions(maxNumSolutions=top_n, verbosity=0)

    sols: list[Solution] = []
    witnesses: list[Witness] = []
    bond = bond_level_objective(ir)
    proc = process_level_objective(ir)
    smiles_to_id = {v.graph.smiles: v.id for v in dg.vertices}
    for s in model.solutions:
        flow_dict: dict[str, int] = {}
        for dg_edge in dg.edges:
            try:
                mult = int(round(s.eval(mod.edgeFlow[dg_edge])))
            except Exception:
                mult = 0
            if mult <= 0:
                continue
            key = _dg_edge_key_raw(dg_edge, smiles_to_id)
            for e in ir.hyperedges:
                if _dg_edge_key(e) == key:
                    flow_dict[e.id] = mult
                    break
        obj_value = evaluate(ir, flow_dict, obj)
        sols.append(Solution(
            flow=flow_dict,
            objective_value=obj_value,
            bond_level_expelled_mass=evaluate(ir, flow_dict, bond),
            process_level_expelled_mass=evaluate(ir, flow_dict, proc),
            dual_bound=obj_value,  # MØD doesn't expose duals; pin to obj
        ))
        witnesses.append(Witness(
            kind="optimal", objective_value=obj_value, dual_bound=obj_value,
        ))

    return ModSolveResult(solutions=sols, witnesses=witnesses, ir=ir)


def _index_dg_edges(dg) -> dict[tuple, Any]:
    smiles_to_id = {v.graph.smiles: v.id for v in dg.vertices}
    return {_dg_edge_key_raw(e, smiles_to_id): e for e in dg.edges}


def _dg_edge_key(ir_edge) -> tuple:
    return ("ir", tuple(sorted(ir_edge.sources)), tuple(sorted(ir_edge.targets)))


def _dg_edge_key_raw(dg_edge, smiles_to_id) -> tuple:
    srcs = tuple(sorted(v.graph.smiles for v in dg_edge.sources))
    tgts = tuple(sorted(v.graph.smiles for v in dg_edge.targets))
    return ("ir", srcs, tgts)
