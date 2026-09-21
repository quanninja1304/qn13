# Open issues and conflict log

| ID | Status | Issue and consequence |
|---|---|---|
| OI-01 | OPEN | No RFCI-stable backend is present. FCI-stable is the implemented primary baseline; K4 and any claim covering RFCI are blocked until RFCI is added. |
| OI-02 | OPEN | No independently verified DAG-with-latents to MAG/PAG converter is available. Oracle FCI is the operational reference. PAG compatibility and ancestral metrics cannot support a gate until cross-validated. |
| OI-03 | OPEN | FCIT/targeted-testing code has not been reproduced. Literature threat remains OPEN; no strong-baseline superiority claim is allowed. |
| OI-04 | OPEN | Scheduler intervention currently covers stable FAS depth batches. Possible-D-SEP calls are provenance-logged but follow upstream order. Phase-1 headroom is therefore a lower/partial characterization of the full scheduling idea. |
| OI-05 | RESOLVED | Deep-dive text calls budgeted `P` a PAG, while the direct prompt forbids this if incomplete. Direct prompt wins: budgeted output is `DiscoveryState`; only completed FCI output is `PAGResult`. |
| OI-06 | RESOLVED | Broad document suggests FCI/RFCI and many baselines; kill-test contract makes FCI-stable/RFCI-stable primary. With RFCI unavailable, FCI-stable is implemented and absence is explicit rather than silently substituting vanilla FCI. |
| OI-07 | OPEN | causal-learn FAS records unions of all separating sets at a depth. The adapter preserves this behavior for equivalence; a minimal-separator-only policy would change orientation evidence and requires a new contract version. |
| OI-08 | OPEN | Phase-3 safety margin 0.1 endpoint/graph is frozen as requested but not yet empirically validated for scale. It cannot be changed after main results without a new contract version. |
| OI-09 | OPEN | The required `hard_prior` negative control and end-to-end Phase-2/3 runners are not implemented because K1 is NOT_RUN. Their absence is a blocker, not an implicit baseline win. |
| OI-10 | OPEN | Peak-memory is not measured per run; only environment RAM is captured. Wall time, raw CI count, cost by query, and weighted cost are available. |
| OI-11 | RESOLVED | Phase-1 run `p1-main-g141-random_valid` hit two post-discovery `MemoryError`s while instrumentation deep-copied hundreds of thousands of query records into `PAGResult` and later into an aggregate-metrics list. Both full-list copies were removed; metrics and JSONL are now computed/written by streaming the authoritative records. Scheduler, generator, seeds, query order, graph output, metric definitions, config digest, and thresholds are unchanged; the failed logical run is retried with its original IDs/seeds. |
| OI-12 | RESOLVED | The first 628 Phase-1 rows stored absolute Windows artifact paths. A deterministic project-root remapping layer now preserves the complete relative path under the current checkout; it does not search by basename and does not rewrite completed rows. New rows store project-relative references. Completion-audit aggregation also streams query JSONL instead of loading GB-scale logs into memory. This is a portability/instrumentation change only. |
