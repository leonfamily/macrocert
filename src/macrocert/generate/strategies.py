"""Generation strategies — Layer B.

A "strategy" in MØD is a programmable plan for applying rules to graphs
under explicit control. We compose them out of the primitives
`mod.addSubset`, `mod.repeat`, `mod.rightPredicate`, etc. Ring-size
application conditions and depth bounds live here, not in the GML.

Predicate framework (Workstream D)
-----------------------------------

MØD exposes two derivation-time hooks usable here:

* ``mod.leftPredicate[p](strat)`` — ``p(derivation)`` is consulted
  *before* the rule fires. Only ``derivation.left`` (the multiset of
  reactant graphs) and ``derivation.r`` (the rule) are valid.
* ``mod.rightPredicate[p](strat)`` — ``p(derivation)`` is consulted on
  the candidate product side. Both ``derivation.left`` and
  ``derivation.right`` are valid here.

References:
    external/mod/examples/py/020_dg/212_dgPredicate.py
    external/mod/libs/pymod/src/mod/py/dg/Strategies.cpp (lines 30-78,
    163-181)

Predicates are composed *outside-in* around the inner ``repeat`` block
so the constraints apply to every individual rule firing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .. spec.rules import RuleDef

import mod  # noqa: E402


# ---------------------------------------------------------------------------
# Predicate-spec dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PredicateSpec:
    """Declarative bundle of predicate parameters.

    Mirrors the YAML schema under ``strategy_predicates:`` in a RunSpec.
    All fields default to *off* — the empty PredicateSpec is the v0
    unconditional behaviour.

    ``enforce_ez_geometry`` is a Workstream D phase-2 addition: maps
    macrocert ``rule_id`` (e.g. ``"rcm"``) to ``"E"`` or ``"Z"``, and is
    consulted on the product side. The motivation is documented in
    ``docs/mod_stereo_reference.md`` §1.5 and §5.2 — MØD's
    ``TrigonalPlanar::morphismIso`` is ``MOD_ABORT`` so double-bond
    geometry cannot be enforced at match time. We instead filter
    candidate derivations by parsing the product SMILES through RDKit
    and inspecting ``Bond.GetStereo()``.
    """
    is_intramolecular: bool = False
    ring_size_equals: Optional[int] = None
    enforce_ez_geometry: Optional[dict] = None
    # Workstream D phase-3: per-rule_id bool maps that gate the two
    # ether siblings (data/rules/aryl_etherification.gml ↔
    # data/rules/biaryl_etherification.gml) by inspecting the new C-O
    # bridge in the product. See PredicateSpec in
    # ``macrocert.spec.runspec`` for the YAML schema and motivation.
    alcohol_partner_C_must_be_aromatic: Optional[dict] = None
    alcohol_partner_C_must_be_sp3: Optional[dict] = None

    def is_empty(self) -> bool:
        return (
            not self.is_intramolecular
            and self.ring_size_equals is None
            and not self.enforce_ez_geometry
            and not self.alcohol_partner_C_must_be_aromatic
            and not self.alcohol_partner_C_must_be_sp3
        )


# ---------------------------------------------------------------------------
# Public strategy constructors
# ---------------------------------------------------------------------------


def add_blocks(graphs: Iterable["mod.Graph"]):
    """Initial: drop building blocks into the working subset."""
    return mod.addSubset(*list(graphs))


def apply_rules_up_to(rules: Iterable["RuleDef"], steps: int):
    """Repeatedly apply any rule from the set, up to `steps` rounds."""
    mod_rules = [_to_mod_rule(r) for r in rules]
    if not mod_rules:
        raise ValueError("no rules supplied to apply_rules_up_to")
    return mod.repeat[steps](mod_rules)


def apply_rules_up_to_with_predicates(
    rules: Iterable["RuleDef"],
    steps: int,
    predicates: PredicateSpec,
):
    """Repeated rule application gated by chemistry-relevant predicates.

    If ``predicates`` is empty, this is equivalent to
    :func:`apply_rules_up_to`. Otherwise the inner ``repeat`` block is
    wrapped, from inside-out, by:

    * ``leftPredicate[_is_intramolecular]`` when
      ``predicates.is_intramolecular`` is true. The predicate accepts
      the derivation iff the left side is exactly one graph (i.e. the
      two atoms being bonded are in the same connected component
      before the rule fires).
    * ``rightPredicate[_ring_size_equals(n)]`` when
      ``predicates.ring_size_equals`` is set. The predicate accepts the
      derivation iff the product side contains a ring of size exactly
      ``n`` (SSSR via RDKit on the product SMILES).

    Wrapping order is irrelevant: both are conjunctive filters on the
    same set of candidate derivations.
    """
    mod_rules = [_to_mod_rule(r) for r in rules]
    if not mod_rules:
        raise ValueError(
            "no rules supplied to apply_rules_up_to_with_predicates"
        )

    inner = mod.repeat[steps](mod_rules)
    if predicates.is_empty():
        return inner

    # Composition order is outside-in:
    #   leftPredicate[is_intramolecular]
    #     ( rightPredicate[ring_size_equals]
    #       ( rightPredicate[enforce_ez_geometry]
    #         ( repeat[steps](rules) ) ) )
    # The three predicates are conjunctive filters on the same set of
    # candidate derivations, so the wrapping order is semantically
    # irrelevant; the inside-out construction below mirrors the order in
    # which we *describe* the predicates in PredicateSpec.
    gated = inner
    if predicates.enforce_ez_geometry:
        gated = mod.rightPredicate[
            _enforce_ez_geometry_factory(dict(predicates.enforce_ez_geometry))
        ](gated)
    if predicates.alcohol_partner_C_must_be_aromatic:
        gated = mod.rightPredicate[
            _alcohol_partner_aromaticity_factory(
                dict(predicates.alcohol_partner_C_must_be_aromatic),
                require_aromatic=True,
            )
        ](gated)
    if predicates.alcohol_partner_C_must_be_sp3:
        gated = mod.rightPredicate[
            _alcohol_partner_aromaticity_factory(
                dict(predicates.alcohol_partner_C_must_be_sp3),
                require_aromatic=False,
            )
        ](gated)
    if predicates.is_intramolecular:
        gated = mod.leftPredicate[_is_intramolecular](gated)
    if predicates.ring_size_equals is not None:
        n = int(predicates.ring_size_equals)
        gated = mod.rightPredicate[_ring_size_equals_factory(n)](gated)
    return gated


# ---------------------------------------------------------------------------
# Predicate callables
# ---------------------------------------------------------------------------


def _is_intramolecular(derivation) -> bool:
    """leftPredicate: accept iff the rule fires on a single reactant graph.

    In MØD, a candidate derivation's ``left`` is the multiset of
    reactant graphs that the rule's LHS matched into. When the LHS
    spans atoms across multiple graphs MØD groups them in ``left``;
    when the LHS matches a single connected component ``left`` has
    exactly one element. So ``len(left) == 1`` is precisely
    "intramolecular candidate".
    """
    return len(derivation.left) == 1


def _ring_size_equals_factory(n: int) -> Callable[[object], bool]:
    """Return a rightPredicate that accepts derivations producing a ring of size n.

    MØD's ``graph::Graph`` does not ship an SSSR routine, so we delegate
    to RDKit via the canonical SMILES. The graph state at this point is
    a small molecule and the round-trip is cheap.
    """

    def _pred(derivation) -> bool:
        for g in derivation.right:
            smiles = g.smiles
            if _has_ring_of_size(smiles, n):
                return True
        return False

    _pred.__name__ = f"ring_size_equals_{n}"
    return _pred


def _has_ring_of_size(smiles: str, n: int) -> bool:
    """Use RDKit's symmetric SSSR to check for a ring of exactly ``n`` atoms."""
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    sssr = Chem.GetSymmSSSR(mol)
    return any(len(ring) == n for ring in sssr)


