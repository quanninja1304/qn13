import pytest
from causallearn.search.ConstraintBased.FCI import fci

from safety_prior.algorithms.icd_reference import (
    EndpointMark,
    PAGSnapshot,
    enumerate_icd_sep_candidates,
)
from safety_prior.algorithms.icd_official_adapter import (
    official_icd_available,
    official_icd_sep_candidates,
    run_official_icd,
)
from safety_prior.ci import OracleCI
from safety_prior.graphs import canonical_pag, dummy_data, motif_graph
from safety_prior.pilots.motifs import common_motif_catalog


def test_radius_zero_returns_the_empty_conditioning_set_for_an_edge():
    graph = PAGSnapshot.circles((0, 1), ((0, 1),))
    candidates = enumerate_icd_sep_candidates(graph, 0, 1, 0)
    assert [candidate.conditioning_set for candidate in candidates] == [()]


def test_radius_one_uses_neighbors_of_either_endpoint():
    graph = PAGSnapshot.circles((0, 1, 2, 3), ((0, 1), (0, 2), (1, 3)))
    candidates = enumerate_icd_sep_candidates(graph, 0, 1, 1)
    assert {candidate.conditioning_set for candidate in candidates} == {(2,), (3,)}


def test_condition_2b_requires_a_pds_path_inside_the_conditioning_set():
    # The triangle 0-2-3-0 makes 0,2,3 a legal PDS path.  Node 4 is only
    # reachable through the non-collider, non-triangle triple 0-2-4.
    graph = PAGSnapshot.circles(
        (0, 1, 2, 3, 4),
        ((0, 1), (0, 2), (2, 3), (0, 3), (2, 4)),
    )
    candidates = enumerate_icd_sep_candidates(graph, 0, 1, 2)
    sets = {candidate.conditioning_set for candidate in candidates}
    assert (2, 3) in sets
    assert all(4 not in conditioning_set for conditioning_set in sets)


def test_definite_collider_extends_a_pds_path_without_a_triangle():
    graph = PAGSnapshot(
        nodes=(0, 1, 2, 3),
        edge_marks={
            (0, 1): (EndpointMark.CIRCLE, EndpointMark.CIRCLE),
            (0, 2): (EndpointMark.CIRCLE, EndpointMark.ARROW),
            (2, 3): (EndpointMark.ARROW, EndpointMark.CIRCLE),
        },
    )
    candidates = enumerate_icd_sep_candidates(
        graph,
        0,
        1,
        2,
        require_possible_ancestor=False,
    )
    assert (2, 3) in {candidate.conditioning_set for candidate in candidates}


def test_possible_ancestor_respects_endpoint_marks():
    graph = PAGSnapshot(
        nodes=(0, 1, 2),
        edge_marks={
            (0, 1): (EndpointMark.TAIL, EndpointMark.ARROW),
            (1, 2): (EndpointMark.TAIL, EndpointMark.ARROW),
        },
    )
    assert graph.is_possible_ancestor(0, 2)
    assert not graph.is_possible_ancestor(2, 0)


def test_snapshot_rejects_noncanonical_edges():
    with pytest.raises(ValueError, match="canonical"):
        PAGSnapshot((0, 1), {(1, 0): (EndpointMark.CIRCLE, EndpointMark.CIRCLE)})


@pytest.mark.skipif(not official_icd_available(), reason="optional pinned ICD reference is not installed")
@pytest.mark.parametrize("radius", [0, 1, 2])
def test_local_candidates_match_the_pinned_official_enumerator(radius):
    graph = PAGSnapshot.circles(
        (0, 1, 2, 3, 4),
        ((0, 1), (0, 2), (2, 3), (0, 3), (2, 4), (1, 4), (3, 4)),
    )
    local = enumerate_icd_sep_candidates(graph, 0, 1, radius)
    official = official_icd_sep_candidates(graph, 0, 1, radius)
    assert [(item.conditioning_set, item.distance_sum) for item in local] == [
        (item.conditioning_set, item.distance_sum) for item in official
    ]


@pytest.mark.skipif(not official_icd_available(), reason="optional pinned ICD reference is not installed")
@pytest.mark.parametrize("name", ["chain", "fork", "collider", "latent_confounder", "latent_mediator"])
def test_pinned_official_icd_matches_upstream_fci_on_base_motifs(name):
    case = motif_graph(name)
    final = run_official_icd(case.observed, OracleCI(case.dag, case.observed))[-1]
    upstream, _ = fci(
        dummy_data(len(case.observed)),
        independence_test_method="d_separation",
        true_dag=case.dag,
        node_names=[f"X{i + 1}" for i in case.observed],
        show_progress=False,
    )
    assert final.done
    assert final.graph == canonical_pag(upstream)


@pytest.mark.skipif(not official_icd_available(), reason="optional pinned ICD reference is not installed")
@pytest.mark.parametrize("name", ["chain", "fork", "collider", "latent_confounder", "latent_mediator"])
def test_dynamic_and_precomputed_official_modes_agree_on_base_motifs(name):
    case = motif_graph(name)
    ci = OracleCI(case.dag, case.observed)
    dynamic = run_official_icd(case.observed, ci, precompute_candidates=False)[-1].graph
    precomputed = run_official_icd(case.observed, ci, precompute_candidates=True)[-1].graph
    assert dynamic == precomputed


@pytest.mark.skipif(not official_icd_available(), reason="optional pinned ICD reference is not installed")
def test_dynamic_snapshot_trace_gap_is_frozen_without_an_output_mismatch():
    case = next(case for case in common_motif_catalog() if case.name == "dynamic_snapshot_trace_gap")
    ci = OracleCI(case.to_dag(), case.observed)
    dynamic = run_official_icd(case.observed, ci, precompute_candidates=False)
    precomputed = run_official_icd(case.observed, ci, precompute_candidates=True)

    assert dynamic[-1].graph == precomputed[-1].graph
    assert [len(iteration.queries) for iteration in dynamic] == [6, 10, 5, 0]
    assert [len(iteration.queries) for iteration in precomputed] == [6, 10, 9, 0]
    assert dynamic[2].queries != precomputed[2].queries
