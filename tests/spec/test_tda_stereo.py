"""Tests for the transannular Diels-Alder stereo-encoding rules.

Workstream F task #35. Three sibling rules now live under data/rules/:

  - ``transannular_diels_alder``        (symmetric, stereo-agnostic,
                                         the legacy v0 rule unchanged)
  - ``transannular_diels_alder_endo``   (R-side TetrahedralFixed on the
                                         4 new sp3 centres, endo face)
  - ``transannular_diels_alder_exo``    (enantiomer of endo at every
                                         centre, exo face)

The base rule remains in the ``all_macrocyclization`` set to keep
existing M5 campaigns backward-compatible. The endo/exo siblings are
opt-in via the ``tda_stereo_aware`` set (data/rules/_index.yaml). See
docs/workstream_f_tda_stereo.md for the design rationale.

Three tests live here:

  1. Base TDA rule still passes conservation re-check (backward compat).
  2. The two stereo siblings load, pass conservation, and carry the
     expected stereo annotations on the 4 new sp3 centres on R.
  3. The endo and exo rules differ by an *odd* permutation on every
     centre -- the canonical encoding for enantiomeric face-of-approach.
"""
from __future__ import annotations

import re
from pathlib import Path

from macrocert.spec.rules import load_rule_library
from macrocert.verifier.conservation import check_rule_conservation
from macrocert.verifier.stereo_conservation import (
    _parse_stereo_string,
    _permutation_parity,
    check_rule_stereo_conservation,
)


RULES_DIR = Path("data/rules")
TDA_CENTERS = (1, 4, 5, 6)  # the four new sp3 centres in the cyclohexene


def _load_lib():
    """Load the live rule library. Skipped silently if the cwd is not
    the repo root (e.g. when pytest is invoked from elsewhere); panel
    tests have the same convention."""
    if not RULES_DIR.is_dir():
        import pytest
        pytest.skip(f"rule library not at {RULES_DIR.resolve()}")
    return load_rule_library(RULES_DIR)


def test_base_tda_rule_unchanged_passes_conservation() -> None:
    """Backward-compat invariant: the original
    ``transannular_diels_alder.gml`` keeps its stereo-agnostic form
    so the existing cassaine M5 cert under ``all_macrocyclization``
    is byte-identical. No stereo annotations on the base rule.
    """
    lib = _load_lib()
    base = lib.rules["transannular_diels_alder"]
    result = check_rule_conservation(base.gml)
    assert result.ok, f"base TDA rule must pass conservation: {result.reason}"
    issues = check_rule_stereo_conservation(base.gml)
    # The base rule is stereo-free -- no errors, no warnings, no infos.
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], f"base TDA rule must be stereo-clean, got: {errors}"
    assert "tetrahedral" not in base.gml, (
        "base rule must remain stereo-agnostic for backward-compat with "
        "the cassaine M5 campaign under all_macrocyclization"
    )


