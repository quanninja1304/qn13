from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import numpy as np


@dataclass(frozen=True)
class GeneratedGraph:
    dag: nx.DiGraph
    observed: tuple[int, ...]
    latent: tuple[int, ...]
    graph_seed: int
    parameters: dict
    digest: str


def canonical_dag(dag: nx.DiGraph, observed: Iterable[int], latent: Iterable[int]) -> dict:
    return {
        "nodes": sorted(int(n) for n in dag.nodes),
        "edges": sorted([int(a), int(b)] for a, b in dag.edges),
        "observed": sorted(int(n) for n in observed),
        "latent": sorted(int(n) for n in latent),
    }


def digest_object(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def graph_digest(dag: nx.DiGraph, observed: Iterable[int], latent: Iterable[int]) -> str:
    return digest_object(canonical_dag(dag, observed, latent))


def generate_dag(observed_nodes: int, latent_ratio: float, mean_degree: float, seed: int) -> GeneratedGraph:
    if observed_nodes < 2 or not 0 <= latent_ratio < 1 or mean_degree <= 0:
        raise ValueError("invalid graph-generator parameters")
    latent_count = max(1, int(round(observed_nodes * latent_ratio / (1 - latent_ratio)))) if latent_ratio else 0
    total = observed_nodes + latent_count
    rng = np.random.default_rng(seed)
    order = rng.permutation(total).tolist()
    probability = min(0.95, mean_degree / max(1, total - 1))
    dag = nx.DiGraph()
    dag.add_nodes_from(range(total))
    for pos, source in enumerate(order):
        for target in order[pos + 1 :]:
            if rng.random() < probability:
                dag.add_edge(int(source), int(target))
    observed = tuple(range(observed_nodes))
    latent = tuple(range(observed_nodes, total))
    params = {
        "observed_nodes": observed_nodes,
        "latent_ratio_target": latent_ratio,
        "latent_count": latent_count,
        "mean_degree_target": mean_degree,
        "edge_probability": probability,
    }
    return GeneratedGraph(dag, observed, latent, seed, params, graph_digest(dag, observed, latent))


def motif_graph(name: str) -> GeneratedGraph:
    """Hand-built full DAG motifs; observed nodes always precede latent nodes."""
    edges_by_name = {
        "chain": (3, (), [(0, 1), (1, 2)]),
        "fork": (3, (), [(1, 0), (1, 2)]),
        "collider": (3, (), [(0, 1), (2, 1)]),
        "collider_descendant": (4, (), [(0, 2), (1, 2), (2, 3)]),
        "two_paths": (4, (), [(0, 2), (2, 1), (0, 3), (3, 1)]),
        "minimal_separator_two": (4, (), [(0, 2), (2, 1), (0, 3), (3, 1)]),
        "latent_confounder": (2, (2,), [(2, 0), (2, 1)]),
        "latent_mediator": (2, (2,), [(0, 2), (2, 1)]),
    }
    if name not in edges_by_name:
        raise KeyError(name)
    observed_count, latent, edges = edges_by_name[name]
    dag = nx.DiGraph()
    dag.add_nodes_from(range(observed_count + len(latent)))
    dag.add_edges_from(edges)
    observed = tuple(range(observed_count))
    latent_tuple = tuple(latent)
    return GeneratedGraph(dag, observed, latent_tuple, -1, {"motif": name}, graph_digest(dag, observed, latent_tuple))


def canonical_pag(graph) -> dict:
    names = [node.get_name() for node in graph.get_nodes()]
    order = sorted(range(len(names)), key=lambda idx: names[idx])
    matrix = np.asarray(graph.graph, dtype=int)
    canonical = matrix[np.ix_(order, order)].tolist()
    return {"nodes": [names[idx] for idx in order], "endpoint_matrix": canonical, "is_pag": bool(graph.is_pag())}


def pag_digest(graph) -> str:
    return digest_object(canonical_pag(graph))


def skeleton_edges_from_pag(value: dict) -> set[tuple[str, str]]:
    nodes = value["nodes"]
    matrix = value["endpoint_matrix"]
    return {
        tuple(sorted((nodes[i], nodes[j])))
        for i in range(len(nodes))
        for j in range(i + 1, len(nodes))
        if matrix[i][j] != 0 or matrix[j][i] != 0
    }


def dummy_data(observed_nodes: int) -> np.ndarray:
    return np.zeros((max(2, observed_nodes), observed_nodes), dtype=float)

