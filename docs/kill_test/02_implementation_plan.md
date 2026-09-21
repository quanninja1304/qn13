# Implementation plan

1. Freeze scientific and evaluator contracts before observing main results.
2. Test the evaluator and full-DAG d-separation oracle on hand-built motifs.
3. Generate deterministic full DAGs with observed nodes indexed before latent
   nodes. Persist graph parameters and canonical digests.
4. Retain causal-learn's FCI orientation and Possible-D-SEP code; replace only
   stable FAS query enumeration with a dependency-aware scheduler. Characterize
   default output against upstream.
5. Log every CI call and every edge/orientation delta. Ordinary scheduler views
   contain candidates, a truth-free state, history, materialized prior, costs,
   and scheduler seed only.
6. Run Phase 0 (20 graphs x baseline + 10 random schedules), retain failures,
   then compute K0 solely from raw artifacts.
7. If and only if K0 passes, dry-run and execute Phase 1. Phase 2/3 remain
   NOT_RUN unless K1 passes and compute/logging requirements are met.

The initial scheduling intervention is the nontrivial permutation of all FAS
queries eligible at a frozen conditioning-depth barrier. Edge commits remain at
the barrier, preserving stable semantics. Upstream Possible-D-SEP and orientation
rules remain unchanged and are logged but not yet reorderable.

