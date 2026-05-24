"""
Layer-A/B smoke test, MØD side.

Run *inside* the jakobandersen/mod Docker container:

    pixi run mod -e "exec(open('/workdir/scripts/smoke_mod.py').read())"
or:
    docker run --rm -v $PWD:/workdir -u $(id -u):$(id -g) \
        --platform linux/amd64 jakobandersen/mod \
        -e "exec(open('/workdir/scripts/smoke_mod.py').read())"

Verifies:
  - mod imports
  - SMILES → molecular graph (the "term" in the Lean analogy)
  - GML rule loads (the "inference rule")
  - Rule applies (DPO derivation) to a tiny seco-precursor model
  - The reaction network is built and its size is reported
This is the bare minimum that the Layer-A/B "specification + generation"
pipeline can express; the certifying ILP layer is exercised host-side.
"""
import mod  # available inside the container

# A. Specification (toy): a hypothetical seco-precursor with one acid + one amine.
seco = mod.smiles("OC(=O)CCCN", name="seco_precursor")
seco.print()

# Rule library: one disconnection schema (macrolactamization).
with open("/workdir/rules/macrolactamization.gml") as f:
    rule = mod.ruleGMLString(f.read())
rule.print()

# B. Generation: apply the rule once to the seco graph and inspect the network.
dg = mod.DG(graphDatabase=[seco])
with dg.build() as b:
    b.execute(mod.addSubset(seco) >> rule)

print(f"DG vertices (molecules): {dg.numVertices}")
print(f"DG edges (reactions):    {dg.numEdges}")

for v in dg.vertices:
    g = v.graph
    print(f"  V {g.name}  atoms={g.numVertices}  edges={g.numEdges}")
for e in dg.edges:
    srcs = [v.graph.name for v in e.sources]
    tgts = [v.graph.name for v in e.targets]
    print(f"  E  {srcs}  ->  {tgts}  (rule: {[r.name for r in e.rules]})")

dg.print()
print("MØD smoke test passed.")
