"""Workstream D — predicate framework smoke tests.

Counterpart of ``test_generate_toy.py``: the same toy macrolactam
target, but with ``strategy.predicates`` set. The intramolecular gate
plus the ring-size gate should remove the linear-dimer vertex and the
intermolecular oligomerization edge.
"""
from macrocert.generate import build_dg_for_runspec
from macrocert.generate.strategies import PredicateSpec
from macrocert.spec.rules import load_rule_library
from macrocert.spec.runspec import load_runspec


def test_predicates_parsed_from_yaml():
    spec = load_runspec("data/targets/toy_macrolactam_predicated")
    assert spec.strategy.predicates.is_intramolecular is True
    assert spec.strategy.predicates.ring_size_equals == 13


def test_predicates_absent_defaults_to_v0():
    spec = load_runspec("data/targets/toy_macrolactam")
    # Backward-compat: no predicates section in YAML => empty PredicateSpec.
    assert spec.strategy.predicates.is_intramolecular is False
    assert spec.strategy.predicates.ring_size_equals is None


def test_predicated_dg_has_3_vertices_1_edge():
    spec = load_runspec("data/targets/toy_macrolactam_predicated")
    lib = load_rule_library("data/rules")
    result = build_dg_for_runspec(
        spec, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam_predicated",
    )
    # v0 (unconditional) produces 4 vertices: seco, water, macrolactam,
    # linear dimer. With both predicates the dimer (intermolecular) and
    # any non-13 ring closures are filtered out, leaving 3 vertices and
    # the single intramolecular cyclization edge.
    assert result.dg.numVertices == 3
    assert result.dg.numEdges == 1
    smiles = {v.graph.smiles for v in result.dg.vertices}
    assert "O" in smiles                              # water
    assert "C1(CCCCCCCCCCCN1)=O" in smiles            # 13-membered lactam


def test_empty_predicate_spec_is_empty():
    assert PredicateSpec().is_empty()
    assert not PredicateSpec(is_intramolecular=True).is_empty()
    assert not PredicateSpec(ring_size_equals=13).is_empty()
    assert not PredicateSpec(enforce_ez_geometry={"rcm": "E"}).is_empty()
    assert not PredicateSpec(
        alcohol_partner_C_must_be_aromatic={"biaryl_etherification": True}
    ).is_empty()
    assert not PredicateSpec(
        alcohol_partner_C_must_be_sp3={"aryl_etherification": True}
    ).is_empty()


# ---------------------------------------------------------------------------
# Workstream D phase 2 — E/Z geometry filter
# ---------------------------------------------------------------------------
#
# Background: docs/mod_stereo_reference.md §1.5, §5.2 and Workstream F's
# audit established that MØD cannot enforce E/Z at match time
# (TrigonalPlanar::morphismIso is MOD_ABORT —
# external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/TrigonalPlanar.cpp:50-54).
# Workstream D's E/Z predicate fills the gap by reading the product
# SMILES from MØD's ``Graph::getSmiles()``
# (external/mod/libs/libmod/src/mod/graph/Graph.hpp:118) and inspecting
# ``Bond.GetStereo()`` via RDKit.
#
# Because MØD does not propagate E/Z through rule firing, end-to-end DG
# builds cannot today produce both an E and a Z product to discriminate
# between — every MØD-generated SMILES has STEREONONE on its new double
# bond. We therefore unit-test the predicate against mock derivations
# carrying hand-crafted SMILES with explicit ``/``\\`` directionality,
# which is the contract the upstream stereo-creating rules (Workstream F
# §4.2) will eventually satisfy.


class _MockGraph:
    """Minimal stand-in for ``mod::graph::Graph`` exposing ``smiles``.

    Mirrors the Python binding's read-only ``Graph.smiles`` property
    (external/mod/libs/pymod/src/mod/py/graph/Graph.cpp) for the purpose
    of unit-testing the rightPredicate; the predicate only touches the
    ``smiles`` accessor.
    """
    def __init__(self, smiles: str):
        self.smiles = smiles


