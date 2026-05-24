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
