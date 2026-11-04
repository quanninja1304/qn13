import json
from dataclasses import replace

import numpy as np
import pytest

from safety_prior.algorithms.epoch import (
    EpochCheckpoint,
    commit_epoch,
    execute_frozen_epoch,
    finalize_epoch_results,
    freeze_epoch,
    incomplete_epoch_state,
    pag_snapshot_digest,
)
from safety_prior.algorithms.icd_reference import PAGSnapshot
from safety_prior.ci import CIResult, GaussianCI, UndefinedCIResultError
from safety_prior.ci_batch import GaussianBatchCI
from safety_prior.models import CIQuery


def _query(query_id, x, y, conditioning_set=()):
    return CIQuery(
        query_id,
        x,
        y,
        tuple(conditioning_set),
        "skeleton",
        "unfrozen",
        0,
        0,
    )


def _snapshot():
    return PAGSnapshot.circles(
        (0, 1, 2, 3),
        ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)),
    )


def _candidate_table():
    return (
        _query("q01-empty", 0, 1),
        _query("q01-z2", 0, 1, (2,)),
        _query("q01-z3", 0, 1, (3,)),
        _query("q02-empty", 0, 2),
        _query("q02-z1", 0, 2, (1,)),
    )


class _TableCI:
    backend = "table"

    def __init__(self, independent):
        self.independent = set(independent)

    def test(self, i, j, conditioning_set):
        key = (min(i, j), max(i, j), tuple(conditioning_set))
        decision = key in self.independent
        return CIResult(decision, 1.0 if decision else 0.0)


class _TableBatchCI(_TableCI):
    def test_many(self, queries):
        return [self.test(query.x, query.y, query.conditioning_set) for query in queries]


def _epoch(candidates=None):
    return freeze_epoch(
        _snapshot(),
        1,
        "unit-reference",
        _candidate_table() if candidates is None else candidates,
    )


def _ci():
    return _TableCI({(0, 1, (2,)), (0, 1, (3,))})


def test_freeze_epoch_is_order_invariant_and_suppresses_semantic_duplicates():
    candidates = _candidate_table()
    duplicate = _query("zz-duplicate", 1, 0, (2,))
    first = _epoch(candidates + (duplicate,))
    second = _epoch(tuple(reversed(candidates + (duplicate,))))

    assert first.epoch_id == second.epoch_id
    assert first.candidate_family_digest == second.candidate_family_digest
    assert len(first.candidates) == len(candidates)
    assert [query.canonical_rank for query in first.candidates] == list(range(len(candidates)))
    assert all(query.epoch_id == first.epoch_id for query in first.candidates)


def test_conflicting_duplicate_query_id_is_rejected():
    with pytest.raises(ValueError, match="conflicting semantics"):
        _epoch((_query("same", 0, 1), _query("same", 0, 2)))


@pytest.mark.parametrize("seed", range(12))
def test_exhaustive_epoch_is_schedule_invariant(seed):
    epoch = _epoch()
    rng = np.random.default_rng(seed)
    order = [query.query_id for query in epoch.candidates]
    rng.shuffle(order)

    result = execute_frozen_epoch(
        epoch, _ci(), mode="exhaustive_epoch", execution_order=order
    )

    assert result.completed
    assert result.deletions == ((0, 1),)
    assert result.selected_witnesses[0].conditioning_set == (2,)
    assert len(result.provisional_witnesses) == 2
    assert result.cancelled_query_ids == ()


def test_result_completion_order_does_not_change_canonical_evidence():
    epoch = _epoch()
    ci = _ci()
    rows = [
        (query.query_id, ci.test(query.x, query.y, query.conditioning_set))
        for query in epoch.candidates
    ]

    forward = finalize_epoch_results(epoch, rows, mode="exhaustive_epoch")
    reverse = finalize_epoch_results(epoch, reversed(rows), mode="exhaustive_epoch")

    assert forward.deletions == reverse.deletions
    assert forward.selected_witnesses == reverse.selected_witnesses
    assert forward.checkpoint.results == reverse.checkpoint.results


