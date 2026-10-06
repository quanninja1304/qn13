from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import scipy

from ..ci import CIResult, GaussianCI
from ..ci_batch import GaussianBatchCI
from ..graphs import digest_object
from ..models import CIQuery
from .schemas import (
    ARTIFACT_SCHEMA_VERSION,
    algorithm_logical_key,
    validate_algorithm_run_record,
    validate_unique_logical_keys,
)


@dataclass(frozen=True)
class BatchAuditMismatch:
    query_id: str
    kind: str
    scalar: dict
    batch: dict


@dataclass(frozen=True)
class BatchAuditSummary:
    contract_version: str
    reference_id: str
    reference_mode: str
    equality_target: str
    backend: str
    batching_strategy: str
    query_count: int
    independent_count: int
    decision_mismatches_outside_margin: int
    decision_mismatches_within_margin: int
    numerical_status_mismatches: int
    max_effect_error: float
    max_statistic_error: float
    max_p_value_error: float
    effect_tolerance: float
    statistic_tolerance: float
    p_value_tolerance: float
    numerical_margin: float
    peak_workspace_bytes: int
    observed_peak_rss_mb: float
    memory_budget_bytes: int
    ci_arithmetic_work: int
    status: str
    mismatches: tuple[BatchAuditMismatch, ...]


def _result_payload(result: CIResult) -> dict:
    return {
        "independent": result.independent,
        "p_value": result.p_value,
        "statistic": result.statistic,
        "effect": result.effect,
        "numerical_status": result.numerical_status,
        "decision_margin": result.decision_margin,
    }


def _error(left: float | None, right: float | None) -> float:
    if left is None and right is None:
        return 0.0
    if left is None or right is None:
        return float("inf")
    return abs(float(left) - float(right))


def audit_scalar_batch(
    data: np.ndarray,
    queries: Sequence[CIQuery],
    *,
    alpha: float = 0.05,
    batching_strategy: str = "exact_size",
    memory_budget_bytes: int = 64 * 1024 * 1024,
    numerical_margin: float = 1e-10,
    effect_tolerance: float = 1e-11,
    statistic_tolerance: float = 1e-10,
    p_value_tolerance: float = 1e-11,
) -> BatchAuditSummary:
    scalar = GaussianCI(data, alpha=alpha)
    batch = GaussianBatchCI(
        data,
        alpha=alpha,
        batching_strategy=batching_strategy,
        memory_budget_bytes=memory_budget_bytes,
    )
    scalar_results = [
        scalar.test(query.x, query.y, query.conditioning_set) for query in queries
    ]
    batch_results = batch.test_many(queries)

    outside = within = status_mismatches = 0
    effect_error = statistic_error = p_error = 0.0
    mismatches: list[BatchAuditMismatch] = []
    for query, expected, actual in zip(queries, scalar_results, batch_results, strict=True):
        local_kinds: list[str] = []
        if expected.numerical_status != actual.numerical_status:
            status_mismatches += 1
            local_kinds.append("numerical_status")
        if expected.independent != actual.independent:
            margins = [
                abs(value)
                for value in (expected.decision_margin, actual.decision_margin)
                if value is not None
            ]
            if margins and min(margins) <= numerical_margin:
                within += 1
                local_kinds.append("decision_within_margin")
            else:
                outside += 1
                local_kinds.append("decision_outside_margin")
        current_effect = _error(expected.effect, actual.effect)
        current_statistic = _error(expected.statistic, actual.statistic)
        current_p = _error(expected.p_value, actual.p_value)
        effect_error = max(effect_error, current_effect)
        statistic_error = max(statistic_error, current_statistic)
        p_error = max(p_error, current_p)
        if current_effect > effect_tolerance:
            local_kinds.append("effect_tolerance")
        if current_statistic > statistic_tolerance:
            local_kinds.append("statistic_tolerance")
        if current_p > p_value_tolerance:
            local_kinds.append("p_value_tolerance")
        if local_kinds:
            mismatches.append(
                BatchAuditMismatch(
                    query.query_id,
                    ",".join(local_kinds),
                    _result_payload(expected),
                    _result_payload(actual),
                )
            )

    passed = (
        outside == 0
        and status_mismatches == 0
        and effect_error <= effect_tolerance
        and statistic_error <= statistic_tolerance
        and p_error <= p_value_tolerance
        and batch.last_diagnostics.peak_workspace_bytes <= memory_budget_bytes
        and batch.last_diagnostics.query_count == len(queries)
        and batch.last_diagnostics.ci_arithmetic_work
        == sum(query.local_size**3 for query in queries)
    )
    return BatchAuditSummary(
        ARTIFACT_SCHEMA_VERSION,
        "GaussianCI.scalar.strict",
        "tensor_backend",
        "ci_result",
        batch.backend,
        batching_strategy,
        len(queries),
        sum(result.independent is True for result in batch_results),
        outside,
        within,
        status_mismatches,
        effect_error,
        statistic_error,
        p_error,
        effect_tolerance,
        statistic_tolerance,
        p_value_tolerance,
        numerical_margin,
        batch.last_diagnostics.peak_workspace_bytes,
        batch.last_diagnostics.observed_peak_rss_bytes / (1024 * 1024),
        memory_budget_bytes,
        batch.last_diagnostics.ci_arithmetic_work,
        "PASS" if passed else "FAIL",
        tuple(mismatches),
    )


