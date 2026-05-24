"""End-to-end pipeline: RunSpec → Layer A → B → C → Certificate.

Layer D (energetics) and Layer E (reports) hook in at M3+ via the
energetics_dependencies cache and the report.render module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .generate import build_dg_for_runspec
from .kernel import certify, compose, dg_to_ir, scip_backend
from .spec.rules import load_rule_library
from .spec.runspec import RunSpec, load_runspec
from .spec.target import encode_target


@dataclass
class RunReport:
    spec: RunSpec
    certificate_path: Path
    witness_kind: str
    objective_value: float
    bond_level_expelled_mass: float
    process_level_expelled_mass: float


def run(
    target_dir: str | Path,
    *,
    rules_dir: str | Path = "data/rules",
    blocks_dir: str | Path = "data/building_blocks",
    artifacts_dir: str | Path = "artifacts",
) -> RunReport:
    target_dir = Path(target_dir)
    rules_dir = Path(rules_dir)
    blocks_dir = Path(blocks_dir)
    artifacts_dir = Path(artifacts_dir)

    spec = load_runspec(target_dir)
    library = load_rule_library(rules_dir)
    encoded = encode_target(
        target_dir / spec.target.structure_path,
        ring_size=spec.target.ring_size,
        name=spec.name,
    )
    gen = build_dg_for_runspec(
        spec, library=library, blocks_dir=blocks_dir, target_dir=target_dir,
    )

    sink_smiles = encoded.graph.smiles  # type: ignore[attr-defined]
    ir = dg_to_ir.build_ir(
        gen.dg,
        library=library,
        sources=[gen.seco_precursor.smiles],
        sink_smiles=sink_smiles,
        ring_size=spec.target.ring_size,
        max_steps=spec.strategy.max_steps,
    )

    result = scip_backend.solve(ir, time_budget_s=spec.solver.time_budget_s)
    composed = (
        compose.compose_route(result.solution, ir, library)
        if result.solution else None
    )
    cert = certify.emit(spec, ir, composed, result.solution, result.witness)
    cert_path = certify.write(cert, artifacts_dir / spec.name / "certificate.json")

    return RunReport(
        spec=spec,
        certificate_path=cert_path,
        witness_kind=result.witness.kind,
        objective_value=result.witness.objective_value,
        bond_level_expelled_mass=(result.solution.bond_level_expelled_mass
                                  if result.solution else float("nan")),
        process_level_expelled_mass=(result.solution.process_level_expelled_mass
                                     if result.solution else float("nan")),
    )
