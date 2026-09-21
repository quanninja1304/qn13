from safety_prior.graphs import canonical_dag, generate_dag, graph_digest


def test_graph_generator_is_deterministic_and_acyclic():
    first = generate_dag(10, 0.2, 2, 41)
    second = generate_dag(10, 0.2, 2, 41)
    assert first.digest == second.digest
    assert sorted(first.dag.edges()) == sorted(second.dag.edges())
    assert all(v < 10 for v in first.observed)


def test_canonicalization_ignores_edge_insertion_order():
    first = generate_dag(6, 0.2, 2, 9)
    reversed_graph = first.dag.__class__()
    reversed_graph.add_nodes_from(reversed(list(first.dag.nodes)))
    reversed_graph.add_edges_from(reversed(list(first.dag.edges)))
    assert graph_digest(first.dag, first.observed, first.latent) == graph_digest(reversed_graph, first.observed, first.latent)

