# Test fixtures

Stable test inputs that are *not* part of the production rule library
under `data/rules/`. Tests import these via paths anchored at the repo
root (per `pyproject.toml`'s `testpaths = ["tests"]`).

| File | Used by | Why it's here, not in `data/rules/` |
|---|---|---|
| `macrolactamization_baseline.gml` | `tests/verifier/test_conservation.py`, `test_gml_reader.py`, `test_stereo_conservation.py` | The M1 stereo-less baseline. The production rule at `data/rules/macrolactamization.gml` carries Workstream-F α-C overlays; the baseline keeps the verifier's conservation tests pinned against a fixed reference that doesn't move when the production rule's stereo annotations evolve. |
