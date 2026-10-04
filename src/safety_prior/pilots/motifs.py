from __future__ import annotations

from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class ResearchMotif:
    name: str
    observed: tuple[int, ...]
    latent: tuple[int, ...]
    directed_edges: tuple[tuple[int, int], ...]
    purpose: str
    expected_failure: str | None = None

    def __post_init__(self) -> None:
        all_nodes = set(self.observed) | set(self.latent)
        if not self.observed:
            raise ValueError(f"Motif {self.name} needs observed nodes")
        if set(self.observed) & set(self.latent):
            raise ValueError(f"Motif {self.name} has observed/latent overlap")
        if any(source not in all_nodes or target not in all_nodes for source, target in self.directed_edges):
            raise ValueError(f"Motif {self.name} has an edge with an unknown node")
        if any(source == target for source, target in self.directed_edges):
            raise ValueError(f"Motif {self.name} has a self-edge")
        if not nx.is_directed_acyclic_graph(self.to_dag()):
            raise ValueError(f"Motif {self.name} is not a DAG")

    def to_dag(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_nodes_from(self.observed)
        graph.add_nodes_from(self.latent)
        graph.add_edges_from(self.directed_edges)
        return graph


def common_motif_catalog() -> tuple[ResearchMotif, ...]:
    """Return the frozen Sprint-0 motifs shared by both research directions."""

    return (
        ResearchMotif("chain", (0, 1, 2), (), ((0, 1), (1, 2)), "basic separator"),
        ResearchMotif("fork", (0, 1, 2), (), ((1, 0), (1, 2)), "common-cause separator"),
        ResearchMotif("collider", (0, 1, 2), (), ((0, 1), (2, 1)), "collider orientation"),
        ResearchMotif(
            "latent_confounder",
            (0, 1),
            (2,),
            ((2, 0), (2, 1)),
            "bidirected latent projection",
        ),
        ResearchMotif(
            "latent_mediator",
            (0, 1),
            (2,),
            ((0, 2), (2, 1)),
            "latent directed projection",
        ),
        ResearchMotif(
            "diamond",
            (0, 1, 2, 3),
            (),
            ((0, 1), (0, 2), (1, 3), (2, 3)),
            "cross-branch separator and block dependency",
            "naive local blocks can omit part of a separator",
        ),
        ResearchMotif(
            "future_confounder_claim",
            (0, 1, 2),
            (),
            ((2, 0), (2, 1)),
            "tier-envelope coverage failure",
            "excluding node 2 leaves a false adjacency between 0 and 1",
        ),
        ResearchMotif(
            "latent_diamond",
            (0, 1, 2, 3),
            (4,),
            ((0, 1), (0, 2), (1, 3), (2, 3), (4, 1), (4, 2)),
            "PDS/discriminating-path stress with latent confounding",
        ),
        ResearchMotif(
            "dynamic_snapshot_trace_gap",
            (0, 1, 2, 3),
            (4, 5),
            ((0, 1), (0, 2), (3, 1), (3, 2), (4, 1), (5, 0), (5, 1)),
            "ICD dynamic-versus-precomputed candidate trace regression",
            "precomputed radius-2 candidates execute four extra CI calls at pinned revision",
        ),
    )
