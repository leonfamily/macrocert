rule [
    ruleID "transannular diels-alder endo ([4+2] cycloaddition, 0 byproduct, endo face)"
    # Stereo-aware sibling of transannular_diels_alder.gml. Same DPO body
    # (L,K,R) for the bond rewrite — the [4+2] cycloaddition that turns
    # C(1)=C(2)-C(3)=C(4) + C(5)=C(6) into a cyclohexene — but adds
    # tetrahedral fixed chirality on the 4 new sp3 centres (1, 4, 5, 6)
    # on the R side, encoding the endo face of approach.
    #
    # Encoding rationale: see docs/workstream_f_tda_stereo.md §2.
    #
    # Endo/exo is the face on which the dienophile (5=6) approaches the
    # diene (1=2-3=4). It is a single binary choice for the concerted
    # [4+2]; the four new sp3 centres are NOT independent — once endo
    # is chosen, all four chiralities are fixed by the suprafacial-
    # suprafacial geometry. We therefore encode endo and exo as two
    # SIBLING RULES with mutually-odd bracket lists at each new sp3
    # centre (docs/mod_stereo_reference.md §4.3 advice).
    #
    # The original symmetric (stereo-agnostic) rule
    # transannular_diels_alder.gml is kept untouched for backward
    # compatibility with the existing M5 campaigns
    # (data/validation_panel/phoenix_reddy_cassaine_tda_2008/runspec.yaml
    # currently selects ``rules: all_macrocyclization`` which keeps the
    # symmetric rule). Stereo-aware runspecs opt in via
    # ``rules: tda_stereo_aware`` (see data/rules/_index.yaml).
    #
    # Citations:
    #   Deslongchamps lineage (TDA methodology):
    #     Lamothe, Ndibwami, Deslongchamps. Tetrahedron Lett. 1988,
    #     29, 1639 (DOI:10.1016/S0040-4039(00)82005-5) and 1641
    #     (DOI:10.1016/S0040-4039(00)82006-7).
    #   Phoenix, Reddy, Deslongchamps. J. Am. Chem. Soc. 2008, 130,
    #     13989-13995 (DOI:10.1021/ja805097s) -- the canonical
    #     macrocycle-preorganised TDA forming the cassaine tricycle.
    #     The cassaine product is endo (per macrocyclic preorganization,
    #     trans-decalin tricycle 5); see docs/cassaine_m5.md.
    #   Andersen et al. ICGT 2017 (DOI:10.1007/978-3-319-61470-0_4)
    #     for the DPO-with-stereo algebra.
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
        # MØD requires degree-4 at rule-load time for tetrahedral
        # configurations (Stereo/Inference.hpp::finalizeVertex). Each
        # cyclohexene sp3 atom keeps two ring neighbours after the
        # rewrite; we expose its two remaining (substrate-side)
        # substituents as wildcards. Wildcard IDs follow a deterministic
        # 2-digit convention: <center><slot> -- 11/12 for atom 1, 41/42
        # for atom 4, 51/52 for atom 5, 61/62 for atom 6.
        node [ id 11 label "*" ]
        node [ id 12 label "*" ]
        node [ id 41 label "*" ]
        node [ id 42 label "*" ]
        node [ id 51 label "*" ]
        node [ id 52 label "*" ]
        node [ id 61 label "*" ]
        node [ id 62 label "*" ]
        edge [ source 1 target 11 label "-" ]
        edge [ source 1 target 12 label "-" ]
        edge [ source 4 target 41 label "-" ]
        edge [ source 4 target 42 label "-" ]
        edge [ source 5 target 51 label "-" ]
        edge [ source 5 target 52 label "-" ]
        edge [ source 6 target 61 label "-" ]
        edge [ source 6 target 62 label "-" ]
    ]
    # R: cyclohexene -- two new sigma bonds (1-6, 4-5) and one remaining
    # endocyclic alkene (2=3). Zero byproduct: maximal atom economy.
    right [
        edge [ source 1 target 2 label "-" ]
        edge [ source 2 target 3 label "=" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 5 target 6 label "-" ]
        edge [ source 1 target 6 label "-" ]
        edge [ source 4 target 5 label "-" ]
        # Endo: all four sp3 centres listed in CANONICAL ascending-
        # ID order. Per docs/stereo_encoding_procedure.md §2.c the
        # convention is ascending real-neighbour IDs followed by the
        # two wildcard substituent IDs ascending. Endo / exo differ
        # by swapping the two substituent wildcards on each centre,
        # which is an odd permutation (one transposition) at every
        # centre -- the exo enantiomer at all four positions.
        # See docs/stereo_encoding_procedure.md §3.3.
        # Per the aconitase canonical example
        # (external/mod/examples/py/030_stereo/320_aconitase.py:54-58),
        # stereo-on-right is declared WITHOUT repeating the label
        # (the label lives in context; declaring it again in right
        # raises "Vertex N has a label both in 'context' and 'right'"
        # at MØD load time).
        node [ id 1 stereo "tetrahedral[2, 6, 11, 12]!" ]
        node [ id 4 stereo "tetrahedral[3, 5, 41, 42]!" ]
        node [ id 5 stereo "tetrahedral[4, 6, 51, 52]!" ]
        node [ id 6 stereo "tetrahedral[1, 5, 61, 62]!" ]
    ]
]
