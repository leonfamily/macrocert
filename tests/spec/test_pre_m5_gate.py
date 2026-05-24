"""Tests for the pre-M5 gate's chemistry-aware stereo-policy check
(Workstream F #36).

The gate's check_stereo_annotations function is loaded by file path so we
don't depend on scripts/ being on sys.path. Each test builds a tiny
fixture rules dir, monkeypatches the gate's REPO_ROOT to point at the
tmp_path, and asserts the per-rule diagnostic + pass/fail outcome.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = REPO_ROOT / "scripts" / "pre_m5_gate.py"


@pytest.fixture
def gate_module(monkeypatch, tmp_path):
    """Load scripts/pre_m5_gate.py with REPO_ROOT pointed at tmp_path."""
    spec = importlib.util.spec_from_file_location("_pre_m5_gate_under_test", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    (tmp_path / "data" / "rules").mkdir(parents=True)
    return mod


LOCK_REQUIRING_STEREO = {
    "rule_library": {"stereo_annotations_required": True},
}


def _write_rule(rules_dir: Path, rid: str, *, gml_body: str, meta_body: str) -> None:
    (rules_dir / f"{rid}.gml").write_text(dedent(gml_body).strip())
    (rules_dir / f"{rid}.meta.yaml").write_text(dedent(meta_body).strip())


# ---------------------------------------------------------------------------
# match_enforced
# ---------------------------------------------------------------------------


def test_match_enforced_with_stereo_passes(gate_module, tmp_path, capsys):
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "macrolactam_toy",
        gml_body='rule [ ruleID "x" left [ node [ id 1 label "C" stereo "tetrahedral[2,3,4,5]" ] ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: match_enforced
        """,
    )
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert ok, out
    assert "match_enforced" in out
    assert "[PASS] stereo policy declared" in out


def test_match_enforced_without_stereo_fails(gate_module, tmp_path, capsys):
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "macrolactam_unannot",
        gml_body='rule [ ruleID "x" left [ node [ id 1 label "C" ] ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: match_enforced
        """,
    )
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert not ok
    assert "macrolactam_unannot" in out
    assert "match_enforced" in out


# ---------------------------------------------------------------------------
# n_a_sp2_only
# ---------------------------------------------------------------------------


def test_n_a_sp2_only_passes_without_stereo_in_gml(gate_module, tmp_path, capsys):
    """Cross-coupling-style rule: bond site is sp²; no stereo annotation
    required and no grep performed on the GML body."""
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "cross_coupling_toy",
        gml_body='rule [ ruleID "x" left [ node [ id 1 label "C" ] ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: n_a_sp2_only
        """,
    )
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert ok, out
    assert "n_a_sp2_only" in out
    assert "sp²-only" in out


# ---------------------------------------------------------------------------
# advisory_only
# ---------------------------------------------------------------------------


def test_advisory_only_with_message_passes(gate_module, tmp_path, capsys):
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "rcm_toy",
        gml_body='rule [ ruleID "x" left [ node [ id 1 label "C" ] ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: advisory_only
            stereo_advisory: "trigonalPlanar is MOD_ABORT; E/Z undetermined at match time."
        """,
    )
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert ok, out
    assert "advisory_only" in out
    assert "advisory present" in out


def test_advisory_only_without_message_fails_at_parse(gate_module, tmp_path):
    """The rules.py parser rejects advisory_only with empty advisory before
    the gate even sees it — but the gate must also defensively fail if
    given a hand-edited meta that slipped through."""
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "rcm_toy",
        gml_body='rule [ ruleID "x" left [ ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: advisory_only
        """,
    )
    # The gate parses the meta independently of rules.py, so it sees the
    # empty advisory and fails — that's the intended defense-in-depth.
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    assert not ok


# ---------------------------------------------------------------------------
# unknown treatment
# ---------------------------------------------------------------------------


def test_unknown_stereo_treatment_fails(gate_module, tmp_path, capsys):
    rules_dir = tmp_path / "data" / "rules"
    _write_rule(
        rules_dir,
        "bogus",
        gml_body='rule [ ruleID "x" left [ ] context [ ] right [ ] ]',
        meta_body="""
            reagent_mass_g_per_mol: 1.0
            classes: []
            stereo_flags: []
            refs: []
            notes: ""
            stereo_treatment: handwave
        """,
    )
    ok = gate_module.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert not ok
    assert "handwave" in out or "UNKNOWN" in out


# ---------------------------------------------------------------------------
# Lock toggle
# ---------------------------------------------------------------------------


def test_check_skipped_when_lock_disables(gate_module, tmp_path, capsys):
    """Lockfile flag stereo_annotations_required=false short-circuits the
    check entirely (backward compat with pre-#36 lockfiles)."""
    ok = gate_module.check_stereo_annotations({"rule_library": {}})
    out = capsys.readouterr().out
    assert ok
    assert "not required by lockfile" in out


# ---------------------------------------------------------------------------
# Live rule library — the 13 shipped rules must all parse and pass.
# ---------------------------------------------------------------------------


def test_live_rule_library_passes_stereo_policy_check(monkeypatch, capsys):
    """End-to-end: load scripts/pre_m5_gate.py against the real repo root
    and run the stereo-policy check on the 13 shipped rules. All 13 must
    declare a treatment and pass."""
    spec = importlib.util.spec_from_file_location("_pre_m5_gate_live", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    ok = mod.check_stereo_annotations(LOCK_REQUIRING_STEREO)
    out = capsys.readouterr().out
    assert ok, out
    # Sanity: at least the three known advisory_only rules should be reported.
    for rid in ("rcm", "hwe_olefination", "biaryl_etherification"):
        assert rid in out
