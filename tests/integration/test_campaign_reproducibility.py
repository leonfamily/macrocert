"""Byte-determinism of pipeline-emitted certificates — Workstream F (#43).

The proposal §6 reproducibility-rigor mechanism says: re-running
``pixi run python -m macrocert.cli run data/targets/toy_macrolactam`` must
produce a byte-identical certificate (modulo timestamps).

The pre-M5 gate's ``check_reproducibility_hash`` enforces this on
``toy_macrolactam`` alone, but only because that target produces a
single trivial route. Larger panel cases (lactam_12/14/16,
vancomycin, ascomylactam) previously had no determinism guarantee.

These tests exercise determinism at two scales:

1. ``toy_macrolactam`` — the smallest fixture, sanity-checks the
   seed-pinning plumbing in
   ``macrocert.generate.build_dg.build_dg_for_runspec``.
2. ``lactam_12_from_11_aminoundecanoic_acid`` — a real panel case,
   confirms determinism survives the predicate-augmented strategy
   path. (Per ``docs/erythronolide_b_m5.md`` §6, MØD's
   geometry-finalization is the historical flakiness culprit; this
   test guards against regression.)

Why subprocess rather than in-process invocation:

MØD assigns each ``mod.DG`` instance a process-global ID
(``mod::lib::DG::NonHyper::getId()``) and embeds it in created-graph
labels (``"p_{<dgId>,<n>}"`` — see
``external/mod/libs/libmod/src/mod/lib/DG/NonHyper.cpp:162``). The ID
counter restarts at 0 every process but not every DG instantiation,
so two ``pipeline.run`` calls in one Python process would emit
``p_{0,*}`` then ``p_{1,*}`` and trivially fail byte-equality. The
proposal §6 contract is over subprocess invocations
(``pixi run python -m macrocert.cli run …`` re-run), which is what we
test here, and what CI / the pre-M5 gate actually does.

Both tests assume ``mod.rngReseed`` is called at the start of every
``build_dg_for_runspec`` invocation (the seed-pinning hook); the
default seed is ``0xC0FFEE`` and can be overridden via the
``MACROCERT_MOD_SEED`` env var.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _normalize_cert(cert: dict) -> dict:
    """Strip timestamp-like fields so byte-comparison is meaningful.

    The certificate carries provenance metadata (e.g., wall-clock
    solver-start times) that legitimately varies run-to-run. We only
    want to assert the *content* — derivation graph, flow, IIS,
    composed rule — is byte-identical.
    """
    redacted = json.loads(json.dumps(cert))  # deep copy
    prov = redacted.get("provenance", {}) or {}
    for key in (
        "timestamp", "started_at", "finished_at", "elapsed_s",
        "wall_clock_s", "solver_wall_clock_s",
    ):
        prov.pop(key, None)
    redacted["provenance"] = prov
    witness = redacted.get("solver_witness", {}) or {}
    for key in ("elapsed_s", "solve_time_s", "wall_clock_s"):
        witness.pop(key, None)
    redacted["solver_witness"] = witness
    return redacted


def _hash_cert(cert_path: Path) -> str:
    cert = json.loads(cert_path.read_text())
    norm = _normalize_cert(cert)
    blob = json.dumps(norm, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _seeded_env() -> dict[str, str]:
    env = dict(os.environ)
    env["MACROCERT_MOD_SEED"] = "0xC0FFEE"
    env["PYTHONHASHSEED"] = "0"
    return env


def _run_pipeline_subprocess(target_dir: Path, artifacts_dir: Path) -> Path:
    """Invoke the CLI as a fresh subprocess; return the cert path."""
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "macrocert.cli", "run",
        str(target_dir),
        "--artifacts-dir", str(artifacts_dir),
    ]
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True,
        env=_seeded_env(), timeout=180,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"pipeline subprocess exited {proc.returncode} for {target_dir}\n"
            f"stdout tail:\n{proc.stdout[-1000:]}\n"
            f"stderr tail:\n{proc.stderr[-1000:]}"
        )
    candidates = sorted(artifacts_dir.rglob("certificate.json"))
    if not candidates:
        pytest.fail(
            f"no certificate.json under {artifacts_dir} after run; "
            f"stdout tail:\n{proc.stdout[-500:]}"
        )
    return candidates[0]


def _has_target_dir(rel_path: str) -> bool:
    return (REPO_ROOT / rel_path / "runspec.yaml").exists()


@pytest.mark.skipif(
    not _has_target_dir("data/targets/toy_macrolactam"),
    reason="data/targets/toy_macrolactam absent",
)
def test_toy_macrolactam_is_byte_deterministic(tmp_path: Path) -> None:
    """Two consecutive subprocess runs of toy_macrolactam emit identical certs.

    Mirrors the proposal §6 reproducibility-rigor mechanism literally:
    re-running ``python -m macrocert.cli run data/targets/toy_macrolactam``
    must produce a byte-identical certificate (modulo timestamps).
    """
    target = Path("data/targets/toy_macrolactam")
    cert1 = _run_pipeline_subprocess(target, tmp_path / "run1")
    cert2 = _run_pipeline_subprocess(target, tmp_path / "run2")
    h1 = _hash_cert(cert1)
    h2 = _hash_cert(cert2)
    assert h1 == h2, (
        f"toy_macrolactam certificate hash drifted across consecutive "
        f"subprocess runs: {h1} != {h2}. Workstream F #43 seed-pinning has "
        f"regressed; check mod.rngReseed call in macrocert.generate.build_dg "
        f"and diff {cert1} vs {cert2}."
    )


@pytest.mark.skipif(
    not _has_target_dir("data/validation_panel/lactam_12_from_11_aminoundecanoic_acid"),
    reason="panel case lactam_12_from_11_aminoundecanoic_acid absent",
)
def test_panel_lactam_12_is_byte_deterministic(tmp_path: Path) -> None:
    """Two consecutive subprocess runs of lactam_12 emit identical certs.

    This is the smallest "real" panel case (11-aminoundecanoic acid →
    12-membered lactam, single macrolactamization tactic). If MØD's RNG
    leaks into the cert here, larger campaigns (ascomylactam, vancomycin,
    erythronolide B) will leak too — this case is the canary.
    """
    target = Path("data/validation_panel/lactam_12_from_11_aminoundecanoic_acid")
    cert1 = _run_pipeline_subprocess(target, tmp_path / "run1")
    cert2 = _run_pipeline_subprocess(target, tmp_path / "run2")
    h1 = _hash_cert(cert1)
    h2 = _hash_cert(cert2)
    assert h1 == h2, (
        f"lactam_12 certificate hash drifted across consecutive subprocess "
        f"runs: {h1} != {h2}. Investigate the cert diff between {cert1} and "
        f"{cert2}; this is the canary for ascomylactam / vancomycin determinism."
    )


def test_mod_seed_env_var_is_honoured(monkeypatch) -> None:
    """``MACROCERT_MOD_SEED`` overrides the default 0xC0FFEE.

    Pure-unit check that does not invoke MØD — guards the env-var
    parsing in ``macrocert.generate.build_dg._resolve_mod_seed``.
    """
    from macrocert.generate import build_dg as bd

    monkeypatch.setenv("MACROCERT_MOD_SEED", "0xDEADBEEF")
    assert bd._resolve_mod_seed() == 0xDEADBEEF

    monkeypatch.setenv("MACROCERT_MOD_SEED", "42")
    assert bd._resolve_mod_seed() == 42

    monkeypatch.delenv("MACROCERT_MOD_SEED", raising=False)
    assert bd._resolve_mod_seed() == 0xC0FFEE

    monkeypatch.setenv("MACROCERT_MOD_SEED", "not-a-number")
    with pytest.raises(ValueError, match="MACROCERT_MOD_SEED"):
        bd._resolve_mod_seed()
