"""
Layer C demo: integer-hyperflow ILP with pyscipopt.

A *toy* of the proposal's §3.3 formulation, with no MØD dependency. Uses
a hand-built reaction hypergraph to exercise:

  * integer multiplicities f_e ≥ 0 on each hyperedge (reaction firing count),
  * flow conservation at every molecule vertex,
  * a single firing of a designated ring-closing reaction (the constraint that
    forces a macrocyclization in the route),
  * a step budget Σ f_e ≤ k,
  * a linear atom-economy objective: minimize expelled atomic mass = maximize AE.

Output: optimal flow vector, certificate of optimality (SCIP dual / status).
With the network defined here, the closure-by-lactamization route beats
closure-by-RCM-with-protecting-group-detour at the chosen weights.

Once `import mod` works natively, the same formulation is wired to MØD via
mod.Flow over a real derivation graph.
"""
from __future__ import annotations
from dataclasses import dataclass
from pyscipopt import Model


# --- Hypergraph definition ---------------------------------------------------
@dataclass(frozen=True)
class Hyperedge:
    """A reaction: consumes `consumes` (with multiplicities), produces `produces`.
    `expelled_mass` is the byproduct mass (g/mol) — the atom-economy penalty.
    """
    name: str
    consumes: dict[str, int]
    produces: dict[str, int]
    expelled_mass: float
    is_macrocyclization: bool = False


vertices = [
    "B_acid",     # carboxylic-acid-bearing building block
    "B_amine",    # amine-bearing building block
    "B_ene_a",    # alkene-bearing arm A (for RCM)
    "B_ene_b",    # alkene-bearing arm B (for RCM)
    "PG_arm",     # arm protected (PG = protecting group)
    "open_chain_amide",     # amide-coupled seco-precursor (pre-closure)
    "macrolactam",          # closed via macrolactamization (TARGET)
    "open_chain_diene",     # seco-precursor for RCM
    "macrocarbocycle",      # closed via RCM (alternative target)
]

reactions = [
    Hyperedge(
        name="amide_coupling",
        consumes={"B_acid": 1, "B_amine": 1},
        produces={"open_chain_amide": 1},
        expelled_mass=18.02,  # H2O
    ),
    Hyperedge(
        name="macrolactamization_closure",
        consumes={"open_chain_amide": 1},
        produces={"macrolactam": 1},
        expelled_mass=18.02,  # H2O (process-level activator mass ignored here)
        is_macrocyclization=True,
    ),
    Hyperedge(
        name="protect_arm",
        consumes={"B_ene_a": 1},
        produces={"PG_arm": 1},
        expelled_mass=15.03,  # methyl loss as a stand-in for PG installation
    ),
    Hyperedge(
        name="couple_ene_arms",
        consumes={"PG_arm": 1, "B_ene_b": 1},
        produces={"open_chain_diene": 1},
        expelled_mass=0.0,  # idealised
    ),
    Hyperedge(
        name="RCM_closure",
        consumes={"open_chain_diene": 1},
        produces={"macrocarbocycle": 1},
        expelled_mass=28.05,  # ethylene
        is_macrocyclization=True,
    ),
]


# --- ILP -------------------------------------------------------------------
def solve(target: str, k_max: int = 6) -> None:
    m = Model(f"hyperflow_to_{target}")
    f = {r.name: m.addVar(name=f"f_{r.name}", vtype="I", lb=0, ub=k_max) for r in reactions}

    # Sources: building blocks may be drawn from infinite supply.
    src = {v: m.addVar(name=f"src_{v}", vtype="I", lb=0)
           for v in ["B_acid", "B_amine", "B_ene_a", "B_ene_b"]}
    sink_target = m.addVar(name="sink", vtype="I", lb=1, ub=1)  # produce exactly 1 target

    # Flow conservation at every vertex: in = out.
    for v in vertices:
        produced = sum(f[r.name] * r.produces.get(v, 0) for r in reactions)
        consumed = sum(f[r.name] * r.consumes.get(v, 0) for r in reactions)
        net_in   = src.get(v, 0)
        net_out  = sink_target if v == target else 0
        m.addCons(produced + net_in == consumed + net_out, name=f"flow_{v}")

    # Exactly one firing of a macrocyclization rule.
    m.addCons(sum(f[r.name] for r in reactions if r.is_macrocyclization) == 1,
              name="exactly_one_ring_closure")

    # Step budget.
    m.addCons(sum(f[r.name] for r in reactions) <= k_max, name="step_budget")

    # Objective: minimize total expelled atomic mass.
    m.setObjective(sum(f[r.name] * r.expelled_mass for r in reactions), "minimize")

    m.hideOutput()
    m.optimize()
    status = m.getStatus()
    print(f"target={target}  status={status}  expelled_mass={m.getObjVal():.2f} g/mol")
    if status == "optimal":
        for r in reactions:
            v = m.getVal(f[r.name])
            if v > 0.5:
                print(f"    fires x{int(v)}  {r.name}  (-{r.expelled_mass:g} g/mol byproduct)")
    else:
        print("    NO ROUTE — infeasibility certificate would be emitted in the real pipeline.")


if __name__ == "__main__":
    solve("macrolactam")        # expected: amide_coupling + macrolactamization
    solve("macrocarbocycle")    # expected: protect + couple + RCM
