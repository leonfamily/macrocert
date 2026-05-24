"""Rule library loader: GML + sibling .meta.yaml + _index.yaml rule sets.

A rule's GML body defines the abstract DPO transformation (L|K|R) and
nothing else. Application conditions that depend on the macrocyclic
*context* (e.g. "only fire when the new bond closes a 13-membered
cycle") live in the generation strategy, not the GML — see
macrocert.generate.strategies.

The sibling .meta.yaml carries everything that isn't part of the
abstract transformation: process-level reagent mass, named class
memberships used by the rule-set algebra, stereo flags, references.
This is the *only* place reagent_mass lives — Layer C reads it from
here, never from the derivation graph. expelled_mass, by contrast, is
derived from the composed rule's atom-map and is not stored.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ReagentAlternative:
    """A non-canonical activator/reagent option for a rule.

    Some rules — notably macrolactonization — have several substantially
    different activator systems (Yamaguchi, Shiina, Corey–Nicolaou, ...)
    that all close the same bond at the bond level but carry different
    process-level reagent and byproduct masses. The canonical activator
    is recorded by ``reagent_mass_g_per_mol``; the alternatives are
    listed here. RunSpec.solver.extra may select an alternative by name.
    """
    name: str
    reagent_mass_g_per_mol: float
    additional_byproduct_mass_g_per_mol: float = 0.0
    description: str = ""
    refs: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ReagentAlternative":
        return cls(
            name=str(d.get("name", "")),
            reagent_mass_g_per_mol=float(d.get("reagent_mass_g_per_mol", 0.0)),
            additional_byproduct_mass_g_per_mol=float(
                d.get("additional_byproduct_mass_g_per_mol", 0.0)
            ),
            description=str(d.get("description", "")),
            refs=tuple(d.get("refs", ())),
        )


# Stereo policy taxonomy. See docs/workstream_f_stereo_policy.md.
#
#   match_enforced   — the rule body carries tetrahedral stereo annotations
#                      and MØD enforces them at match-time. The pre-M5 gate
#                      requires the GML body to contain the "stereo" token.
#   n_a_sp2_only     — the bond-forming atoms are sp²; there is no sp³
#                      stereocenter at the bond site to enforce. Off-rule
#                      sp³ stereo (e.g. the alcohol C in aryl_etherification)
#                      is preserved automatically by graph-isomorphism.
#   advisory_only    — the rule's stereo outcome is documented in the
#                      certificate's provenance but cannot be enforced by
#                      MØD (e.g. atropisomerism, E/Z trigonalPlanar abort
#                      per docs/workstream_f_harness.md §5.2). Requires a
#                      non-empty ``stereo_advisory`` message.
STEREO_TREATMENTS: frozenset[str] = frozenset(
    {"match_enforced", "n_a_sp2_only", "advisory_only"}
)


@dataclass(frozen=True)
class RuleMeta:
    reagent_mass_g_per_mol: float
    byproduct_mass_g_per_mol: float
    retained_root_atom: int
    classes: tuple[str, ...]
    stereo_flags: tuple[str, ...]
    refs: tuple[str, ...]
    notes: str
    reagent_mass_alternatives: tuple[ReagentAlternative, ...] = ()
    # Chemistry-aware stereo policy. Default ``match_enforced`` preserves
    # backward compatibility: the existing macrolactam/macrolactone rules
    # carry tetrahedral α-C stereo and must keep "stereo" in their GML.
    stereo_treatment: str = "match_enforced"
    # Free-text advisory message that flows into the certificate's
    # provenance when ``stereo_treatment == 'advisory_only'``. Required
    # in that case; empty otherwise.
    stereo_advisory: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RuleMeta":
        treatment = str(d.get("stereo_treatment", "match_enforced"))
        if treatment not in STEREO_TREATMENTS:
            raise ValueError(
                f"unknown stereo_treatment {treatment!r}; "
                f"expected one of {sorted(STEREO_TREATMENTS)}"
            )
        advisory = str(d.get("stereo_advisory", ""))
        if treatment == "advisory_only" and not advisory.strip():
            raise ValueError(
                "stereo_treatment == 'advisory_only' requires a non-empty "
                "stereo_advisory field"
            )
        if treatment != "advisory_only" and advisory.strip():
            # Non-fatal: tolerate, but the gate will only forward advisories
            # for advisory_only rules. Keep the text for documentation.
            pass
        return cls(
            reagent_mass_g_per_mol=float(d.get("reagent_mass_g_per_mol", 0.0)),
            byproduct_mass_g_per_mol=float(d.get("byproduct_mass_g_per_mol", 0.0)),
            retained_root_atom=int(d.get("retained_root_atom", 1)),
            classes=tuple(d.get("classes", ())),
            stereo_flags=tuple(d.get("stereo_flags", ())),
            refs=tuple(d.get("refs", ())),
            notes=str(d.get("notes", "")),
            reagent_mass_alternatives=tuple(
                ReagentAlternative.from_dict(alt)
                for alt in (d.get("reagent_mass_alternatives") or ())
            ),
            stereo_treatment=treatment,
            stereo_advisory=advisory,
        )

    def get_alternative(self, name: str) -> ReagentAlternative | None:
        for alt in self.reagent_mass_alternatives:
            if alt.name == name:
                return alt
        return None


@dataclass(frozen=True)
class RuleDef:
    id: str
    gml: str
    meta: RuleMeta
    path: Path

    def in_class(self, klass: str) -> bool:
        return klass in self.meta.classes


@dataclass(frozen=True)
class RuleSet:
    name: str
    rule_ids: tuple[str, ...]


@dataclass(frozen=True)
class RuleLibrary:
    rules: dict[str, RuleDef] = field(default_factory=dict)
    sets: dict[str, RuleSet] = field(default_factory=dict)

    def get(self, rid: str) -> RuleDef:
        return self.rules[rid]

    def resolve_set(self, name_or_id: str) -> tuple[RuleDef, ...]:
        if name_or_id in self.sets:
            return tuple(self.rules[r] for r in self.sets[name_or_id].rule_ids)
        if name_or_id in self.rules:
            return (self.rules[name_or_id],)
        raise KeyError(f"unknown rule or rule-set: {name_or_id!r}")

    def in_class(self, klass: str) -> tuple[RuleDef, ...]:
        return tuple(r for r in self.rules.values() if r.in_class(klass))


def load_rule_library(directory: str | Path) -> RuleLibrary:
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"rule directory not found: {directory}")

    rules: dict[str, RuleDef] = {}
    for gml_path in sorted(directory.glob("*.gml")):
        rid = gml_path.stem
        meta_path = gml_path.with_suffix(".meta.yaml")
        if not meta_path.exists():
            raise FileNotFoundError(
                f"rule {rid!r} missing metadata: {meta_path}"
            )
        meta = RuleMeta.from_dict(yaml.safe_load(meta_path.read_text()) or {})
        rules[rid] = RuleDef(
            id=rid,
            gml=gml_path.read_text(),
            meta=meta,
            path=gml_path,
        )

    sets: dict[str, RuleSet] = {}
    index_path = directory / "_index.yaml"
    if index_path.exists():
        idx = yaml.safe_load(index_path.read_text()) or {}
        for set_name, members in (idx.get("sets") or {}).items():
            unknown = [m for m in members if m not in rules]
            if unknown:
                raise ValueError(
                    f"rule-set {set_name!r} references unknown rules: {unknown}"
                )
            sets[set_name] = RuleSet(name=set_name, rule_ids=tuple(members))

    return RuleLibrary(rules=rules, sets=sets)
