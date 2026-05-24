"""Independent certificate verifier (kernel #2).

This subpackage must not import from macrocert.* or from mod. It
re-parses certificate JSON, the embedded GML rule bodies, and the
solver witness from scratch using only the standard library plus
optional RDKit for display. The structural test is: it runs in an
environment where MØD is uninstalled.
"""
