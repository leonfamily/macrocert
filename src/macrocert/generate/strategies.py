"""Generation strategies — Layer B.

A "strategy" in MØD is a programmable plan for applying rules to graphs
under explicit control. We compose them out of the primitives
`mod.addSubset`, `mod.repeat`, `mod.rightPredicate`, etc. Ring-size
application conditions and depth bounds live here, not in the GML.
"""
from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .. spec.rules import RuleDef

import mod  # noqa: E402


def add_blocks(graphs: Iterable["mod.Graph"]):
    """Initial: drop building blocks into the working subset."""
    return mod.addSubset(*list(graphs))


def apply_rules_up_to(rules: Iterable["RuleDef"], steps: int):
    """Repeatedly apply any rule from the set, up to `steps` rounds."""
    mod_rules = [_to_mod_rule(r) for r in rules]
    if not mod_rules:
        raise ValueError("no rules supplied to apply_rules_up_to")
    return mod.repeat[steps](mod_rules)


def _to_mod_rule(rule_def: "RuleDef") -> "mod.Rule":
    return mod.Rule.fromGMLString(rule_def.gml)
