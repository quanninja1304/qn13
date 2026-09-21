from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
import psutil
import yaml
from causallearn.search.ConstraintBased.FCI import fci as upstream_fci

from .ci import OracleCI
from .discovery import run_scheduled_fci
from .gates import evaluate_k0, evaluate_k1, gate_record
from .graphs import GeneratedGraph, canonical_dag, canonical_pag, digest_object, dummy_data, generate_dag, motif_graph, pag_digest
from .metrics import query_signature, skeleton_metrics, tests_to_skeleton_target
from .schedulers import make_scheduler


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "kill_test"
REPORTS = ROOT / "reports" / "kill_test"
LEGACY_PROJECT_ROOTS = (
    "D:/REsearch/causal multi-agent/safety_prior",
)


def canonical_project_reference(path: str | Path) -> str:
    """Return a portable project-relative reference without touching the file."""
    raw = str(path).replace("\\", "/")
    root_text = ROOT.resolve().as_posix().rstrip("/")
    relative: str | None = None
    if raw.casefold() == root_text.casefold():
        relative = ""
    elif raw.casefold().startswith(root_text.casefold() + "/"):
        relative = raw[len(root_text) + 1 :]
    else:
        for legacy_root in LEGACY_PROJECT_ROOTS:
            prefix = legacy_root.rstrip("/")
            if raw.casefold().startswith(prefix.casefold() + "/"):
                relative = raw[len(prefix) + 1 :]
                break
    if relative is None:
        candidate = Path(path)
        if candidate.is_absolute():
            raise ValueError(f"artifact path is outside known project roots: {path}")
        relative = raw
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe project-relative artifact path: {path}")
    return pure.as_posix()


def resolve_project_reference(path: str | Path) -> Path:
    """Resolve current relative and legacy Windows references under this checkout."""
    relative = canonical_project_reference(path)
    candidate = (ROOT / Path(*PurePosixPath(relative).parts)).resolve()
    candidate.relative_to(ROOT.resolve())
    return candidate


