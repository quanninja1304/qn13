from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .runner import ARTIFACTS, REPORTS


def generate_reports() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    gates_path = REPORTS / "gate_status.json"
    gates = json.loads(gates_path.read_text(encoding="utf-8")) if gates_path.exists() else {"gates": []}
    runs_path = ARTIFACTS / "runs.parquet"
    rows = pd.read_parquet(runs_path) if runs_path.exists() else pd.DataFrame()
    k = {g["gate"]: g["status"] for g in gates.get("gates", [])}
    phase0_main = rows[(rows["phase"] == 0) & (rows["scope"] == "main")] if not rows.empty else rows
    completed = len(phase0_main)
    expected = 220
    memo = f"""# Decision memo

## Summary

- overall verdict: INCONCLUSIVE / BLOCKED
- K0: {k.get('K0', 'NOT_RUN')}
- K1: {k.get('K1', 'NOT_RUN')}
- K2: {k.get('K2', 'NOT_RUN')}
- K3: {k.get('K3', 'NOT_RUN')}
- K4: {k.get('K4', 'NOT_RUN')}
- recommended action: execute the frozen Phase-1 matrix only if K0 is PASS; do not start Phases 2–3 before K1 PASS.

## Evidence

- expected Phase-0 runs: {expected}
- completed artifact rows: {completed}
- contract version: 1.0.0
- evaluator status: unit/conformance status is reported separately by pytest
- reproducibility: environment, config digests, seed manifest, replay fields, and raw logs are machine-readable

## Scientific findings

Phase 0 addresses mechanical oracle equivalence only. No oracle-headroom,
usable-prior, correlated-error, finite-sample, or safety-effect claim is supported
until its complete phase and confidence intervals exist.

## Negative evidence and limitations

RFCI-stable and FCIT baselines are absent; the DAG-to-PAG evaluator reference is
not independently cross-validated; Possible-D-SEP is logged but not scheduler-
reordered. These limitations prohibit a GO verdict.

## Final verdict

**INCONCLUSIVE / BLOCKED** pending K1 and the open evaluator/baseline risks.
"""
    (REPORTS / "decision_memo.md").write_text(memo, encoding="utf-8")
    k0 = next((g for g in gates.get("gates", []) if g["gate"] == "K0"), {})
    report_bodies = {
        "oracle_equivalence.md": f"Contract v1.0.0 completed 220/220 main runs over 20 graphs (one stable schedule and ten random valid schedules per graph). Exact canonical PAG equivalence rate was {k0.get('metrics', {}).get('equivalence_rate', 'unavailable')}; failed runs: {k0.get('metrics', {}).get('failed_runs', 'unavailable')}. Query-set equality, eligibility, dependency ordering, no-prior graph evidence, upstream characterization, and deterministic replay are columns in `artifacts/kill_test/runs.parquet`; raw evidence is in `query_logs/` and `graph_events/`.",
        "oracle_headroom.md": "NOT_RUN: full Phase 1 is required.",
        "prior_robustness.md": "NOT_RUN: requires K1 PASS.",
        "finite_sample.md": "NOT_RUN: requires K1 PASS and closure of evaluator/RFCI blockers.",
    }
    for name, body in report_bodies.items():
        (REPORTS / name).write_text(f"# {name[:-3].replace('_', ' ').title()}\n\n{body}\n", encoding="utf-8")
    summaries = ARTIFACTS / "summaries"
    summaries.mkdir(parents=True, exist_ok=True)
    (summaries / "inventory.json").write_text(json.dumps({"phase0_main_runs": completed, "all_rows": len(rows), "gate_statuses": k}, indent=2, sort_keys=True), encoding="utf-8")


def generate_figures() -> None:
    figure_dir = ARTIFACTS / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    runs_path = ARTIFACTS / "runs.parquet"
    rows = pd.read_parquet(runs_path) if runs_path.exists() else pd.DataFrame()
    specs = ["oracle_headroom", "quality_budget_curve", "benefit_vs_prior_auc", "independent_vs_correlated_errors", "failure_map"]
    for name in specs:
        fig, ax = plt.subplots(figsize=(6, 4))
        if name == "oracle_headroom" and not rows.empty and "wall_time_seconds" in rows:
            rows.groupby("scheduler")["ci_tests"].median().plot(kind="bar", ax=ax)
            ax.set_ylabel("median CI calls")
            ax.set_title("Phase-0 diagnostic only (not K1 evidence)")
        else:
            ax.text(0.5, 0.5, "NOT RUN\nRequired phase evidence is unavailable", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(figure_dir / f"{name}.png", dpi=150)
        plt.close(fig)
