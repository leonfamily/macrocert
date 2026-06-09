"""Command-line entry point for MØD-MacroCert.

Subcommands:
  check-rules <dir>           validate rule library (conservation per rule)
  encode-target <target_dir>  encode the target graph and emit perimeter audit
  run <runspec.yaml>          (M2+) end-to-end pipeline (placeholder in M1)
  verify <cert.json>          deferred to macrocert-verify entry point
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_check_rules(args: argparse.Namespace) -> int:
    from macrocert.spec import load_rule_library
    from macrocert.verifier.conservation import check_rule_conservation
    # Workstream F (Component 2): stereo conservation runs alongside
    # the existing element/charge balance check. See
    # docs/mod_stereo_reference.md §3.1 and
    # src/macrocert/verifier/stereo_conservation.py.
    from macrocert.verifier.stereo_conservation import (
        check_rule_stereo_conservation,
    )

    lib = load_rule_library(args.directory)
    if not lib.rules:
        print(f"no rules found in {args.directory}", file=sys.stderr)
        return 1

    failures = 0
    stereo_errors = 0
    stereo_warnings = 0
    stereo_infos = 0
    for rid, rule in lib.rules.items():
        result = check_rule_conservation(rule.gml)
        if result.ok:
            print(f"  OK  {rid:40s}  classes={list(rule.meta.classes)}")
        else:
            failures += 1
            print(f"  FAIL {rid:40s}  {result.reason}", file=sys.stderr)
        # Stereo pass: orthogonal to mass conservation. Errors are
        # treated as failures; warnings/infos are reported but do not
        # flip the exit code.
        for issue in check_rule_stereo_conservation(rule.gml):
            tag = {
                "error": "STEREO-ERROR",
                "warning": "STEREO-WARN",
                "info": "STEREO-INFO",
            }[issue.severity]
            stream = sys.stderr if issue.severity == "error" else sys.stdout
            print(f"  {tag} {rid:40s}  [{issue.code}] {issue.message}", file=stream)
            if issue.severity == "error":
                stereo_errors += 1
            elif issue.severity == "warning":
                stereo_warnings += 1
            else:
                stereo_infos += 1
    if failures or stereo_errors:
        if failures:
            print(f"\n{failures} rule(s) failed conservation re-check", file=sys.stderr)
        if stereo_errors:
            print(f"{stereo_errors} stereo conservation error(s)", file=sys.stderr)
        return 1
    summary = (
        f"\n{len(lib.rules)} rule(s) pass conservation re-check "
        f"(stereo: {stereo_warnings} warning(s), {stereo_infos} info(s))"
    )
    print(summary)
    return 0


def _cmd_encode_target(args: argparse.Namespace) -> int:
    from macrocert.spec.runspec import load_runspec
    from macrocert.spec.target import encode_target, write_perimeter_audit

    target_dir = Path(args.target_dir)
    spec = load_runspec(target_dir)
    structure = target_dir / spec.target.structure_path
    encoded = encode_target(
        structure,
        ring_size=spec.target.ring_size,
        name=spec.name,
    )
    audit_path = target_dir / "ring_perimeter.txt"
    write_perimeter_audit(encoded, audit_path)
    print(f"encoded {encoded.name}: {len(encoded.ring_atom_indices)}-membered ring "
          f"located; perimeter audit written to {audit_path}")
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    from macrocert.generate import build_dg_for_runspec
    from macrocert.spec.rules import load_rule_library
    from macrocert.spec.runspec import load_runspec

    target_dir = Path(args.target_dir)
    spec = load_runspec(target_dir)
    library = load_rule_library(args.rules_dir)
    result = build_dg_for_runspec(
        spec,
        library=library,
        blocks_dir=args.blocks_dir,
        target_dir=target_dir,
    )
    n_v = result.dg.numVertices
    n_e = result.dg.numEdges
    print(
        f"DG for {spec.name!r}: {n_v} molecules, {n_e} reactions  "
        f"(rules: {list(result.rules_used)}; blocks: {list(spec.blocks)})"
    )
    if args.dump_smiles:
        for v in result.dg.vertices:
            try:
                smi = v.graph.smiles
            except Exception:
                smi = "<no-smiles>"
            print(f"  v{v.id}: {smi}")
    if args.print_dg:
        result.dg.print()
        print(f"DG TeX/dot artifacts written under ./out/ (compile with `pixi run mod-shell mod_post`)")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    from macrocert.pipeline import run

    report = run(
        args.target_dir,
        rules_dir=args.rules_dir,
        blocks_dir=args.blocks_dir,
        artifacts_dir=args.artifacts_dir,
    )
    print(f"{report.spec.name}: witness={report.witness_kind}")
    if report.witness_kind == "optimal":
        print(f"  bond-level expelled mass:    {report.bond_level_expelled_mass:.2f} g/mol")
        print(f"  process-level expelled mass: {report.process_level_expelled_mass:.2f} g/mol")
    if report.energetics_summary:
        cs = report.energetics_summary.get("cache_stats", {})
        per_edge = report.energetics_summary.get("per_edge", {})
        print(f"  energetics: {len(per_edge)} edge(s) evaluated, "
              f"cache hits={cs.get('hits', 0)} misses={cs.get('misses', 0)}")
        for eid, ent in per_edge.items():
            dG = ent.get("dG_kcal_per_mol")
            print(f"    {eid}: tier={ent['tier']} ΔG={dG:+.2f} kcal/mol")
    print(f"  certificate: {report.certificate_path}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from macrocert.report import render_certificate

    for cert_path in args.certificates:
        md, html = render_certificate(Path(cert_path))
        print(f"  {md}")
        print(f"  {html}")
    return 0


def _cmd_cache_stats(args: argparse.Namespace) -> int:
    """Aggregate disk-cache stats; optionally purge by tier.

    Reports per-cache entry count, total disk usage, and most-recent
    last-modified for both content-addressed caches in the repo:

      .cache/energetics/<VERSION>/  — ΔG-rxn cache (cache.py)
      .cache/ts/<VERSION>/          — TS saddle cache (ts_cache.py)

    With --purge-tier <mlip|xtb|dft>, scans each cache for entries
    whose stored ``tier`` matches and deletes them. The cache-key
    schema includes the tier, so eviction is exact: no other tier's
    entries are touched.
    """
    import json
    import time
    from pathlib import Path

    cache_roots = [
        ("energetics (ΔG)", Path(".cache/energetics")),
        ("TS-search",       Path(".cache/ts")),
    ]

    if args.purge_tier:
        purged = _purge_tier(cache_roots, args.purge_tier)
        print(f"purged {purged} entries with tier={args.purge_tier!r}")
        return 0

    for label, root in cache_roots:
        if not root.exists():
            print(f"  {label}: (no cache directory yet at {root}/)")
            continue
        all_entries = sorted(root.rglob("*.json"))
        if not all_entries:
            print(f"  {label}: 0 entries under {root}/")
            continue
        total_bytes = sum(p.stat().st_size for p in all_entries)
        most_recent = max(p.stat().st_mtime for p in all_entries)
        # Per-version subdir breakdown — both caches use this layout.
        per_version: dict[str, int] = {}
        for p in all_entries:
            ver = p.parent.name if p.parent.parent == root else "(flat)"
            per_version[ver] = per_version.get(ver, 0) + 1
        ver_str = ", ".join(f"{n} in {ver}/" for ver, n in sorted(per_version.items()))
        print(
            f"  {label}: {len(all_entries)} entries  "
            f"({total_bytes / 1024:.1f} KB)  "
            f"last-modified {time.strftime('%Y-%m-%d %H:%M', time.localtime(most_recent))}  "
            f"[{ver_str}]"
        )
    return 0


def _purge_tier(cache_roots, tier: str) -> int:
    import json
    purged = 0
    for _label, root in cache_roots:
        if not root.exists():
            continue
        for p in root.rglob("*.json"):
            try:
                data = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            # Two cache schemas:
            #   EnergeticsCache:  {"tier": "...", ...}                    (cache.py CacheEntry)
            #   TSCache:          {"tier": "...", "result": {...}, ...}   (ts_cache.py TSCacheEntry)
            cache_tier = data.get("tier")
            if cache_tier == tier:
                p.unlink()
                purged += 1
    return purged


def _cmd_pareto(args: argparse.Namespace) -> int:
    from macrocert.report import render_pareto

    output = Path(args.output)
    out = render_pareto([Path(p) for p in args.certificates], output)
    if out:
        print(f"  {out}")
        return 0
    print("no optimal certificates among inputs; nothing to plot", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="macrocert")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_cr = sub.add_parser("check-rules", help="validate rule library")
    p_cr.add_argument("directory")
    p_cr.set_defaults(func=_cmd_check_rules)

    p_et = sub.add_parser("encode-target", help="encode target + emit perimeter audit")
    p_et.add_argument("target_dir")
    p_et.set_defaults(func=_cmd_encode_target)

    p_gen = sub.add_parser("generate", help="Layer B: build the DG only")
    p_gen.add_argument("target_dir")
    p_gen.add_argument("--rules-dir", default="data/rules")
    p_gen.add_argument("--blocks-dir", default="data/building_blocks")
    p_gen.add_argument("--dump-smiles", action="store_true")
    p_gen.add_argument("--print-dg", action="store_true",
                       help="emit dg/graph/rule TeX+dot under out/ (uses MØD's printing)")
    p_gen.set_defaults(func=_cmd_generate)

    p_run = sub.add_parser("run", help="A→B→C end-to-end with certificate emission")
    p_run.add_argument("target_dir")
    p_run.add_argument("--rules-dir", default="data/rules")
    p_run.add_argument("--blocks-dir", default="data/building_blocks")
    p_run.add_argument("--artifacts-dir", default="artifacts")
    p_run.set_defaults(func=_cmd_run)

    p_rep = sub.add_parser("report", help="render a certificate as Markdown+HTML")
    p_rep.add_argument("certificates", nargs="+")
    p_rep.set_defaults(func=_cmd_report)

    p_par = sub.add_parser("pareto", help="Pareto plot over certificates")
    p_par.add_argument("certificates", nargs="+")
    p_par.add_argument("-o", "--output", default="artifacts/pareto.png")
    p_par.set_defaults(func=_cmd_pareto)

    p_cs = sub.add_parser("cache-stats",
                          help="Disk-cache stats (and optional --purge-tier)")
    p_cs.add_argument("--purge-tier", choices=["mlip", "xtb", "dft"],
                      help="Evict all entries (both caches) with this tier")
    p_cs.set_defaults(func=_cmd_cache_stats)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
