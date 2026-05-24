# MØD source patches

Patches applied to the vendored MØD source at `external/mod/`. Each patch
is a standalone unified diff exported via `git format-patch`, suitable
for re-applying after a clean re-vendor (`git checkout -- external/mod &&
git apply patches/*.patch`).

## Inventory

### `0001-Stereo-copy-LonePair-virtual-edges-in-copy-unmatched.patch`

Fixes `RC::Visitor::Stereo::handleBoth`'s "copy unmatched from R1"
branch at `libs/libmod/src/mod/lib/RC/Visitor/Stereo.hpp:404-407`.

The upstream branch `develop` (at commit `c13e570`) aborts unconditionally
in the LonePair / Radical case, even though the same file's
`copyAllFromSide` lambda at lines 94-101 handles LonePair correctly. The
patch mirrors that pattern.

**Reproducer (without patch):** any rule application under
`LabelSettings.withStereo=true` on a substrate carrying an amine N at
degree 3+ triggers `MOD_ABORT;` at line 406. See
`docs/mod_abort_investigation.md` for the full root-cause analysis +
9 empirical scratch tests + chain-of-causation through `Stereo/Inference.hpp`,
`Rule.cpp`, and `RC::Super`.

**Reproducer (with patch):** the DG builds; LonePair virtual edges flow
through to the composed rule's stereo configuration unchanged.

**Status:** committed locally on branch `fix/stereo-finalize-copy-unmatched-r1`
in `external/mod/` (forked from `develop`). Upstream PR draft at
`patches/upstream_PR_draft.md`. Once the PR merges into
`jakobandersen/mod` and the upstream commit lands in macrocert's
vendored copy, this patch can be removed.

**Required for:** Workstream F runtime stereo enforcement, which is
load-bearing for the ascomylactam A M5 target (12 sp³ stereocenters +
atropoisomerism).

## How to re-apply (clean re-vendor)

```bash
cd external/mod
git checkout develop
git checkout -b fix/stereo-finalize-copy-unmatched-r1
git am ../../patches/0001-Stereo-copy-LonePair-virtual-edges-in-copy-unmatched.patch
cd ../..
pixi run build-mod
```

The local fork branch is preserved across `pixi run build-mod` rebuilds
because the build script reads from the working tree, not from a clean
upstream checkout.

## Build verification

After applying any patch in this directory:

1. `pixi run build-mod` — rebuild MØD from source
2. `pixi run pytest tests/` — confirm no regressions
3. Run scratch reproducer `/tmp/macrocert_stereo_test/*.py` (from
   `docs/mod_abort_investigation.md`) — confirm the fix