class _MockRule:
    def __init__(self, name: str):
        self.name = name


class _MockDerivation:
    """Minimal stand-in for ``mod::Derivation``.

    C++ shape: ``left: GraphList, r: shared_ptr<Rule>, right: GraphList``
    — see external/mod/libs/libmod/src/mod/Derivation.hpp:23-49. The
    Python binding renames ``r`` to ``rule``
    (external/mod/libs/pymod/src/mod/py/Derivation.cpp:32). We expose
    *both* attributes so the predicate's compatibility fallback path is
    exercisable.
    """
    def __init__(self, rule_name: str, right_smiles):
        self.rule = _MockRule(rule_name)
        self.r = self.rule  # C++ name; predicate falls back to this
        self.right = [_MockGraph(s) for s in right_smiles]
        self.left = []


def test_ez_predicate_accepts_e_and_rejects_z():
    """Direct predicate unit test: with map {rcm: 'E'}, an E-product
    derivation is accepted and a Z-product derivation is rejected."""
    from macrocert.generate.strategies import _enforce_ez_geometry_factory

    pred = _enforce_ez_geometry_factory({"rcm": "E"})
    # The MØD rule's GML ruleID is "rcm (ring-closing metathesis, -C2H4)"
    # — see data/rules/rcm.gml:2. The predicate must match by prefix.
    rule_name = "rcm (ring-closing metathesis, -C2H4)"
    # 13-membered macrocyclic alkene with explicit /C=C/ → E.
    e_smiles = "C1CCCCC/C=C/CCCCC1"
    # Same skeleton with /C=C\ → Z.
    z_smiles = "C1CCCCC/C=C\\CCCCC1"
    assert pred(_MockDerivation(rule_name, [e_smiles])) is True
    assert pred(_MockDerivation(rule_name, [z_smiles])) is False


def test_ez_predicate_noop_for_other_rules():
    """When the firing rule isn't in the map, the predicate is a no-op
    (returns True) regardless of the product's geometry — including the
    stereo-undetermined STEREONONE case that MØD currently emits."""
    from macrocert.generate.strategies import _enforce_ez_geometry_factory

    pred = _enforce_ez_geometry_factory({"rcm": "E"})
    # macrolactamization product (no double bond at all) — would never
    # satisfy an E-filter, but must be accepted because the rule isn't
    # in the map.
    mla_name = "macrolactamization (amide ring closure, -H2O)"
    macrolactam = "C1(CCCCCCCCCCCN1)=O"
    assert pred(_MockDerivation(mla_name, [macrolactam])) is True
    # Even a Z-product survives when the rule isn't in the map.
    z_smiles = "C1CCCCC/C=C\\CCCCC1"
    assert pred(_MockDerivation(mla_name, [z_smiles])) is True


def test_ez_predicate_rejects_stereo_undetermined_products():
    """A SMILES with no ``/``\\`` directionality has STEREONONE on its
    double bond — RDKit's ``FindPotentialStereoBonds`` cannot infer a
    direction, so neither 'E' nor 'Z' matches. Documents the
    consequence of the MØD stereo gap (§5.2): until Workstream F adds
    stereo-creating rule annotations, an E/Z gate on the rcm rule
    rejects every product. This is intentional — the predicate is a
    *positive* filter."""
    from macrocert.generate.strategies import _enforce_ez_geometry_factory

    pred = _enforce_ez_geometry_factory({"rcm": "E"})
    rule_name = "rcm (ring-closing metathesis, -C2H4)"
    undetermined = "C1CCCCCC=CCCCCC1"  # no /\ directionality
    assert pred(_MockDerivation(rule_name, [undetermined])) is False


