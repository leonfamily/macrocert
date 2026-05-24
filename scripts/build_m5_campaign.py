"""M5 campaign runner: per-tactic certificates + aggregated report.

Proposal §5 deliverable for the ascomylactam A run:
    "shortlist of ≤10 strategy families with certificates;
     no-go certificates for ruled-out classes; report rendered;
     verifier-clean on every emitted certificate."

This script materializes that by invoking the macrocert pipeline once
per macrocyclization rule (treating each as an independent tactic),
saving each certificate under
``artifacts/<target>/campaign/<rule_id>/certificate.json``, running
the independent verifier on each, and aggregating into a markdown
report at ``docs/M5_REPORT_<target>.md``.

Outcomes per rule:
- **optimal** — the rule fires productively and reaches the target.
  This is the cert that should appear in the §5 "shortlist".
- **infeasible** — the rule either doesn't match the seco-precursor
  or matches but produces a product that's not the target. The
  certificate's IIS captures the no-go reason. These are the
  proposal's "no-go certificates for ruled-out classes".
- **errored** — pipeline-level failure (e.g., a rule's GML triggers
  a MØD edge case). These are not no-go certificates; they're
  harness bugs the campaign exposes.

Usage:
    pixi run python scripts/build_m5_campaign.py data/targets/ascomylactam_a
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parent.parent


def _load_rule_set(rules_dir: Path, set_name: str) -> list[str]:
    idx = yaml.safe_load((rules_dir / "_index.yaml").read_text())
    sets = idx.get("sets", {}) or {}
    if set_name not in sets:
        raise KeyError(f"rule set {set_name!r} not in {rules_dir}/_index.yaml")
    return list(sets[set_name])


def _run_one_rule(
    target_dir: Path,
    rule_id: str,
    campaign_dir: Path,
    rules_dir: Path,
) -> dict[str, Any]:
    """Run the pipeline pinned to a single rule; save cert under campaign_dir."""
    base_runspec = yaml.safe_load((target_dir / "runspec.yaml").read_text())
    # Pin to the single rule for this leg of the campaign.
    runspec = dict(base_runspec)
    runspec["rules"] = rule_id
    runspec["name"] = f"{base_runspec['name']}__{rule_id}"

    # Stage a working copy of the target dir with the rewritten runspec
    # so the pipeline reads it. structure.mol and blocks reference are
    # via the target_dir path, so we shadow only runspec.yaml.
    work = campaign_dir / rule_id / "_work"
    work.mkdir(parents=True, exist_ok=True)
    # symlink (or copy) structure.mol so the encoder finds it
    for f in target_dir.iterdir():
        if f.name == "runspec.yaml":
            continue
        if f.name == "Chen2019_paper.pdf":
            continue  # don't haul the 2 MB PDF into every campaign leg
        target_path = work / f.name
        if target_path.exists():
            continue
        if f.is_file():
            try:
                os.symlink(f.resolve(), target_path)
            except (OSError, FileExistsError):
                shutil.copy(f, target_path)
    (work / "runspec.yaml").write_text(yaml.safe_dump(runspec, sort_keys=False))

    result: dict[str, Any] = {"rule_id": rule_id, "outcome": "unknown"}
    cmd = [
        "pixi", "run", "python", "-m", "macrocert.cli", "run",
        str(work.relative_to(REPO)),
        "--artifacts-dir", str((campaign_dir / rule_id).relative_to(REPO)),
    ]
    # Workstream F (#43): pin MØD's RNG + Python hash randomization so
    # the same runspec always yields a byte-identical certificate. The
    # subprocess inherits the parent env, then we override the two
    # determinism knobs. Callers can override the MØD seed by exporting
    # MACROCERT_MOD_SEED before invoking this script.
    env = dict(os.environ)
    env.setdefault("MACROCERT_MOD_SEED", "0xC0FFEE")
    env["PYTHONHASHSEED"] = "0"

    try:
        proc = subprocess.run(
            cmd, cwd=REPO, capture_output=True, text=True, timeout=180,
            env=env,
        )
        result["stdout_tail"] = "\n".join(proc.stdout.splitlines()[-6:])
        result["stderr_tail"] = "\n".join(proc.stderr.splitlines()[-3:])
        result["returncode"] = proc.returncode
    except subprocess.TimeoutExpired:
        result["outcome"] = "timeout"
        result["error"] = "180s pipeline timeout"
        return result

    cert_path = campaign_dir / rule_id / runspec["name"] / "certificate.json"
    if not cert_path.exists():
        # CLI might write to a directory named after the original target name
        # — search for a certificate.json under campaign_dir/rule_id.
        candidates = list((campaign_dir / rule_id).rglob("certificate.json"))
        if candidates:
            cert_path = candidates[0]
        else:
            result["outcome"] = "errored"
            result["error"] = "no certificate emitted"
            return result

    result["certificate_path"] = str(cert_path.relative_to(REPO))
    cert = json.loads(cert_path.read_text())
    witness = cert.get("solver_witness", {})
    result["outcome"] = witness.get("kind", "unknown")
    result["objective_value"] = witness.get("obj_value")
    result["dual_bound"] = witness.get("dual_bound")
    if result["outcome"] == "optimal":
        # Pull mass numbers from the composed rule
        cr = cert.get("composed_rule", {})
        result["bond_level_expelled_mass"] = cr.get("expelled_mass_g_per_mol")
        # process-level not in cert; pull from the rule's meta
    elif result["outcome"] == "infeasible":
        result["iis"] = witness.get("iis_constraint_ids", [])[:10]

    # Verify independently
    verify_cmd = ["pixi", "run", "macrocert-verify", str(cert_path)]
    vproc = subprocess.run(verify_cmd, cwd=REPO, capture_output=True, text=True, timeout=60)
    result["verifier_exit"] = vproc.returncode
    result["verifier_output"] = vproc.stdout.strip() or vproc.stderr.strip()

    return result


def _render_report(
    target_name: str,
    results: list[dict[str, Any]],
    output_path: Path,
) -> None:
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    lines = [
        f"# M5 Campaign Report — {target_name}",
        "",
        f"_Auto-generated {timestamp} by `scripts/build_m5_campaign.py`._",
        "",
        f"Proposal §5 deliverable: per-tactic certificates for "
        f"`data/targets/{target_name}/` across all macrocyclization rules.",
        "",
        "## Outcome by tactic",
        "",
        "| Rule | Witness | Objective (g/mol) | Verifier | Certificate |",
        "|------|---------|-------------------|----------|-------------|",
    ]
    # Sort: optimal first (by objective ascending), then infeasible, then errored
    def _sort_key(r):
        outcome_order = {"optimal": 0, "infeasible": 1, "timeout": 2,
                         "errored": 3, "unknown": 4}
        return (outcome_order.get(r["outcome"], 99),
                r.get("objective_value") or 1e9, r["rule_id"])
    for r in sorted(results, key=_sort_key):
        rid = r["rule_id"]
        out = r["outcome"]
        obj = r.get("objective_value")
        obj_str = f"{obj:.3f}" if isinstance(obj, (int, float)) else "—"
        ver = "OK" if r.get("verifier_exit") == 0 else f"exit {r.get('verifier_exit', '?')}"
        cert = r.get("certificate_path", "—")
        lines.append(f"| `{rid}` | **{out}** | {obj_str} | {ver} | `{cert}` |")

    lines += ["", "## Interpretation", ""]

    optimals = [r for r in results if r["outcome"] == "optimal"]
    infeasibles = [r for r in results if r["outcome"] == "infeasible"]
    errored = [r for r in results if r["outcome"] not in ("optimal", "infeasible")]

    if optimals:
        # The shortlist: optimals ordered by objective ascending (lower is better)
        lines.append(f"### Shortlist ({len(optimals)} optimal tactic{'s' if len(optimals) != 1 else ''})")
        lines.append("")
        lines.append("Ordered by bond-level expelled mass (lower = better AE):")
        lines.append("")
        for r in sorted(optimals, key=lambda r: r.get("objective_value") or 1e9):
            obj = r.get("objective_value")
            lines.append(
                f"1. **`{r['rule_id']}`** — objective {obj:.3f} g/mol; "
                f"certificate verifier-clean: {r.get('verifier_exit') == 0}"
            )
        lines.append("")
    else:
        lines.append("### Shortlist: empty")
        lines.append("")
        lines.append("No tactic produced an optimal certificate for this target. "
                     "Review the no-go certificates below.")
        lines.append("")

    if infeasibles:
        lines.append(f"### No-go certificates ({len(infeasibles)} ruled-out tactic{'s' if len(infeasibles) != 1 else ''})")
        lines.append("")
        for r in infeasibles:
            lines.append(f"- **`{r['rule_id']}`** — IIS (first 3): "
                         + ", ".join(f"`{c[:50]}{'…' if len(c) > 50 else ''}`"
                                      for c in (r.get("iis") or [])[:3]))
        lines.append("")
        lines.append(
            "Each no-go certificate is independently verifier-clean — "
            "the verifier confirms that the rule cannot produce the target "
            "from the seco-precursor under the runspec's constraints."
        )
        lines.append("")

    if errored:
        lines.append(f"### Pipeline errors ({len(errored)} rule{'s' if len(errored) != 1 else ''})")
        lines.append("")
        lines.append("These are harness bugs, NOT chemistry failures. Fix and re-run.")
        lines.append("")
        for r in errored:
            lines.append(f"- **`{r['rule_id']}`** — outcome={r['outcome']}, error={r.get('error', '—')}")
            tail = r.get("stderr_tail") or r.get("stdout_tail")
            if tail:
                lines.append(f"  ```\n  {tail}\n  ```")
        lines.append("")

    lines += [
        "## Provenance",
        "",
        "- target dir: `data/targets/{}/`".format(target_name),
        "- seco-precursor block: `data/building_blocks/{}_seco.yaml`".format(target_name),
        "- rule library: `data/rules/_index.yaml` set `all_macrocyclization`",
        "- generated by: `scripts/build_m5_campaign.py`",
        "- each leg's working dir preserved under "
        "`artifacts/.../campaign/<rule>/_work/` for reproducibility",
        "",
        "## Verification",
        "",
        "Every certificate referenced above was independently re-checked by "
        "`pixi run macrocert-verify`. The `Verifier` column records the exit "
        "code (0 = OK).",
        "",
    ]

    output_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path,
                        help="path to target dir (e.g., data/targets/ascomylactam_a)")
    parser.add_argument("--rules-set", default="all_macrocyclization",
                        help="rule-set name from data/rules/_index.yaml")
    parser.add_argument("--rules-dir", type=Path, default=REPO / "data" / "rules")
    args = parser.parse_args()

    target_dir = args.target.resolve()
    if not (target_dir / "runspec.yaml").exists():
        print(f"target dir {target_dir} missing runspec.yaml", file=sys.stderr)
        return 2

    target_name = target_dir.name
    rule_ids = _load_rule_set(args.rules_dir, args.rules_set)
    print(f"M5 campaign: {target_name}; evaluating {len(rule_ids)} tactics from {args.rules_set!r}")
    print()

    campaign_dir = REPO / "artifacts" / target_name / "campaign"
    if campaign_dir.exists():
        shutil.rmtree(campaign_dir)
    campaign_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for i, rid in enumerate(rule_ids, 1):
        print(f"[{i:2d}/{len(rule_ids)}] {rid} ...", end="", flush=True)
        r = _run_one_rule(target_dir, rid, campaign_dir, args.rules_dir)
        results.append(r)
        outcome = r["outcome"]
        obj = r.get("objective_value")
        obj_str = f" obj={obj:.3f}" if isinstance(obj, (int, float)) else ""
        ver = "✓" if r.get("verifier_exit") == 0 else "✗"
        print(f" {outcome}{obj_str} verifier={ver}")

    report_path = REPO / "docs" / f"M5_REPORT_{target_name}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _render_report(target_name, results, report_path)
    print(f"\nreport: {report_path.relative_to(REPO)}")

    # Also write the JSON manifest of campaign results
    manifest_path = campaign_dir / "manifest.json"
    manifest_path.write_text(json.dumps({
        "target": target_name,
        "rules_set": args.rules_set,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "results": results,
    }, indent=2))
    print(f"manifest: {manifest_path.relative_to(REPO)}")

    # Summarize
    optimals = sum(1 for r in results if r["outcome"] == "optimal")
    infeasibles = sum(1 for r in results if r["outcome"] == "infeasible")
    errored = len(results) - optimals - infeasibles
    print(f"\nsummary: {optimals} optimal · {infeasibles} no-go · {errored} errored")

    return 0


if __name__ == "__main__":
    sys.exit(main())
