#!/usr/bin/env python
"""Pre-M5 gate.

Run before invoking the ascomylactam A run. Exits 0 only if every check
passes. Any non-zero exit means the M5 run should not proceed —
something is incomplete or out of sync with the pre-registration.

The gate's nine checks correspond 1:1 with the lockfile + plan.
See ~/.claude/plans/think-extremely-carefully-and-composed-widget.md
'Pre-M5 gate' section.

Usage:
    pixi run python scripts/pre_m5_gate.py
    pixi run python scripts/pre_m5_gate.py --lockfile data/pre_registration.lock.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


def _check(name: str, ok: bool, detail: str = "") -> bool:
    mark = "PASS" if ok else "FAIL"
    line = f"[{mark}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    return ok


def check_ascomylactam_target(lock: dict) -> bool:
    p = REPO_ROOT / "data" / "targets" / "ascomylactam_a"
    structure = p / "structure.mol"
    perimeter = p / "ring_perimeter.txt"
    notes = p / "notes.md"
    ok = structure.exists() and perimeter.exists() and notes.exists()
    if ok and "Ivan-signed" not in notes.read_text():
        ok = False
        detail = "notes.md present but missing 'Ivan-signed' marker"
    else:
        detail = "structure + perimeter + signed notes present" if ok else "missing artifacts"
    return _check("ascomylactam target encoded + signed", ok, detail)


def check_panel(lock: dict) -> bool:
    panel_dir = REPO_ROOT / "data" / "validation_panel"
    cases = [d for d in panel_dir.iterdir() if d.is_dir()]
    min_count = lock.get("panel", {}).get("min_case_count", 10)
    min_rate = lock.get("panel", {}).get("min_pass_rate", 0.80)

    if len(cases) < min_count:
        return _check("panel size", False, f"{len(cases)} < {min_count}")

    # Run panel tests
    result = subprocess.run(
        ["pixi", "run", "pytest", "tests/panel/", "-q", "--tb=no"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    # crude parse: count passed / total
    # On exit 0, all pass. On other, compute rate from "X passed, Y failed".
    output = result.stdout + result.stderr
    passed = sum(1 for line in output.splitlines() if " PASSED" in line or "passed" in line.lower())
    # Better: parse the summary line. For now, require all pass when min_rate is high.
    if result.returncode == 0:
        return _check("panel pass rate", True, f"{len(cases)} cases, all pass")
    return _check("panel pass rate", False, f"non-zero pytest exit; rate < {min_rate}")


def check_rule_library(lock: dict) -> bool:
    rules_dir = REPO_ROOT / "data" / "rules"
    gmls = list(rules_dir.glob("*.gml"))
    min_tactics = lock.get("rule_library", {}).get("min_tactic_count", 5)
    if len(gmls) < min_tactics:
        return _check("rule library size", False, f"{len(gmls)} < {min_tactics}")

    result = subprocess.run(
        ["pixi", "run", "python", "-m", "macrocert.cli", "check-rules", "data/rules"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    ok = result.returncode == 0
    return _check("rule library conservation", ok,
                  f"{len(gmls)} rules, check-rules {'green' if ok else 'failed'}")


def check_strategy_predicates(lock: dict) -> bool:
    """Every panel runspec must opt-in to required predicates.

    Accepts either of the two YAML shapes the runspec loader supports:
      strategy:
        predicates:
          is_intramolecular: true
          ring_size_equals: 13
    or
      strategy_predicates:
        is_intramolecular: true
        ring_size_equals: 13

    Placeholder-MOL cases (literature panel awaiting Ivan's CIF) are
    excluded — they're scaffolded and will receive predicates once the
    structure is provided.
    """
    panel_dir = REPO_ROOT / "data" / "validation_panel"
    required = {k for k, v in lock.get("strategy_predicates", {}).items() if v == "required"}
    if not required:
        return _check("strategy predicates", True, "no required predicates")

    missing = []
    for case in panel_dir.iterdir():
        if not case.is_dir():
            continue
        runspec = case / "runspec.yaml"
        if not runspec.exists():
            continue
        # Skip placeholder-structure cases (they will be re-spec'd after CIF lands).
        mol = case / "structure.mol"
        if mol.exists() and mol.read_text(encoding="utf-8", errors="replace").lstrip().startswith("# PLACEHOLDER"):
            continue
        spec = yaml.safe_load(runspec.read_text()) or {}
        predicates = (
            spec.get("strategy_predicates", {})
            or (spec.get("strategy", {}) or {}).get("predicates", {})
            or {}
        )
        for r in required:
            if r not in predicates:
                missing.append(f"{case.name}: missing {r}")
    ok = not missing
    return _check("strategy predicates in panel runspecs", ok,
                  f"{len(missing)} missing" if missing else "all opt-in")


def check_stereo_annotations(lock: dict) -> bool:
    if not lock.get("rule_library", {}).get("stereo_annotations_required", False):
        return _check("stereo annotations", True, "not required by lockfile")
    rules_dir = REPO_ROOT / "data" / "rules"
    missing = []
    for gml in rules_dir.glob("*.gml"):
        body = gml.read_text()
        # Heuristic: at least one stereo annotation present
        if "stereo" not in body:
            missing.append(gml.name)
    ok = not missing
    return _check("stereo annotations present", ok,
                  f"{', '.join(missing)} lack stereo" if missing else "all rules annotated")


def check_energetics_protocol(lock: dict) -> bool:
    proto = REPO_ROOT / "data" / "energetics_protocol.yaml"
    if not proto.exists():
        return _check("energetics protocol", False, "data/energetics_protocol.yaml absent")

    # Verify TS-search worked example wrote a real barrier
    cert = REPO_ROOT / "artifacts" / "toy_macrolactam_energetics" / "certificate.json"
    if not cert.exists():
        return _check("energetics protocol", False, "no toy_macrolactam_energetics certificate")
    data = json.loads(cert.read_text())
    barrier = data.get("energetics_dependencies", {}).get("worked_example_barrier_kcal_per_mol")
    if barrier is None:
        return _check("energetics protocol TS example", False, "barrier_kcal_per_mol is None")
    return _check("energetics protocol", True, f"barrier = {barrier:.1f} kcal/mol")


def check_adversarial_verifier(lock: dict) -> bool:
    min_tests = lock.get("verifier", {}).get("adversarial_test_count_min", 6)
    test_file = REPO_ROOT / "tests" / "verifier" / "test_adversarial.py"
    if not test_file.exists():
        return _check("adversarial verifier suite", False, "test file missing")
    body = test_file.read_text()
    test_count = sum(1 for line in body.splitlines() if line.strip().startswith("def test_"))
    if test_count < min_tests:
        return _check("adversarial verifier suite size", False,
                      f"{test_count} < {min_tests}")
    result = subprocess.run(
        ["pixi", "run", "pytest", "tests/verifier/test_adversarial.py", "-q"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return _check("adversarial verifier suite", result.returncode == 0,
                  f"{test_count} tests, exit {result.returncode}")


def check_reproducibility_hash(lock: dict) -> bool:
    """Two consecutive runs of toy_macrolactam must produce identical certificate hashes.

    Since Workstream F #43 this check is backed by deterministic
    seed-pinning: ``macrocert.generate.build_dg.build_dg_for_runspec``
    calls ``mod.rngReseed(MACROCERT_MOD_SEED or 0xC0FFEE)`` at the start
    of every invocation, plus seeds Python's ``random`` + NumPy globals.
    The check is considerably more robust on larger campaigns
    (lactam_12/14/16, ascomylactam, vancomycin) than it used to be when
    only the toy fixture happened to be deterministic by accident.
    Detailed regression coverage lives in
    ``tests/integration/test_campaign_reproducibility.py``.
    """
    cmd = ["pixi", "run", "python", "-m", "macrocert.cli", "run",
           "data/targets/toy_macrolactam"]
    cert_path = REPO_ROOT / "artifacts" / "toy_macrolactam" / "certificate.json"
    if not cert_path.exists():
        subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if not cert_path.exists():
        return _check("reproducibility hash", False, "first run did not emit certificate")
    h1 = hashlib.sha256(cert_path.read_bytes()).hexdigest()
    subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    h2 = hashlib.sha256(cert_path.read_bytes()).hexdigest()
    ok = h1 == h2
    return _check("reproducibility hash", ok,
                  f"{h1[:8]} = {h2[:8]}" if ok else f"{h1[:8]} != {h2[:8]}")


def check_pre_registration_signed(lock: dict, lock_path: Path) -> bool:
    signed_by = lock.get("signed_by")
    locked_at = lock.get("locked_at")
    ok = bool(signed_by) and bool(locked_at)
    return _check("pre-registration signed", ok,
                  f"signed_by={signed_by!r} locked_at={locked_at!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lockfile",
        default=str(REPO_ROOT / "data" / "pre_registration.lock.yaml"),
        help="Path to pre-registration lockfile (default: data/pre_registration.lock.yaml)",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Report all check results but still exit 0 if any fail. For dry-run diagnostics.",
    )
    args = parser.parse_args()

    lock_path = Path(args.lockfile)
    if not lock_path.exists():
        print(f"[FAIL] lockfile missing: {lock_path}")
        print(
            "       Copy data/pre_registration.template.yaml to "
            "data/pre_registration.lock.yaml, fill in values, sign, then re-run."
        )
        return 2
    lock = yaml.safe_load(lock_path.read_text()) or {}

    print(f"Pre-M5 gate — lockfile: {lock_path}\n")

    checks = [
        ("pre-registration signed", lambda: check_pre_registration_signed(lock, lock_path)),
        ("ascomylactam target", lambda: check_ascomylactam_target(lock)),
        ("panel", lambda: check_panel(lock)),
        ("rule library", lambda: check_rule_library(lock)),
        ("strategy predicates", lambda: check_strategy_predicates(lock)),
        ("stereo annotations", lambda: check_stereo_annotations(lock)),
        ("energetics protocol", lambda: check_energetics_protocol(lock)),
        ("adversarial verifier", lambda: check_adversarial_verifier(lock)),
        ("reproducibility hash", lambda: check_reproducibility_hash(lock)),
    ]
    results = [(name, fn()) for name, fn in checks]
    print()
    failed = [name for name, ok in results if not ok]
    if failed:
        print(f"Pre-M5 gate FAILED ({len(failed)}/{len(results)} checks failed):")
        for f in failed:
            print(f"  - {f}")
        return 0 if args.allow_partial else 1
    print("Pre-M5 gate PASSED — ascomylactam A run may proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
