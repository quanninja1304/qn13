from pathlib import Path

import pytest
import yaml

from safety_prior.pilots.schemas import (
    ALGORITHM_RUN_FIELDS,
    ARTIFACT_SCHEMA_VERSION,
    algorithm_logical_key,
    validate_algorithm_run_record,
    validate_unique_logical_keys,
)


def _record(run_id: str = "run-1") -> dict:
    record = {field: None for field in ALGORITHM_RUN_FIELDS}
    record.update(
        {
            "contract_version": ARTIFACT_SCHEMA_VERSION,
            "run_id": run_id,
            "graph_seed": 1,
            "data_seed": 2,
            "prior_seed": None,
            "scheduler_seed": 3,
            "git_revision": "abc",
            "config_digest": "cfg",
            "dependency_lock": "lock",
            "reference_id": "GaussianCI.scalar.strict",
            "reference_mode": "tensor_backend",
            "equality_target": "ci_result",
            "backend": "gaussian_cpu_batch_exact_size_strict",
            "device": "cpu",
            "dtype": "float64",
            "regularization_mode": "strict",
            "radius": 1,
            "epoch_id": "epoch-1",
            "candidate_count": 10,
            "executed_count": 8,
            "skipped_count": 2,
            "independent_witness_count": 3,
            "block_count": 0,
            "largest_block": 0,
            "ready_width": 0,
            "dependency_build_work": 0,
            "dependency_build_time_ms": 0.0,
            "ci_arithmetic_work": 216,
            "graph_work": 0,
            "speculative_work": 0,
            "peak_rss_mb": 12.0,
            "peak_vram_mb": None,
            "nodes_equal": True,
            "skeleton_equal": True,
            "endpoint_matrix_equal": True,
            "witnessed_sepsets_valid": True,
            "status": "completed",
            "failure_signature": None,
        }
    )
    record["logical_key"] = algorithm_logical_key(record)
    return record


def test_schema_v020_accepts_a_complete_record():
    validate_algorithm_run_record(_record())


def test_schema_v020_rejects_missing_or_invalid_contract_fields():
    missing = _record()
    missing.pop("reference_mode")
    with pytest.raises(ValueError, match="Missing algorithm run fields"):
        validate_algorithm_run_record(missing)

    invalid = _record()
    invalid["reference_mode"] = "ambiguous"
    with pytest.raises(ValueError, match="reference_mode"):
        validate_algorithm_run_record(invalid)


def test_schema_v020_rejects_duplicate_resume_logical_keys():
    first = _record("attempt-1")
    second = _record("attempt-2")

    with pytest.raises(ValueError, match="Duplicate logical_key"):
        validate_unique_logical_keys((first, second))


def test_schema_v020_rejects_a_stale_or_forged_logical_key():
    record = _record()
    record["epoch_id"] = "different"

    with pytest.raises(ValueError, match="logical_key"):
        validate_algorithm_run_record(record)


def test_schema_v020_requires_completed_candidate_accounting():
    record = _record()
    record["skipped_count"] = 1

    with pytest.raises(ValueError, match="account for every candidate"):
        validate_algorithm_run_record(record)


def test_reference_contract_declares_all_modes_and_regression_seed():
    root = Path(__file__).resolve().parents[2]
    contract = yaml.safe_load(
        (root / "configs/tensorized_icd/reference_contract.yaml").read_text(encoding="utf-8")
    )

    assert contract["contract_version"] == ARTIFACT_SCHEMA_VERSION
    assert set(contract["reference_modes"]) == {
        "dynamic_reference",
        "frozen_epoch_reference",
        "block_candidate",
        "tensor_backend",
    }
    assert contract["gates"]["g0_5"]["frozen_regression_seed"] == 74304
