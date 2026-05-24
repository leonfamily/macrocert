# MØD-MacroCert — environment

Stack provisioning for the proposal. Apple Silicon (osx-arm64) host.

## Layout

- `pixi.toml` — two pixi environments managed from one workspace:
  - `default` — Layer A–C certifying core + Layer D energetics. Native arm64.
  - `casp` — AiZynthFinder, isolated because it pins `rdkit<2024`.
- `rules/` — GML rule library (one schema per macrocyclization tactic).
- `scripts/` — smoke tests; `smoke_host.py` for pixi env, `smoke_mod.py` for Docker.

## Components and where they live

| Proposal layer | Tool                       | Where                                                                     |
| -------------- | -------------------------- | ------------------------------------------------------------------------- |
| A–B (kernel)   | MØD 1.0.0.43               | pixi `default` (built from source; see "Native MØD build" below)          |
| A–C            | RDKit, pyscipopt, ASE      | pixi `default` (conda-forge, native arm64)                                |
| D — semiemp.   | xtb (GFN2-xTB)             | pixi `default`                                                            |
| D — DFT        | Psi4                       | pixi `default` (open-source; ORCA skipped — registration + no arm64)      |
| D — MLIP       | PyTorch + MACE-OFF         | pixi `default` PyPI; uses MPS device                                      |
| D — MLIP       | AIMNet2                    | pip from GitHub on demand (no PyPI release)                               |
| 2.6 — CASP     | AiZynthFinder              | pixi `casp` (isolated)                                                    |
| §3.5 optional  | SCINE/Chemoton             | **Not installed**: `scine-database-python` has no osx-arm64 conda build.  |
| —              | Docker `jakobandersen/mod` | Kept around for the LaTeX `mod_post` summary PDFs (PostMØD is OFF in the  |
|                |                            | native build because conda-forge graphviz lacks the cairo SVG plugin).    |

## Verifying

```bash
pixi run smoke         # RDKit, SCIP, xtb, Psi4, PyTorch, MACE
pixi run mod-smoke     # MØD inside container: load rule, build DG
pixi run -e casp python -c "import aizynthfinder; print(aizynthfinder.__version__)"
```

## Workflow — running the proposal

End-to-end on a single target:

```bash
# Layer A: validate the rule library (conservation re-check)
pixi run check-rules

# Layer A→B→C→E: run the pipeline, emit a verifiable Certificate
pixi run python -m macrocert.cli run data/targets/toy_macrolactam

# Independent re-check of the emitted certificate (works on a host without MØD)
pixi run macrocert-verify artifacts/toy_macrolactam/certificate.json

# Layer E: render a human-readable report
pixi run python -m macrocert.cli report artifacts/toy_macrolactam/certificate.json

# Bond-vs-process AE Pareto across all certificates
pixi run python -m macrocert.cli pareto artifacts/**/certificate.json -o artifacts/pareto.png
```

Full sweep (every target + verify + report + Pareto):

```bash
bash scripts/run_all.sh
```

Retrodictive validation panel:

```bash
pixi run pytest tests/panel/         # asserts each panel case reproduces its expected literature outcome
pixi run python scripts/calibrate_panel.py   # → data/validation_panel/REPORT.md, τ recomputation
```

The `data/validation_panel/panel_TODO.md` file lists the literature
cases (vancomycin, epothilone B, citreoviridin, norzoanthamine,
erythronolide B, ...) that the chemistry-team member will encode
before M5's ascomylactam A run; the v0 panel ships only surrogate
ω-aminoacid and α,ω-diene cases.

## Known gaps (and why they're acceptable for v1)

- **ORCA** (DFT): closed-source, registration, no arm64. Psi4 covers the
  documented DFT role in Layer D.
- **SCINE/Chemoton** (autonomous PES): proposal lists this as optional
  ("if autonomous PES exploration around the closure is wanted"). Falls
  back to ASE-driven CI-NEB/FSM with the MLIP/Psi4 calculators.
- **ASKCOS** (alt CASP): proposal §2.6 explicitly "consulted, not
  reproduced" — AiZynthFinder fills the same role with a lighter install.
## Native MØD build (osx-arm64)

`pixi run build-mod` compiles MØD into the `default` env. Five patches
needed on top of the upstream source — all applied in this worktree's
copy at `external/mod/`:

1. **LTO off** (`-DENABLE_IPO=OFF`). conda-forge clang's bundled `ar`
   path isn't seen by CMake's `CheckIPOSupported` probe.
2. **PostMØD off** (`-DBUILD_POST_MOD=OFF`). conda-forge graphviz lacks
   the cairo SVG plugin. The container is still useful when you want
   `mod_post` summary PDFs.
3. **OpenBabel C++17 binders define**
   (`-D_LIBCPP_ENABLE_CXX17_REMOVED_UNARY_BINARY_FUNCTION`). OpenBabel
   3.1.0's `plugin.h` uses `std::binary_function`, removed from libc++
   at C++17 strict.
4. **Apple-ld flag patches** (`libs/{libmod,pymod}/CMakeLists.txt`).
   conda-forge clang reports as `Clang` (not `AppleClang`), so MØD
   passes GNU-ld-only flags (`--exclude-libs,ALL`, `--no-undefined`,
   `--disable-new-dtags`) that Apple's ld rejects. Patches skip them on
   `APPLE` and use `-Wl,-undefined,error` as the Mach-O analogue.
5. **`Python3::Module` instead of `Python3::Python` on Darwin**
   (`libs/pymodutils/CMakeLists.txt`). The conda-forge `python3.11`
   binary is statically linked to libpython (it links only `libSystem`).
   Linking the extension against `libpython3.11.dylib` loads a *second*
   libpython copy with an uninitialised `_PyRuntime`; `libboost_python311`
   uses flat-namespace dynamic lookup for Py* symbols, so its
   `PyDict_New` call resolves to the second copy and crashes at
   `NULL+0x10` during module init. Using `Python3::Module` +
   `-Wl,-undefined,dynamic_lookup` is the standard setuptools-on-macOS
   pattern: Python symbols are resolved at runtime from the running
   interpreter, so there's only one `_PyRuntime` in the process.
