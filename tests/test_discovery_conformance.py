from causallearn.search.ConstraintBased.FCI import fci

from safety_prior.ci import OracleCI
from safety_prior.discovery import run_scheduled_fci
from safety_prior.graphs import canonical_pag, dummy_data, generate_dag, motif_graph
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

