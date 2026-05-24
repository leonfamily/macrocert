"""Building-block library: SMILES + provenance per block, stored as YAML."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class BuildingBlock:
    id: str
    smiles: str
    name: str
    provenance: str
    notes: str = ""

    @classmethod
    def from_dict(cls, bid: str, d: dict[str, Any]) -> "BuildingBlock":
        return cls(
            id=bid,
            smiles=str(d["smiles"]),
            name=str(d.get("name", bid)),
            provenance=str(d.get("provenance", "")),
            notes=str(d.get("notes", "")),
        )


def load_blocks(directory: str | Path) -> dict[str, BuildingBlock]:
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"building-block directory not found: {directory}")
    blocks: dict[str, BuildingBlock] = {}
    for yaml_path in sorted(directory.glob("*.yaml")):
        bid = yaml_path.stem
        if bid.startswith("_") or bid.startswith("."):
            continue
        data = yaml.safe_load(yaml_path.read_text()) or {}
        blocks[bid] = BuildingBlock.from_dict(bid, data)
    return blocks
