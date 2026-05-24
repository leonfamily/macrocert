#!/usr/bin/env bash
# Full M5-style smoke: run every target, verify every certificate, render
# every report, emit Pareto plot.
set -euo pipefail
cd "$(dirname "$0")/.."

TARGETS=(
    data/targets/toy_macrolactam
    data/targets/toy_macrolactam_energetics
    data/targets/toy_infeasible
    data/validation_panel/lactam_12_from_11_aminoundecanoic_acid
    data/validation_panel/lactam_14_from_13_aminotridecanoic_acid
    data/validation_panel/lactam_16_from_15_aminopentadecanoic_acid
    data/validation_panel/lactam_20_from_19_aminononadecanoic_acid
    data/validation_panel/rcm_13_from_pentadecadiene
    data/validation_panel/rcm_15_from_heptadecadiene
)

echo "=== Run ==="
for t in "${TARGETS[@]}"; do
    name=$(basename "$t")
    if [[ "$t" == data/validation_panel/* ]]; then
        artifacts="artifacts/panel"
    else
        artifacts="artifacts"
    fi
    python -m macrocert.cli run "$t" --artifacts-dir "$artifacts" 2>&1 | grep -E "witness=|mass:|cache" | sed "s/^/  /"
done

echo ""
echo "=== Verify ==="
shopt -s nullglob
ALL_CERTS=(artifacts/*/certificate.json artifacts/panel/*/certificate.json)
macrocert-verify "${ALL_CERTS[@]}"

echo ""
echo "=== Reports ==="
for c in "${ALL_CERTS[@]}"; do
    python -m macrocert.cli report "$c" 2>&1 | tail -2
done

echo ""
echo "=== Pareto plot ==="
python -m macrocert.cli pareto "${ALL_CERTS[@]}" -o artifacts/pareto.png

echo ""
echo "Done."
