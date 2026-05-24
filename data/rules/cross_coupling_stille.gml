rule [
    ruleID "cross_coupling_stille (Ar-SnR3 + Ar'-Br -> Ar-Ar' + R3Sn-Br) [opaque-Sn variant]"
    # Stille cross-coupling for macrocyclization. Bond-level model per
    # Stille 1986 (DOI:10.1002/anie.198605081) and Farina/Krishnamurthy/
    # Scott 1997 (DOI:10.1002/0471264180.or050.01): organostannane
    # transmetalates to Pd, then reductive elimination forms C-C; the
    # tin partner departs as R3SnBr.
    #
    # *Opaque-Sn convention*: we encode Sn as a single atom and do NOT
    # explicitly track its three n-Bu substituents in the rule body.
    # The strict bond-level byproduct under this encoding is Sn + Br
    # (198.61 g/mol). The chemically realistic byproduct, including the
    # three n-Bu groups, is Bu3SnBr (326.94 g/mol); that value is
    # recorded in byproduct_mass_alternatives and discussed in the
    # meta notes. The strict-atom-conserving form keeps consistency
    # with the other four cross_coupling_* rules and with the
    # macrolactamization precedent (atoms in body == atoms in byproduct).
    #
    # Atom map:
    #   1  C  context  -- ipso C of organostannane, retained_root
    #   2  C  context  -- ipso C of halide
    #   3  Sn L+R      -- tin (opaque; three implicit n-Bu groups not in rule body)
    #   4  Br L+R      -- leaving halide; on L bonded to C(2); on R bonded to Sn(3)
    #
    # Bond changes: break {1-3, 2-4}; form {1-2, 3-4}.
    left [
        node [ id 3 label "Sn" ]
        node [ id 4 label "Br" ]
        edge [ source 1 target 3 label "-" ]
        edge [ source 2 target 4 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
    ]
    right [
        node [ id 3 label "Sn" ]
        node [ id 4 label "Br" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 3 target 4 label "-" ]
    ]
]
