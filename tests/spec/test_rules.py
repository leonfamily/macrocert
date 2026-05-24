from pathlib import Path
from textwrap import dedent

from macrocert.spec.rules import load_rule_library


def _write_rule(directory: Path, rule_id: str, classes: list[str]) -> None:
    (directory / f"{rule_id}.gml").write_text(dedent(f"""
        rule [
            ruleID "{rule_id}"
            left    [ node [ id 1 label "C" ] ]
            context [ ]
            right   [ node [ id 1 label "C" ] ]
        ]
    """).strip())
    (directory / f"{rule_id}.meta.yaml").write_text(dedent(f"""
        reagent_mass_g_per_mol: 18.02
        classes: {classes}
        stereo_flags: []
        refs: []
        notes: ""
    """).strip())


def test_loads_rules_and_metadata(tmp_path: Path) -> None:
    _write_rule(tmp_path, "alpha", ["macrocyclization"])
    _write_rule(tmp_path, "beta", ["cross_coupling"])

    lib = load_rule_library(tmp_path)
    assert set(lib.rules) == {"alpha", "beta"}
    assert lib.rules["alpha"].meta.reagent_mass_g_per_mol == 18.02
    assert lib.rules["alpha"].in_class("macrocyclization")
    assert not lib.rules["beta"].in_class("macrocyclization")
    assert tuple(r.id for r in lib.in_class("macrocyclization")) == ("alpha",)


def test_missing_metadata_rejected(tmp_path: Path) -> None:
    _write_rule(tmp_path, "alpha", [])
    (tmp_path / "alpha.meta.yaml").unlink()
    try:
        load_rule_library(tmp_path)
    except FileNotFoundError as e:
        assert "alpha" in str(e)
    else:
        raise AssertionError("expected FileNotFoundError for missing metadata")


def test_rule_set_index(tmp_path: Path) -> None:
    _write_rule(tmp_path, "alpha", ["macrocyclization"])
    _write_rule(tmp_path, "beta", ["macrocyclization"])
    (tmp_path / "_index.yaml").write_text(dedent("""
        sets:
          all_macrocyclization: [alpha, beta]
    """).strip())
    lib = load_rule_library(tmp_path)
    members = lib.resolve_set("all_macrocyclization")
    assert {r.id for r in members} == {"alpha", "beta"}
