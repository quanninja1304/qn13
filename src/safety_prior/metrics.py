from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np

from .graphs import skeleton_edges_from_pag


def _prf(predicted: set, truth: set) -> dict[str, float | int]:
    tp = len(predicted & truth)
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def skeleton_metrics(predicted_pag: dict, reference_pag: dict) -> dict[str, float | int]:
    return _prf(skeleton_edges_from_pag(predicted_pag), skeleton_edges_from_pag(reference_pag))


def endpoint_metrics(predicted_pag: dict, reference_pag: dict) -> dict:
    if predicted_pag["nodes"] != reference_pag["nodes"]:
        raise ValueError("canonical node sets/order differ")
    p = np.asarray(predicted_pag["endpoint_matrix"], dtype=int)
    r = np.asarray(reference_pag["endpoint_matrix"], dtype=int)
    result = {}
    for name, code in (("tail", -1), ("arrowhead", 1)):
        result[name] = _prf(set(map(tuple, np.argwhere(p == code))), set(map(tuple, np.argwhere(r == code))))
    determined = np.isin(p, [-1, 1])
    result["wrong_determined_endpoints"] = int(np.sum(determined & (p != r)))
    result["circles"] = int(np.sum(p == 2))
    return result


def weighted_cost(conditioning_sets: Iterable[Iterable]) -> int:
    return sum((len(tuple(z)) + 2) ** 3 for z in conditioning_sets)


def cost_by_order(query_rows: Iterable[dict]) -> dict[int, dict[str, int]]:
    counts = Counter(int(row["conditioning_order"]) for row in query_rows)
    return {order: {"tests": count, "weighted_cost": count * (order + 2) ** 3} for order, count in sorted(counts.items())}


def bootstrap_ci(values: Iterable[float], seed: int, resamples: int = 10_000) -> tuple[float, float]:
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        raise ValueError("bootstrap needs observations")
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(resamples, values.size), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def bootstrap_median_ci(values: Iterable[float], seed: int, resamples: int = 10_000) -> tuple[float, float]:
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        raise ValueError("bootstrap needs observations")
    rng = np.random.default_rng(seed)
    samples = np.median(rng.choice(values, size=(resamples, values.size), replace=True), axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def tests_to_skeleton_target(query_rows: list[dict], reference_pag: dict, target: float = 0.95) -> int | None:
    nodes = reference_pag["nodes"]
    complete = {tuple(sorted((nodes[i], nodes[j]))) for i in range(len(nodes)) for j in range(i + 1, len(nodes))}
    truth = skeleton_edges_from_pag(reference_pag)
    removed: set[tuple[str, str]] = set()
    if _prf(complete, truth)["f1"] >= target:
        return 0
    for step, row in enumerate(query_rows, start=1):
        if row["ci_decision"] == "independent":
            removed.add(tuple(sorted((row["i"], row["j"]))))
        if _prf(complete - removed, truth)["f1"] >= target:
            return step
    return None


def query_signature(row: dict) -> tuple:
    return row["phase"], row["i"], row["j"], tuple(row["conditioning_set"])
