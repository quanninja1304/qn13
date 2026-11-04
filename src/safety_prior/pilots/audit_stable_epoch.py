from __future__ import annotations

import argparse
import json
import platform
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from ..algorithms.epoch import (
    EPOCH_CONTRACT_VERSION,
    EpochCheckpoint,
    commit_epoch,
    execute_frozen_epoch,
    finalize_epoch_results,
    freeze_epoch,
    incomplete_epoch_state,
)
from ..algorithms.icd_reference import PAGSnapshot
from ..ci import CIResult
from ..graphs import digest_object
from ..models import CIQuery


@dataclass(frozen=True)
class StableEpochAuditSummary:
    contract_version: str
    reference_id: str
    reference_mode: str
    equality_target: str
    truth_table_count: int
    schedule_permutations_per_table: int
    audited_schedule_count: int
    deletion_mismatches: int
    selected_witness_mismatches: int
    completion_order_mismatches: int
    frontier_mismatches: int
    replay_resume_mismatches: int
    provenance_mismatches: int
    budget_state_mismatches: int
    status: str
    first_failures: tuple[dict, ...]


G2_TRUTH_TABLE_COUNT = 64
G2_MINIMUM_AUDITED_SCHEDULES = 256


class _DecisionTableCI:
    def __init__(self, independent_query_ids: set[str], candidates: tuple[CIQuery, ...]):
        self._decisions = {
            (query.x, query.y, query.conditioning_set): query.query_id in independent_query_ids
            for query in candidates
        }

    def test(self, i: int, j: int, conditioning_set: tuple[int, ...]) -> CIResult:
        key = (min(i, j), max(i, j), tuple(sorted(conditioning_set)))
        independent = self._decisions[key]
        return CIResult(independent, 1.0 if independent else 0.0)


def _query(query_id: str, x: int, y: int, conditioning_set=()) -> CIQuery:
    return CIQuery(
        query_id,
        x,
        y,
        tuple(conditioning_set),
        "stable_epoch_audit",
        "unfrozen",
        0,
        0,
    )


def _audit_epoch():
    snapshot = PAGSnapshot.circles(
        (0, 1, 2, 3),
        ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)),
    )
    candidates = (
        _query("p01-empty", 0, 1),
        _query("p01-z2", 0, 1, (2,)),
        _query("p01-z3", 0, 1, (3,)),
        _query("p02-empty", 0, 2),
        _query("p02-z1", 0, 2, (1,)),
        _query("p02-z3", 0, 2, (3,)),
    )
    return snapshot, freeze_epoch(snapshot, 1, "FrozenEpoch.exhaustive_epoch", candidates)


def _same_completed_state(left, right) -> tuple[bool, bool]:
    return left.deletions == right.deletions, left.selected_witnesses == right.selected_witnesses


