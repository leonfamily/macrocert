"""Cert provenance — stereo_advisories propagation (Workstream F #36).

certify.emit() copies the stereo_advisory text of any advisory_only rule
whose rule_id appears in the IR's hyperedges (or the composed rule's
rule_ids_traced) into ``cert.provenance.stereo_advisories``.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from macrocert.kernel import certify
from macrocert.kernel.ir import (
    HyperEdge,
    HyperFlowIR,
    LinearObjective,
    Vertex,
    Witness,
)
from macrocert.spec.rules import load_rule_library
from macrocert.spec.runspec import RunSpec, TargetSpec


def _write_rule(
    directory: Path,
    rid: str,
    *,
    treatment: str,
    advisory: str = "",
) -> None:
    (directory / f"{rid}.gml").write_text(
        f'rule [ ruleID "{rid}" left [ node [ id 1 label "C" ] ] '
        f'context [ ] right [ node [ id 1 label "C" ] ] ]'
    )
    body = dedent(
        f"""
        reagent_mass_g_per_mol: 1.0
        classes: []
        stereo_flags: []
        refs: []
        notes: ""
        stereo_treatment: {treatment}
        """
    ).strip()
    if advisory:
        body += f'\nstereo_advisory: "{advisory}"'
    (directory / f"{rid}.meta.yaml").write_text(body)


def _minimal_runspec() -> RunSpec:
    return RunSpec(
        name="fixture",
        target=TargetSpec(structure_path="structure.mol", ring_size=13),
        blocks=(),
        rules=("rcm_fixture",),
    )


def _minimal_ir(rule_id: str) -> HyperFlowIR:
    edge = HyperEdge(
        id="edge_0",
        rule_id=rule_id,
        sources=("A",),
        targets=("B",),
        expelled_mass_g_per_mol=28.0,
        reagent_mass_g_per_mol=30.0,
        is_macrocyclization=True,
    )
    return HyperFlowIR(
        vertices=(Vertex(id="A"), Vertex(id="B")),
        hyperedges=(edge,),
        sources=("A",),
        sink="B",
        max_steps=1,
        constraints=(),
        objective=LinearObjective(coeffs={"edge_0": 28.0}),
    )


def test_stereo_advisory_propagates_to_cert(tmp_path: Path) -> None:
    _write_rule(
        tmp_path,
        "rcm_fixture",
        treatment="advisory_only",
        advisory="trigonalPlanar MOD_ABORT; E/Z undetermined",
    )
    library = load_rule_library(tmp_path)
    ir = _minimal_ir("rcm_fixture")
    witness = Witness(kind="infeasible")
    cert = certify.emit(
        _minimal_runspec(), ir, None, None, witness, library=library
    )
    advisories = cert["provenance"]["stereo_advisories"]
    assert len(advisories) == 1
    assert advisories[0]["rule_id"] == "rcm_fixture"
    assert "MOD_ABORT" in advisories[0]["advisory"]


def test_no_advisory_for_match_enforced_rule(tmp_path: Path) -> None:
    _write_rule(tmp_path, "rcm_fixture", treatment="match_enforced")
    library = load_rule_library(tmp_path)
    ir = _minimal_ir("rcm_fixture")
    witness = Witness(kind="infeasible")
    cert = certify.emit(
        _minimal_runspec(), ir, None, None, witness, library=library
    )
    assert cert["provenance"]["stereo_advisories"] == []


def test_no_advisory_for_sp2_only_rule(tmp_path: Path) -> None:
    _write_rule(tmp_path, "rcm_fixture", treatment="n_a_sp2_only")
    library = load_rule_library(tmp_path)
    ir = _minimal_ir("rcm_fixture")
    witness = Witness(kind="infeasible")
    cert = certify.emit(
        _minimal_runspec(), ir, None, None, witness, library=library
    )
    assert cert["provenance"]["stereo_advisories"] == []


def test_emit_without_library_returns_empty_advisories() -> None:
    """Backward compat: emit() called without a library yields an empty
    stereo_advisories list rather than failing — the provenance block is
    always present but inert."""
    ir = _minimal_ir("any_rule")
    witness = Witness(kind="infeasible")
    cert = certify.emit(_minimal_runspec(), ir, None, None, witness)
    assert "provenance" in cert
    assert cert["provenance"]["stereo_advisories"] == []
