# A Constraint-Certified Mechanization for High-Atom-Economy Macrocyclization Design

**Working name:** MØD-MacroCert
**Target case study:** forward, diversification-rich, high-atom-economy closure of the 13-membered ring of ascomylactam A
**Audience:** a small team spanning graph-rewriting / formal methods, computational quantum chemistry, cheminformatics engineering, and synthetic organic chemistry
**Document type:** problem description · literature review · technical proposal

---

## 0. Orienting idea: this is interactive theorem proving, ported to mechanism-level chemistry

The request that motivated this document was precise: not "let an AI design the synthesis," but "build the chemistry analogue of the Lean 4 workflow I use to constrain the design of complex systems — encode the object and its admissibility conditions, let a kernel/solver establish which directions survive, collapse an intractable space to a small certified set, and keep every judgment call with the human." The whole proposal is organized around making that analogy literal and load-bearing rather than rhetorical.

The correspondence we will hold ourselves to:

| Interactive theorem proving (Lean 4)                              | This mechanization                                                                                                                                                       |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Well-typedness / the kernel's type checker                        | Chemical validity: conservation of atoms, charge, and bond order, enforced _by construction_ by the double-pushout (DPO) rewriting formalism                             |
| A term / definition                                               | A molecular graph (target, building blocks, intermediates)                                                                                                               |
| An inference rule / axiom                                         | A reaction rule, written as a DPO span `L ← K → R` in MØD's GML rule language                                                                                            |
| A derivation / proof object                                       | A _derivation graph_ of rule applications; a synthetic route is a sub-object of it                                                                                       |
| The theorem to be proved                                          | A _pathway query_: "there exists a route, under rule set 𝓡 and building-block set 𝓑, that closes the macrocycle with atom economy ≥ τ and ≤ k steps" — or its refutation |
| Tactics / decision procedures / automation                        | MØD generation _strategies_ (to build the network) + an (M)ILP solver (to search pathways)                                                                               |
| Elaboration / typeclass resolution collapsing many steps into one | _Rule composition_: collapsing a multi-step path into a single atom-traced coarse rule whose net transformation can be inspected                                         |
| The proof certificate checked by the kernel                       | The composed, atom-mapped overall rule + the conservation check + the ILP optimality/infeasibility certificate                                                           |
| `sorry` / trusted external axioms                                 | The **energetic feasibility** verdicts from MLIP/DFT — empirical and defeasible, _not_ deductive. This is the part of the system we explicitly do not trust as a proof   |
| Undecidable fragment requiring human-guided tactics               | The generated chemical space is in general infinite and the pathway search is NP-hard; strategies and budgets bound it, and a chemist steers it                          |

**The single most important honesty constraint in this project** falls directly out of that last row. A theorem prover certifies _soundness relative to its axioms_. This system can genuinely certify statements of the form

> _no pathway in the generated network closes the ring while meeting atom-economy threshold τ under rule set 𝓡_

— a real, decision-useful **no-go result**, exactly the "rule out whole directions / reduce to clear options" function Lean provides. It **cannot** certify that a surviving route will work at the bench. The rule set's completeness is a modeling assumption, and the energetics layer is statistical. MØD-MacroCert is therefore a _constraint-certified design assistant_, not a synthesis-correctness prover. Everything below is engineered to make the certifiable part rigorous and the defeasible part clearly labelled.

---

## 1. Problem description and project scope

### 1.1 The concrete problem

Given the experimentally verified structure of a complex macrocyclic target — here ascomylactam A, a 13-membered-ring macrocyclic alkaloid — mechanize the following decision problem:

> Over a controlled space of macrocyclization disconnections that close the 13-membered ring, enumerate the candidate forward ring-closing strategies, rank them by a formally defined atom-economy objective, filter them by computed thermodynamic and kinetic feasibility, and return a small set of _certified candidates_ — each accompanied by a machine-checkable provenance object — together with, where applicable, a certificate that some regions of the design space are provably empty under the stated assumptions.

The deliverable for the chemist is not "the route." It is a pruned, ranked, annotated option set plus the explicit no-go regions, so that human retrosynthetic judgment is spent only where it is actually needed.

### 1.2 Why this target, and why it is hard

Ascomylactam A was first reported in 2019 from the mangrove endophytic fungus _Didymella_ sp. CYSK-4; it is a decahydrofluorene-type analogue presenting a (6/5/6/5) tetracyclic core fused to a 13-membered macrocyclic moiety, with absolute configuration fixed by single-crystal X-ray diffraction [Chen 2019]. It belongs to the cytochalasan structural class — fungal PKS–NRPS hybrid metabolites built from a polyketide chain condensed with an amino acid (phenylalanine in the aryl-bearing members), released reductively, cyclized (Knoevenagel), and elaborated by an intramolecular Diels–Alder that forges the fused carbocyclic/isoindolone core, with macrocyclization completing the perimeter [Skellam 2017; Scherlach 2010]. Two features make it a genuine frontier target rather than a teaching exercise:

1. **No reported total synthesis** (as of this writing), so there is no literature route to anchor on — the design space is open.
2. **The brief is multi-objective and partly novel**: (i) maximize downstream diversification, (ii) require a _novel, high-atom-economy_ macrocyclization, (iii) deliver something a graduate team can actually run. Objective (ii) is precisely the part that data-driven retrosynthesis tools handle worst (Section 2.6), and precisely the part a mechanism-level formal model handles best, because atom maps and conservation are first-class.

### 1.3 In/out of scope

**In scope.** Mechanism-level encoding of the target and a curated building-block set; a rule library of macrocyclization disconnection _schemas_; deterministic generation of the reachable disconnection network; a formally specified atom-economy objective and an (M)ILP pathway search with optimality/infeasibility certificates; an energetic feasibility filter (MLIP screen → DFT refinement) over surviving ring-closure steps; a provenance/certificate object and a chemist-facing report.

**Out of scope (v1).** Full de novo route prediction from commercial starting materials (the heuristic CASP layer is consulted, not reproduced); quantitative yield prediction; solvent/temperature optimization; automatic stereochemical outcome prediction beyond feasibility screening; anything claiming bench-readiness without human review.

### 1.4 Success criteria

- **Soundness of the certified claims.** Every "no route with AE ≥ τ" claim is backed by an ILP infeasibility certificate over an explicitly serialized network; every ranked candidate carries an atom-mapped composed rule that passes an independent conservation re-check.
- **Retrodictive validity.** On a held-out set of _known_ macrocyclizations (RCM, macrolactamization, transannular Diels–Alder cases drawn from the reviews in Section 2.2), the pipeline recovers the literature ring-closure as a top-ranked, feasibility-passing candidate.
- **Decision utility.** For ascomylactam A, the system reduces a combinatorially large disconnection space to a human-reviewable shortlist (target: ≤ 10 strategy families) with transparent reasons for every exclusion.

---

## 2. Literature review

### 2.1 The target and its biosynthetic logic (what the rules should respect)

Cytochalasans share a macrocycle fused to a perhydroisoindolone (or, in the ascomylactam/phomapyrrolidone sub-series, a more carbocyclic decahydrofluorene-type) core; molecular diversity arises from (1) the amino-acid–derived pyrrolidinone/lactam, (2) the carbocyclic ring system, and (3) the macrocycle, which across the family appears as 11- or 13-membered carbocycles, lactones, carbonates, and — diagnostically for the "-lactam" series — macrolactams, decorated by oxidative tailoring [Skellam 2017; Scherlach 2010; biosynthesis studies of the PKS–NRPS hybrid, reductive release, Knoevenagel and Diels–Alder steps]. Two consequences for us: first, the **biosynthetic disconnections are themselves chemically privileged hypotheses** (a biomimetic transannular Diels–Alder, or a late macrolactamization at the ring amide) and should be first-class entries in the rule library; second, the **exact ring membership** — which atoms and which heteroatom positions constitute the 13-membered perimeter — must be taken verbatim from the deposited crystal structure (CCDC entry associated with [Chen 2019]) and encoded as the ground-truth target graph. The team must not infer connectivity from the class; it must read it from the structure.

### 2.2 Macrocyclization tactics and atom economy (the chemistry to encode)

The modern macrocyclization toolbox is well reviewed [Gradillas 2006 (RCM); Martí-Centelles *Chem. Rev.* 2015 (preorganization); *Stereoconfining macrocyclizations*, *Nat. Prod. Rep.* 2019; *Lessons from Natural Product Total Synthesis*, *Acc. Chem. Res.* 2021; *Unconventional Macrocyclizations*, *ACS Cent. Sci.* 2020]. The dominant ring-closing tactics and their atom-economy signatures — the quantity our objective will score — are:

- **Macrolactamization** (amide closure): byproduct is essentially H₂O (after activation); intrinsically _very high atom economy_, and biosynthetically aligned for the lactam series. The reviews note its frequent superiority over alternatives (e.g., SNAr) for medium/large lactams.
- **Macrolactonization** (Yamaguchi/Shiina/Corey–Nicolaou): high atom economy for the bond itself, but activators add stoichiometric mass to the _process_ (a distinction we formalize in Section 3.3 as bond-level vs process-level atom economy).
- **Ring-closing metathesis (RCM)** and **ring-closing alkyne metathesis (RCAM)**: C–C closure expelling only ethylene (or 2-butyne); high atom economy, but with E/Z and semireduction caveats.
- **Transannular / intramolecular Diels–Alder**: cycloadditions add no atoms at all → _maximal_ atom economy, and biomimetic here.
- **Transition-metal cross-coupling and C–H/C–H activation macrocyclization**: ranging from moderate (halide + organometal, with stoichiometric byproducts) to very high (dehydrogenative C–H/C–H, expelling H₂/H₂O).

The central modeling point: **atom economy partially orders these tactics independently of any particular molecule**, which is exactly why it makes a good _objective_ and _filter_ in a generative search.