def _enforce_ez_geometry_factory(
    rule_to_geometry: dict,
) -> Callable[[object], bool]:
    """Return a rightPredicate that filters E/Z geometry per rule.

    ``rule_to_geometry`` maps macrocert ``rule_id`` (e.g. ``"rcm"``) to
    ``"E"`` or ``"Z"``. The MØD ``ruleID`` field stored in the rule's
    GML body conventionally starts with the macrocert rule_id followed
    by a space and a parenthesised description (see
    ``data/rules/rcm.gml`` line 2: ``ruleID "rcm (ring-closing
    metathesis, -C2H4)"``); we match by either exact equality or by
    ``rule_id + " "`` prefix on ``derivation.r.name``. If the rule's
    name is not in the map, the predicate is a no-op (returns True).

    For matched rules:
      * Take each product graph in ``derivation.right`` and parse its
        canonical SMILES via RDKit (``mod::graph::Graph::getSmiles()`` —
        external/mod/libs/libmod/src/mod/graph/Graph.hpp:118; Python
        binding ``Graph.smiles`` exposes this read-only).
      * Run ``Chem.FindPotentialStereoBonds(mol)`` so that
        ``Bond.GetStereo()`` returns ``STEREOE`` / ``STEREOZ`` rather
        than ``STEREONONE`` for stereo-capable double bonds whose
        directionality is implied by the SMILES (see RDKit's
        ``rdkit/Chem/rdmolops.h::DetectBondStereochemistry`` / the docs
        on stereo handling).
      * Accept the derivation iff at least one product carries a double
        bond whose ``Bond.GetStereo()`` matches the requested geometry.

    Important caveat (docs/mod_stereo_reference.md §1.5, §5.2): MØD
    today does not propagate E/Z through rule firing, so a stereo-free
    rule applied to a stereo-free substrate yields a product SMILES
    whose double bonds are ``STEREONONE``. The predicate therefore
    rejects them, which is the correct behaviour for an E/Z gate
    (rule didn't produce a determinate geometry → don't accept either
    label). A downstream Workstream F pass is responsible for
    *creating* stereo on the product side; this predicate enforces it.
    """
    # Materialise the geometry vocab once; RDKit's Bond enum values are
    # not stable across versions so import-and-translate at predicate
    # construction time keeps the hot path branch-free.
    from rdkit.Chem import BondStereo

    e_set = {BondStereo.STEREOE, BondStereo.STEREOTRANS}
    z_set = {BondStereo.STEREOZ, BondStereo.STEREOCIS}
    accepted: dict[str, set] = {
        rid: (e_set if tok.upper() == "E" else z_set)
        for rid, tok in rule_to_geometry.items()
    }
    keys = tuple(rule_to_geometry.keys())

    def _pred(derivation) -> bool:
        # MØD's Python binding renames ``Derivation::r`` (C++,
        # external/mod/libs/libmod/src/mod/Derivation.hpp:39) to
        # ``derivation.rule`` (Python,
        # external/mod/libs/pymod/src/mod/py/Derivation.cpp:32). The
        # name attribute on Rule is ``rule.name``
        # (external/mod/libs/pymod/src/mod/py/rule/Rule.cpp:123 binds
        # ``Rule::getName`` —
        # external/mod/libs/libmod/src/mod/rule/Rule.hpp:129-133).
        # derivation.rule.name is the GML ``ruleID`` string; the
        # macrocert convention is ``"<rule_id> (<description>)"`` so we
        # match by equality OR by ``rule_id + " "`` prefix.
        rule_obj = getattr(derivation, "rule", None) or getattr(derivation, "r", None)
        if rule_obj is None:
            return True  # no rule on derivation → cannot filter
        rule_name = rule_obj.name
        rid: str | None = None
        for k in keys:
            if rule_name == k or rule_name.startswith(k + " "):
                rid = k
                break
        if rid is None:
            return True  # no-op for unmapped rules

        wanted = accepted[rid]
        for g in derivation.right:
            if _product_has_double_bond_with_geometry(g.smiles, wanted):
                return True
        return False

    _pred.__name__ = "enforce_ez_geometry"
    return _pred


