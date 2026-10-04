import pytest

from safety_prior.tiers.reference import (
    TierOrdering,
    robust_pds_envelope,
    simple_tfci_adjacency_candidates,
    simple_tfci_pds_candidates,
)


def test_past_and_joint_past_follow_the_paper_definition():
    tiering = TierOrdering({0: 1, 1: 2, 2: 2, 3: 3})
    assert tiering.past(0) == frozenset({0})
    assert tiering.past(1) == frozenset({0, 1, 2})
    assert tiering.joint_past(0, 1) == frozenset({0, 1, 2})


def test_simple_tfci_intersects_pds_with_joint_past():
    tiering = TierOrdering({0: 1, 1: 2, 2: 2, 3: 3, 4: 1})
    restricted = simple_tfci_pds_candidates({2, 3, 4}, 0, 1, tiering)
    assert restricted == frozenset({2, 4})


def test_simple_tfci_first_stage_uses_the_source_specific_past():
    tiering = TierOrdering({0: 1, 1: 3, 2: 2, 3: 1})
    source_zero = simple_tfci_adjacency_candidates({1, 2, 3}, 0, 1, tiering)
    source_one = simple_tfci_adjacency_candidates({0, 2, 3}, 1, 0, tiering)
    assert source_zero == frozenset({3})
    assert source_one == frozenset({2, 3})


def test_robust_envelope_is_the_union_over_feasible_tierings():
    first = TierOrdering({0: 1, 1: 1, 2: 2, 3: 1})
    second = TierOrdering({0: 2, 1: 2, 2: 1, 3: 3})
    envelope = robust_pds_envelope({2, 3}, 0, 1, (first, second))
    assert envelope == frozenset({2, 3})


def test_empty_feasible_set_forces_an_explicit_fallback():
    with pytest.raises(ValueError, match="fall back"):
        robust_pds_envelope({2}, 0, 1, ())


def test_missing_tier_is_rejected_instead_of_silently_dropped():
    with pytest.raises(ValueError, match="missing"):
        simple_tfci_pds_candidates({2}, 0, 1, TierOrdering({0: 1, 1: 2}))
