"""Tests for Workstream F (Component 2): stereo conservation checker.

Cross-reference: docs/mod_stereo_reference.md §3.1 enumerates the
invariants under test here.
"""
from __future__ import annotations

from macrocert.verifier.stereo_conservation import (
    StereoIssue,
    _parse_stereo_string,
    _permutation_parity,
    check_rule_stereo_conservation,
)


# ----------------------------------------------------------------------------
# Sub-grammar
# ----------------------------------------------------------------------------


def test_parse_stereo_geometry_only():
    p = _parse_stereo_string("tetrahedral")
    assert p is not None
    assert p.geometry == "tetrahedral"
    assert p.neighbours == ()
    assert p.fixed is False


def test_parse_stereo_full_form():
    p = _parse_stereo_string("tetrahedral[1, 2, 3, 4]!")
    assert p is not None and p.geometry == "tetrahedral"
    assert p.neighbours == (1, 2, 3, 4)
    assert p.fixed is True


def test_parse_stereo_with_virtual_edge():
    """A single letter in the bracket list is a virtual edge (lone pair
    or radical) per Stereo/IO/Read.cpp:26."""
    p = _parse_stereo_string("[1, 2, 3, e]!")
    assert p is not None and p.geometry is None
    assert p.neighbours == (1, 2, 3, "e")
    assert p.fixed is True


def test_parse_stereo_empty_rejected():
    """MØD's parser rejects the empty embedding (!eoi after no
    components). See Stereo/IO/Read.cpp."""
    assert _parse_stereo_string("") is None


def test_parse_stereo_bracket_only_with_fix():
    p = _parse_stereo_string("[]!")
    assert p is not None
    assert p.geometry is None
    assert p.neighbours == ()
    assert p.fixed is True


# ----------------------------------------------------------------------------
# Permutation parity (the Good/Bad partition from
# external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp:118-155)
# ----------------------------------------------------------------------------


def test_parity_identity_is_even():
    assert _permutation_parity([1, 2, 3, 4], [1, 2, 3, 4]) == "even"


def test_parity_single_transposition_is_odd():
    assert _permutation_parity([1, 2, 3, 4], [2, 1, 3, 4]) == "odd"


def test_parity_3cycle_is_even():
    # [1,2,3,4] -> [2,3,1,4] is a 3-cycle (1->2,2->3,3->1) which is two
    # transpositions, i.e. EVEN. This matches MØD's "Good" table entry
    # in Tetrahedral.cpp:118-155.
    assert _permutation_parity([1, 2, 3, 4], [2, 3, 1, 4]) == "even"


def test_parity_reverse_is_even():
    # [1,2,3,4] -> [4,3,2,1] = (1 4)(2 3) — two transpositions, even.
    assert _permutation_parity([1, 2, 3, 4], [4, 3, 2, 1]) == "even"


# ----------------------------------------------------------------------------
# Invariant 1: even-permutation discipline
# ----------------------------------------------------------------------------


_PRESERVING_RULE = """
rule [
    ruleID "preserve sp3 chirality"
    left  [ node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ] ]
    context [
        node [ id 0 label "C" ]
        node [ id 1 label "H" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [ node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ] ]
]
"""


_INVERTING_RULE = """
rule [
    ruleID "silent inversion (odd permutation)"
    left  [ node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ] ]
    context [
        node [ id 0 label "C" ]
        node [ id 1 label "H" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [ node [ id 0 stereo "tetrahedral[2, 1, 3, 4]!" ] ]
]
"""


_3CYCLE_RULE = """
rule [
    ruleID "even 3-cycle reorder (chirality preserved)"
    left  [ node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ] ]
    context [
        node [ id 0 label "C" ]
        node [ id 1 label "H" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [ node [ id 0 stereo "tetrahedral[2, 3, 1, 4]!" ] ]
]
"""


def test_preserving_rule_has_no_errors():
    issues = check_rule_stereo_conservation(_PRESERVING_RULE)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors


def test_silent_inversion_is_flagged_as_error():
    issues = check_rule_stereo_conservation(_INVERTING_RULE)
    errs = [i for i in issues if i.severity == "error"]
    assert any(i.code == "odd_permutation_inversion" for i in errs), issues


def test_even_3cycle_reorder_is_not_flagged():
    """[1,2,3,4] -> [2,3,1,4] is an even permutation (3-cycle = two
    transpositions). Same chirality class per MØD's Good table."""
    issues = check_rule_stereo_conservation(_3CYCLE_RULE)
    errs = [i for i in issues if i.severity == "error"]
    assert errs == [], errs


# ----------------------------------------------------------------------------
# Invariant 2: fixation transitions
# ----------------------------------------------------------------------------


_SYM_TO_FIXED = """
rule [
    ruleID "create chirality (Sym → Fixed)"
    left  [ node [ id 0 stereo "tetrahedral" ] ]
    context [
        node [ id 0 label "C" ]
        node [ id 1 label "H" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
        edge [ source 0 target 1 label "-" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
        edge [ source 0 target 4 label "-" ]
    ]
    right [ node [ id 0 stereo "tetrahedral[1, 2, 3, 4]!" ] ]
]
"""


def test_fixation_transition_warns():
    issues = check_rule_stereo_conservation(_SYM_TO_FIXED)
    warns = [i for i in issues if i.code == "fixation_transition"]
    assert warns, issues
    assert all(i.severity == "warning" for i in warns)


# ----------------------------------------------------------------------------
# Invariant 3: edge stereo is documentation-only
# ----------------------------------------------------------------------------


_EDGE_STEREO_RULE = """
rule [
    ruleID "edge stereo (advisory)"
    left  [ ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
        edge [ source 1 target 2 label "=" stereo "E" ]
    ]
    right [ ]
]
"""


def test_edge_stereo_emits_info():
    issues = check_rule_stereo_conservation(_EDGE_STEREO_RULE)
    infos = [i for i in issues if i.code == "edge_stereo_ignored"]
    assert infos, issues
    assert all(i.severity == "info" for i in infos)


# ----------------------------------------------------------------------------
# Invariant 4: unenforced geometry with `!`
# ----------------------------------------------------------------------------


_TRIGONAL_FIXED_RULE = """
rule [
    ruleID "trigonalPlanar fixed (MOD_ABORT risk)"
    left  [ ]
    context [
        node [ id 0 label "C" ]
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        edge [ source 0 target 1 label "=" ]
        edge [ source 0 target 2 label "-" ]
        edge [ source 0 target 3 label "-" ]
    ]
    right [ node [ id 0 stereo "trigonalPlanar[1, 2, 3]!" ] ]
]
"""


def test_unenforced_geometry_fixed_warns():
    issues = check_rule_stereo_conservation(_TRIGONAL_FIXED_RULE)
    warns = [i for i in issues if i.code == "unenforced_geometry_fixed"]
    assert warns, issues
    assert all(i.severity == "warning" for i in warns)


# ----------------------------------------------------------------------------
# Existing rule library: stereo-free rules emit no issues
# ----------------------------------------------------------------------------


def test_stereo_free_macrolactam_no_issues():
    """The shipped macrolactamization rule has no stereo annotations,
    so the checker must be silent."""
    text = open("tests/fixtures/macrolactamization_baseline.gml").read()
    issues = check_rule_stereo_conservation(text)
    assert issues == [], issues


def test_isinstance_StereoIssue():
    issues = check_rule_stereo_conservation(_INVERTING_RULE)
    assert issues
    assert all(isinstance(i, StereoIssue) for i in issues)
