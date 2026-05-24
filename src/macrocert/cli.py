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


def _cmd_run(args: argparse.Namespace) -> int:
    print("pipeline.run is not yet implemented (M2)", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="macrocert")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_cr = sub.add_parser("check-rules", help="validate rule library")
    p_cr.add_argument("directory")
    p_cr.set_defaults(func=_cmd_check_rules)

    p_et = sub.add_parser("encode-target", help="encode target + emit perimeter audit")
    p_et.add_argument("target_dir")
    p_et.set_defaults(func=_cmd_encode_target)

    p_run = sub.add_parser("run", help="run the pipeline (M2+)")
    p_run.add_argument("runspec")
    p_run.set_defaults(func=_cmd_run)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
