from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from .ci import UndefinedCIResultError
from .models import QueryCandidate, QueryRecord, ScoreBreakdown


class ProvenanceLog:
    def __init__(self, run_id: str, node_names: list[str], ci_backend: str, seed_refs: dict[str, int | None]):
        self.run_id = run_id
        self.node_names = node_names
        self.ci_backend = ci_backend
        self.seed_refs = seed_refs
        self.queries: list[QueryRecord] = []
        self.graph_events: list[dict] = []

    def record_query(
        self,
        candidate: QueryCandidate,
        score: ScoreBreakdown,
        result,
        eligible_count: int,
        state_after: str,
        elapsed_ms: float,
        provisional_removed_edges: set[tuple[int, int]],
        separating_set_recorded: bool = False,
    ) -> QueryRecord:
        rec = QueryRecord(
            run_id=self.run_id,
            query_id=candidate.query_id,
            step=len(self.queries),
            phase=candidate.phase,
            i=self.node_names[candidate.pair[0]],
            j=self.node_names[candidate.pair[1]],
            conditioning_set=[self.node_names[z] for z in candidate.conditioning_set],
            conditioning_order=candidate.conditioning_order,
            eligible_candidate_count=eligible_count,
            prerequisite_ids=list(candidate.prerequisite_ids),
            state_digest_before=candidate.state_digest,
            ci_backend=self.ci_backend,
            ci_statistic=result.statistic,
            p_value=result.p_value,
            ci_decision=(
                "undefined"
                if result.independent is None
                else "independent" if result.independent else "dependent"
            ),
            prior_score=score.prior_score,
            graph_score=score.graph_score,
            cost_score=score.cost_score,
            uncertainty_score=score.uncertainty_score,
            total_score=score.total_score,
            tie_break_key=score.tie_break_key,
            estimated_cost=candidate.estimated_cost,
            wall_time_ms=elapsed_ms,
            state_digest_after=state_after,
            edge_removed=False,
            separating_set_recorded=separating_set_recorded,
            opened_query_ids=[],
            seed_refs=dict(self.seed_refs),
            provisional_removed_edges=[
                [self.node_names[i], self.node_names[j]] for i, j in sorted(provisional_removed_edges)
            ],
            independence_witness=result.independent is True,
            ci_effect=getattr(result, "effect", None),
            ci_numerical_status=getattr(result, "numerical_status", "ok"),
            ci_decision_margin=getattr(result, "decision_margin", None),
        )
        self.queries.append(rec)
        return rec

    def mark_separating_set_recorded(self, query_id: str) -> None:
        matches = [query for query in self.queries if query.query_id == query_id]
        if len(matches) != 1:
            raise RuntimeError(f"expected exactly one provenance record for {query_id!r}")
        matches[0].separating_set_recorded = True
        matches[0].edge_removed = True

    def graph_event(self, event_type: str, rule: str, before: str, after: str, evidence_query_ids: list[str], details: dict) -> None:
        self.graph_events.append({
            "run_id": self.run_id,
            "event_index": len(self.graph_events),
            "event_type": event_type,
            "rule": rule,
            "state_digest_before": before,
            "state_digest_after": after,
            "evidence_query_ids": list(evidence_query_ids),
            "details": details,
            "prior_is_evidence": False,
        })

    def write(self, query_path: Path, event_path: Path) -> None:
        query_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.parent.mkdir(parents=True, exist_ok=True)
        with query_path.open("w", encoding="utf-8", newline="\n") as handle:
            for query in self.queries:
                handle.write(json.dumps(query.as_dict(), sort_keys=True) + "\n")
        with event_path.open("w", encoding="utf-8", newline="\n") as handle:
            for event in self.graph_events:
                handle.write(json.dumps(event, sort_keys=True) + "\n")


class LoggedCIProxy:
    """Log upstream Possible-D-SEP/R4 CI calls without exposing truth to schedulers."""
    def __init__(self, ci, provenance: ProvenanceLog, graph_digest: Callable[[], str], phase: str = "possible_dsep"):
        self.ci = ci
        self.provenance = provenance
        self.graph_digest = graph_digest
        self.phase = phase
        self.method = getattr(ci, "backend", "unknown")

    def __call__(self, i, j, conditioning_set=None):
        z = tuple(sorted(map(int, conditioning_set or ())))
        before = self.graph_digest()
        ordinal = len(self.provenance.queries)
        qid = f"{self.phase}:{int(i)}:{int(j)}:{','.join(map(str, z))}:{ordinal}"
        candidate = QueryCandidate(qid, (int(i), int(j)), z, self.phase, len(z), ("barrier:skeleton",), before, (len(z) + 2) ** 3)
        start = time.perf_counter()
        result = self.ci.test(int(i), int(j), z)
        elapsed = (time.perf_counter() - start) * 1000
        query_record = self.provenance.record_query(
            candidate,
            ScoreBreakdown(tie_break_key=qid),
            result,
            1,
            self.graph_digest(),
            elapsed,
            set(),
            separating_set_recorded=result.independent is True,
        )
        if result.independent is None:
            raise UndefinedCIResultError(
                qid,
                getattr(result, "numerical_status", "unknown"),
                query_record.as_dict(),
            )
        return result.p_value
