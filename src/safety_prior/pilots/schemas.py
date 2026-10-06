from __future__ import annotations

import hashlib
import json
from typing import Iterable, Mapping


ARTIFACT_SCHEMA_VERSION = "0.2.0"
REFERENCE_MODES = frozenset(
    {
        "dynamic_reference",
        "frozen_epoch_reference",
        "block_candidate",
        "tensor_backend",
    }
)
EQUALITY_TARGETS = frozenset({"trace", "evidence", "final_pag", "ci_result"})
RUN_STATUSES = frozenset({"completed", "failed", "incomplete"})


COMMON_RUN_FIELDS = frozenset(
    {
        "contract_version",
        "run_id",
        "direction",
        "graph_id",
        "graph_seed",
        "config_digest",
        "git_revision",
        "reference_id",
        "status",
        "wall_time_seconds",
        "peak_rss_mb",
    }
)

BLOCK_RUN_FIELDS = COMMON_RUN_FIELDS | {
    "radius",
    "block_count",
    "largest_block_cost_fraction",
    "ci_tests",
    "weighted_cost",
    "reference_equal",
    "wrong_determined_endpoints",
}

TIER_RUN_FIELDS = COMMON_RUN_FIELDS | {
    "gamma",
    "error_mode",
    "true_tier_covered",
    "pds_candidates",
    "envelope_candidates",
    "retention_ratio",
    "reference_equal",
    "solver_time_seconds",
}

ALGORITHM_RUN_FIELDS = frozenset(
    {
        "contract_version",
        "run_id",
        "logical_key",
        "graph_seed",
        "data_seed",
        "prior_seed",
        "scheduler_seed",
        "git_revision",
        "config_digest",
        "dependency_lock",
        "reference_id",
        "reference_mode",
        "equality_target",
        "backend",
        "device",
        "dtype",
        "regularization_mode",
        "radius",
        "epoch_id",
        "candidate_count",
        "executed_count",
        "skipped_count",
        "independent_witness_count",
        "block_count",
        "largest_block",
        "ready_width",
        "dependency_build_work",
        "dependency_build_time_ms",
        "ci_arithmetic_work",
        "graph_work",
        "speculative_work",
        "peak_rss_mb",
        "peak_vram_mb",
        "nodes_equal",
        "skeleton_equal",
        "endpoint_matrix_equal",
        "witnessed_sepsets_valid",
        "status",
        "failure_signature",
    }
)

_COUNT_FIELDS = frozenset(
    {
        "candidate_count",
        "executed_count",
        "skipped_count",
        "independent_witness_count",
        "block_count",
        "largest_block",
        "ready_width",
        "dependency_build_work",
        "ci_arithmetic_work",
        "graph_work",
        "speculative_work",
    }
)

_LOGICAL_KEY_FIELDS = (
    "graph_seed",
    "data_seed",
    "prior_seed",
    "scheduler_seed",
    "config_digest",
    "reference_id",
    "reference_mode",
    "backend",
    "radius",
    "epoch_id",
)


def validate_run_record(record: Mapping[str, object], direction: str) -> None:
    if direction == "block_icd":
        required = BLOCK_RUN_FIELDS
    elif direction == "robust_tier":
        required = TIER_RUN_FIELDS
    else:
        raise ValueError(f"Unknown research direction: {direction}")
    missing = required - set(record)
    if missing:
        raise ValueError(f"Missing {direction} run fields: {sorted(missing)}")


def algorithm_logical_key(record: Mapping[str, object]) -> str:
    missing = set(_LOGICAL_KEY_FIELDS) - set(record)
    if missing:
        raise ValueError(f"Missing logical-key fields: {sorted(missing)}")
    payload = {field: record[field] for field in _LOGICAL_KEY_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_algorithm_run_record(record: Mapping[str, object]) -> None:
    missing = ALGORITHM_RUN_FIELDS - set(record)
    if missing:
        raise ValueError(f"Missing algorithm run fields: {sorted(missing)}")
    if record["contract_version"] != ARTIFACT_SCHEMA_VERSION:
        raise ValueError(f"contract_version must be {ARTIFACT_SCHEMA_VERSION}")
    if record["reference_mode"] not in REFERENCE_MODES:
        raise ValueError(f"Unknown reference_mode: {record['reference_mode']}")
    if record["equality_target"] not in EQUALITY_TARGETS:
        raise ValueError(f"Unknown equality_target: {record['equality_target']}")
    if record["status"] not in RUN_STATUSES:
        raise ValueError(f"Unknown run status: {record['status']}")
    for field in _COUNT_FIELDS:
        value = record[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{field} must be a non-negative integer")
    if record["executed_count"] + record["skipped_count"] > record["candidate_count"]:
        raise ValueError("executed_count + skipped_count cannot exceed candidate_count")
    if record["status"] == "completed" and (
        record["executed_count"] + record["skipped_count"] != record["candidate_count"]
    ):
        raise ValueError("completed runs must account for every candidate")
    if record["independent_witness_count"] > record["executed_count"]:
        raise ValueError("independent_witness_count cannot exceed executed_count")
    if record["block_count"] == 0 and record["largest_block"] != 0:
        raise ValueError("largest_block must be zero when block_count is zero")
    if record["status"] == "failed" and not record["failure_signature"]:
        raise ValueError("failed runs require a failure_signature")
    expected_key = algorithm_logical_key(record)
    if record["logical_key"] != expected_key:
        raise ValueError("logical_key does not match the canonical run identity")


def validate_unique_logical_keys(records: Iterable[Mapping[str, object]]) -> None:
    owners: dict[str, str] = {}
    for record in records:
        validate_algorithm_run_record(record)
        key = str(record["logical_key"])
        run_id = str(record["run_id"])
        if key in owners:
            raise ValueError(
                f"Duplicate logical_key for run_id {owners[key]!r} and {run_id!r}: {key}"
            )
        owners[key] = run_id
