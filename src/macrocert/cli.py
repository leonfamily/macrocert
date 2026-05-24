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

    lib = load_rule_library(args.directory)
    if not lib.rules:
        print(f"no rules found in {args.directory}", file=sys.stderr)
        return 1

    failures = 0
    for rid, rule in lib.rules.items():
        result = check_rule_conservation(rule.gml)
        if result.ok:
            print(f"  OK  {rid:40s}  classes={list(rule.meta.classes)}")
        else:
            failures += 1
            print(f"  FAIL {rid:40s}  {result.reason}", file=sys.stderr)
    if failures:
        print(f"\n{failures} rule(s) failed conservation re-check", file=sys.stderr)
        return 1
    print(f"\n{len(lib.rules)} rule(s) pass conservation re-check")
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
    print(f"  certificate: {report.certificate_path}")
    return 0


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

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
