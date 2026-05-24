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

from ..spec.rules import RuleLibrary
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
    library: RuleLibrary | None = None,
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
        "provenance": _build_provenance(ir, composed, library),
    }
    return cert


def _build_provenance(
    ir: HyperFlowIR,
    composed: ComposedRule | None,
    library: RuleLibrary | None,
) -> dict[str, Any]:
    """Assemble cert provenance.

    Currently only carries ``stereo_advisories``: one entry per distinct
    rule (across composed.rule_ids_traced ∪ ir.hyperedges) whose
    ``stereo_treatment == 'advisory_only'``. The list is sorted and
    deduplicated for hash-stable certificates.
    """
    advisories: dict[str, str] = {}
    if library is not None:
        rule_ids: set[str] = set()
        if composed is not None:
            rule_ids.update(composed.rule_ids_traced)
        for edge in ir.hyperedges:
            rid = getattr(edge, "rule_id", None)
            if rid and rid in library.rules:
                rule_ids.add(rid)
        for rid in rule_ids:
            if rid not in library.rules:
                continue
            meta = library.rules[rid].meta
            if meta.stereo_treatment == "advisory_only" and meta.stereo_advisory:
                advisories[rid] = meta.stereo_advisory
    return {
        "stereo_advisories": [
            {"rule_id": rid, "advisory": advisories[rid]}
            for rid in sorted(advisories)
        ],
    }


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