def test_endo_and_exo_siblings_load_and_carry_stereo_on_R() -> None:
    """The two stereo-aware siblings exist, pass conservation, and
    carry tetrahedral fixed (``[..]!``) annotations on each of the
    four new sp3 centres in their R-side block.
    """
    lib = _load_lib()
    assert "transannular_diels_alder_endo" in lib.rules
    assert "transannular_diels_alder_exo" in lib.rules

    # The ``tda_stereo_aware`` rule set selects both.
    members = lib.resolve_set("tda_stereo_aware")
    member_ids = {r.id for r in members}
    assert member_ids == {
        "transannular_diels_alder_endo",
        "transannular_diels_alder_exo",
    }

    # Base rule is in all_macrocyclization but the stereo siblings are
    # NOT (to avoid double-counting in M5 campaigns).
    all_ids = {r.id for r in lib.resolve_set("all_macrocyclization")}
    assert "transannular_diels_alder" in all_ids
    assert "transannular_diels_alder_endo" not in all_ids
    assert "transannular_diels_alder_exo" not in all_ids

    for rid in ("transannular_diels_alder_endo", "transannular_diels_alder_exo"):
        rule = lib.rules[rid]
        # Conservation passes.
        cons = check_rule_conservation(rule.gml)
        assert cons.ok, f"{rid}: conservation re-check must pass: {cons.reason}"
        # Stereo conservation: no errors. Warnings/infos allowed (none
        # expected for fully-paired TetrahedralFixed R-only annotations
        # on a rule whose L has no stereo).
        stereo_issues = check_rule_stereo_conservation(rule.gml)
        errors = [i for i in stereo_issues if i.severity == "error"]
        assert errors == [], f"{rid}: stereo errors: {errors}"
        # Each of the 4 new sp3 centres must carry a fixed tetrahedral
        # bracket on R. Scan the right block.
        right_match = re.search(
            r"right\s*\[(.*?)\n\s*\]\s*\n\s*\]", rule.gml, re.DOTALL
        )
        assert right_match, f"{rid}: couldn't find right [...] block"
        right_body = right_match.group(1)
        for nid in TDA_CENTERS:
            patt = re.compile(
                rf"node\s*\[\s*id\s+{nid}\b[^]]*"
                rf'stereo\s+"tetrahedral\[[^"]*\]!"'
            )
            assert patt.search(right_body), (
                f"{rid}: expected tetrahedral[...]! stereo on R-side node {nid}"
            )
        # stereo_flags must include either 'endo' or 'exo'.
        face_flag = "endo" if rid.endswith("endo") else "exo"
        assert face_flag in rule.meta.stereo_flags, (
            f"{rid}: stereo_flags must include {face_flag!r}, got "
            f"{rule.meta.stereo_flags}"
        )
        assert "sets_four_sp3_stereocenters" in rule.meta.stereo_flags


def test_endo_and_exo_differ_by_odd_permutation_at_every_center() -> None:
    """The endo and exo siblings encode mutually-enantiomeric faces:
    at every one of the 4 new sp3 centres the two bracket lists must
    be an *odd* permutation of each other. This is the canonical
    sibling-rule pattern for concerted multi-centre stereo creation
    (docs/mod_stereo_reference.md §4.3, docs/stereo_encoding_procedure.md
    §3.3).
    """
    lib = _load_lib()
    endo = lib.rules["transannular_diels_alder_endo"].gml
    exo = lib.rules["transannular_diels_alder_exo"].gml

    def _extract_right_brackets(gml: str) -> dict[int, list]:
        """Return {node_id: [neighbour-id, ...]} for every R-side
        tetrahedral fixed annotation."""
        right_match = re.search(
            r"right\s*\[(.*?)\n\s*\]\s*\n\s*\]", gml, re.DOTALL
        )
        assert right_match
        body = right_match.group(1)
        out: dict[int, list] = {}
        for m in re.finditer(
            r'node\s*\[\s*id\s+(\d+)\b[^\]]*?stereo\s+"(tetrahedral\[[^"]*\]!)"',
            body,
        ):
            nid = int(m.group(1))
            parsed = _parse_stereo_string(m.group(2))
            assert parsed is not None
            out[nid] = [x for x in parsed.neighbours if isinstance(x, int)]
        return out

    endo_brackets = _extract_right_brackets(endo)
    exo_brackets = _extract_right_brackets(exo)
    assert set(endo_brackets) == set(TDA_CENTERS)
    assert set(exo_brackets) == set(TDA_CENTERS)

    for nid in TDA_CENTERS:
        e = endo_brackets[nid]
        x = exo_brackets[nid]
        assert sorted(e) == sorted(x), (
            f"node {nid}: endo and exo must list the same neighbour set; "
            f"endo={e} exo={x}"
        )
        parity = _permutation_parity(e, x)
        assert parity == "odd", (
            f"node {nid}: endo {e} and exo {x} must be an ODD permutation "
            f"(enantiomeric face); got parity={parity}. This is the "
            f"canonical sibling-rule pattern for the concerted [4+2] "
            f"face-of-approach split (docs/stereo_encoding_procedure.md §3.3)."
        )
