from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np

from .models import PriorView, QueryCandidate, ScoreBreakdown


def _tie(seed: int, query_id: str) -> str:
    return hashlib.sha256(f"{seed}:{query_id}".encode()).hexdigest()


class Scheduler(ABC):
    name = "base"
    allows_ground_truth = False

    def __init__(self, seed: int):
        self.seed = int(seed)

    @abstractmethod
    def score(self, candidate: QueryCandidate, state: dict, prior: PriorView | None) -> ScoreBreakdown:
        ...

    def order(self, candidates: Sequence[QueryCandidate], state: dict, prior: PriorView | None = None) -> list[tuple[QueryCandidate, ScoreBreakdown]]:
        scored = [(candidate, self.score(candidate, state, prior)) for candidate in candidates]
        return sorted(scored, key=lambda item: (-item[1].total_score, item[1].tie_break_key, item[0].query_id))

    def select(self, candidates: Sequence[QueryCandidate], state: dict, prior: PriorView | None = None) -> QueryCandidate:
        if not candidates:
            raise ValueError("cannot select from an empty eligible set")
        return self.order(candidates, state, prior)[0][0]


class StableDefault(Scheduler):
    name = "stable_default"

    def score(self, candidate, state, prior):
        key = f"{candidate.pair[0]:06d}:{candidate.pair[1]:06d}:" + ",".join(map(str, candidate.conditioning_set))
        return ScoreBreakdown(tie_break_key=key)


class RandomValid(Scheduler):
    name = "random_valid"

    def score(self, candidate, state, prior):
        key = _tie(self.seed, candidate.query_id)
        value = int(key[:13], 16) / float(16**13)
        return ScoreBreakdown(total_score=value, tie_break_key=key)


class CostOnly(Scheduler):
    name = "cost_only"

    def score(self, candidate, state, prior):
        cost_score = -float(candidate.estimated_cost)
        return ScoreBreakdown(cost_score=cost_score, total_score=cost_score, tie_break_key=_tie(self.seed, candidate.query_id))


class GraphOnly(Scheduler):
    name = "graph_only"

    def score(self, candidate, state, prior):
        degrees = state.get("degrees", {})
        graph_score = float(degrees.get(candidate.pair[0], 0) + degrees.get(candidate.pair[1], 0))
        cost_score = -candidate.estimated_cost / 1000.0
        return ScoreBreakdown(graph_score=graph_score, cost_score=cost_score, total_score=graph_score + cost_score, tie_break_key=_tie(self.seed, candidate.query_id))


class PriorGuided(Scheduler):
    name = "prior_guided"

    def score(self, candidate, state, prior):
        if prior is None:
            raise ValueError("prior_guided requires a materialized PriorView")
        prior_score = float(prior.scores.get(candidate.query_id, 0.0))
        cost_score = -candidate.estimated_cost / 1000.0
        return ScoreBreakdown(prior_score=prior_score, cost_score=cost_score, total_score=prior_score + cost_score, tie_break_key=_tie(self.seed, candidate.query_id))


class OracleQuery(Scheduler):
    name = "oracle_query"
    allows_ground_truth = True

    def __init__(self, seed: int, oracle):
        super().__init__(seed)
        self.oracle = oracle

    def score(self, candidate, state, prior):
        useful = float(self.oracle.test(*candidate.pair, candidate.conditioning_set).independent)
        return ScoreBreakdown(prior_score=useful, total_score=useful, tie_break_key=_tie(self.seed, candidate.query_id))


def make_scheduler(name: str, seed: int, oracle=None) -> Scheduler:
    mapping = {"stable_default": StableDefault, "random_valid": RandomValid, "cost_only": CostOnly, "graph_only": GraphOnly, "prior_guided": PriorGuided}
    if name == "oracle_query":
        if oracle is None:
            raise ValueError("oracle_query requires an oracle")
        return OracleQuery(seed, oracle)
    if name not in mapping:
        raise KeyError(name)
    return mapping[name](seed)