def test_canonical_frontier_matches_exhaustive_and_cancels_only_safe_suffix():
    epoch = _epoch()
    canonical_order = [query.query_id for query in epoch.candidates]
    exhaustive = execute_frozen_epoch(epoch, _ci(), mode="exhaustive_epoch")
    frontier = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="canonical_frontier",
        execution_order=canonical_order,
    )

    assert frontier.completed
    assert frontier.deletions == exhaustive.deletions
    assert frontier.selected_witnesses == exhaustive.selected_witnesses
    assert "q01-z3" in frontier.cancelled_query_ids
    assert "q01-z3" not in frontier.executed_query_ids


def test_random_frontier_order_records_speculation_but_preserves_output():
    epoch = _epoch()
    order = ["q01-z3", "q01-empty", "q01-z2", "q02-empty", "q02-z1"]
    result = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="canonical_frontier",
        execution_order=order,
    )

    assert result.completed
    assert result.selected_witnesses[0].conditioning_set == (2,)
    assert result.speculative_work == 3**3


def test_interrupted_resume_equals_uninterrupted_and_does_not_commit_early():
    epoch = _epoch()
    full = execute_frozen_epoch(epoch, _ci(), mode="exhaustive_epoch")
    partial = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="exhaustive_epoch",
        weighted_budget=8,
    )

    assert not partial.completed
    assert partial.deletions == ()
    with pytest.raises(RuntimeError, match="incomplete"):
        commit_epoch(_snapshot(), epoch, partial)
    state = incomplete_epoch_state(_snapshot(), epoch, partial, 8)
    assert state.object_type == "DiscoveryState"
    assert not state.completed
    assert state.untested

    restored = EpochCheckpoint.from_dict(
        json.loads(json.dumps(partial.checkpoint.as_dict()))
    )
    resumed = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="exhaustive_epoch",
        weighted_budget=full.used_work,
        checkpoint=restored,
    )
    assert resumed.completed
    assert resumed.deletions == full.deletions
    assert resumed.selected_witnesses == full.selected_witnesses
    assert resumed.used_work == full.used_work


def test_resume_rejects_candidate_family_digest_drift():
    epoch = _epoch()
    partial = execute_frozen_epoch(
        epoch, _ci(), mode="exhaustive_epoch", weighted_budget=8
    )
    changed = _epoch(_candidate_table() + (_query("new", 0, 3),))

    assert changed.epoch_id == epoch.epoch_id
    with pytest.raises(ValueError, match="candidate-family digest drift"):
        execute_frozen_epoch(
            changed,
            _ci(),
            mode="exhaustive_epoch",
            checkpoint=partial.checkpoint,
        )

    corrupt = replace(partial.checkpoint, candidate_family_digest="drifted")
    with pytest.raises(ValueError, match="candidate-family digest drift"):
        execute_frozen_epoch(
            epoch,
            _ci(),
            mode="exhaustive_epoch",
            checkpoint=corrupt,
        )


def test_explicit_empty_execution_order_is_not_treated_as_default_order():
    with pytest.raises(ValueError, match="permutation"):
        execute_frozen_epoch(
            _epoch(),
            _ci(),
            mode="exhaustive_epoch",
            execution_order=(),
        )


def test_budget_before_and_after_witness_respects_the_epoch_barrier():
    epoch = _epoch(_candidate_table()[:3])
    before_witness = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="canonical_frontier",
        weighted_budget=8,
    )
    after_witness = execute_frozen_epoch(
        epoch,
        _ci(),
        mode="canonical_frontier",
        weighted_budget=35,
    )

    assert not before_witness.completed
    assert before_witness.deletions == ()
    assert after_witness.completed
    assert after_witness.deletions == ((0, 1),)
    assert after_witness.cancelled_query_ids == ("q01-z3",)


