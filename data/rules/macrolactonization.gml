rule [
    ruleID "macrolactonization (ester ring closure, -H2O)"
    # L: carboxylic acid carbon (1)=O(2)/-O(3)-H(4)  and alcohol O(5)-H(6)
    # Structurally identical to macrolactamization with N(5) -> O(5).
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
        node [ id 5 label "O" ]
        # α-carbon (id 7): sp3 tetrahedral, symmetric (no brackets, no '!')
        # so the rule matches either chirality on the substrate. Acyl
        # substitution at C(1)=O does not touch the α-C, so identical
        # stereo on L and R — encoded as a single context annotation per
        # docs/mod_stereo_reference.md §2.1 / §5.6: L = left ∪ context and
        # R = right ∪ context, so stereo placed on context applies to both.
        # MØD requires the geometric vertex to have degree 4 at rule-load
        # time (Stereo/Inference.hpp::finalizeVertex), so we expose the
        # α-C's three additional neighbours (8, 9, 10) as wildcards. Same
        # pattern as the canonical Tartaric "Change" rule in
        # external/mod/examples/py/030_stereo/330_tartaric.py (cited in
        # docs/mod_stereo_reference.md §1.6.2). retains_alpha_stereo per
        # meta.yaml — verified by Workstream C macrolactonization research §4.
        node [ id 7 label "C" stereo "tetrahedral" ]
        node [ id 8 label "*" ]
        node [ id 9 label "*" ]
        node [ id 10 label "*" ]
        edge [ source 1 target 2 label "=" ]
        edge [ source 1 target 7 label "-" ]
        edge [ source 7 target 8 label "-" ]
        edge [ source 7 target 9 label "-" ]
        edge [ source 7 target 10 label "-" ]
    ]
    # R: ester C(1)(=O(2))-O(5) plus expelled H2O (atoms 3,4,6)
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
