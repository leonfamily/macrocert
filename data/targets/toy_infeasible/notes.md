# Toy infeasibility target — provably empty under stated rules

Same physical target as `toy_macrolactam` (13-membered macrolactam from
12-aminododecanoic acid) but the RunSpec restricts the rule set to
**transannular_diels_alder only** — a rule that cannot fire on a
substrate with no diene or dienophile.

The pipeline should:
1. Generate a DG that contains no macrocyclization edges (the TDA rule
   matches no firings against an all-saturated aminocarboxylic-acid
   precursor).
2. Solve the hyperflow ILP, find no feasible flow satisfying
   exactly-one-macrocyclization.
3. Emit an *infeasibility certificate* — the proposal §3.3
   "highest-value output" telling the chemist that the entire TDA
   class is provably empty for this target/precursor pair.

This is the M2 exit criterion's "infeasibility certificate on a toy
macrocycle."
