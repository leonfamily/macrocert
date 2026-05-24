rule [
    ruleID "cross_coupling_sonogashira (R-C#C-H + Ar-Br -> R-C#C-Ar + HBr)"
    # Sonogashira terminal-alkyne / aryl-halide cross-coupling for
    # macrocyclization. Bond-level model per Sonogashira 1975
    # (DOI:10.1016/S0040-4039(00)91094-3) and the modern Pd/Cu
    # mechanism review (Chinchilla & Najera 2007, DOI:10.1021/cr050992x):
    # Cu(I) abstracts the terminal alkyne H to form a Cu-acetylide,
    # which transmetalates to Pd, then reductive elimination forms the
    # new sp-sp2 C-C bond. Amine base (Et3N) absorbs HX.
    # Strict atom conservation: H+ migrates directly from terminal
    # alkyne to halide; no protic fiction needed.
    #
    # Atom map (Workstream C research §Appendix, docs/cross_coupling_research.md):
    #   1  C  context  -- internal sp C of alkyne, retained_root
    #   2  C  context  -- terminal sp C of alkyne (loses H, gains aryl)
    #   3  H  L+R      -- terminal alkyne H; on L bonded to C(2); on R bonded to Br(5)
    #   4  C  context  -- ipso aryl C bonded to halide
    #   5  Br L+R      -- leaving halide; on L bonded to C(4); on R bonded to H(3) as HBr
    #
    # Bond changes: break {2-3, 4-5}; form {2-4, 3-5}.
    # The alkyne triple bond 1#2 is preserved (in context), as is the
    # alkyne sp-hybridization at C(1) and C(2).
    left [
        node [ id 3 label "H"  ]
        node [ id 5 label "Br" ]
        edge [ source 2 target 3 label "-" ]
        edge [ source 4 target 5 label "-" ]
    ]
    context [
        node [ id 1 label "C" ]
        node [ id 2 label "C" ]
        node [ id 4 label "C" ]
        edge [ source 1 target 2 label "#" ]
    ]
    right [
        node [ id 3 label "H"  ]
        node [ id 5 label "Br" ]
        edge [ source 2 target 4 label "-" ]
        edge [ source 3 target 5 label "-" ]
    ]
]
