"""Validation-panel test runner — M4.

Iterates every directory under data/validation_panel/ that contains a
runspec.yaml and expected.yaml. For each case, invokes pipeline.run
and asserts the literature outcome.

Pass policy: per the plan, ≥ 80% of cases pass. Individual failures
are diagnosed via the REPORT.md taxonomy (rule-library gap, strategy
gap, τ miscalibration).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml


PANEL_ROOT = Path("data/validation_panel")


def _discover_cases() -> list[Path]:
    cases: list[Path] = []
    if not PANEL_ROOT.is_dir():
        return cases
    for d in sorted(PANEL_ROOT.iterdir()):
        if d.is_dir() and (d / "runspec.yaml").exists() and (d / "expected.yaml").exists():
            cases.append(d)
    return cases


@dataclass
class PanelCase:
    path: Path
    expected: dict

    @property
    def name(self) -> str:
        return self.path.name


def _load_expected(case_dir: Path) -> dict:
    return yaml.safe_load((case_dir / "expected.yaml").read_text())


def _is_placeholder_structure(case_dir: Path) -> bool:
    """Detect Workstream B placeholder MOL files awaiting Ivan's CIF audit.

    The first three literature panel cases (vancomycin, epothilone B,
    citreoviridin) ship a structure.mol that is explicitly a
    placeholder — the file's first line is ``# PLACEHOLDER`` per the
    Workstream B agent's contract. These cases skip until Ivan
    encodes the real structure from CIF / institutional access.
    """
    mol = case_dir / "structure.mol"
    if not mol.exists():
        return True
    try:
        head = mol.read_text(encoding="utf-8", errors="replace").lstrip()[:64]
    except OSError:
        return True
    return head.startswith("# PLACEHOLDER")


@pytest.mark.parametrize("case_dir", _discover_cases(), ids=lambda p: p.name)
def test_panel_case(case_dir: Path) -> None:
    from macrocert.pipeline import run

    expected = _load_expected(case_dir)

    # Workstream B added literature cases with placeholder MOL files
    # awaiting Ivan's CIF audit (Chen 2019 / Nicolaou 1997 / Boger 1999).
    # Skip until real structures land; the case stays in the panel as a
    # placeholder visible to the reviewer.
    skip_reason = expected.get("skip")
    if skip_reason or _is_placeholder_structure(case_dir):
        pytest.skip(skip_reason or f"{case_dir.name}: structure.mol is a placeholder awaiting Ivan's CIF audit")

    report = run(case_dir, artifacts_dir="artifacts/panel")
    assert report.witness_kind == expected["expected_witness"], (
        f"{case_dir.name}: witness mismatch — got {report.witness_kind}, "
        f"expected {expected['expected_witness']}"
    )

    if expected["expected_witness"] == "optimal":
        cert = json.loads(report.certificate_path.read_text())
        used_edges = [
            cert["derivation_graph"]["hyperedges"][i]
            for i, e in enumerate(cert["derivation_graph"]["hyperedges"])
            if e["id"] in cert["flow"] and cert["flow"][e["id"]] > 0
        ]
        used_rule_ids = {e["rule_id"] for e in used_edges}
        literature_tactic = expected["literature_tactic"]
        assert literature_tactic in used_rule_ids, (
            f"{case_dir.name}: literature tactic {literature_tactic!r} not in "
            f"top route's rules {used_rule_ids}"
        )
