from __future__ import annotations

import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psutil

from .graphs import digest_object
from .phase1_execution import (
    PHASE_DIR,
    ROW_DIR,
    SHARD_DIR,
    _json_write,
    _run_metrics,
    _total_cpu_hours,
)
from .runner import ROOT, _phase1_graphs, _persist_run, _revision, _run_once, load_config


QUEUE_DIR = PHASE_DIR / "graph_queue"
CONTRACT_PATH = PHASE_DIR / "delta_contract.json"
CLAIM_DIR = QUEUE_DIR / "claims"
SLOT_DIR = QUEUE_DIR / "slots"
GRAPH_MANIFEST_DIR = QUEUE_DIR / "graph_manifests"
WORKER_MANIFEST_DIR = QUEUE_DIR / "worker_manifests"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _process_identity() -> dict:
    process = psutil.Process()
    return {
        "hostname": platform.node(),
        "pid": process.pid,
        "process_create_time": process.create_time(),
    }


def _owner_is_alive(payload: dict) -> bool:
    if payload.get("hostname") != platform.node():
        return True
    try:
        process = psutil.Process(int(payload["pid"]))
        return abs(process.create_time() - float(payload["process_create_time"])) < 1.0
    except (KeyError, TypeError, ValueError, psutil.Error):
        return False


def _atomic_claim(path: Path, payload: dict) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(descriptor, encoded)
    finally:
        os.close(descriptor)
    return True


