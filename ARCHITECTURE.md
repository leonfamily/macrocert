# MØD-MacroCert — Architecture

A one-page map of the system and the load-bearing invariants. Pair
with [`README.md`](README.md) (status + quick start),
[`SETUP.md`](SETUP.md) (env provisioning), and
[`proposal.md`](proposal.md) (the original design document).

## The five layers

```
       ┌─────────────────────────────────────────────────────────────┐
CHEMIST│ A. SPECIFICATION   target graph + building blocks + rule lib │  axioms & terms
       │       │            GML rules; valence/conservation = typing  │
       │       ▼                                                       │
       │ B. GENERATION      strategy-bounded DPO expansion → hypergraph│  proof-search space
       │       │                                                       │
       │       ▼                                                       │
       │ C. CONSTRAINT      integer-hyperflow (M)ILP:                  │  the kernel
       │    SOLVING         max atom economy s.t. closes ring, ≤k steps│   → optimality cert
       │       │            ΔG-admissible; enumerate top-N; prove ∅    │   → IIS / infeasibility
       │  ═════╪═══════════════════════════════════════════════════   │  ── certifiable above ──
       │       ▼                                                       │  ── defeasible  below ──
       │ D. FEASIBILITY     MLIP screen → xtb → DFT refine             │  the "sorry":
       │    FILTER          NEB → Sella P-RFO TS search; lazy cache    │   trusted to prune,
       │       │                                                       │   not to prove
       │       ▼                                                       │
       │ E. CERTIFICATE     atom-mapped composed rule + AE values +    │  the proof object
       │    & HANDOFF       ΔG/barrier + provenance → report           │   for human review
       └─────────────────────────────────────────────────────────────┘ → CHEMIST
```

## File-to-layer map

| Layer | Code | Data | Docs |
|---|---|---|---|
| **A** Specification | `src/macrocert/spec/` (RunSpec, RuleLibrary, target encoder, SMILES canonicalize) | `data/rules/`, `data/building_blocks/`, `data/targets/`, `data/validation_panel/` | `docs/ascomylactam_a_encoding.md`, `docs/stereo_encoding_procedure.md`, every `docs/*_research.md` |
| **B** Generation | `src/macrocert/generate/` (strategies, build_dg, predicate framework) | — | `docs/workstream_d_*.md` (predicates), `docs/workstream_f_*.md` (stereo wiring) |
| **C** Kernel | `src/macrocert/kernel/` (IR, scip_backend, mod_backend, compose, objective, certify, dg_to_ir) — and `src/macrocert/verifier/` (independent kernel #2) | — | `docs/adversarial_verifier_roadmap.md`, `docs/adversarial_verifier_expansion.md` |
| **D** Energetics | `src/macrocert/energetics/` (cache, ts_cache, qm, mlip, ts_search, feedback) | `data/energetics_protocol.yaml` | `docs/energetics_protocol_research.md`, `docs/energetics_ts_search_landed.md`, `docs/ts_cache_landed.md` |
| **E** Report | `src/macrocert/report/` + `scripts/build_m5_campaign.py` | — | `docs/M5_REPORT_*.md` (auto-generated outputs) |
| MØD harness | `src/macrocert/spec/canonical.py`, `external/mod/` (vendored) | `patches/` | `docs/mod_stereo_reference.md`, `docs/mod_abort_investigation.md`, `docs/mod_patch_build_validation.md` |

## Load-bearing invariants

These are non-negotiable design properties. Code reviews reject
changes that violate them. The verifier and gate together enforce
them at runtime.

### 1. Kernel / `sorry` boundary

Layers A–C are *certifying*. Their outputs (certificate JSON) are
sound relative to the encoded rule set 𝓡, building-block set 𝓑, and
the generated hypergraph. Layer D is *defeasible* — the proposal's
`sorry` analogue. Layer-D numbers enter the certificate as named
hypotheses recorded in `energetics_dependencies`; the verifier checks
that the certificate is honest about which energetic claims it relied
on, but does **not** re-run xtb / MLIP / DFT.

### 2. Verifier independence

`macrocert-verify` is a separate-process re-checker. It imports
**only** from `src/macrocert/verifier/` (gml_reader, conservation,
stereo_conservation, schema/), the standard library, and optionally
RDKit (for SMILES display, never for conservation). It must run
cleanly on a machine where MØD is uninstalled. This is the structural
test that the kernel / `sorry` boundary is real, not just documented.

### 3. `expelled_mass` is derived, never stored

Bond-level expelled mass is recomputed by the verifier from the
composed rule's atom-map (R-side connected-component analysis
anchored at `retained_root_atom`). Storing it as metadata would
create a second source of truth that can drift. `reagent_mass` *is*
metadata, because it is a property of the disconnection tactic
(Yamaguchi vs Corey-Nicolaou vs T3P) rather than of any single
firing.

