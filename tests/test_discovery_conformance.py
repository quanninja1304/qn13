import json

import networkx as nx
import numpy as np
import pytest
from causallearn.search.ConstraintBased.FCI import fci

from safety_prior.ci import CIResult, GaussianCI, OracleCI, UndefinedCIResultError
from safety_prior.discovery import run_scheduled_fci, scheduled_fas
from safety_prior.graphs import canonical_pag, dummy_data, generate_dag, motif_graph
from safety_prior.provenance import ProvenanceLog
from safety_prior.schedulers import make_scheduler


def run(graph, scheduler_name="stable_default", seed=4, budget=None):
    ci = OracleCI(graph.dag, graph.observed)
    scheduler = make_scheduler(scheduler_name, seed, ci if scheduler_name == "oracle_query" else None)
    return run_scheduled_fci("test", [f"X{i+1}" for i in graph.observed], ci, scheduler, seed, graph.graph_seed, weighted_budget=budget)


def test_adapter_matches_upstream_on_known_motifs():
    for name in ("chain", "fork", "collider", "latent_confounder", "latent_mediator"):
        graph = motif_graph(name)
        state, _, _ = run(graph)
        upstream, _ = fci(dummy_data(len(graph.observed)), independence_test_method="d_separation", true_dag=graph.dag, node_names=[f"X{i+1}" for i in graph.observed], show_progress=False)
        assert state.graph == canonical_pag(upstream)


def test_random_full_budget_oracle_equivalence_and_replay():
    graph = generate_dag(7, 0.3, 2, 18)
    baseline, _, _ = run(graph)
    first, first_log, _ = run(graph, "random_valid", 91)
    second, second_log, _ = run(graph, "random_valid", 91)
    assert first.graph == baseline.graph == second.graph
    assert [q.query_id for q in first_log.queries] == [q.query_id for q in second_log.queries]


def test_budgeted_output_is_discovery_state_not_pag():
    graph = generate_dag(7, 0.3, 2, 19)
    state, _, _ = run(graph, budget=8)
    assert state.object_type == "DiscoveryState"
    assert not state.completed
    assert state.untested
    assert not state.graph["is_pag"]


def test_no_graph_event_uses_prior_as_evidence():
    graph = generate_dag(6, 0.2, 2, 8)
    _, provenance, _ = run(graph, "random_valid", 7)
    assert provenance.graph_events
    assert all(not event["prior_is_evidence"] for event in provenance.graph_events)


def test_union_of_valid_separators_can_open_a_collider_path():
    # X -> C1 <- M -> C2 <- Y: either collider alone remains closed, while
    # conditioning on both colliders opens the whole path.
    dag = nx.DiGraph([(0, 1), (2, 1), (2, 3), (4, 3)])
    ci = OracleCI(dag, (0, 1, 2, 3, 4))

    assert ci.test(0, 4, (1,)).independent is True
    assert ci.test(0, 4, (3,)).independent is True
    assert ci.test(0, 4, (1, 3)).independent is False


class _MultipleWitnessCI:
    backend = "test_multiple_witness"

    def test(self, i, j, conditioning_set):
        pair = tuple(sorted((i, j)))
        separator = tuple(conditioning_set)
        independent = pair == (0, 1) and separator in {(2,), (3,)}
        return CIResult(independent, 1.0 if independent else 0.0, None)


def _run_multiple_witness_skeleton(scheduler_name: str, seed: int):
    names = ["X0", "X1", "X2", "X3"]
    ci = _MultipleWitnessCI()
    scheduler = make_scheduler(scheduler_name, seed)
    provenance = ProvenanceLog("witness-test", names, ci.backend, {"scheduler_seed": seed})
    _, sep_sets, _, _, stopped = scheduled_fas(names, ci, scheduler, provenance, depth=1)
    return sep_sets, provenance, stopped


def test_skeleton_selects_one_canonical_witness_without_unioning_sepsets():
    stable_sets, stable_log, stable_stopped = _run_multiple_witness_skeleton("stable_default", 1)
    random_sets, random_log, random_stopped = _run_multiple_witness_skeleton("random_valid", 91)

    assert not stable_stopped and not random_stopped
    assert stable_sets[(0, 1)] == {2}
    assert random_sets[(0, 1)] == stable_sets[(0, 1)]

    for provenance in (stable_log, random_log):
        selected = [q for q in provenance.queries if q.separating_set_recorded]
        observed = [q for q in provenance.queries if q.independence_witness]
        event = next(e for e in provenance.graph_events if e["details"]["edge"] == ["X0", "X1"])
        assert len(observed) == 4
        assert len(selected) == 1
        assert selected[0].conditioning_set == ["X2"]
        assert selected[0].edge_removed is True
        assert all(not query.edge_removed for query in observed if query is not selected[0])
        assert event["evidence_query_ids"] == [selected[0].query_id]
        assert event["details"]["witness_query_id"] == selected[0].query_id
        assert event["details"]["witness_count"] == 4


class _UndefinedCI:
    backend = "test_undefined"

    def test(self, i, j, conditioning_set):
        return CIResult(None, None, None, None, "singular", None)


def test_undefined_ci_is_logged_and_aborts_before_graph_mutation():
    names = ["X0", "X1"]
    ci = _UndefinedCI()
    provenance = ProvenanceLog("undefined-test", names, ci.backend, {})

    with pytest.raises(UndefinedCIResultError, match="graph mutation aborted") as caught:
        scheduled_fas(names, ci, make_scheduler("stable_default", 1), provenance, depth=0)

    assert len(provenance.queries) == 1
    assert provenance.queries[0].ci_decision == "undefined"
    assert provenance.queries[0].ci_numerical_status == "singular"
    assert provenance.graph_events == []
    assert caught.value.as_dict()["terminal_status"] == "failed"
    assert caught.value.as_dict()["query_record"]["ci_decision"] == "undefined"
    json.dumps(caught.value.as_dict())


def test_discovery_rejects_a_mismatched_gaussian_decision_threshold():
    data = np.random.default_rng(31).normal(size=(100, 2))
    ci = GaussianCI(data, alpha=0.01)
    provenance = ProvenanceLog("alpha-test", ["X0", "X1"], ci.backend, {})

    with pytest.raises(ValueError, match="exactly match"):
        scheduled_fas(
            ["X0", "X1"],
            ci,
            make_scheduler("stable_default", 1),
            provenance,
            alpha=0.05,
            depth=0,
        )