def recover_stale_claims() -> list[str]:
    recovered: list[str] = []
    for directory in (CLAIM_DIR, SLOT_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                payload = _read_json(path)
            except Exception:
                payload = {}
            if not _owner_is_alive(payload):
                path.unlink(missing_ok=True)
                recovered.append(path.relative_to(ROOT).as_posix())
    return recovered


def _load_contract() -> dict:
    if not CONTRACT_PATH.exists():
        raise RuntimeError("delta contract is missing; install the delta input package first")
    contract = _read_json(CONTRACT_PATH)
    if contract.get("status") != "FROZEN":
        raise RuntimeError("delta contract is not frozen")
    if int(contract.get("workers", 0)) != 3:
        raise RuntimeError("this handoff authorizes exactly three graph workers")
    revision = _revision()
    if revision != contract.get("code_revision"):
        raise RuntimeError(
            f"code revision mismatch: expected {contract.get('code_revision')}, got {revision}"
        )
    return contract


def _inventory() -> pd.DataFrame:
    return pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")


def _validated_completed_row(item: dict) -> dict | None:
    path = ROW_DIR / f"{item['logical_run_id']}.json"
    if not path.exists():
        return None
    row = _read_json(path)
    checks = (
        row.get("terminal_status") == "completed",
        row.get("logical_run_id") == item["logical_run_id"],
        row.get("config_digest") == item["config_digest"],
        row.get("logical_key_digest") == item["logical_key_digest"],
        row.get("graph_digest") == item["graph_digest"],
        int(row.get("graph_seed", -1)) == int(item["graph_seed"]),
        int(row.get("scheduler_seed", -1)) == int(item["scheduler_seed"]),
    )
    if not all(checks):
        raise RuntimeError(f"successful/partial row collision for {item['logical_run_id']}")
    return row


def prepare_queue() -> dict:
    contract = _load_contract()
    recovered = recover_stale_claims()
    inventory = _inventory()
    expected_pending = set(contract["pending_ids"])
    actual_pending = {
        item["logical_run_id"]
        for item in inventory.to_dict("records")
        if item["logical_run_id"] in expected_pending and _validated_completed_row(item) is None
    }
    unexpected_completed = expected_pending - actual_pending
    if unexpected_completed:
        raise RuntimeError(
            "delta input already contains rows that were pending at freeze: "
            + ", ".join(sorted(unexpected_completed)[:5])
        )
    current_completed = {path.stem for path in ROW_DIR.glob("*.json")}
    if current_completed != set(contract["base_completed_ids"]):
        missing = set(contract["base_completed_ids"]) - current_completed
        extra = current_completed - set(contract["base_completed_ids"])
        raise RuntimeError(
            f"base row set mismatch: missing={len(missing)} extra={len(extra)}"
        )
    for directory in (CLAIM_DIR, SLOT_DIR, GRAPH_MANIFEST_DIR, WORKER_MANIFEST_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "READY",
        "prepared_at": _now(),
        "workers": 3,
        "pending_runs": len(expected_pending),
        "pending_graphs": len(contract["graph_indices"]),
        "recovered_stale_claims": recovered,
    }
    _json_write(QUEUE_DIR / "queue_status.json", payload)
    return payload


def _acquire_slot(worker_id: str) -> Path:
    identity = {**_process_identity(), "worker_id": worker_id, "claimed_at": _now()}
    for index in range(3):
        path = SLOT_DIR / f"slot-{index}.json"
        if _atomic_claim(path, {**identity, "slot": index}):
            return path
    raise RuntimeError("all three authorized worker slots are occupied")


def _claim_graph(graph_index: int, worker_id: str) -> Path | None:
    path = CLAIM_DIR / f"g{graph_index:03d}.json"
    payload = {
        **_process_identity(),
        "worker_id": worker_id,
        "graph_index": graph_index,
        "claimed_at": _now(),
    }
    return path if _atomic_claim(path, payload) else None


def _execute_item(item: dict, graph_tuple: tuple, config: dict, process: psutil.Process) -> dict:
    graph, _p, _latent, _degree, replicate = graph_tuple
    run_id = item["logical_run_id"]
    started_at = _now()
    cpu_start = time.process_time()
    wall_start = time.perf_counter()
    rss_start = process.memory_info().rss
    state, provenance, _, _, _ = _run_once(
        graph, item["scheduler"], int(item["scheduler_seed"]), config, run_id
    )
    cpu_elapsed = time.process_time() - cpu_start
    wall_elapsed = time.perf_counter() - wall_start
    rss_peak = max(rss_start, process.memory_info().rss)
    qpath, epath, gpath = _persist_run(run_id, graph, state, provenance)
    if item["scheduler"] == "stable_default":
        reference = state.graph
        baseline_cost = state.budget["weighted_cost"]
    else:
        stable_id = f"p1-main-g{int(item['graph_index']):03d}-stable_default"
        stable_path = ROW_DIR / f"{stable_id}.json"
        if not stable_path.exists():
            raise RuntimeError(f"stable reference is missing for {run_id}")
        stable = _read_json(stable_path)
        reference = stable["output_graph"]
        baseline_cost = int(stable["weighted_cost"])
    metrics = _run_metrics(
        state,
        provenance,
        reference,
        wall_elapsed,
        cpu_elapsed,
        rss_peak,
        baseline_cost,
        config["budget_checkpoints"],
    )
    row = {
        **item,
        **metrics,
        "phase": 1,
        "scope": "main",
        "replicate": replicate,
        "terminal_status": "completed",
        "started_at": started_at,
        "ended_at": _now(),
        "output_digest": digest_object(state.graph),
        "output_graph": state.graph,
        "full_output_matches_stable": state.graph == reference,
        "query_log": qpath,
        "event_log": epath,
        "graph_artifact": gpath,
        "data_seed": None,
        "prior_seed": None,
        "bootstrap_seed": config["bootstrap_seed"],
    }
    _json_write(ROW_DIR / f"{run_id}.json", row)
    return row


def _graph_is_complete(graph_index: int, inventory: pd.DataFrame) -> bool:
    items = inventory[inventory["graph_index"] == graph_index].to_dict("records")
    return all(_validated_completed_row(item) is not None for item in items)


def _run_graph(graph_index: int, worker_id: str, inventory: pd.DataFrame) -> dict:
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    graph_map = {index: value for index, value in enumerate(_phase1_graphs(config))}
    items = (
        inventory[inventory["graph_index"] == graph_index]
        .sort_values("scheduler_seed")
        .to_dict("records")
    )
    process = psutil.Process()
    manifest_path = GRAPH_MANIFEST_DIR / f"g{graph_index:03d}.json"
    states: list[dict] = []
    manifest = {
        "graph_index": graph_index,
        "worker_id": worker_id,
        "status": "running",
        "started_at": _now(),
        "runs": states,
    }
    _json_write(manifest_path, manifest)
    for item in items:
        completed = _validated_completed_row(item)
        if completed is not None:
            states.append({"logical_run_id": item["logical_run_id"], "status": "completed", "resumed": True})
            manifest["runs"] = states
            _json_write(manifest_path, manifest)
            continue
        plan = _read_json(PHASE_DIR / "execution_plan.json")
        if _total_cpu_hours() >= float(plan["hard_stop_cpu_hours"]):
            manifest.update(
                {
                    "status": "hard_stopped",
                    "reason": "COMPUTE_BUDGET_EXCEEDED",
                    "ended_at": _now(),
                    "runs": states,
                }
            )
            _json_write(manifest_path, manifest)
            return manifest
        state = {
            "logical_run_id": item["logical_run_id"],
            "status": "started",
            "started_at": _now(),
            "graph_seed": int(item["graph_seed"]),
            "scheduler_seed": int(item["scheduler_seed"]),
            "config_digest": item["config_digest"],
        }
        states.append(state)
        manifest["runs"] = states
        _json_write(manifest_path, manifest)
        try:
            row = _execute_item(item, graph_map[graph_index], config, process)
        except Exception as exc:
            state.update({"status": "failed", "failed_at": _now(), "error": repr(exc)})
            manifest.update({"status": "failed", "ended_at": _now(), "runs": states})
            _json_write(manifest_path, manifest)
            raise
        state.update(
            {
                "status": "completed",
                "completed_at": row["ended_at"],
                "cpu_time_seconds": row["cpu_time_seconds"],
                "wall_time_seconds": row["wall_time_seconds"],
            }
        )
        manifest["runs"] = states
        _json_write(manifest_path, manifest)
    manifest.update({"status": "completed", "ended_at": _now(), "runs": states})
    _json_write(manifest_path, manifest)
    return manifest


def run_graph_worker(worker_id: str) -> dict:
    if not worker_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in worker_id):
        raise ValueError("worker ID may contain only letters, digits, '-' and '_'")
    contract = _load_contract()
    if not (QUEUE_DIR / "queue_status.json").exists():
        raise RuntimeError("queue is not prepared")
    recover_stale_claims()
    slot = _acquire_slot(worker_id)
    worker_manifest = WORKER_MANIFEST_DIR / f"{worker_id}.json"
    completed_graphs: list[int] = []
    status = {
        "worker_id": worker_id,
        "status": "running",
        "started_at": _now(),
        "completed_graphs": completed_graphs,
        "slot": slot.name,
        **_process_identity(),
    }
    _json_write(worker_manifest, status)
    inventory = _inventory()
    try:
        while True:
            claimed: tuple[int, Path] | None = None
            for graph_index in contract["graph_indices"]:
                graph_index = int(graph_index)
                if _graph_is_complete(graph_index, inventory):
                    continue
                claim = _claim_graph(graph_index, worker_id)
                if claim is not None:
                    claimed = (graph_index, claim)
                    break
            if claimed is None:
                break
            graph_index, claim_path = claimed
            try:
                result = _run_graph(graph_index, worker_id, inventory)
                if result["status"] == "completed":
                    completed_graphs.append(graph_index)
                elif result["status"] == "hard_stopped":
                    status.update({"status": "hard_stopped", "reason": result["reason"]})
                    break
            finally:
                claim_path.unlink(missing_ok=True)
            status["completed_graphs"] = completed_graphs
            _json_write(worker_manifest, status)
        if status["status"] == "running":
            remaining = [
                int(index)
                for index in contract["graph_indices"]
                if not _graph_is_complete(int(index), inventory)
            ]
            status["status"] = "completed" if not remaining else "idle_waiting_for_claimed_graphs"
            status["remaining_graphs"] = remaining
        status["ended_at"] = _now()
        _json_write(worker_manifest, status)
        return status
    except Exception as exc:
        status.update({"status": "failed", "ended_at": _now(), "error": repr(exc)})
        _json_write(worker_manifest, status)
        raise
    finally:
        slot.unlink(missing_ok=True)


