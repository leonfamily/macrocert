rule [
    ruleID "hwe_olefination (intramolecular Horner-Wadsworth-Emmons, beta-keto phosphonate + aldehyde -> alkene + dialkyl phosphate)"
    # L: phosphonate alpha-C(1)-H(2) bonded to P(3) carrying P=O(4); aldehyde C(5)=O(6).
    # See docs/hwe_olefination_research.md §2 (atom-mapped DPO scheme) and §10
    # (proposed GML structure). Atoms 1 and 5 are the *retained* alkene carbons;
    # atoms 2, 3, 4, 6 plus the off-rule (RO)x decorations on atom 3 form the
    # dialkyl phosphate byproduct. The two OR groups on P live in substrate
    # context (off-rule) so the rule body is phosphonate-variant agnostic
    # (dimethyl / diethyl / Still-Gennari / Ando are all selected via
    # reagent_mass_alternatives in the .meta.yaml file).
    left [
        node [ id 2 label "H" ]                # alpha-H of phosphonate, deprotonated by base
        edge [ source 1 target 2 label "-" ]    # alpha-C-H bond, broken
        edge [ source 1 target 3 label "-" ]    # alpha-C-P bond, broken (C=C replaces it on R)
        edge [ source 5 target 6 label "=" ]    # aldehyde C=O double bond, broken (the O migrates to P)
    ]
    context [
        node [ id 1 label "C" ]                # phosphonate alpha-C (sp3 -> sp2 alkene C); retained ring atom
        node [ id 3 label "P" ]                # phosphorus of phosphonate, retained in byproduct
        node [ id 4 label "O" ]                # P=O of phosphonate, retained across L -> R
        node [ id 5 label "C" ]                # aldehyde C (sp2 -> sp2 alkene C); retained ring atom
        node [ id 6 label "O" ]                # aldehyde O, migrates to P in R (becomes one of the phosphate O's)
        edge [ source 3 target 4 label "=" ]    # P=O bond preserved
    ]
    # R: new C=C alkene (1=5) closes the macrocycle; new P-O bond (3-6) and
    # protonated phosphate O-H (2-6) form the (RO)2P(O)OH byproduct (atoms
    # 2, 3, 4, 6 + the two off-rule OR decorations on atom 3).
    right [
        node [ id 2 label "H" ]
        edge [ source 1 target 5 label "=" ]    # new C=C alkene (ring closure)
        edge [ source 3 target 6 label "-" ]    # new P-O bond (aldehyde O migrates to P)
        edge [ source 2 target 6 label "-" ]    # alpha-H becomes the protonated phosphate O-H
    ]
]
