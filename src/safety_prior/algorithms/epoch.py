from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Iterable, Mapping, Sequence

from ..ci import CIResult, UndefinedCIResultError
from ..graphs import digest_object
from ..models import CIQuery, DiscoveryState, SeparationWitness
from .icd_reference import PAGSnapshot


EPOCH_CONTRACT_VERSION = "0.2.0"
EPOCH_MODES = frozenset({"exhaustive_epoch", "canonical_frontier"})


def pag_snapshot_digest(snapshot: PAGSnapshot) -> str:
    return digest_object(
        {
            "nodes": list(snapshot.nodes),
            "edges": [
                [left, right, left_mark.value, right_mark.value]
                for (left, right), (left_mark, right_mark) in sorted(
                    snapshot.edge_marks.items()
                )
            ],
        }
    )


@dataclass(frozen=True)
class FrozenEpoch:
    epoch_id: str
    snapshot_digest: str
    candidate_family_digest: str
    radius: int
    reference_id: str
    contract_version: str
    candidates: tuple[CIQuery, ...]

    def candidate_map(self) -> dict[str, CIQuery]:
        return {query.query_id: query for query in self.candidates}

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EpochCheckpoint:
    epoch_id: str
    candidate_family_digest: str
    mode: str
    results: tuple[tuple[str, CIResult], ...]
    used_work: int

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["results"] = [
            {"query_id": query_id, "result": asdict(result)}
            for query_id, result in self.results
        ]
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> EpochCheckpoint:
        rows = payload.get("results", ())
        results = tuple(
            (
                str(row["query_id"]),
                CIResult(**dict(row["result"])),
            )
            for row in rows
        )
        return cls(
            str(payload["epoch_id"]),
            str(payload["candidate_family_digest"]),
            str(payload["mode"]),
            results,
            int(payload["used_work"]),
        )


@dataclass(frozen=True)
class EpochExecutionResult:
    epoch_id: str
    candidate_family_digest: str
    mode: str
    completed: bool
    used_work: int
    executed_query_ids: tuple[str, ...]
    pending_query_ids: tuple[str, ...]
    cancelled_query_ids: tuple[str, ...]
    provisional_witnesses: tuple[SeparationWitness, ...]
    selected_witnesses: tuple[SeparationWitness, ...]
    deletions: tuple[tuple[int, int], ...]
    speculative_work: int
    checkpoint: EpochCheckpoint

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EpochCommitResult:
    snapshot: PAGSnapshot
    graph_events: tuple[dict, ...]


def freeze_epoch(
    snapshot: PAGSnapshot | str,
    radius: int,
    reference_id: str,
    candidates: Iterable[CIQuery],
    *,
    contract_version: str = EPOCH_CONTRACT_VERSION,
) -> FrozenEpoch:
    if radius < 0:
        raise ValueError("epoch radius must be non-negative")
    if not reference_id:
        raise ValueError("reference_id cannot be empty")
    snapshot_digest = (
        pag_snapshot_digest(snapshot) if isinstance(snapshot, PAGSnapshot) else str(snapshot)
    )
    if not snapshot_digest:
        raise ValueError("snapshot digest cannot be empty")

    query_ids: dict[str, tuple] = {}
    by_semantics: dict[tuple, CIQuery] = {}
    for query in candidates:
        semantics = (
            query.x,
            query.y,
            query.conditioning_set,
            query.phase,
        )
        previous_semantics = query_ids.get(query.query_id)
        if previous_semantics is not None and previous_semantics != semantics:
            raise ValueError(f"query_id {query.query_id!r} has conflicting semantics")
        query_ids[query.query_id] = semantics
        previous = by_semantics.get(semantics)
        if previous is None or query.query_id < previous.query_id:
            by_semantics[semantics] = query

    ordered = sorted(
        by_semantics.values(),
        key=lambda query: (
            query.x,
            query.y,
            len(query.conditioning_set),
            query.conditioning_set,
            query.phase,
            query.query_id,
        ),
    )
    family_rows = [
        {
            "query_id": query.query_id,
            "pair": [query.x, query.y],
            "conditioning_set": list(query.conditioning_set),
            "phase": query.phase,
        }
        for query in ordered
    ]
    candidate_family_digest = digest_object(family_rows)
    epoch_id = digest_object(
        {
            "snapshot_digest": snapshot_digest,
            "radius": radius,
            "reference_id": reference_id,
            "contract_version": contract_version,
        }
    )
    pair_orders: dict[tuple[int, int], int] = {}
    frozen: list[CIQuery] = []
    for canonical_rank, query in enumerate(ordered):
        pair = (query.x, query.y)
        pair_order = pair_orders.get(pair, 0)
        pair_orders[pair] = pair_order + 1
        frozen.append(
            replace(
                query,
                epoch_id=epoch_id,
                pair_order=pair_order,
                canonical_rank=canonical_rank,
            )
        )
    return FrozenEpoch(
        epoch_id,
        snapshot_digest,
        candidate_family_digest,
        radius,
        reference_id,
        contract_version,
        tuple(frozen),
    )


