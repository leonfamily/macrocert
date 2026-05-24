"""Tests for the ``solver.extra.activators`` override path.

The override travels:

    runspec.yaml  →  RunSpec.solver.extra["activators"]
                  →  spec.runspec.resolve_activators(spec, library)
                  →  kernel.dg_to_ir.build_ir(activator_reagent_masses=...)
                  →  HyperEdge.reagent_mass_g_per_mol
                  →  kernel.objective.process_level_objective(ir).coeffs

These tests exercise each leg so a future refactor can't silently drop
the override (the precise failure mode the Workstream-C erythronolide
B M5 cert surfaced before this wiring landed).
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from macrocert.kernel.dg_to_ir import build_ir
from macrocert.kernel.objective import process_level_objective
from macrocert.spec.rules import load_rule_library
from macrocert.spec.runspec import load_runspec, resolve_activators


# Real rule library (data/rules/) so the macrolactonization
# alternatives table is the production one — Yamaguchi 568, Corey
# 482, etc. per data/rules/macrolactonization.meta.yaml.
RULES_DIR = Path(__file__).resolve().parents[2] / "data" / "rules"


# -- Fake MØD DG --------------------------------------------------------
#
# build_ir only consumes a thin slice of mod.DG: vertex.graph.smiles,
# vertex.graph.name, edge.rules (iterable), edge.sources, edge.targets.
# We synthesise enough to drive one macrolactonization-class edge
# without needing to import mod at all (mod can be unavailable in unit
# test environments).

class _FakeGraph:
    def __init__(self, smiles: str, name: str = "") -> None:
        self.smiles = smiles
        self.name = name


class _FakeVertex:
    def __init__(self, smiles: str, name: str = "") -> None:
        self.graph = _FakeGraph(smiles, name)


class _FakeRule:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeEdge:
    def __init__(self, rule_name: str, sources: list[_FakeVertex],
                 targets: list[_FakeVertex]) -> None:
        self.rules = [_FakeRule(rule_name)]
        self.sources = sources
        self.targets = targets


class _FakeDG:
    def __init__(self, vertices: list[_FakeVertex],
                 edges: list[_FakeEdge]) -> None:
        self.vertices = vertices
        self.edges = edges


def _make_macrolactonization_dg():
    """One seco-acid → cyclized 14-membered lactone edge under the
    macrolactonization rule. The SMILES are placeholders that round-trip
    canonical_smiles cleanly; only the activator-mass plumbing is under
    test here, not the chemistry."""
    # Linear seco-acid (open chain, free -OH and -COOH).
    seco = "OC(=O)CCCCCCCCCCCCO"
    # 14-membered lactone (intramolecular ester from the same chain).
    lactone = "O=C1OCCCCCCCCCCCC1"
    v_seco = _FakeVertex(seco)
    v_lactone = _FakeVertex(lactone)
    edge = _FakeEdge(
        rule_name='macrolactonization (ester ring closure, -H2O)',
        sources=[v_seco],
        targets=[v_lactone],
    )
    return _FakeDG([v_seco, v_lactone], [edge]), seco, lactone


def test_canonical_reagent_mass_when_no_override() -> None:
    """No solver.extra.activators → canonical Yamaguchi 568 g/mol."""
    library = load_rule_library(RULES_DIR)
    dg, seco, lactone = _make_macrolactonization_dg()
    ir = build_ir(
        dg,
        library=library,
        sources=[seco],
        sink_smiles=lactone,
        ring_size=14,
        max_steps=1,
    )
    macro_edges = [e for e in ir.hyperedges
                   if e.rule_id == "macrolactonization"]
    assert macro_edges, "macrolactonization rule_id resolution failed"
    # Canonical Yamaguchi mass per data/rules/macrolactonization.meta.yaml.
    assert macro_edges[0].reagent_mass_g_per_mol == 568.0


def test_corey_nicolaou_override_threads_to_ir() -> None:
    """``activator_reagent_masses={'macrolactonization': 482}`` → the
    per-edge reagent_mass_g_per_mol becomes 482 (Corey-Nicolaou) instead
    of 568 (Yamaguchi canonical)."""
    library = load_rule_library(RULES_DIR)
    dg, seco, lactone = _make_macrolactonization_dg()
    alt = library.rules["macrolactonization"].meta.get_alternative(
        "Corey_Nicolaou"
    )
    assert alt is not None and alt.reagent_mass_g_per_mol == 482.0
    ir = build_ir(
        dg,
        library=library,
        sources=[seco],
        sink_smiles=lactone,
        ring_size=14,
        max_steps=1,
        activator_reagent_masses={"macrolactonization": 482.0},
    )
    macro_edges = [e for e in ir.hyperedges
                   if e.rule_id == "macrolactonization"]
    assert macro_edges
    assert macro_edges[0].reagent_mass_g_per_mol == 482.0
    # Bond-level mass (H2O) is identical under either activator.
    assert macro_edges[0].expelled_mass_g_per_mol == pytest.approx(18.015)


def test_process_level_objective_picks_up_override() -> None:
    """The process-level objective coefficient on the macrolactonization
    edge equals expelled_mass + reagent_mass — so the Corey-Nicolaou
    override must propagate all the way through to the linear
    objective consumed by both backends."""
    library = load_rule_library(RULES_DIR)
    dg, seco, lactone = _make_macrolactonization_dg()
    ir = build_ir(
        dg,
        library=library,
        sources=[seco],
        sink_smiles=lactone,
        ring_size=14,
        max_steps=1,
        activator_reagent_masses={"macrolactonization": 482.0},
    )
    obj = process_level_objective(ir)
    macro_edge = next(e for e in ir.hyperedges
                      if e.rule_id == "macrolactonization")
    # 18.015 (H2O) + 482.0 (Corey-Nicolaou) = 500.015.
    assert obj.coeffs[macro_edge.id] == pytest.approx(18.015 + 482.0)


# -- resolve_activators ----------------------------------------------

def _write_minimal_runspec(tmp_path: Path, extra: str) -> Path:
    (tmp_path / "runspec.yaml").write_text(dedent(f"""
        name: act_override
        target:
          structure_path: structure.mol
          ring_size: 14
        blocks: [b]
        rules: [macrolactonization]
        solver:
          backend: scip
          extra:
            {extra}
    """).strip())
    return tmp_path


def test_resolve_activators_happy_path(tmp_path: Path) -> None:
    library = load_rule_library(RULES_DIR)
    p = _write_minimal_runspec(
        tmp_path,
        "activators:\n              macrolactonization: Corey_Nicolaou",
    )
    spec = load_runspec(p)
    resolved = resolve_activators(spec, library)
    assert resolved == {"macrolactonization": 482.0}


def test_resolve_activators_empty_map_is_default(tmp_path: Path) -> None:
    """RunSpecs without solver.extra.activators yield an empty map and
    the canonical reagent_mass path is preserved."""
    (tmp_path / "runspec.yaml").write_text(dedent("""
        name: no_override
        target:
          structure_path: structure.mol
          ring_size: 14
        blocks: [b]
        rules: [macrolactonization]
    """).strip())
    spec = load_runspec(tmp_path)
    library = load_rule_library(RULES_DIR)
    assert resolve_activators(spec, library) == {}


def test_resolve_activators_unknown_activator_name(tmp_path: Path) -> None:
    library = load_rule_library(RULES_DIR)
    p = _write_minimal_runspec(
        tmp_path,
        "activators:\n              macrolactonization: NotAnActivator",
    )
    spec = load_runspec(p)
    with pytest.raises(ValueError, match="no such reagent_mass_alternative"):
        resolve_activators(spec, library)


def test_resolve_activators_unknown_rule_id(tmp_path: Path) -> None:
    library = load_rule_library(RULES_DIR)
    p = _write_minimal_runspec(
        tmp_path,
        "activators:\n              not_a_rule: Yamaguchi",
    )
    spec = load_runspec(p)
    with pytest.raises(ValueError,
                       match="not present in the loaded RuleLibrary"):
        resolve_activators(spec, library)


def test_legacy_activator_singular_rejected(tmp_path: Path) -> None:
    """The pre-wiring shape ``solver.extra.activator: <name>`` (singular,
    no per-rule key) is rejected at parse time so existing RunSpecs that
    used the placeholder syntax fail loud instead of being silently
    ignored."""
    (tmp_path / "runspec.yaml").write_text(dedent("""
        name: legacy
        target:
          structure_path: structure.mol
          ring_size: 14
        blocks: [b]
        rules: [macrolactonization]
        solver:
          extra:
            activator: Corey_Nicolaou
    """).strip())
    with pytest.raises(ValueError, match="no longer supported"):
        load_runspec(tmp_path)


def test_erythronolide_b_runspec_uses_corey_nicolaou() -> None:
    """The Workstream-C panel case actually carries the override after
    the rename. Guards against future YAML edits that silently regress
    the case."""
    panel_dir = (Path(__file__).resolve().parents[2]
                 / "data" / "validation_panel"
                 / "corey_erythronolide_b_macrolactonization_1978")
    spec = load_runspec(panel_dir)
    library = load_rule_library(RULES_DIR)
    resolved = resolve_activators(spec, library)
    assert resolved == {"macrolactonization": 482.0}
