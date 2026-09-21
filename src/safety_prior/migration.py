from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psutil

from .graphs import digest_object
from .runner import (
    ARTIFACTS,
    ROOT,
    _phase1_graphs,
    _revision,
    _run_once,
    load_config,
    resolve_project_reference,
)


PHASE_DIR = ARTIFACTS / "phase1"
ROW_DIR = PHASE_DIR / "run_rows"
ENV_DIR = ROOT / "env"
CHECKSUM_PATH = PHASE_DIR / "migration_sha256.jsonl"
CHECKSUM_SUMMARY_PATH = PHASE_DIR / "migration_sha256_summary.json"
SNAPSHOT_PATH = PHASE_DIR / "migration_snapshot.json"
REPLAY_REFERENCE_PATH = PHASE_DIR / "migration_replay_reference.json"
REPLAY_VALIDATION_PATH = PHASE_DIR / "migration_replay_validation.json"
DEFAULT_REPLAY_IDS = tuple(
    f"p1-main-g001-{scheduler}"
    for scheduler in ("stable_default", "random_valid", "cost_only", "graph_only", "oracle_query")
)
QUERY_SIGNATURE_FIELDS = (
    "run_id",
    "query_id",
    "step",
    "phase",
    "i",
    "j",
    "conditioning_set",
    "conditioning_order",
    "eligible_candidate_count",
    "prerequisite_ids",
    "state_digest_before",
    "ci_backend",
    "ci_statistic",
    "p_value",
    "ci_decision",
    "prior_score",
    "graph_score",
    "cost_score",
    "uncertainty_score",
    "total_score",
    "tie_break_key",
    "estimated_cost",
    "state_digest_after",
    "edge_removed",
    "separating_set_recorded",
    "opened_query_ids",
    "seed_refs",
    "provisional_removed_edges",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _package_versions() -> dict[str, str | None]:
    names = (
        "causal-learn",
        "matplotlib",
        "networkx",
        "numpy",
        "pandas",
        "psutil",
        "pyarrow",
        "PyYAML",
        "scikit-learn",
        "scipy",
        "pytest",
    )
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def write_environment_freeze(label: str) -> dict:
    if label not in {"windows_source", "linux_vps"}:
        raise ValueError("environment label must be windows_source or linux_vps")
    ENV_DIR.mkdir(parents=True, exist_ok=True)
    freeze = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze", "--all"], text=True
    )
    freeze_path = ENV_DIR / f"{label}_freeze.txt"
    freeze_path.write_text(freeze, encoding="utf-8", newline="\n")
    payload = {
        "captured_at": _now(),
        "label": label,
        "os": platform.system(),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "python_executable": sys.executable,
        "cpu_count": os.cpu_count(),
        "memory_bytes": psutil.virtual_memory().total,
        "packages": _package_versions(),
        "code_revision": _revision(),
        "pip_freeze": freeze_path.relative_to(ROOT).as_posix(),
    }
    _write_json(ENV_DIR / f"{label}_environment.json", payload)
    if label == "windows_source":
        lock_lines = [
            f"{name}=={version}"
            for name, version in payload["packages"].items()
            if version is not None
        ]
        (ENV_DIR / "core_requirements_lock.txt").write_text(
            "\n".join(lock_lines) + "\n", encoding="utf-8", newline="\n"
        )
    return payload


