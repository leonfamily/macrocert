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
class PredicateSpec:
    """Application-condition predicates for the MØD strategy.

    See `macrocert.generate.strategies.PredicateSpec` for the runtime
    counterpart. This dataclass is the YAML-deserialised shape; the
    encoder in `build_dg.py` translates it into the generate-layer
    object before composing the strategy.

    When all fields are at their defaults the strategy reduces to the
    v0 unconditional behaviour (`apply_rules_up_to`).

    ``enforce_ez_geometry`` is a per-rule E/Z gate keyed by macrocert
    rule_id (e.g. ``"rcm"``); values are ``"E"`` or ``"Z"``. Background
    in ``docs/mod_stereo_reference.md`` §1.5, §5.2: MØD's
    ``TrigonalPlanar::morphismIso`` is ``MOD_ABORT`` so E/Z cannot be
    enforced at match time; the strategy-level filter implemented in
    ``strategies._enforce_ez_geometry_factory`` parses the product
    SMILES through RDKit and rejects derivations whose new double bond
    has the opposite geometry. Default ``None`` means "no E/Z gating",
    which preserves v0 behaviour for every existing RunSpec.
    """
    is_intramolecular: bool = False
    ring_size_equals: int | None = None
    enforce_ez_geometry: dict[str, str] | None = None
    # Workstream D phase-3: discriminator predicates between the two
    # ether rules. The two GML bodies (data/rules/aryl_etherification.gml
    # and data/rules/biaryl_etherification.gml) are structurally identical
    # because MØD's match operates on element labels — sp²-aromatic vs
    # sp³ context at atom 5 (the alcohol-side O) is invisible at the GML
    # level. See docs/macroetherification_research.md §1.4 and
    # docs/biaryl_etherification_research.md §1.2.
    #
    # Each field is a per-rule_id map of bool: when True for a given
    # rule_id, accept the derivation only if the product satisfies the
    # corresponding aromaticity/hybridization constraint at the new O
    # bridge. Implemented as rightPredicates with RDKit substructure
    # matching on the product SMILES (MØD's Derivation Python binding
    # does not expose the L→substrate morph mapping —
    # external/mod/libs/pymod/src/mod/py/Derivation.cpp:8-39 binds only
    # left/rule/right — so the substrate-side atom-5 inspection isn't
    # tractable; the rightPredicate substructure-match fallback is the
    # API-supported route).
    alcohol_partner_C_must_be_aromatic: dict[str, bool] | None = None
    alcohol_partner_C_must_be_sp3: dict[str, bool] | None = None


