rule [
    ruleID "rcm (ring-closing metathesis, -C2H4)"
    # L: two terminal alkenes C(1)=C(2)H2  and  C(3)=C(4)H2 on the substrate.
    # Hydrogens on the CH2 termini (5,6,7,8) are explicit so the verifier
    # can audit atom balance and identify ethylene as the byproduct on R.
    left [
        node [ id 5 label "H" ]
        node [ id 6 label "H" ]
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 2 label "=" ]
        edge [ source 3 target 4 label "=" ]
        edge [ source 2 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
        edge [ source 4 target 7 label "-" ]
        edge [ source 4 target 8 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
    ]
    # R: new ring alkene C(1)=C(3), expelled ethylene H2C(2)=C(4)H2.
    right [
        node [ id 5 label "H" ]
        node [ id 6 label "H" ]
        node [ id 7 label "H" ]
        node [ id 8 label "H" ]
        edge [ source 1 target 3 label "=" ]
        edge [ source 2 target 4 label "=" ]
        edge [ source 2 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
        edge [ source 4 target 7 label "-" ]
        edge [ source 4 target 8 label "-" ]
    ]
]
