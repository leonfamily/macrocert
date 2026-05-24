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
class RuleMeta:
    reagent_mass_g_per_mol: float
    classes: tuple[str, ...]
    stereo_flags: tuple[str, ...]
    refs: tuple[str, ...]
    notes: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RuleMeta":
        return cls(
            reagent_mass_g_per_mol=float(d.get("reagent_mass_g_per_mol", 0.0)),
            classes=tuple(d.get("classes", ())),
            stereo_flags=tuple(d.get("stereo_flags", ())),
            refs=tuple(d.get("refs", ())),
            notes=str(d.get("notes", "")),
        )


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
