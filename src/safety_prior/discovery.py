from __future__ import annotations

import time
from dataclasses import asdict
from itertools import combinations
from typing import Iterable

import numpy as np
from causallearn.graph.Endpoint import Endpoint
from causallearn.graph.GraphClass import CausalGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.search.ConstraintBased import FCI as upstream
from causallearn.utils.PCUtils.Helper import append_value

from .graphs import canonical_pag, digest_object, pag_digest
from .ci import UndefinedCIResultError
from .models import DiscoveryState, PAGResult, PriorView, QueryCandidate, SeparationWitness
from .provenance import LoggedCIProxy, ProvenanceLog
from .schedulers import Scheduler


def _raw_graph_digest(graph) -> str:
    return digest_object({"nodes": [n.get_name() for n in graph.get_nodes()], "matrix": np.asarray(graph.graph, dtype=int).tolist()})


def _degrees(graph) -> dict[int, int]:
    matrix = np.asarray(graph.graph)
    return {i: int(np.count_nonzero(matrix[i])) for i in range(matrix.shape[0])}


def _remove(graph, x: int, y: int) -> None:
    edge = graph.get_edge(graph.nodes[x], graph.nodes[y])
    if edge is not None:
        graph.remove_edge(edge)


def _candidates(graph, depth: int, state_digest: str) -> list[QueryCandidate]:
    matrix = np.asarray(graph.graph)
    result: list[QueryCandidate] = []
    prereq = () if depth == 0 else (f"barrier:skeleton:{depth - 1}",)
    for x in range(matrix.shape[0]):
        neighbors = tuple(int(v) for v in np.flatnonzero(matrix[x]))
        for y in neighbors:
            without_y = tuple(v for v in neighbors if v != y)
            for z in combinations(without_y, depth):
                qid = f"skeleton:{depth}:{x}:{y}:{','.join(map(str, z))}"
                result.append(QueryCandidate(qid, (x, y), tuple(z), "skeleton", depth, prereq, state_digest, (depth + 2) ** 3))
    return result


def scheduled_fas(
    node_names: list[str], ci, scheduler: Scheduler, provenance: ProvenanceLog,
    alpha: float = 0.05, depth: int = -1, prior: PriorView | None = None,
    weighted_budget: int | None = None,
):
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    ci_alpha = getattr(ci, "alpha", None)
    if ci_alpha is not None and not np.isclose(float(ci_alpha), float(alpha), rtol=0.0, atol=0.0):
        raise ValueError("discovery alpha must exactly match the CI decision alpha")
    cg = CausalGraph(len(node_names), node_names)
    sep_sets: dict[tuple[int, int], set[int]] = {}
    used_weighted = 0
    untested: list[QueryCandidate] = []
    current_depth = -1
    max_depth = float("inf") if depth == -1 else depth
    provisional_removed: set[tuple[int, int]] = set()
    stopped = False

    while cg.max_degree() - 1 > current_depth and current_depth < max_depth:
        current_depth += 1
        before_level = _raw_graph_digest(cg.G)
        candidates = _candidates(cg.G, current_depth, before_level)
        canonical_rank = {candidate.query_id: rank for rank, candidate in enumerate(candidates)}
        state_view = {"graph_digest": before_level, "degrees": _degrees(cg.G), "depth": current_depth}
        ordered = scheduler.order(candidates, state_view, prior)
        pair_witnesses: dict[tuple[int, int], list[SeparationWitness]] = {}
        for index, (candidate, score) in enumerate(ordered):
            if weighted_budget is not None and used_weighted + candidate.estimated_cost > weighted_budget:
                untested.extend(c for c, _ in ordered[index:])
                stopped = True
                break
            if candidate not in candidates:
                raise RuntimeError("scheduler selected an ineligible query")
            start = time.perf_counter()
            result = ci.test(*candidate.pair, candidate.conditioning_set)
            elapsed = (time.perf_counter() - start) * 1000
            used_weighted += candidate.estimated_cost
            x, y = candidate.pair
            if result.independent:
                key = tuple(sorted((x, y)))
                provisional_removed.add(key)
                pair_witnesses.setdefault(key, []).append(
                    SeparationWitness(
                        key,
                        candidate.conditioning_set,
                        candidate.query_id,
                        canonical_rank[candidate.query_id],
                    )
                )
            query_record = provenance.record_query(
                candidate,
                score,
                result,
                len(candidates) - index,
                before_level,
                elapsed,
                provisional_removed,
            )
            if result.independent is None:
                raise UndefinedCIResultError(
                    candidate.query_id,
                    getattr(result, "numerical_status", "unknown"),
                    query_record.as_dict(),
                )
        if stopped:
            break
        for (x, y), witnesses in sorted(pair_witnesses.items()):
            witness = min(witnesses, key=lambda item: (item.canonical_rank, item.query_id))
            separator = witness.conditioning_set
            provenance.mark_separating_set_recorded(witness.query_id)
            before = _raw_graph_digest(cg.G)
            _remove(cg.G, x, y)
            append_value(cg.sepset, x, y, tuple(sorted(separator)))
            append_value(cg.sepset, y, x, tuple(sorted(separator)))
            sep_sets[(x, y)] = set(separator)
            sep_sets[(y, x)] = set(separator)
            after = _raw_graph_digest(cg.G)
            provenance.graph_event(
                "edge_removal",
                "stable_fas_depth_barrier",
                before,
                after,
                [witness.query_id],
                {
                    "edge": [node_names[x], node_names[y]],
                    "separator": [node_names[z] for z in separator],
                    "depth": current_depth,
                    "witness_query_id": witness.query_id,
                    "witness_count": len(witnesses),
                    "selection_policy": "minimum_frozen_candidate_rank",
                },
            )
        # Record empty sepset observations in the same container shape expected by FCI.
        for candidate in candidates:
            x, y = candidate.pair
            if cg.sepset[x, y] is None:
                append_value(cg.sepset, x, y, ())

    return cg.G, sep_sets, untested, used_weighted, stopped