The canonical definition we adopt is Trost's [Trost, *Science* 1991]: atom economy is the ratio of the molar mass of atoms retained in the desired product to the molar mass of all atoms in the reactants. We extend it to _pathway_ atom economy in Section 3.3.

### 2.3 Graph transformation as mechanism-level chemistry; the DPO formalism and MØD

Rule-based chemistry represents molecules as labelled graphs and reactions as graph-rewriting rules; reaction networks are generated by iterated rule application from a seed set. Among the frameworks, Kappa and BioNetGen use single-pushout-style binding-site abstractions suited to biological signalling, whereas **MØD** uses the **double-pushout (DPO)** approach, which is the right altitude for organic synthesis because it tracks every atom and bond explicitly [Andersen 2016 (software package); Andersen 2017 (intermediate level of abstraction)]. A DPO rule is a span `L ← K → R`: `L` is the reactant pattern, `R` the product pattern, and the interface `K` is what is preserved. Because nothing in `K` is created or destroyed, **conservation of mass, atom type, and charge is structural, not checked after the fact**, and a _consistent atom-to-atom map_ between reactants and products is induced automatically [Andersen 2016; "A Software Package for Chemically Inspired Graph Transformation"]. DPO is invertible and side-effect-free, which is why it, rather than SPO, models bond reorganization faithfully [Rule-Based Gillespie simulation note, 2025]. MØD is implemented in C++ with comprehensive Python bindings, reads molecules from SMILES and rules/graphs from GML, and ships visualization for molecules, rules, DPO diagrams, and the generated hypergraphs [Andersen 2016; MØD documentation].

Three MØD capabilities are pillars of this proposal:

- **Generation strategies** for controlling the combinatorial explosion of the generated space — without them, chemical graph rewriting is in general unbounded (indeed Turing-complete on polymeric tapes), so naïve breadth-first expansion is hopeless [Andersen 2014, "Generic Strategies for Chemical Space Exploration"].
- **Stereo-aware rules**, necessary because ascomylactam is stereochemically dense and a macrocyclization's value is inseparable from the configuration it sets [Andersen 2017, "Chemical Graph Transformation with Stereo-Information"].
- **Rule composition**, which collapses a multi-step derivation into a single coarse rule that _preserves the atom traces through the pathway_ — the mechanism by which we turn a route into an inspectable, atom-mapped certificate, and the same machinery used for isotope-labelling design [Andersen 2018, "Rule Composition…"; Andersen 2014, "50 Shades of Rule Composition"].

### 2.4 Pathways as integer hyperflows; the thermodynamic MILP extension

MØD models a reaction network as a directed multi-hypergraph (molecules = vertices, reactions = hyperedges) and a _pathway_ as an **integer hyperflow**: a non-negative integer multiplicity on each hyperedge (how many times each reaction fires) subject to flow conservation at every molecule vertex, augmented with detailed routing constraints. Insisting on _integer_ (not fractional, as in flux-balance or elementary-mode analysis) flows is what lets the model answer mechanistic questions and _enumerate optimal and near-optimal pathways_, at the cost of solving generally hard integer linear programs [Andersen 2019, "Chemical Transformation Motifs — Modelling Pathways as Integer Hyperflows," *IEEE/ACM TCBB*]. The framework has been used to explore the design space of non-oxidative glycolysis (recovering and _improving on_ hand-designed pathways) and the formose process [ibid.]. A 2024–2025 extension folds **thermodynamic constraints** into the same hyperflow model via mixed-integer linear programming, allowing pathways to be required to be thermodynamically favourable and ranked by thermodynamics-based metrics, demonstrated on HCN–formamide chemistry where it surfaced alternatives superior to the literature hypothesis [arXiv:2411.15900, 2025]. This is the direct precedent for using the _same_ solver to carry our atom-economy objective and a thermodynamic admissibility constraint simultaneously.

### 2.5 Energetic feasibility: QM, semiempirics, and machine-learned potentials

Whether a proposed ring-closing step is _physically_ viable — surmountable barrier, favourable or at least accessible ΔG — is a potential-energy-surface question, answered by locating minima and transition states. Full DFT is accurate but expensive; the field's response is a tiered stack:

- **GFN2-xTB**, an extended-tight-binding semiempirical method with self-consistent multipole electrostatics and D4 dispersion, parameterized through Z = 86 — a fast, broad "floor" for geometry and relative energies [GFN2-xTB, as benchmarked in arXiv:2604.00405, 2026].
- **Machine-learned interatomic potentials (MLIPs)** for near-DFT accuracy at orders-of-magnitude lower cost: transferable organic force fields such as **MACE-OFF23** (barrier-height errors ≈ 0.25 kcal/mol vs reference for the larger models) and **AIMNet2** (comparable to small MACE-OFF) [MACE-OFF, *JACS* 2025], with newer foundation models trained on the Open Molecules 2025 set performing best in transition-state workflows.
- **Automated transition-state search** combining these potentials with path methods — climbing-image nudged elastic band (CI-NEB) and the freezing/growing-string method (FSM). A 2026 benchmark over 58 reactions reports that OMol25-trained models (e.g., MACE-OMol25) reach a 96.6% TS-search success rate at fewer than four DFT-gradient evaluations per reaction [arXiv:2604.00405, 2026]. Generative TS approaches (React-OT and successors) target the same bottleneck [Adv. Sci. 2025].
- **Autonomous reaction-network exploration** as the integrated engine: SCINE/Chemoton screens potential-energy surfaces for intermediates and transition states across arbitrary reaction chemistry, with a human-in-the-loop interface and pluggable energy backends [Chemoton 2.0, *JCTC* 2022], and MLIPs are being embedded to make this tractable, with reported ~10⁴× acceleration of network exploration relative to reference QM [Lifelong MLPs, *JCTC* 2025; reactive-MLP preprint, ChemRxiv 2026].

