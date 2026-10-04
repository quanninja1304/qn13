from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from ..graphs import skeleton_edges_from_pag


@dataclass(frozen=True)
class PAGComparison:
    nodes_equal: bool
    skeleton_equal: bool
    endpoint_matrix_equal: bool

    @property
    def exact(self) -> bool:
        return self.nodes_equal and self.endpoint_matrix_equal


def compare_canonical_pags(
    left: Mapping[str, object],
    right: Mapping[str, object],
) -> PAGComparison:
    """Compare canonical PAGs without conflating skeleton and endpoints."""

    left_nodes = tuple(left.get("nodes", ()))
    right_nodes = tuple(right.get("nodes", ()))
    nodes_equal = left_nodes == right_nodes
    skeleton_equal = nodes_equal and skeleton_edges_from_pag(dict(left)) == skeleton_edges_from_pag(dict(right))

    left_matrix = np.asarray(left.get("endpoint_matrix", ()), dtype=int)
    right_matrix = np.asarray(right.get("endpoint_matrix", ()), dtype=int)
    endpoint_matrix_equal = nodes_equal and left_matrix.shape == right_matrix.shape and bool(
        np.array_equal(left_matrix, right_matrix)
    )
    return PAGComparison(nodes_equal, skeleton_equal, endpoint_matrix_equal)


def canonical_conditioning_set(values: Sequence[int]) -> tuple[int, ...]:
    """Canonicalize a conditioning set while rejecting duplicate nodes."""

    canonical = tuple(sorted(values))
    if len(canonical) != len(set(canonical)):
        raise ValueError("A conditioning set cannot contain duplicate nodes")
    return canonical
