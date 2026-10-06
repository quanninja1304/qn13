from dataclasses import asdict

import numpy as np
import pytest

from safety_prior.ci import GaussianCI
from safety_prior.ci_batch import GaussianBatchCI, plan_batch_memory
from safety_prior.models import CIQuery
from safety_prior.pilots.audit_batch_ci import audit_scalar_batch


def _query(rank: int, x: int, y: int, conditioning_set=()) -> CIQuery:
    return CIQuery(
        f"q{rank}",
        x,
        y,
        tuple(conditioning_set),
        "test",
        "epoch",
        rank,
        rank,
    )


def _queries() -> tuple[CIQuery, ...]:
    return (
        _query(0, 0, 1),
        _query(1, 0, 2, (1,)),
        _query(2, 1, 3, (4, 0)),
        _query(3, 2, 5, (0, 1, 4)),
        _query(4, 6, 1, (5, 3, 2, 0)),
    )


def _assert_results_close(left, right):
    assert left.independent is right.independent
    assert left.numerical_status == right.numerical_status
    assert left.effect == pytest.approx(right.effect, abs=1e-12)
    assert left.statistic == pytest.approx(right.statistic, abs=1e-11)
    assert left.p_value == pytest.approx(right.p_value, abs=1e-12)
    assert left.decision_margin == pytest.approx(right.decision_margin, abs=1e-12)


def test_ci_query_canonicalizes_pair_and_conditioning_set():
    query = _query(0, 5, 2, (4, 1, 3))
    assert (query.x, query.y) == (2, 5)
    assert query.conditioning_set == (1, 3, 4)
    assert query.local_size == 5

    with pytest.raises(ValueError, match="duplicate"):
        _query(1, 0, 1, (2, 2))
    with pytest.raises(ValueError, match="non-negative"):
        CIQuery("bad", 0, 1, (), "test", "epoch", -1, 0)


@pytest.mark.parametrize("strategy", ["exact_size", "power_of_two"])
def test_cpu_batch_matches_scalar_for_mixed_conditioning_orders(strategy):
    data = np.random.default_rng(101).normal(size=(600, 7))
    scalar = GaussianCI(data)
    batch = GaussianBatchCI(data, batching_strategy=strategy)

    actual = batch.test_many(_queries())
    expected = [scalar.test(q.x, q.y, q.conditioning_set) for q in _queries()]

    for scalar_result, batch_result in zip(expected, actual, strict=True):
        _assert_results_close(scalar_result, batch_result)
    assert batch.last_diagnostics.query_count == len(_queries())
    assert batch.last_diagnostics.ci_arithmetic_work == sum(q.local_size**3 for q in _queries())
    assert batch.last_diagnostics.bucket_count == (5 if strategy == "exact_size" else 3)


def test_batch_result_is_invariant_to_composition_and_permutation():
    data = np.random.default_rng(102).normal(size=(500, 7))
    backend = GaussianBatchCI(data, batching_strategy="power_of_two")
    queries = _queries()
    together = dict(zip((q.query_id for q in queries), backend.test_many(queries), strict=True))
    reversed_results = backend.test_many(tuple(reversed(queries)))
    reversed_map = dict(zip((q.query_id for q in reversed(queries)), reversed_results, strict=True))

    for query in queries:
        _assert_results_close(together[query.query_id], reversed_map[query.query_id])
        _assert_results_close(together[query.query_id], backend.test_many((query,))[0])


def test_batch_matches_scalar_for_undefined_cases():
    rng = np.random.default_rng(103)
    base = rng.normal(size=(6, 3))
    data = np.column_stack((base, base[:, 0]))
    queries = (
        _query(0, 0, 1, (3,)),
        _query(1, 0, 1, (2, 3)),
    )
    scalar = GaussianCI(data)
    batch = GaussianBatchCI(data)

    actual = batch.test_many(queries)
    expected = [scalar.test(q.x, q.y, q.conditioning_set) for q in queries]

    assert [result.numerical_status for result in actual] == [
        result.numerical_status for result in expected
    ]
    assert [result.independent for result in actual] == [None, None]


