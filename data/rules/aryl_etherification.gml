rule [
    ruleID "aryl_etherification (SNAr Ar-O-C(sp3) ring closure, -HF)"
    # L: aromatic C(1) bearing F(2) and alcohol O(5)-H(6).
    # Atom IDs match macrolactamization/macrolactonization family:
    # 1 = retained anchor (ar C); 5/6 = alcohol O/H. IDs 3, 4 omitted
    # so the BFS-from-1 traversal in the verifier classifies atoms 2, 6
    # (HF) as byproduct.
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
    # R: Ar(1)-O(5)-C(sp3) ether plus expelled HF (atoms 2, 6).
    right [
        node [ id 2 label "F" ]
        node [ id 6 label "H" ]
        edge [ source 1 target 5 label "-" ]
        edge [ source 2 target 6 label "-" ]
    ]
]
