from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import pandas as pd

from .graphs import digest_object
from .phase1_execution import PHASE_DIR, ROW_DIR, SHARD_DIR, _json_write
from .phase1_parallel import CONTRACT_PATH, QUEUE_DIR, queue_status
from .runner import ROOT, _revision, load_config, resolve_project_reference


PACKAGE_METADATA = "delta_package.json"
PACKAGE_MANIFEST = "delta_package_sha256.jsonl"
HANDOFF_PATH = ROOT / "docs" / "kill_test" / "windows_i9_delta_handoff.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_output(output: Path) -> Path:
    output = output.resolve()
    try:
        output.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError("delta packages must be written outside the project root")
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def _copy_relative(relative: str, output: Path) -> None:
    source = ROOT / Path(*PurePosixPath(relative).parts)
    if not source.is_file():
        raise FileNotFoundError(source)
    destination = output / Path(*PurePosixPath(relative).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _write_package_manifest(output: Path, metadata: dict) -> dict:
    metadata_path = output / PACKAGE_METADATA
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    paths = sorted(
        path
        for path in output.rglob("*")
        if path.is_file() and path.name != PACKAGE_MANIFEST
    )
    tree = hashlib.sha256()
    total = 0
    manifest_path = output / PACKAGE_MANIFEST
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        for path in paths:
            relative = path.relative_to(output).as_posix()
            size = path.stat().st_size
            sha256 = _sha256(path)
            entry = {"path": relative, "size": size, "sha256": sha256}
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
            tree.update(f"{relative}\0{size}\0{sha256}\n".encode("utf-8"))
            total += size
    summary = {
        "files": len(paths),
        "bytes": total,
        "tree_sha256": tree.hexdigest(),
        "manifest": PACKAGE_MANIFEST,
    }
    return summary


def verify_delta_package(package: str | Path) -> dict:
    package = Path(package).resolve()
    metadata = _read_json(package / PACKAGE_METADATA)
    missing: list[str] = []
    mismatched: list[str] = []
    checked = 0
    with (package / PACKAGE_MANIFEST).open("r", encoding="utf-8") as handle:
        for line in handle:
            entry = json.loads(line)
            pure = PurePosixPath(entry["path"])
            if pure.is_absolute() or ".." in pure.parts:
                raise ValueError(f"unsafe package path: {entry['path']}")
            path = (package / Path(*pure.parts)).resolve()
            path.relative_to(package)
            if not path.is_file():
                missing.append(entry["path"])
                continue
            if path.stat().st_size != int(entry["size"]) or _sha256(path) != entry["sha256"]:
                mismatched.append(entry["path"])
            checked += 1
    status = "PASS" if not missing and not mismatched else "FAIL"
    return {
        "status": status,
        "kind": metadata.get("kind"),
        "checked": checked,
        "missing": missing,
        "mismatched": mismatched,
        "metadata": metadata,
    }


def _frozen_contract() -> dict:
    snapshot = _read_json(PHASE_DIR / "migration_snapshot.json")
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    expected_ids = set(inventory["logical_run_id"])
    base_completed_ids = set()
    for path in ROW_DIR.glob("*.json"):
        row = _read_json(path)
        if row.get("terminal_status") == "completed":
            base_completed_ids.add(row["logical_run_id"])
    pending_ids = expected_ids - base_completed_ids
    if snapshot.get("completed") != 650 or snapshot.get("pending") != 150:
        raise RuntimeError("delta export requires the frozen 650/800 source snapshot")
    if pending_ids != set(snapshot["pending_ids"]):
        raise RuntimeError("current pending IDs differ from the frozen migration snapshot")
    pending_inventory = inventory[inventory["logical_run_id"].isin(pending_ids)]
    if set(pending_inventory["shard"].astype(int)) != {5, 7}:
        raise RuntimeError("delta scope must contain only shard 5 and shard 7")
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    config_digest = digest_object(config)
    if config_digest != snapshot["config_digest"]:
        raise RuntimeError("scientific config digest differs from the frozen snapshot")
    return {
        "status": "FROZEN",
        "created_at": _now(),
        "code_revision": _revision(),
        "config_digest": config_digest,
        "expected_total": len(expected_ids),
        "base_completed": len(base_completed_ids),
        "pending": len(pending_ids),
        "base_completed_ids": sorted(base_completed_ids),
        "pending_ids": sorted(pending_ids),
        "graph_indices": sorted(int(value) for value in pending_inventory["graph_index"].unique()),
        "allowed_shards": [5, 7],
        "workers": 3,
        "parallel_unit": "graph_index",
        "scheduler_order": [
            "stable_default",
            "random_valid",
            "cost_only",
            "graph_only",
            "oracle_query",
        ],
        "return_policy": "all artifacts referenced by exactly the 150 frozen pending run IDs",
    }


def export_delta_input(output: str | Path) -> dict:
    output = _prepare_output(Path(output))
    contract = _frozen_contract()
    _json_write(CONTRACT_PATH, contract)
    relative_files = [
        "artifacts/kill_test/phase1/execution_plan.json",
        "artifacts/kill_test/phase1/logical_inventory.parquet",
        "artifacts/kill_test/phase1/migration_snapshot.json",
        "artifacts/kill_test/phase1/migration_replay_reference.json",
        "artifacts/kill_test/phase1/delta_contract.json",
        "artifacts/kill_test/phase1/shard_manifests/shard-05.json",
        "artifacts/kill_test/phase1/shard_manifests/shard-07.json",
        "env/core_requirements_lock.txt",
        "env/windows_source_environment.json",
        "env/windows_source_freeze.txt",
        "docs/kill_test/windows_i9_delta_handoff.md",
    ]
    relative_files.extend(
        path.relative_to(ROOT).as_posix() for path in sorted(ROW_DIR.glob("*.json"))
    )
    for relative in relative_files:
        _copy_relative(relative, output)
    subprocess.run(
        ["git", "bundle", "create", str(output / "handoff_code.bundle"), "HEAD"],
        cwd=ROOT,
        check=True,
    )
    metadata = {
        "kind": "phase1_delta_input",
        "created_at": _now(),
        "code_revision": contract["code_revision"],
        "config_digest": contract["config_digest"],
        "base_completed": contract["base_completed"],
        "pending": contract["pending"],
        "workers": 3,
    }
    summary = _write_package_manifest(output, metadata)
    return {"status": "PASS", "output": str(output), **summary, **metadata}


def _copy_package_into_project(package: Path, allow_return: bool) -> int:
    count = 0
    for source in sorted(package.rglob("*")):
        if not source.is_file() or source.name in {
            PACKAGE_MANIFEST,
            PACKAGE_METADATA,
            "handoff_code.bundle",
        }:
            continue
        relative = source.relative_to(package)
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if _sha256(destination) == _sha256(source):
                continue
            relative_text = relative.as_posix()
            permitted_input_provenance = not allow_return and relative_text in {
                "env/windows_source_environment.json",
                "env/windows_source_freeze.txt",
            }
            permitted_return_state = allow_return and (
                relative_text.startswith("artifacts/kill_test/phase1/shard_manifests/")
                or relative_text.startswith("artifacts/kill_test/phase1/graph_queue/")
            )
            permitted_overwrite = permitted_input_provenance or permitted_return_state
            if not permitted_overwrite:
                raise RuntimeError(f"package collision with different content: {relative_text}")
        temp = destination.with_suffix(destination.suffix + ".delta-import.tmp")
        shutil.copy2(source, temp)
        if _sha256(temp) != _sha256(source):
            temp.unlink(missing_ok=True)
            raise RuntimeError(f"copy verification failed: {relative.as_posix()}")
        temp.replace(destination)
        count += 1
    return count


def install_delta_input(package: str | Path) -> dict:
    package = Path(package).resolve()
    verification = verify_delta_package(package)
    if verification["status"] != "PASS" or verification["kind"] != "phase1_delta_input":
        raise RuntimeError("delta input package verification failed")
    expected_revision = verification["metadata"]["code_revision"]
    if _revision() != expected_revision:
        raise RuntimeError(f"checkout must be exactly {expected_revision}")
    copied = _copy_package_into_project(package, allow_return=False)
    contract = _read_json(CONTRACT_PATH)
    return {
        "status": "PASS",
        "copied_files": copied,
        "code_revision": expected_revision,
        "completed": contract["base_completed"],
        "pending": contract["pending"],
        "workers": contract["workers"],
    }


def export_delta_return(output: str | Path) -> dict:
    output = _prepare_output(Path(output))
    contract = _read_json(CONTRACT_PATH)
    status = queue_status(finalize=False)
    if status["status"] != "COMPLETED" or status["active_slots"]:
        raise RuntimeError("all 150 pending runs must be complete and all workers stopped")
    relative_files: set[str] = {
        CONTRACT_PATH.relative_to(ROOT).as_posix(),
        (SHARD_DIR / "shard-05.json").relative_to(ROOT).as_posix(),
        (SHARD_DIR / "shard-07.json").relative_to(ROOT).as_posix(),
    }
    for path in QUEUE_DIR.rglob("*.json"):
        relative_files.add(path.relative_to(ROOT).as_posix())
    for run_id in contract["pending_ids"]:
        row_path = ROW_DIR / f"{run_id}.json"
        row = _read_json(row_path)
        if row.get("terminal_status") != "completed" or row.get("config_digest") != contract["config_digest"]:
            raise RuntimeError(f"invalid completed delta row: {run_id}")
        relative_files.add(row_path.relative_to(ROOT).as_posix())
        for field in ("query_log", "event_log", "graph_artifact"):
            artifact = resolve_project_reference(row[field])
            if not artifact.is_file():
                raise RuntimeError(f"missing {field} for {run_id}")
            relative_files.add(artifact.relative_to(ROOT).as_posix())
    for relative in sorted(relative_files):
        _copy_relative(relative, output)
    metadata = {
        "kind": "phase1_delta_return",
        "created_at": _now(),
        "code_revision": contract["code_revision"],
        "config_digest": contract["config_digest"],
        "completed_delta_runs": len(contract["pending_ids"]),
        "run_ids": contract["pending_ids"],
    }
    summary = _write_package_manifest(output, metadata)
    return {"status": "PASS", "output": str(output), **summary, **metadata}


def import_delta_return(package: str | Path) -> dict:
    package = Path(package).resolve()
    verification = verify_delta_package(package)
    if verification["status"] != "PASS" or verification["kind"] != "phase1_delta_return":
        raise RuntimeError("delta return package verification failed")
    metadata = verification["metadata"]
    if _revision() != metadata["code_revision"]:
        raise RuntimeError("local checkout does not match the delta return code revision")
    local_contract = _read_json(CONTRACT_PATH)
    if metadata["config_digest"] != local_contract["config_digest"]:
        raise RuntimeError("delta return config digest mismatch")
    if set(metadata["run_ids"]) != set(local_contract["pending_ids"]):
        raise RuntimeError("delta return run-ID set differs from the frozen pending set")
    package_rows = package / ROW_DIR.relative_to(ROOT)
    row_ids = {path.stem for path in package_rows.glob("*.json")}
    if row_ids != set(local_contract["pending_ids"]):
        raise RuntimeError("delta return does not contain exactly the 150 pending rows")
    copied = _copy_package_into_project(package, allow_return=True)
    post = queue_status(finalize=False)
    if post["status"] != "COMPLETED":
        raise RuntimeError("imported delta is incomplete after verified copy")
    return {
        "status": "PASS",
        "copied_files": copied,
        "completed_delta_runs": post["completed_pending"],
        "next_command": "python -m safety_prior.cli phase1-analyze",
    }
