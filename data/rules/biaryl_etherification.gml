rule [
    ruleID "biaryl_etherification (Ar-O-Ar SNAr ring closure, -HF)"
    # Sibling of aryl_etherification.gml. Atom IDs (1, 2, 5, 6) identical
    # to aryl_etherification so the verifier BFS-from-1 traversal works
    # the same way. The body is structurally a near-copy of
    # aryl_etherification because MØD's match operates on element
    # labels — the sp2-aromatic vs sp3 distinction at atom 5 (phenolic
    # vs aliphatic O) cannot be enforced in the GML.
    #
    # Discrimination from aryl_etherification happens at the strategy
    # layer: Workstream D needs `alcohol_partner_C_must_be_aromatic`
    # predicate for this rule and `alcohol_partner_C_must_be_sp3` for
    # the sibling. Until those predicates land both rules will fire on
    # the same substrate.
    #
    # See docs/biaryl_etherification_research.md §2.2 (Option A) for the
    # rationale.
    left [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 5 target 6 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 5 label "O" ]
    ]
    right [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
    ]
]