def test_shared_s_matches_per_query_batch_backend():
    data = np.random.default_rng(104).normal(size=(700, 6))
    queries = (
        _query(0, 0, 1, (4, 5)),
        _query(1, 0, 2, (4, 5)),
        _query(2, 1, 3, (4, 5)),
    )
    ordinary = GaussianBatchCI(data).test_many(queries)
    shared_backend = GaussianBatchCI(data, shared_s_min_reuse=2)
    shared = shared_backend.test_many(queries)

    for expected, actual in zip(ordinary, shared, strict=True):
        _assert_results_close(expected, actual)
    assert shared_backend.last_diagnostics.shared_factorization_count == 1
    assert shared_backend.last_diagnostics.shared_work_saved_estimate > 0


@pytest.mark.parametrize(
    ("inversion", "ridge"),
    [("strict", 0.0), ("ridge", 1e-6), ("pinv", 0.0)],
)
def test_batch_matches_scalar_across_explicit_numerical_modes(inversion, ridge):
    rng = np.random.default_rng(107)
    data = rng.normal(size=(450, 5))
    data[:, 4] = data[:, 0] + 1e-10 * rng.normal(size=450)
    queries = (_query(0, 0, 1, (2, 4)), _query(1, 2, 3, (0, 4)))
    scalar = GaussianCI(data, inversion=inversion, ridge=ridge)
    batch = GaussianBatchCI(data, inversion=inversion, ridge=ridge)

    for expected, actual in zip(
        (scalar.test(q.x, q.y, q.conditioning_set) for q in queries),
        batch.test_many(queries),
        strict=True,
    ):
        _assert_results_close(expected, actual)


def test_memory_planner_respects_budget_and_splits_waves():
    one = plan_batch_memory(6, 1, 1_000_000)
    budget = one.bytes_per_query * 3
    plan = plan_batch_memory(6, 10, budget)

    assert plan.batch_capacity == 3
    assert plan.waves == 4
    assert plan.peak_workspace_bytes <= budget
    with pytest.raises(MemoryError):
        plan_batch_memory(6, 1, one.bytes_per_query - 1)


def test_empty_batch_is_a_valid_deterministic_noop():
    data = np.random.default_rng(108).normal(size=(100, 4))
    backend = GaussianBatchCI(data)

    assert backend.test_many(()) == []
    assert backend.last_diagnostics.query_count == 0


def test_batch_audit_is_deterministic_and_declares_reference_mode():
    data = np.random.default_rng(105).normal(size=(400, 7))
    first = audit_scalar_batch(data, _queries(), batching_strategy="power_of_two")
    second = audit_scalar_batch(data, _queries(), batching_strategy="power_of_two")

    assert first.status == "PASS"
    assert first.reference_mode == "tensor_backend"
    assert first.equality_target == "ci_result"
    assert asdict(first) == asdict(second)


@pytest.mark.parametrize("strategy", ["exact_size", "power_of_two"])
def test_randomized_scalar_batch_equivalence_grid(strategy):
    for seed in range(8):
        rng = np.random.default_rng(200 + seed)
        variables = 5 + seed % 4
        samples = 80 + 20 * seed
        data = rng.normal(size=(samples, variables))
        queries = []
        for rank in range(24):
            order = rank % min(4, variables - 1)
            permutation = rng.permutation(variables).tolist()
            queries.append(
                _query(
                    rank,
                    permutation[0],
                    permutation[1],
                    permutation[2 : 2 + order],
                )
            )
        summary = audit_scalar_batch(data, tuple(queries), batching_strategy=strategy)
        assert summary.status == "PASS"
        assert summary.decision_mismatches_outside_margin == 0
        assert summary.numerical_status_mismatches == 0
