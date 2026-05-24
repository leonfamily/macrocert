from macrocert.verifier.gml_reader import parse_rule


def test_parses_macrolactamization_rule():
    rule = parse_rule(open("rules/macrolactamization.gml").read())
    assert rule.ruleID.startswith("macrolactamization")
    assert 1 in rule.context.nodes
    assert rule.context.nodes[1].label == "C"
    assert rule.context.nodes[5].label == "N"
    assert any(e.label == "=" for e in rule.context.edges)


def test_strips_comments_and_semicolons():
    text = """
    rule [
        ruleID "trivial"
        # this is a comment line
        left  [ node [ id 1 label "C" ]; node [ id 2 label "H" ] ]
        context [ ]
        right [ node [ id 1 label "C" ]; node [ id 2 label "H" ] ]
    ]
    """
    rule = parse_rule(text)
    assert rule.ruleID == "trivial"
    assert {1, 2} == set(rule.left.nodes.keys())
    assert {1, 2} == set(rule.right.nodes.keys())