def _witnesses(
    epoch: FrozenEpoch, results: Mapping[str, CIResult]
) -> tuple[SeparationWitness, ...]:
    return tuple(
        SeparationWitness(
            (query.x, query.y),
            query.conditioning_set,
            query.query_id,
            query.canonical_rank,
        )
        for query in epoch.candidates
        if query.query_id in results and results[query.query_id].independent is True
    )


def _selected_by_pair(
    witnesses: Iterable[SeparationWitness],
) -> dict[tuple[int, int], SeparationWitness]:
    selected: dict[tuple[int, int], SeparationWitness] = {}
    for witness in witnesses:
        previous = selected.get(witness.pair)
        if previous is None or (witness.canonical_rank, witness.query_id) < (
            previous.canonical_rank,
            previous.query_id,
        ):
            selected[witness.pair] = witness
    return selected


def _frontier_closed(
    pair_candidates: Sequence[CIQuery],
    selected: SeparationWitness,
    results: Mapping[str, CIResult],
) -> bool:
    return all(
        candidate.query_id in results
        for candidate in pair_candidates
        if candidate.canonical_rank < selected.canonical_rank
    )


def finalize_epoch_results(
    epoch: FrozenEpoch,
    results: Mapping[str, CIResult] | Iterable[tuple[str, CIResult]],
    *,
    mode: str,
    used_work: int | None = None,
) -> EpochExecutionResult:
    if mode not in EPOCH_MODES:
        raise ValueError(f"unknown epoch execution mode: {mode}")
    rows = list(results.items()) if isinstance(results, Mapping) else list(results)
    if len({query_id for query_id, _ in rows}) != len(rows):
        raise ValueError("duplicate query result in epoch")
    result_map = dict(rows)
    candidates = epoch.candidate_map()
    unknown = set(result_map) - set(candidates)
    if unknown:
        raise ValueError(f"results contain queries outside the frozen epoch: {sorted(unknown)}")
    undefined = [
        query_id for query_id, result in result_map.items() if result.independent is None
    ]
    if undefined:
        query_id = min(undefined, key=lambda value: candidates[value].canonical_rank)
        result = result_map[query_id]
        raise UndefinedCIResultError(
            query_id,
            result.numerical_status,
            {
                "epoch_id": epoch.epoch_id,
                "candidate_family_digest": epoch.candidate_family_digest,
                "result": asdict(result),
            },
        )

    provisional = _witnesses(epoch, result_map)
    selected_by_pair = _selected_by_pair(provisional)
    by_pair: dict[tuple[int, int], list[CIQuery]] = {}
    for query in epoch.candidates:
        by_pair.setdefault((query.x, query.y), []).append(query)

    cancelled: set[str] = set()
    if mode == "canonical_frontier":
        for pair, selected in selected_by_pair.items():
            pair_candidates = by_pair[pair]
            if _frontier_closed(pair_candidates, selected, result_map):
                cancelled.update(
                    candidate.query_id
                    for candidate in pair_candidates
                    if candidate.canonical_rank > selected.canonical_rank
                    and candidate.query_id not in result_map
                )
    pending = tuple(
        query.query_id
        for query in epoch.candidates
        if query.query_id not in result_map and query.query_id not in cancelled
    )
    completed = not pending and (
        mode == "canonical_frontier" or len(result_map) == len(epoch.candidates)
    )
    selected = (
        tuple(selected_by_pair[pair] for pair in sorted(selected_by_pair))
        if completed
        else ()
    )
    deletions = tuple(witness.pair for witness in selected)
    speculative_work = 0
    if completed and mode == "canonical_frontier":
        for witness in selected:
            speculative_work += sum(
                candidate.local_size**3
                for candidate in by_pair[witness.pair]
                if candidate.query_id in result_map
                and candidate.canonical_rank > witness.canonical_rank
            )
    expected_work = sum(
        candidates[query_id].local_size**3 for query_id in result_map
    )
    accounted_work = expected_work if used_work is None else int(used_work)
    if accounted_work != expected_work:
        raise ValueError("epoch work counter does not match executed query results")
    checkpoint = EpochCheckpoint(
        epoch.epoch_id,
        epoch.candidate_family_digest,
        mode,
        tuple(
            (query.query_id, result_map[query.query_id])
            for query in epoch.candidates
            if query.query_id in result_map
        ),
        accounted_work,
    )
    return EpochExecutionResult(
        epoch.epoch_id,
        epoch.candidate_family_digest,
        mode,
        completed,
        accounted_work,
        tuple(
            query.query_id
            for query in epoch.candidates
            if query.query_id in result_map
        ),
        pending,
        tuple(
            query.query_id
            for query in epoch.candidates
            if query.query_id in cancelled
        ),
        provisional,
        selected,
        deletions,
        speculative_work,
        checkpoint,
    )


