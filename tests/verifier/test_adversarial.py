"""Adversarial certificate tests — M2 exit criterion.

Per the plan: 'verifier rejects three intentionally corrupted
certificates (atom-map break, dual-bound mismatch, missing IIS row).'

We mutate a known-good certificate and assert the verifier returns
the right exit code (10 for conservation/atom-map failure, 20 for
solver-witness invalid, 30 for schema/format error).
"""
from __future__ import annotations

import copy
import json
import sys
import subprocess
from pathlib import Path
from typing import Any

import pytest


GOOD_CERT_PATH = Path("artifacts/toy_macrolactam/certificate.json")


@pytest.fixture(scope="module")
def good_cert() -> dict[str, Any]:
    if not GOOD_CERT_PATH.exists():
        subprocess.run(
            [sys.executable, "-m", "macrocert.cli", "run", "data/targets/toy_macrolactam"],
            check=True, capture_output=True,
        )
    return json.loads(GOOD_CERT_PATH.read_text())


def _write_and_verify(cert: dict[str, Any], tmp_path: Path) -> int:
    target = tmp_path / "cert.json"
    target.write_text(json.dumps(cert))
    result = subprocess.run(
        [sys.executable, "-m", "macrocert.verifier.verify", str(target)],
        capture_output=True, text=True,
    )
    return result.returncode


def test_good_certificate_verifies(good_cert, tmp_path):
    assert _write_and_verify(good_cert, tmp_path) == 0


# --- exit 10: conservation / atom-map failure --------------------------------
def test_atom_map_break_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    gml = cert["composed_rule"]["gml"]
    left_o = gml.find('id 2 label "O"')
    cert["composed_rule"]["gml"] = (
        gml[:left_o] + 'id 2 label "S"' + gml[left_o + len('id 2 label "O"'):]
    )
    assert _write_and_verify(cert, tmp_path) == 10


def test_tampered_expelled_mass_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["composed_rule"]["expelled_mass_g_per_mol"] = 999.0
    assert _write_and_verify(cert, tmp_path) == 10


# --- exit 20: solver witness invalid -----------------------------------------
def test_dual_bound_above_obj_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["solver_witness"]["dual_bound"] = cert["solver_witness"]["obj_value"] + 1.0
    assert _write_and_verify(cert, tmp_path) == 20


def test_obj_value_disagrees_with_recomputed_flow_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["solver_witness"]["obj_value"] = 0.0
    cert["solver_witness"]["dual_bound"] = 0.0
    assert _write_and_verify(cert, tmp_path) == 20


def test_missing_macrocyclization_in_flow_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["flow"] = {}
    assert _write_and_verify(cert, tmp_path) == 20


def test_infeasible_witness_missing_iis_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["solver_witness"] = {"kind": "infeasible"}
    assert _write_and_verify(cert, tmp_path) == 20


# --- exit 30: schema / format ------------------------------------------------
def test_missing_top_level_key_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert.pop("composed_rule")
    assert _write_and_verify(cert, tmp_path) == 30


def test_unknown_witness_kind_rejected(good_cert, tmp_path):
    cert = copy.deepcopy(good_cert)
    cert["solver_witness"] = {"kind": "feels_good_to_me"}
    assert _write_and_verify(cert, tmp_path) == 30


# --- energetics_dependencies checks ----------------------------------------
@pytest.fixture(scope="module")
def good_energetics_cert() -> dict[str, Any]:
    path = Path("artifacts/toy_macrolactam_energetics/certificate.json")
    if not path.exists():
        subprocess.run(
            [sys.executable, "-m", "macrocert.cli", "run",
             "data/targets/toy_macrolactam_energetics"],
            check=True, capture_output=True,
        )
    return json.loads(path.read_text())


def test_good_energetics_cert_verifies(good_energetics_cert, tmp_path):
    assert _write_and_verify(good_energetics_cert, tmp_path) == 0


def test_orphan_energetics_entry_rejected(good_energetics_cert, tmp_path):
    cert = copy.deepcopy(good_energetics_cert)
    cert["energetics_dependencies"]["per_edge"]["nonexistent_edge_id"] = {
        "tier": "xtb", "dG_kcal_per_mol": 0.0,
        "cache_key": "x", "method": "GFN2-xTB",
    }
    assert _write_and_verify(cert, tmp_path) == 20


def test_invalid_tier_rejected(good_energetics_cert, tmp_path):
    cert = copy.deepcopy(good_energetics_cert)
    eid = next(iter(cert["energetics_dependencies"]["per_edge"]))
    cert["energetics_dependencies"]["per_edge"][eid]["tier"] = "vibes"
    assert _write_and_verify(cert, tmp_path) == 20


def test_silent_on_used_edge_rejected(good_energetics_cert, tmp_path):
    cert = copy.deepcopy(good_energetics_cert)
    cert["energetics_dependencies"]["per_edge"] = {}
    assert _write_and_verify(cert, tmp_path) == 20


