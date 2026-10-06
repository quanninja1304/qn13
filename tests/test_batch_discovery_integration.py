import numpy as np

from safety_prior.ci import GaussianCI
from safety_prior.ci_batch import GaussianBatchCI
from safety_prior.discovery import run_scheduled_fci
from safety_prior.schedulers import make_scheduler


def _run(ci, run_id):
    return run_scheduled_fci(
        run_id,
        ["X0", "X1", "X2", "X3"],
        ci,
        make_scheduler("stable_default", 11),
        scheduler_seed=11,
        graph_seed=17,
        alpha=0.05,
    )


def test_cpu_batch_adapter_preserves_candidates_evidence_and_final_output():
    rng = np.random.default_rng(106)
    common = rng.normal(size=1200)
    data = np.column_stack(
        (
            common + 0.4 * rng.normal(size=1200),
            common + 0.4 * rng.normal(size=1200),
            rng.normal(size=1200),
            rng.normal(size=1200),
        )
    )
    scalar_state, scalar_log, _ = _run(GaussianCI(data), "scalar")
    batch_state, batch_log, _ = _run(
        GaussianBatchCI(data, batching_strategy="exact_size"), "batch"
    )

    assert batch_state.graph == scalar_state.graph
    scalar_trace = [
        (row.phase, row.i, row.j, tuple(row.conditioning_set), row.ci_decision)
        for row in scalar_log.queries
    ]
    batch_trace = [
        (row.phase, row.i, row.j, tuple(row.conditioning_set), row.ci_decision)
        for row in batch_log.queries
    ]
    assert batch_trace == scalar_trace
    assert [event["evidence_query_ids"] for event in batch_log.graph_events] == [
        event["evidence_query_ids"] for event in scalar_log.graph_events
    ]
