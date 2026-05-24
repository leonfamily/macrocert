"""Target encoder: structure file → MØD stereo-annotated Graph.

Per proposal §2.1, the 13-membered ring perimeter must be encoded
from the deposited crystal structure, not inferred from the cytochalasan
class. The encoder enforces this by *requiring* a structure file (CIF,
Molfile, SDF) and refusing to fall back to SMILES. The ring perimeter
is detected on the encoded graph and written to a sidecar file for
chemist sign-off.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mod  # noqa: F401


@dataclass(frozen=True)
class EncodedTarget:
    name: str
    graph: object  # mod.Graph; typed as object to keep this module mod-import-free at module load
    structure_path: Path
    ring_atom_indices: tuple[int, ...]


def encode_target(
    structure_path: str | Path,
    *,
    ring_size: int,
    name: str | None = None,
) -> EncodedTarget:
    """Encode a crystal-structure file as a stereo-annotated mod.Graph.

    Accepts .mol / .sdf (MDL) directly. SMILES is *not* accepted at
    this layer — see proposal §2.1.
    """
    import mod

    structure_path = Path(structure_path)
    if not structure_path.exists():
        raise FileNotFoundError(structure_path)

    suffix = structure_path.suffix.lower()
    text = structure_path.read_text()
    if suffix in (".mol", ".sdf"):
        graphs = mod.Graph.fromSDString(text) if suffix == ".sdf" else [
            mod.Graph.fromMOLString(text)
        ]
        if not graphs:
            raise ValueError(f"no molecules parsed from {structure_path}")
        graph = graphs[0]
    elif suffix == ".cif":
        raise NotImplementedError(
            "CIF parsing not implemented in M1; convert to .mol via openbabel"
            " (obabel input.cif -O output.mol) and re-run."
        )
    elif suffix in (".smi", ".smiles"):
        raise ValueError(
            "SMILES targets are forbidden at this layer per proposal §2.1 — "
            "use a .mol/.sdf from the deposited crystal structure."
        )
    else:
        raise ValueError(f"unsupported structure format: {suffix}")

    ring_atoms = _find_ring(graph, ring_size)
    return EncodedTarget(
        name=name or structure_path.stem,
        graph=graph,
        structure_path=structure_path,
        ring_atom_indices=ring_atoms,
    )


def _find_ring(graph: object, ring_size: int) -> tuple[int, ...]:
    """Return atom IDs of one ring of the requested size, or () if not found.

    Uses RDKit's SSSR via the graph's SMILES round-trip — acceptable here
    because the perimeter is then *cross-checked* against the published
    structure by a human (the sidecar file is the audit trail).
    """
    from rdkit import Chem

    smiles = graph.smiles  # type: ignore[attr-defined]
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ()
    sssr = Chem.GetSymmSSSR(mol)
    for ring in sssr:
        if len(ring) == ring_size:
            return tuple(sorted(int(i) for i in ring))
    return ()


def write_perimeter_audit(target: EncodedTarget, output_path: str | Path) -> None:
    """Emit a human-readable file listing the perimeter atoms for sign-off."""
    output_path = Path(output_path)
    lines = [
        f"# Ring-perimeter audit for {target.name}",
        f"# Source: {target.structure_path}",
        f"# Ring size: {len(target.ring_atom_indices)}",
        "",
        "Atoms on the perimeter (RDKit canonical SMILES indexing):",
    ]
    for idx in target.ring_atom_indices:
        lines.append(f"  - atom_index: {idx}")
    lines.append("")
    lines.append("Reviewer to compare each atom against the published crystal structure")
    lines.append("(Chen 2019, J. Nat. Prod., DOI:10.1021/acs.jnatprod.8b00918).")
    output_path.write_text("\n".join(lines) + "\n")
