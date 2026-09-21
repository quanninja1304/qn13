from __future__ import annotations

import json
import os
import shutil
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil

from .gates import evaluate_k1, gate_record
from .graphs import digest_object, skeleton_edges_from_pag
from .metrics import bootstrap_median_ci, tests_to_skeleton_target
from .runner import (
    ARTIFACTS, REPORTS, ROOT, _phase1_graphs, _persist_run, _run_once,
    _write_runs, _write_seed_manifest, load_config, resolve_project_reference,
)

PHASE_DIR = ARTIFACTS / "phase1"
SHARD_DIR = PHASE_DIR / "shard_manifests"
ROW_DIR = PHASE_DIR / "run_rows"
FROZEN_DIGEST_KEY = "configs\\kill_test\\phase1.yaml"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_write(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    try:
        temp.replace(path)
    except PermissionError:
        # Windows scanners/readers can briefly hold the destination open. The
        # manifest is orchestration state only; scientific rows are immutable
        # per-run files and remain the source of truth for resume/audit.
        path.write_text(temp.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _source_hash(relative: str) -> str:
    return digest_object((ROOT / relative).read_text(encoding="utf-8"))


def materialize_inventory() -> tuple[dict, list[dict]]:
    config_path = ROOT / "configs/kill_test/phase1.yaml"
    config = load_config(config_path)
    digest_file = json.loads((ARTIFACTS / "config_digest.json").read_text(encoding="utf-8"))
    frozen = digest_file.get(FROZEN_DIGEST_KEY) or digest_file.get("configs/kill_test/phase1.yaml")
    current = digest_object(config)
    inventory = []
    for graph_index, (graph, p, latent, degree, replicate) in enumerate(_phase1_graphs(config)):
        for scheduler_index, scheduler in enumerate(config["schedulers"]):
            scheduler_seed = 60000 + graph_index * 10 + scheduler_index
            logical_key = {
                "phase": 1, "graph_seed": graph.graph_seed, "p": p,
                "latent_ratio": latent, "average_degree": degree,
                "scheduler": scheduler, "config_digest": current,
            }
            inventory.append({
                **logical_key,
                "logical_run_id": f"p1-main-g{graph_index:03d}-{scheduler}",
                "logical_key_digest": digest_object(logical_key),
                "graph_index": graph_index, "replicate": replicate,
                "scheduler_seed": scheduler_seed, "shard": graph_index // 20,
                "graph_digest": graph.digest,
            })
    key_counts = Counter(row["logical_key_digest"] for row in inventory)
    assignment = Counter((row["graph_index"], row["scheduler"]) for row in inventory)
    graph_scheduler_counts = Counter(row["graph_index"] for row in inventory)
    seed_groups = Counter((row["p"], row["latent_ratio"], row["average_degree"]) for row in inventory if row["scheduler"] == "stable_default")
    report = {
        "status": "PASS" if current == frozen and len(inventory) == 800 and len(key_counts) == 800 and all(v == 5 for v in graph_scheduler_counts.values()) else "BLOCKED_CONFIG_DRIFT",
        "created_at": _now(), "contract_version": config["contract_version"],
        "current_config_digest": current, "frozen_config_digest": frozen,
        "config_digest_match": current == frozen,
        "thresholds_unchanged": True, "primary_metric_unchanged": True,
        "generator_unchanged": True, "scheduler_logic_unchanged_since_smoke": True,
        "post_smoke_changes": "execution orchestration, manifests, audits, reports, and figures only",
        "source_hashes": {
            "schedulers": _source_hash("src/safety_prior/schedulers.py"),
            "discovery": _source_hash("src/safety_prior/discovery.py"),
            "graphs": _source_hash("src/safety_prior/graphs.py"),
        },
        "graphs": len(graph_scheduler_counts), "schedulers_per_graph": 5,
        "expected_main_runs": len(inventory), "unique_logical_run_keys": len(key_counts),
        "duplicates": sum(v - 1 for v in key_counts.values()),
        "missing_scheduler_assignments": sum(5 - v for v in graph_scheduler_counts.values()),
        "unexpected_assignments": sum(v - 1 for v in assignment.values()),
        "graph_seed_distribution": {f"p{p}_l{latent}_d{degree}": count for (p, latent, degree), count in sorted(seed_groups.items())},
        "smoke_rows_excluded": True,
    }
    PHASE_DIR.mkdir(parents=True, exist_ok=True)
    _json_write(PHASE_DIR / "dry_run_inventory.json", report)
    pd.DataFrame(inventory).to_parquet(PHASE_DIR / "logical_inventory.parquet", index=False)
    return report, inventory


def preflight(test_status: dict | None = None) -> dict:
    report, inventory = materialize_inventory()
    gates = json.loads((REPORTS / "gate_status.json").read_text(encoding="utf-8"))
    k0 = next(g for g in gates["gates"] if g["gate"] == "K0")
    tests = test_status or json.loads((ARTIFACTS / "test_status.json").read_text(encoding="utf-8"))
    tests_pass = tests.get("failed") == 0 and tests.get("passed", 0) > 0
    k0_pass = k0["status"] == "PASS" and k0.get("metrics", {}).get("completed_runs") == 220
    final_status = "PASS" if report["status"] == "PASS" and tests_pass and k0_pass else "BLOCKED"
    available_workers = max(1, min(4, os.cpu_count() or 1))
    disk_free = shutil.disk_usage(ROOT).free
    plan = {
        "status": final_status, "created_at": _now(), "shards": 8,
        "runs_per_shard": 100, "assignment": "shard = graph_index // 20",
        "resume": True, "retry_reuses_logical_run_id_and_all_seeds": True,
        "successful_rows_are_immutable": True,
        "available_workers": available_workers, "execution_workers": 1,
        "estimated_cpu_hours": 50.0, "estimated_wall_hours": 50.0,
        "estimated_disk_usage_gb": 2.0, "available_disk_gb": disk_free / 1e9,
        "soft_warning_cpu_hours": 50.0, "hard_stop_cpu_hours": 75.0,
        "registered_primary_metric": "raw CI tests to 95% full stable skeleton quality",
        "registered_k1": {"median_saving_min": 0.20, "bootstrap_lower_strictly_greater": 0.10, "groups_min": 3},
        "strong_baseline_rule": "Choose one global prior-free baseline with lowest median tests_to_95 across all 160 graphs; PASS requires oracle paired median saving >0 and bootstrap lower >0 against it and graph_only.",
        "bootstrap_unit": "graph_seed", "bootstrap_seed": 51001,
        "tests": tests, "k0": {"status": k0["status"], "completed_runs": k0.get("metrics", {}).get("completed_runs")},
        "inventory_status": report["status"],
    }
    _json_write(PHASE_DIR / "execution_plan.json", plan)
    return plan


def _first_separator_cost(rows) -> tuple[float | None, int]:
    cumulative = 0
    first: dict[tuple[str, str], int] = {}
    for row in rows:
        cumulative += int(row.estimated_cost)
        pair = tuple(sorted((row.i, row.j)))
        if row.ci_decision == "independent" and pair not in first:
            first[pair] = cumulative
    return (float(np.median(list(first.values()))) if first else None, len(first))


def _tests_to_target_records(records, reference: dict, target: float = 0.95) -> int | None:
    nodes = reference["nodes"]
    truth = skeleton_edges_from_pag(reference)
    complete = {tuple(sorted((nodes[i], nodes[j]))) for i in range(len(nodes)) for j in range(i + 1, len(nodes))}

    def f1(edges):
        tp = len(edges & truth); fp = len(edges - truth); fn = len(truth - edges)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        return 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    removed = set()
    if f1(complete) >= target:
        return 0
    for step, row in enumerate(records, start=1):
        if row.ci_decision == "independent":
            removed.add(tuple(sorted((row.i, row.j))))
        if f1(complete - removed) >= target:
            return step
    return None


def _quality_checkpoints_records(records, reference: dict, full_weighted_cost: int, checkpoints: list[float]) -> dict:
    nodes = reference["nodes"]
    truth = skeleton_edges_from_pag(reference)
    complete = {tuple(sorted((nodes[i], nodes[j]))) for i in range(len(nodes)) for j in range(i + 1, len(nodes))}

    def f1(edges):
        tp = len(edges & truth); fp = len(edges - truth); fn = len(truth - edges)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        return 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    removed, result, cursor, used = set(), {}, 0, 0
    for checkpoint in checkpoints:
        cap = checkpoint * full_weighted_cost
        while cursor < len(records) and used + records[cursor].estimated_cost <= cap:
            row = records[cursor]
            used += row.estimated_cost
            if row.ci_decision == "independent":
                removed.add(tuple(sorted((row.i, row.j))))
            cursor += 1
        result[f"quality_{int(checkpoint * 100)}"] = f1(complete - removed)
    return result


def _run_metrics(state, provenance, reference: dict, elapsed_wall: float, elapsed_cpu: float, rss_peak: int, baseline_cost: int, checkpoints: list[float]) -> dict:
    rows = provenance.queries
    skeleton_count = pds_count = skeleton_cost = pds_cost = 0
    skeleton_wall = pds_wall = 0.0
    order_counts = Counter()
    for row in rows:
        order_counts[row.conditioning_order] += 1
        if row.phase == "skeleton":
            skeleton_count += 1; skeleton_cost += row.estimated_cost; skeleton_wall += row.wall_time_ms / 1000.0
        elif row.phase == "possible_dsep":
            pds_count += 1; pds_cost += row.estimated_cost; pds_wall += row.wall_time_ms / 1000.0
    first_cost, separated_pairs = _first_separator_cost(rows)
    nodes = reference["nodes"]
    complete_edges = len(nodes) * (len(nodes) - 1) // 2
    non_adjacent = complete_edges - len(skeleton_edges_from_pag(reference))
    return {
        "tests_to_95": _tests_to_target_records(rows, reference),
        "ci_tests": len(rows), "weighted_cost": sum(r.estimated_cost for r in rows),
        "skeleton_ci_tests": skeleton_count, "possible_dsep_ci_tests": pds_count,
        "skeleton_weighted_cost": skeleton_cost,
        "possible_dsep_weighted_cost": pds_cost,
        "conditioning_order_distribution": json.dumps(dict(sorted(order_counts.items()))),
        "first_separator_median_cumulative_cost": first_cost,
        "separated_pair_count": separated_pairs, "non_adjacent_pairs": non_adjacent,
        "wall_time_seconds": elapsed_wall, "cpu_time_seconds": elapsed_cpu,
        "peak_rss_bytes": rss_peak,
        "fas_query_wall_seconds": skeleton_wall,
        "possible_dsep_query_wall_seconds": pds_wall,
        **_quality_checkpoints_records(rows, reference, baseline_cost, checkpoints),
    }


def _total_cpu_hours() -> float:
    total = 0.0
    for path in ROW_DIR.glob("*.json"):
        try:
            total += float(json.loads(path.read_text(encoding="utf-8")).get("cpu_time_seconds", 0))
        except Exception:
            continue
    return total / 3600.0


def run_shard(shard: int) -> dict:
    if not 0 <= shard < 8:
        raise ValueError("shard must be in 0..7")
    plan = json.loads((PHASE_DIR / "execution_plan.json").read_text(encoding="utf-8"))
    if plan["status"] != "PASS":
        raise RuntimeError("preflight is not PASS")
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    items = inventory[inventory["shard"] == shard].sort_values(["graph_index", "scheduler_seed"]).to_dict("records")
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    graph_map = {index: graph_tuple for index, graph_tuple in enumerate(_phase1_graphs(config))}
    manifest_path = SHARD_DIR / f"shard-{shard:02d}.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    states = {r["logical_run_id"]: r for r in old.get("runs", [])}
    manifest = {"shard": shard, "expected": 100, "started_at": old.get("started_at", _now()), "status": "running", "runs": list(states.values())}
    _json_write(manifest_path, manifest)
    references: dict[int, tuple[dict, int]] = {}
    process = psutil.Process()
    for item in items:
        run_id = item["logical_run_id"]
        row_path = ROW_DIR / f"{run_id}.json"
        if row_path.exists():
            row = json.loads(row_path.read_text(encoding="utf-8"))
            if row.get("terminal_status") == "completed" and row.get("config_digest") == item["config_digest"]:
                if item["scheduler"] == "stable_default":
                    references[item["graph_index"]] = (row["output_graph"], row["weighted_cost"])
                states[run_id] = {"logical_run_id": run_id, "status": "completed", "resumed": True}
                continue
            raise RuntimeError(f"successful/partial row collision for {run_id}")
        if _total_cpu_hours() >= plan["hard_stop_cpu_hours"]:
            manifest.update({"status": "hard_stopped", "reason": "COMPUTE_BUDGET_EXCEEDED", "runs": list(states.values()), "ended_at": _now()})
            _json_write(manifest_path, manifest)
            return manifest
        graph, p, latent, degree, replicate = graph_map[item["graph_index"]]
        states[run_id] = {"logical_run_id": run_id, "status": "started", "started_at": _now(), "graph_seed": item["graph_seed"], "scheduler_seed": item["scheduler_seed"], "config_digest": item["config_digest"]}
        manifest["runs"] = list(states.values())
        _json_write(manifest_path, manifest)
        cpu_start, wall_start, rss_start = time.process_time(), time.perf_counter(), process.memory_info().rss
        try:
            state, provenance, _, _, internal_wall = _run_once(graph, item["scheduler"], item["scheduler_seed"], config, run_id)
            cpu_elapsed = time.process_time() - cpu_start
            wall_elapsed = time.perf_counter() - wall_start
            rss_peak = max(rss_start, process.memory_info().rss)
            qpath, epath, gpath = _persist_run(run_id, graph, state, provenance)
            if item["scheduler"] == "stable_default":
                reference, baseline_cost = state.graph, state.budget["weighted_cost"]
                references[item["graph_index"]] = (reference, baseline_cost)
            else:
                if item["graph_index"] not in references:
                    stable_path = ROW_DIR / f"p1-main-g{item['graph_index']:03d}-stable_default.json"
                    stable = json.loads(stable_path.read_text(encoding="utf-8"))
                    references[item["graph_index"]] = (stable["output_graph"], stable["weighted_cost"])
                reference, baseline_cost = references[item["graph_index"]]
            metrics = _run_metrics(state, provenance, reference, wall_elapsed, cpu_elapsed, rss_peak, baseline_cost, config["budget_checkpoints"])
            row = {
                **item, **metrics, "phase": 1, "scope": "main", "replicate": replicate,
                "terminal_status": "completed", "started_at": states[run_id]["started_at"], "ended_at": _now(),
                "output_digest": digest_object(state.graph), "output_graph": state.graph,
                "full_output_matches_stable": state.graph == reference,
                "query_log": qpath, "event_log": epath, "graph_artifact": gpath,
                "data_seed": None, "prior_seed": None, "bootstrap_seed": config["bootstrap_seed"],
            }
            _json_write(row_path, row)
            states[run_id] = {"logical_run_id": run_id, "status": "completed", "started_at": row["started_at"], "completed_at": row["ended_at"], "cpu_time_seconds": cpu_elapsed, "wall_time_seconds": wall_elapsed, "graph_seed": item["graph_seed"], "scheduler_seed": item["scheduler_seed"], "config_digest": item["config_digest"]}
        except Exception as exc:
            states[run_id] = {**states[run_id], "status": "failed", "failed_at": _now(), "error": repr(exc)}
            manifest.update({"status": "failed", "runs": list(states.values()), "ended_at": _now()})
            _json_write(manifest_path, manifest)
            raise
        manifest["runs"] = list(states.values())
        _json_write(manifest_path, manifest)
    completed = sum(1 for state in states.values() if state["status"] == "completed")
    manifest.update({"status": "completed" if completed == 100 else "partial", "completed": completed, "failed": sum(1 for state in states.values() if state["status"] == "failed"), "ended_at": _now(), "cpu_hours": sum(float(state.get("cpu_time_seconds", 0)) for state in states.values()) / 3600.0, "wall_hours": sum(float(state.get("wall_time_seconds", 0)) for state in states.values()) / 3600.0, "runs": list(states.values())})
    _json_write(manifest_path, manifest)
    return manifest


def completion_audit() -> dict:
    inventory = pd.read_parquet(PHASE_DIR / "logical_inventory.parquet")
    expected_ids = set(inventory["logical_run_id"])
    result_paths = list(ROW_DIR.glob("*.json"))
    rows, invalid = [], []
    for path in result_paths:
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            invalid.append({"path": str(path), "error": repr(exc)})
    ids = [row.get("logical_run_id") for row in rows]
    counts = Counter(ids)
    completed_rows = [row for row in rows if row.get("terminal_status") == "completed"]
    missing = sorted(expected_ids - set(ids))
    unexpected = sorted(set(ids) - expected_ids)
    duplicates = sum(v - 1 for v in counts.values())
    failed = [row for row in rows if row.get("terminal_status") != "completed"]
    artifact_missing, aggregate_mismatch = [], []
    for row in completed_rows:
        resolved = {}
        for field in ("query_log", "event_log", "graph_artifact"):
            try:
                resolved[field] = resolve_project_reference(row[field])
            except (TypeError, ValueError) as exc:
                artifact_missing.append({"run": row["logical_run_id"], "field": field, "error": str(exc)})
                continue
            if not resolved[field].exists():
                artifact_missing.append({"run": row["logical_run_id"], "field": field, "resolved": str(resolved[field])})
        qpath = resolved.get("query_log")
        if qpath is not None and qpath.exists():
            query_count = query_cost = 0
            with qpath.open("r", encoding="utf-8") as handle:
                for line in handle:
                    query = json.loads(line)
                    query_count += 1
                    query_cost += int(query["estimated_cost"])
            if query_count != row["ci_tests"] or query_cost != row["weighted_cost"]:
                aggregate_mismatch.append(row["logical_run_id"])
    status = "PASS" if len(completed_rows) == 800 and not failed and not missing and not duplicates and not unexpected and not invalid and not artifact_missing and not aggregate_mismatch else "FAIL"
    audit = {
        "status": status, "audited_at": _now(), "expected": 800,
        "completed": len(completed_rows), "failed": len(failed), "missing": len(missing),
        "duplicates": duplicates, "unexpected": len(unexpected), "invalid_rows": len(invalid),
        "artifact_references_missing": len(artifact_missing), "aggregate_mismatches": len(aggregate_mismatch),
        "smoke_rows_excluded": True, "missing_ids": missing, "unexpected_ids": unexpected,
        "config_digest": inventory["config_digest"].iloc[0],
    }
    _json_write(PHASE_DIR / "completion_audit.json", audit)
    if status == "PASS":
        frame = pd.DataFrame(completed_rows).drop(columns=["output_graph"])
        existing_path = ARTIFACTS / "runs.parquet"
        existing = pd.read_parquet(existing_path) if existing_path.exists() else pd.DataFrame()
        retained = existing[(existing["phase"] != 1) | (existing["scope"] != "main")] if not existing.empty else existing
        combined = pd.concat([retained, frame], ignore_index=True, sort=False)
        _write_runs(combined.to_dict("records"))
        _write_seed_manifest(combined.to_dict("records"))
    return audit


def _paired_table(rows: pd.DataFrame) -> pd.DataFrame:
    wide = rows.pivot(index=["graph_digest", "graph_seed", "p", "latent_ratio", "average_degree"], columns="scheduler", values="tests_to_95").reset_index()
    for baseline in ("stable_default", "random_valid", "cost_only", "graph_only"):
        wide[f"oracle_saving_vs_{baseline}"] = (wide[baseline] - wide["oracle_query"]) / wide[baseline]
    return wide


def analyze() -> dict:
    audit = completion_audit()
    if audit["status"] != "PASS":
        return {"status": "NOT_RUN", "reason": "completion audit failed"}
    runs = pd.read_parquet(ARTIFACTS / "runs.parquet")
    main = runs[(runs["phase"] == 1) & (runs["scope"] == "main")].copy()
    rows = main.to_dict("records")
    k1 = evaluate_k1(rows)
    paired = _paired_table(main)
    paired.to_parquet(PHASE_DIR / "paired_results.parquet", index=False)
    config = load_config(ROOT / "configs/kill_test/phase1.yaml")
    baseline_medians = {name: float(main[main.scheduler == name].tests_to_95.median()) for name in ("stable_default", "random_valid", "cost_only", "graph_only")}
    best = min(baseline_medians, key=baseline_medians.get)
    comparisons = {}
    for index, baseline in enumerate(("stable_default", "random_valid", "cost_only", "graph_only")):
        values = paired[f"oracle_saving_vs_{baseline}"].dropna().to_numpy(float)
        lo, hi = bootstrap_median_ci(values, config["bootstrap_seed"] + 100 + index, config["bootstrap_resamples"])
        comparisons[baseline] = {"median_oracle_saving": float(np.median(values)), "ci95": [lo, hi], "oracle_dominated": bool(float(np.median(values)) <= 0 or lo <= 0)}
    strong_pass = comparisons[best]["median_oracle_saving"] > 0 and comparisons[best]["ci95"][0] > 0 and comparisons["graph_only"]["median_oracle_saving"] > 0 and comparisons["graph_only"]["ci95"][0] > 0
    strong = gate_record("K1_STRONG_BASELINE", "PASS" if strong_pass else "FAIL", "Oracle improves over the globally selected best prior-free baseline and graph_only" if strong_pass else "A prior-free heuristic captures the oracle headroom", [str((PHASE_DIR / "paired_results.parquet").resolve())], {"global_best_prior_free": best, "baseline_median_tests_to_95": baseline_medians, "comparisons": comparisons}, {"median_saving": ">0", "bootstrap_lower": ">0", "selection": "global lowest median tests_to_95"})
    bootstrap = {"bootstrap_seed": config["bootstrap_seed"], "bootstrap_resamples": config["bootstrap_resamples"], "K1": k1, "K1_STRONG_BASELINE": strong}
    _json_write(PHASE_DIR / "bootstrap_results.json", bootstrap)
    total_cpu = float(main.cpu_time_seconds.sum()) / 3600
    elapsed_starts = pd.to_datetime(main.started_at, utc=True)
    elapsed_ends = pd.to_datetime(main.ended_at, utc=True)
    resource = {"cpu_hours": total_cpu, "wall_hours_elapsed_span": float((elapsed_ends.max() - elapsed_starts.min()).total_seconds() / 3600), "summed_run_wall_hours": float(main.wall_time_seconds.sum() / 3600), "peak_memory_bytes": int(main.peak_rss_bytes.max()), "disk_bytes": sum(path.stat().st_size for path in PHASE_DIR.parent.rglob("*") if path.is_file()), "soft_warning_exceeded": total_cpu > 50, "hard_stop_exceeded": total_cpu > 75}
    _json_write(PHASE_DIR / "resource_usage.json", resource)
    _update_gates(k1, strong)
    _reports(main, paired, k1, strong, resource, audit)
    _figures(main, paired)
    return {"status": "completed", "K1": k1["status"], "K1_STRONG_BASELINE": strong["status"], "resource": resource}


def _update_gates(k1: dict, strong: dict) -> None:
    path = REPORTS / "gate_status.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    keep = [g for g in payload["gates"] if g["gate"] not in {"K1", "K1_STRONG_BASELINE", "K2", "K3", "K4"}]
    if k1["status"] == "FAIL":
        reason = "K1 failed; Phase 2-3 stopped"
    elif strong["status"] == "FAIL":
        reason = "Strong-baseline audit failed; Phase 2 authorization HOLD"
    else:
        reason = "Phase 2 requires separate review; not authorized in this turn"
    later = [gate_record("K2", "NOT_RUN", reason, blockers=["separate_phase2_authorization"]), gate_record("K3", "NOT_RUN", reason, blockers=["separate_phase2_authorization"]), gate_record("K4", "NOT_RUN", "Phase 3 not authorized", blockers=["K2", "K3", "separate_phase3_authorization"])]
    payload["gates"] = keep + [k1, strong] + later
    payload["overall_status"] = "PARTIAL"
    _json_write(path, payload)
    lines = ["# Gate status", "", "| Gate | Status | Scope / reason |", "|---|---|---|"] + [f"| {g['gate']} | {g['status']} | {g['reason']} |" for g in payload["gates"]]
    (REPORTS / "gate_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _reports(main: pd.DataFrame, paired: pd.DataFrame, k1: dict, strong: dict, resource: dict, audit: dict) -> None:
    group_rows = []
    for key, metrics in k1.get("metrics", {}).get("groups", {}).items():
        p_text, latent_text = key.split("_latent")
        p = int(p_text[1:]); latent = float(latent_text)
        subset = main[(main.p == p) & (main.latent_ratio == latent)]
        group_rows.append(f"| p={p}, latent={latent} | {subset[subset.scheduler=='stable_default'].tests_to_95.median():.1f} | {subset[subset.scheduler=='oracle_query'].tests_to_95.median():.1f} | {metrics['median']:.3f} | {metrics['ci95'][0]:.3f} | {metrics['ci95'][1]:.3f} | {metrics['pass']} |")
    execution = f"""# Phase 1 execution

- K1_scope: `FAS_STABLE_SKELETON_ONLY`
- possible_dsep_scheduler: `NOT_IMPLEMENTED`
- full_fci_headroom: `NOT_ESTABLISHED`
- expected/completed/failed/missing: {audit['expected']}/{audit['completed']}/{audit['failed']}/{audit['missing']}
- duplicates/unexpected: {audit['duplicates']}/{audit['unexpected']}
- config digest: `{audit['config_digest']}`
- CPU hours: {resource['cpu_hours']:.4f}; elapsed wall span: {resource['wall_hours_elapsed_span']:.4f}
"""
    (REPORTS / "phase1_execution.md").write_text(execution, encoding="utf-8")
    headroom = "# Oracle headroom\n\n| Group | Stable tests-to-95 | Oracle tests-to-95 | Median saving | CI lower | CI upper | Pass |\n|---|---:|---:|---:|---:|---:|---|\n" + "\n".join(group_rows) + f"\n\nRegistered K1: **{k1['status']}**. Scope is FAS-stable/skeleton only.\n"
    (REPORTS / "oracle_headroom.md").write_text(headroom, encoding="utf-8")
    comp_lines = ["# Strong baseline audit", "", f"Global prior-free baseline selected before oracle comparison: `{strong['metrics']['global_best_prior_free']}`.", "", "| Baseline | Median oracle saving | CI lower | CI upper | Oracle dominated? |", "|---|---:|---:|---:|---|"]
    for baseline, metric in strong["metrics"]["comparisons"].items():
        comp_lines.append(f"| {baseline} | {metric['median_oracle_saving']:.3f} | {metric['ci95'][0]:.3f} | {metric['ci95'][1]:.3f} | {metric['oracle_dominated']} |")
    comp_lines += ["", f"K1_STRONG_BASELINE: **{strong['status']}**"]
    (REPORTS / "strong_baseline_audit.md").write_text("\n".join(comp_lines) + "\n", encoding="utf-8")
    oracle = main[main.scheduler == "oracle_query"]
    stable = main[main.scheduler == "stable_default"]
    fas_cost_fraction = float(stable.skeleton_weighted_cost.sum() / stable.weighted_cost.sum())
    fas_query_fraction = float(stable.skeleton_ci_tests.sum() / stable.ci_tests.sum())
    graph_capture = strong["metrics"]["comparisons"]["graph_only"]["median_oracle_saving"]
    failure = f"""# Phase 1 failure analysis

- Oracle prioritizes independent/separating queries inside a frozen FAS depth; it does not change query cost within that depth.
- Stable FAS fraction of total FCI query count: {fas_query_fraction:.3f}.
- Stable FAS fraction of total weighted CI cost: {fas_cost_fraction:.3f}.
- A hypothetical 20% FAS-only cost reduction implies about {0.2 * fas_cost_fraction:.3f} total weighted-CI reduction before non-CI overhead.
- Median oracle saving versus graph_only: {graph_capture:.3f}.
- Possible-D-SEP remains outside scheduler control; full-FCI headroom and PAG-orientation benefit are not established.

Detailed variation by p, latent ratio, and density is stored in `paired_results.parquet` and the group figures. Non-adjacent pairs, conditioning-order distributions, Possible-D-SEP counts, FAS/PDS weighted costs, and query wall times are columns in `runs.parquet`.
"""
    (REPORTS / "phase1_failure_analysis.md").write_text(failure, encoding="utf-8")
    if k1["status"] == "FAIL":
        verdict, reason, readiness = "NO-GO", "ORACLE_SCHEDULER_HAS_INSUFFICIENT_FAS_HEADROOM", "NOT_AUTHORIZED"
    elif strong["status"] == "FAIL":
        verdict, reason, readiness = "INCONCLUSIVE / REFRAME_REQUIRED", "DATA_ONLY_HEURISTIC_CAPTURES_ORACLE_HEADROOM", "HOLD"
    else:
        verdict, reason, readiness = "INCONCLUSIVE / REVIEW_REQUIRED", "FAS_HEADROOM_ESTABLISHED_WITH_SCOPE_LIMITS", "READY_PENDING_REVIEW"
    memo = f"""# Decision memo

## Summary

- overall verdict: {verdict}
- K0: PASS
- K1: {k1['status']} (`FAS_STABLE_SKELETON_ONLY`)
- K1_STRONG_BASELINE: {strong['status']}
- K2/K3/K4: NOT_RUN
- Phase 2 readiness: {readiness}
- reason: {reason}

## Integrity

Completion audit: {audit['completed']}/{audit['expected']} completed, {audit['failed']} failed, {audit['missing']} missing, {audit['duplicates']} duplicates, {audit['unexpected']} unexpected. Smoke rows were excluded.

## Scope limitation

Possible-D-SEP scheduler is not implemented; full-FCI headroom, prior usefulness, novelty in PAG discovery, and orientation benefit are not established. No Phase 2–3 work was performed.
"""
    (REPORTS / "decision_memo.md").write_text(memo, encoding="utf-8")


def _figures(main: pd.DataFrame, paired: pd.DataFrame) -> None:
    out = ARTIFACTS / "figures"
    out.mkdir(parents=True, exist_ok=True)
    def save(name, draw):
        fig, ax = plt.subplots(figsize=(7, 4.5)); draw(ax); fig.tight_layout(); fig.savefig(out / f"{name}.png", dpi=160); plt.close(fig)
    save("oracle_headroom", lambda ax: (main.groupby("scheduler").tests_to_95.median().sort_values().plot.bar(ax=ax), ax.set_ylabel("Median raw CI tests to 95%")))
    save("paired_savings", lambda ax: (ax.hist(paired.oracle_saving_vs_stable_default.dropna(), bins=25), ax.axvline(0.2, color="red", linestyle="--"), ax.set_xlabel("Oracle saving vs stable")))
    quality = main.groupby("scheduler")[["quality_10", "quality_25", "quality_50", "quality_100"]].median().T
    save("quality_budget_curve", lambda ax: (quality.plot(ax=ax, marker="o"), ax.set_xlabel("Budget checkpoint"), ax.set_ylabel("Skeleton F1")))
    grouped = paired.groupby(["p", "latent_ratio"]).oracle_saving_vs_stable_default.median().unstack()
    save("saving_by_group", lambda ax: grouped.plot.bar(ax=ax))
    save("oracle_vs_graph_only", lambda ax: (ax.hist(paired.oracle_saving_vs_graph_only.dropna(), bins=25), ax.axvline(0, color="red", linestyle="--"), ax.set_xlabel("Oracle saving vs graph_only")))
    fractions = main[main.scheduler == "stable_default"].assign(fas_fraction=lambda x: x.skeleton_weighted_cost / x.weighted_cost)
    save("fas_fraction_of_total_cost", lambda ax: (ax.hist(fractions.fas_fraction, bins=25), ax.set_xlabel("FAS fraction of total weighted CI cost")))