**The honest caveat that fixes our architecture.** On _out-of-distribution_ reaction networks, even the best MLIPs show transition-state-energy MAEs above 5 kcal/mol — far worse than their ≤ 2 kcal/mol on in-distribution validation sets [Adv. Sci. 2025]. A novel macrocyclization is, by construction, out-of-distribution. Therefore MLIPs are used **only as a cheap pre-filter to triage and rank**, and any candidate that informs a go/no-go recommendation is **refined with DFT** (e.g., ORCA/Psi4). The MLIP layer is the system's `sorry`: trusted to prune, never to prove.

### 2.6 The complementary heuristic layer (CASP), and where it fails

Computer-aided synthesis planning — Synthia/Chematica [Grzybowski and coworkers], ASKCOS [Coley and coworkers, MIT], AiZynthFinder [Genheden et al., AstraZeneca] — performs learned/expert-rule tree search over _known_ reaction space and is excellent for the diversification objective (i): proposing fragment couplings and functional-group interconversions with literature precedent. But these tools extrapolate from observed reactions, so they are weakest exactly at objective (ii), a _novel_ ring closure with no precedent to retrieve. The intended division of labour: CASP supplies and decorates the acyclic precursor arms (precedented chemistry, diversification); MØD-MacroCert owns the unprecedented ring-closing event (mechanism-level, atom-economy-certified). The two are consulted in series, not merged.

### 2.7 Formal-methods precedent

The analogy is not merely aspirational. Lean 4 itself is both a dependently typed programming language and an interactive theorem prover [de Moura & Ullrich, CADE 2021]. Chemistry-side formalization is nascent — general provers have been used to formalize chemical _physics_ (gas laws, kinematics) [arXiv:2210.12150, 2022] — but no chemistry-native prover exists. MØD's hyperflow + (M)ILP machinery is the closest _operational_ analogue of the "specify, constrain, certify, reduce to options" loop for mechanism-level synthesis, and the DPO foundation gives it the categorical rigor (it is firmly grounded in category theory [Andersen 2018]) that makes the "type checker" metaphor accurate rather than loose.

---

## 3. Technical proposal: architecture

The pipeline has five layers, A–E, mirroring the Lean correspondence of Section 0. Layers A–C are _deterministic and certifying_; layers D–E are _defeasible and advisory_. The boundary between them is the central design commitment.

```
            ┌─────────────────────────────────────────────────────────────┐
  CHEMIST → │ A. SPECIFICATION   target graph + building blocks + rule lib   │  (the "axioms & terms")
            │       │            GML rules; valence/conservation = typing    │
            │       ▼                                                         │
            │ B. GENERATION      strategy-bounded DPO expansion → hypergraph  │  (proof-search space)
            │       │                                                         │
            │       ▼                                                         │
            │ C. CONSTRAINT      integer-hyperflow (M)ILP:                    │  (the "kernel")
            │    SOLVING         max atom economy s.t. closes ring, ≤k steps, │   → optimality cert
            │       │            ΔG-admissible; enumerate top-N; prove ∅      │   → infeasibility cert
            │  ═════╪═════════════════════════════════════════════════════   │  ── certifiable above ──
            │       ▼                                                         │  ── defeasible below ──
            │ D. FEASIBILITY     MLIP screen (rank/triage) → DFT refine       │  (the "sorry": trusted
            │    FILTER          CI-NEB / FSM transition states               │   to prune, not to prove)
            │       │                                                         │
            │       ▼                                                         │
            │ E. CERTIFICATE     atom-mapped composed rule + AE value +       │  (the proof object,
            │    & HANDOFF       ΔG/barrier estimates + provenance → report   │   for human review)
            └─────────────────────────────────────────────────────────────┘ → CHEMIST
```

### 3.1 Layer A — Specification (axioms and terms)

**Target.** Encode ascomylactam A as a stereo-annotated molecular graph from the crystallographic structure. This graph, and the explicit set of bonds constituting the 13-membered perimeter, are the formal "goal."

**Building blocks 𝓑.** A curated, finite set of candidate acyclic precursors / fragments (the "arms" whose union forms the seco-macrocycle), parameterized so that diversification (objective i) corresponds to swapping decorated variants. CASP (Layer 2.6) proposes and decorates these.

