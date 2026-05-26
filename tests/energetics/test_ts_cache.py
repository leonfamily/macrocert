"""Tests for the TS-search content-addressed cache (ts_cache.py).

Covers:
  * Unit: ``OptimizerConfig.fingerprint`` is stable and discriminates
    on every documented knob (n_images, spring constant, NEB / Sella
    tolerances and step caps).
  * Unit: ``TSCacheEntry`` round-trips through ``put`` + ``get``;
    the persisted JSON carries the cache key for self-identification.
  * Unit: distinct workflows / substrates / tiers / methods / optimizer
    configs all produce distinct keys (no silent collisions).
  * Unit: ``lookup_or_compute`` calls compute() exactly once per
    unique key — the second call is served from cache.
  * Unit (slow, opt-in): The end-to-end worked-example invocation
    populates the TS cache; a second invocation hits the cache and
    skips the Sella refinement.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from macrocert.energetics.ts_cache import (
    CACHE_VERSION,
    OptimizerConfig,
    TSCache,
    TSCacheEntry,
    make_ts_cache_key,
    substrate_id_from_smiles,
)
from macrocert.energetics.ts_search import TSResult


def _result(barrier: float = 6.11, converged: bool = True) -> TSResult:
    return TSResult(
        barrier_kcal_per_mol=barrier,
        e_reactant_ev=-120.4,
        e_product_ev=-120.4,
        e_ts_ev=-120.18,
        n_neb_images=0,
        n_sella_iterations=42,
        converged=converged,
        method="GFN2-xTB",
        provenance="test fixture",
    )


def test_optimizer_config_default_fingerprint_is_stable():
    """Two default-constructed configs produce the same fingerprint."""
    a = OptimizerConfig().fingerprint()
    b = OptimizerConfig().fingerprint()
    assert a == b
    assert len(a) == 16


def test_optimizer_config_discriminates_on_every_knob():
    """Each documented knob change shifts the fingerprint."""
    base = OptimizerConfig().fingerprint()
    knobs = [
        OptimizerConfig(n_images=11),
        OptimizerConfig(spring_constant_eV_per_A=0.2),
        OptimizerConfig(neb_steps=50),
        OptimizerConfig(neb_fmax=0.1),
        OptimizerConfig(sella_fmax=0.01),
        OptimizerConfig(sella_max_steps=500),
    ]
    fps = {c.fingerprint() for c in knobs} | {base}
    assert len(fps) == 7, f"expected 7 distinct fingerprints, got {len(fps)}"


def test_round_trip_through_disk(tmp_path: Path):
    cache = TSCache(root=tmp_path)
    entry = TSCacheEntry(
        workflow="worked_example",
        substrate_id="nh3_inversion",
        tier="xtb",
        method="GFN2-xTB",
        optimizer_fingerprint=OptimizerConfig().fingerprint(),
        result=_result(),
    )
    key = cache.put(entry)
    assert len(key) == 32

    fetched = cache.get(key)
    assert fetched is not None
    assert fetched.result.barrier_kcal_per_mol == pytest.approx(6.11)
    assert fetched.result.converged is True
    assert fetched.method == "GFN2-xTB"


def test_persisted_json_carries_its_own_key(tmp_path: Path):
    """The on-disk record contains the cache_key so it can be cross-checked."""
    cache = TSCache(root=tmp_path)
    entry = TSCacheEntry(
        workflow="worked_example",
        substrate_id="nh3_inversion",
        tier="xtb",
        method="GFN2-xTB",
        optimizer_fingerprint=OptimizerConfig().fingerprint(),
        result=_result(),
    )
    key = cache.put(entry)
    on_disk = json.loads((cache.root / f"{key}.json").read_text())
    assert on_disk["cache_key"] == key


def test_distinct_keys_for_distinct_workflows():
    a = make_ts_cache_key(
        workflow="worked_example", substrate_id="x", tier="xtb",
        method="GFN2-xTB", optimizer_fingerprint="abc",
    )
    b = make_ts_cache_key(
        workflow="neb_to_sella", substrate_id="x", tier="xtb",
        method="GFN2-xTB", optimizer_fingerprint="abc",
    )
    assert a != b


def test_distinct_keys_for_distinct_solvents_via_method_label():
    """ALPB-DMF vs ALPB-DCM is encoded in the ``method`` label per the
    feedback.py convention; cache keys must reflect that."""
    a = make_ts_cache_key(
        workflow="worked_example", substrate_id="nh3", tier="xtb",
        method="GFN2-xTB_ALPB-DMF", optimizer_fingerprint="abc",
    )
    b = make_ts_cache_key(
        workflow="worked_example", substrate_id="nh3", tier="xtb",
        method="GFN2-xTB_ALPB-DCM", optimizer_fingerprint="abc",
    )
    assert a != b


def test_distinct_keys_for_distinct_optimizer_configs():
    fp1 = OptimizerConfig().fingerprint()
    fp2 = OptimizerConfig(sella_fmax=0.001).fingerprint()
    a = make_ts_cache_key(
        workflow="worked_example", substrate_id="nh3", tier="xtb",
        method="GFN2-xTB", optimizer_fingerprint=fp1,
    )
    b = make_ts_cache_key(
        workflow="worked_example", substrate_id="nh3", tier="xtb",
        method="GFN2-xTB", optimizer_fingerprint=fp2,
    )
    assert a != b


def test_lookup_or_compute_calls_compute_exactly_once(tmp_path: Path):
    cache = TSCache(root=tmp_path)
    call_count = {"n": 0}

    def _compute():
        call_count["n"] += 1
        return _result(barrier=6.11)

    cfg = OptimizerConfig()
    entry1, miss1 = cache.lookup_or_compute(
        workflow="worked_example", substrate_id="nh3_inversion",
        tier="xtb", method="GFN2-xTB", optimizer_config=cfg, compute=_compute,
    )
    entry2, miss2 = cache.lookup_or_compute(
        workflow="worked_example", substrate_id="nh3_inversion",
        tier="xtb", method="GFN2-xTB", optimizer_config=cfg, compute=_compute,
    )
    assert miss1 is True and miss2 is False
    assert call_count["n"] == 1, "compute() must run exactly once"
    assert entry1.cache_key() == entry2.cache_key()
    assert cache.stats.hits == 1 and cache.stats.misses == 1


def test_lookup_or_compute_persists_the_cache_key_on_the_result(tmp_path: Path):
    """The persisted TSResult carries its own cache_key — readers can
    cross-check that the entry they fetched is the one they meant."""
    cache = TSCache(root=tmp_path)

    entry, _ = cache.lookup_or_compute(
        workflow="worked_example", substrate_id="nh3_inversion",
        tier="xtb", method="GFN2-xTB",
        optimizer_config=OptimizerConfig(),
        compute=lambda: _result(),
    )
    assert entry.result.cache_key == entry.cache_key()


def test_substrate_id_canonical_under_smiles_order():
    a = substrate_id_from_smiles(("CCO", "CC=O"), ("CC=O", "CCO"))
    b = substrate_id_from_smiles(("CC=O", "CCO"), ("CCO", "CC=O"))
    assert a == b
    c = substrate_id_from_smiles(("CCO",), ("CC=O",))
    assert a != c, "single-component substrate must hash differently"


def test_cache_root_is_namespaced_by_version(tmp_path: Path):
    """v1 lives under .cache/ts/v1/ so a version bump doesn't collide."""
    cache = TSCache(root=tmp_path)
    assert cache.root == tmp_path / CACHE_VERSION


@pytest.mark.slow
def test_worked_example_second_call_hits_cache(tmp_path: Path):
    """End-to-end: a second compute_worked_example_barrier on a shared
    TSCache hits the persisted entry and skips the Sella refinement."""
    from macrocert.energetics.feedback import compute_worked_example_barrier

    cache = TSCache(root=tmp_path)
    b1, _, _, k1, s1 = compute_worked_example_barrier(tier="xtb", ts_cache=cache)
    b2, _, _, k2, s2 = compute_worked_example_barrier(tier="xtb", ts_cache=cache)

    assert b1 is not None and b2 is not None
    assert b1 == pytest.approx(b2)             # cache returned the same result
    assert k1 == k2                             # same key both times
    assert s1["misses"] == 1                    # first call was a miss
    assert s2["hits"] >= 1 and s2["misses"] == 0  # second call hit
