rule [
    ruleID "transannular diels-alder exo ([4+2] cycloaddition, 0 byproduct, exo face)"
    # Stereo-aware sibling of transannular_diels_alder.gml. Same DPO body
    # (L,K,R) for the bond rewrite, with tetrahedral fixed chirality on
    # the 4 new sp3 centres (1, 4, 5, 6) on the R side encoding the
    # exo face of approach.
    #
    # Endo/exo encoding rationale: see
    # docs/workstream_f_tda_stereo.md §2 and
    # docs/stereo_encoding_procedure.md §3.3. This rule is the chirality
    # ENANTIOMER of transannular_diels_alder_endo.gml at every new sp3
    # centre: the two wildcard substituent IDs on each centre are
    # swapped (an odd permutation at each centre, flipping the face of
    # approach for the concerted [4+2]).
    #
    # The original symmetric (stereo-agnostic) rule
    # transannular_diels_alder.gml is kept untouched for backward
    # compatibility; stereo-aware runspecs select the endo/exo siblings
    # via the ``tda_stereo_aware`` rule set (see _index.yaml).
    #
    # Citations: as in transannular_diels_alder_endo.gml. The exo
    # outcome is observed for some TDA substrates lacking carbonyl
    # secondary-orbital stabilisation; see Lamothe-Ndibwami-Deslongchamps
    # 1988 (DOI:10.1016/S0040-4039(00)82005-5) for the
    # macrocycle-preorganisation analysis.
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
        # Wildcard substituents to satisfy MØD's degree-4 requirement
        # for tetrahedral configurations at load time (same scheme as
        # the endo sibling).
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
    right [
        edge [ source 1 target 2 label "-" ]
        edge [ source 2 target 3 label "=" ]
        edge [ source 3 target 4 label "-" ]
        edge [ source 5 target 6 label "-" ]
        edge [ source 1 target 6 label "-" ]
        edge [ source 4 target 5 label "-" ]
        # Exo: same bracket lists as endo with the two wildcard
        # substituent IDs SWAPPED on every centre (one transposition
        # per centre -- odd permutation, enantiomer face).
        # Per the aconitase canonical example
        # (external/mod/examples/py/030_stereo/320_aconitase.py:54-58),
        # stereo-on-right is declared WITHOUT repeating the label.
        node [ id 1 stereo "tetrahedral[2, 6, 12, 11]!" ]
        node [ id 4 stereo "tetrahedral[3, 5, 42, 41]!" ]
        node [ id 5 stereo "tetrahedral[4, 6, 52, 51]!" ]
        node [ id 6 stereo "tetrahedral[1, 5, 62, 61]!" ]
    ]
]
