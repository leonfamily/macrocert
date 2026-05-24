"""MACE-OFF MLIP driver (Layer D triage tier).

MACE-OFF (Kovács 2025) is a transferable organic force field that runs
on PyTorch — Apple Silicon MPS where available. We use it for cheap
*ranking* of candidate ring closures, never for go/no-go decisions, per
the proposal §2.5 OOD caveat (MAE > 5 kcal/mol on novel reaction
networks).

The model loads lazily on first use; weights download from HuggingFace
the first time. For headless CI / smoke tests, mlip_available() returns
False if mace-torch or its weights aren't reachable.
"""
from __future__ import annotations

from functools import lru_cache

from .qm import EV_TO_KCAL, EnergyResult, smiles_to_atoms


@lru_cache(maxsize=1)
def _calc(model_size: str = "small", device: str = "mps"):
    from mace.calculators import mace_off
    return mace_off(model=model_size, device=device, default_dtype="float64")


def mlip_available() -> bool:
    try:
        _calc()
        return True
    except Exception:
        return False


def mace_off_single_point(
    smiles: str,
    *,
    model: str = "small",
    device: str = "mps",
    solvent_name: str | None = None,
) -> EnergyResult:
    """MACE-OFF single-point energy.

    MACE-OFF itself is a gas-phase MLIP, but we still flow ``solvent_name``
    through so the result's ``method`` label is solvent-stamped. Downstream
    the energetics cache key (Workstream E fix) requires the solvent to
    be part of the key — if a future MACE-Solv model lands here, the
    label will already be correct.
    """
    atoms = smiles_to_atoms(smiles)
    atoms.calc = _calc(model, device)
    e_ev = atoms.get_potential_energy()
    solvent_tag = solvent_name or "vacuum"
    return EnergyResult(
        e_kcal_per_mol=e_ev * EV_TO_KCAL,
        method=f"MACE-OFF/{model}_{solvent_tag}",
        provenance=f"mace-torch on {device}; MMFF-pre-optimized geometry from SMILES",
    )


def mace_reaction_dG(
    reactant_smiles: tuple[str, ...],
    product_smiles: tuple[str, ...],
    *,
    model: str = "small",
    device: str = "mps",
    solvent_name: str | None = None,
) -> tuple[float, str, str]:
    method_label = ""
    parts: list[str] = []
    e_react = 0.0
    for smi in reactant_smiles:
        r = mace_off_single_point(smi, model=model, device=device, solvent_name=solvent_name)
        e_react += r.e_kcal_per_mol
        method_label = r.method
        parts.append(f"R[{smi}]={r.e_kcal_per_mol:.3f}")
    e_prod = 0.0
    for smi in product_smiles:
        r = mace_off_single_point(smi, model=model, device=device, solvent_name=solvent_name)
        e_prod += r.e_kcal_per_mol
        parts.append(f"P[{smi}]={r.e_kcal_per_mol:.3f}")
    return e_prod - e_react, method_label, "; ".join(parts)