# === Parametrized adversarial coverage for the 9 new rules (2026-05-24) =====
#
# The original adversarial fixture (toy_macrolactam + lactone panel) only
# exercises 3 of macrocert's 12 macrocyclization rules. The 9 rules added in
# Workstream C have no rule-specific tampering coverage — a verifier bug
# tied to (e.g.) Sn atomic mass, Suzuki's compound B(OH)2O byproduct, or
# the dehydrogenative-coupling H2 byproduct could ship silently. Each test
# below pins a specific bug pattern the verifier MUST catch for every new
# rule. See ``tests/verifier/README.md`` for the coverage matrix.
from .fixtures import (  # noqa: E402
    ATOM_MAP_BREAK,
    NEW_RULES,
    build_minimal_certificate,
)


@pytest.fixture(scope="module")
def good_cert_per_rule() -> dict[str, dict[str, Any]]:
    """Map rule_id → freshly-built minimal certificate.

    Built once per test module; deep-copy before each mutation so
    parametrized tests don't bleed state between cases.
    """
    return {r: build_minimal_certificate(r) for r in NEW_RULES}


@pytest.mark.parametrize("rule_id", NEW_RULES)
def test_new_rule_good_certificate_verifies(rule_id, good_cert_per_rule, tmp_path):
    # Baseline: synthetic certificate built around the rule's real GML
    # MUST verify cleanly. Guards against rule-library drift silently
    # invalidating downstream tests in this module.
    cert = copy.deepcopy(good_cert_per_rule[rule_id])
    assert _write_and_verify(cert, tmp_path) == 0


# --- exit 10: per-rule atom-map break -----------------------------------------
@pytest.mark.parametrize("rule_id", NEW_RULES)
def test_new_rule_atom_map_break_rejected(rule_id, good_cert_per_rule, tmp_path):
    # Guards against: tampered GML where a node's element label is changed
    # on one side of the DPO span only (L/R disagreement). This is the
    # canonical "swap O for S in the byproduct" attack from
    # test_atom_map_break_rejected, generalized across rules. Must return
    # exit 10 (conservation/atom-map failure).
    cert = copy.deepcopy(good_cert_per_rule[rule_id])
    needle, replacement = ATOM_MAP_BREAK[rule_id]
    gml = cert["composed_rule"]["gml"]
    assert needle in gml, f"atom-map-break needle {needle!r} not in {rule_id} GML"
    # ``str.replace(..., 1)`` only swaps the LEFT-block occurrence; the
    # R-block copy remains unchanged, producing the L/R label mismatch
    # the verifier is supposed to catch.
    cert["composed_rule"]["gml"] = gml.replace(needle, replacement, 1)
    assert _write_and_verify(cert, tmp_path) == 10


# --- exit 10: tampered declared expelled mass --------------------------------
@pytest.mark.parametrize("rule_id", NEW_RULES)
def test_new_rule_tampered_expelled_mass_rejected(rule_id, good_cert_per_rule, tmp_path):
    # Guards against: certificate that declares a wrong bond-level byproduct
    # mass while presenting a correct GML. The verifier MUST recompute the
    # mass from the GML's atom-map and reject the mismatch (exit 10). This
    # is critical for Layer C trust — the AE objective is recomputed from
    # this number, so an unchecked declaration is a silent route-quality
    # forgery.
    cert = copy.deepcopy(good_cert_per_rule[rule_id])
    cert["composed_rule"]["expelled_mass_g_per_mol"] = 999.0
    assert _write_and_verify(cert, tmp_path) == 10


# --- exit 20: solver witness inconsistent with recomputed flow ---------------
@pytest.mark.parametrize("rule_id", NEW_RULES)
def test_new_rule_obj_value_disagrees_with_flow_rejected(
    rule_id, good_cert_per_rule, tmp_path
):
    # Guards against: solver_witness.obj_value that disagrees with the
    # bond-level expelled mass recomputed from flow × per-edge expelled
    # mass. The verifier's recompute path must not just trust the
    # witness's self-reported objective (exit 20).
    cert = copy.deepcopy(good_cert_per_rule[rule_id])
    cert["solver_witness"]["obj_value"] = 0.0
    cert["solver_witness"]["dual_bound"] = 0.0
    assert _write_and_verify(cert, tmp_path) == 20


# --- exit 20: edge expelled mass tampered (witness path) ---------------------
@pytest.mark.parametrize("rule_id", NEW_RULES)
def test_new_rule_edge_expelled_mass_mismatch_rejected(
    rule_id, good_cert_per_rule, tmp_path
):
    # Guards against: derivation-graph edge claiming a different
    # expelled mass than the composed rule. The verifier's _check_obj_value
    # sums flow × edge.expelled_mass; if the edge under-reports, obj_value
    # will not match and verification must fail (exit 20). This pins the
    # honesty of the per-edge weights that the LP/MIP solver sees.
    cert = copy.deepcopy(good_cert_per_rule[rule_id])
    cert["derivation_graph"]["hyperedges"][0]["expelled_mass_g_per_mol"] = 1.0
    assert _write_and_verify(cert, tmp_path) == 20


