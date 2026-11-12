"""Oracle FCI with typed hard background knowledge (rules section 3.1-3.2), built on causal-learn 0.1.4.8 rule functions.

Skeleton and sepsets come from the true MAG (equivalent to FAS + Possible-D-SEP under a d-separation oracle);
sepset(a, c) = (An_G({a, c}) & O) \\ {a, c}, which d-separates a and c whenever they are non-adjacent in the MAG.
Injected marks are set before the collider step and kept immutable: any rule call that changes them is undone and
counted as an override conflict.

Endpoint convention (causal-learn GeneralGraph): graph[i, j] is the mark at node i on edge i-j;
-1 tail, 1 arrow, 2 circle.
"""
from __future__ import annotations

import contextlib
import io
from itertools import combinations

import networkx as nx
import numpy as np
from causallearn.graph.Edge import Edge
from causallearn.graph.Endpoint import Endpoint
from causallearn.graph.GeneralGraph import GeneralGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.search.ConstraintBased.FCI import rule8, rule9, rule10, ruleR3, ruleR4B, rulesR1R2cycle
from causallearn.utils.cit import CIT, d_separation

TAIL, ARROW, CIRCLE = -1, 1, 2


def relabel(g: nx.DiGraph, observed):
    """Return (dag with observed -> 0..k-1 in given order, latents after), list of observed names."""
    obs = list(observed)
    lat = [v for v in g.nodes if v not in set(obs)]
    mapping = {v: i for i, v in enumerate(obs + lat)}
    return nx.relabel_nodes(g, mapping), obs


def skeleton_and_sepsets(dag: nx.DiGraph, k: int):
    """MAG adjacency over observed 0..k-1 and An-set sepsets for non-adjacent pairs."""
    anc = {v: nx.ancestors(dag, v) for v in range(k)}
    obs = set(range(k))
    adj, sep = set(), {}
    for a, b in combinations(range(k), 2):
        z = ((anc[a] | anc[b]) & obs) - {a, b}
        if nx.is_d_separator(dag, {a}, {b}, z):
            sep[(a, b)] = set(z)
            sep[(b, a)] = set(z)
        else:
            adj.add((a, b))
    return adj, sep, anc


def _set_edge(G: GeneralGraph, nodes, i, j, end_i, end_j):
    e = G.get_edge(nodes[i], nodes[j])
    if e is not None:
        G.remove_edge(e)
    if end_i == ARROW and end_j != ARROW:
        i, j, end_i, end_j = j, i, end_j, end_i
    if end_i == CIRCLE and end_j == TAIL:
        i, j, end_i, end_j = j, i, end_j, end_i
    ok = G.add_edge(Edge(nodes[i], nodes[j], Endpoint(end_i), Endpoint(end_j)))
    if ok is False:
        raise RuntimeError(f"could not set edge {i}-{j} marks {end_i},{end_j}")