def batch_audit_run_record(
    summary: BatchAuditSummary,
    *,
    run_id: str,
    data_seed: int,
    config_digest: str,
    git_revision: str,
    dependency_lock: str,
) -> dict:
    record = {
        "contract_version": ARTIFACT_SCHEMA_VERSION,
        "run_id": run_id,
        "logical_key": "",
        "graph_seed": None,
        "data_seed": data_seed,
        "prior_seed": None,
        "scheduler_seed": None,
        "git_revision": git_revision,
        "config_digest": config_digest,
        "dependency_lock": dependency_lock,
        "reference_id": summary.reference_id,
        "reference_mode": summary.reference_mode,
        "equality_target": summary.equality_target,
        "backend": summary.backend,
        "device": "cpu",
        "dtype": "float64",
        "regularization_mode": "strict",
        "radius": None,
        "epoch_id": f"batch-audit:{data_seed}",
        "candidate_count": summary.query_count,
        "executed_count": summary.query_count,
        "skipped_count": 0,
        "independent_witness_count": summary.independent_count,
        "block_count": 0,
        "largest_block": 0,
        "ready_width": 0,
        "dependency_build_work": 0,
        "dependency_build_time_ms": 0.0,
        "ci_arithmetic_work": summary.ci_arithmetic_work,
        "graph_work": 0,
        "speculative_work": 0,
        "peak_rss_mb": summary.observed_peak_rss_mb,
        "peak_vram_mb": None,
        "nodes_equal": None,
        "skeleton_equal": None,
        "endpoint_matrix_equal": None,
        "witnessed_sepsets_valid": None,
        "status": "completed" if summary.status == "PASS" else "failed",
        "failure_signature": None
        if summary.status == "PASS"
        else (summary.mismatches[0].kind if summary.mismatches else "batch_audit_failed"),
    }
    record["logical_key"] = algorithm_logical_key(record)
    validate_algorithm_run_record(record)
    return record


def deterministic_audit_case(
    *, seed: int, samples: int, variables: int, query_count: int
) -> tuple[np.ndarray, tuple[CIQuery, ...]]:
    if variables < 4 or samples < 8 or query_count < 1:
        raise ValueError("audit case requires variables>=4, samples>=8, and queries>=1")
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(samples, variables))
    queries = []
    for rank in range(query_count):
        permutation = rng.permutation(variables).tolist()
        x, y = permutation[:2]
        order = rank % min(5, variables - 1)
        conditioning_set = tuple(permutation[2 : 2 + order])
        queries.append(
            CIQuery(
                f"audit:{rank}",
                x,
                y,
                conditioning_set,
                "batch_audit",
                f"seed:{seed}",
                rank,
                rank,
            )
        )
    return data, tuple(queries)


def _git_revision() -> str:
    root = Path(__file__).resolve().parents[3]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()
    return f"{revision}+dirty" if dirty else revision


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit scalar and CPU-batch Gaussian CI")
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--samples", type=int, default=512)
    parser.add_argument("--variables", type=int, default=12)
    parser.add_argument("--queries", type=int, default=256)
    parser.add_argument(
        "--strategy", choices=("exact_size", "power_of_two", "both"), default="both"
    )
    parser.add_argument("--memory-mb", type=float, default=64.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    data, queries = deterministic_audit_case(
        seed=args.seed,
        samples=args.samples,
        variables=args.variables,
        query_count=args.queries,
    )
    strategies = (
        ("exact_size", "power_of_two") if args.strategy == "both" else (args.strategy,)
    )
    summaries = [
        audit_scalar_batch(
            data,
            queries,
            batching_strategy=strategy,
            memory_budget_bytes=int(args.memory_mb * 1024 * 1024),
        )
        for strategy in strategies
    ]
    config_digest = digest_object(
        {
            "seed": args.seed,
            "samples": args.samples,
            "variables": args.variables,
            "queries": args.queries,
            "memory_mb": args.memory_mb,
            "strategies": strategies,
        }
    )
    dependency_lock = digest_object(
        {"numpy": np.__version__, "scipy": scipy.__version__}
    )
    run_records = [
        batch_audit_run_record(
            summary,
            run_id=f"batch-audit-{args.seed}-{summary.batching_strategy}",
            data_seed=args.seed,
            config_digest=config_digest,
            git_revision=_git_revision(),
            dependency_lock=dependency_lock,
        )
        for summary in summaries
    ]
    validate_unique_logical_keys(run_records)
    payload = {
        "contract_version": ARTIFACT_SCHEMA_VERSION,
        "reference_mode": "tensor_backend",
        "equality_target": "ci_result",
        "status": "PASS" if all(summary.status == "PASS" for summary in summaries) else "FAIL",
        "run_records": run_records,
        "summaries": [asdict(summary) for summary in summaries],
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(encoded + "\n", encoding="utf-8", newline="\n")
        temporary.replace(args.output)
    print(encoded)
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
