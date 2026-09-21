# Scientific contract v1.0.0

Frozen: 2026-09-19, before main experiment results.

## Hypotheses and baselines

H0-H4 and K0-K4 follow `02a_safe_imperfect_priors_kill_test_vi.md` exactly.
Mandatory prior-free schedules are `stable_default`, `random_valid`,
`cost_only`, and `graph_only`; `oracle_query` is a diagnostic upper bound;
`noisy_query_oracle` and `separator_membership_prior` are prior-guided;
`hard_prior` is a labeled negative control. FCI-stable is primary. RFCI-stable
and FCIT are required before claims against those methods, and currently OPEN.

## Matrix

- Phase 0: 20 small oracle-DAG instances, baseline plus 10 random schedules.
- Phase 1: observed p={10,20}, latent ratio={0.2,0.4}, mean degree={2,4},
  20 graph seeds/cell (160 graphs), oracle CI.
- Phase 2: Phase-1 graphs, target AUC={0.55,0.65,0.75,0.425}, independent,
  node-correlated, and motif-correlated errors.
- Phase 3: p=20, latent ratio=0.3, degree=2.5, linear Gaussian,
  n={500,2000}, 30 graph seeds, 3 data seeds/graph (180 data sets).

## Priors and calibration

Positive query means an eligible query whose oracle CI is independent and hence
provides separating evidence; negative means dependent. AUC is computed within
graph and scheduling phase over eligible scored queries, then macro-averaged by
graph; cells without both classes are reported and excluded from AUC, never
imputed. Target tolerance is +/-0.02.

Prior A scores the positive-query label plus calibrated noise and is diagnostic
only. Prior B claims whether `z` belongs to at least one inclusion-minimal
observed separator for `(i,j)`. A fixed query score is the mean claim score over
`Z`, minus `0.05*|Z|`; the empty set receives zero claim contribution. It is not
fit on test graphs. Independent errors perturb claims independently. Node errors
share a blind-node offset; motif errors share offsets in predeclared chain,
fork, collider, and latent-confounding regions. Comparisons require same graph,
claim count, positive rate, and realized AUC within 0.02; otherwise correlation
effects are not attributed.

## Budgets and metrics

Each graph is normalized to its own full-budget `stable_default` run. Checkpoints
are 10%, 25%, 50%, and 100% of weighted cost, where each query costs
`(|Z|+2)^3`. A query that would exceed the cap is not run. The stop state is a
`DiscoveryState` containing graph, complete query history, untested candidates/
regions, and raw/weighted budget use.

Primary Phase-1 metric is raw CI calls to reach 95% of the full baseline
skeleton quality. Primary Phase-2/3 efficiency and safety metrics are those in
the attached contract. Secondary metrics include cost by |Z|, weighted cost,
first separator cost, wall time, peak memory, quality-budget AUC, adjacency and
endpoint metrics, circles, ranking AUC, oracle savings, recovered savings, and
paired regret. Pair/bootstrap unit is graph seed (graph/data seed in Phase 3),
never an edge.

## Gates and stops

K0 requires 100% equivalence across the complete Phase-0 matrix and all listed
provenance/eligibility/replay invariants. K1 requires >=20% median saving, 95%
bootstrap lower bound >10%, in >=3/4 p-by-latent groups. K2 requires Prior B at
realized AUC 0.65 to recover >=30% oracle savings, save >=8% vs best prior-free,
positive 95% lower bound, in >=3/4 groups. K3 and K4 use the exact robustness and
0.1 endpoint/graph rules in the source contract. Failure invokes its prescribed
NO-GO; later phases are not run after K1 failure.

Before results, only bug fixes, performance-preserving refactors, and explicitly
missing provenance fields may change. Any threshold, primary metric, prior map,
generator, or evaluator change requires a new version, reason, and separately
labeled old/new results.

