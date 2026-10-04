from __future__ import annotations

from typing import Mapping


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
