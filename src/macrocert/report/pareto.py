"""Bond-vs-process AE Pareto plot across a set of certificates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def render_pareto(cert_paths: Iterable[Path], output: Path) -> Path:
    points: list[tuple[float, float, str]] = []
    for p in cert_paths:
        cert = json.loads(Path(p).read_text())
        if cert["solver_witness"]["kind"] != "optimal":
            continue
        edges_by_id = {e["id"]: e for e in cert["derivation_graph"]["hyperedges"]}
        bond = 0.0
        proc = 0.0
        for eid, n in cert["flow"].items():
            n = int(n)
            if n <= 0:
                continue
            e = edges_by_id[eid]
            bond += n * float(e["expelled_mass_g_per_mol"])
            proc += n * float(e["expelled_mass_g_per_mol"] + e["reagent_mass_g_per_mol"])
        points.append((bond, proc, Path(p).parent.name))

    if not points:
        return Path()

    fig, ax = plt.subplots(figsize=(7, 5))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, s=80, alpha=0.7)
    for x, y, name in points:
        ax.annotate(name, (x, y), fontsize=7, alpha=0.7,
                    xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("bond-level expelled mass (g/mol)  — lower is better AE")
    ax.set_ylabel("process-level expelled mass (g/mol)  — lower is better AE")
    ax.set_title("MØD-MacroCert: certified routes, bond-vs-process AE")
    ax.grid(alpha=0.3)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=120)
    plt.close(fig)
    return output
