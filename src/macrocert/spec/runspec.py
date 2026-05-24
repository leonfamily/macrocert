"""RunSpec: the single struct that drives one pipeline.run() invocation.

Ascomylactam A and every validation-panel case are RunSpec YAMLs. The
pipeline does not branch on "is this the real target" — see
proposal §3, milestone M4.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml


@dataclass(frozen=True)
class TargetSpec:
    structure_path: str
    ring_size: int
    expected_ring_atoms: tuple[int, ...] = ()


@dataclass(frozen=True)
class StrategySpec:
    max_steps: int = 6
    ring_close_only: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SolverSpec:
    backend: Literal["mod", "scip"] = "mod"
    top_n: int = 10
    time_budget_s: int = 60
    request_infeasibility_cert: bool = False


@dataclass(frozen=True)
class EnergeticsSpec:
    enabled: bool = False
    initial_tier: Literal["xtb", "mlip", "dft"] = "xtb"
    dG_kcal_max: float | None = None


@dataclass(frozen=True)
class RunSpec:
    name: str
    target: TargetSpec
    blocks: tuple[str, ...]
    rules: tuple[str, ...]
    strategy: StrategySpec = field(default_factory=StrategySpec)
    solver: SolverSpec = field(default_factory=SolverSpec)
    energetics: EnergeticsSpec = field(default_factory=EnergeticsSpec)
    notes: str = ""

    def content_hash(self) -> str:
        payload = json.dumps(_to_jsonable(self), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()


def load_runspec(path: str | Path) -> RunSpec:
    path = Path(path)
    if path.is_dir():
        path = path / "runspec.yaml"
    data = yaml.safe_load(path.read_text()) or {}

    target = data.get("target") or {}
    strategy = data.get("strategy") or {}
    solver = data.get("solver") or {}
    energetics = data.get("energetics") or {}

    return RunSpec(
        name=str(data.get("name") or path.parent.name),
        target=TargetSpec(
            structure_path=str(target["structure_path"]),
            ring_size=int(target["ring_size"]),
            expected_ring_atoms=tuple(target.get("expected_ring_atoms", ())),
        ),
        blocks=_as_tuple(data.get("blocks", ())),
        rules=_as_tuple(data.get("rules", ())),
        strategy=StrategySpec(
            max_steps=int(strategy.get("max_steps", 6)),
            ring_close_only=bool(strategy.get("ring_close_only", True)),
            extra=dict(strategy.get("extra", {})),
        ),
        solver=SolverSpec(
            backend=str(solver.get("backend", "mod")),  # type: ignore[arg-type]
            top_n=int(solver.get("top_n", 10)),
            time_budget_s=int(solver.get("time_budget_s", 60)),
            request_infeasibility_cert=bool(
                solver.get("request_infeasibility_cert", False)
            ),
        ),
        energetics=EnergeticsSpec(
            enabled=bool(energetics.get("enabled", False)),
            initial_tier=str(energetics.get("initial_tier", "xtb")),  # type: ignore[arg-type]
            dG_kcal_max=energetics.get("dG_kcal_max"),
        ),
        notes=str(data.get("notes", "")),
    )


def _as_tuple(v: Any) -> tuple[str, ...]:
    if isinstance(v, str):
        return (v,)
    return tuple(v or ())


def _to_jsonable(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {f: _to_jsonable(getattr(obj, f)) for f in obj.__dataclass_fields__}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj
