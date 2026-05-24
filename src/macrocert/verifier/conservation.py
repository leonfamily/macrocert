"""DPO rule conservation re-check.

A DPO rule `L ← K → R` is well-formed when:
  - Every node ID shared between sides has the same element label and charge
  - The K (context) set is the intersection of nodes preserved across L and R
  - Atoms in (L ∪ K) but not in (R ∪ K) are *deleted* (expelled fragments)
  - Atoms in (R ∪ K) but not in (L ∪ K) are *created* — disallowed except for
    rules explicitly tagged as adding atoms (e.g., hydration); v0 flags them

For mass conservation at the *rule* level, we report:
  - balanced: atoms-deleted == atoms-created (multisets, by element+charge)
  - net_expelled: multiset of atoms in L not retained in R
  - net_incorporated: multiset of atoms in R not present in L

This module is import-isolated from MØD per the verifier trust property.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .gml_reader import GMLRule, GMLSide, parse_rule


@dataclass(frozen=True)
class ConservationResult:
    ok: bool
    reason: str = ""
    balanced: bool = True
    net_expelled: tuple[tuple[str, int], ...] = ()
    net_incorporated: tuple[tuple[str, int], ...] = ()


def check_rule_conservation(gml_text: str) -> ConservationResult:
    try:
        rule = parse_rule(gml_text)
    except Exception as e:
        return ConservationResult(ok=False, reason=f"GML parse error: {e}")

    l_atoms, k_atoms, r_atoms = rule.left.nodes, rule.context.nodes, rule.right.nodes

    for nid, n_l in l_atoms.items():
        n_r = r_atoms.get(nid)
        if n_r is not None and (n_l.label, n_l.charge) != (n_r.label, n_r.charge):
            return ConservationResult(
                ok=False,
                reason=(
                    f"node {nid} differs between L and R: "
                    f"({n_l.label},{n_l.charge}) vs ({n_r.label},{n_r.charge})"
                ),
            )
    for nid, n_k in k_atoms.items():
        n_l = l_atoms.get(nid)
        n_r = r_atoms.get(nid)
        for other_name, other in (("L", n_l), ("R", n_r)):
            if other is not None and (n_k.label, n_k.charge) != (other.label, other.charge):
                return ConservationResult(
                    ok=False,
                    reason=(
                        f"context node {nid} disagrees with {other_name}: "
                        f"({n_k.label},{n_k.charge}) vs ({other.label},{other.charge})"
                    ),
                )

    l_total = _atom_counter(rule.left, rule.context)
    r_total = _atom_counter(rule.right, rule.context)
    net_expelled = _subtract(l_total, r_total)
    net_incorporated = _subtract(r_total, l_total)

    for nid, n_l in l_atoms.items():
        if nid in k_atoms or nid in r_atoms:
            continue
        if not _edges_internal_to_left_only(rule, nid):
            return ConservationResult(
                ok=False,
                reason=(
                    f"deleted atom {nid} ({n_l.label}) still has edges crossing "
                    "into the preserved scaffold"
                ),
            )

    balanced = (net_expelled == net_incorporated == Counter())
    return ConservationResult(
        ok=True,
        balanced=balanced,
        net_expelled=_freeze(net_expelled),
        net_incorporated=_freeze(net_incorporated),
    )


def expelled_mass_g_per_mol(gml_text: str) -> float:
    """Bond-level Trost expelled mass from the rule's atom-map: ΣmW(L\\R).

    This is the *only* place expelled_mass is computed for the certificate;
    the producer must not store it as metadata. Recomputed by the verifier
    against the same atom-map, so tampering is detectable.
    """
    rule = parse_rule(gml_text)
    expelled = _subtract(
        _atom_counter(rule.left, rule.context),
        _atom_counter(rule.right, rule.context),
    )
    return sum(_atomic_mass(elem) * n for (elem, _charge), n in expelled.items())


def _atom_counter(side: GMLSide, context: GMLSide) -> Counter:
    c: Counter = Counter()
    for nd in side.nodes.values():
        c[(nd.label, nd.charge)] += 1
    for nd in context.nodes.values():
        if nd.id not in side.nodes:
            c[(nd.label, nd.charge)] += 1
    return c


def _subtract(a: Counter, b: Counter) -> Counter:
    out: Counter = Counter()
    for k, n in a.items():
        diff = n - b.get(k, 0)
        if diff > 0:
            out[k] = diff
    return out


def _freeze(c: Counter) -> tuple[tuple[str, int], ...]:
    return tuple(sorted((f"{elem}{charge:+d}" if charge else elem, n) for (elem, charge), n in c.items()))


def _edges_internal_to_left_only(rule: GMLRule, atom_id: int) -> bool:
    for e in rule.left.edges:
        if atom_id in (e.source, e.target):
            other = e.target if e.source == atom_id else e.source
            if other in rule.right.nodes or other in rule.context.nodes:
                return False
    return True


_ATOMIC_MASS: dict[str, float] = {
    "H": 1.008, "D": 2.014, "T": 3.016,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998,
    "P": 30.974, "S": 32.06, "Cl": 35.45, "Br": 79.904, "I": 126.904,
    "B": 10.81, "Si": 28.085, "Na": 22.990, "K": 39.098, "Mg": 24.305,
    "Ca": 40.078, "Zn": 65.38, "Cu": 63.546, "Fe": 55.845, "Ni": 58.693,
    "Pd": 106.42, "Pt": 195.084, "Ru": 101.07, "Rh": 102.906,
}


def _atomic_mass(elem: str) -> float:
    if elem not in _ATOMIC_MASS:
        raise ValueError(f"atomic mass not tabulated for element {elem!r}")
    return _ATOMIC_MASS[elem]