def write_migration_snapshot() -> dict:
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    expected_ids = set(inventory["logical_run_id"])
    completed_ids = set()
    invalid_rows = []
    for path in sorted(ROW_DIR.glob("*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            invalid_rows.append({"path": path.relative_to(ROOT).as_posix(), "error": repr(exc)})
            continue
        if row.get("terminal_status") == "completed":
            completed_ids.add(row["logical_run_id"])
    payload = {
        "created_at": _now(),
        "expected": len(expected_ids),
        "completed": len(completed_ids),
        "pending": len(expected_ids - completed_ids),
        "unexpected": sorted(completed_ids - expected_ids),
        "pending_ids": sorted(expected_ids - completed_ids),
        "invalid_rows": invalid_rows,
        "config_digest": str(inventory["config_digest"].iloc[0]),
        "scientific_contract_version": load_config(ROOT / "configs/kill_test/phase1.yaml")["contract_version"],
        "active_executor": "NONE_MIGRATION_QUIESCED",
        "source_of_truth_policy": {
            "code": "source tree checksum; Git revision unavailable until repository is initialized",
            "active_artifacts": "VPS after validation",
            "durable_artifacts": "external archive with verified checksum",
            "laptop_during_vps_execution": "READ_ONLY",
        },
    }
    _write_json(SNAPSHOT_PATH, payload)
    return payload


def _query_signature(rows) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    count = cost = 0
    for row in rows:
        payload = row if isinstance(row, dict) else row.as_dict()
        scientific = {field: payload.get(field) for field in QUERY_SIGNATURE_FIELDS}
        encoded = json.dumps(scientific, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest.update(encoded.encode("utf-8"))
        digest.update(b"\n")
        count += 1
        cost += int(payload["estimated_cost"])
    return digest.hexdigest(), count, cost


def _stored_query_signature(row: dict) -> tuple[str, int, int]:
    path = resolve_project_reference(row["query_log"])

    def records():
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                yield json.loads(line)

    return _query_signature(records())


def _replay_result(item: dict, graph_tuple: tuple, config: dict) -> dict:
    graph = graph_tuple[0]
    state, provenance, _, _, _ = _run_once(
        graph,
        item["scheduler"],
        int(item["scheduler_seed"]),
        config,
        item["logical_run_id"],
    )
    signature, count, cost = _query_signature(provenance.queries)
    return {
        "logical_run_id": item["logical_run_id"],
        "graph_seed": int(item["graph_seed"]),
        "scheduler_seed": int(item["scheduler_seed"]),
        "scheduler": item["scheduler"],
        "config_digest": item["config_digest"],
        "graph_digest": graph.digest,
        "output_digest": digest_object(state.graph),
        "output_graph": state.graph,
        "ci_tests": count,
        "weighted_cost": cost,
        "query_sequence_digest": signature,
    }


def create_replay_reference(run_ids: tuple[str, ...] = DEFAULT_REPLAY_IDS) -> dict:
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    records = {row["logical_run_id"]: row for row in inventory.to_dict("records")}
    graph_map = {index: value for index, value in enumerate(_phase1_graphs(config))}
    results = []
    for run_id in run_ids:
        if run_id not in records:
            raise ValueError(f"replay run is not in frozen inventory: {run_id}")
        stored_path = ROW_DIR / f"{run_id}.json"
        stored = json.loads(stored_path.read_text(encoding="utf-8"))
        if stored.get("terminal_status") != "completed":
            raise RuntimeError(f"replay source is not completed: {run_id}")
        source_signature, source_count, source_cost = _stored_query_signature(stored)
        replay = _replay_result(records[run_id], graph_map[int(records[run_id]["graph_index"])], config)
        checks = {
            "graph_digest": replay["graph_digest"] == stored["graph_digest"],
            "output_digest": replay["output_digest"] == stored["output_digest"],
            "output_graph": replay["output_graph"] == stored["output_graph"],
            "ci_tests": replay["ci_tests"] == stored["ci_tests"] == source_count,
            "weighted_cost": replay["weighted_cost"] == stored["weighted_cost"] == source_cost,
            "query_sequence": replay["query_sequence_digest"] == source_signature,
        }
        results.append({**replay, "checks": checks, "source_query_sequence_digest": source_signature})
    payload = {
        "created_at": _now(),
        "status": "PASS" if all(all(r["checks"].values()) for r in results) else "FAIL",
        "purpose": "Windows source reference for cross-platform replay; timing fields excluded",
        "run_ids": list(run_ids),
        "results": results,
    }
    _write_json(REPLAY_REFERENCE_PATH, payload)
    if payload["status"] != "PASS":
        raise RuntimeError("source replay reference did not reproduce completed scientific outputs")
    return payload


def validate_replay_reference() -> dict:
    reference = json.loads(REPLAY_REFERENCE_PATH.read_text(encoding="utf-8"))
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    records = {row["logical_run_id"]: row for row in inventory.to_dict("records")}
    graph_map = {index: value for index, value in enumerate(_phase1_graphs(config))}
    expected = {row["logical_run_id"]: row for row in reference["results"]}
    results = []
    for run_id in reference["run_ids"]:
        replay = _replay_result(records[run_id], graph_map[int(records[run_id]["graph_index"])], config)
        source = expected[run_id]
        checks = {
            field: replay[field] == source[field]
            for field in (
                "graph_digest",
                "output_digest",
                "output_graph",
                "ci_tests",
                "weighted_cost",
                "query_sequence_digest",
            )
        }
        results.append({"logical_run_id": run_id, "checks": checks})
    payload = {
        "validated_at": _now(),
        "status": "PASS" if all(all(r["checks"].values()) for r in results) else "FAIL",
        "source_reference": REPLAY_REFERENCE_PATH.relative_to(ROOT).as_posix(),
        "results": results,
    }
    _write_json(REPLAY_VALIDATION_PATH, payload)
    if payload["status"] != "PASS":
        raise RuntimeError("cross-platform replay differs from the Windows source reference")
    return payload


def _migration_files() -> list[Path]:
    roots = [ROOT / name for name in ("src", "configs", "tests", "reports", "artifacts", "env")]
    paths = []
    for root in roots:
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    paths.extend(
        path
        for path in (ROOT / "pyproject.toml", ROOT / "README.md")
        if path.exists()
    )
    excluded_names = {
        CHECKSUM_PATH.name,
        CHECKSUM_SUMMARY_PATH.name,
        "migration_checksum_verification.json",
        REPLAY_VALIDATION_PATH.name,
        "linux_vps_freeze.txt",
        "linux_vps_environment.json",
    }
    return sorted(
        {
            path.resolve()
            for path in paths
            if path.name not in excluded_names
            and path.suffix not in {".pyc", ".tmp"}
            and "__pycache__" not in path.parts
            and ".pytest_cache" not in path.parts
            and not any(part.endswith(".egg-info") for part in path.parts)
        },
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def write_checksum_manifest() -> dict:
    files = _migration_files()
    CHECKSUM_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_bytes = 0
    tree_digest = hashlib.sha256()
    with CHECKSUM_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            size = path.stat().st_size
            sha256 = _sha256(path)
            entry = {"path": relative, "size": size, "sha256": sha256}
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
            tree_digest.update(f"{relative}\0{size}\0{sha256}\n".encode("utf-8"))
            total_bytes += size
    payload = {
        "created_at": _now(),
        "algorithm": "sha256",
        "file_count": len(files),
        "total_bytes": total_bytes,
        "source_tree_digest": tree_digest.hexdigest(),
        "manifest": CHECKSUM_PATH.relative_to(ROOT).as_posix(),
    }
    _write_json(CHECKSUM_SUMMARY_PATH, payload)
    return payload


def verify_checksum_manifest() -> dict:
    missing = []
    mismatched = []
    checked = 0
    with CHECKSUM_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            entry = json.loads(line)
            path = resolve_project_reference(entry["path"])
            if not path.exists():
                missing.append(entry["path"])
                continue
            actual_size = path.stat().st_size
            actual_hash = _sha256(path)
            if actual_size != entry["size"] or actual_hash != entry["sha256"]:
                mismatched.append(
                    {
                        "path": entry["path"],
                        "expected_size": entry["size"],
                        "actual_size": actual_size,
                        "expected_sha256": entry["sha256"],
                        "actual_sha256": actual_hash,
                    }
                )
            checked += 1
    payload = {
        "verified_at": _now(),
        "status": "PASS" if not missing and not mismatched else "FAIL",
        "checked": checked,
        "missing": missing,
        "mismatched": mismatched,
    }
    _write_json(PHASE_DIR / "migration_checksum_verification.json", payload)
    if payload["status"] != "PASS":
        raise RuntimeError("migration checksum verification failed")
    return payload


def prepare_source_migration() -> dict:
    environment = write_environment_freeze("windows_source")
    if environment["os"] != "Windows":
        raise RuntimeError("migration source preparation must run on the Windows source")
    snapshot = write_migration_snapshot()
    replay = create_replay_reference()
    checksums = write_checksum_manifest()
    return {
        "status": "PASS",
        "environment": environment,
        "snapshot": snapshot,
        "replay": {"status": replay["status"], "run_ids": replay["run_ids"]},
        "checksums": checksums,
    }


def validate_vps_migration() -> dict:
    environment = write_environment_freeze("linux_vps")
    if environment["os"] != "Linux":
        raise RuntimeError("VPS migration validation must run on Linux")
    checksums = verify_checksum_manifest()
    replay = validate_replay_reference()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return {
        "status": "PASS",
        "environment": environment,
        "source_snapshot": snapshot,
        "checksums": checksums,
        "cross_platform_replay": replay,
        "resume_authorized": checksums["status"] == "PASS" and replay["status"] == "PASS",
    }
