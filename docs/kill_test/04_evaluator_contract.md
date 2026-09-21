# Evaluator contract v1.0.0

The canonical graph form is sorted node names plus an endpoint matrix with
causal-learn codes (`-1` tail, `1` arrow, `2` circle, `0` absent). Equality is
exact after canonical node ordering. Skeleton edges are unordered node pairs.

Adjacency TP/FP/FN are computed against the full-budget oracle-FCI reference.
Precision/recall/F1 use explicit zero-denominator conventions: precision=1 when
no predicted positives and no false positives, recall=1 when truth is empty,
and F1=0 when P+R=0. Endpoint tail/arrow metrics treat each ordered edge endpoint
as one item. A wrong determined endpoint is a predicted tail/arrow differing
from the reference; circles are unresolved, not false determined endpoints.
Ancestral and MAG/PAG-compatibility metrics remain disabled until OI-02 closes.

Budget-curve quality is skeleton F1. `tests_to_95` is the first logged step at
which the provisional evidence skeleton reaches at least 95% of final-baseline
F1; missing attainment is infinity and cannot count as a win. Bootstrap uses
paired graph-level differences, 10,000 resamples, frozen `bootstrap_seed`, and
the percentile 2.5/97.5 interval.

Gate evaluator reads machine-readable rows and validates matrix completeness,
required baselines, calibration, evaluator-test status, confidence intervals,
and evidence-file existence before numerical thresholds. Gate states are only
PASS, FAIL, BLOCKED, or NOT_RUN. Smoke rows have `scope=smoke` and are prohibited
from PASS evidence.

