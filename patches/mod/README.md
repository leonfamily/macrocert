# MØD source patches for native osx-arm64

These are the three patches applied on top of upstream MØD
(`develop` branch, commit `efd877f`) to make `import mod` work in the
pixi `default` env on Apple Silicon. They are tracked here in the
parent repo for audit so the build is reproducible without depending
on the working-tree state of `external/mod/`.

The patches are documented at length in `../../SETUP.md` § *Native
MØD build (osx-arm64)*. Short form:

| Patch                                           | What it fixes                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| `01-libmod-apple-ld-flags.patch`                | Skip GNU-ld-only flags (`--exclude-libs`, `--no-undefined`,        |
|                                                 | `--disable-new-dtags`) on Apple; use `-undefined,error` as the     |
|                                                 | Mach-O analogue.                                                   |
| `02-pymod-apple-ld-flags.patch`                 | Same flag-skip; let `pymodutils` inject `-undefined,dynamic_lookup` |
|                                                 | rather than fighting `-undefined,error`.                            |
| `03-pymodutils-darwin-python-module.patch`      | Link `Python3::Module` (not `Python3::Python`) on Darwin and add   |
|                                                 | `-undefined,dynamic_lookup`. Fixes the boost-python `PyDict_New`   |
|                                                 | SIGSEGV caused by a second `libpython` copy with uninitialized      |
|                                                 | `_PyRuntime`.                                                       |

To apply them to a fresh upstream clone:

```bash
cd external/mod
git apply ../../patches/mod/*.patch
```

`scripts/build_mod.sh` assumes patches are already applied to the
worktree at `external/mod/`.
