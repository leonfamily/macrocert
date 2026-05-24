"""Certificate verifier CLI (macrocert-verify).

Re-checks a Certificate JSON from scratch, importing only from the
standard library plus this subpackage's gml_reader/conservation. The
verifier MUST run successfully on a machine where MØD is uninstalled.

Exit codes:
   0  valid certificate
  10  conservation/atom-map failure
  20  solver-witness invalid (re-check fails)
  30  schema/format error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .conservation import check_rule_conservation, expelled_mass_g_per_mol


def verify_certificate(cert_path: Path) -> int:
    try:
        cert = json.loads(cert_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read certificate {cert_path}: {e}", file=sys.stderr)
        return 30

    required = {"spec_hash", "derivation_graph", "composed_rule", "flow", "solver_witness"}
    missing = required - cert.keys()
    if missing:
        print(f"missing top-level keys: {sorted(missing)}", file=sys.stderr)
        return 30

    composed = cert["composed_rule"]
    if not isinstance(composed, dict) or "gml" not in composed:
        print("composed_rule missing inline GML", file=sys.stderr)
        return 30

    result = check_rule_conservation(composed["gml"])
    if not result.ok:
        print(f"composed rule failed conservation: {result.reason}", file=sys.stderr)
        return 10

    declared_expelled = composed.get("expelled_mass_g_per_mol")
    if declared_expelled is not None:
        recomputed = expelled_mass_g_per_mol(composed["gml"])
        if abs(float(declared_expelled) - recomputed) > 1e-6:
            print(
                f"expelled_mass mismatch: declared {declared_expelled}, "
                f"recomputed {recomputed:.6f}",
                file=sys.stderr,
            )
            return 10

    witness = cert["solver_witness"]
    kind = witness.get("kind")
    if kind == "optimal":
        if "dual_bound" not in witness or "obj_value" not in witness:
            print("optimal witness missing dual_bound/obj_value", file=sys.stderr)
            return 20
        if float(witness["dual_bound"]) > float(witness["obj_value"]) + 1e-6:
            print(
                "dual bound exceeds objective; not a valid optimality certificate",
                file=sys.stderr,
            )
            return 20
    elif kind == "infeasible":
        if "farkas_multipliers" not in witness and "iis_constraint_ids" not in witness:
            print(
                "infeasibility witness missing both farkas_multipliers and iis_constraint_ids",
                file=sys.stderr,
            )
            return 20
    else:
        print(f"unknown solver witness kind: {kind!r}", file=sys.stderr)
        return 30

    print(f"OK  {cert_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="macrocert-verify")
    p.add_argument("certificates", nargs="+", help="paths to certificate JSON files")
    args = p.parse_args(argv)

    worst = 0
    for cert in args.certificates:
        rc = verify_certificate(Path(cert))
        if rc > worst:
            worst = rc
    return worst


if __name__ == "__main__":
    sys.exit(main())
