"""End-to-end pipeline: RunSpec → Layer A → B → C → Certificate.

Layer D (energetics) and Layer E (reports) hook in at M3+ via the
energetics_dependencies cache and the report.render module.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .energetics.cache import EnergeticsCache
from .energetics.feedback import EnergeticsDeps, run_with_energetics
from .generate import build_dg_for_runspec
from .kernel import certify, compose, dg_to_ir, scip_backend
from .spec.rules import load_rule_library
from .spec.runspec import RunSpec, load_runspec, resolve_activators
from .spec.target import encode_target


@dataclass
class RunReport:
    spec: RunSpec
    certificate_path: Path
    witness_kind: str
    objective_value: float
    bond_level_expelled_mass: float
    process_level_expelled_mass: float
    energetics_summary: dict[str, Any] | None = None


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
    # Resolve solver.extra.activators against the library before any
    # generation or solver work, so unknown rule_ids / unknown activator
    # names surface as a clean ValueError early. Empty map = canonical
    # reagent_mass for every rule (backward-compatible default).
    activator_reagent_masses = resolve_activators(spec, library)
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
        activator_reagent_masses=activator_reagent_masses,
    )

    energetics_deps: EnergeticsDeps | None = None
    if spec.energetics.enabled:
        fb = run_with_energetics(
            ir,
            initial_tier=spec.energetics.initial_tier,
            dG_max_kcal_per_mol=spec.energetics.dG_kcal_max or 1e9,
            cache=EnergeticsCache(),
            time_budget_s=spec.solver.time_budget_s,
        )
        result = fb.final
        energetics_deps = fb.energetics
    else:
        result = scip_backend.solve(ir, time_budget_s=spec.solver.time_budget_s)

    composed = (
        compose.compose_route(result.solution, ir, library)
        if result.solution else None
    )
    cert = certify.emit(
        spec, ir, composed, result.solution, result.witness,
        energetics_deps=energetics_deps,
        library=library,
    )
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
        energetics_summary=(energetics_deps.to_jsonable()
                            if energetics_deps is not None else None),
    )
