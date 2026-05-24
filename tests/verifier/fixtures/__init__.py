"""Fixtures for adversarial verifier tests.

Builds minimal-but-valid certificates per rule by combining the rule's
real GML body with a synthetic 1-firing derivation graph and witness.
This stays grounded in the real rule library (so atom-map and
conservation checks operate on the actual GML the producer emits)
while avoiding the cost of running the full pipeline for each of the
12 macrocyclization rules.
"""
from .builders import build_minimal_certificate, NEW_RULES, NEW_RULE_REAGENT_MASS, ATOM_MAP_BREAK

__all__ = [
    "build_minimal_certificate",
    "NEW_RULES",
    "NEW_RULE_REAGENT_MASS",
    "ATOM_MAP_BREAK",
]
