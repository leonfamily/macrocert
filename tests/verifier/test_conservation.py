from macrocert.verifier.conservation import check_rule_conservation, expelled_mass_g_per_mol


MACROLACTAM = open("tests/fixtures/macrolactamization_baseline.gml").read()


def test_macrolactamization_passes_conservation():
    result = check_rule_conservation(MACROLACTAM)
    assert result.ok
    assert result.balanced  # the rule rebonds rather than deleting atoms


def test_mismatched_element_label_rejected():
    bad = """
    rule [
        ruleID "bad: nitrogen becomes carbon"
        left    [ node [ id 1 label "N" ] ]
        context [ ]
        right   [ node [ id 1 label "C" ] ]
    ]
    """
    result = check_rule_conservation(bad)
    assert not result.ok
    assert "node 1" in result.reason


def test_charge_mismatch_rejected():
    bad = """
    rule [
        ruleID "bad: charge flip"
        left    [ node [ id 1 label "C" charge 0 ] ]
        context [ ]
        right   [ node [ id 1 label "C" charge 1 ] ]
    ]
    """
    result = check_rule_conservation(bad)
    assert not result.ok


def test_dangling_deleted_atom_rejected():
    bad = """
    rule [
        ruleID "bad: atom 2 is dropped but still bonded to retained scaffold"
        left [
            node [ id 1 label "C" ]
            node [ id 2 label "Cl" ]
            edge [ source 1 target 2 label "-" ]
        ]
        context [ node [ id 1 label "C" ] ]
        right [ node [ id 1 label "C" ] ]
    ]
    """
    result = check_rule_conservation(bad)
    assert not result.ok
    assert "edges crossing" in result.reason


def test_expelled_mass_zero_for_balanced_rule():
    assert expelled_mass_g_per_mol(MACROLACTAM) == 0.0