def test_ez_predicate_parsed_from_yaml(tmp_path):
    """YAML round-trip: ``strategy.predicates.enforce_ez_geometry`` is
    deserialised into the spec ``PredicateSpec.enforce_ez_geometry``
    dict with uppercased ``E``/``Z`` tokens. Verifies backward-compat
    keys ``is_intramolecular`` and ``ring_size_equals`` still parse.
    """
    from macrocert.spec.runspec import load_runspec

    runspec_path = tmp_path / "runspec.yaml"
    runspec_path.write_text(
        "name: ez_smoke\n"
        "target:\n"
        "  structure_path: structure.mol\n"
        "  ring_size: 13\n"
        "blocks:\n"
        "  - aminododecanoic_acid\n"
        "rules: macrolactamization\n"
        "strategy:\n"
        "  max_steps: 1\n"
        "  predicates:\n"
        "    enforce_ez_geometry:\n"
        "      rcm: e\n"  # lower-case to exercise normalisation
        "      transannular_diels_alder: Z\n"
    )
    spec = load_runspec(runspec_path)
    assert spec.strategy.predicates.enforce_ez_geometry == {
        "rcm": "E",
        "transannular_diels_alder": "Z",
    }
    # Default-off backwards compatibility: a runspec without the field
    # parses to enforce_ez_geometry=None.
    from macrocert.spec.runspec import PredicateSpec as SpecPS
    assert SpecPS().enforce_ez_geometry is None


def test_ez_predicate_yaml_rejects_invalid_token(tmp_path):
    """A bad geometry token raises immediately at YAML load time —
    misconfigured runspecs fail loud rather than silently producing an
    always-False predicate."""
    import pytest
    from macrocert.spec.runspec import load_runspec

    runspec_path = tmp_path / "runspec.yaml"
    runspec_path.write_text(
        "name: ez_bad\n"
        "target:\n"
        "  structure_path: structure.mol\n"
        "  ring_size: 13\n"
        "blocks: [aminododecanoic_acid]\n"
        "rules: macrolactamization\n"
        "strategy:\n"
        "  predicates:\n"
        "    enforce_ez_geometry: {rcm: 'cis'}\n"  # not E/Z
    )
    with pytest.raises(ValueError, match="expected 'E' or 'Z'"):
        load_runspec(runspec_path)


