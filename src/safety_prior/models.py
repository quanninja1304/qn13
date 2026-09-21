from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class QueryCandidate:
    query_id: str
    pair: tuple[int, int]
    conditioning_set: tuple[int, ...]
    phase: str
    conditioning_order: int
    prerequisite_ids: tuple[str, ...]
    state_digest: str
    estimated_cost: int


@dataclass(frozen=True)
class ScoreBreakdown:
    prior_score: float = 0.0
    graph_score: float = 0.0
    cost_score: float = 0.0
    uncertainty_score: float = 0.0
    total_score: float = 0.0
    tie_break_key: str = ""


@dataclass
class QueryRecord:
    run_id: str
    query_id: str
    step: int
    phase: str
    i: str
    j: str
    conditioning_set: list[str]
    conditioning_order: int
    eligible_candidate_count: int
    prerequisite_ids: list[str]
    state_digest_before: str
    ci_backend: str
    ci_statistic: float | None
    p_value: float | None
    ci_decision: str
    prior_score: float
    graph_score: float
    cost_score: float
    uncertainty_score: float
    total_score: float
    tie_break_key: str
    estimated_cost: int
    wall_time_ms: float
    state_digest_after: str
    edge_removed: bool
    separating_set_recorded: bool
    opened_query_ids: list[str]
    seed_refs: dict[str, int | None]
    provisional_removed_edges: list[list[str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryState:
    graph: Mapping[str, Any]
    tests: Sequence[Mapping[str, Any]]
    untested: Sequence[Mapping[str, Any]]
    budget: Mapping[str, float | int | None]
    completed: bool
    object_type: str = "DiscoveryState"


@dataclass
class PAGResult(DiscoveryState):
    completed: bool = True
    object_type: str = "PAGResult"


@dataclass(frozen=True)
class PriorView:
    scores: Mapping[str, float]
    source: str
    realized_auc: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