def _product_has_double_bond_with_geometry(smiles: str, wanted: set) -> bool:
    """True iff some C=C bond in ``smiles`` has stereo in ``wanted``.

    Uses ``Chem.FindPotentialStereoBonds`` to flip ``STEREONONE`` to
    ``STEREOE``/``STEREOZ`` for bonds whose neighbours' directionality
    (``/``, ``\\``) is encoded in the SMILES string. Bonds whose
    geometry is genuinely undetermined remain ``STEREONONE`` /
    ``STEREOANY`` and do not satisfy the predicate.
    """
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    Chem.FindPotentialStereoBonds(mol)
    for bond in mol.GetBonds():
        if bond.GetBondType() != Chem.BondType.DOUBLE:
            continue
        if bond.GetStereo() in wanted:
            return True
    return False


# ---------------------------------------------------------------------------
# Workstream D phase-3 — alcohol-partner aromaticity / sp³ discriminator
# ---------------------------------------------------------------------------
#
# Motivation. The two ether GML rules
# (data/rules/aryl_etherification.gml, data/rules/biaryl_etherification.gml)
# have structurally identical bodies because MØD matches on element
# labels — atom 5 = O in both, and the sp²-aromatic vs sp³ context of
# the alcohol-side carbon is invisible at the GML level. See
# docs/macroetherification_research.md §1.4 and
# docs/biaryl_etherification_research.md §1.2.
#
# Ideal path. Inspect the substrate atom matched to rule-atom 5 and its
# non-rule-atom neighbour (the "alcohol partner C") via the L→substrate
# morph mapping. That would be a *leftPredicate*. However the MØD Python
# binding exposes Derivation as `left: GraphList`, `rule: Rule`,
# `right: GraphList` only — no morph mapping is bound, see
# external/mod/libs/pymod/src/mod/py/Derivation.cpp:8-39. So the
# substrate-side inspection isn't tractable from Python today.
#
# Fallback (what we ship). A *rightPredicate* substructure match on the
# product SMILES. The product carries the freshly-formed Ar-O-X bond as
# atoms 1-5 in MØD's atom map; RDKit's SMARTS engine can locate it on
# the canonical product SMILES via `Graph.smiles`
# (external/mod/libs/libmod/src/mod/graph/Graph.hpp:118). The
# substructure SMARTS are:
#   require_aromatic=True   → "[c;!H0,$(c(:*)(:*))]-O-c"  i.e. Ar-O-Ar
#   require_aromatic=False  → "c-O-[CX4]"                 i.e. Ar-O-C(sp³)
# (RDKit aromaticity model is set per parsing; lower-case `c` matches
# aromatic carbons, upper-case `C` aliphatic. `[CX4]` further restricts
# the alcohol-partner carbon to four-coordinate (sp³).)


