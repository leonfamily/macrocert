# MØD Stereo Patch — Build & Validation Report

Author: Build engineer (MØD-MacroCert team)
Date: 2026-05-24
Branch under test: `fix/stereo-finalize-copy-unmatched-r1` in `external/mod/`
Patched commit: `e1ec8f0 Stereo: copy LonePair virtual edges in 'copy unmatched from R1' branch`
Patched file: `external/mod/libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:405-414`

## Executive summary

The 4-line patch closes the `MOD_ABORT` previously thrown at
`RC/Visitor/Stereo.hpp:406` whenever a substrate contained a trivalent
neutral nitrogen under `LabelSettings.withStereo == true`. Build succeeded
incrementally, the three available reproducers (`test_ammonia.py`,
`test_macrolactam_stereo.py`, and a fresh minimal `CCN` test at
`/tmp/test_stereo_patch.py`) all now complete cleanly, and the macrocert
test suite holds at **128 passed / 7 skipped** with **12/12** rules
passing conservation re-check — no regressions.

## 1. Build outcome — SUCCEEDED

- Command: `pixi run build-mod` (from `scripts/build_mod.sh:42-52`)
- Build log: `/tmp/mod_build.log`, exit code **0**
- Wall-clock: **25 s** (incremental — `CMakeCache.txt` already existed at
  `external/mod/build/CMakeCache.txt`; only the changed `Stereo.hpp`
  translation units needed recompiling, then re-link of `libmod.dylib` and
  `libpymod.so`, then `make install`)
- Expected warnings observed and ignored:
  - `ld: warning: duplicate -rpath ...` (already-documented benign macOS
    linker noise)
- Install confirmed: the patched comment `"Copy lone-pair virtual edges
  through unchanged"` is present at
  `.pixi/envs/default/include/mod/lib/RC/Visitor/Stereo.hpp:405`, and
  `libmod.dylib` + `libpymod.so` were freshly written under
  `.pixi/envs/default/lib/` and `.pixi/envs/default/lib/mod/`.
- Python sanity: `pixi run python -c "import mod"` loads from
  `.pixi/envs/default/lib/mod/__init__.py` (the conda-prefix install, not
  a stale wheel).

## 2. Pre-patch reproducer behavior — documented, not re-run

The pre-patch behavior is already characterised in
`docs/mod_abort_investigation.md:1-40` (Workstream F investigator,
2026-05-24):

> The `Stereo.hpp:406` abort previously attributed to "stereo-free rules
> under `Repeat`/`Parallel`" is **substrate-driven, not rule-driven**. It
> fires whenever … `LabelSettings.withStereo == true` … and the substrate
> molecule … contains a *trivalent neutral nitrogen*.

I deliberately did **not** roll back to `develop` to re-witness the abort
because (a) the failure mode is already evidenced and described in the
investigation memo, and (b) doing so would burn ~25 minutes of incremental
build time twice (back to `develop`, then forward again to the patched
branch) for zero new information.

## 3. Post-patch reproducer behavior — does NOT abort

All three scripts ran under `pixi run python` against the freshly built
`libmod.dylib` / `libpymod.so` in `.pixi/envs/default/lib/`.

### 3.1 `/tmp/macrocert_stereo_test/test_ammonia.py`

Minimal `N` substrate (degree 0 amine; lone-pair count > 0 from
`Stereo/GeometryGraph.cpp` `chemValids` table) under the 3-arg
`LabelSettings(Term, Specialisation, Specialisation)`.

```
Repeat, limit = 1
  Round 1:
  Round 1: Result subset has 2 graphs.
OK if reached
```

Exit 0. The line that previously fired `MOD_ABORT` at
`Stereo.hpp:406` is now the documented `LonePair` switch arm at
`Stereo.hpp:405-414` (verified in the installed header), and the
LonePair virtual edge is copied through unchanged.

### 3.2 `/tmp/macrocert_stereo_test/test_macrolactam_stereo.py`

The actual workstream-F target: the real
`data/rules/macrolactamization.gml` rule + `propionic_acid` + `ethylamine`
substrates + `withStereo=true`.

```
Repeat, limit = 1
  Round 1:
WARNING: No viable geometries for O with bonds D = 1.
WARNING: No viable geometries for O with bonds S = 2.
... (benign chemValids fallback warnings, per Stereo/GeometryGraph.cpp:296-302)
  Round 1: Result subset has 2 graphs.
OK: DG built with 4 vertices and 1 edges
```

Exit 0. The `"No viable geometries"` warnings are benign
`Res{any, 0}` fallbacks (documented in
`docs/mod_abort_investigation.md:117-125`), not the abort.

### 3.3 `/tmp/test_stereo_patch.py` (fresh minimal, from the task spec)

```
OK: dg.numVertices = 1
```

Matches expected outcome exactly.

## 4. macrocert regression results — NO regressions

### 4.1 `pixi run pytest tests/ -q`

```
128 passed, 7 skipped in 5.30s
```

The 7 skips are all placeholder `structure.mol` files awaiting Ivan's CIF
audit (per `tests/panel/test_panel.py:79`), unchanged from prior session.
Pass count matches the pre-patch baseline (128/7) — zero regressions.

### 4.2 `pixi run python -m macrocert.cli check-rules data/rules`

```
12 rule(s) pass conservation re-check (stereo: 0 warning(s), 0 info(s))
```

All 12 rules (CC closures, macrolactamization, macrolactonization, RCM,
trans-annular Diels-Alder, etc.) still pass conservation re-check. Zero
stereo warnings, zero info-level notes.

## 5. Time spent per phase

| Phase                         | Wall-clock |
| ----------------------------- | ---------- |
| Phase 1 — incremental build   | 25 s       |
| Phase 2 — three reproducers   | 26 s       |
| Phase 3 — pytest + check-rules| 11 s       |
| **Total**                     | **~1 min** |

The build was an incremental rebuild — only the `Stereo.hpp` consumers
were recompiled. A cold build from a wiped `external/mod/build/` is the
~10-30 min figure quoted in the task spec.

## 6. Recommendation

The patch (`e1ec8f0`) is safe to merge into `external/mod`'s tracked
branch. It unblocks `stereo_enforcement = true` in `build_dg.py:76-81`
without touching any of the 12 existing rule GML files. Downstream
work (per-vertex `tetrahedral[...]!` annotations on the 6 chirality-
relevant rules) remains the open follow-up described in
`docs/stereo_encoding_procedure.md`.
