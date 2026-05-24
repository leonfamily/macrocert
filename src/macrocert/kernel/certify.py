"""Emit a Certificate JSON object from a Solution + Witness + RunSpec.

The schema lives at src/macrocert/verifier/schema/certificate.schema.json
and is the one source of truth for the format. The verifier loads it
on every run.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..spec.runspec import RunSpec
from .compose import ComposedRule
from .ir import HyperFlowIR, Witness, Solution


SCHEMA_VERSION = "1.0"


def emit(
    spec: RunSpec,
    ir: HyperFlowIR,
    composed: ComposedRule | None,
    solution: Solution | None,
    witness: Witness,
    *,
    energetics_deps: Any = None,
) -> dict[str, Any]:
    cert: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec_hash": spec.content_hash(),
        "derivation_graph": _serialize_ir(ir),
        "composed_rule": _serialize_composed(composed) if composed else _empty_composed(ir),
        "flow": dict(solution.flow) if solution else {},
        "solver_witness": _serialize_witness(witness),
        "energetics_dependencies": (
            energetics_deps.to_jsonable() if energetics_deps is not None else None
        ),
    }
    return cert


def write(cert: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cert, indent=2, sort_keys=True))
    return path


def _serialize_ir(ir: HyperFlowIR) -> dict[str, Any]:
    return {
        "vertices": [asdict(v) for v in ir.vertices],
        "hyperedges": [asdict(e) for e in ir.hyperedges],
        "sources": list(ir.sources),
        "sink": ir.sink,
        "max_steps": ir.max_steps,
    }


def _serialize_composed(c: ComposedRule) -> dict[str, Any]:
    return {
        "gml": c.gml,
        "atom_map": {str(k): v for k, v in c.atom_map.items()},
        "expelled_mass_g_per_mol": c.expelled_mass_g_per_mol,
        "retained_root_atom": c.retained_root_atom,
        "rule_ids_traced": list(c.rule_ids_traced),
    }


def _empty_composed(ir: HyperFlowIR) -> dict[str, Any]:
    return {
        "gml": "rule [ ruleID \"empty\" left [ ] context [ ] right [ ] ]",
        "atom_map": {},
        "expelled_mass_g_per_mol": 0.0,
        "retained_root_atom": 0,
        "rule_ids_traced": [],
    }


def _serialize_witness(w: Witness) -> dict[str, Any]:
    if w.kind == "optimal":
        return {
            "kind": "optimal",
            "obj_value": w.objective_value,
            "dual_bound": w.dual_bound,
        }
    return {
        "kind": "infeasible",
        "iis_constraint_ids": list(w.iis_constraint_ids),
        "farkas_multipliers": dict(w.farkas_multipliers),
    }