**Rule library 𝓡 — disconnection schemas.** Each macrocyclization tactic of Section 2.2 is written once, as a _schema_ (a GML DPO rule, possibly with application conditions and stereo annotations), not per-molecule. Illustrative skeleton for a macrolactamization closure (GML is schematic — consult MØD docs for exact syntax and labels):

```
rule [
  ruleID "macrolactamization (amide ring closure, -H2O equiv.)"
  left  [  # carboxyl carbon ... amine nitrogen, pre-closure
     node [ id 1 label "C" ] node [ id 2 label "O" ]   # C=O / C-OH
     node [ id 3 label "N" ] node [ id 4 label "H" ]
     edge [ source 1 target 2 label "-" ]              # C-OH (activated form abstracted)
     edge [ source 3 target 4 label "-" ]
  ]
  context [ ]                                           # K: atoms preserved
  right [
     node [ id 1 label "C" ] node [ id 2 label "O" ]
     node [ id 3 label "N" ]
     edge [ source 1 target 3 label "-" ]              # new amide C-N
     edge [ source 1 target 2 label "=" ]              # C=O retained
  ]
  # application condition: atoms 1 and 3 lie on the same component AND
  # graph distance(1,3) places the new bond on a 13-membered cycle
]
```

The valence model and DPO interface make any rule application that would violate atom/charge/bond-order conservation simply _non-derivable_ — the analogue of a type error being rejected by the kernel before any "proof" proceeds. Stereo annotations are carried per [Andersen 2017].

### 3.2 Layer B — Generation (bounding the proof-search space)

Apply 𝓡 to 𝓑 under explicit MØD **strategies** to build the derivation graph / hypergraph of reachable disconnections, _without_ attempting exhaustive expansion. Strategies encode chemist priors as search control: restrict ring-closing rules to fire only when the induced cycle has the target size (13); cap intermolecular events; forbid chemically nonsensical contexts; bound derivation depth [Andersen 2014]. This is the engineering crux that keeps an in-principle-infinite space finite and relevant — the counterpart of choosing the right tactics and `simp` sets so a Lean goal is actually discharged.

### 3.3 Layer C — Constraint solving (the kernel)

Formulate pathway selection as an integer hyperflow problem on the generated hypergraph [Andersen 2019], extended with the thermodynamic-constraint machinery of [arXiv:2411.15900].

**Variables.** For each hyperedge (reaction) `e`, an integer multiplicity `f_e ≥ 0`. Source/sink terms inject building blocks and withdraw the target.

**Hard constraints.**

- _Flow conservation_ at every molecule vertex (mass balance across the whole route).
- _Goal_: net production of the target macrocycle = 1; consumption of designated building blocks bounded by availability.
- _Ring-closure_: the route must include exactly one firing of a rule in the macrocyclization class that creates the 13-membered cycle.
- _Step budget_: Σ f_e ≤ k.
- _Thermodynamic admissibility_ (optional, staged): each fired reaction, or the route net, satisfies a ΔG bound supplied by Layer D.

**Objective — pathway atom economy.** Distinguish two formalizations and report both:

- _Bond-level / net AE_: from the composed overall rule (Section 3.4), Trost atom economy of target vs the stoichiometric net inputs — the theoretical ceiling of the disconnection.
- _Process-level AE_: charges each fired reaction with the stoichiometric mass of its required reagents/activators (e.g., the coupling agent in lactamization), penalizing tactics that are atom-economical at the bond but not at the bench.

Maximizing AE is equivalent to minimizing expelled atomic mass, a linear objective in `f_e`.

**Outputs and certificates.**

