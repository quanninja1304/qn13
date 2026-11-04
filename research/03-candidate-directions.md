# 03 — Initial Candidate Research Areas (NOT confirmed gaps)

A/B are initially prioritized for exploration because failure modes and evaluation may be testable early. Reorder or reject them whenever literature and empirical evidence justify it. Do not assume the suggested mechanisms below are new.

## A. Robust Causal Discovery under Unreliable CI Evidence — initial priority: high

**Problem.** CI tests can become unreliable with small n, large conditioning sets, weak dependence, high dimensionality, measurement noise or model misspecification. Erroneous decisions can propagate through skeleton and orientation, especially with latent confounding.

**Research question.** How can CI evidence and structural constraints be integrated so that causal discovery remains reliable when CI tests are uncertain, including settings with latent confounders?

**Possible mechanisms to investigate:** reliability-aware aggregation, confidence-aware graph reasoning, evidence reconciliation, selective orientation/abstention, coherent uncertainty propagation. These are *idea families*, not novelty claims.

**Critical gap audit:** compare dcFCI, conservative/bootstrapped FCI, RFCI, differentiable constraint-based discovery, Bayesian/uncertainty-aware causal discovery and CI calibration approaches. Ask whether existing approaches already handle noisy evidence, confidence propagation, contradictory CI facts or conservative uncertainty reporting.

**Required contribution:** a concrete new mechanism grounded in a verified failure, not merely weighting p-values or voting over bootstrap graphs.

**Evaluation:** n, conditioning dimension, graph degree, dependence strength, latent fraction, CI false positives/negatives, measurement noise/test misspecification. Match appropriate strong baselines. Measure PAG/skeleton/endpoint errors, stability, uncertainty quality/calibration if claimed, and computational cost.

## B. Budget-Aware and Anytime Causal Discovery — initial priority: high

**Problem.** CI queries and graph operations can be expensive. Ordering, truncation and cutoffs can alter the explored hypotheses; early output may disguise search uncertainty as causal certainty.

**Research question.** Can a method allocate limited budget toward the most valuable CI queries or structural hypotheses while maintaining useful, properly qualified causal conclusions at interruption time?

**Possible mechanisms:** adaptive query selection, information-value or uncertainty-guided graph search, cost-aware inference, budget-aware stopping, partial-result abstention or uncertainty reporting. Active learning and query ordering already exist; identify a *new principle* rather than rebranding them.

**Critical gap audit:** active causal discovery, adaptive CI testing, budgeted inference, anytime discovery, search uncertainty, family-dependent scoring. Separate statistical test cost from graph-oracle and scoring cost.

**Required contribution:** a defensible acquisition/search policy or uncertainty mechanism, with a clear reason it can beat cheap heuristics; characterize when it helps and when it cannot.

**Evaluation:** budget-matched accuracy-versus-budget, CI execution counts and cost, runtime/CPU/RSS, feature/PAG quality, confidence under early stopping, reliability across orderings, sensitivity to hard cutoffs. Task definitions must remain matched.

## C. Robust Causal Discovery under Data Heterogeneity — initial priority: medium

**Problem.** Data from different environments/populations may have covariate shift, mechanism changes, measurement differences, selection effects and unobserved confounding. Pooling may create misleading dependencies or conceal invariant structure.

**Research question.** Can cross-environment agreement and variation be exploited to learn more reliable causal structures under heterogeneity and latent confounding?

**Possible mechanisms:** environment-aware CI tests, invariant evidence, reliability-weighted cross-environment reasoning, shared-versus-specific graph structure, uncertainty-aware aggregation.

**Critical gap audit:** invariant causal prediction/discovery, multi-environment structure learning, distribution shift, heterogeneous causal discovery, selection effects and latent-confounder assumptions. “Multi-environment FCI” alone is not a novelty claim.

**Required contribution:** a novel mechanism resolving a specific heterogeneity-related failure, with assumptions and counterexamples when invariance is violated.

**Evaluation:** environment count/sample allocation, shifts and mechanism interventions, graph topology, latent confounding, invariance violations, domain transfer and natural multi-environment datasets. Report accuracy, stability and failure boundaries.

## Alternatives

The shortlist can include directions outside A/B/C. Each must meet the same significance, gap, insight, mechanism and validation standards. Do not expand abstract theory simply because it sounds more prestigious. Distinguish **search topics** from **validated research problems** at all times.
