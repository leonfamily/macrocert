from pathlib import Path
from textwrap import dedent

import pytest

from macrocert.spec.rules import (
    STEREO_TREATMENTS,
    RuleMeta,
    load_rule_library,
)


def _write_rule(
    directory: Path,
    rule_id: str,
    classes: list[str],
    *,
    extra_meta: str = "",
) -> None:
    (directory / f"{rule_id}.gml").write_text(dedent(f"""
        rule [
            ruleID "{rule_id}"
            left    [ node [ id 1 label "C" ] ]
            context [ ]
            right   [ node [ id 1 label "C" ] ]
        ]
    """).strip())
    body = dedent(f"""
        reagent_mass_g_per_mol: 18.02
        classes: {classes}
        stereo_flags: []
        refs: []
        notes: ""
    """).strip()
    if extra_meta:
        body += "\n" + dedent(extra_meta).strip() + "\n"
    (directory / f"{rule_id}.meta.yaml").write_text(body)


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


# ---------------------------------------------------------------------------
# Stereo policy (Workstream F #36)
# ---------------------------------------------------------------------------


def test_stereo_treatment_default_is_match_enforced() -> None:
    """Rules without ``stereo_treatment`` parse as match_enforced — keeps
    macrolactam/lactone semantics unchanged for pre-#36 metadata."""
    meta = RuleMeta.from_dict({})
    assert meta.stereo_treatment == "match_enforced"
    assert meta.stereo_advisory == ""


def test_stereo_treatment_n_a_sp2_only_parses() -> None:
    meta = RuleMeta.from_dict({"stereo_treatment": "n_a_sp2_only"})
    assert meta.stereo_treatment == "n_a_sp2_only"
    assert meta.stereo_advisory == ""


def test_stereo_treatment_advisory_only_requires_advisory() -> None:
    """advisory_only without a stereo_advisory message is a parse error."""
    with pytest.raises(ValueError, match="advisory_only"):
        RuleMeta.from_dict({"stereo_treatment": "advisory_only"})


def test_stereo_treatment_advisory_only_with_message_parses() -> None:
    meta = RuleMeta.from_dict(
        {
            "stereo_treatment": "advisory_only",
            "stereo_advisory": "E/Z is geometry, not point chirality.",
        }
    )
    assert meta.stereo_treatment == "advisory_only"
    assert "geometry" in meta.stereo_advisory


def test_stereo_treatment_unknown_value_rejected() -> None:
    with pytest.raises(ValueError, match="unknown stereo_treatment"):
        RuleMeta.from_dict({"stereo_treatment": "bogus"})


def test_stereo_treatments_taxonomy_is_exactly_three() -> None:
    """The taxonomy is intentionally small. Adding a fourth treatment
    requires updating the pre-M5 gate, the cert provenance flow, and the
    workstream_f_stereo_policy doc — flag accidental additions here."""
    assert STEREO_TREATMENTS == frozenset(
        {"match_enforced", "n_a_sp2_only", "advisory_only"}
    )


def test_load_rule_library_threads_stereo_treatment(tmp_path: Path) -> None:
    _write_rule(
        tmp_path,
        "alpha",
        ["macrocyclization"],
        extra_meta="stereo_treatment: n_a_sp2_only",
    )
    _write_rule(
        tmp_path,
        "beta",
        ["macrocyclization"],
        extra_meta=(
            'stereo_treatment: advisory_only\n'
            'stereo_advisory: "atropisomerism is 3D-geometric"'
        ),
    )
    lib = load_rule_library(tmp_path)
    assert lib.rules["alpha"].meta.stereo_treatment == "n_a_sp2_only"
    assert lib.rules["beta"].meta.stereo_treatment == "advisory_only"
    assert "atropisomerism" in lib.rules["beta"].meta.stereo_advisory


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
