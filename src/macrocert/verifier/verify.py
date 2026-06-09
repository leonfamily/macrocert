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
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .conservation import check_rule_conservation, expelled_mass_g_per_mol

_SCHEMA_PATH = Path(__file__).parent / "schema" / "certificate.schema.json"
_INTEGRITY_HASH_FIELD = "integrity_hash"


def verify_certificate(cert_path: Path) -> int:
    try:
        cert = json.loads(cert_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read certificate {cert_path}: {e}", file=sys.stderr)
        return 30

    schema_rc = _check_schema(cert)
    if schema_rc:
        return schema_rc

    rc = _check_integrity_hash(cert)
    if rc:
        return rc

    rc = _check_composed_rule(cert)
    if rc:
        return rc

    rc = _check_witness(cert)
    if rc:
        return rc

    rc = _check_energetics(cert)
    if rc:
        return rc

    rc = _check_advisory_propagation(cert)
    if rc:
        return rc

    print(f"OK  {cert_path}")
    return 0


def _check_integrity_hash(cert: dict[str, Any]) -> int:
    """Recompute and validate the cert's integrity_hash, if published.

    Pre-#7 certificates without the field continue to verify unchanged
    (the field is OPTIONAL per the schema). Certificates that publish
    the hash are held to it: any single-field tamper changes the hash.

    The canonical form mirrors :func:`macrocert.kernel.certify.compute_integrity_hash`:
    sort_keys + compact separators. Hash bytes only (no whitespace).
    """
    declared = cert.get(_INTEGRITY_HASH_FIELD)
    if declared is None:
        return 0
    payload = {k: v for k, v in cert.items() if k != _INTEGRITY_HASH_FIELD}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    recomputed = hashlib.sha256(canonical).hexdigest()
    if recomputed != declared:
        print(
            f"integrity_hash mismatch: declared {declared}, "
            f"recomputed {recomputed} — certificate has been tampered with",
            file=sys.stderr,
        )
        return 30
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


def _check_advisory_propagation(cert: dict[str, Any]) -> int:
    """Enforce proposal §6 honesty plumbing on stereo advisories.

    Every hyperedge carries ``stereo_treatment`` (from the producer-side
    rule meta). If the cert uses (flow > 0) an edge whose treatment is
    ``advisory_only``, the cert's ``provenance.stereo_advisories``
    MUST publish a non-empty entry for that rule_id. This catches the
    'silently drop the advisory and pretend the rule enforced stereo'
    attack documented in docs/adversarial_verifier_roadmap.md §3.

    Symmetrically: every published advisory must reference a rule_id
    that exists in ``derivation_graph.hyperedges`` (no orphan advisories).
    """
    provenance = cert.get("provenance") or {}
    advisories_raw = provenance.get("stereo_advisories", []) or []

    advisories: dict[str, str] = {}
    for entry in advisories_raw:
        rid = entry.get("rule_id")
        text = entry.get("advisory", "")
        if not rid:
            print("provenance.stereo_advisories entry missing rule_id",
                  file=sys.stderr)
            return 20
        if not text:
            print(
                f"provenance.stereo_advisories[{rid!r}] has empty advisory text",
                file=sys.stderr,
            )
            return 20
        advisories[rid] = text

    edges_by_rule: dict[str, list[dict[str, Any]]] = {}
    for e in cert["derivation_graph"]["hyperedges"]:
        edges_by_rule.setdefault(e["rule_id"], []).append(e)

    for rid in advisories:
        if rid not in edges_by_rule:
            print(
                f"provenance.stereo_advisories references orphan rule_id {rid!r} "
                "(not in derivation_graph.hyperedges)",
                file=sys.stderr,
            )
            return 20

    flow: dict[str, int] = {k: int(v) for k, v in cert["flow"].items()}
    used_rules: set[str] = set()
    for e in cert["derivation_graph"]["hyperedges"]:
        if int(flow.get(e["id"], 0)) > 0:
            used_rules.add(e["rule_id"])

    for rid in used_rules:
        edges = edges_by_rule[rid]
        if any(e.get("stereo_treatment") == "advisory_only" for e in edges):
            if rid not in advisories:
                print(
                    f"used edge for rule {rid!r} is advisory_only but the cert "
                    "publishes no matching provenance.stereo_advisories entry — "
                    "violates proposal §6 honesty plumbing",
                    file=sys.stderr,
                )
                return 20

    return 0


def _check_energetics(cert: dict[str, Any]) -> int:
    """Re-check energetics_dependencies for internal consistency.

    The verifier does NOT re-run DFT/MLIP — Layer D is defeasible by
    construction (proposal §3.5). What we check:
      - If energetics_dependencies is null, the certificate makes no
        energetics claims; nothing to verify.
      - If non-null, every entry must declare {tier, dG_kcal_per_mol,
        cache_key, method}. The tier must be in {mlip, xtb, dft}.
      - Every entry must correspond to an actual edge in the
        derivation_graph (no orphan claims).
      - Every edge that appears in flow with multiplicity > 0 must
        have an energetics entry — the certificate is honest about
        which 'sorry's it relied on.
    """
    deps = cert.get("energetics_dependencies")
    if deps is None:
        return 0
    if not isinstance(deps, dict):
        print("energetics_dependencies must be a dict or null", file=sys.stderr)
        return 30

    per_edge = deps.get("per_edge", {})
    if not isinstance(per_edge, dict):
        print("energetics_dependencies.per_edge must be a dict", file=sys.stderr)
        return 30

    valid_tiers = {"mlip", "xtb", "dft"}
    edge_ids = {e["id"] for e in cert["derivation_graph"]["hyperedges"]}

    for eid, entry in per_edge.items():
        if eid not in edge_ids:
            print(
                f"energetics_dependencies references orphan edge {eid!r}",
                file=sys.stderr,
            )
            return 20
        for required in ("tier", "dG_kcal_per_mol", "cache_key", "method"):
            if required not in entry:
                print(
                    f"energetics_dependencies[{eid}] missing {required!r}",
                    file=sys.stderr,
                )
                return 20
        if entry["tier"] not in valid_tiers:
            print(
                f"energetics_dependencies[{eid}] has invalid tier {entry['tier']!r}",
                file=sys.stderr,
            )
            return 20

    flow = {k: int(v) for k, v in cert["flow"].items()}
    for eid, n in flow.items():
        if n > 0 and eid not in per_edge:
            print(
                f"flow uses edge {eid} x{n} but no energetics entry — "
                "certificate is silent on which ΔG was trusted",
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
