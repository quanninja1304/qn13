# 06 — Experimental Evaluation, Benchmarks & Robustness

## Design first

Every candidate proposal needs an evaluation protocol **before** framework implementation. Experiments should test the scientific mechanism, not maximize the number of datasets or metrics.

## Three evidence layers

| Layer | Purpose | Ground-truth warning |
|---|---|---|
| Controlled synthetic / semi-synthetic | Control mechanisms and graph truth, vary one assumption at a time | Use independently validated causal graph generation and latent projection when appropriate |
| Established public benchmarks | Comparable SOTA evidence using agreed tasks, protocols and metrics | Verify actual benchmark assumptions and output object |
| Real-world datasets | Practical relevance, stability, plausibility, transfer | Do not claim graph-recovery accuracy where causal ground truth is unknown; differentiate expert graph from verified truth |

An “official” benchmark is not automatically suitable for the new scientific question. Name and verify concrete datasets and how labels/ground truth are justified.

## Baseline standard

Identify **at least three relevant baseline approaches where applicable**:

1. Standard reference baseline for the problem.
2. Closest/strongest direct published competitor.
3. Simple but competent alternative, heuristic, or matched ablation.

Add more where a relevant SOTA family would otherwise be omitted. Compare **the same scientific task**: matching assumptions, graph representation, sample splits, CI test, compute budget, cache/preprocessing, stopping/caps and evaluation rules. Reproduce exact paper hyperparameter protocol when feasible and disclose differences.

## Primary metrics by claim

- **Graph accuracy:** skeleton precision/recall/F1, orientation metrics, PAG-specific endpoint error; define SHD convention rather than mix incompatible definitions.
- **Causal uncertainty:** coverage, uncertainty quality, calibration, abstention accuracy and set size where justified.
- **Efficiency:** actual CI executions and cost, graph-oracle calls, wall time, CPU, peak RSS (including workers), timeouts/OOM; accuracy–budget curves for anytime algorithms.
- **Robustness:** average, distribution, lower-tail/worst-group when appropriate, paired confidence intervals and seed variance.
- **Scientific validity:** relevant causal features and interventions where supported; never select the best predicted graph using truth and report that as normal inference.

## Controlled perturbations

Select those motivated by the failure hypothesis: sample size, graph size/degree/topology, latent fraction, conditioning dimension, dependence strength, noise, measurement error, CI misspecification, heterogeneity, distribution shift, environment count, computational budget, stopping order. Specify **why** each factor matters.

Plan cases favorable, neutral and adversarial to the proposed mechanism. Avoid evaluating robustness only as “number of datasets with a win.”

## Ablations and controls

- Remove/replace **the central new mechanism**.
- Compare stronger simple variants (e.g., thresholding, bootstrap voting, random/adaptive query ordering, memoization).
- Isolate whether gains come from extra compute, changed stopping conditions, data leakage, oracle access or dataset tuning.
- Analyze both wins and regressions; show when/why the model fails.
- Use multiple matched seeds/graphs and confidence intervals where feasible; avoid treating thousands of correlated candidate graphs as independent datasets.

## Reproducibility contract

Record version/commit, package/environment versions, graph generators and seeds, raw datasets and preprocessing, model/test settings, hardware, budget, cache, timeout/OOM, exact output schema and evaluation scripts. Clearly separate pilot from confirmatory test sets to limit tuning to the benchmark.

## Scientific goal

Don't merely conclude “SOTA improves by N%.” Establish **which failure is mitigated, which new mechanism causes that mitigation, under what assumptions, at what cost, and in which cases it does not help**.