def audit_stable_epoch(
    *, seed: int = 20261006, schedule_permutations: int = 4
) -> StableEpochAuditSummary:
    if schedule_permutations < 1:
        raise ValueError("schedule_permutations must be positive")
    snapshot, epoch = _audit_epoch()
    query_ids = tuple(query.query_id for query in epoch.candidates)
    total_work = sum(query.local_size**3 for query in epoch.candidates)
    rng = np.random.default_rng(seed)
    counters = {
        "deletion": 0,
        "witness": 0,
        "completion": 0,
        "frontier": 0,
        "resume": 0,
        "provenance": 0,
        "budget": 0,
    }
    failures: list[dict] = []

    def record(kind: str, truth_table: int, permutation: int, detail: str) -> None:
        counters[kind] += 1
        if len(failures) < 20:
            failures.append(
                {
                    "kind": kind,
                    "truth_table": truth_table,
                    "permutation": permutation,
                    "detail": detail,
                }
            )

    for truth_table in range(1 << len(query_ids)):
        independent = {
            query_id
            for bit, query_id in enumerate(query_ids)
            if truth_table & (1 << bit)
        }
        ci = _DecisionTableCI(independent, epoch.candidates)
        reference = execute_frozen_epoch(epoch, ci, mode="exhaustive_epoch")
        committed = commit_epoch(snapshot, epoch, reference)
        if len(committed.graph_events) != len(reference.selected_witnesses):
            record("provenance", truth_table, -1, "event count")
        for event, witness in zip(committed.graph_events, reference.selected_witnesses):
            if (
                event["pair"] != list(witness.pair)
                or event["conditioning_set"] != list(witness.conditioning_set)
                or event["evidence_query_ids"] != [witness.query_id]
                or event["epoch_id"] != epoch.epoch_id
            ):
                record("provenance", truth_table, -1, "event evidence")

        budgeted = execute_frozen_epoch(
            epoch, ci, mode="exhaustive_epoch", weighted_budget=0
        )
        budget_state = incomplete_epoch_state(snapshot, epoch, budgeted, 0)
        if budgeted.completed or budgeted.deletions or budget_state.completed:
            record("budget", truth_table, -1, "budgeted state was committable")

        for permutation in range(schedule_permutations):
            order = list(query_ids)
            rng.shuffle(order)
            scheduled = execute_frozen_epoch(
                epoch, ci, mode="exhaustive_epoch", execution_order=order
            )
            deletion_equal, witness_equal = _same_completed_state(reference, scheduled)
            if not deletion_equal:
                record("deletion", truth_table, permutation, "schedule changed deletions")
            if not witness_equal:
                record("witness", truth_table, permutation, "schedule changed witness")

            rows = list(scheduled.checkpoint.results)
            rng.shuffle(rows)
            completion = finalize_epoch_results(epoch, rows, mode="exhaustive_epoch")
            if _same_completed_state(reference, completion) != (True, True):
                record("completion", truth_table, permutation, "completion order changed state")

            frontier = execute_frozen_epoch(
                epoch,
                ci,
                mode="canonical_frontier",
                execution_order=order,
            )
            if _same_completed_state(reference, frontier) != (True, True):
                record("frontier", truth_table, permutation, "frontier changed state")

            partial = execute_frozen_epoch(
                epoch,
                ci,
                mode="exhaustive_epoch",
                execution_order=order,
                weighted_budget=max(0, total_work - 1),
            )
            restored = EpochCheckpoint.from_dict(
                json.loads(json.dumps(partial.checkpoint.as_dict()))
            )
            resumed = execute_frozen_epoch(
                epoch,
                ci,
                mode="exhaustive_epoch",
                execution_order=order,
                weighted_budget=total_work,
                checkpoint=restored,
            )
            if _same_completed_state(reference, resumed) != (True, True):
                record("resume", truth_table, permutation, "resume changed state")

    passed = not any(counters.values())
    return StableEpochAuditSummary(
        EPOCH_CONTRACT_VERSION,
        "FrozenEpoch.exhaustive_epoch",
        "frozen_epoch_reference",
        "completed_epoch_state",
        1 << len(query_ids),
        schedule_permutations,
        (1 << len(query_ids)) * schedule_permutations,
        counters["deletion"],
        counters["witness"],
        counters["completion"],
        counters["frontier"],
        counters["resume"],
        counters["provenance"],
        counters["budget"],
        "PASS" if passed else "FAIL",
        tuple(failures),
    )


def evaluate_g2(summary: StableEpochAuditSummary) -> dict:
    mismatch_fields = {
        "deletion_mismatches": summary.deletion_mismatches,
        "selected_witness_mismatches": summary.selected_witness_mismatches,
        "completion_order_mismatches": summary.completion_order_mismatches,
        "frontier_mismatches": summary.frontier_mismatches,
        "replay_resume_mismatches": summary.replay_resume_mismatches,
        "provenance_mismatches": summary.provenance_mismatches,
        "budget_state_mismatches": summary.budget_state_mismatches,
    }
    passed = (
        summary.truth_table_count == G2_TRUTH_TABLE_COUNT
        and summary.audited_schedule_count >= G2_MINIMUM_AUDITED_SCHEDULES
        and summary.status == "PASS"
        and not any(mismatch_fields.values())
    )
    return {
        "gate": "G2_STABLE_EPOCH_SOUND",
        "status": "PASS" if passed else "FAIL",
        "metrics": {
            "truth_table_count": summary.truth_table_count,
            "audited_schedule_count": summary.audited_schedule_count,
            **mismatch_fields,
        },
        "thresholds": {
            "truth_table_count": G2_TRUTH_TABLE_COUNT,
            "minimum_audited_schedules": G2_MINIMUM_AUDITED_SCHEDULES,
            "maximum_mismatches_per_category": 0,
        },
        "blockers": []
        if passed
        else ["run_full_g2_audit_and_resolve_all_mismatches"],
    }


def _git_revision() -> str:
    root = Path(__file__).resolve().parents[3]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=root,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    return f"{revision}+dirty" if dirty else revision


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit frozen stable-epoch semantics")
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--permutations", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    summary = audit_stable_epoch(
        seed=args.seed, schedule_permutations=args.permutations
    )
    gate = evaluate_g2(summary)
    payload = {
        "contract_version": EPOCH_CONTRACT_VERSION,
        "gate": gate,
        "reproducibility": {
            "git_revision": _git_revision(),
            "config_digest": digest_object(
                {
                    "seed": args.seed,
                    "schedule_permutations": args.permutations,
                    "epoch_contract_version": EPOCH_CONTRACT_VERSION,
                }
            ),
            "dependency_lock": digest_object(
                {"python": platform.python_version(), "numpy": np.__version__}
            ),
        },
        "audit": asdict(summary),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(encoded + "\n", encoding="utf-8", newline="\n")
        temporary.replace(args.output)
    print(encoded)
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