def test_undefined_ci_result_aborts_without_a_committable_epoch():
    class UndefinedCI:
        def test(self, i, j, conditioning_set):
            return CIResult(None, None, numerical_status="singular")

    epoch = _epoch((_query("undefined", 0, 1),))
    with pytest.raises(UndefinedCIResultError) as captured:
        execute_frozen_epoch(epoch, UndefinedCI(), mode="exhaustive_epoch")

    assert captured.value.as_dict()["terminal_status"] == "failed"
    assert captured.value.as_dict()["query_id"] == "undefined"


def test_atomic_commit_uses_one_witness_and_does_not_mutate_source_snapshot():
    snapshot = _snapshot()
    before = pag_snapshot_digest(snapshot)
    epoch = _epoch()
    execution = execute_frozen_epoch(epoch, _ci(), mode="exhaustive_epoch")

    committed = commit_epoch(snapshot, epoch, execution)

    assert pag_snapshot_digest(snapshot) == before
    assert snapshot.adjacent(0, 1)
    assert not committed.snapshot.adjacent(0, 1)
    assert len(committed.graph_events) == 1
    event = committed.graph_events[0]
    assert event["conditioning_set"] == [2]
    assert event["evidence_query_ids"] == ["q01-z2"]


def test_commit_rejects_tampered_execution_evidence():
    snapshot = _snapshot()
    epoch = _epoch()
    execution = execute_frozen_epoch(epoch, _ci(), mode="exhaustive_epoch")

    with pytest.raises(ValueError, match="does not reproduce"):
        commit_epoch(
            snapshot,
            epoch,
            replace(execution, selected_witnesses=(), deletions=()),
        )


def test_resume_rejects_tampered_work_counter():
    epoch = _epoch()
    partial = execute_frozen_epoch(
        epoch, _ci(), mode="exhaustive_epoch", weighted_budget=8
    )
    corrupt = replace(partial.checkpoint, used_work=partial.used_work + 1)

    with pytest.raises(ValueError, match="work counter"):
        execute_frozen_epoch(
            epoch,
            _ci(),
            mode="exhaustive_epoch",
            checkpoint=corrupt,
        )


def test_scalar_and_batch_backends_produce_the_same_epoch_evidence():
    rng = np.random.default_rng(301)
    data = rng.normal(size=(500, 5))
    candidates = (
        _query("a", 0, 1),
        _query("b", 0, 1, (2,)),
        _query("c", 0, 2, (1, 3)),
        _query("d", 1, 4, (0, 2, 3)),
    )
    epoch = _epoch(candidates)
    scalar = execute_frozen_epoch(
        epoch, GaussianCI(data), mode="exhaustive_epoch", wave_size=4
    )
    batch = execute_frozen_epoch(
        epoch,
        GaussianBatchCI(data, batching_strategy="power_of_two"),
        mode="exhaustive_epoch",
        wave_size=4,
    )

    assert batch.deletions == scalar.deletions
    assert batch.selected_witnesses == scalar.selected_witnesses
    for (_, batch_result), (_, scalar_result) in zip(
        batch.checkpoint.results, scalar.checkpoint.results, strict=True
    ):
        assert batch_result.independent == scalar_result.independent
        assert batch_result.numerical_status == scalar_result.numerical_status
        assert batch_result.p_value == pytest.approx(scalar_result.p_value, abs=1e-12)
        assert batch_result.statistic == pytest.approx(scalar_result.statistic, abs=1e-12)
        assert batch_result.effect == pytest.approx(scalar_result.effect, abs=1e-12)


def test_batch_wave_preserves_canonical_selection_under_speculative_completion():
    epoch = _epoch()
    result = execute_frozen_epoch(
        epoch,
        _TableBatchCI(_ci().independent),
        mode="canonical_frontier",
        wave_size=3,
    )

    assert result.completed
    assert result.selected_witnesses[0].conditioning_set == (2,)
    assert result.speculative_work == 3**3
