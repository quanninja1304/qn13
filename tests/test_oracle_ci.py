import pytest

from safety_prior.ci import OracleCI
from safety_prior.graphs import motif_graph


def oracle(name):
    graph = motif_graph(name)
    return OracleCI(graph.dag, graph.observed)


def test_chain_and_fork_blocked_by_middle():
    for name in ("chain", "fork"):
        ci = oracle(name)
        assert not ci.test(0, 2, ()).independent
        assert ci.test(0, 2, (1,)).independent


def test_collider_opens_when_conditioned():
    ci = oracle("collider")
    assert ci.test(0, 2, ()).independent
    assert not ci.test(0, 2, (1,)).independent


def test_collider_descendant_opens_path():
    ci = oracle("collider_descendant")
    assert ci.test(0, 1, ()).independent
    assert not ci.test(0, 1, (3,)).independent


def test_latent_confounder_and_mediator_are_not_conditioned_implicitly():
    assert not oracle("latent_confounder").test(0, 1, ()).independent
    assert not oracle("latent_mediator").test(0, 1, ()).independent


def test_two_paths_only_one_blocked_remains_dependent():
    ci = oracle("two_paths")
    assert not ci.test(0, 1, (2,)).independent
    assert ci.test(0, 1, (2, 3)).independent


def test_minimal_separator_has_multiple_members():
    ci = oracle("minimal_separator_two")
    assert not ci.test(0, 1, (2,)).independent
    assert not ci.test(0, 1, (3,)).independent
    assert ci.test(0, 1, (2, 3)).independent


def test_latent_variable_rejected_from_conditioning_set():
    graph = motif_graph("latent_confounder")
    with pytest.raises(ValueError):
        OracleCI(graph.dag, graph.observed).test(0, 1, (2,))

