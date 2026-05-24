"""Stereo conservation re-check for MØD DPO rules.

Workstream F (Component 2). The mass-conservation pass in
``conservation.py`` validates element/charge/edge integrity but is
*silent on stereo*. This module adds stereo-specific invariants that
can be checked purely from the GML text — no MØD import required, so
it remains compatible with the verifier's trust property (see
``verifier/__init__.py``).

Invariants implemented (from ``docs/mod_stereo_reference.md`` §3.1):

1. **Even-permutation discipline.** If a tetrahedral stereo vertex
   appears in both ``left`` and ``right`` with the same neighbour
   *set*, the two bracket lists must be even permutations of each
   other (i.e., the same chirality class — see
   ``external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp:118-155``).
   An odd-permutation pair silently encodes inversion. This is the
   single highest-value check.

2. **Fixation discipline.** A vertex that is fixed on one side
   (``TetrahedralFixed`` — bracket list + ``!``) and free on the other
   (``TetrahedralSym`` — bare ``tetrahedral`` or no annotation) flips
   between "patterns a chirality" and "creates/erases chirality".
   That is legitimate ("Change" / "Generalize" rules in MØD's paper
   examples) but suspicious without explicit intent. Emit as a
   warning.

3. **Edge stereo is documentation-only.** The MØD GML grammar
   accepts ``edge [ ... stereo "..." ]`` but no consumer interprets it
   (see ``mod_stereo_reference.md`` §5.1 and
   ``external/mod/libs/libmod/src/mod/lib/IO/GML.hpp``). Emit an
   info-level message so rule authors know it will be ignored.

4. **Geometry registration.** MØD registers exactly four geometries:
   ``any``, ``linear``, ``trigonalPlanar``, ``tetrahedral`` (see
   ``external/mod/libs/libmod/src/mod/lib/Stereo/GeometryGraph.cpp``).
   Only ``tetrahedral`` has working ``morphismIso``/``morphismSpec``;
   ``trigonalPlanar`` and ``linear`` are ``MOD_ABORT``. So a rule that
   *constrains* (i.e., uses ``!``) a non-tetrahedral geometry is
   warn-worthy because at runtime MØD will abort if the substrate
   side has matching geometry annotations.

The function ``check_rule_stereo_conservation(gml: str) ->
list[StereoIssue]`` returns a list of issues with severity levels
``"error" | "warning" | "info"``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from .gml_reader import GMLNode, GMLRule, parse_rule


Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class StereoIssue:
    """A single stereo-conservation finding.

    ``severity``:
      - ``error``: rule is incoherent; the runtime would silently
        misbehave (e.g., odd-permutation inversion under a "preserve"
        intent).
      - ``warning``: looks suspicious or relies on MØD behaviour that
        is incomplete (non-tetrahedral, Sym↔Fixed transitions).
      - ``info``: documentation-only annotation (e.g., edge stereo).
    """
    severity: Severity
    code: str
    message: str
    node_id: int | None = None


@dataclass(frozen=True)
class ParsedStereo:
    """Decomposition of the stereo-string sub-grammar from
    ``external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp``."""
    geometry: str | None        # e.g. "tetrahedral", or None when omitted
    neighbours: tuple[object, ...]   # ints (real edges) or single-char strs (virtual)
    fixed: bool                 # the trailing '!'
    raw: str


# ----------------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------------


def check_rule_stereo_conservation(gml_text: str) -> list[StereoIssue]:
    """Walk both sides of the rule and emit a list of stereo issues.

    Cross-reference: see ``docs/mod_stereo_reference.md`` §3.1 for the
    catalogue of invariants. Empty list ≡ "no stereo issues found"
    (which is the case for the entire current rule library — every
    rule under ``data/rules/`` is stereo-free as of Workstream F).
    """
    issues: list[StereoIssue] = []
    try:
        rule = parse_rule(gml_text)
    except Exception as e:
        # Defer to the conservation checker for syntax issues. A
        # malformed GML body is its problem, not ours.
        return [StereoIssue(
            severity="error",
            code="parse_error",
            message=f"could not parse rule GML: {e}",
        )]

    # Invariant 3: edge-stereo (any side) is documentation-only.
    # The GML grammar accepts ``edge [ ... stereo "..." ]`` but no MØD
    # consumer reads it. Detect by raw text scan because our reader
    # does not preserve edge stereo (see gml_reader.py:124-127).
    for side_name, m in _edge_stereo_occurrences(gml_text):
        issues.append(StereoIssue(
            severity="info",
            code="edge_stereo_ignored",
            message=(
                f"edge stereo on the {side_name} side will be ignored by "
                f"MØD ({m!r}); see mod_stereo_reference.md §5.1."
            ),
        ))

    # Vertex-level invariants per side.
    for side_name, side in (("left", rule.left), ("right", rule.right)):
        for nid, node in side.nodes.items():
            if node.stereo is None:
                continue
            parsed = _parse_stereo_string(node.stereo)
            if parsed is None:
                issues.append(StereoIssue(
                    severity="error",
                    code="stereo_parse_error",
                    message=(
                        f"node {nid} on {side_name} has unparseable stereo "
                        f"string {node.stereo!r} (see "
                        f"external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp)."
                    ),
                    node_id=nid,
                ))
                continue
            # Invariant 4: geometry registration.
            issues.extend(_check_geometry(parsed, nid, side_name))

    # Pairwise invariants (1) and (2) — vertices that bear stereo on
    # both L and R.
    stereo_vertices = sorted(
        set(rule.left.nodes) & set(rule.right.nodes)
    )
    for nid in stereo_vertices:
        l_node = rule.left.nodes[nid]
        r_node = rule.right.nodes[nid]
        if l_node.stereo is None and r_node.stereo is None:
            continue
        l_p = _parse_stereo_string(l_node.stereo) if l_node.stereo else None
        r_p = _parse_stereo_string(r_node.stereo) if r_node.stereo else None
        issues.extend(_check_pairwise(nid, l_node, r_node, l_p, r_p))

    return issues


# ----------------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------------


_GEOMETRY_VOCAB = {"any", "linear", "trigonalPlanar", "tetrahedral"}
_ENFORCED_GEOMETRIES = {"tetrahedral"}  # only one with working morphism (§5.2)


def _check_geometry(parsed: ParsedStereo, nid: int, side: str) -> list[StereoIssue]:
    """Invariant 4: warn if the geometry is unregistered, or if a non-
    tetrahedral geometry is fixed (``!``) — MØD will ``MOD_ABORT``
    when matching such a substrate (see §5.2/§5.3 of the reference).
    """
    out: list[StereoIssue] = []
    geom = parsed.geometry
    if geom is None:
        return out
    if geom not in _GEOMETRY_VOCAB:
        out.append(StereoIssue(
            severity="warning",
            code="unregistered_geometry",
            message=(
                f"node {nid} on {side} declares geometry {geom!r}, which is "
                f"not registered in MØD's GeometryGraph (registered: "
                f"{sorted(_GEOMETRY_VOCAB)}). MØD will likely error at load."
            ),
            node_id=nid,
        ))
        return out
    if geom not in _ENFORCED_GEOMETRIES and parsed.fixed:
        # Constraining (Fixed) a non-tetrahedral geometry is a runtime
        # MOD_ABORT trap. Loudly warn.
        out.append(StereoIssue(
            severity="warning",
            code="unenforced_geometry_fixed",
            message=(
                f"node {nid} on {side} uses fixed {geom!r} chirality (with "
                f"`!`), but MØD's {geom} configuration has MOD_ABORT in "
                f"morphismIso/morphismSpec — substrate matches with stereo "
                f"on the matched vertex will crash at runtime. See "
                f"mod_stereo_reference.md §5.2 and "
                f"external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/"
                f"{geom[0].upper()}{geom[1:]}.cpp."
            ),
            node_id=nid,
        ))
    return out


def _check_pairwise(
    nid: int,
    l_node: GMLNode,
    r_node: GMLNode,
    l_p: ParsedStereo | None,
    r_p: ParsedStereo | None,
) -> list[StereoIssue]:
    """Invariants 1 (even-permutation) and 2 (Sym↔Fixed)."""
    out: list[StereoIssue] = []

    # Invariant 2: fixation transitions.
    l_fixed = bool(l_p and l_p.fixed)
    r_fixed = bool(r_p and r_p.fixed)
    if (l_p is not None or r_p is not None) and (l_fixed != r_fixed):
        # One side TetrahedralFixed, the other TetrahedralSym (or
        # missing). Suspicious without explicit intent.
        l_kind = _kind_label(l_p, "(no stereo)")
        r_kind = _kind_label(r_p, "(no stereo)")
        out.append(StereoIssue(
            severity="warning",
            code="fixation_transition",
            message=(
                f"node {nid}: chirality discipline differs between L "
                f"({l_kind}) and R ({r_kind}). If the rule is intended "
                f"to create or erase chirality, that is fine; if it is "
                f"meant to preserve chirality, both sides should match "
                f"in fixation. See mod_stereo_reference.md §2.1."
            ),
            node_id=nid,
        ))

    # Invariant 1: even-permutation discipline. Only applies when both
    # sides have explicit bracket lists with the same neighbour set
    # over real (integer) edges.
    if (
        l_p is not None and r_p is not None
        and l_fixed and r_fixed
        and l_p.neighbours and r_p.neighbours
    ):
        l_ints = [x for x in l_p.neighbours if isinstance(x, int)]
        r_ints = [x for x in r_p.neighbours if isinstance(x, int)]
        # Skip if either side has virtual edges (letters) — pairing
        # them requires correlating fresh-virtual offsets which the
        # reference doc punts on.
        if (
            len(l_ints) == len(l_p.neighbours)
            and len(r_ints) == len(r_p.neighbours)
            and set(l_ints) == set(r_ints)
            and len(l_ints) >= 2
        ):
            parity = _permutation_parity(l_ints, r_ints)
            if parity == "odd":
                out.append(StereoIssue(
                    severity="error",
                    code="odd_permutation_inversion",
                    message=(
                        f"node {nid}: bracket lists on L ({l_ints!r}) and "
                        f"R ({r_ints!r}) are an *odd* permutation of each "
                        f"other. This silently encodes chirality "
                        f"inversion. If inversion is intended, document "
                        f"it in the rule's meta.yaml; if preservation is "
                        f"intended, fix the bracket order. See "
                        f"mod_stereo_reference.md §3.1 invariant 3 and "
                        f"§4.1."
                    ),
                    node_id=nid,
                ))
    return out


def _kind_label(p: ParsedStereo | None, fallback: str) -> str:
    if p is None:
        return fallback
    g = p.geometry or "(geometry-deduced)"
    return f"{g}{'Fixed' if p.fixed else 'Sym'}"


# ----------------------------------------------------------------------------
# Stereo-string sub-grammar (Python port of MØD's Boost.Spirit parser)
# ----------------------------------------------------------------------------


# Matches the sub-grammar in
# external/mod/libs/libmod/src/mod/lib/Stereo/IO/Read.cpp:
#   stereoEmbedding := geometry? >> ('[' neighbours? ']')? >> '!'? >> eoi
# where geometry is /[A-Za-z][A-Za-z0-9]*/ and neighbour is /-?\d+/
# or a single ASCII letter (virtual edge).
_STEREO_RX = re.compile(
    r"""^\s*
        (?P<geom>[A-Za-z][A-Za-z0-9]*)?\s*
        (?:\[\s*(?P<inside>[^\]]*)\s*\])?\s*
        (?P<fix>!)?\s*$""",
    re.VERBOSE,
)


def _parse_stereo_string(s: str) -> ParsedStereo | None:
    """Best-effort port of MØD's Boost.Spirit X3 sub-grammar
    (``Stereo/IO/Read.cpp:14-44``). Returns ``None`` if the string is
    not a valid stereo embedding."""
    m = _STEREO_RX.match(s)
    if m is None:
        return None
    geom = m.group("geom")
    inside = (m.group("inside") or "").strip()
    fixed = m.group("fix") is not None
    if geom is None and inside == "" and not fixed:
        # The MØD parser rejects the empty embedding (`!eoi` plus the
        # requirement that at least one component is present).
        return None
    neighbours: list[object] = []
    if inside:
        for raw in (x.strip() for x in inside.split(",") if x.strip()):
            if re.fullmatch(r"-?\d+", raw):
                neighbours.append(int(raw))
            elif re.fullmatch(r"[A-Za-z]", raw):
                neighbours.append(raw)
            else:
                return None
    return ParsedStereo(
        geometry=geom,
        neighbours=tuple(neighbours),
        fixed=fixed,
        raw=s,
    )


# ----------------------------------------------------------------------------
# Edge-stereo text scan
# ----------------------------------------------------------------------------


_EDGE_STEREO_RX = re.compile(r"""stereo\s+"(?P<v>[^"]*)\"""")


def _edge_stereo_occurrences(gml_text: str) -> list[tuple[str, str]]:
    """Return ``(side, raw_stereo_string)`` pairs for every edge block
    that has a ``stereo`` attribute. We do this with a bracket-aware
    scan because our GML reader drops edge stereo (see
    ``gml_reader.py:124-127``) and a naive regex over nested
    ``node [ ... ]`` / ``edge [ ... ]`` blocks does not handle the
    nesting correctly.
    """
    out: list[tuple[str, str]] = []
    for side_name in ("left", "context", "right"):
        body = _extract_side_body(gml_text, side_name)
        if body is None:
            continue
        for edge_body in _extract_edge_bodies(body):
            sm = _EDGE_STEREO_RX.search(edge_body)
            if sm:
                out.append((side_name, sm.group("v")))
    return out


def _extract_side_body(gml_text: str, side: str) -> str | None:
    """Return the inner body of the ``<side> [ ... ]`` block, with
    bracket nesting respected."""
    key = re.search(rf"\b{re.escape(side)}\s*\[", gml_text)
    if key is None:
        return None
    i = key.end()
    depth = 1
    n = len(gml_text)
    start = i
    in_string = False
    while i < n and depth > 0:
        c = gml_text[i]
        if in_string:
            if c == "\\" and i + 1 < n:
                i += 2
                continue
            if c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return gml_text[start:i]
        i += 1
    return None


def _extract_edge_bodies(text: str) -> list[str]:
    """Yield the inner body of every top-level ``edge [ ... ]`` block
    inside ``text``."""
    out: list[str] = []
    for m in re.finditer(r"\bedge\s*\[", text):
        i = m.end()
        depth = 1
        n = len(text)
        start = i
        in_string = False
        while i < n and depth > 0:
            c = text[i]
            if in_string:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == '"':
                    in_string = False
            else:
                if c == '"':
                    in_string = True
                elif c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                    if depth == 0:
                        out.append(text[start:i])
                        break
            i += 1
    return out


# ----------------------------------------------------------------------------
# Permutation parity (Tetrahedral.cpp:118-155 Good/Bad partition)
# ----------------------------------------------------------------------------


def _permutation_parity(src: list[int], dst: list[int]) -> Literal["even", "odd"]:
    """Parity of the permutation that maps ``src`` to ``dst``.

    Mirrors the partition of {0,1,2,3}-permutations into the ``Good``
    and ``Bad`` tables in
    ``external/mod/libs/libmod/src/mod/lib/Stereo/Configuration/Tetrahedral.cpp:118-155``
    (even ↔ Good ↔ same chirality; odd ↔ Bad ↔ enantiomer). The
    implementation here is the generic cycle-decomposition algorithm —
    valid for any tetrahedral/4-tuple permutation that MØD supports.
    """
    assert sorted(src) == sorted(dst)
    pos = {v: i for i, v in enumerate(dst)}
    perm = [pos[v] for v in src]
    visited = [False] * len(perm)
    transpositions = 0
    for i in range(len(perm)):
        if visited[i]:
            continue
        j = i
        cycle_len = 0
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            cycle_len += 1
        transpositions += cycle_len - 1
    return "even" if transpositions % 2 == 0 else "odd"
