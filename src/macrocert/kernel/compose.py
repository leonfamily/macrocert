"""Compose a multi-step DPO firing sequence into a single atom-mapped rule.

Wraps MØD's RCEvaluator + the rule-composition operators (`rcSuper`,
`rcParallel`) which collapse a derivation into a single coarse rule
with the atom-to-atom map preserved through the firings
(proposal §3.4, [Andersen 2018]).

The composed rule is the *proof object* embedded in the certificate.
At v0 we cover the single-firing case (composed rule = the rule that
fired), which is exact for the toy macrolactam M2 exit. Multi-step
composition lands when M3+ pipelines start enumerating routes with
multiple coupling steps before the cyclization.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mod  # noqa: F401

from ..spec.rules import RuleLibrary
from .ir import HyperFlowIR, Solution


@dataclass(frozen=True)
class ComposedRule:
    gml: str
    atom_map: dict[int, int]              # composed-rule atom ID → block-side atom ID
    expelled_mass_g_per_mol: float        # bond-level byproduct mass (from R-side CC analysis)
    retained_root_atom: int               # anchor for the verifier's CC recomputation
    rule_ids_traced: tuple[str, ...]


def compose_route(
    sol: Solution,
    ir: HyperFlowIR,
    library: RuleLibrary,
) -> ComposedRule:
    fired = []
    for eid, n in sol.flow.items():
        edge = ir.edge_by_id(eid)
        if edge.rule_id == edge.rule_id:  # skip vertices that aren't rule firings
            fired.extend([edge.rule_id] * n)

    if len(fired) == 0:
        raise ValueError("solution has no rule firings — nothing to compose")

    if len(fired) == 1:
        rid = fired[0]
        rule = library.get(rid)
        atom_map = _identity_atom_map_from_gml(rule.gml)
        from ..verifier.conservation import expelled_mass_g_per_mol
        return ComposedRule(
            gml=rule.gml,
            atom_map=atom_map,
            expelled_mass_g_per_mol=expelled_mass_g_per_mol(
                rule.gml, retained_root_atom=rule.meta.retained_root_atom,
            ),
            retained_root_atom=rule.meta.retained_root_atom,
            rule_ids_traced=(rid,),
        )

    return _compose_via_mod(fired, library)


def _identity_atom_map_from_gml(gml: str) -> dict[int, int]:
    from ..verifier.gml_reader import parse_rule
    parsed = parse_rule(gml)
    ids = sorted(
        set(parsed.left.nodes) | set(parsed.context.nodes) | set(parsed.right.nodes)
    )
    return {i: i for i in ids}


def _compose_via_mod(fired_rule_ids: list[str], library: RuleLibrary) -> ComposedRule:
    import mod

    rules = [mod.Rule.fromGMLString(library.get(rid).gml) for rid in fired_rule_ids]
    rc = mod.RCEvaluator.new(rules)
    composed_iter = rc.eval(rules[0] * mod.rcSuper * rules[1])
    if not composed_iter:
        raise RuntimeError("RCEvaluator returned no composed rule")
    composed = composed_iter[0]
    gml_text = composed.getGMLString()

    from ..verifier.conservation import expelled_mass_g_per_mol
    first_root = library.get(fired_rule_ids[0]).meta.retained_root_atom
    return ComposedRule(
        gml=gml_text,
        atom_map=_identity_atom_map_from_gml(gml_text),
        expelled_mass_g_per_mol=expelled_mass_g_per_mol(
            gml_text, retained_root_atom=first_root,
        ),
        retained_root_atom=first_root,
        rule_ids_traced=tuple(fired_rule_ids),
    )
