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
