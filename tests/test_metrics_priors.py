import numpy as np

from safety_prior.metrics import bootstrap_ci, endpoint_metrics, weighted_cost
from safety_prior.priors import corrupt_claims, ranking_auc


def test_weighted_cost_accounting():
    assert weighted_cost([(), (1,), (1, 2)]) == 8 + 27 + 64


def test_endpoint_evaluator_known_graphs():
    reference = {"nodes": ["X1", "X2"], "endpoint_matrix": [[0, 1], [-1, 0]], "is_pag": True}
    predicted = {"nodes": ["X1", "X2"], "endpoint_matrix": [[0, 2], [-1, 0]], "is_pag": True}
    result = endpoint_metrics(predicted, reference)
    assert result["wrong_determined_endpoints"] == 0
    assert result["circles"] == 1
    wrong = {"nodes": ["X1", "X2"], "endpoint_matrix": [[0, -1], [-1, 0]], "is_pag": True}
    assert endpoint_metrics(wrong, reference)["wrong_determined_endpoints"] == 1


def test_auc_and_calibration_independent_node_and_motif():
    claims = {(0, 1, z): z % 2 for z in range(20)}
    for mode in ("independent", "node_correlated", "motif_correlated"):
        scores, auc, metadata = corrupt_claims(claims, 0.65, 3, mode)
        assert set(scores) == set(claims)
        assert auc is not None
        assert abs(auc - 0.65) <= 0.02
        assert metadata["calibration_status"] == "PASS"


def test_auc_requires_both_classes():
    assert ranking_auc([1, 1], [0.1, 0.2]) is None


def test_bootstrap_uses_graph_level_values_deterministically():
    assert bootstrap_ci([1, 2, 3], 9, 100) == bootstrap_ci([1, 2, 3], 9, 100)

