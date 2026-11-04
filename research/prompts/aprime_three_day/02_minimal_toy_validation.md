# DAY 2 — Minimal Mechanism Validation and Falsification of A′

## Role and entry conditions
Act as an independent computational statistician and adversarial experimental reviewer. Your task is **to test algebraic/numerical claims and expose failure modes**, not to prove that A′ improves causal discovery. Treat all predicted gains as hypotheses.

**First read Day 1's `A1_mathematical_contract_v2.md`, especially its authorization.** If it says `STOP-AND-REFORMULATE`, do not implement the original scoring method; instead construct the smallest numerical counterexample illustrating the blocker and record `BLOCKED`. If Day 1 has unresolved definitions, run only clearly valid subtests and explicitly label their limited scope. Do not quietly override the gate.

## Inputs and controls
Read the original A′ derivation P1–P7, the current experiment plan, and Day 1's corrections. Freeze a small, explicit, versioned mathematical specification for this toy test only: statistic vector z, covariance Σ, model-pattern regions, score, and pseudoinverse/support convention. Record every change from the original proposal. Use reproducible Python with NumPy/SciPy or equivalent libraries already available; no large solver, exhaustive MAG enumeration or SOTA benchmark unless a particular minimal correctness check absolutely requires one.

## Experiment A — Deterministic algebra sanity
For K=2, examine joint Gaussian statistics with covariance `[[1,r],[r,1]]` at r∈{0,0.3,0.6,0.9}, with both positive and negative correlation controls as relevant. Compare the diagonal squared loss and full-covariance squared loss **at exactly the same observed z**, e.g. z=(2,1.8); derive values independently and compare numerical calculations to the analytical formula. State explicitly that fixed-z variation is a *mathematical illustration*, not sampled causal data or evidence for better calibration.

Test:
1. r=0: exact diagonal agreement under matched weights and region definitions.
2. r≠0: verify or falsify P4 nonseparability under its stated inactive constraints; explicitly inspect the active-boundary case rather than assuming the same formula applies.
3. Change the sign of r and/or z to test whether the alleged effect is merely caused by a chosen favorable example.
4. Near singularity r→±1: numerical conditioning, limiting behavior and whether a valid limit exists for each selected z.
5. Exact duplicate query: build the duplicated statistic and covariance; check the specified pseudoinverse **with support restrictions**; compare scores before/after duplicate. Compare to naive additive loss and an elementary dedup control so duplicate invariance is not presented as automatically novel.
6. Verify expected behavior and formula reductions by symbolic reasoning or independently computed reference values, not only by testing the implementation against itself.

## Experiment B — Sampling-based properties (still toy, not causal validation)
Draw independent Monte Carlo replicates (not one hand-picked sample) under clearly specified joint Gaussian null and alternative means. Vary correlations, query redundancy and mean configurations; report sampling uncertainty and random seeds. Separate exploratory tuning from evaluation. Compare only mathematically equivalent targets:
- diagonal ACI-type weighted objective defined by Day 1;
- a diagonal-reweighted control;
- a valid full-covariance objective if defined;
- optional sample-splitting or oracle-covariance controls to isolate covariance-estimation effects.

Measure, as meaningful for the toy statistical model: empirical distribution of scores, false assertion rate **under an explicitly defined decision threshold**, ranking changes, threshold-transfer sensitivity, and sensitivity to covariance estimation. Do not call empirical stability “calibration” or claim nominal 95% coverage without a valid procedure. If a statistic cannot be mapped to a defensible threshold, report descriptive distributions and do not invent a guarantee.

## Experiment C — Estimation, dimensionality, and model relevance
Investigate covariance estimated from finite samples versus oracle Σ, with multiple n and K where cheap. Include K larger than the dimension of the underlying Gaussian covariance parameterization when testing shared-data Fisher-z. Check effective rank, condition numbers, shrinkage/pseudoinverse effects and estimated versus true score discrepancy.

If feasible **without building a large new pipeline**, construct one tiny realizable causal graph/SCM and two real CI queries whose statistics share observations. Confirm that an illustrative CI pattern or P4 contrast can arise from a valid graph. If not feasible, keep the experiment explicitly abstract; do not present arbitrary patterns as MAG-realizable.

Evaluate whether adding an apparently “redundant” conditioning set preserves the CI fact in the specific graph. Never assume CI is monotone in conditioning. Distinguish a byte-identical duplicate from correlated but logically distinct evidence.

## Critical checks and falsification
For each experiment, declare in advance:
- the precise statement under test;
- independent input and null/alternative definitions;
- what observation supports it;
- a counterexample or observation that refutes it;
- which conclusions remain untested;
- whether any result is tautological given how the toy was constructed.

Prioritize *correctness and mechanism visibility* over effect-size maximization. Report all regimes, including where full covariance worsens performance. Do not “fix” data/assumptions retrospectively to force a positive outcome. Do not use the toy result to claim improvement over ACI/BSC-D/FCI in real causal discovery.

## Reproducibility
Produce `A1_toy_mechanism_validation.ipynb` (or a reproducible `.py` script if notebooks are unavailable) and `A1_toy_results.md`. Save versions, package dependencies, seeds, full numerical tables, figures only where useful, warnings/failures and explicit test assertions. Figures must identify axes, null/alternative and whether covariance is oracle or estimated. Unit tests should reflect the **corrected** Day 1 mathematics, not erroneous original expectations.

## Decision
Provide one of:
- **MECHANISM VALIDATED (TOY ONLY):** stated identities hold and nontrivial toy behavior is visible;
- **MIXED / REFORMULATION NEEDED:** some identities or regimes fail;
- **BLOCKED / INVALID:** prerequisites fail or results contradict the formulation.

Do not approve a full pilot. List the *minimum* new evidence required from causal SCMs and the closest baselines before any research novelty claim.

**Response language: Vietnamese with English technical terminology. Never fabricate execution, timings, plots or scientific conclusions.**