- _Top-N enumeration_: the optimal and near-optimal routes (the solver's native capability [Andersen 2019]), i.e., the ranked shortlist.
- _Optimality certificate_: the solver's dual/bound proving the reported AE is maximal in the network.
- _Infeasibility certificate_: when "AE ≥ τ within k steps" has no solution, an irreducible infeasible subsystem / Farkas certificate — the formal **no-go result**. This is the highest-value output: it tells the chemist, with proof relative to 𝓡, that an entire class of clean closures does not exist, so effort should move elsewhere.

### 3.4 Layer C′ — Rule composition into a checkable proof object

For each shortlisted route, use MØD rule composition to collapse the derivation into a single coarse DPO rule whose atom-to-atom map traces every target atom back to a building-block atom [Andersen 2018]. This object (a) is independently re-checkable for conservation by a second, minimal verifier, giving a kernel-style trust reduction; (b) makes the net transformation and the true byproduct set explicit, which _is_ the net atom-economy statement; and (c) is human-legible as a one-glance summary of "what this route actually does."

### 3.5 Layer D — Energetic feasibility filter (the trusted-but-defeasible step)

For the small set of surviving ring-closing steps:

1. Generate conformers/embeddings of the seco-precursor and product (RDKit + a fast force field).
2. **MLIP screen** (MACE-OFF/AIMNet2 or an OMol25-trained model via ASE): relative energies and a TS guess via CI-NEB or FSM — used to _triage and rank_, never to decide [arXiv:2604.00405].
3. **DFT refinement** (ORCA/Psi4; GFN2-xTB as an intermediate tier) on the handful that survive triage, to obtain ΔG and a barrier estimate good enough to feed back as the thermodynamic constraint in Layer C.

The contract is explicit: numbers from this layer are advisory inputs to ranking and to the optional ΔG constraint; they never enter a _certified_ claim. Out-of-distribution MLIP error (Section 2.5) is the reason.

### 3.6 Layer E — Certificate and human handoff

Each shortlisted candidate is emitted as a structured record: the composed atom-mapped rule (the proof object); bond-level and process-level AE with the explicit byproduct set; ΔG/barrier estimates with their provenance and method tier; the strategy/rule trace that produced it; and a rendered scheme. The no-go certificates are emitted alongside. The report is explicitly framed as _input to the chemist's retrosynthetic judgment_ — the human chooses, defends, and executes.

---

## 4. Illustrative encoding sketch on ascomylactam A

This sketch shows the _shape_ of the analysis, not a proposed route — exact atom maps must come from the crystal structure (Section 2.1).

Three disconnection families are encoded as competing rule schemas across the 13-membered perimeter:

1. **Late macrolactamization** at the ring amide. Net byproduct ≈ H₂O → high bond-level AE; biosynthetically aligned. Process-level AE is docked by the activation reagent. Layer D asks whether the medium-ring amide closure is conformationally and energetically accessible.
2. **Transannular / intramolecular Diels–Alder** closing two of the perimeter C–C bonds with **zero byproduct** → maximal bond-level AE; biomimetic. Layer C would flag it as the AE-optimal class; Layer D must check the diene/dienophile geometry is reachable on the medium ring.
3. **RCM** across two alkene-terminated arms → byproduct ethylene; high AE; but Layer D/E weighs E/Z control and the downstream cost of correcting it.

The mechanization's job is to (a) confirm whether the Diels–Alder class is in fact AE-optimal and feasibility-passing (promoting it), (b) rank lactamization vs RCM on the _combined_ AE-plus-feasibility criterion rather than on intuition, and (c) if, say, every clean C–C closure fails the ΔG bound at 13-membered ring size, emit the corresponding infeasibility certificate so the team stops pursuing that family. A solver pseudo-call (MØD API names illustrative):

```python
import mod
# A. specification
target = mod.smiles("...ascomylactam-A-from-Xray...", name="target")
blocks = [mod.smiles(s) for s in building_block_library]
rules  = mod.ruleGMLString(open("macrolactamization.gml").read()), ...  # the schema library

# B. generation under strategy control (13-membered closure only, bounded depth)
dg = mod.DG(graphDatabase=blocks + [target])
dg.build().execute( mod.addUniverse(blocks)
                    >> mod.repeat[k]( mod.rightPredicate[ closes_13_ring ]( rules ) ) )

# C. integer-hyperflow ILP: maximize atom economy, close the ring, <= k steps
flow = mod.Flow(dg)              # hyperflow model over the derivation graph
flow.addSource(...); flow.addSink(target)
flow.addConstraint( ring_closure_in_macrocyclization_class == 1 )
flow.addConstraint( total_steps <= k )
flow.objective = maximize(atom_economy)   # = minimize expelled atomic mass
solutions = flow.solve(enumerate=N)       # top-N + optimality/infeasibility certificate
```

### 4.1 Validation before trusting any of this

Run the identical pipeline, unchanged, on a panel of _solved_ macrocyclic syntheses from [Acc. Chem. Res. 2021] / [ACS Cent. Sci. 2020] (RCM, macrolactamization, transannular cycloaddition cases). Acceptance: the literature's actual ring closure appears among the top-N AE-ranked, feasibility-passing candidates, and the pipeline does not certify a false no-go that contradicts a known route. Only after this retrodiction passes is the ascomylactam output trustworthy as decision support.

---

## 5. Implementation plan

**Stack.** MØD (C++/Python) for A–C and C′ [Andersen 2016]; an exact (M)ILP backend (SCIP open-source, or Gurobi/CPLEX) behind the hyperflow solver; RDKit for cheminformatics I/O and conformers; ASE as the driver for MLIPs (MACE-OFF/AIMNet2/OMol25-trained) and for CI-NEB/FSM; xtb (GFN2-xTB) and ORCA or Psi4 for QM refinement; optionally SCINE/Chemoton if autonomous PES exploration around the closure is wanted [Chemoton 2.0]. CASP via ASKCOS or AiZynthFinder (both open) for precursor decoration.

**Team roles.** (1) Graph-rewriting/formal-methods engineer: rule library, strategies, hyperflow/ILP formulation, certificate verifier. (2) Computational chemist: Layer D/E, MLIP/DFT protocol, ΔG/barrier feedback into Layer C. (3) Cheminformatics engineer: data model, building-block/CASP integration, provenance, reporting, orchestration. (4) Synthetic chemist (domain authority): target encoding from the crystal structure, rule-library chemical correctness, strategy priors, and final review — the human in "human-in-the-loop."

**Milestones.**

- **M1 (weeks 1–4):** target + building blocks encoded; first three disconnection schemas; conservation/typing re-checker. _Exit:_ a generated network for one disconnection family, visualized.
- **M2 (weeks 5–10):** hyperflow ILP with the atom-economy objective and ring-closure/step constraints; top-N enumeration and infeasibility certificates. _Exit:_ certified ranking on a toy macrocycle.
- **M3 (weeks 8–14):** Layer D/E — MLIP screen + DFT refinement + TS search; ΔG feedback into Layer C. _Exit:_ feasibility-annotated shortlist.
- **M4 (weeks 12–18):** retrodictive validation panel (Section 4.1). _Exit:_ documented recovery of known closures; calibrated thresholds.
- **M5 (weeks 16–22):** full ascomylactam A run; certificate/report generation; chemist review. _Exit:_ the ranked, certified option set and the no-go certificates.

**Compute.** Layers A–C are CPU/ILP-bound (a workstation suffices for v1; ILP hardness is the scaling risk). Layer D/E needs a modest GPU node for MLIPs and CPU for DFT refinement of the surviving handful.

---

## 6. Risks, limitations, and what is deliberately not claimed

- **Combinatorial explosion / ILP hardness.** The generated space is unbounded in principle and the pathway ILP is NP-hard [Andersen 2019]. _Mitigation:_ aggressive strategy control (Layer B), tight step budgets, and treating intractability itself as information (if it won't close under reasonable budgets, that is a finding). This is the honest analogue of a Lean goal that is true but not discharged within resource limits.
- **Rule-set completeness is a modeling assumption.** Certificates are sound _relative to_ 𝓡. A novel closure outside the library cannot be discovered or ruled in. _Mitigation:_ curate 𝓡 from the macrocyclization reviews; treat 𝓡 as versioned and auditable; state the relativization on every certificate. A no-go is "no clean closure _of these kinds_," never "no closure exists."
- **MLIP out-of-distribution error (> 5 kcal/mol on novel networks).** Hard-wired into the architecture by confining MLIPs to triage and mandating DFT refinement before any recommendation [Adv. Sci. 2025]. Even DFT barriers for medium-ring TSs carry real uncertainty; numbers are advisory.
- **Stereochemistry and conformation.** Medium-ring closures live or die on preorganization [Martí-Centelles, *Chem. Rev.* 2015]; stereo-aware rules [Andersen 2017] capture configuration but conformational feasibility is only as good as the sampling. _Mitigation:_ explicit conformer ensembles; flag low-confidence cases for the chemist.
- **"Atom-economical and feasible" ≠ "robust, selective, scalable."** The system says nothing about yield, selectivity in practice, protecting-group tax, or chromatography. These remain human and experimental.
- **Forward vs retrosynthetic framing.** The brief asks for a _forward_ route; the mechanization reasons over a disconnection network that is read forward (building blocks → target). The output is forward-executable strategies, but the ordering of non-cyclization steps is delegated to CASP + chemist.

**Net claim.** MØD-MacroCert mechanizes the part of the brief that is formally mechanizable — certified ranking of, and certified no-go results over, high-atom-economy ring-closing strategies — and rigorously quarantines the part that is not (bench feasibility) behind a clearly labelled, DFT-backed advisory layer. It augments the chemist's judgment in exactly the sense intended; it does not replace it, and it is engineered so that it cannot silently pretend to.

---

## 7. Positioning and novelty

MØD's hyperflow machinery has been used for metabolic, prebiotic, and combustion networks [Andersen 2019; arXiv:2411.15900], and CASP tools own precedented retrosynthesis [ASKCOS; AiZynthFinder; Synthia]. The novel combination proposed here is: (1) using DPO rule composition to manufacture an **atom-traced certificate** for a _target-oriented macrocyclization_; (2) making **atom economy the first-class (M)ILP objective** with a bond-level/process-level split; (3) treating **infeasibility certificates as primary deliverables** (formal no-go results that prune retrosynthetic effort); and (4) cleanly layering a **defeasible MLIP/DFT feasibility filter** beneath the certifying core, with the trust boundary drawn explicitly. Framed in the requester's terms, it is the synthesis-chemistry instantiation of the Lean workflow: specify, type-check by construction, search with certified optimality/infeasibility, and hand a small proven option set back to the human.

---

## References

Primary — graph transformation, MØD, hyperflows

- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _A Software Package for Chemically Inspired Graph Transformation._ ICGT 2016, 73–88. arXiv:1603.02481.
- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _An Intermediate Level of Abstraction for Computational Systems Chemistry._ Phil. Trans. R. Soc. A 375(2109):20160354, 2017. arXiv:1701.09097.
- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _Chemical Graph Transformation with Stereo-Information._ ICGT 2017, 54–69.
- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _Rule Composition in Graph Transformation Models of Chemical Reactions._ MATCH Commun. Math. Comput. Chem. 80(3):661–704, 2018.
- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _Generic Strategies for Chemical Space Exploration._ Int. J. Comput. Biol. Drug Des. 7(2/3):225–258, 2014. arXiv:1302.4006.
- Andersen, J. L.; Flamm, C.; Merkle, D.; Stadler, P. F. _Chemical Transformation Motifs — Modelling Pathways as Integer Hyperflows._ IEEE/ACM Trans. Comput. Biol. Bioinform. 16(2):510–523, 2019. arXiv:1712.02594.
- _Finding Thermodynamically Favorable Pathways in Chemical Reaction Networks using Flows in Hypergraphs and Mixed Integer Linear Programming._ arXiv:2411.15900, 2025.
- MØD software and documentation. Algorithmic Cheminformatics Group, SDU. https://cheminf.imada.sdu.dk/mod ; https://github.com/jakobandersen/mod

Primary/secondary — the target and its chemistry

- Chen, Y.; Liu, Z.; Huang, Y.; Liu, L.; He, J.; Wang, L.; Yuan, J.; She, Z. _Ascomylactams A–C, Cytotoxic 12- or 13-Membered-Ring Macrocyclic Alkaloids… and Structure Revisions of Phomapyrrolidones A and C._ J. Nat. Prod. 82(7):1752–1758, 2019. DOI:10.1021/acs.jnatprod.8b00918.
- _A Marine Alkaloid, Ascomylactam A, Suppresses Lung Tumorigenesis…_ Mar. Drugs 18(10):494, 2020.
- Skellam, E. _The biosynthesis of cytochalasans._ Nat. Prod. Rep. 34:1252–1263, 2017.
- Scherlach, K.; Boettger, D.; Remme, N.; Hertweck, C. _The chemistry and biology of cytochalasans._ Nat. Prod. Rep. 27:869–886, 2010.

Secondary — macrocyclization and atom economy

- Trost, B. M. _The Atom Economy—A Search for Synthetic Efficiency._ Science 254:1471–1477, 1991.
- Gradillas, A.; Pérez-Castells, J. _Macrocyclization by Ring-Closing Metathesis in the Total Synthesis of Natural Products._ Angew. Chem. Int. Ed. 45:6086–6101, 2006.
- Martí-Centelles, V.; et al. _Macrocyclization Reactions: The Importance of Conformational, Configurational, and Template-Induced Preorganization._ Chem. Rev., 2015 (DOI:10.1021/acs.chemrev.5b00056).
- _Stereoconfining Macrocyclizations in the Total Synthesis of Natural Products._ Nat. Prod. Rep., 2019 (DOI:10.1039/c8np00094h).
- _Lessons from Natural Product Total Synthesis: Macrocyclization and Postcyclization Strategies._ Acc. Chem. Res., 2021 (DOI:10.1021/acs.accounts.0c00759).
- _Unconventional Macrocyclizations in Natural Product Synthesis._ ACS Cent. Sci., 2020 (DOI:10.1021/acscentsci.0c00599).

Primary/secondary — energetics, MLIPs, network exploration

- Kovács, D. P.; et al. (Csányi group). _MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules._ J. Am. Chem. Soc., 2025 (DOI:10.1021/jacs.4c07099).
- Anstine, D.; Zubatyuk, R.; Isayev, O. _AIMNet2_ (second-generation atoms-in-molecules neural-network potential).
- _Reliable and Efficient Automated Transition-State Searches with Machine-Learned Interatomic Potentials._ arXiv:2604.00405, 2026.
- _Harnessing Machine Learning to Enhance Transition State Search with Interatomic Potentials and Generative Models._ Adv. Sci., 2025 (DOI:10.1002/advs.202506240).
- Unsleber, J. P.; et al. (Reiher group). _Chemoton 2.0: Autonomous Exploration of Chemical Reaction Networks._ J. Chem. Theory Comput., 2022 (DOI:10.1021/acs.jctc.2c00193).
- _Lifelong Machine Learning Potentials for Chemical Reaction Network Explorations._ J. Chem. Theory Comput., 2025 (DOI:10.1021/acs.jctc.5c01127).

Heuristic synthesis planning and formal methods

- Coley, C. W.; et al. ASKCOS (open-source CASP, MIT).
- Genheden, S.; et al. _AiZynthFinder._ J. Cheminform. 12:70, 2020 (AstraZeneca).
- Grzybowski, B. A.; et al. Chematica/Synthia.
- de Moura, L.; Ullrich, S. _The Lean 4 Theorem Prover and Programming Language._ CADE 2021.
- _Formalizing Chemical Physics using the Lean Theorem Prover._ arXiv:2210.12150, 2022.

---

_Scope note: claims labelled "certificate," "optimal," or "infeasible" are sound only relative to the encoded rule set 𝓡, building-block set 𝓑, and the generated network; energetic verdicts are statistical/defeasible and DFT-backed, not deductive. The structure of ascomylactam A and the precise atom membership of its 13-membered ring must be encoded from the deposited crystallographic data before any run._
