"""Atom-economy objectives over the hyperflow IR.

Two objectives, always reported separately, never collapsed into a
weighted sum (proposal §3.3):

- *Bond-level* expelled mass: Σ flow[e] × expelled_mass[e] — the theoretical
  ceiling of the disconnection, from the composed rule's atom map.

- *Process-level* expelled mass: Σ flow[e] × (expelled_mass[e] + reagent_mass[e]) —
  charges each firing with its activator/coupling-agent mass.

Both are *minimized*; maximum atom economy = minimum expelled mass.
"""
from __future__ import annotations

from .ir import HyperFlowIR, LinearObjective


def bond_level_objective(ir: HyperFlowIR) -> LinearObjective:
    return LinearObjective(
        coeffs={e.id: e.expelled_mass_g_per_mol for e in ir.hyperedges},
        minimize=True,
        name="bond_level_expelled_mass",
    )


def process_level_objective(ir: HyperFlowIR) -> LinearObjective:
    return LinearObjective(
        coeffs={e.id: e.expelled_mass_g_per_mol + e.reagent_mass_g_per_mol
                for e in ir.hyperedges},
        minimize=True,
        name="process_level_expelled_mass",
    )


def evaluate(ir: HyperFlowIR, flow: dict[str, int], obj: LinearObjective) -> float:
    return sum(flow.get(e.id, 0) * obj.coeffs.get(e.id, 0.0) for e in ir.hyperedges)
