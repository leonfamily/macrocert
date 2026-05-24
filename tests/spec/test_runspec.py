from pathlib import Path
from textwrap import dedent

from macrocert.spec.runspec import load_runspec


def test_load_runspec_minimal(tmp_path: Path) -> None:
    (tmp_path / "runspec.yaml").write_text(dedent("""
        name: toy
        target:
          structure_path: structure.mol
          ring_size: 13
        blocks: [b_acid, b_amine]
        rules: [macrolactamization]
    """).strip())
    spec = load_runspec(tmp_path)
    assert spec.name == "toy"
    assert spec.target.ring_size == 13
    assert spec.target.structure_path == "structure.mol"
    assert spec.blocks == ("b_acid", "b_amine")
    assert spec.rules == ("macrolactamization",)
    assert spec.solver.backend == "mod"
    assert spec.solver.top_n == 10
    assert spec.energetics.enabled is False
    # Workstream F Component 1: stereo_enforcement defaults to False so
    # that legacy stereo-free runs continue to use the default 2-arg
    # LabelSettings path in build_dg.py.
    assert spec.strategy.stereo_enforcement is False


def test_load_runspec_with_stereo_enforcement(tmp_path: Path) -> None:
    """Workstream F (Component 1): the YAML key ``stereo_enforcement``
    under ``strategy`` flips MØD into 3-arg LabelSettings mode (see
    docs/mod_stereo_reference.md §2.3).
    """
    (tmp_path / "runspec.yaml").write_text(dedent("""
        name: stereo_on
        target:
          structure_path: structure.mol
          ring_size: 13
        blocks: [b]
        rules: [r]
        strategy:
          stereo_enforcement: true
    """).strip())
    spec = load_runspec(tmp_path)
    assert spec.strategy.stereo_enforcement is True


def test_content_hash_is_stable(tmp_path: Path) -> None:
    (tmp_path / "runspec.yaml").write_text(dedent("""
        name: toy
        target:
          structure_path: structure.mol
          ring_size: 13
        blocks: [b]
        rules: [r]
    """).strip())
    h1 = load_runspec(tmp_path).content_hash()
    h2 = load_runspec(tmp_path).content_hash()
    assert h1 == h2 and len(h1) == 64
