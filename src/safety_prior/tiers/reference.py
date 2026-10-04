from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class TierOrdering:
    """A total assignment of observed nodes to positive integer tiers."""

    tiers: Mapping[int, int]

    def __post_init__(self) -> None:
        if not self.tiers:
            raise ValueError("A tier ordering cannot be empty")
        if any(not isinstance(node, int) for node in self.tiers):
            raise TypeError("Tier node identifiers must be integers")
        if any(not isinstance(tier, int) or tier < 1 for tier in self.tiers.values()):
            raise ValueError("Tier values must be positive integers")

    @property
    def nodes(self) -> frozenset[int]:
        return frozenset(self.tiers)

    def past(self, node: int) -> frozenset[int]:
        cutoff = self.tiers[node]
        return frozenset(candidate for candidate, tier in self.tiers.items() if tier <= cutoff)

    def joint_past(self, *nodes: int) -> frozenset[int]:
        if not nodes:
            raise ValueError("joint_past requires at least one node")
        cutoff = max(self.tiers[node] for node in nodes)
        return frozenset(candidate for candidate, tier in self.tiers.items() if tier <= cutoff)


def _validate_pair_and_candidates(
    candidates: Iterable[int],
    x: int,
    y: int,
    tiering: TierOrdering,
) -> frozenset[int]:
    if x == y:
        raise ValueError("A tested pair must contain distinct nodes")
    candidate_set = frozenset(candidates)
    required = candidate_set | {x, y}
    missing = required - tiering.nodes
    if missing:
        raise ValueError(f"Tier ordering is missing nodes: {sorted(missing)}")
    return candidate_set - {x, y}


def simple_tfci_pds_candidates(
    pds_candidates: Iterable[int],
    x: int,
    y: int,
    tiering: TierOrdering,
) -> frozenset[int]:
    """Return the simple-tFCI PDS restriction for a tested pair.

    The restriction is ``PDS(X,Y) intersect past_tau({X,Y})`` as used by the
    oracle simple tFCI algorithm.  This function intentionally performs no
    tier-based orientation.
    """

    candidate_set = _validate_pair_and_candidates(pds_candidates, x, y, tiering)
    return candidate_set & tiering.joint_past(x, y)


def simple_tfci_adjacency_candidates(
    adjacent_to_source: Iterable[int],
    source: int,
    target: int,
    tiering: TierOrdering,
) -> frozenset[int]:
    """Return the first-stage simple-tFCI pool for an ordered pair.

    The tFCI pseudo-algorithm checks subsets of
    ``adj(source) intersect past_tau(source) minus {target}``.  Calling this
    function for both ordered pairs recovers the two endpoint-specific pools.
    """

    candidate_set = _validate_pair_and_candidates(adjacent_to_source, source, target, tiering)
    return candidate_set & tiering.past(source)


def robust_pds_envelope(
    pds_candidates: Iterable[int],
    x: int,
    y: int,
    feasible_tierings: Iterable[TierOrdering],
) -> frozenset[int]:
    """Union simple-tFCI candidates over an explicit feasible tiering set.

    This brute-force function is the Sprint-0 oracle for later SAT/ILP or DP
    implementations.  An empty feasible set is rejected so callers must make
    the full-PDS fallback explicit.
    """

    tierings = tuple(feasible_tierings)
    if not tierings:
        raise ValueError("No feasible tiering; caller must fall back to full PDS")
    envelope: set[int] = set()
    for tiering in tierings:
        envelope.update(simple_tfci_pds_candidates(pds_candidates, x, y, tiering))
    return frozenset(envelope)
