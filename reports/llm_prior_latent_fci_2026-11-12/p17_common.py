"""Shared primitives for the P17 pilots (P-A, P-B). Semantics follow PA_PB_reading_rules_vi.md (locked 12/11/2026).

- parse_bif:        structure-only reader for bnlearn .bif files (untrusted input; run callers with python -I).
- hide_variables:   latent selection per rules section 2.2.
- mag_from_dag:     MAG over the observed variables of a DAG with latents (rules section 2.3).
                    Adjacency criterion: A, B adjacent  <=>  d-connected given (An_G({A,B}) & O) \\ {A,B}.
                    Justification (moralisation argument): X, Y are d-separated by Z iff separated in the moral graph of
                    G restricted to An({X,Y} | Z). With Z = (An({X,Y}) & O) \\ {X,Y}, every non-latent vertex of that
                    ancestral subgraph other than X, Y is in Z, so X and Y are connected iff some moral path runs through
                    latent ancestors only. Enlarging Z' (any subset of O) only enlarges the ancestral subgraph and its moral
                    graph, so such a latent-only path survives, and no Z' subset of O separates X and Y. Conversely, if the
                    criterion separates them, Z itself is a separating subset of O. The rules still require an exhaustive
                    cross-check on every graph with |O| <= 12 (see verify_adjacency_criterion).
- pair_class:       D / B / I / N classification of an observed pair.
"""
from __future__ import annotations

import math
import random
import re
from itertools import combinations
from pathlib import Path

import networkx as nx

BIF_VAR = re.compile(r"^\s*variable\s+(\S+)\s*\{", re.M)
BIF_PROB = re.compile(r"^\s*probability\s*\(\s*([^|)]+?)\s*(?:\|\s*([^)]*?))?\s*\)", re.M)

MARK_DIRECTED = "-->"   # a --> b : a is an ancestor of b
MARK_BIDIRECTED = "<->"  # a <-> b : neither is an ancestor of the other


def parse_bif(path) -> nx.DiGraph:
    """Return the DAG encoded by a .bif file; raises if names mismatch or the graph is cyclic."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    names = BIF_VAR.findall(text)
    if not names:
        raise ValueError(f"no 'variable' blocks found in {path}")
    g = nx.DiGraph()
    g.add_nodes_from(names)
    n_blocks = 0
    for m in BIF_PROB.finditer(text):
        n_blocks += 1
        child = m.group(1).strip()
        parents = [p.strip() for p in (m.group(2) or "").split(",") if p.strip()]
        if child not in g:
            raise ValueError(f"probability block for unknown variable {child!r} in {path}")
        for p in parents:
            if p not in g:
                raise ValueError(f"unknown parent {p!r} of {child!r} in {path}")
            g.add_edge(p, child)
    if n_blocks != len(names):
        raise ValueError(f"{path}: {len(names)} variables but {n_blocks} probability blocks")
    if not nx.is_directed_acyclic_graph(g):
        raise ValueError(f"{path}: graph is not acyclic")
    return g


def ancestors_map(g: nx.DiGraph, nodes) -> dict:
    return {v: nx.ancestors(g, v) for v in nodes}


def mag_from_dag(g: nx.DiGraph, observed, exhaustive: bool = False) -> dict:
    """Return {frozenset({a, b}): (tail_node_or_None, mark)} for every adjacent observed pair.

    For a directed MAG edge the tuple is (a, '-->') meaning a --> b (a ancestor of b).
    For a bidirected edge the tuple is (None, '<->').
    exhaustive=True checks every subset of O \\ {a, b} (only sensible for |O| <= 12).
    """
    obs = list(observed)
    obs_set = set(obs)
    anc = ancestors_map(g, obs)
    edges = {}
    for a, b in combinations(obs, 2):
        if exhaustive:
            others = [v for v in obs if v not in (a, b)]
            separable = any(
                nx.is_d_separator(g, {a}, {b}, set(z))
                for r in range(len(others) + 1)
                for z in combinations(others, r)
            )
        else:
            d_set = ((anc[a] | anc[b]) & obs_set) - {a, b}
            separable = nx.is_d_separator(g, {a}, {b}, d_set)
        if separable:
            continue
        if a in anc[b]:
            edges[frozenset((a, b))] = (a, MARK_DIRECTED)
        elif b in anc[a]:
            edges[frozenset((a, b))] = (b, MARK_DIRECTED)
        else:
            edges[frozenset((a, b))] = (None, MARK_BIDIRECTED)
    return edges


def pair_class(a, b, mag_edges: dict, anc: dict) -> str:
    """D: adjacent directed; B: adjacent bidirected; I: non-adjacent but ancestrally related; N: neither."""
    key = frozenset((a, b))
    if key in mag_edges:
        return "D" if mag_edges[key][1] == MARK_DIRECTED else "B"
    if a in anc[b] or b in anc[a]:
        return "I"
    return "N"


def classify_pairs(g: nx.DiGraph, observed, mag_edges: dict) -> dict:
    obs = list(observed)
    anc = ancestors_map(g, obs)
    return {frozenset((a, b)): pair_class(a, b, mag_edges, anc) for a, b in combinations(obs, 2)}


def hide_variables(g: nx.DiGraph, seed: int, min_b_pairs: int = 1, max_redraws: int = 5) -> dict:
    """Latent selection per rules section 2.2. Returns dict(latent=set, observed=list, draws=int, seed_used=int)."""
    nodes = sorted(g.nodes)
    k = max(2, math.ceil(0.25 * len(nodes)))
    for attempt in range(max_redraws + 1):
        seed_used = seed + 100 * attempt
        rng = random.Random(seed_used)
        multi_child = sorted(v for v in nodes if g.out_degree(v) >= 2)
        if len(multi_child) >= k:
            latent = set(rng.sample(multi_child, k))
        else:
            latent = set(multi_child)
            rest = [v for v in nodes if v not in latent]
            latent |= set(rng.sample(rest, k - len(latent)))
        observed = [v for v in nodes if v not in latent]
        mag = mag_from_dag(g, observed)
        n_b = sum(1 for _, m in mag.values() if m == MARK_BIDIRECTED)
        if n_b >= min_b_pairs:
            return {"latent": latent, "observed": observed, "draws": attempt + 1, "seed_used": seed_used, "n_B": n_b}
    return {"latent": None, "observed": None, "draws": max_redraws + 1, "seed_used": None, "n_B": 0}


def random_dag(n: int, mean_degree: float, seed: int) -> nx.DiGraph:
    """Erdos-Renyi DAG on a random order; expected total degree ~ mean_degree."""
    rng = random.Random(seed)
    order = list(range(n))
    rng.shuffle(order)
    p = min(1.0, mean_degree / max(1, n - 1))
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                g.add_edge(order[i], order[j])
    return g


def verify_adjacency_criterion(g: nx.DiGraph, observed) -> bool:
    """True iff the An-set criterion and the exhaustive check give the same MAG (edges and marks)."""
    return mag_from_dag(g, observed, exhaustive=False) == mag_from_dag(g, observed, exhaustive=True)
