rule [
    ruleID "macrolactamization (amide ring closure, -H2O)"
    # L: carboxylic acid carbon (1)=O(2)/-O(3)-H(4)  and amine N(5)-H(6)
    left [
        node [ id 2 label "O" ]
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 3 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 5 target 6 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 5 label "N" ]
        edge [ source 1 target 2 label "=" ]
    ]
    # R: amide C(1)(=O(2))-N(5) plus expelled H2O (atoms 3,4,6)
    right [
        node [ id 2 label "O" ]
        node [ id 3 label "O" ]
        node [ id 4 label "H" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 3 target 6 label "-" ]
    ]
]
