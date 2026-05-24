#!/usr/bin/env bash
# AIMNet2 (Isayev group) — second-generation MLIP, no PyPI release.
# Install on demand into the pixi `default` env.
#
# Run via:  pixi run install-aimnet2
set -euo pipefail

python -m pip install --no-deps "git+https://github.com/isayevlab/AIMNet2.git@main"
echo "AIMNet2 installed; verify with: python -c 'import aimnet2_calc; print(\"ok\")'"
