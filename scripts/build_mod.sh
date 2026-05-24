#!/usr/bin/env bash
# Build MØD natively for osx-arm64 inside the pixi `default` env.
# Run via:  pixi run build-mod
#
# CMake knobs:
#   -DENABLE_IPO=OFF
#     conda-forge clang's bundled `ar` path isn't picked up by the CMake
#     CheckIPOSupported probe, so LTO fails even when the rest works.
#   -DBUILD_POST_MOD=OFF
#     conda-forge graphviz lacks the cairo SVG plugin needed by mod_post.
#   -DWITH_GUROBI=OFF -DWITH_CPLEX=OFF
#     Open-source only: CBC for MØD's built-in flow solver, pyscipopt for
#     the proposal's Layer-C ILP.
#   CXXFLAGS=-D_LIBCPP_ENABLE_CXX17_REMOVED_UNARY_BINARY_FUNCTION
#     OpenBabel 3.1.0's plugin.h uses `std::binary_function`, which libc++
#     drops at C++17 strict. The define re-enables the deprecated names.
#
# Source patches applied to external/mod (committed in this repo's worktree):
#   libs/libmod/CMakeLists.txt       Skip GNU-ld-only flags on Apple
#                                    (--exclude-libs, --no-undefined,
#                                    --disable-new-dtags); use
#                                    -undefined,error as the Mach-O analogue.
#   libs/pymod/CMakeLists.txt        Same flag-skip; let pymodutils inject
#                                    the dynamic_lookup option on Darwin.
#   libs/pymodutils/CMakeLists.txt   Link Python3::Module (not Python3::Python)
#                                    on Darwin and add -undefined,dynamic_lookup.
#                                    The python3.11 binary on conda-forge is
#                                    statically linked to libpython; linking
#                                    the extension against libpython3.11.dylib
#                                    would load a 2nd copy with uninitialised
#                                    _PyRuntime and crash boost_python's
#                                    PyDict_New at import time.
set -euo pipefail

cd "$(dirname "$0")/../external/mod"

# Bootstrap requires real history to produce a semver-style VERSION;
# the proposal worktree clones with full history (see SETUP.md).
[ -d build ] || mkdir build
cd build

export CXXFLAGS="${CXXFLAGS:-} -D_LIBCPP_ENABLE_CXX17_REMOVED_UNARY_BINARY_FUNCTION"

if [ ! -f CMakeCache.txt ]; then
    cmake .. \
        -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" \
        -DCMAKE_BUILD_TYPE=Release \
        -DENABLE_IPO=OFF \
        -DBUILD_POST_MOD=OFF \
        -DWITH_GUROBI=OFF \
        -DWITH_CPLEX=OFF
fi

make -j "$(sysctl -n hw.ncpu)"
make install
