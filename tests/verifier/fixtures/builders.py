"""Minimal certificate builders for adversarial tests.

For each rule in ``NEW_RULES``, ``build_minimal_certificate`` produces a
self-consistent certificate JSON suitable as a starting point for
mutation tests. The composed_rule's GML is the *real* rule body from
``data/rules/{rule}.gml`` — every conservation, atom-map, and
expelled-mass check the verifier runs operates on the same GML the
producer ships, so a mutation that escapes the verifier here would
also escape it in production.

What is synthetic (not from the pipeline):

  - derivation_graph: 3 vertices (precursor → product + byproduct)
    bridged by a single macrocyclization edge. Sufficient to exercise
    flow-balance, step-budget, and macrocyclization-uniqueness checks
    in :mod:`macrocert.verifier.verify`.
  - solver_witness: optimal, dual_bound == obj_value == expelled_mass
    (a single firing's bond-level mass).
  - spec_hash: opaque 64-char string; the verifier doesn't validate it.

This is Option A-lite: real GMLs (the part the verifier cares most
about) + synthetic plumbing. The full pipeline path is still
exercised by the panel artifacts (``artifacts/panel/lactone_*``,
``artifacts/toy_macrolactam/``) and by the existing
``test_adversarial.py`` cases against those.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from macrocert.verifier.conservation import expelled_mass_g_per_mol

# The 9 rules added 2026-05-24 (Workstream C). macrolactamization, rcm,
# and transannular_diels_alder predate this expansion and are already
# covered by the existing toy_macrolactam fixture.
NEW_RULES: tuple[str, ...] = (
    "macrolactonization",
    "aryl_etherification",
    "biaryl_etherification",
    "c_h_dehydrogenative_coupling",
    "cross_coupling_suzuki",
    "cross_coupling_negishi",
    "cross_coupling_buchwald",
    "cross_coupling_sonogashira",
    "cross_coupling_stille",
)

# Process-level reagent masses, pulled from data/rules/*.meta.yaml.
# Only used to populate the synthetic derivation_graph edge; the
# verifier does not currently re-check process AE against the rule
# library, but downstream tooling does, so we keep the values honest.
NEW_RULE_REAGENT_MASS: dict[str, float] = {
    "macrolactonization": 568.0,
    "aryl_etherification": 1094.0,
    "biaryl_etherification": 326.0,
    "c_h_dehydrogenative_coupling": 50.0,
    "cross_coupling_suzuki": 306.0,
    "cross_coupling_negishi": 30.0,
    "cross_coupling_buchwald": 300.0,
    "cross_coupling_sonogashira": 427.0,
    "cross_coupling_stille": 263.0,
}

# Per-rule atom-map break: a (needle, replacement) pair that swaps the
# label of a node that appears in both L and R. The replacement chooses
# a chemically nearby element that's tabulated in
# verifier.conservation._ATOMIC_MASS, so the failure mode is a
# label-disagreement L↔R, not a missing-atomic-mass exception.
#
# The needle MUST be the canonical GML string as it appears in the
# *left* block (we replace only the first occurrence). The verifier
# then sees L=(replacement), R=(needle's element) and returns 10.
ATOM_MAP_BREAK: dict[str, tuple[str, str]] = {
    # macrolactonization: O on the byproduct hydroxyl (id 2) → S
    "macrolactonization": ('id 2 label "O"', 'id 2 label "S"'),
    # aryl_etherification: leaving F (id 2) → Cl
    "aryl_etherification": ('id 2 label "F"', 'id 2 label "Cl"'),
    # biaryl_etherification: same atom map as aryl_eth (F → Cl)
    "biaryl_etherification": ('id 2 label "F"', 'id 2 label "Cl"'),
    # c_h_dehydrogenative_coupling: byproduct H (id 7) → F
    "c_h_dehydrogenative_coupling": ('id 7 label "H"', 'id 7 label "F"'),
    # cross_coupling_suzuki: boronate B (id 3) → N (both tabulated)
    "cross_coupling_suzuki": ('id 3  label "B"  ', 'id 3  label "N"  '),
    # cross_coupling_negishi: Zn (id 3) → Cu
    "cross_coupling_negishi": ('id 3 label "Zn"', 'id 3 label "Cu"'),
    # cross_coupling_buchwald: leaving Br (id 3) → Cl
    "cross_coupling_buchwald": ('id 3 label "Br"', 'id 3 label "Cl"'),
    # cross_coupling_sonogashira: leaving Br (id 5) → Cl
    "cross_coupling_sonogashira": ('id 5 label "Br"', 'id 5 label "Cl"'),
    # cross_coupling_stille: opaque Sn (id 3) → Si (both tabulated; Si
    # mass 28.085 vs Sn 118.710 — large delta exposes mass-recompute).
    "cross_coupling_stille": ('id 3 label "Sn"', 'id 3 label "Si"'),
}

# Repo-rooted path to the rule library. Tests run from the repo root
# (see existing test_conservation.py which uses the same relative
# pattern: ``open("tests/fixtures/macrolactamization_baseline.gml")``).
_RULES_DIR = Path("data/rules")


def build_minimal_certificate(rule_id: str) -> dict[str, Any]:
    """Construct a verifies-clean certificate around the given rule.

    The certificate uses the rule's real GML body so that conservation,
    atom-map, and expelled-mass checks operate on the actual rule.
    Flow / witness scaffolding is synthetic (1 firing of 1 edge).
    """
    gml = (_RULES_DIR / f"{rule_id}.gml").read_text()
    mass = expelled_mass_g_per_mol(gml, retained_root_atom=1)
    reagent = NEW_RULE_REAGENT_MASS[rule_id]
    return {
        "composed_rule": {
            "gml": gml,
            "expelled_mass_g_per_mol": mass,
            "retained_root_atom": 1,
            "rule_ids_traced": [rule_id],
            "atom_map": {},
        },
        "derivation_graph": {
            "hyperedges": [
                {
                    "id": "e1",
                    "is_macrocyclization": True,
                    "expelled_mass_g_per_mol": mass,
                    "reagent_mass_g_per_mol": reagent,
                    "rule_id": rule_id,
                    "sources": ["S"],
                    "targets": ["P", "B"],
                }
            ],
            "sources": ["S"],
            "sink": "P",
            "max_steps": 1,
            "vertices": [
                {"id": "S", "label": "precursor"},
                {"id": "P", "label": "product"},
                {"id": "B", "label": "byproduct"},
            ],
        },
        "flow": {"e1": 1},
        "solver_witness": {
            "kind": "optimal",
            "dual_bound": mass,
            "obj_value": mass,
        },
        "spec_hash": "0" * 64,
        "schema_version": "1.0",
        "energetics_dependencies": None,
    }