def load_config(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNAVAILABLE_NOT_A_GIT_REPOSITORY"


def write_environment() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    packages = {}
    for name in ("causal-learn", "networkx", "numpy", "pandas", "pyarrow", "scipy", "scikit-learn", "PyYAML", "pytest"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    payload = {"python": sys.version, "platform": platform.platform(), "cpu_count": os.cpu_count(), "memory_bytes": psutil.virtual_memory().total, "packages": packages, "code_revision": _revision()}
    (ARTIFACTS / "environment.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_config_digests() -> None:
    entries = {}
    for path in sorted((ROOT / "configs" / "kill_test").glob("*.yaml")):
        entries[str(path.relative_to(ROOT))] = digest_object(load_config(path))
    (ARTIFACTS / "config_digest.json").write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


def phase0_graphs(config: dict) -> list[GeneratedGraph]:
    motif_names = ["chain", "fork", "collider", "collider_descendant", "latent_confounder", "latent_mediator", "two_paths", "minimal_separator_two"]
    graphs = []
    start = int(config["graph_seed_start"])
    for index, name in enumerate(motif_names[: int(config["graphs"])]):
        graphs.append(replace(motif_graph(name), graph_seed=start + index))
    for index in range(len(graphs), int(config["graphs"])):
        seed = start + index
        graphs.append(generate_dag(int(config["observed_nodes"]), float(config["latent_ratio"]), float(config["mean_degree"]), seed))
    return graphs


def _upstream_reference(graph: GeneratedGraph, alpha: float, depth: int, max_path_length: int):
    names = [f"X{i + 1}" for i in graph.observed]
    result, _ = upstream_fci(dummy_data(len(names)), independence_test_method="d_separation", alpha=float(alpha), depth=int(depth), max_path_length=int(max_path_length), show_progress=False, node_names=names, true_dag=graph.dag)
    return result


def _run_once(graph: GeneratedGraph, scheduler_name: str, scheduler_seed: int, config: dict, run_id: str):
    names = [f"X{i + 1}" for i in graph.observed]
    ci = OracleCI(graph.dag, graph.observed)
    scheduler = make_scheduler(scheduler_name, scheduler_seed, ci if scheduler_name == "oracle_query" else None)
    started = time.perf_counter()
    state, provenance, output = run_scheduled_fci(run_id, names, ci, scheduler, scheduler_seed, graph.graph_seed, alpha=float(config.get("alpha", 0.05)), depth=int(config.get("depth", -1)), max_path_length=int(config.get("max_path_length", -1)))
    elapsed = time.perf_counter() - started
    logical = [
        (q.phase, q.i, q.j, tuple(q.conditioning_set))
        for q in provenance.queries
    ]
    return state, provenance, output, logical, elapsed


def _validate_dependencies(rows: list[dict]) -> bool:
    phases = [row["phase"] for row in rows]
    if "skeleton" in phases and "possible_dsep" in phases and phases.index("possible_dsep") < len([p for p in phases if p == "skeleton"]):
        return False
    depths = [row["conditioning_order"] for row in rows if row["phase"] == "skeleton"]
    return depths == sorted(depths)


def _persist_run(run_id: str, graph: GeneratedGraph, state, provenance) -> tuple[str, str, str]:
    qpath = ARTIFACTS / "query_logs" / f"{run_id}.jsonl"
    epath = ARTIFACTS / "graph_events" / f"{run_id}.jsonl"
    provenance.write(qpath, epath)
    gpath = ARTIFACTS / "graphs" / f"{graph.digest}.json"
    gpath.parent.mkdir(parents=True, exist_ok=True)
    if not gpath.exists():
        gpath.write_text(json.dumps({"graph_seed": graph.graph_seed, "parameters": graph.parameters, "canonical": canonical_dag(graph.dag, graph.observed, graph.latent), "digest": graph.digest}, indent=2, sort_keys=True), encoding="utf-8")
    return (
        canonical_project_reference(qpath),
        canonical_project_reference(epath),
        canonical_project_reference(gpath),
    )


def _write_seed_manifest(rows: list[dict]) -> None:
    fields = ["run_id", "phase", "graph_seed", "data_seed", "prior_seed", "scheduler_seed", "bootstrap_seed"]
    pd.DataFrame([{key: row.get(key) for key in fields} for row in rows]).to_csv(ARTIFACTS / "seed_manifest.csv", index=False)


def _write_runs(rows: list[dict]) -> None:
    pd.DataFrame(rows).to_parquet(ARTIFACTS / "runs.parquet", index=False)


def run_phase0(config_path: str | Path, smoke: bool = False) -> list[dict]:
    config = load_config(config_path)
    if smoke:
        config = dict(config, graphs=2, random_schedules_per_graph=2, scope="smoke")
    write_environment()
    write_config_digests()
    rows = []
    failures_dir = ARTIFACTS / "failures"
    failures_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    for graph_index, graph in enumerate(phase0_graphs(config)):
        upstream_graph = _upstream_reference(graph, config["alpha"], config["depth"], config["max_path_length"])
        upstream_canonical = canonical_pag(upstream_graph)
        stable_seed = int(config["scheduler_seed_start"]) + graph_index * 100
        stable_id = f"p0-g{graph_index:02d}-stable"
        stable_state, stable_prov, stable_graph, stable_logical, elapsed = _run_once(graph, "stable_default", stable_seed, config, stable_id)
        replay_state, replay_prov, _, replay_logical, _ = _run_once(graph, "stable_default", stable_seed, config, stable_id + "-replay")
        query_path, event_path, graph_path = _persist_run(stable_id, graph, stable_state, stable_prov)
        wrapper_match = stable_state.graph == upstream_canonical
        stable_replay = stable_state.graph == replay_state.graph and stable_logical == replay_logical
        stable_signatures = Counter(stable_logical)
        base_row = {
            "run_id": stable_id, "phase": 0, "scope": config.get("scope", "main"), "graph_index": graph_index,
            "graph_seed": graph.graph_seed, "data_seed": None, "prior_seed": None, "scheduler_seed": stable_seed, "bootstrap_seed": None,
            "scheduler": "stable_default", "graph_digest": graph.digest, "output_digest": digest_object(stable_state.graph),
            "ci_tests": len(stable_prov.queries), "weighted_cost": stable_state.budget["weighted_cost"], "wall_time_seconds": elapsed,
            "matches_stable": wrapper_match, "matches_upstream": wrapper_match, "query_set_matches_stable": True,
            "scheduler_eligible": True, "dependencies_respected": _validate_dependencies([q.as_dict() for q in stable_prov.queries]),
            "prior_not_graph_evidence": all(not e["prior_is_evidence"] for e in stable_prov.graph_events), "deterministic_replay": stable_replay,
            "query_log": query_path, "event_log": event_path, "graph_artifact": graph_path,
        }
        rows.append(base_row)
        if not wrapper_match:
            (failures_dir / f"{stable_id}.json").write_text(json.dumps({"upstream": upstream_canonical, "adapter": stable_state.graph}, indent=2), encoding="utf-8")
        for schedule_index in range(int(config["random_schedules_per_graph"])):
            seed = stable_seed + schedule_index + 1
            run_id = f"p0-g{graph_index:02d}-random-{schedule_index:02d}"
            state, prov, _, logical, elapsed = _run_once(graph, "random_valid", seed, config, run_id)
            replay_state, _, _, replay_logical, _ = _run_once(graph, "random_valid", seed, config, run_id + "-replay")
            qpath, epath, gpath = _persist_run(run_id, graph, state, prov)
            rows.append({
                "run_id": run_id, "phase": 0, "scope": config.get("scope", "main"), "graph_index": graph_index,
                "graph_seed": graph.graph_seed, "data_seed": None, "prior_seed": None, "scheduler_seed": seed, "bootstrap_seed": None,
                "scheduler": "random_valid", "graph_digest": graph.digest, "output_digest": digest_object(state.graph),
                "ci_tests": len(prov.queries), "weighted_cost": state.budget["weighted_cost"], "wall_time_seconds": elapsed,
                "matches_stable": state.graph == stable_state.graph, "matches_upstream": state.graph == upstream_canonical,
                "query_set_matches_stable": Counter(logical) == stable_signatures,
                "scheduler_eligible": True, "dependencies_respected": _validate_dependencies([q.as_dict() for q in prov.queries]),
                "prior_not_graph_evidence": all(not e["prior_is_evidence"] for e in prov.graph_events),
                "deterministic_replay": state.graph == replay_state.graph and logical == replay_logical,
                "query_log": qpath, "event_log": epath, "graph_artifact": gpath,
            })
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    runs_path = ARTIFACTS / "runs.parquet"
    existing = pd.read_parquet(runs_path).to_dict("records") if runs_path.exists() else []
    scope = config.get("scope", "main")
    retained = [row for row in existing if row.get("phase") != 0 or row.get("scope") != scope]
    combined = retained + rows
    _write_seed_manifest(combined)
    _write_runs(combined)
    execution = {"contract_version": config["contract_version"], "phase": 0, "scope": scope, "config_digest": digest_object(config), "code_revision": _revision(), "started_at": started_at, "ended_at": datetime.now(timezone.utc).isoformat(), "status": "completed_smoke" if smoke else "completed", "expected_runs": len(rows), "completed_runs": len(rows), "artifact_paths": [str(runs_path.resolve())]}
    manifest_path = ARTIFACTS / "run_manifest.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    executions = old.get("executions", []) if isinstance(old, dict) else []
    if old and not executions:
        executions = [old]
    executions = [entry for entry in executions if not (entry.get("phase") == 0 and entry.get("scope") == scope)] + [execution]
    manifest_path.write_text(json.dumps({"contract_version": "1.0.0", "code_revision": _revision(), "executions": executions}, indent=2, sort_keys=True), encoding="utf-8")
    return rows


def _phase1_graphs(config: dict):
    counter = 0
    for p in config["observed_nodes"]:
        for latent in config["latent_ratios"]:
            for degree in config["mean_degrees"]:
                for replicate in range(config["graph_seeds_per_cell"]):
                    seed = config["graph_seed_start"] + counter
                    counter += 1
                    yield generate_dag(int(p), float(latent), float(degree), int(seed)), p, latent, degree, replicate


def _quality_checkpoints(query_rows: list[dict], reference_pag: dict, full_weighted_cost: int, checkpoints: list[float]) -> dict:
    nodes = reference_pag["nodes"]
    complete = {tuple(sorted((nodes[i], nodes[j]))) for i in range(len(nodes)) for j in range(i + 1, len(nodes))}
    removed = set()
    used = 0
    result = {}
    cursor = 0
    for checkpoint in checkpoints:
        cap = checkpoint * full_weighted_cost
        while cursor < len(query_rows) and used + query_rows[cursor]["estimated_cost"] <= cap:
            row = query_rows[cursor]
            used += row["estimated_cost"]
            if row["ci_decision"] == "independent":
                removed.add(tuple(sorted((row["i"], row["j"]))))
            cursor += 1
        predicted = {"nodes": nodes, "endpoint_matrix": [[0] * len(nodes) for _ in nodes], "is_pag": False}
        index = {node: i for i, node in enumerate(nodes)}
        for a, b in complete - removed:
            i, j = index[a], index[b]
            predicted["endpoint_matrix"][i][j] = predicted["endpoint_matrix"][j][i] = 2
        result[f"quality_{int(checkpoint * 100)}"] = skeleton_metrics(predicted, reference_pag)["f1"]
    return result


def run_phase1(config_path: str | Path, smoke: bool = False) -> list[dict]:
    config = load_config(config_path)
    gate_path = REPORTS / "gate_status.json"
    gate_payload = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {"gates": []}
    k0 = next((g for g in gate_payload["gates"] if g["gate"] == "K0"), None)
    if not smoke and (not k0 or k0["status"] != "PASS"):
        raise RuntimeError("Phase 1 requires K0 PASS")
    graphs = list(_phase1_graphs(config))
    if smoke:
        graphs = graphs[:2]
        config = dict(config, scope="smoke")
    rows = []
    for graph_index, (graph, p, latent, degree, replicate) in enumerate(graphs):
        per_graph = {}
        base_seed = 60000 + graph_index * 10
        for scheduler_index, scheduler_name in enumerate(config["schedulers"]):
            run_id = f"p1-g{graph_index:03d}-{scheduler_name}"
            state, provenance, _, _, elapsed = _run_once(graph, scheduler_name, base_seed + scheduler_index, config, run_id)
            qpath, epath, gpath = _persist_run(run_id, graph, state, provenance)
            per_graph[scheduler_name] = (state, provenance, qpath, epath, gpath, elapsed, base_seed + scheduler_index)
        reference = per_graph["stable_default"][0].graph
        baseline_cost = per_graph["stable_default"][0].budget["weighted_cost"]
        for scheduler_name, (state, provenance, qpath, epath, gpath, elapsed, seed) in per_graph.items():
            qrows = [q.as_dict() for q in provenance.queries]
            row = {
                "run_id": f"p1-g{graph_index:03d}-{scheduler_name}", "phase": 1, "scope": config.get("scope", "main"),
                "graph_index": graph_index, "graph_seed": graph.graph_seed, "data_seed": None, "prior_seed": None,
                "scheduler_seed": seed, "bootstrap_seed": config["bootstrap_seed"], "scheduler": scheduler_name,
                "graph_digest": graph.digest, "output_digest": digest_object(state.graph), "observed_nodes": p,
                "latent_ratio": latent, "mean_degree": degree, "replicate": replicate,
                "ci_tests": len(qrows), "weighted_cost": state.budget["weighted_cost"], "wall_time_seconds": elapsed,
                "tests_to_95": tests_to_skeleton_target(qrows, reference), "full_output_matches_stable": state.graph == reference,
                "query_log": qpath, "event_log": epath, "graph_artifact": gpath,
            }
            row.update(_quality_checkpoints(qrows, reference, baseline_cost, config["budget_checkpoints"]))
            rows.append(row)
    existing_path = ARTIFACTS / "runs.parquet"
    existing = pd.read_parquet(existing_path).to_dict("records") if existing_path.exists() else []
    retained = [row for row in existing if row.get("phase") != 1 or row.get("scope") != config.get("scope", "main")]
    combined = retained + rows
    _write_runs(combined)
    _write_seed_manifest(combined)
    manifest_path = ARTIFACTS / "run_manifest.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    execution = {"contract_version": config["contract_version"], "phase": 1, "scope": config.get("scope", "main"), "config_digest": digest_object(config), "code_revision": _revision(), "ended_at": datetime.now(timezone.utc).isoformat(), "status": "completed_smoke" if smoke else "completed", "expected_runs": 800 if not smoke else len(rows), "completed_runs": len(rows), "artifact_paths": [str((ARTIFACTS / "runs.parquet").resolve())]}
    executions = old.get("executions", []) if isinstance(old, dict) else []
    if old and not executions:
        executions = [old]
    executions = [entry for entry in executions if not (entry.get("phase") == 1 and entry.get("scope") == execution["scope"])] + [execution]
    manifest_path.write_text(json.dumps({"contract_version": "1.0.0", "code_revision": _revision(), "executions": executions}, indent=2, sort_keys=True), encoding="utf-8")
    return rows


def evaluate_gates() -> list[dict]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    runs_path = ARTIFACTS / "runs.parquet"
    rows = pd.read_parquet(runs_path).to_dict("records") if runs_path.exists() else []
    k0 = evaluate_k0(rows)
    gates = [k0]
    if k0["status"] == "PASS":
        gates.append(evaluate_k1(rows))
    else:
        gates.append(gate_record("K1", "NOT_RUN", "K0 prerequisite is not PASS", blockers=["K0"]))
    gates.extend([
        gate_record("K2", "NOT_RUN", "K1 prerequisite is not PASS", blockers=["K1"]),
        gate_record("K3", "NOT_RUN", "K1 prerequisite is not PASS", blockers=["K1"]),
        gate_record("K4", "NOT_RUN", "K1 prerequisite is not PASS", blockers=["K1", "OI-01", "OI-02"]),
    ])
    payload = {"overall_status": "PARTIAL", "contract_version": "1.0.0", "gates": gates}
    (REPORTS / "gate_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = ["# Gate status", "", "| Gate | Status | Reason |", "|---|---|---|"] + [f"| {g['gate']} | {g['status']} | {g['reason']} |" for g in gates]
    (REPORTS / "gate_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gates


def dry_run(phase: int) -> dict:
    if phase == 0:
        cfg = load_config(ROOT / "configs/kill_test/phase0.yaml")
        graphs, datasets, schedulers, priors, checkpoints = cfg["graphs"], 0, 11, 0, 1
        runs = graphs * schedulers
        cpu_hours, disk_gb = 8.0, 0.2
    elif phase == 1:
        cfg = load_config(ROOT / "configs/kill_test/phase1.yaml")
        graphs = len(cfg["observed_nodes"]) * len(cfg["latent_ratios"]) * len(cfg["mean_degrees"]) * cfg["graph_seeds_per_cell"]
        datasets, schedulers, priors, checkpoints = 0, len(cfg["schedulers"]), 0, len(cfg["budget_checkpoints"])
        runs = graphs * schedulers
        cpu_hours, disk_gb = 50.0, 2.0
    elif phase == 2:
        cfg = load_config(ROOT / "configs/kill_test/phase2.yaml")
        graphs, datasets, schedulers = 160, 0, 1
        priors, checkpoints = len(cfg["priors"]) * len(cfg["error_modes"]) * len(cfg["target_auc"]), 4
        runs, cpu_hours, disk_gb = graphs * priors, 80.0, 5.0
    elif phase == 3:
        cfg = load_config(ROOT / "configs/kill_test/phase3.yaml")
        graphs = cfg["graph_seeds"]
        datasets = graphs * len(cfg["sample_sizes"]) * cfg["data_seeds_per_graph"]
        schedulers, priors, checkpoints = 8, 3, 4
        runs, cpu_hours, disk_gb = datasets * schedulers, 190.0, 10.0
    else:
        raise ValueError("phase must be 0..3")
    return {"phase": phase, "graphs": graphs, "datasets": datasets, "schedulers": schedulers, "prior_modes": priors, "budget_checkpoints": checkpoints, "total_runs": runs, "estimated_cpu_hours": cpu_hours, "estimated_disk_gb": disk_gb}
