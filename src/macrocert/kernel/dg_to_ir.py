"""Translate a MØD derivation graph + RuleLibrary into the backend-neutral IR.

Per-edge macrocyclization detection: an edge is a macrocyclization
if (a) its rule is tagged 'macrocyclization' in the rule metadata
AND (b) the edge produces a vertex whose graph contains a ring of
exactly the target size.

Per-edge expelled_mass: in M2 v0 we take the rule's bond-level
byproduct_mass_g_per_mol from its meta.yaml. This is approximate
because the *actual* byproduct depends on which connected components
of the rule's R side are reachable from the substrate atoms — the
composed-rule path (kernel.compose) gives the correct number for
each *route*, not each edge. We refine in M2 step 4 once routes are
enumerated.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..spec.rules import RuleLibrary
from .ir import Constraint, HyperEdge, HyperFlowIR, LinearObjective, Vertex, make_edge_id
from .objective import bond_level_objective

if TYPE_CHECKING:
    import mod  # noqa: F401


def build_ir(
    dg: "mod.DG",
    *,
    library: RuleLibrary,
    sources: list[str],
    sink_smiles: str,
    ring_size: int,
    max_steps: int,
) -> HyperFlowIR:
    """Walk dg.vertices / dg.edges → IR."""
    from rdkit import Chem

    vertices_list = [
        Vertex(id=v.graph.smiles, label=getattr(v.graph, "name", "") or "")
        for v in dg.vertices
    ]
    vid_set = {v.id for v in vertices_list}
    if sink_smiles not in vid_set:
        # Sink absent from DG → the rule set + strategy never produced the
        # target. Inject it so the solver sees an infeasibility (sink must
        # be produced = 1, no edges produce it) rather than crashing.
        vertices_list.append(Vertex(id=sink_smiles, label="target (unreachable in DG)"))
    for s in sources:
        if s not in vid_set and s != sink_smiles:
            raise ValueError(f"source SMILES {s!r} not found among the DG vertices")
    vertices = tuple(vertices_list)

    hyperedges: list[HyperEdge] = []
    macro_class_rule_ids = {r.id for r in library.in_class("macrocyclization")}

    for he in dg.edges:
        rule = next(iter(he.rules))
        rule_id = _find_rule_id(rule, library)
        srcs = tuple(sorted(v.graph.smiles for v in he.sources))
        tgts = tuple(sorted(v.graph.smiles for v in he.targets))

        rule_def = library.get(rule_id) if rule_id in library.rules else None
        bond_mass = rule_def.meta.byproduct_mass_g_per_mol if rule_def else 0.0
        reagent_mass = rule_def.meta.reagent_mass_g_per_mol if rule_def else 0.0
        is_macro = (
            rule_id in macro_class_rule_ids
            and _produces_ring_of_size(tgts, ring_size, Chem)
        )

        hyperedges.append(
            HyperEdge(
                id=make_edge_id(rule_id, srcs, tgts),
                rule_id=rule_id,
                sources=srcs,
                targets=tgts,
                expelled_mass_g_per_mol=bond_mass,
                reagent_mass_g_per_mol=reagent_mass,
                is_macrocyclization=is_macro,
            )
        )

    constraints: list[Constraint] = [
        Constraint(
            id=f"flow_balance:{v.id}",
            kind="flow_balance",
            description=f"flow conservation at vertex {v.id}",
            payload={"vertex_id": v.id},
        )
        for v in vertices
    ]
    constraints.append(Constraint(
        id="step_budget",
        kind="step_budget",
        description=f"sum of edge flows ≤ {max_steps}",
        payload={"max_steps": max_steps},
    ))
    constraints.append(Constraint(
        id="exactly_one_macrocyclization",
        kind="exactly_one_macrocyclization",
        description="exactly one firing of a macrocyclization-class rule that closes the target ring",
        payload={"ring_size": ring_size,
                 "edge_ids": [e.id for e in hyperedges if e.is_macrocyclization]},
    ))
    constraints.append(Constraint(
        id="sink_required",
        kind="sink_required",
        description=f"net production of {sink_smiles} = 1",
        payload={"vertex_id": sink_smiles, "amount": 1},
    ))
    for s in sources:
        constraints.append(Constraint(
            id=f"source_bound:{s}",
            kind="source_bound",
            description=f"vertex {s} is a building block (lb 0, ub unbounded)",
            payload={"vertex_id": s},
        ))

    return HyperFlowIR(
        vertices=vertices,
        hyperedges=tuple(hyperedges),
        sources=tuple(sources),
        sink=sink_smiles,
        max_steps=max_steps,
        constraints=tuple(constraints),
        objective=bond_level_objective(_TempIR(vertices, tuple(hyperedges))),
    )


def _find_rule_id(mod_rule: "mod.Rule", library: RuleLibrary) -> str:
    name = mod_rule.name
    for rid, rdef in library.rules.items():
        if rdef.gml.find(f'ruleID "{name}"') >= 0 or rdef.id == name or rdef.id in name:
            return rid
    return mod_rule.name  # fallback


def _produces_ring_of_size(target_smiles_tuple: tuple[str, ...], n: int, Chem) -> bool:
    for smi in target_smiles_tuple:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        for ring in Chem.GetSymmSSSR(mol):
            if len(ring) == n:
                return True
    return False


class _TempIR:
    """Minimal proxy so bond_level_objective() can be evaluated before
    the final IR exists. Only `.hyperedges` is consulted."""
    def __init__(self, vertices, hyperedges):
        self.vertices = vertices
        self.hyperedges = hyperedges
