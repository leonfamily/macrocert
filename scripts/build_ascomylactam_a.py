"""Build ascomylactam A (Chen 2019; CCDC 1515168) from primary-source connectivity.

This script constructs the molecular graph atom-by-atom from the
ring-connectivity description in Chen 2019 (and the triangulated
brief at data/targets/ascomylactam_a/research_findings.md), assigns
the 12 sp3 stereocenters per the X-ray absolute configuration
(1S, 4R, 7S, 8S, 10R, 12S, 13R, 14R, 15S, 16S, 1'R, 2'R), embeds in
3D with RDKit, and writes a strict V2000 Molfile via OpenBabel.

Atropoisomerism of the para-arene inside the 13-membered macrocycle
is NOT enforced by RDKit's embedder — the 3D pose may not match the
published X-ray atropisomer. See notes.md.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


TARGET_FORMULA = "C35H45NO5"
TARGET_STEREO_COUNT = 12
RING_SIZE = 13

# Absolute configuration from Chen 2019 single-crystal X-ray
# (Cu Kalpha, Flack -0.13(9), P2_1, T=150K; CCDC 1515168).
# Paper-label -> CIP descriptor.
STEREO_ASSIGNMENTS = {
    1: "S", 4: "R", 7: "S", 8: "S", 10: "R", 12: "S",
    13: "R", 14: "R", 15: "S", 16: "S",
    "1p": "R", "2p": "R",
}


def build_mol() -> tuple[Chem.Mol, dict[str | int, int]]:
    """Construct the RDKit Mol; returns (sanitized mol, paper-label -> atom-idx map)."""
    m = Chem.RWMol()

    def addC() -> int:
        return m.AddAtom(Chem.Atom("C"))

    def addN() -> int:
        return m.AddAtom(Chem.Atom("N"))

    def addO() -> int:
        return m.AddAtom(Chem.Atom("O"))

    # Carbocyclic core C1..C16
    c: dict[int, int] = {i: addC() for i in range(1, 17)}
    # Aromatic + macrocyclic primes C1'..C9'
    cp: dict[int, int] = {i: addC() for i in range(1, 10)}
    # C17 (enol), C18 (sp2), C19 (amide C=O)
    c[17] = addC()
    c[18] = addC()
    c[19] = addC()
    # Methyls C20..C25
    for i in range(20, 26):
        c[i] = addC()
    # OMe carbon C26 (1'-OMe)
    c[26] = addC()

    # Heteroatoms
    n_amide = addN()
    o_amide = addO()
    o_ether = addO()
    o_ome = addO()
    o_hemi = addO()
    o_enol = addO()

    S = Chem.BondType.SINGLE
    D = Chem.BondType.DOUBLE
    A = Chem.BondType.AROMATIC

    # Ring A (5-mem cyclopentenyl): C1-C2=C3-C4-C16-C1
    m.AddBond(c[1], c[2], S)
    m.AddBond(c[2], c[3], D)
    m.AddBond(c[3], c[4], S)
    m.AddBond(c[4], c[16], S)
    m.AddBond(c[16], c[1], S)

    # Ring B (6-mem cyclohexadienyl): C4-C5=C6-C7-C15-C16, sharing C4-C16 edge with A
    m.AddBond(c[4], c[5], S)
    m.AddBond(c[5], c[6], D)
    m.AddBond(c[6], c[7], S)
    m.AddBond(c[7], c[15], S)
    m.AddBond(c[15], c[16], S)

    # Ring C (6-mem cyclohexane): C8-C9-C10-C11-C12-C13(-C8)
    m.AddBond(c[8], c[9], S)
    m.AddBond(c[9], c[10], S)
    m.AddBond(c[10], c[11], S)
    m.AddBond(c[11], c[12], S)
    m.AddBond(c[12], c[13], S)
    m.AddBond(c[13], c[8], S)

    # Ring D (5-mem cyclopentane): C7-C8-C13-C14-C15
    # shared edges: C7-C15 with ring B, C8-C13 with ring C.
    m.AddBond(c[7], c[8], S)
    m.AddBond(c[13], c[14], S)
    m.AddBond(c[14], c[15], S)

    # Macrocycle (ring E): C14-O-C7'-C8'-C9'-C4'-C3'-C2'-C1'-C18=C17-C16-C15(-C14)
    m.AddBond(c[14], o_ether, S)
    m.AddBond(o_ether, cp[7], S)

    # para-arene: 6-mem aromatic C4'-C5'-C6'-C7'-C8'-C9'(-C4')
    m.AddBond(cp[4], cp[5], A)
    m.AddBond(cp[5], cp[6], A)
    m.AddBond(cp[6], cp[7], A)
    m.AddBond(cp[7], cp[8], A)
    m.AddBond(cp[8], cp[9], A)
    m.AddBond(cp[9], cp[4], A)
    for i in (4, 5, 6, 7, 8, 9):
        m.GetAtomWithIdx(cp[i]).SetIsAromatic(True)

    # Macrocycle continuation
    m.AddBond(cp[4], cp[3], S)
    m.AddBond(cp[3], cp[2], S)
    m.AddBond(cp[2], cp[1], S)
    m.AddBond(cp[1], c[18], S)
    m.AddBond(c[18], c[17], D)
    m.AddBond(c[17], c[16], S)

    # Ring F (γ-lactam, 5-mem): C1'-C2'-N(H)-C19(=O)-C18(-C1')
    m.AddBond(cp[2], n_amide, S)
    m.AddBond(n_amide, c[19], S)
    m.AddBond(c[19], c[18], S)
    m.AddBond(c[19], o_amide, D)

    # Methyl substituents
    m.AddBond(c[1], c[20], S)   # C20 on C1
    m.AddBond(c[2], c[21], S)   # C21 on C2 (sp2 vinyl Me)
    m.AddBond(c[4], c[22], S)   # C22 on C4 (quaternary)
    m.AddBond(c[6], c[23], S)   # C23 on C6 (sp2)
    m.AddBond(c[10], c[24], S)  # C24 on C10
    m.AddBond(c[12], c[25], S)  # C25 on C12

    # OMe on C1' (-O-CH3) and hemiaminal/enol hydroxyls
    m.AddBond(cp[1], o_ome, S)
    m.AddBond(o_ome, c[26], S)
    m.AddBond(cp[2], o_hemi, S)
    m.AddBond(c[17], o_enol, S)

    mol = m.GetMol()
    Chem.SanitizeMol(mol)

    label_to_idx: dict[str | int, int] = {}
    for i in range(1, 27):
        label_to_idx[i] = c[i]
    for i in range(1, 10):
        label_to_idx[f"{i}p"] = cp[i]
    label_to_idx["N"] = n_amide
    label_to_idx["O_amide"] = o_amide
    label_to_idx["O_ether"] = o_ether
    label_to_idx["O_ome"] = o_ome
    label_to_idx["O_hemi"] = o_hemi
    label_to_idx["O_enol"] = o_enol

    return mol, label_to_idx


def _set_chirality(mol: Chem.Mol, atom_idx: int, cip: str) -> None:
    """Set the CIP descriptor of an atom by trial-and-error on chiral tag.

    RDKit's CIP code (`AssignStereochemistry`) is the canonical mapping
    between (neighbor order, chiral tag) and (R/S); rather than
    hand-computing the parity, we try CW and CCW and accept whichever
    yields the requested CIP descriptor.
    """
    atom = mol.GetAtomWithIdx(atom_idx)
    for tag in (Chem.ChiralType.CHI_TETRAHEDRAL_CW, Chem.ChiralType.CHI_TETRAHEDRAL_CCW):
        atom.SetChiralTag(tag)
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        if atom.HasProp("_CIPCode") and atom.GetProp("_CIPCode") == cip:
            return
    raise ValueError(f"Failed to set CIP {cip} at atom idx {atom_idx}")


def assign_stereo(mol: Chem.Mol, label_to_idx: dict) -> None:
    rw = Chem.RWMol(mol)
    for label, cip in STEREO_ASSIGNMENTS.items():
        idx = label_to_idx[label]
        _set_chirality(rw, idx, cip)
    # Verify all assignments stuck.
    Chem.AssignStereochemistry(rw, cleanIt=True, force=True)
    for label, expected in STEREO_ASSIGNMENTS.items():
        idx = label_to_idx[label]
        a = rw.GetAtomWithIdx(idx)
        got = a.GetProp("_CIPCode") if a.HasProp("_CIPCode") else "?"
        if got != expected:
            raise ValueError(
                f"Stereo verification failed at paper-label {label}: "
                f"wanted {expected}, got {got}"
            )
    # Mutate caller's mol in place.
    mol.__init__(rw)


def main(out_dir: Path) -> None:
    mol, label_map = build_mol()
    formula = CalcMolFormula(mol)
    if formula != TARGET_FORMULA:
        raise SystemExit(f"Formula mismatch: got {formula}, expected {TARGET_FORMULA}")

    assign_stereo(mol, label_map)
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    stereos = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)
    assigned = [s for s in stereos if s[1] in ("R", "S")]
    if len(assigned) != TARGET_STEREO_COUNT:
        raise SystemExit(
            f"Stereocenter count mismatch: got {len(assigned)} assigned ({stereos}), "
            f"expected {TARGET_STEREO_COUNT}"
        )

    iso_smi = Chem.MolToSmiles(mol)
    print(f"formula:        {formula}")
    print(f"stereocenters:  {len(assigned)} assigned of {len(stereos)} total")
    print(f"canonical_smi:  {iso_smi}")

    mh = Chem.AddHs(mol)
    embed_ok = AllChem.EmbedMolecule(
        mh, randomSeed=0xC0FFEE, useRandomCoords=True, maxAttempts=200
    )
    used_2d = False
    if embed_ok != 0:
        # Try ETKDG with relaxed parameters
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        params.maxAttempts = 500
        params.randomSeed = 0xDEC0DE
        embed_ok = AllChem.EmbedMolecule(mh, params)
    if embed_ok != 0:
        print("3D embedding failed; falling back to 2D coordinates.")
        AllChem.Compute2DCoords(mh)
        used_2d = True
    else:
        try:
            AllChem.MMFFOptimizeMolecule(mh, maxIters=2000)
        except Exception:
            AllChem.UFFOptimizeMolecule(mh, maxIters=2000)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure.mol"

    # Write through obabel for strict V2000 output (matches toy_macrolactam).
    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tf:
        tmp = Path(tf.name)
    try:
        Chem.MolToMolFile(mh, str(tmp))
        # Replace the RDKit title block with a content header line:
        text = tmp.read_text()
        lines = text.splitlines()
        lines[0] = "ascomylactam_A Chen2019 CCDC1515168 (3D embed via RDKit)" if not used_2d else \
                   "ascomylactam_A Chen2019 CCDC1515168 (2D fallback via RDKit)"
        tmp.write_text("\n".join(lines) + "\n")
        subprocess.run(["obabel", str(tmp), "-O", str(out_path)], check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)

    # Patch the obabel-written title line to carry the citation (obabel
    # rewrites the title block on conversion).
    text = out_path.read_text()
    lines = text.splitlines()
    if lines:
        lines[0] = (
            "ascomylactam_A Chen2019 CCDC1515168 3D-RDKit" if not used_2d
            else "ascomylactam_A Chen2019 CCDC1515168 2D-RDKit-fallback"
        )
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}  (used_2d={used_2d})")

    # Also dump the atom-label map and canonical SMILES alongside for traceability.
    audit = out_dir / "atom_label_map.txt"
    rows = []
    for label, idx in sorted(label_map.items(), key=lambda kv: (str(type(kv[0])), str(kv[0]))):
        sym = mol.GetAtomWithIdx(idx).GetSymbol() if isinstance(idx, int) else "?"
        rows.append(f"paper={label!s:>10s}  rdkit_idx={idx:>3d}  element={sym}")
    audit.write_text(
        "# Paper-label -> RDKit atom index (heavy atoms only; built by build_ascomylactam_a.py)\n"
        f"# canonical_isomeric_smiles: {iso_smi}\n"
        "\n".join(rows) + "\n"
    )
    print(f"wrote {audit}")


if __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent.parent / "data" / "targets" / "ascomylactam_a"
    main(target_dir)