def _can_cancel(
    query: CIQuery,
    epoch: FrozenEpoch,
    results: Mapping[str, CIResult],
) -> bool:
    pair = (query.x, query.y)
    pair_candidates = [
        candidate
        for candidate in epoch.candidates
        if (candidate.x, candidate.y) == pair
    ]
    selected = _selected_by_pair(_witnesses(epoch, results)).get(pair)
    return bool(
        selected
        and query.canonical_rank > selected.canonical_rank
        and _frontier_closed(pair_candidates, selected, results)
    )


def execute_frozen_epoch(
    epoch: FrozenEpoch,
    ci,
    *,
    mode: str = "exhaustive_epoch",
    execution_order: Sequence[str] | None = None,
    weighted_budget: int | None = None,
    checkpoint: EpochCheckpoint | None = None,
    wave_size: int = 1,
) -> EpochExecutionResult:
    if mode not in EPOCH_MODES:
        raise ValueError(f"unknown epoch execution mode: {mode}")
    if weighted_budget is not None and weighted_budget < 0:
        raise ValueError("weighted_budget cannot be negative")
    if wave_size < 1:
        raise ValueError("wave_size must be positive")
    candidate_map = epoch.candidate_map()
    order = tuple(candidate_map) if execution_order is None else tuple(execution_order)
    if len(order) != len(candidate_map) or set(order) != set(candidate_map):
        raise ValueError("execution_order must be a permutation of the frozen candidate IDs")

    if checkpoint is None:
        results: dict[str, CIResult] = {}
        used_work = 0
    else:
        if checkpoint.epoch_id != epoch.epoch_id:
            raise ValueError("checkpoint epoch_id does not match the frozen epoch")
        if checkpoint.candidate_family_digest != epoch.candidate_family_digest:
            raise ValueError("checkpoint candidate-family digest drift")
        if checkpoint.mode != mode:
            raise ValueError("checkpoint execution mode does not match")
        results = dict(checkpoint.results)
        if len(results) != len(checkpoint.results):
            raise ValueError("checkpoint contains duplicate query results")
        if not set(results) <= set(candidate_map):
            raise ValueError("checkpoint contains a query outside the frozen epoch")
        used_work = checkpoint.used_work
        expected_work = sum(
            candidate_map[query_id].local_size**3 for query_id in results
        )
        if used_work != expected_work:
            raise ValueError("checkpoint work counter does not match its query results")

    cursor = 0
    budget_stopped = False
    while cursor < len(order):
        wave: list[CIQuery] = []
        while cursor < len(order) and len(wave) < wave_size:
            query = candidate_map[order[cursor]]
            cursor += 1
            if query.query_id in results:
                continue
            if mode == "canonical_frontier" and _can_cancel(query, epoch, results):
                continue
            cost = query.local_size**3
            if weighted_budget is not None and used_work + sum(
                item.local_size**3 for item in wave
            ) + cost > weighted_budget:
                budget_stopped = True
                cursor = len(order)
                break
            wave.append(query)
        if not wave:
            if budget_stopped:
                break
            continue
        if hasattr(ci, "test_many"):
            wave_results = ci.test_many(tuple(wave))
        else:
            wave_results = [
                ci.test(query.x, query.y, query.conditioning_set) for query in wave
            ]
        if len(wave_results) != len(wave):
            raise RuntimeError("CI backend returned the wrong number of batch results")
        for query, result in zip(wave, wave_results, strict=True):
            results[query.query_id] = result
            used_work += query.local_size**3
            if result.independent is None:
                raise UndefinedCIResultError(
                    query.query_id,
                    result.numerical_status,
                    {
                        "epoch_id": epoch.epoch_id,
                        "candidate_family_digest": epoch.candidate_family_digest,
                        "result": asdict(result),
                    },
                )

    return finalize_epoch_results(epoch, results, mode=mode, used_work=used_work)


