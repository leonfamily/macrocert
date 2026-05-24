rule [
    ruleID "c-h dehydrogenative coupling (C-C closure, -H2)"
    # Canonical acceptorless dehydrogenative C-H/C-H -> C-C closure.
    # L: two C-H bonds C(1)-H(7) and C(2)-H(8). C(1) and C(2) are
    # tethered through the macrocyclic backbone (out of scope for the
    # rule body; the strategy layer enforces intramolecularity and
    # ring-size). Hydrogens H(7), H(8) are explicit so the verifier
    # can identify H2 (mass 2.016 g/mol) as the byproduct on R via
    # the BFS-from-retained_root_atom partition.
    left [
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 7 label "-" ]
        edge [ source 2 target 8 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]
    # R: new C(1)-C(2) bond closes the ring. Expelled H(7)-H(8) forms H2.
    # The H2 fragment is a disconnected component from C(1)-C(2) in R,
    # so the verifier's BFS from retained_root_atom=1 identifies it
    # automatically as the byproduct.
    right [
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 7 target 8 label "-" ]
    ]
]