@dataclass(frozen=True)
class StrategySpec:
    max_steps: int = 6
    ring_close_only: bool = True
    predicates: PredicateSpec = field(default_factory=lambda: PredicateSpec())
    # Workstream F (Component 1): per-RunSpec opt-in for MØD stereo
    # enforcement. When True, build_dg.py constructs the DG with
    # ``LabelSettings(LabelType.Term, LabelRelation.Specialisation,
    # LabelRelation.Specialisation)`` so that stereo annotations on rule
    # vertices are honoured at match time. When False (default), MØD's
    # default 2-arg ``LabelSettings`` is used and stereo strings are
    # parsed but never enforced. See docs/mod_stereo_reference.md §2.3
    # and external/mod/libs/libmod/src/mod/Config.hpp:82-118 for the
    # underlying API; the on-path mirrors
    # external/mod/examples/py/030_stereo/320_aconitase.py:54-58.
    stereo_enforcement: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SolverSpec:
    backend: Literal["mod", "scip"] = "mod"
    top_n: int = 10
    time_budget_s: int = 60
    request_infeasibility_cert: bool = False
    # Per-rule activator overrides. Keys are rule_ids; values are
    # ``ReagentAlternative.name`` strings listed in the rule's
    # ``reagent_mass_alternatives``. When a rule_id is present here,
    # ``dg_to_ir.build_ir`` substitutes the named alternative's
    # ``reagent_mass_g_per_mol`` into the per-edge process-level penalty
    # in place of the canonical ``meta.reagent_mass_g_per_mol``. A rule
    # absent from this map keeps its canonical activator mass (current
    # default behaviour, preserved for backward compatibility).
    # Example YAML:
    #   solver:
    #     extra:
    #       activators:
    #         macrolactonization: Corey_Nicolaou
    # Validation against the loaded RuleLibrary happens in
    # ``pipeline.run`` via ``validate_activators`` so an unknown
    # alternative name (or unknown rule_id) fails loud before any
    # generation or solver work is done.
    extra: dict[str, Any] = field(default_factory=dict)


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
            predicates=_parse_predicates(
                strategy.get("predicates")
                if isinstance(strategy.get("predicates"), dict)
                else data.get("strategy_predicates")
            ),
            # Workstream F (Component 1): off by default for backward
            # compatibility — existing rule library is stereo-free and
            # must continue to build under the default 2-arg
            # ``LabelSettings``. See docs/mod_stereo_reference.md §2.3.
            stereo_enforcement=bool(strategy.get("stereo_enforcement", False)),
            extra=dict(strategy.get("extra", {})),
        ),
        solver=SolverSpec(
            backend=str(solver.get("backend", "mod")),  # type: ignore[arg-type]
            top_n=int(solver.get("top_n", 10)),
            time_budget_s=int(solver.get("time_budget_s", 60)),
            request_infeasibility_cert=bool(
                solver.get("request_infeasibility_cert", False)
            ),
            extra=_parse_solver_extra(solver.get("extra")),
        ),
        energetics=EnergeticsSpec(
            enabled=bool(energetics.get("enabled", False)),
            initial_tier=str(energetics.get("initial_tier", "xtb")),  # type: ignore[arg-type]
            dG_kcal_max=energetics.get("dG_kcal_max"),
        ),
        notes=str(data.get("notes", "")),
    )


def _parse_predicates(d: Any) -> PredicateSpec:
    """Build a PredicateSpec from the YAML dict.

    Accepts either ``strategy.predicates:`` (nested) or top-level
    ``strategy_predicates:`` — both encode the same thing. Unknown
    keys are ignored to keep forward-compatibility room for additional
    predicates added by later Workstream D milestones.
    """
    if not isinstance(d, dict):
        return PredicateSpec()
    raw_n = d.get("ring_size_equals")
    raw_ez = d.get("enforce_ez_geometry")
    ez_map: dict[str, str] | None
    if isinstance(raw_ez, dict) and raw_ez:
        # Normalise keys to str and values to upper-case "E"/"Z";
        # anything else raises so misconfigured YAML fails loud.
        ez_map = {}
        for k, v in raw_ez.items():
            tok = str(v).strip().upper()
            if tok not in ("E", "Z"):
                raise ValueError(
                    f"enforce_ez_geometry[{k!r}]={v!r}; expected 'E' or 'Z'"
                )
            ez_map[str(k)] = tok
    else:
        ez_map = None

    # Phase-3 discriminator predicates. Each is a per-rule_id bool map;
    # mis-typed YAML (e.g. string instead of bool) fails loud at load
    # time so RunSpecs don't silently bypass the gate.
    def _parse_bool_map(raw: Any, name: str) -> dict[str, bool] | None:
        if raw is None:
            return None
        if not isinstance(raw, dict) or not raw:
            return None
        out: dict[str, bool] = {}
        for k, v in raw.items():
            if not isinstance(v, bool):
                raise ValueError(
                    f"{name}[{k!r}]={v!r}; expected bool (true/false)"
                )
            out[str(k)] = v
        return out

    aromatic_map = _parse_bool_map(
        d.get("alcohol_partner_C_must_be_aromatic"),
        "alcohol_partner_C_must_be_aromatic",
    )
    sp3_map = _parse_bool_map(
        d.get("alcohol_partner_C_must_be_sp3"),
        "alcohol_partner_C_must_be_sp3",
    )

    return PredicateSpec(
        is_intramolecular=bool(d.get("is_intramolecular", False)),
        ring_size_equals=int(raw_n) if raw_n is not None else None,
        enforce_ez_geometry=ez_map,
        alcohol_partner_C_must_be_aromatic=aromatic_map,
        alcohol_partner_C_must_be_sp3=sp3_map,
    )