def _log_stage_delta(provenance: ProvenanceLog, graph, rule: str, before_matrix: np.ndarray) -> None:
    after_matrix = np.asarray(graph.graph, dtype=int).copy()
    changes = np.argwhere(before_matrix != after_matrix)
    if changes.size:
        provenance.graph_event("orientation_or_graph_update", rule, digest_object(before_matrix.tolist()), digest_object(after_matrix.tolist()), [q.query_id for q in provenance.queries if q.separating_set_recorded], {"changed_endpoints": changes.tolist()})


def run_scheduled_fci(
    run_id: str,
    node_names: list[str],
    ci,
    scheduler: Scheduler,
    scheduler_seed: int,
    graph_seed: int,
    prior_seed: int | None = None,
    prior: PriorView | None = None,
    alpha: float = 0.05,
    depth: int = -1,
    max_path_length: int = -1,
    weighted_budget: int | None = None,
):
    provenance = ProvenanceLog(run_id, node_names, ci.backend, {"graph_seed": graph_seed, "data_seed": None, "prior_seed": prior_seed, "scheduler_seed": scheduler_seed, "bootstrap_seed": None})
    graph, sep_sets, untested, used_weighted, stopped = scheduled_fas(node_names, ci, scheduler, provenance, alpha, depth, prior, weighted_budget)
    budget = {"raw_ci_tests": len(provenance.queries), "weighted_cost": used_weighted, "weighted_limit": weighted_budget}
    if stopped:
        state = DiscoveryState({"nodes": node_names, "endpoint_matrix": np.asarray(graph.graph, dtype=int).tolist(), "is_pag": False}, [q.as_dict() for q in provenance.queries], [asdict(q) for q in untested], budget, False)
        return state, provenance, graph

    upstream.reorientAllWith(graph, Endpoint.CIRCLE)
    nodes = list(graph.get_nodes())
    before = np.asarray(graph.graph, dtype=int).copy()
    upstream.rule0(graph, nodes, sep_sets, None, False)
    _log_stage_delta(provenance, graph, "FCI_rule0_pre_possible_dsep", before)

    logged_ci = LoggedCIProxy(ci, provenance, lambda: _raw_graph_digest(graph), "possible_dsep")
    before = np.asarray(graph.graph, dtype=int).copy()
    upstream.removeByPossibleDsep(graph, logged_ci, alpha, sep_sets)
    _log_stage_delta(provenance, graph, "FCI_possible_dsep", before)

    upstream.reorientAllWith(graph, Endpoint.CIRCLE)
    before = np.asarray(graph.graph, dtype=int).copy()
    upstream.rule0(graph, nodes, sep_sets, None, False)
    _log_stage_delta(provenance, graph, "FCI_rule0_post_possible_dsep", before)
    change = True
    first = True
    while change:
        before = np.asarray(graph.graph, dtype=int).copy()
        change = False
        change = upstream.rulesR1R2cycle(graph, None, change, False)
        change = upstream.ruleR3(graph, sep_sets, None, change, False)
        if change:
            change = upstream.ruleR4B(graph, max_path_length, np.zeros((max(2, len(node_names)), len(node_names))), logged_ci, alpha, sep_sets, change, None, False)
            first = False
        change = upstream.ruleR5(graph, change, False)
        change = upstream.ruleR6(graph, change, False)
        change = upstream.ruleR7(graph, change, False)
        change = upstream.rule8(graph, nodes, change)
        change = upstream.rule9(graph, nodes, change)
        change = upstream.rule10(graph, change)
        _log_stage_delta(provenance, graph, "FCI_rules_R1_R10", before)
    graph.set_pag(True)
    budget = {"raw_ci_tests": len(provenance.queries), "weighted_cost": sum(q.estimated_cost for q in provenance.queries), "weighted_limit": weighted_budget}
    # Keep the authoritative records in the provenance object without making a
    # second deep copy. Large dense graphs can produce hundreds of thousands of
    # records; duplicating them here is instrumentation-only memory overhead.
    state = PAGResult(canonical_pag(graph), provenance.queries, [], budget)
    return state, provenance, graph
