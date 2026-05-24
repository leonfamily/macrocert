"""Render a Certificate JSON into Markdown + HTML for human review.

Markdown is the canonical format (renders in any PR review tool, in
Obsidian, in IDE previews). HTML is a styled wrapper for browser
viewing. The chemist's `proof object` — the atom-mapped composed rule
— is embedded as a fenced GML code block so they can hand it to MØD
for verification themselves.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def render_markdown(cert: dict[str, Any]) -> str:
    lines: list[str] = []
    witness = cert["solver_witness"]
    composed = cert["composed_rule"]

    lines.append("# MØD-MacroCert Certificate Report")
    lines.append("")
    lines.append(f"- **spec_hash**: `{cert['spec_hash']}`")
    lines.append(f"- **schema version**: {cert.get('schema_version', 'n/a')}")
    lines.append(f"- **witness**: `{witness['kind']}`")
    lines.append("")

    if witness["kind"] == "optimal":
        lines.append("## Route summary")
        lines.append("")
        lines.append(f"- **objective value (bond-level expelled mass)**: "
                     f"{witness['obj_value']:.2f} g/mol")
        lines.append(f"- **dual bound**: {witness['dual_bound']:.2f} g/mol")
        lines.append(f"- **target sink**: `{cert['derivation_graph']['sink']}`")
        lines.append("")
        lines.append("### Reactions fired")
        lines.append("")
        edges_by_id = {e["id"]: e for e in cert["derivation_graph"]["hyperedges"]}
        for eid, n in cert["flow"].items():
            if int(n) <= 0:
                continue
            e = edges_by_id[eid]
            macro_tag = " (macrocyclization)" if e.get("is_macrocyclization") else ""
            lines.append(
                f"- **×{n}** `{e['rule_id']}`{macro_tag}  \n"
                f"  reactants: " + ", ".join(f"`{s}`" for s in e["sources"]) + "  \n"
                f"  products: " + ", ".join(f"`{s}`" for s in e["targets"]) + "  \n"
                f"  bond AE cost / firing: {e['expelled_mass_g_per_mol']:.2f} g/mol; "
                f"process AE cost / firing: "
                f"{e['expelled_mass_g_per_mol'] + e['reagent_mass_g_per_mol']:.2f} g/mol"
            )
        lines.append("")
        lines.append("### Atom-mapped composed rule (proof object)")
        lines.append("")
        lines.append(f"- **bond-level byproduct**: "
                     f"{composed.get('expelled_mass_g_per_mol', 0.0):.2f} g/mol")
        lines.append(f"- **rules traced**: "
                     f"{', '.join('`' + r + '`' for r in composed.get('rule_ids_traced', []))}")
        lines.append("")
        lines.append("```gml")
        lines.append(composed["gml"].strip())
        lines.append("```")
        lines.append("")

    elif witness["kind"] == "infeasible":
        lines.append("## NO-GO CERTIFICATE")
        lines.append("")
        lines.append("This certificate proves no route exists under the encoded")
        lines.append("rule set 𝓡, building blocks 𝓑, and step budget that closes")
        lines.append(f"`{cert['derivation_graph']['sink']}` and uses exactly one")
        lines.append("macrocyclization-class firing. The witness:")
        lines.append("")
        iis = witness.get("iis_constraint_ids", [])
        if iis:
            lines.append("### Irreducible infeasible subsystem (IIS)")
            lines.append("")
            for cid in iis:
                lines.append(f"- `{cid}`")
            lines.append("")
        farkas = witness.get("farkas_multipliers", {})
        if farkas:
            lines.append("### Farkas multipliers")
            lines.append("")
            for cid, mult in farkas.items():
                lines.append(f"- `{cid}`: {mult}")
            lines.append("")

    deps = cert.get("energetics_dependencies")
    if deps:
        lines.append("## Layer D — energetics (advisory, defeasible)")
        lines.append("")
        cs = deps.get("cache_stats", {})
        lines.append(f"- cache stats: {cs.get('hits', 0)} hits, "
                     f"{cs.get('misses', 0)} misses")
        lines.append("")
        per = deps.get("per_edge", {})
        if per:
            lines.append("| edge | tier | method | ΔG (kcal/mol) | barrier | cache key |")
            lines.append("|------|------|--------|---------------|---------|-----------|")
            for eid, ent in per.items():
                barr = ent.get("barrier_kcal_per_mol")
                lines.append(
                    f"| `{eid[:12]}…` | {ent['tier']} | "
                    f"`{ent['method']}` | {ent['dG_kcal_per_mol']:+.2f} | "
                    f"{barr if barr is not None else '—'} | "
                    f"`{ent['cache_key'][:12]}…` |"
                )
            lines.append("")
    else:
        lines.append("## Layer D — energetics")
        lines.append("")
        lines.append("Not applied to this certificate (RunSpec.energetics.enabled=false).")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> Per proposal §0: claims labelled *optimal* or *infeasible* are")
    lines.append("> sound relative to the encoded rule set 𝓡 and building-block")
    lines.append("> set 𝓑. Layer D verdicts (ΔG, barriers) are statistical /")
    lines.append("> defeasible — they refine ranking, never certify bench-readiness.")
    return "\n".join(lines) + "\n"


def render_html(md: str, *, title: str = "MØD-MacroCert report") -> str:
    body_lines = []
    for line in md.split("\n"):
        body_lines.append(html.escape(line))
    body = "<br>\n".join(body_lines)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
  body {{ font: 14px/1.45 ui-monospace, Menlo, monospace; max-width: 900px;
          margin: 2em auto; padding: 0 1em; color: #1a1a1a; }}
  pre {{ background: #f5f5f5; padding: 1em; overflow-x: auto; }}
  code {{ background: #f5f5f5; padding: 0 0.25em; border-radius: 3px; }}
  h1, h2, h3 {{ font-family: -apple-system, sans-serif; }}
  hr {{ border: 0; border-top: 1px solid #ccc; }}
</style></head>
<body>
<pre style="background:none;border:none;padding:0;white-space:pre-wrap">{body}</pre>
</body></html>
"""


def render_certificate(cert_path: Path, out_dir: Path | None = None) -> tuple[Path, Path]:
    cert = json.loads(cert_path.read_text())
    md = render_markdown(cert)
    html_doc = render_html(md, title=cert_path.parent.name)
    out_dir = out_dir or cert_path.parent
    md_path = out_dir / "report.md"
    html_path = out_dir / "report.html"
    md_path.write_text(md)
    html_path.write_text(html_doc)
    return md_path, html_path
