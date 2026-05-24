rule [
    ruleID "cross_coupling_suzuki (Ar-B(OH)2 + Ar'-Br -> Ar-Ar' + B(OH)2O + HBr)"
    # Suzuki-Miyaura macrocyclization. Bond-level model per the
    # Lennox/Denmark boronate mechanism (DOI:10.1039/c3cs60197h;
    # DOI:10.1021/jacs.1c08283): the boronate R-B(OH)3 anion transmetalates
    # to Pd; the third hydroxyl loses its H, which migrates to the halide
    # to form HBr. Boron departs as B(OH)2(O-) (60.82 g/mol) -- a 1.008
    # g/mol delta from the chemically natural neutral B(OH)3 (61.83). We
    # take the strict atom-conserving form, matching macrolactamization
    # which expels neutral H2O (DOI:10.1021/cr00039a007 for the canonical
    # Suzuki review; see meta.yaml for the full citation list).
    #
    # Atom map (Workstream C research §2.2 final, docs/cross_coupling_research.md):
    #   1  C  context  -- ipso C of organoboron, retained_root
    #   2  C  context  -- ipso C of halide
    #   3  B  L+R      -- boron of B(OH)3- / B(OH)2O byproduct
    #   4,6,8  O  L+R  -- three boronate oxygens
    #   5,7    H  L+R  -- H on O(4) and O(6); both retained on B(OH)2O
    #   9      H  L+R  -- H on O(8) on L; migrates to Br(10) on R as HBr
    #   10     Br L+R  -- leaving halide; bonded to C(2) on L, to H(9) on R
    #
    # Bond changes: break {1-3, 8-9, 2-10}; form {1-2, 9-10}.
    left [
        node [ id 3  label "B"  ]
        node [ id 4  label "O"  ]
        node [ id 5  label "H"  ]
        node [ id 6  label "O"  ]
        node [ id 7  label "H"  ]
        node [ id 8  label "O"  ]
        node [ id 9  label "H"  ]
        node [ id 10 label "Br" ]
        edge [ source 1  target 3  label "-" ]
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        edge [ source 8  target 9  label "-" ]
        edge [ source 2  target 10 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]
    right [
        node [ id 3  label "B"  ]
        node [ id 4  label "O"  ]
        node [ id 5  label "H"  ]
        node [ id 6  label "O"  ]
        node [ id 7  label "H"  ]
        node [ id 8  label "O"  ]
        node [ id 9  label "H"  ]
        node [ id 10 label "Br" ]
        edge [ source 1  target 2  label "-" ]
        edge [ source 3  target 4  label "-" ]
        edge [ source 4  target 5  label "-" ]
        edge [ source 3  target 6  label "-" ]
        edge [ source 6  target 7  label "-" ]
        edge [ source 3  target 8  label "-" ]
        edge [ source 9  target 10 label "-" ]
    ]
]
