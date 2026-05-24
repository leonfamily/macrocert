"""Build a MØD derivation graph from a RunSpec — Layer B orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..spec.runspec import RunSpec
    from ..spec.rules import RuleLibrary, RuleDef

import mod  # noqa: E402

from .strategies import add_blocks, apply_rules_up_to


@dataclass
class GenerationResult:
    dg: "mod.DG"
    seco_precursor: "mod.Graph"
    rules_used: tuple[str, ...]


def build_dg_for_runspec(
    spec: "RunSpec",
    *,
    library: "RuleLibrary",
    blocks_dir: str | Path,
    target_dir: str | Path,
) -> GenerationResult:
    blocks_dir = Path(blocks_dir)
    target_dir = Path(target_dir)

    from ..spec.blocks import load_blocks

    all_blocks = load_blocks(blocks_dir)
    spec_blocks = [all_blocks[b] for b in spec.blocks]
    block_graphs = [
        mod.Graph.fromSMILES(b.smiles, name=b.id) for b in spec_blocks
    ]

    rule_defs: tuple["RuleDef", ...] = ()
    for r in spec.rules:
        rule_defs = rule_defs + library.resolve_set(r)
    seen: set[str] = set()
    deduped: list["RuleDef"] = []
    for r in rule_defs:
        if r.id in seen:
            continue
        seen.add(r.id)
        deduped.append(r)
    rule_defs = tuple(deduped)

    if not rule_defs:
        raise ValueError(f"RunSpec {spec.name!r} resolved to zero rules")
    if not block_graphs:
        raise ValueError(f"RunSpec {spec.name!r} resolved to zero building blocks")

    dg = mod.DG(graphDatabase=block_graphs)
    with dg.build() as builder:
        strat = add_blocks(block_graphs) >> apply_rules_up_to(
            rule_defs, steps=spec.strategy.max_steps
        )
        builder.execute(strat)

    return GenerationResult(
        dg=dg,
        seco_precursor=block_graphs[0],
        rules_used=tuple(r.id for r in rule_defs),
    )