def _parse_solver_extra(raw: Any) -> dict[str, Any]:
    """Normalise ``solver.extra`` and validate the shape of known keys.

    Currently the only known key is ``activators``: a ``dict[str, str]``
    mapping rule_id → ``ReagentAlternative.name``. Unknown keys are
    preserved verbatim so future solver-level toggles can be added
    without churning this parser.

    A bare ``activator: <name>`` (singular, no per-rule scoping) is
    rejected with a pointer to the new key — the original Workstream-C
    runspecs used that shape before this wiring landed, and silently
    dropping it (the previous behaviour) is the bug this whole change
    is fixing. Per
    ``data/validation_panel/corey_erythronolide_b_macrolactonization_1978``
    history.
    """
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(
            f"solver.extra must be a mapping, got {type(raw).__name__}"
        )
    out: dict[str, Any] = {}
    for k, v in raw.items():
        key = str(k)
        if key == "activator":
            raise ValueError(
                "solver.extra.activator is no longer supported; use "
                "solver.extra.activators: {<rule_id>: <activator_name>} "
                "for per-rule activator selection"
            )
        if key == "activators":
            if not isinstance(v, dict) or not v:
                raise ValueError(
                    "solver.extra.activators must be a non-empty mapping "
                    "of rule_id -> activator_name"
                )
            norm: dict[str, str] = {}
            for rule_id, alt_name in v.items():
                if not isinstance(alt_name, str) or not alt_name:
                    raise ValueError(
                        f"solver.extra.activators[{rule_id!r}]={alt_name!r}; "
                        f"expected non-empty string (activator name)"
                    )
                norm[str(rule_id)] = alt_name
            out[key] = norm
        else:
            out[key] = v
    return out


def _as_tuple(v: Any) -> tuple[str, ...]:
    if isinstance(v, str):
        return (v,)
    return tuple(v or ())


def resolve_activators(
    spec: "RunSpec", library: Any
) -> dict[str, float]:
    """Resolve ``solver.extra.activators`` against the RuleLibrary.

    Returns a ``dict[rule_id -> reagent_mass_g_per_mol]`` ready to be
    consumed by ``dg_to_ir.build_ir``. Raises ``ValueError`` on:

      * ``rule_id`` not present in the loaded library
      * activator name not listed in the rule's
        ``reagent_mass_alternatives`` (i.e. ``RuleMeta.get_alternative``
        returns ``None``)

    A rule absent from the map is *not* an error — the caller falls
    back to the rule's canonical ``meta.reagent_mass_g_per_mol``.

    This is the surface where a typo in ``solver.extra.activators``
    becomes a loud failure *before* MØD generation or solving runs.
    Called from ``pipeline.run``; tests may call it directly.
    """
    activators = spec.solver.extra.get("activators") if spec.solver.extra else None
    if not activators:
        return {}
    out: dict[str, float] = {}
    for rule_id, alt_name in activators.items():
        if rule_id not in library.rules:
            raise ValueError(
                f"solver.extra.activators[{rule_id!r}]={alt_name!r}: rule "
                f"{rule_id!r} is not present in the loaded RuleLibrary "
                f"(known: {sorted(library.rules)!r})"
            )
        rule_def = library.rules[rule_id]
        alt = rule_def.meta.get_alternative(alt_name)
        if alt is None:
            known = [a.name for a in rule_def.meta.reagent_mass_alternatives]
            raise ValueError(
                f"solver.extra.activators[{rule_id!r}]={alt_name!r}: no such "
                f"reagent_mass_alternative on rule {rule_id!r} "
                f"(known: {known!r})"
            )
        out[rule_id] = alt.reagent_mass_g_per_mol
    return out


def _to_jsonable(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {f: _to_jsonable(getattr(obj, f)) for f in obj.__dataclass_fields__}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj
