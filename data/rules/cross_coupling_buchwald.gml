rule [
    ruleID "cross_coupling_buchwald (Ar-NHR + Ar'-Br -> Ar-N(R)-Ar' + HBr)"
    # Buchwald-Hartwig C-N cross-coupling for macrocyclization.
    # Bond-level model per Hartwig 1998 (DOI:10.1021/ar970282g): aryl
    # halide oxidative-adds to Pd, amine coordinates, deprotonation by
    # base affords aryl-amido Pd, reductive elimination forms C-N.
    # We do not track the base atoms in the rule body; H+ comes directly
    # off N and pairs with Br to form HBr -- strict atom-conserving,
    # matching the macrolactamization "neutral byproduct on the rule body"
    # convention.
    #
    # Atom map (Workstream C research §Appendix, docs/cross_coupling_research.md):
    #   1  C  context  -- aryl C bonded to halide, retained_root
    #   2  N  context  -- amine N (carries the migrating H on L)
    #   3  Br L+R      -- leaving halide; on L bonded to C(1); on R bonded to H(4) as HBr
    #   4  H  L+R      -- N-H proton; on L bonded to N(2); on R bonded to Br(3)
    #
    # Bond changes: break {1-3, 2-4}; form {1-2, 3-4}.
    left [
        node [ id 3 label "Br" ]
        node [ id 4 label "H"  ]
        edge [ source 1 target 3 label "-" ]
        edge [ source 2 target 4 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "N" ]
    ]
    right [
        node [ id 3 label "Br" ]
        node [ id 4 label "H"  ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 3 target 4 label "-" ]
    ]
]
