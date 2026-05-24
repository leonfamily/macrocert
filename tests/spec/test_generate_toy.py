"""Layer-B smoke: build a DG for the toy macrolactam target.

The MØD strategy is invoked end-to-end. Asserts the expected vertex
count (4: seco, water, macrolactam, linear dimer) and the 2 reaction
edges (1 intramolecular cyclization + 1 intermolecular oligomerization).
The M2 strategy will add a predicate to suppress the intermolecular
path; until then we treat the dimer as expected output.
"""
from macrocert.generate import build_dg_for_runspec
from macrocert.spec.rules import load_rule_library
from macrocert.spec.runspec import load_runspec


def test_generates_4_vertices_2_edges():
    spec = load_runspec("data/targets/toy_macrolactam")
    lib = load_rule_library("data/rules")
    result = build_dg_for_runspec(
        spec, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    assert result.dg.numVertices == 4
    assert result.dg.numEdges == 2
    smiles = {v.graph.smiles for v in result.dg.vertices}
    assert "O" in smiles                             # water
    assert "C1(CCCCCCCCCCCN1)=O" in smiles           # macrolactam target


def test_stereo_enforcement_constructs_labelsettings_for_dg(monkeypatch, tmp_path):
    """Workstream F (Component 1): with ``stereo_enforcement: true`` the
    ``DG`` is constructed with the 3-arg ``LabelSettings`` form (see
    docs/mod_stereo_reference.md §2.3 and
    external/mod/libs/libmod/src/mod/Config.hpp:82-118), i.e.
    ``LabelSettings(LabelType.Term, LabelRelation.Specialisation,
    LabelRelation.Specialisation)`` — which flips ``withStereo=true``.

    With the flag off, ``DG`` is constructed with the 2-arg
    ``LabelSettings(LabelType.Term, LabelRelation.Specialisation)`` —
    ``withStereo=false`` but ``LabelType.Term`` is now the default so
    that rule-side wildcard labels (``label "*"``) in the α-C overlays
    on ``macrolactamization.gml`` / ``macrolactonization.gml`` work as
    unification variables. See docs/workstream_f_alpha_c_overlays.md.

    NB: this is the divergence captured in
    ``docs/workstream_f_harness.md``. End-to-end execution of the
    existing rule library under ``withStereo=true`` hits
    ``MOD_ABORT`` in ``RC/Visitor/Stereo.hpp:406`` because MØD's rule
    composition (under ``Repeat``/``Parallel``) walks stereo
    configurations even for stereo-free rules. We therefore test the
    wiring at the constructor level rather than driving a full
    ``builder.execute`` under the on-path.

    We isolate the rule library to a tmp_path so that concurrent
    additions to ``data/rules/`` by other agents don't break this test.
    """
    from dataclasses import replace
    import shutil
    import mod
    import macrocert.generate.build_dg as build_dg_mod

    # Stage a minimal one-rule library in tmp_path so we are independent
    # of the in-flight contents of ``data/rules/``.
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    shutil.copy("data/rules/macrolactamization.gml", rules_dir / "macrolactamization.gml")
    shutil.copy(
        "data/rules/macrolactamization.meta.yaml",
        rules_dir / "macrolactamization.meta.yaml",
    )

    captured: dict[str, object] = {}
    real_dg = mod.DG

    def fake_dg(**kwargs):
        captured.update(kwargs)
        return real_dg(graphDatabase=kwargs.get("graphDatabase", []))

    monkeypatch.setattr(build_dg_mod.mod, "DG", fake_dg)

    spec = load_runspec("data/targets/toy_macrolactam")
    # Reduce the rules to a stereo-free one so that load_rule_library
    # resolves only macrolactamization.
    spec = replace(spec, rules=("macrolactamization",))
    spec_on = replace(spec, strategy=replace(spec.strategy, stereo_enforcement=True))
    lib = load_rule_library(rules_dir)
    try:
        build_dg_for_runspec(
            spec_on, library=lib, blocks_dir="data/building_blocks",
            target_dir="data/targets/toy_macrolactam",
        )
    except Exception:
        # The strategy may still fail under withStereo=true; we only
        # care that the LabelSettings was constructed and passed.
        pass
    assert "labelSettings" in captured, "stereo_enforcement=True must pass labelSettings to mod.DG"
    ls_on = captured["labelSettings"]
    # MØD exposes ``withStereo`` on LabelSettings.
    assert getattr(ls_on, "withStereo", True) is True
    # Reset capture and verify the off-path passes the 2-arg
    # LabelSettings (Term, Specialisation) — withStereo False but
    # LabelType.Term so wildcards in rules work.
    captured.clear()
    build_dg_for_runspec(
        spec, library=lib, blocks_dir="data/building_blocks",
        target_dir="data/targets/toy_macrolactam",
    )
    assert "labelSettings" in captured, (
        "default stereo_enforcement=False must still pass a 2-arg LabelSettings "
        "with LabelType.Term so rule-side wildcards work (see "
        "docs/workstream_f_alpha_c_overlays.md)."
    )
    ls_off = captured["labelSettings"]
    assert getattr(ls_off, "withStereo", True) is False, (
        "default stereo_enforcement=False must produce withStereo=false"
    )
