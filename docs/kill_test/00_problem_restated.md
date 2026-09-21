# Problem restatement

## Inputs and truth

The input is an observed variable set, a full DAG containing observed and
latent variables (simulation only), a CI backend, a frozen experiment config,
and optionally a materialized prior. Oracle CI asks `Xi independent Xj | Z` by
d-separation in the **full DAG**; `Z` contains observed variables only. The full
DAG is simulation truth. For evaluation, the canonical full-budget oracle FCI
result is the operational PAG reference; this is deliberately called a
reference rather than an independently verified DAG-to-PAG conversion.

FCI returns a PAG only after the complete algorithm finishes. A budget-stopped
run returns `DiscoveryState(P, T, U, B)`, not a PAG: current graph state, executed
queries, unexecuted/closed regions, and consumed budget.

## Boundary of the prior

The prior may rank currently eligible `(i,j,Z)` queries or allocate budget. It
may not answer CI, add/remove an edge, orient an endpoint, alter an FCI rule, see
unqueried CI outcomes, or serve as evaluator truth. Except for the explicitly
named `oracle_query` diagnostic, schedulers receive no DAG/PAG truth.

`oracle_query` directly sees CI usefulness and is only an upper bound. A usable
prior is the noisy separator-membership interface: claims about whether `z`
belongs to a minimal separator are materialized using truth, corrupted, and only
then exposed as scores.

## Falsification targets

- K0/H0: any unexplained full-budget oracle mismatch, ineligible selection,
  dependency violation, prior-authored graph decision, or replay mismatch kills
  mechanical validity.
- K1/H1: no oracle headroom meeting the frozen 20%/10%-lower-bound/3-of-4 rule
  yields NO-GO.
- K2/H2: failure of Prior B at realized AUC 0.65 to recover 30% of oracle saving,
  improve 8%, and have positive paired bootstrap lower bound yields
  NO-GO_FOR_CURRENT_PRIOR_INTERFACE.
- K3/H3-H4: disappearance against strong prior-free baselines or loss of over
  half the benefit under AUC-matched correlated errors yields NO-GO_OR_REFRAME.
- K4: excessive finite-sample endpoint harm, loss at either sample size, or loss
  against stable/graph-only baselines yields NO-GO.

No smoke result can pass a gate. Missing matrix cells, an unverified evaluator,
or absent required baselines produce BLOCKED/NOT_RUN rather than optimism.