def _alcohol_partner_aromaticity_factory(
    rule_to_bool: dict, *, require_aromatic: bool
) -> Callable[[object], bool]:
    """Return a rightPredicate that gates the two ether rules.

    ``rule_to_bool`` maps macrocert ``rule_id`` (e.g.
    ``"biaryl_etherification"``) to ``True``/``False``. When ``True``
    for a firing rule, the predicate enforces the constraint; when
    ``False`` or absent, the predicate is a no-op for that rule.

    ``require_aromatic=True`` => product must contain Ar-O-Ar (biaryl
    ether). ``require_aromatic=False`` => product must contain
    Ar-O-C(sp³) (aryl-alkyl ether).

    Rule-name matching mirrors ``_enforce_ez_geometry_factory``: the
    GML ``ruleID`` is the full ``"<rule_id> (<description>)"`` string
    (data/rules/aryl_etherification.gml:2 →
    ``"aryl_etherification (SNAr Ar-O-C(sp3) ring closure, -HF)"``);
    match by equality or by ``rule_id + " "`` prefix. If a derivation's
    rule isn't in the map, the predicate returns True (no-op) so it
    composes safely with mixed rule sets like ``all_macrocyclization``.
    """
    from rdkit import Chem

    # Pre-compile SMARTS once; the pattern depends on the constraint
    # direction so we materialise both at construction time.
    # Ar-O-Ar: both bridge carbons aromatic (lower-case c).
    # Ar-O-C(sp³): one aromatic C, one sp³ C (CX4 = four explicit
    # connections, ensuring sp³ — aromatic carbons are CX3 in RDKit's
    # SMARTS atom-class accounting).
    smarts = "c-O-c" if require_aromatic else "c-O-[CX4]"
    pattern = Chem.MolFromSmarts(smarts)
    if pattern is None:  # pragma: no cover — pattern is a compile-time literal
        raise RuntimeError(f"failed to compile SMARTS {smarts!r}")

    # Keep only rule_ids whose bool flag is True; False entries are
    # explicit opt-outs and the predicate skips them.
    active_keys = tuple(k for k, v in rule_to_bool.items() if v)

    def _pred(derivation) -> bool:
        if not active_keys:
            return True  # nothing to enforce
        rule_obj = getattr(derivation, "rule", None) or getattr(derivation, "r", None)
        if rule_obj is None:
            return True  # no rule on derivation → cannot filter
        rule_name = rule_obj.name
        matched = False
        for k in active_keys:
            if rule_name == k or rule_name.startswith(k + " "):
                matched = True
                break
        if not matched:
            return True  # no-op for unmapped/inactive rules

        for g in derivation.right:
            smiles = g.smiles
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
            if mol.HasSubstructMatch(pattern):
                return True
        return False

    _pred.__name__ = (
        "alcohol_partner_C_must_be_aromatic"
        if require_aromatic
        else "alcohol_partner_C_must_be_sp3"
    )
    return _pred


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _to_mod_rule(rule_def: "RuleDef") -> "mod.Rule":
    return mod.Rule.fromGMLString(rule_def.gml)
