from __future__ import annotations

from itertools import combinations

import numpy as np
from sklearn.metrics import roc_auc_score

from .models import PriorView, QueryCandidate


def ranking_auc(labels, scores) -> float | None:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if labels.size == 0 or np.unique(labels).size < 2:
        return None
    return float(roc_auc_score(labels, scores))


def minimal_separator_membership(oracle, observed: tuple[int, ...], max_size: int = 3) -> dict[tuple[int, int, int], int]:
    claims: dict[tuple[int, int, int], int] = {}
    for i, j in combinations(observed, 2):
        others = tuple(v for v in observed if v not in (i, j))
        minimal: list[frozenset[int]] = []
        for size in range(min(max_size, len(others)) + 1):
            for z in combinations(others, size):
                zs = frozenset(z)
                if any(existing <= zs for existing in minimal):
                    continue
                if oracle.test(i, j, z).independent:
                    minimal.append(zs)
        for z in others:
            claims[(i, j, z)] = int(any(z in separator for separator in minimal))
    return claims


def corrupt_claims(claims: dict, target_auc: float, seed: int, mode: str = "independent", blind_fraction: float = 0.2) -> tuple[dict, float | None, dict]:
    keys = sorted(claims)
    labels = np.asarray([claims[key] for key in keys], dtype=int)
    rng = np.random.default_rng(seed)
    strength_grid = np.linspace(-10, 10, 4001)
    shared = np.zeros(len(keys))
    metadata = {"mode": mode, "target_auc": target_auc}
    if mode == "node_correlated":
        nodes = sorted({v for key in keys for v in key})
        count = max(1, round(len(nodes) * blind_fraction))
        blind = set(rng.choice(nodes, size=count, replace=False).tolist())
        offsets = {node: rng.normal() for node in blind}
        shared = np.asarray([sum(offsets.get(node, 0.0) for node in key) for key in keys])
        metadata["blind_nodes"] = sorted(blind)
    elif mode == "motif_correlated":
        # Fixed hash-based regions are a deterministic stand-in until explicit motif
        # annotations from latent projection close OI-02.
        region_offsets = rng.normal(size=4)
        shared = np.asarray([region_offsets[sum(key) % 4] for key in keys])
        metadata["region_definition"] = "sum(triple) mod 4; OI-02 limitation"
    elif mode != "independent":
        raise KeyError(mode)
    noise = rng.normal(size=len(keys))
    base = noise + shared
    best = None
    for strength in strength_grid:
        scores = strength * (2 * labels - 1) + base
        auc = ranking_auc(labels, scores)
        if auc is None:
            best = (scores, auc, strength)
            break
        error = abs(auc - target_auc)
        if best is None or error < best[0]:
            best = (error, scores.copy(), auc, strength)
    if best is None:
        raise RuntimeError("calibration failed")
    if len(best) == 3:
        scores, auc, strength = best
    else:
        _, scores, auc, strength = best
    metadata.update({"realized_auc": auc, "strength": float(strength), "calibration_status": "PASS" if auc is not None and abs(auc - target_auc) <= 0.02 else "FAIL"})
    return {key: float(score) for key, score in zip(keys, scores)}, auc, metadata


def separator_query_score(candidate: QueryCandidate, claim_scores: dict, size_penalty: float = 0.05) -> float:
    i, j = sorted(candidate.pair)
    if candidate.conditioning_set:
        contribution = float(np.mean([claim_scores.get((i, j, z), 0.0) for z in candidate.conditioning_set]))
    else:
        contribution = 0.0
    return contribution - size_penalty * len(candidate.conditioning_set)


def materialize_prior(candidates: list[QueryCandidate], claim_scores: dict, realized_auc: float | None, metadata: dict) -> PriorView:
    scores = {candidate.query_id: separator_query_score(candidate, claim_scores) for candidate in candidates}
    return PriorView(scores, "separator_membership_prior", realized_auc, metadata)