def commit_epoch(
    snapshot: PAGSnapshot,
    epoch: FrozenEpoch,
    execution: EpochExecutionResult,
) -> EpochCommitResult:
    if pag_snapshot_digest(snapshot) != epoch.snapshot_digest:
        raise ValueError("snapshot digest does not match the frozen epoch")
    if execution.epoch_id != epoch.epoch_id:
        raise ValueError("execution result belongs to a different epoch")
    if execution.candidate_family_digest != epoch.candidate_family_digest:
        raise ValueError("execution candidate-family digest does not match")
    if not execution.completed:
        raise RuntimeError("cannot commit an incomplete frozen epoch")
    if (
        execution.checkpoint.epoch_id != epoch.epoch_id
        or execution.checkpoint.candidate_family_digest
        != epoch.candidate_family_digest
        or execution.checkpoint.mode != execution.mode
    ):
        raise ValueError("execution checkpoint identity does not match the frozen epoch")
    replayed = finalize_epoch_results(
        epoch,
        execution.checkpoint.results,
        mode=execution.mode,
        used_work=execution.used_work,
    )
    if (
        not replayed.completed
        or replayed.selected_witnesses != execution.selected_witnesses
        or replayed.deletions != execution.deletions
    ):
        raise ValueError("execution evidence does not reproduce its committed state")

    marks = dict(snapshot.edge_marks)
    events: list[dict] = []
    for witness in execution.selected_witnesses:
        if witness.pair not in marks:
            raise RuntimeError(f"deletion pair is not adjacent in the frozen snapshot: {witness.pair}")
        del marks[witness.pair]
        events.append(
            {
                "event_type": "edge_removal",
                "rule": "frozen_epoch_canonical_witness",
                "epoch_id": epoch.epoch_id,
                "pair": list(witness.pair),
                "conditioning_set": list(witness.conditioning_set),
                "evidence_query_ids": [witness.query_id],
                "canonical_rank": witness.canonical_rank,
            }
        )
    return EpochCommitResult(PAGSnapshot(snapshot.nodes, marks), tuple(events))


def incomplete_epoch_state(
    snapshot: PAGSnapshot,
    epoch: FrozenEpoch,
    execution: EpochExecutionResult,
    weighted_budget: int | None,
) -> DiscoveryState:
    if execution.completed:
        raise ValueError("completed epochs are not incomplete DiscoveryState objects")
    graph = {
        "nodes": list(snapshot.nodes),
        "edge_marks": [
            [left, right, left_mark.value, right_mark.value]
            for (left, right), (left_mark, right_mark) in sorted(snapshot.edge_marks.items())
        ],
        "snapshot_digest": epoch.snapshot_digest,
        "epoch_id": epoch.epoch_id,
        "is_pag": False,
    }
    tests = [
        {"query_id": query_id, "result": asdict(result)}
        for query_id, result in execution.checkpoint.results
    ]
    untested = [asdict(epoch.candidate_map()[query_id]) for query_id in execution.pending_query_ids]
    budget = {
        "weighted_cost": execution.used_work,
        "weighted_limit": weighted_budget,
        "speculative_work": execution.speculative_work,
    }
    return DiscoveryState(graph, tests, untested, budget, False)
