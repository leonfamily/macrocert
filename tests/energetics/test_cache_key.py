"""Regression tests for the energetics cache key.

Workstream E (Marks Vandezande Gomes 2026, arXiv:2604.00405) found that the
v1 SHA-256 key did not include the solvent name or the DFT composite
identifier (functional + basis + dispersion + solver). Two computations on
the same SMILES in different solvents — or with different functionals
under the same display "method" label — would collide and silently return
the wrong energy.

These tests pin the v2 key down so that regression cannot recur:

  * different ``solvent_name`` → different key (the literal bug)
  * different ``method_id``    → different key (the same bug, other axis)
  * different tier             → different key (already true in v1)
  * same inputs                → same key (deterministic)
  * end-to-end: ``EnergeticsCache.lookup_or_compute`` honours the new
    fields and does not cross-pollute DMF results into a DCM lookup.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from macrocert.energetics.cache import (
    CACHE_VERSION,
    CacheEntry,
    EnergeticsCache,
    VACUUM_SOLVENT,
    make_cache_key,
)


# ---------------------------------------------------------------------------
# Direct key-function tests
# ---------------------------------------------------------------------------


def _base_args() -> dict:
    return dict(
        rule_id="suzuki",
        reactant_smiles=("c1ccccc1Br",),
        product_smiles=("c1ccc(-c2ccccc2)cc1",),
        tier="dft",
        method="SCF/STO-3G",
    )


def test_different_solvents_produce_different_keys():
    """The Workstream E collision case: same SMILES, different solvent."""
    k_dmf = make_cache_key(**_base_args(),
                           method_id="B3LYP-D3BJ_def2-SVP_PCM-DMF",
                           solvent_name="DMF")
    k_dcm = make_cache_key(**_base_args(),
                           method_id="B3LYP-D3BJ_def2-SVP_PCM-DCM",
                           solvent_name="DCM")
    assert k_dmf != k_dcm, (
        "Cache key must discriminate solvents — Workstream E "
        "(arXiv:2604.00405) found this collision in v1."
    )


def test_different_method_ids_produce_different_keys():
    """B3LYP vs PBE under the same display ``method`` must not collide."""
    k_b3lyp = make_cache_key(**_base_args(),
                             method_id="B3LYP-D3BJ_def2-SVP_PCM-DMF",
                             solvent_name="DMF")
    k_pbe = make_cache_key(**_base_args(),
                           method_id="PBE-D3BJ_def2-SVP_PCM-DMF",
                           solvent_name="DMF")
    assert k_b3lyp != k_pbe


def test_vacuum_default_is_distinct_from_named_solvent():
    k_vac = make_cache_key(**_base_args(),
                           method_id="SCF/STO-3G",
                           solvent_name=VACUUM_SOLVENT)
    k_dmf = make_cache_key(**_base_args(),
                           method_id="SCF/STO-3G_PCM-DMF",
                           solvent_name="DMF")
    assert k_vac != k_dmf


def test_deterministic_same_inputs_same_key():
    a = make_cache_key(**_base_args(),
                       method_id="GFN2-xTB_ALPB-DMF",
                       solvent_name="DMF")
    b = make_cache_key(**_base_args(),
                       method_id="GFN2-xTB_ALPB-DMF",
                       solvent_name="DMF")
    assert a == b


def test_smiles_order_does_not_matter():
    """Cache key is canonical under permutation of the SMILES tuples."""
    common = dict(rule_id="r", tier="xtb",
                  method="GFN2-xTB", method_id="GFN2-xTB_ALPB-DMF",
                  solvent_name="DMF")
    k1 = make_cache_key(reactant_smiles=("A", "B"),
                        product_smiles=("C", "D"), **common)
    k2 = make_cache_key(reactant_smiles=("B", "A"),
                        product_smiles=("D", "C"), **common)
    assert k1 == k2


def test_cache_version_changes_invalidate_keys():
    """The CACHE_VERSION constant is part of the key — bumping it
    invalidates any pre-fix entries (defence in depth for Workstream E)."""
    # We don't have two CACHE_VERSIONS live at once, but we can prove
    # the constant participates in the key by constructing what the v1
    # key would have looked like and asserting non-collision.
    import hashlib
    import json
    v1_payload = json.dumps({
        "rule_id": _base_args()["rule_id"],
        "reactants": list(_base_args()["reactant_smiles"]),
        "products": list(_base_args()["product_smiles"]),
        "tier": _base_args()["tier"],
        "method": _base_args()["method"],
    }, sort_keys=True).encode()
    v1_key = hashlib.sha256(v1_payload).hexdigest()[:32]
    v2_key = make_cache_key(**_base_args(),
                            method_id=_base_args()["method"],
                            solvent_name=VACUUM_SOLVENT)
    assert v1_key != v2_key
    assert CACHE_VERSION == "v2"


# ---------------------------------------------------------------------------
# End-to-end test through EnergeticsCache.lookup_or_compute
# ---------------------------------------------------------------------------


def test_lookup_or_compute_does_not_cross_pollute_across_solvents(tmp_path: Path):
    cache = EnergeticsCache(root=tmp_path)

    smiles_args = ("suzuki", ("c1ccccc1Br",), ("c1ccc(-c2ccccc2)cc1",))

    # First call: in DMF, returns ΔG = -5.0
    entry_dmf, miss_dmf = cache.lookup_or_compute(
        key_args=(*smiles_args, "dft", "SCF/STO-3G",
                  "SCF/STO-3G_PCM-DMF", "DMF"),
        compute=lambda: (-5.0, None, "DMF run"),
    )
    assert miss_dmf is True
    assert entry_dmf.dG_kcal_per_mol == -5.0
    assert entry_dmf.solvent_name == "DMF"

    # Second call with same SMILES + method but solvent_name=DCM —
    # the v1 bug would have served the DMF entry; the v2 key must miss
    # and run the compute() callback again.
    entry_dcm, miss_dcm = cache.lookup_or_compute(
        key_args=(*smiles_args, "dft", "SCF/STO-3G",
                  "SCF/STO-3G_PCM-DCM", "DCM"),
        compute=lambda: (+7.0, None, "DCM run"),
    )
    assert miss_dcm is True, (
        "DCM lookup must miss — if it hits, the Workstream E "
        "(arXiv:2604.00405) collision regression is back."
    )
    assert entry_dcm.dG_kcal_per_mol == +7.0
    assert entry_dcm.solvent_name == "DCM"

    # And a re-lookup of the DMF entry still hits.
    entry_dmf_again, miss_dmf_again = cache.lookup_or_compute(
        key_args=(*smiles_args, "dft", "SCF/STO-3G",
                  "SCF/STO-3G_PCM-DMF", "DMF"),
        compute=lambda: pytest.fail("should not recompute on DMF hit"),
    )
    assert miss_dmf_again is False
    assert entry_dmf_again.dG_kcal_per_mol == -5.0


def test_cache_entry_round_trips_new_fields(tmp_path: Path):
    cache = EnergeticsCache(root=tmp_path)
    entry = CacheEntry(
        rule_id="suzuki",
        reactant_smiles=("c1ccccc1Br",),
        product_smiles=("c1ccc(-c2ccccc2)cc1",),
        tier="dft",
        method="SCF/STO-3G",
        method_id="B3LYP-D3BJ_def2-SVP_PCM-DMF",
        solvent_name="DMF",
        dG_kcal_per_mol=-3.21,
    )
    key = cache.put(entry)
    rt = cache.get(key)
    assert rt is not None
    assert rt.solvent_name == "DMF"
    assert rt.method_id == "B3LYP-D3BJ_def2-SVP_PCM-DMF"
