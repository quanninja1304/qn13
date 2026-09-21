from safety_prior.models import PriorView, QueryCandidate
from safety_prior.schedulers import PriorGuided, RandomValid, StableDefault


def candidates():
    return [
        QueryCandidate("q1", (0, 1), (), "skeleton", 0, (), "s", 8),
        QueryCandidate("q2", (0, 2), (1,), "skeleton", 1, ("b0",), "s", 27),
    ]


def test_scheduler_selects_only_eligible_and_ties_are_deterministic():
    eligible = candidates()
    a = RandomValid(7).select(eligible, {})
    b = RandomValid(7).select(list(reversed(eligible)), {})
    assert a in eligible
    assert a == b


def test_stable_default_is_input_order_independent():
    assert StableDefault(1).select(candidates(), {}) == StableDefault(1).select(list(reversed(candidates())), {})


def test_prior_changes_order_not_graph_state():
    state = {"graph_digest": "before"}
    selected = PriorGuided(1).select(candidates(), state, PriorView({"q2": 2.0}, "test"))
    assert selected.query_id == "q2"
    assert state == {"graph_digest": "before"}

