from __future__ import annotations

from pathlib import Path

import numpy as np

from .metrics import bootstrap_median_ci


VALID = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}


def gate_record(gate: str, status: str, reason: str, evidence_files=None, metrics=None, thresholds=None, blockers=None) -> dict:
    if status not in VALID:
        raise ValueError(f"invalid gate status {status}")
    return {
        "gate": gate,
        "status": status,
        "contract_version": "1.0.0",
        "evidence_files": list(evidence_files or []),
        "metrics": dict(metrics or {}),
        "thresholds": dict(thresholds or {}),
        "reason": reason,
        "blocking_dependencies": list(blockers or []),
    }


def evaluate_k0(rows: list[dict], expected_graphs: int = 20, schedules_per_graph: int = 10) -> dict:
    main = [row for row in rows if row.get("scope") == "main" and row.get("phase") == 0]
    expected = expected_graphs * (1 + schedules_per_graph)
    evidence = sorted({path for row in main for path in (row.get("query_log", ""), row.get("event_log", "")) if path})
    if len(main) != expected:
        return gate_record("K0", "BLOCKED", "Phase-0 matrix is incomplete", evidence, {"expected_runs": expected, "completed_runs": len(main)}, {"equivalence_rate": 1.0}, ["complete_phase0_matrix"])
    failures = [row for row in main if not all([row.get("matches_stable"), row.get("matches_upstream"), row.get("query_set_matches_stable"), row.get("scheduler_eligible"), row.get("dependencies_respected"), row.get("prior_not_graph_evidence"), row.get("deterministic_replay")])]
    missing = [path for path in evidence if not Path(path).exists()]
    if missing:
        return gate_record("K0", "BLOCKED", "Evidence files are missing", evidence, {"missing_evidence": len(missing)}, {"equivalence_rate": 1.0}, ["restore_raw_artifacts"])
    status = "PASS" if not failures else "FAIL"
    return gate_record("K0", status, "All Phase-0 invariants hold" if status == "PASS" else "At least one Phase-0 invariant failed", evidence, {"expected_runs": expected, "completed_runs": len(main), "failed_runs": len(failures), "equivalence_rate": (expected - len(failures)) / expected}, {"equivalence_rate": 1.0})


def evaluate_k1(rows: list[dict], bootstrap_seed: int = 51001, resamples: int = 10_000) -> dict:
    phase = [row for row in rows if row.get("scope") == "main" and row.get("phase") == 1]
    expected = 160 * 5
    if len(phase) != expected:
        return gate_record("K1", "NOT_RUN" if not phase else "BLOCKED", "Full Phase-1 matrix is incomplete", metrics={"expected_runs": expected, "completed_runs": len(phase)}, thresholds={"median_saving": 0.20, "bootstrap_lower": 0.10, "groups": 3}, blockers=["complete_phase1_matrix"])
    by_key = {(r["graph_digest"], r["scheduler"]): r for r in phase}
    reductions = []
    grouped: dict[tuple, list[float]] = {}
    missing = 0
    for row in phase:
        if row["scheduler"] != "oracle_query":
            continue
        baseline = by_key.get((row["graph_digest"], "stable_default"))
        b, o = baseline.get("tests_to_95") if baseline else None, row.get("tests_to_95")
        if not b or o is None:
            missing += 1
            continue
        reduction = (b - o) / b
        reductions.append(reduction)
        grouped.setdefault((row["observed_nodes"], row["latent_ratio"]), []).append(reduction)
    if missing or len(reductions) != 160:
        return gate_record("K1", "BLOCKED", "Primary metric was unattained or missing for one or more paired graphs", metrics={"valid_pairs": len(reductions), "missing_pairs": missing}, thresholds={"valid_pairs": 160}, blockers=["complete_tests_to_95"])
    median = float(np.median(reductions))
    lower, upper = bootstrap_median_ci(reductions, bootstrap_seed, resamples)
    group_metrics = {}
    groups_passed = 0
    for index, (group, values) in enumerate(sorted(grouped.items())):
        gl, gu = bootstrap_median_ci(values, bootstrap_seed + index + 1, resamples)
        gm = float(np.median(values))
        passed = gm >= 0.20 and gl > 0.10
        groups_passed += int(passed)
        group_metrics[f"p{group[0]}_latent{group[1]}"] = {"median": gm, "ci95": [gl, gu], "pass": passed}
    status = "PASS" if median >= 0.20 and lower > 0.10 and groups_passed >= 3 else "FAIL"
    evidence = sorted({row["query_log"] for row in phase if row.get("query_log")})
    return gate_record("K1", status, "Oracle headroom meets frozen thresholds" if status == "PASS" else "Oracle headroom fails at least one frozen threshold", evidence, {"median_saving": median, "bootstrap_ci95": [lower, upper], "groups_passed": groups_passed, "groups": group_metrics}, {"median_saving": 0.20, "bootstrap_lower": 0.10, "groups": 3})
