from __future__ import annotations

import argparse
import contextlib
import io
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from causallearn.search.ConstraintBased.FCI import fci

from ..algorithms.icd_official_adapter import OfficialICDUnavailable, run_official_icd
from ..ci import OracleCI
from ..graphs import canonical_pag, dummy_data, generate_dag
from .schemas import ARTIFACT_SCHEMA_VERSION


@dataclass(frozen=True)
class AuditMismatch:
    kind: str
    observed_nodes: int
    latent_ratio: float
    seed: int
    dynamic_queries: int
    precomputed_queries: int


@dataclass(frozen=True)
class ICDAuditSummary:
    graphs: int
    icd_fci_output_mismatches: int
    dynamic_precomputed_output_mismatches: int
    dynamic_precomputed_trace_mismatches: int
    first_mismatches: tuple[AuditMismatch, ...]
    contract_version: str = ARTIFACT_SCHEMA_VERSION
    reference_id: str = "causality-lab@36625da6eeef059e36dab2b4467235a036136b76"
    reference_mode: str = "dynamic_reference"
    equality_target: str = "final_pag"


def _trace(iterations) -> tuple[tuple[int, int, tuple[int, ...]], ...]:
    return tuple(query for iteration in iterations for query in iteration.queries)


def audit_icd_reference(
    observed_sizes: Iterable[int] = (4, 5, 6, 7),
    latent_ratios: Iterable[float] = (0.0, 0.3),
    seeds_per_cell: int = 5,
    mean_degree: float = 2.0,
    seed_base: int = 70_000,
) -> ICDAuditSummary:
    """Compare pinned ICD, its precomputed mode, and upstream oracle FCI."""

    if seeds_per_cell < 1:
        raise ValueError("seeds_per_cell must be positive")

    counts = {
        "graphs": 0,
        "icd_fci": 0,
        "mode_output": 0,
        "mode_trace": 0,
    }
    first: dict[str, AuditMismatch] = {}

    for observed_nodes in observed_sizes:
        for latent_ratio in latent_ratios:
            for offset in range(seeds_per_cell):
                seed = seed_base + observed_nodes * 1_000 + int(latent_ratio * 100) * 10 + offset
                case = generate_dag(observed_nodes, latent_ratio, mean_degree, seed)
                ci = OracleCI(case.dag, case.observed)
                dynamic = run_official_icd(case.observed, ci, precompute_candidates=False)
                precomputed = run_official_icd(case.observed, ci, precompute_candidates=True)

                # causal-learn currently prints some visible edges even with
                # verbose=False.  Capture that library noise in audit mode.
                with contextlib.redirect_stdout(io.StringIO()):
                    upstream, _ = fci(
                        dummy_data(len(case.observed)),
                        independence_test_method="d_separation",
                        true_dag=case.dag,
                        node_names=[f"X{i + 1}" for i in case.observed],
                        show_progress=False,
                    )
                reference = canonical_pag(upstream)
                dynamic_trace = _trace(dynamic)
                precomputed_trace = _trace(precomputed)
                counts["graphs"] += 1

                def record(kind: str) -> None:
                    first.setdefault(
                        kind,
                        AuditMismatch(
                            kind,
                            observed_nodes,
                            latent_ratio,
                            seed,
                            len(dynamic_trace),
                            len(precomputed_trace),
                        ),
                    )

                if dynamic[-1].graph != reference:
                    counts["icd_fci"] += 1
                    record("icd_fci_output")
                if dynamic[-1].graph != precomputed[-1].graph:
                    counts["mode_output"] += 1
                    record("dynamic_precomputed_output")
                if dynamic_trace != precomputed_trace:
                    counts["mode_trace"] += 1
                    record("dynamic_precomputed_trace")

    return ICDAuditSummary(
        graphs=counts["graphs"],
        icd_fci_output_mismatches=counts["icd_fci"],
        dynamic_precomputed_output_mismatches=counts["mode_output"],
        dynamic_precomputed_trace_mismatches=counts["mode_trace"],
        first_mismatches=tuple(first.values()),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit the pinned official ICD reference")
    parser.add_argument("--seeds-per-cell", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = audit_icd_reference(seeds_per_cell=args.seeds_per_cell)
    except OfficialICDUnavailable as exc:
        payload = {
            "contract_version": ARTIFACT_SCHEMA_VERSION,
            "reference_id": "causality-lab@36625da6eeef059e36dab2b4467235a036136b76",
            "reference_mode": "dynamic_reference",
            "equality_target": "final_pag",
            "status": "BLOCKED_EXTERNAL_DEPENDENCY",
            "reason": str(exc),
        }
    else:
        payload = asdict(summary)
        payload["status"] = (
            "PASS"
            if summary.icd_fci_output_mismatches == 0
            and summary.dynamic_precomputed_output_mismatches == 0
            else "FAIL"
        )
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(encoded + "\n", encoding="utf-8", newline="\n")
        temporary.replace(args.output)
    print(encoded)
    if payload["status"] == "PASS":
        return 0
    return 2 if payload["status"] == "BLOCKED_EXTERNAL_DEPENDENCY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
