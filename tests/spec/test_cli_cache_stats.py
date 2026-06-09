"""Tests for the `macrocert cache-stats` CLI subcommand.

Exercises both the reporting path (no-flag) and the --purge-tier path
on a temporary cache layout. Avoids the real .cache/ directory by
running each test in tmp_path.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(*argv: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "macrocert.cli", "cache-stats", *argv],
        cwd=cwd, capture_output=True, text=True,
    )


def _seed_caches(root: Path) -> None:
    """Create a synthetic cache layout under ``root`` matching the real
    EnergeticsCache + TSCache directory structure + JSON schemas."""
    (root / ".cache/energetics/v2").mkdir(parents=True, exist_ok=True)
    (root / ".cache/ts/v1").mkdir(parents=True, exist_ok=True)

    # 2 energetics entries (xtb + dft) and 1 TS entry (xtb)
    (root / ".cache/energetics/v2/abc.json").write_text(json.dumps({
        "tier": "xtb", "method": "GFN2-xTB", "dG_kcal_per_mol": 5.0,
        "rule_id": "macrolactamization",
        "reactant_smiles": ["A"], "product_smiles": ["B"],
    }))
    (root / ".cache/energetics/v2/def.json").write_text(json.dumps({
        "tier": "dft", "method": "B3LYP", "dG_kcal_per_mol": 6.0,
        "rule_id": "macrolactamization",
        "reactant_smiles": ["A"], "product_smiles": ["B"],
    }))
    (root / ".cache/ts/v1/ghi.json").write_text(json.dumps({
        "tier": "xtb", "method": "GFN2-xTB",
        "workflow": "worked_example",
        "substrate_id": "nh3", "optimizer_fingerprint": "fp",
        "result": {
            "barrier_kcal_per_mol": 6.11,
            "e_reactant_ev": -120.0, "e_product_ev": -120.0, "e_ts_ev": -119.8,
            "n_neb_images": 0, "n_sella_iterations": 42,
            "converged": True, "method": "GFN2-xTB",
            "provenance": "test", "cache_key": "ghi",
        },
    }))


def test_cache_stats_reports_both_caches(tmp_path):
    _seed_caches(tmp_path)
    result = _run_cli(cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "energetics" in out
    assert "TS-search" in out
    assert "2 entries" in out          # the two ΔG entries
    assert "1 entries" in out          # the one TS entry


def test_cache_stats_reports_missing_caches_cleanly(tmp_path):
    result = _run_cli(cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "no cache directory" in result.stdout


def test_purge_tier_xtb_drops_only_xtb(tmp_path):
    _seed_caches(tmp_path)
    result = _run_cli("--purge-tier", "xtb", cwd=tmp_path)
    assert result.returncode == 0
    assert "purged 2 entries" in result.stdout

    # dft entry is the only survivor
    remaining = list((tmp_path / ".cache").rglob("*.json"))
    assert len(remaining) == 1
    assert json.loads(remaining[0].read_text())["tier"] == "dft"


def test_purge_tier_unknown_value_rejected(tmp_path):
    _seed_caches(tmp_path)
    result = _run_cli("--purge-tier", "vibes", cwd=tmp_path)
    assert result.returncode != 0
    assert "invalid choice" in result.stderr or "argument" in result.stderr