### 4. Backend-neutral IR

`kernel/ir.py` is the single hyperflow formulation. Both backends
consume it:

- `kernel/scip_backend.py` — pyscipopt path. Top-N enumeration plus
  IIS / Farkas extraction. The certificate path.
- `kernel/mod_backend.py` — `mod.hyperflow.Model` path. Fast top-N
  via the bundled solver. Used when no infeasibility certificate is
  requested.

Both write the same IR into the certificate, so a reader can
reconstruct the formulation without depending on either backend.

### 5. Content-addressed caches

`energetics/cache.py` (ΔG cache) and `energetics/ts_cache.py` (TS
saddle cache) both:

- key on `(rule_id, R/P SMILES, tier, method, …)` so DMF vs DCM,
  B3LYP vs PBE, or 5-image vs 7-image NEB never collide;
- carry a `CACHE_VERSION` so schema changes invalidate pre-fix entries
  cleanly;
- persist the cache key inside the on-disk record so readers can
  cross-check the entry they fetched is the one they meant;
- live under `.cache/` (gitignored, regenerable).

The certificate records the cache key it consulted. A future
cert-integrity SHA pass (`docs/adversarial_verifier_roadmap.md` P3
#7) makes the cache attestable cheaply.

### 6. SMILES canonicalization at every IR boundary

`spec/canonical.py` collapses aromatic + Kekulé representations of
the same molecule to one canonical form before either form reaches
the IR. Without this, MØD emits aromatic and Kekulé as distinct DG
vertices, the flow balance breaks, and the kernel finds the route
infeasible. The fix is load-bearing on every IR-emitting path.

### 7. Deterministic campaigns

`scripts/build_m5_campaign.py` sets `MACROCERT_MOD_SEED` (consumed by
`mod.rngReseed`) and `PYTHONHASHSEED=0` so two runs from the same
inputs produce byte-identical certificates. The pre-M5 gate's
reproducibility-hash check exists precisely to fail when this
property silently breaks.

## Trust reduction at a glance

```
RunSpec ───────► pipeline.run ─────► Certificate ─────► macrocert-verify
                       │                  ▲                    │
                       │                  │                    │ exit 0 / 10 / 20 / 30
                       ▼                  │                    ▼
                  kernel.ir + kernel.compose                 chemist trusts certificate
                       │                                     iff verifier said exit 0
                       ▼                                     AND they accept the rules /
                  kernel.scip_backend / kernel.mod_backend   building blocks / Layer-D
                       │                                     tier disclosed in the
                       ▼                                     `energetics_dependencies`
                  certify.emit
```

The trust chain is: chemist → verifier exit code → composed-rule
atom-map + IR + solver witness → rule library + building blocks.
Everything to the *right* of the verifier is checked by the verifier
on every run. Everything to the *left* is the chemist's
responsibility to audit (via the research briefs and target
encoding notes).

## Where to start as a new contributor

1. Read [`proposal.md`](proposal.md) — design intent.
2. Read this file — system layout + invariants.
3. Read [`HANDOFF.md`](HANDOFF.md) — current state + open follow-ups.
4. Run the quick-start from [`README.md`](README.md).
5. Walk one M5 report end-to-end:
   `docs/M5_REPORT_ascomylactam_a.md` ← `docs/ascomylactam_a_encoding.md`
   ← `data/targets/ascomylactam_a/` ← `scripts/build_m5_campaign.py`
   ← `src/macrocert/pipeline.py` ← every layer above.
6. Pick a P1/P2/P3 item from `HANDOFF.md` § "Open items, prioritized".