def _rebuild_shard_manifest(shard: int, inventory: pd.DataFrame) -> dict:
    items = inventory[inventory["shard"] == shard].sort_values(["graph_index", "scheduler_seed"])
    states = []
    for item in items.to_dict("records"):
        row = _validated_completed_row(item)
        if row is None:
            states.append({"logical_run_id": item["logical_run_id"], "status": "missing"})
        else:
            states.append(
                {
                    "logical_run_id": item["logical_run_id"],
                    "status": "completed",
                    "resumed": True,
                    "started_at": row.get("started_at"),
                    "completed_at": row.get("ended_at"),
                    "cpu_time_seconds": row.get("cpu_time_seconds"),
                    "wall_time_seconds": row.get("wall_time_seconds"),
                    "graph_seed": int(item["graph_seed"]),
                    "scheduler_seed": int(item["scheduler_seed"]),
                    "config_digest": item["config_digest"],
                }
            )
    completed = sum(state["status"] == "completed" for state in states)
    payload = {
        "shard": shard,
        "expected": len(states),
        "completed": completed,
        "failed": 0,
        "status": "completed" if completed == len(states) else "partial",
        "rebuilt_at": _now(),
        "source_of_truth": "immutable run_rows",
        "runs": states,
    }
    _json_write(SHARD_DIR / f"shard-{shard:02d}.json", payload)
    return payload


def queue_status(finalize: bool = False) -> dict:
    contract = _load_contract()
    recover_stale_claims()
    inventory = _inventory()
    pending_ids = set(contract["pending_ids"])
    completed = []
    failed = []
    for run_id in sorted(pending_ids):
        path = ROW_DIR / f"{run_id}.json"
        if not path.exists():
            continue
        try:
            row = _read_json(path)
            if row.get("terminal_status") == "completed" and row.get("config_digest") == contract["config_digest"]:
                completed.append(run_id)
            else:
                failed.append(run_id)
        except Exception:
            failed.append(run_id)
    active_slots = sorted(path.name for path in SLOT_DIR.glob("*.json")) if SLOT_DIR.exists() else []
    payload = {
        "status": "COMPLETED" if len(completed) == len(pending_ids) and not failed else "RUNNING_OR_INCOMPLETE",
        "expected_pending": len(pending_ids),
        "completed_pending": len(completed),
        "missing_pending": len(pending_ids) - len(completed) - len(failed),
        "failed_or_invalid": len(failed),
        "active_slots": active_slots,
        "graph_progress": {
            str(index): _graph_is_complete(int(index), inventory)
            for index in contract["graph_indices"]
        },
    }
    if finalize:
        if active_slots:
            raise RuntimeError("cannot finalize while worker slots are active")
        if payload["status"] != "COMPLETED":
            raise RuntimeError("cannot finalize an incomplete delta queue")
        payload["shards"] = {
            str(shard): _rebuild_shard_manifest(int(shard), inventory)
            for shard in contract["allowed_shards"]
        }
        payload["finalized_at"] = _now()
    _json_write(QUEUE_DIR / "queue_status.json", payload)
    return payload
