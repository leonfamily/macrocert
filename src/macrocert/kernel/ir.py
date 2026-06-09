"""Backend-neutral hyperflow IR.

Both kernel.mod_backend and kernel.scip_backend consume this IR. The
IR itself is serializable — it lives inside the certificate so the
verifier can rebuild and re-check the formulation without depending
on either backend.

Vertices are keyed by canonical SMILES (so a fresh MØD invocation on
the same RunSpec produces identical IDs). Hyperedges are keyed by a
deterministic hash of (rule_id, sorted source IDs, sorted target IDs)
so the certificate is stable under serialization round-trips.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Literal


@dataclass(frozen=True)
class Vertex:
    id: str           # canonical SMILES (also the human-readable identifier)
    label: str = ""   # optional friendly name


@dataclass(frozen=True)
class HyperEdge:
    id: str                                  # deterministic hash
    rule_id: str
    sources: tuple[str, ...]                 # vertex IDs (multiset; order is canonical-sorted)
    targets: tuple[str, ...]
    expelled_mass_g_per_mol: float           # bond-level Trost cost per firing
    reagent_mass_g_per_mol: float            # process-level penalty per firing
    is_macrocyclization: bool = False        # used in the ring-closure-exactly-once constraint
    # Stereo treatment of the fired rule, copied from RuleMeta.stereo_treatment.
    # The verifier uses this to enforce advisory_propagation invariants on
    # the cert without needing to load the rule library at verify time.
    # Default keeps pre-Workstream-F-#36 fixtures still valid.
    stereo_treatment: str = "match_enforced"


@dataclass(frozen=True)
class Constraint:
    id: str
    kind: Literal["flow_balance", "step_budget", "exactly_one_macrocyclization",
                  "source_bound", "sink_required", "dG_bound"]
    description: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LinearObjective:
    coeffs: dict[str, float]                 # edge_id → coefficient
    minimize: bool = True                    # AE = minimize expelled mass
    name: str = "bond_level_expelled_mass"


@dataclass(frozen=True)
class HyperFlowIR:
    vertices: tuple[Vertex, ...]
    hyperedges: tuple[HyperEdge, ...]
    sources: tuple[str, ...]                 # vertex IDs that may be drawn from infinite supply
    sink: str                                # the target vertex ID (production = 1)
    max_steps: int
    constraints: tuple[Constraint, ...]
    objective: LinearObjective

    def edge_by_id(self, eid: str) -> HyperEdge:
        for e in self.hyperedges:
            if e.id == eid:
                return e
        raise KeyError(f"no hyperedge with id {eid!r}")

    def vertex_by_id(self, vid: str) -> Vertex:
        for v in self.vertices:
            if v.id == vid:
                return v
        raise KeyError(f"no vertex with id {vid!r}")

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "vertices": [asdict(v) for v in self.vertices],
            "hyperedges": [asdict(e) for e in self.hyperedges],
            "sources": list(self.sources),
            "sink": self.sink,
            "max_steps": self.max_steps,
            "constraints": [asdict(c) for c in self.constraints],
            "objective": asdict(self.objective),
        }


@dataclass(frozen=True)
class Solution:
    flow: dict[str, int]                     # edge_id → integer multiplicity
    objective_value: float
    bond_level_expelled_mass: float          # = objective_value when objective.name matches
    process_level_expelled_mass: float       # sum(flow[e] * (expelled + reagent))
    dual_bound: float                        # solver-reported best dual; equal to objective when optimal


@dataclass(frozen=True)
class Witness:
    kind: Literal["optimal", "infeasible"]
    objective_value: float = 0.0
    dual_bound: float = 0.0
    farkas_multipliers: dict[str, float] = field(default_factory=dict)
    iis_constraint_ids: tuple[str, ...] = ()


def make_edge_id(rule_id: str, sources: tuple[str, ...], targets: tuple[str, ...]) -> str:
    payload = "|".join([rule_id, ";".join(sorted(sources)), ";".join(sorted(targets))])
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