def run(dag: nx.DiGraph, k: int, injection=None):
    """injection: None, or dict(kind='directed', a=, b=) meaning a --> b, or dict(kind='bidirected', a=, b=).

    Returns dict with the final mark matrix M (k x k, M[i, j] = mark at i on edge i-j, 0 = no edge),
    origin[(i, j)] = rule that last set mark M[i, j], conflicts (blocked colliders, overrides, added edge on sepset pair).
    """
    adj, sep, anc = skeleton_and_sepsets(dag, k)
    nodes = [GraphNode(f"X{i}") for i in range(k)]
    for i, n in enumerate(nodes):
        n.add_attribute("id", i)
    G = GeneralGraph(nodes)
    for a, b in adj:
        G.add_edge(Edge(nodes[a], nodes[b], Endpoint.CIRCLE, Endpoint.CIRCLE))
    conflicts = {"blocked_collider": 0, "override": 0, "added_on_sepset_pair": 0}
    fixed = {}  # (i, j) -> mark at i on edge i-j
    if injection is not None:
        a, b = injection["a"], injection["b"]
        if (min(a, b), max(a, b)) not in adj:
            conflicts["added_on_sepset_pair"] = 1
        if injection["kind"] == "directed":
            fixed = {(a, b): TAIL, (b, a): ARROW}
        else:
            fixed = {(a, b): ARROW, (b, a): ARROW}
        _set_edge(G, nodes, a, b, fixed[(a, b)], fixed[(b, a)])
    origin = {}

    def mat():
        return np.array(G.graph, dtype=int).copy()

    def note(before, rule):
        after = mat()
        for i, j in zip(*np.nonzero(before != after)):
            origin[(int(i), int(j))] = rule
        return after

    def enforce():
        n = 0
        for (i, j), m in fixed.items():
            if G.graph[i, j] != m:
                n += 1
                _set_edge(G, nodes, i, j, fixed[(i, j)], fixed[(j, i)])
        return n

    # collider step (R0) on unshielded triples a *-* b *-* c with b not in sepset(a, c)
    before = mat()
    adjm = (G.graph != 0)
    for b in range(k):
        nbrs = [x for x in range(k) if adjm[b, x]]
        for a, c in combinations(nbrs, 2):
            if adjm[a, c]:
                continue
            if b in sep.get((a, c), set()):
                continue
            if any(fixed.get((b, x)) == TAIL for x in (a, c)):
                conflicts["blocked_collider"] += 1
                continue
            for x in (a, c):
                end_x = int(G.graph[x, b])
                if G.graph[b, x] != ARROW:
                    _set_edge(G, nodes, x, b, end_x, ARROW)
    before = note(before, "R0")

    data = np.empty(shape=(0, k))
    cit = CIT(data, method=d_separation, true_dag=dag)
    sep_idx = {key: set(v) for key, v in sep.items()}
    sink = io.StringIO()
    change = True
    guard = 0
    while change and guard < 200:
        guard += 1
        change = False
        with contextlib.redirect_stdout(sink):
            for name, call in (
                ("R1R2", lambda c: rulesR1R2cycle(G, None, c, False)),
                ("R3", lambda c: ruleR3(G, sep_idx, None, c, False)),
                ("R4", lambda c: ruleR4B(G, -1, data, cit, 0.05, sep_sets=sep_idx, change_flag=c, bk=None, verbose=False)),
                ("R8", lambda c: rule8(G, nodes=nodes, changeFlag=c)),
                ("R9", lambda c: rule9(G, nodes=nodes, changeFlag=c)),
                ("R10", lambda c: rule10(G, changeFlag=c)),
            ):
                change = call(change)
                ov = enforce()
                conflicts["override"] += ov
                before = note(before, name)
    return {"M": mat(), "origin": origin, "conflicts": conflicts, "adj": adj, "anc": anc, "loops": guard}


def errors(M: np.ndarray, anc: dict, k: int, exclude=None):
    """FA: tail at x on edge x-y but x not an ancestor of y. FNA: arrow at x but x is an ancestor of y."""
    fa, fna, wrong_edges = 0, 0, set()
    for x in range(k):
        for y in range(k):
            if x == y or M[x, y] == 0:
                continue
            if exclude is not None and {x, y} == set(exclude):
                continue
            x_anc_y = x in anc[y]
            if M[x, y] == TAIL and not x_anc_y:
                fa += 1
                wrong_edges.add((min(x, y), max(x, y)))
            elif M[x, y] == ARROW and x_anc_y:
                fna += 1
                wrong_edges.add((min(x, y), max(x, y)))
    return fa, fna, wrong_edges


def dag2pag_marks(dag: nx.DiGraph, k: int) -> np.ndarray:
    """Reference PAG from causal-learn dag2pag, as a k x k mark matrix indexed like run()."""
    from causallearn.graph.Dag import Dag
    from causallearn.utils.DAG2PAG import dag2pag
    n = dag.number_of_nodes()
    nodes = [GraphNode(f"X{i}") for i in range(n)]
    D = Dag(nodes)
    for u, v in dag.edges:
        D.add_directed_edge(nodes[u], nodes[v])
    with contextlib.redirect_stdout(io.StringIO()):
        P = dag2pag(D, [nodes[i] for i in range(k, n)])
    name_to_idx = {f"X{i}": i for i in range(k)}
    pnodes = P.get_nodes()
    M = np.zeros((k, k), dtype=int)
    for a in pnodes:
        for b in pnodes:
            if a is b:
                continue
            e = P.get_edge(a, b)
            if e is not None:
                M[name_to_idx[a.get_name()], name_to_idx[b.get_name()]] = int(e.get_proximal_endpoint(a).value)
    return M