def test_ez_predicate_filters_rcm_to_e_only():
    """End-to-end: with ``enforce_ez_geometry: {rcm: 'E'}`` set, an RCM
    run on a flexible α,ω-diene substrate produces zero new
    cyclization edges (the stereo-free rule yields STEREONONE products
    which fail the gate). With the predicate disabled, the same run
    produces at least one RCM closure. This documents the current MØD
    stereo gap (docs/mod_stereo_reference.md §5.2): until a
    stereo-creating RCM rule is authored (Workstream F), the E/Z gate
    is necessarily a *blocking* filter, not a *selecting* filter.

    This is the closest end-to-end form of "filter RCM to E-only" that
    the current MØD substrate-and-rule library can express; once
    Workstream F adds explicit ``trigonalPlanar[...]!`` on rcm.gml's
    right side, the same test path will pass through E products and
    reject Z products separately.
    """
    from dataclasses import replace
    from macrocert.generate import build_dg_for_runspec
    from macrocert.spec.rules import load_rule_library
    from macrocert.spec.runspec import (
        PredicateSpec as SpecPS,
        load_runspec,
    )

    # Re-use the toy_macrolactam target shell (gives us a runspec dir
    # with a structure.mol); swap blocks/rules for a diene + rcm.
    spec = load_runspec("data/targets/toy_macrolactam")
    spec_ungated = replace(
        spec,
        blocks=("pentadecadiene",),
        rules=("rcm",),
    )
    spec_gated = replace(
        spec_ungated,
        strategy=replace(
            spec_ungated.strategy,
            predicates=SpecPS(enforce_ez_geometry={"rcm": "E"}),
        ),
    )
    lib = load_rule_library("data/rules")

    ungated = build_dg_for_runspec(
        spec_ungated, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    gated = build_dg_for_runspec(
        spec_gated, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    # The ungated DG should contain at least one RCM-closure edge
    # (substrate + ethylene + macrocycle). The gated DG should contain
    # strictly fewer edges (the predicate rejected the STEREONONE
    # product). This is the substrate-level analogue of "E-only".
    assert gated.dg.numEdges < ungated.dg.numEdges
    assert gated.dg.numEdges == 0


def test_ez_predicate_macrolactam_run_unaffected():
    """The map ``{rcm: 'E'}`` is a no-op on a macrolactamization-only
    run: the predicate's rule_name check filters out non-rcm
    derivations before touching the product SMILES, so the DG matches
    the v0 4-vertex / 2-edge baseline (toy_macrolactam)."""
    from dataclasses import replace
    from macrocert.generate import build_dg_for_runspec
    from macrocert.spec.rules import load_rule_library
    from macrocert.spec.runspec import PredicateSpec as SpecPS, load_runspec

    spec = load_runspec("data/targets/toy_macrolactam")
    spec = replace(
        spec,
        strategy=replace(
            spec.strategy,
            predicates=SpecPS(enforce_ez_geometry={"rcm": "E"}),
        ),
    )
    lib = load_rule_library("data/rules")
    result = build_dg_for_runspec(
        spec, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    # Same as test_generates_4_vertices_2_edges — the E/Z map is a no-op
    # because macrolactamization isn't in the rule_to_geometry map.
    assert result.dg.numVertices == 4
    assert result.dg.numEdges == 2


# ---------------------------------------------------------------------------
# Workstream D phase-3 — alcohol-partner discriminator predicates
# ---------------------------------------------------------------------------
#
# Motivation. data/rules/aryl_etherification.gml and
# data/rules/biaryl_etherification.gml have structurally identical
# bodies because MØD matches on element labels — atom 5 = O in both
# rules, and the phenolic-vs-aliphatic distinction at the alcohol
# partner C is invisible at the GML level. See
# docs/macroetherification_research.md §1.4 and
# docs/biaryl_etherification_research.md §1.2 / §2.2.
#
# Because the MØD Python binding does not expose the L→substrate morph
# mapping (external/mod/libs/pymod/src/mod/py/Derivation.cpp:8-39
# binds only `left`, `rule`, `right`), the implementation is a
# rightPredicate substructure-match on the product SMILES rather than
# a leftPredicate atom-by-atom check. The tests here exercise that
# product-side path with hand-crafted SMILES mock derivations — the
# same shape used by the E/Z predicate's unit tests above.


def test_alcohol_partner_aromatic_filters_biaryl_correctly():
    """With ``alcohol_partner_C_must_be_aromatic={biaryl_etherification: True}``,
    a derivation whose product carries an Ar-O-Ar bridge is accepted
    and one carrying Ar-O-C(sp3) only is rejected.

    The mock substrates use a 13-atom skeleton with the new bridge
    expressed in different hybridization contexts:
      - ``c1ccc(Oc2ccccc2)cc1`` is diphenyl ether — Ar-O-Ar.
      - ``c1ccc(OCC)cc1`` is phenetole — Ar-O-C(sp3).
    Only the former satisfies the biaryl-ether constraint.
    """
    from macrocert.generate.strategies import (
        _alcohol_partner_aromaticity_factory,
    )

    pred = _alcohol_partner_aromaticity_factory(
        {"biaryl_etherification": True}, require_aromatic=True
    )
    # data/rules/biaryl_etherification.gml:2 ruleID
    rname = "biaryl_etherification (Ar-O-Ar SNAr ring closure, -HF)"
    ar_o_ar = "c1ccc(Oc2ccccc2)cc1"       # diphenyl ether
    ar_o_alkyl = "c1ccc(OCC)cc1"          # phenetole (Ar-O-CH2-CH3)
    assert pred(_MockDerivation(rname, [ar_o_ar])) is True
    assert pred(_MockDerivation(rname, [ar_o_alkyl])) is False
    # Unmapped rule: predicate is a no-op (returns True regardless).
    mla_name = "macrolactamization (amide ring closure, -H2O)"
    assert pred(_MockDerivation(mla_name, [ar_o_alkyl])) is True


def test_alcohol_partner_sp3_filters_aryl_correctly():
    """Opposite gate. With
    ``alcohol_partner_C_must_be_sp3={aryl_etherification: True}``, an
    Ar-O-C(sp3) product is accepted and an Ar-O-Ar product is rejected.
    """
    from macrocert.generate.strategies import (
        _alcohol_partner_aromaticity_factory,
    )

    pred = _alcohol_partner_aromaticity_factory(
        {"aryl_etherification": True}, require_aromatic=False
    )
    # data/rules/aryl_etherification.gml:2 ruleID
    rname = "aryl_etherification (SNAr Ar-O-C(sp3) ring closure, -HF)"
    ar_o_alkyl = "c1ccc(OCC)cc1"          # phenetole — Ar-O-C(sp3)
    ar_o_ar = "c1ccc(Oc2ccccc2)cc1"       # diphenyl ether
    assert pred(_MockDerivation(rname, [ar_o_alkyl])) is True
    assert pred(_MockDerivation(rname, [ar_o_ar])) is False
    # Unmapped rule: predicate is a no-op.
    mla_name = "macrolactamization (amide ring closure, -H2O)"
    assert pred(_MockDerivation(mla_name, [ar_o_ar])) is True


def test_discriminator_predicates_off_by_default():
    """Empty PredicateSpec leaves DG unchanged from current behaviour.

    Backward-compat check: a RunSpec without the two new fields parses
    to ``alcohol_partner_C_must_be_aromatic=None`` and
    ``alcohol_partner_C_must_be_sp3=None``, and
    ``apply_rules_up_to_with_predicates`` reduces to the unconditional
    inner ``repeat`` block (``PredicateSpec.is_empty()`` short-circuits).
    The 4-vertex / 2-edge toy_macrolactam baseline must still hold.
    """
    from macrocert.generate import build_dg_for_runspec
    from macrocert.spec.rules import load_rule_library
    from macrocert.spec.runspec import (
        PredicateSpec as SpecPS,
        load_runspec,
    )

    # Defaults: no discriminator fields set.
    ps = SpecPS()
    assert ps.alcohol_partner_C_must_be_aromatic is None
    assert ps.alcohol_partner_C_must_be_sp3 is None

    # The existing toy_macrolactam RunSpec parses identically.
    spec = load_runspec("data/targets/toy_macrolactam")
    assert spec.strategy.predicates.alcohol_partner_C_must_be_aromatic is None
    assert spec.strategy.predicates.alcohol_partner_C_must_be_sp3 is None

    # End-to-end DG is the v0 baseline (4 vertices, 2 edges).
    lib = load_rule_library("data/rules")
    result = build_dg_for_runspec(
        spec, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    assert result.dg.numVertices == 4
    assert result.dg.numEdges == 2


def test_discriminator_predicates_parsed_from_yaml(tmp_path):
    """YAML round-trip for the two new fields. Lower-case bool tokens
    (``true``/``false``) parse to Python bools and survive into
    ``PredicateSpec``; an unsupported value type fails loud at load
    time (matches the EZ predicate's normalisation philosophy).
    """
    from macrocert.spec.runspec import load_runspec

    runspec_path = tmp_path / "runspec.yaml"
    runspec_path.write_text(
        "name: ether_discrim\n"
        "target:\n"
        "  structure_path: structure.mol\n"
        "  ring_size: 13\n"
        "blocks: [aminododecanoic_acid]\n"
        "rules: ether_macrocyclization\n"
        "strategy:\n"
        "  predicates:\n"
        "    alcohol_partner_C_must_be_aromatic:\n"
        "      biaryl_etherification: true\n"
        "    alcohol_partner_C_must_be_sp3:\n"
        "      aryl_etherification: true\n"
    )
    spec = load_runspec(runspec_path)
    assert spec.strategy.predicates.alcohol_partner_C_must_be_aromatic == {
        "biaryl_etherification": True,
    }
    assert spec.strategy.predicates.alcohol_partner_C_must_be_sp3 == {
        "aryl_etherification": True,
    }
