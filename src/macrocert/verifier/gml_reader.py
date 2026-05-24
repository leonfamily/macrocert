"""Minimal GML reader for MØD DPO rules.

Trust property: this module imports only from the standard library so
the verifier can run on a machine where MØD, RDKit, and the rest of
the producer stack are uninstalled. The parser handles only the
subset of GML that MØD rules use: nested `key [ ... ]` blocks with
`key value` leaves where values are quoted strings, integers, or
floats.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class GMLNode:
    id: int
    label: str
    charge: int = 0
    stereo: str | None = None


@dataclass
class GMLEdge:
    source: int
    target: int
    label: str


@dataclass
class GMLSide:
    nodes: dict[int, GMLNode] = field(default_factory=dict)
    edges: list[GMLEdge] = field(default_factory=list)


@dataclass
class GMLRule:
    ruleID: str
    left: GMLSide
    context: GMLSide
    right: GMLSide


class GMLParseError(ValueError):
    pass


def parse_rule(text: str) -> GMLRule:
    tokens = list(_tokenize(text))
    pos = 0

    def peek() -> str | None:
        return tokens[pos] if pos < len(tokens) else None

    def consume() -> str:
        nonlocal pos
        if pos >= len(tokens):
            raise GMLParseError("unexpected end of input")
        t = tokens[pos]
        pos += 1
        return t

    def expect(s: str) -> None:
        t = consume()
        if t != s:
            raise GMLParseError(f"expected {s!r}, got {t!r}")

    def parse_block() -> dict[str, object]:
        expect("[")
        result: dict[str, object] = {}
        while peek() != "]":
            key = consume()
            if peek() == "[":
                value: object = parse_block()
            else:
                value = _coerce(consume())
            if key in ("node", "edge"):
                result.setdefault(key, []).append(value)  # type: ignore[union-attr]
            else:
                result[key] = value
        expect("]")
        return result

    head = consume()
    if head != "rule":
        raise GMLParseError(f"expected top-level 'rule', got {head!r}")
    body = parse_block()

    return GMLRule(
        ruleID=str(body.get("ruleID", "")),
        left=_side_from(body.get("left", {})),
        context=_side_from(body.get("context", {})),
        right=_side_from(body.get("right", {})),
    )


def _coerce(raw: str) -> object:
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _side_from(block: object) -> GMLSide:
    if not isinstance(block, dict):
        return GMLSide()
    side = GMLSide()
    for n in block.get("node", []) or []:
        nd = GMLNode(
            id=int(n["id"]),
            label=str(n["label"]),
            charge=int(n.get("charge", 0)),
            stereo=str(n["stereo"]) if "stereo" in n else None,
        )
        side.nodes[nd.id] = nd
    for e in block.get("edge", []) or []:
        side.edges.append(
            GMLEdge(source=int(e["source"]), target=int(e["target"]), label=str(e["label"]))
        )
    return side


def _tokenize(text: str) -> Iterator[str]:
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace() or c == ";":
            i += 1
        elif c == "#":
            while i < n and text[i] != "\n":
                i += 1
        elif c in "[]":
            yield c
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                else:
                    j += 1
            if j >= n:
                raise GMLParseError("unterminated string")
            yield text[i:j + 1]
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "[];#":
                j += 1
            yield text[i:j]
            i = j
