from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Protocol

import numpy as np

from .icd_reference import EndpointMark, ICDSepCandidate, PAGSnapshot


class TestableCI(Protocol):
    def test(self, i: int, j: int, conditioning_set: Iterable[int]): ...


class OfficialICDUnavailable(ImportError):
    pass


def _official_classes():
    try:
        from causal_discovery_algs import LearnStructICD
    except ImportError as exc:
        raise OfficialICDUnavailable(
            "Install the optional 'reference' dependency to use the pinned official ICD implementation"
        ) from exc
    return LearnStructICD


def official_icd_available() -> bool:
    try:
        _official_classes()
    except OfficialICDUnavailable:
        return False
    return True


class _BooleanCIAdapter:
    def __init__(self, ci_test: TestableCI):
        self._ci_test = ci_test
        self.queries: list[tuple[int, int, tuple[int, ...]]] = []

    def cond_indep(self, x: int, y: int, conditioning_set: Iterable[int]) -> bool:
        canonical_pair = (x, y) if x < y else (y, x)
        canonical_set = tuple(sorted(conditioning_set))
        self.queries.append((*canonical_pair, canonical_set))
        return bool(self._ci_test.test(x, y, canonical_set).independent)


def _official_matrix(snapshot: PAGSnapshot) -> np.ndarray:
    nodes = tuple(sorted(snapshot.nodes))
    index = {node: position for position, node in enumerate(nodes)}
    codes = {
        EndpointMark.CIRCLE: 1,
        EndpointMark.ARROW: 2,
        EndpointMark.TAIL: 3,
    }
    matrix = np.zeros((len(nodes), len(nodes)), dtype=int)
    for (left, right), (left_mark, right_mark) in snapshot.edge_marks.items():
        # causality-lab stores the mark at the column node.
        matrix[index[right], index[left]] = codes[left_mark]
        matrix[index[left], index[right]] = codes[right_mark]
    return matrix


def official_icd_sep_candidates(
    snapshot: PAGSnapshot,
    x: int,
    y: int,
    radius: int,
    *,
    require_possible_ancestor: bool = True,
) -> tuple[ICDSepCandidate, ...]:
    """Call the pinned official ICD candidate enumerator on a PAG snapshot."""

    LearnStructICD = _official_classes()

    class _NeverCalledCI:
        @staticmethod
        def cond_indep(*_args, **_kwargs):
            raise AssertionError("Candidate enumeration must not call CI")

    learner = LearnStructICD(set(snapshot.nodes), _NeverCalledCI())
    learner.graph.init_from_adj_mat(_official_matrix(snapshot), nodes_order=sorted(snapshot.nodes))
    learner.test_cond_ancestor = require_possible_ancestor
    raw = learner._get_pdsep_range_sets(x, y, radius)

    best_by_set: dict[tuple[int, ...], ICDSepCandidate] = {}
    for conditioning_set, distance_sum in raw:
        key = tuple(sorted(conditioning_set))
        candidate = ICDSepCandidate(key, int(distance_sum), min(x, y))
        previous = best_by_set.get(key)
        if previous is None or candidate.distance_sum < previous.distance_sum:
            best_by_set[key] = candidate
    return tuple(sorted(best_by_set.values(), key=lambda item: (item.distance_sum, item.conditioning_set)))


def _canonical_official_pag(graph) -> dict:
    nodes = sorted(graph.nodes_set)
    official = np.asarray(graph.get_adj_mat(), dtype=int)
    mark_map = np.asarray([0, 2, 1, -1], dtype=int)
    # Official matrix[row, column] stores the mark at the column node, while
    # causal-learn's canonical matrix[row, column] stores the mark at row.
    canonical = mark_map[official].T
    return {
        "nodes": [f"X{node + 1}" for node in nodes],
        "endpoint_matrix": canonical.tolist(),
        "is_pag": True,
    }


@dataclass(frozen=True)
class OfficialICDIteration:
    radius: int
    done: bool
    graph: dict
    sepsets: dict[tuple[int, int], tuple[int, ...]]
    queries: tuple[tuple[int, int, tuple[int, ...]], ...]


def run_official_icd(
    nodes: Iterable[int],
    ci_test: TestableCI,
    *,
    max_radius: int | None = None,
    precompute_candidates: bool = False,
    selection_bias: bool = False,
    tail_completeness: bool = True,
) -> tuple[OfficialICDIteration, ...]:
    """Run the pinned official ICD one iteration at a time.

    This adapter exposes the dynamic reference mode by default.  Setting
    ``precompute_candidates`` selects the official comparison mode rather than
    silently changing the reference semantics.
    """

    LearnStructICD = _official_classes()
    node_tuple = tuple(sorted(set(nodes)))
    ci_adapter = _BooleanCIAdapter(ci_test)
    learner = LearnStructICD(
        set(node_tuple),
        ci_adapter,
        is_pre_calc_cond_set=precompute_candidates,
        is_selection_bias=selection_bias,
        is_tail_completeness=tail_completeness,
    )

    results: list[OfficialICDIteration] = []
    while True:
        query_start = len(ci_adapter.queries)
        done, radius = learner.learn_structure_iteration()
        sepsets = {
            (left, right): tuple(sorted(learner.sepset.get_sepset(left, right)))
            for left, right in combinations(node_tuple, 2)
            if learner.sepset.get_sepset(left, right)
        }
        results.append(
            OfficialICDIteration(
                radius=radius,
                done=bool(done),
                graph=_canonical_official_pag(learner.graph),
                sepsets=sepsets,
                queries=tuple(ci_adapter.queries[query_start:]),
            )
        )
        if done or (max_radius is not None and radius >= max_radius):
            break
    return tuple(results)
