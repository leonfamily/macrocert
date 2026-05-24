rule [
    ruleID "cross_coupling_negishi (Ar-ZnBr + Ar'-Br -> Ar-Ar' + ZnBr2)"
    # Negishi cross-coupling macrocyclization. Bond-level model per
    # Negishi 1977 (DOI:10.1021/jo00438a041): organozinc transmetalates
    # to Pd; the zinc partner departs as the dihalide ZnBr2.
    # No proton transfer required -- strict atom conservation is exact
    # (in contrast to Suzuki, which needs a base-derived H to neutralize).
    #
    # Atom map (Workstream C research §Appendix, docs/cross_coupling_research.md):
    #   1  C  context  -- ipso C of organozinc, retained_root
    #   2  C  context  -- ipso C of halide
    #   3  Zn L+R      -- zinc; on L bonded to C(1) and Br(4); on R bonded to Br(4) and Br(5)
    #   4  Br L+R      -- first halide; on L bonded to Zn(3); on R still bonded to Zn(3)
    #   5  Br L+R      -- second halide; on L bonded to C(2); on R bonded to Zn(3) (as ZnBr2)
    #
    # Bond changes: break {1-3, 2-5}; form {1-2, 3-5}.
    left [
        node [ id 3 label "Zn" ]
        node [ id 4 label "Br" ]
        node [ id 5 label "Br" ]
        edge [ source 1 target 3 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 2 target 5 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]
    right [
        node [ id 3 label "Zn" ]
        node [ id 4 label "Br" ]
        node [ id 5 label "Br" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 3 target 5 label "-" ]
    ]
]
