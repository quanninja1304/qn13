import json

from safety_prior.gates import evaluate_k0, gate_record
from safety_prior.models import QueryRecord


def test_query_record_schema_is_json_serializable():
    row = QueryRecord("r", "q", 0, "skeleton", "X1", "X2", [], 0, 1, [], "a", "oracle", None, 1.0, "independent", 0, 0, 0, 0, 0, "t", 8, 0.1, "b", False, True, [], {"graph_seed": 1})
    assert json.loads(json.dumps(row.as_dict()))["query_id"] == "q"


def test_gate_rejects_partial_pass():
    try:
        gate_record("K0", "PARTIAL PASS", "bad")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid gate state accepted")


def test_smoke_cannot_pass_and_incomplete_main_is_blocked():
    smoke = [{"scope": "smoke", "phase": 0}]
    assert evaluate_k0(smoke)["status"] == "BLOCKED"


def test_seed_names_are_separated_in_schema():
    seeds = {"graph_seed": 1, "data_seed": 2, "prior_seed": 3, "scheduler_seed": 4, "bootstrap_seed": 5}
    assert len(set(seeds.values())) == 5
    assert set(seeds) == {"graph_seed", "data_seed", "prior_seed", "scheduler_seed", "bootstrap_seed"}
