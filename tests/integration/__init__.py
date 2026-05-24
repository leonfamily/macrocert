"""Integration tests — end-to-end pipeline assertions.

These tests exercise the full RunSpec → Layer A → B → C → Certificate
flow on the smallest fixtures we have (``toy_macrolactam``, plus one
panel case). They're slower than unit tests but still complete in
seconds because the fixtures are kept minimal on purpose.
"""
