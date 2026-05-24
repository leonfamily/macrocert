"""Build a MØD derivation graph from a RunSpec — Layer B orchestrator."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..spec.runspec import RunSpec
    from ..spec.rules import RuleLibrary, RuleDef

import mod  # noqa: E402

from .strategies import (
    PredicateSpec,
    add_blocks,
    apply_rules_up_to,
    apply_rules_up_to_with_predicates,
)


# Workstream F (#43) — byte-deterministic certificates.
#
# MØD's RNG (``mod::lib::Random::Random()`` in
# external/mod/libs/libmod/src/mod/lib/Random.cpp) seeds itself from
# ``std::random_device`` on first use, so DG construction can differ
# run-to-run in ways that ripple into the certificate (vertex ordering,
# rule-application ordering, geometry-finalization choices). MØD exposes
# the seed via the C++ entry point ``mod::rngReseed(seed)`` and the
# Python binding ``mod.rngReseed(seed)`` (see
# external/mod/libs/libmod/src/mod/Misc.cpp:31 and
# external/mod/libs/pymod/src/mod/py/Misc.cpp:85), so we can pin it
# without patching MØD.
#
# The default ``0xC0FFEE`` matches the RDKit seed used in
# ``macrocert.energetics.qm.smiles_to_atoms`` for consistency. Override
# via the ``MACROCERT_MOD_SEED`` env var (parsed as base-0 so ``0x...``
# / ``0o...`` literals work).
_DEFAULT_MOD_SEED = 0xC0FFEE


def _resolve_mod_seed() -> int:
    raw = os.environ.get("MACROCERT_MOD_SEED")
    if raw is None or raw == "":
        return _DEFAULT_MOD_SEED
    try:
        return int(raw, 0)
    except ValueError as exc:
        raise ValueError(
            f"MACROCERT_MOD_SEED={raw!r} is not a valid integer literal"
        ) from exc


MOD_SEED = _resolve_mod_seed()


@dataclass
class GenerationResult:
    dg: "mod.DG"
    seco_precursor: "mod.Graph"
    rules_used: tuple[str, ...]


def build_dg_for_runspec(
    spec: "RunSpec",
    *,
    library: "RuleLibrary",
    blocks_dir: str | Path,
    target_dir: str | Path,
) -> GenerationResult:
    blocks_dir = Path(blocks_dir)
    target_dir = Path(target_dir)

    # Workstream F (#43): pin MØD's PRNG before any DG construction so
    # rule-application ordering, vertex ordering, and geometry
    # finalization are byte-deterministic. Re-read the env var on every
    # call (rather than relying on the import-time ``MOD_SEED``) so
    # tests can vary the seed within a single process.
    seed = _resolve_mod_seed()
    mod.rngReseed(seed)
    # Also seed Python's ``random`` module and NumPy. RDKit calls that
    # accept ``randomSeed=`` (notably ``AllChem.EmbedMolecule`` in
    # ``macrocert.energetics.qm``) already pin their own seed; this
    # covers the rest (any third-party code reaching for the global
    # PRNG during DG construction).
    import random as _random
    _random.seed(seed)
    try:
        import numpy as _np  # noqa: WPS433
        _np.random.seed(seed & 0xFFFFFFFF)
    except ImportError:  # pragma: no cover - numpy is a hard dep in pixi
        pass

    from ..spec.blocks import load_blocks

    all_blocks = load_blocks(blocks_dir)
    spec_blocks = [all_blocks[b] for b in spec.blocks]
    block_graphs = [
        mod.Graph.fromSMILES(b.smiles, name=b.id) for b in spec_blocks
    ]

    rule_defs: tuple["RuleDef", ...] = ()
    for r in spec.rules:
        rule_defs = rule_defs + library.resolve_set(r)
    seen: set[str] = set()
    deduped: list["RuleDef"] = []
    for r in rule_defs:
        if r.id in seen:
            continue
        seen.add(r.id)
        deduped.append(r)
    rule_defs = tuple(deduped)

    if not rule_defs:
        raise ValueError(f"RunSpec {spec.name!r} resolved to zero rules")
    if not block_graphs:
        raise ValueError(f"RunSpec {spec.name!r} resolved to zero building blocks")

    # Workstream F (Component 1): wire MØD stereo enforcement through
    # ``LabelSettings``. The default 2-arg constructor leaves
    # ``withStereo=false`` — stereo annotations on rule vertices parse
    # but are never checked at match time
    # (external/mod/libs/libmod/src/mod/Config.hpp:82-118). The 3-arg
    # form ``LabelSettings(LabelType.Term, LabelRelation.Specialisation,
    # LabelRelation.Specialisation)`` flips ``withStereo=true`` and
    # selects the specialisation comparator for stereo (pattern
    # ``Sym``/free matches substrate ``Fixed``, but not vice versa).
    # Mirrors external/mod/examples/py/030_stereo/320_aconitase.py:54-58
    # and …/330_tartaric.py:27-30.
    #
    # Workstream F (α-C overlay follow-up): we use ``LabelType.Term``
    # unconditionally so that rule-side wildcard labels (``label "*"``)
    # work as unification variables for the α-C neighbour-degree shim in
    # ``macrolactamization.gml`` / ``macrolactonization.gml``. Under the
    # default ``LabelType.String`` mode, ``"*"`` would be a literal label
    # the substrate cannot satisfy, and the rule would fail to match
    # (verified empirically against the lactam_*/lactone_* panel cases —
    # see docs/workstream_f_alpha_c_overlays.md §"Regression handled").
    # Term mode treats element labels (``"C"``, ``"O"``, ``"N"``) as
    # constants, so all other rules (which use only element labels)
    # continue to match exactly as they did under String mode. This is
    # the same mode the canonical stereo examples use
    # (external/mod/examples/py/030_stereo/{320_aconitase, 330_tartaric}.py).
    dg_kwargs: dict[str, object] = {"graphDatabase": block_graphs}
    if spec.strategy.stereo_enforcement:
        dg_kwargs["labelSettings"] = mod.LabelSettings(
            mod.LabelType.Term,
            mod.LabelRelation.Specialisation,
            mod.LabelRelation.Specialisation,
        )
    else:
        dg_kwargs["labelSettings"] = mod.LabelSettings(
            mod.LabelType.Term,
            mod.LabelRelation.Specialisation,
        )
    dg = mod.DG(**dg_kwargs)
    with dg.build() as builder:
        spec_preds = spec.strategy.predicates
        gen_preds = PredicateSpec(
            is_intramolecular=spec_preds.is_intramolecular,
            ring_size_equals=spec_preds.ring_size_equals,
            enforce_ez_geometry=(
                dict(spec_preds.enforce_ez_geometry)
                if spec_preds.enforce_ez_geometry
                else None
            ),
            # Workstream D phase-3 discriminators forwarded as dict
            # copies so the generate-layer PredicateSpec stays
            # independent of the spec-layer one (the strategies factory
            # mutates internally via `tuple(rule_to_bool)`).
            alcohol_partner_C_must_be_aromatic=(
                dict(spec_preds.alcohol_partner_C_must_be_aromatic)
                if spec_preds.alcohol_partner_C_must_be_aromatic
                else None
            ),
            alcohol_partner_C_must_be_sp3=(
                dict(spec_preds.alcohol_partner_C_must_be_sp3)
                if spec_preds.alcohol_partner_C_must_be_sp3
                else None
            ),
        )
        if gen_preds.is_empty():
            inner_strat = apply_rules_up_to(
                rule_defs, steps=spec.strategy.max_steps
            )
        else:
            inner_strat = apply_rules_up_to_with_predicates(
                rule_defs,
                steps=spec.strategy.max_steps,
                predicates=gen_preds,
            )
        strat = add_blocks(block_graphs) >> inner_strat
        builder.execute(strat)

    return GenerationResult(
        dg=dg,
        seco_precursor=block_graphs[0],
        rules_used=tuple(r.id for r in rule_defs),
    )
