import pytest

from macrocert.spec.runspec import load_runspec
from macrocert.spec.target import encode_target


def test_smiles_target_forbidden(tmp_path):
    f = tmp_path / "x.smi"
    f.write_text("O=C1CCCCCCCCCCCN1")
    with pytest.raises(ValueError, match=r"SMILES targets are forbidden"):
        encode_target(f, ring_size=13)


def test_toy_macrolactam_has_13_ring():
    spec = load_runspec("data/targets/toy_macrolactam")
    encoded = encode_target(
        "data/targets/toy_macrolactam/" + spec.target.structure_path,
        ring_size=spec.target.ring_size,
        name=spec.name,
    )
    assert len(encoded.ring_atom_indices) == 13
