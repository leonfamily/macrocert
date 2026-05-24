"""SMILES canonicalization for IR vertex identity.

MØD's ``Graph.smiles`` is canonical *within MØD's own perception* but
this is not stable across rule-application paths. Specifically, the
same molecule can appear with two distinct ``Graph.smiles`` strings —
one with aromatic-perceived bonds (``:c:c:``) and one with Kekulé
bonds (``C=CC``) — when a rule's R side is constructed via a
composition path that doesn't reach MØD's aromatic re-perception. The
ascomylactam A M5 run surfaced this with two distinct DG vertices
representing the same cyclized product.

The IR (kernel.ir.HyperFlowIR) keys vertices by SMILES, so these
become two separate vertices and the ILP solver cannot connect a
seco-precursor to the literature target. The certificate is technically
correct (it's a no-go for the *encoded* target) but the underlying
chemistry should match.

This module provides the single canonicalization function applied at
every boundary where a SMILES becomes a vertex identity:

  * ``dg_to_ir.build_ir`` — when converting MØD vertices to IR vertices
  * ``mod_backend`` — when looking up MØD vertices from IR identities
  * ``pipeline`` — when computing ``sink_smiles`` from the target and
    ``sources`` from the seco-precursor / building blocks

All callers funnel through ``canonical_smiles(smi)`` so that two
representations of the same molecule collapse to one IR vertex.

The implementation round-trips through RDKit with:

  * full sanitization (assigns aromaticity)
  * canonical ordering
  * isomeric SMILES (preserves stereo @/@@ tags)
  * NOT ``kekuleSmiles`` (output uses aromatic bond notation)
"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=4096)
def canonical_smiles(smi: str) -> str:
    """Return the canonical aromatic-perceived SMILES for ``smi``.

    If RDKit cannot parse the input, returns it unchanged. This is a
    quiet fallback (no warning) because MØD occasionally emits SMILES
    that round-trip with edge cases on aromaticity perception — we
    don't want a transient parse failure to crash certification.

    Stereo is preserved (the @/@@ chirality tags survive the
    round-trip).
    """
    if not smi:
        return smi
    # Lazy import — RDKit is heavy and not every consumer of this
    # module needs to pay the import at module-load time.
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return smi
    return Chem.MolToSmiles(
        mol, canonical=True, isomericSmiles=True, kekuleSmiles=False
    )