# --- rule-specific: cross_coupling_stille Sn-Br ------------------------------
def test_stille_sn_mass_recomputed_not_trusted(good_cert_per_rule, tmp_path):
    # Guards against: a tampered Stille certificate that swaps the
    # opaque-Sn label for a much lighter element (Si: 28.085 g/mol vs
    # Sn: 118.710 g/mol). Workstream C added Sn to
    # verifier.conservation._ATOMIC_MASS — if that addition regresses,
    # this test fails with a "atomic mass not tabulated" parse error
    # instead of the expected exit 10. The 90 g/mol delta also stress-
    # tests the recompute-mass comparison tolerance.
    cert = copy.deepcopy(good_cert_per_rule["cross_coupling_stille"])
    gml = cert["composed_rule"]["gml"]
    # Mutate only the right-side Sn label; conservation catches the L↔R
    # mismatch before the mass-recompute step would, but the recompute
    # path is also exercised by ``test_new_rule_tampered_expelled_mass_rejected``.
    right_idx = gml.find("right [")
    assert right_idx > 0, "stille GML missing right block"
    head, tail = gml[:right_idx], gml[right_idx:]
    cert["composed_rule"]["gml"] = head + tail.replace(
        'id 3 label "Sn"', 'id 3 label "Si"', 1
    )
    assert _write_and_verify(cert, tmp_path) == 10


# --- rule-specific: cross_coupling_suzuki B(OH)2O off-by-one -----------------
def test_suzuki_off_by_one_boron_oxygen_rejected(good_cert_per_rule, tmp_path):
    # Guards against: a tampered Suzuki certificate that drops one of the
    # three boronate oxygens from the R-side byproduct (B(OH)2O → B(OH)2).
    # Verifier must catch the L/R atom-multiset asymmetry. The Suzuki
    # byproduct is the only multi-heteroatom expelled fragment in the
    # rule library; this test pins the verifier's correctness for
    # complex byproduct stoichiometry.
    cert = copy.deepcopy(good_cert_per_rule["cross_coupling_suzuki"])
    gml = cert["composed_rule"]["gml"]
    # Flip R-side O(id=8) to H. Conservation now sees L=(O at id 8) vs
    # R=(H at id 8) — one boronate oxygen has "disappeared" from the
    # byproduct.
    right_idx = gml.find("right [")
    head, tail = gml[:right_idx], gml[right_idx:]
    needle = 'node [ id 8  label "O"  ]'
    replacement = 'node [ id 8  label "H"  ]'
    assert needle in tail, "suzuki right block missing id 8 O"
    cert["composed_rule"]["gml"] = head + tail.replace(needle, replacement, 1)
    assert _write_and_verify(cert, tmp_path) == 10


# --- rule-specific: c_h_dehydrogenative_coupling H2 disconnection ------------
def test_dehydrog_byproduct_claimed_in_product_rejected(
    good_cert_per_rule, tmp_path
):
    # Guards against: a tampered c_h_dehydrogenative_coupling certificate
    # that claims one of the H2 byproduct atoms is bonded to the retained
    # carbon scaffold instead of departing as H2. The verifier's BFS from
    # retained_root_atom MUST partition correctly: if H7 is bonded to C1
    # on R, BFS reaches it (and H8 via the still-present 7-8 edge), so
    # the recomputed expelled mass collapses to 0 g/mol while the
    # certificate still declares 2.016. Must return exit 10. This is the
    # H2-byproduct version of the "byproduct atoms hidden in product"
    # attack — the only rule whose byproduct is a disconnected component
    # rather than a heteroatom-bearing fragment.
    cert = copy.deepcopy(good_cert_per_rule["c_h_dehydrogenative_coupling"])
    gml = cert["composed_rule"]["gml"]
    # Add a spurious 1-7 edge on R. H7 was already bonded to C1 on L;
    # the R side normally only has 1-2 (new C-C) and 7-8 (H2). Adding
    # 1-7 makes H7 re-attach to the retained C1 in R, which under BFS
    # incorporates H8 via 7-8 → no atoms expelled.
    right_idx = gml.find("right [")
    head, tail = gml[:right_idx], gml[right_idx:]
    needle = 'edge [ source 1 target 2 label "-" ]'
    assert needle in tail, "dehydrog right block missing 1-2 edge"
    cert["composed_rule"]["gml"] = head + tail.replace(
        needle,
        needle + '\n        edge [ source 1 target 7 label "-" ]',
        1,
    )
    assert _write_and_verify(cert, tmp_path) == 10
