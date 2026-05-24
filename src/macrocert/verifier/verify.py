"""Certificate verifier CLI (macrocert-verify).

Re-checks a Certificate JSON from scratch, importing only from the
standard library plus this subpackage's gml_reader/conservation. The
verifier MUST run successfully on a machine where MØD is uninstalled.

Exit codes:
   0  valid certificate
  10  conservation / atom-map failure
  20  solver-witness invalid (re-check fails)
  30  schema / format error
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .conservation import check_rule_conservation, expelled_mass_g_per_mol

_SCHEMA_PATH = Path(__file__).parent / "schema" / "certificate.schema.json"


def verify_certificate(cert_path: Path) -> int:
    try:
        cert = json.loads(cert_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read certificate {cert_path}: {e}", file=sys.stderr)
        return 30

    schema_rc = _check_schema(cert)
    if schema_rc:
        return schema_rc

    rc = _check_composed_rule(cert)
    if rc:
        return rc

    rc = _check_witness(cert)
    if rc:
        return rc

    print(f"OK  {cert_path}")
    return 0


def _check_schema(cert: dict[str, Any]) -> int:
    required = {"spec_hash", "derivation_graph", "composed_rule", "flow", "solver_witness"}
    missing = required - cert.keys()
    if missing:
        print(f"missing top-level keys: {sorted(missing)}", file=sys.stderr)
        return 30

    dg = cert["derivation_graph"]
    for k in ("vertices", "hyperedges", "sources", "sink", "max_steps"):
        if k not in dg:
            print(f"derivation_graph missing {k!r}", file=sys.stderr)
            return 30

    composed = cert["composed_rule"]
    if "gml" not in composed:
        print("composed_rule missing inline GML", file=sys.stderr)
        return 30

    if not isinstance(cert["flow"], dict):
        print("flow must be a dict edge_id → multiplicity", file=sys.stderr)
        return 30

    return 0


def _check_composed_rule(cert: dict[str, Any]) -> int:
    composed = cert["composed_rule"]
    gml = composed["gml"]

    result = check_rule_conservation(gml)
    if not result.ok:
        print(f"composed rule failed conservation: {result.reason}", file=sys.stderr)
        return 10

    declared = composed.get("expelled_mass_g_per_mol")
    if declared is not None and float(declared) > 0:
        retained_root = composed.get("retained_root_atom")
        recomputed = expelled_mass_g_per_mol(gml, retained_root_atom=retained_root)
        if abs(float(declared) - recomputed) > 1e-3:
            print(
                f"expelled_mass mismatch: declared {declared}, "
                f"recomputed {recomputed:.3f}",
                file=sys.stderr,
            )
            return 10

    return 0


def _check_witness(cert: dict[str, Any]) -> int:
    witness = cert["solver_witness"]
    kind = witness.get("kind")

    if kind == "optimal":
        if "dual_bound" not in witness or "obj_value" not in witness:
            print("optimal witness missing dual_bound/obj_value", file=sys.stderr)
            return 20
        if float(witness["dual_bound"]) > float(witness["obj_value"]) + 1e-6:
            print(
                f"dual bound {witness['dual_bound']} exceeds obj_value "
                f"{witness['obj_value']}; not a valid optimality certificate",
                file=sys.stderr,
            )
            return 20

        rc = _check_flow_balance(cert)
        if rc:
            return rc
        rc = _check_obj_value(cert)
        if rc:
            return rc
        return 0

    if kind == "infeasible":
        has_iis = bool(witness.get("iis_constraint_ids"))
        has_farkas = bool(witness.get("farkas_multipliers"))
        if not (has_iis or has_farkas):
            print(
                "infeasibility witness missing both farkas_multipliers and iis_constraint_ids",
                file=sys.stderr,
            )
            return 20
        return 0

    print(f"unknown solver witness kind: {kind!r}", file=sys.stderr)
    return 30


def _check_flow_balance(cert: dict[str, Any]) -> int:
    dg = cert["derivation_graph"]
    flow: dict[str, int] = {k: int(v) for k, v in cert["flow"].items()}
    edges_by_id = {e["id"]: e for e in dg["hyperedges"]}

    for eid in flow:
        if eid not in edges_by_id:
            print(f"flow references unknown edge {eid!r}", file=sys.stderr)
            return 20

    sources = set(dg["sources"])
    sink = dg["sink"]
    macro_count = 0
    sum_f = sum(flow.values())
    if sum_f > int(dg["max_steps"]):
        print(f"flow violates step budget: Σf={sum_f} > max_steps={dg['max_steps']}", file=sys.stderr)
        return 20

    for v in dg["vertices"]:
        vid = v["id"]
        produced = sum(
            flow.get(e["id"], 0) * Counter(e["targets"]).get(vid, 0)
            for e in dg["hyperedges"]
        )
        consumed = sum(
            flow.get(e["id"], 0) * Counter(e["sources"]).get(vid, 0)
            for e in dg["hyperedges"]
        )
        delta = produced - consumed
        if vid == sink:
            if delta < 1:
                print(
                    f"sink {vid!r}: net production {delta} < 1 (not enough target produced)",
                    file=sys.stderr,
                )
                return 20
        elif vid in sources:
            pass
        else:
            if delta < 0:
                print(
                    f"vertex {vid!r}: net production {delta} < 0 (more consumed than produced)",
                    file=sys.stderr,
                )
                return 20

    for eid, n in flow.items():
        if edges_by_id[eid].get("is_macrocyclization"):
            macro_count += n
    if macro_count != 1:
        print(
            f"exactly_one_macrocyclization violated: flow uses {macro_count} macrocyclization firings",
            file=sys.stderr,
        )
        return 20

    return 0


def _check_obj_value(cert: dict[str, Any]) -> int:
    flow = {k: int(v) for k, v in cert["flow"].items()}
    edges_by_id = {e["id"]: e for e in cert["derivation_graph"]["hyperedges"]}
    bond_level = sum(
        n * float(edges_by_id[eid]["expelled_mass_g_per_mol"])
        for eid, n in flow.items()
    )
    declared = float(cert["solver_witness"]["obj_value"])
    if abs(declared - bond_level) > 1e-3:
        print(
            f"declared obj_value {declared} disagrees with recomputed "
            f"bond-level expelled mass {bond_level:.3f}",
            file=sys.stderr,
        )
        return 20
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
