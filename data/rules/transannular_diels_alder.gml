rule [
    ruleID "transannular diels-alder ([4+2] cycloaddition, 0 byproduct)"
    # L: diene C(1)=C(2)-C(3)=C(4)  and  dienophile C(5)=C(6).
    # All six carbons are sp2 reactive carbons; substituents are implicit
    # and treated as out-of-scope for the rule.
    left [
        edge [ source 1 target 2 label "=" ]
        edge [ source 2 target 3 label "-" ]
        edge [ source 3 target 4 label "=" ]
        edge [ source 5 target 6 label "=" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
        node [ id 3 label "C" ]
        node [ id 4 label "C" ]
        node [ id 5 label "C" ]
        node [ id 6 label "C" ]
    ]
    # R: cyclohexene — two new sigma bonds (1-6, 4-5) and one remaining
    # endocyclic alkene (2=3). Zero byproduct: maximal atom economy.
    right [
        edge [ source 1 target 2 label "-" ]
        edge [ source 2 target 3 label "=" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 5 target 6 label "-" ]
        edge [ source 1 target 6 label "-" ]
        edge [ source 4 target 5 label "-" ]
    ]
]
