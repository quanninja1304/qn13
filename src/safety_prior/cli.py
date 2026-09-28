from __future__ import annotations

import argparse
import json

from .reporting import generate_figures, generate_reports
from .runner import ROOT, dry_run, evaluate_gates, run_phase0, run_phase1
from .phase1_execution import analyze as analyze_phase1, preflight as preflight_phase1, run_shard
from .phase1_parallel import prepare_queue, queue_status, run_graph_worker
from .delta_handoff import (
    export_delta_input,
    export_delta_return,
    import_delta_return,
    install_delta_input,
    verify_delta_package,
)
from .migration import prepare_source_migration, validate_vps_migration


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Safe Imperfect Priors kill test")
    sub = parser.add_subparsers(dest="command", required=True)
    dry = sub.add_parser("dry-run")
    dry.add_argument("--phase", type=int, required=True, choices=range(4))
    smoke = sub.add_parser("smoke")
    p0 = sub.add_parser("phase0")
    p1 = sub.add_parser("phase1")
    p1.add_argument("--smoke", action="store_true")
    sub.add_parser("phase1-preflight")
    shard = sub.add_parser("phase1-shard")
    shard.add_argument("--shard", type=int, required=True, choices=range(8))
    sub.add_parser("phase1-queue-prepare")
    worker = sub.add_parser("phase1-graph-worker")
    worker.add_argument("--worker-id", required=True)
    queue = sub.add_parser("phase1-queue-status")
    queue.add_argument("--finalize", action="store_true")
    sub.add_parser("phase1-analyze")
    delta_export = sub.add_parser("delta-export-input")
    delta_export.add_argument("--output", required=True)
    delta_install = sub.add_parser("delta-install-input")
    delta_install.add_argument("--package", required=True)
    delta_verify = sub.add_parser("delta-verify-package")
    delta_verify.add_argument("--package", required=True)
    delta_return = sub.add_parser("delta-export-return")
    delta_return.add_argument("--output", required=True)
    delta_import = sub.add_parser("delta-import-return")
    delta_import.add_argument("--package", required=True)
    sub.add_parser("migration-prepare")
    sub.add_parser("migration-validate")
    sub.add_parser("evaluate-gates")
    sub.add_parser("report")
    sub.add_parser("figures")
    args = parser.parse_args(argv)
    if args.command == "dry-run":
        print(json.dumps(dry_run(args.phase), indent=2))
    elif args.command == "smoke":
        print(json.dumps({"runs": len(run_phase0(ROOT / "configs/kill_test/phase0.yaml", smoke=True)), "scope": "smoke"}, indent=2))
    elif args.command == "phase0":
        print(json.dumps({"runs": len(run_phase0(ROOT / "configs/kill_test/phase0.yaml")), "scope": "main"}, indent=2))
    elif args.command == "phase1":
        print(json.dumps({"runs": len(run_phase1(ROOT / "configs/kill_test/phase1.yaml", smoke=args.smoke)), "scope": "smoke" if args.smoke else "main"}, indent=2))
    elif args.command == "phase1-preflight":
        print(json.dumps(preflight_phase1(), indent=2))
    elif args.command == "phase1-shard":
        print(json.dumps(run_shard(args.shard), indent=2))
    elif args.command == "phase1-queue-prepare":
        print(json.dumps(prepare_queue(), indent=2))
    elif args.command == "phase1-graph-worker":
        print(json.dumps(run_graph_worker(args.worker_id), indent=2))
    elif args.command == "phase1-queue-status":
        print(json.dumps(queue_status(finalize=args.finalize), indent=2))
    elif args.command == "phase1-analyze":
        print(json.dumps(analyze_phase1(), indent=2))
    elif args.command == "delta-export-input":
        print(json.dumps(export_delta_input(args.output), indent=2))
    elif args.command == "delta-install-input":
        print(json.dumps(install_delta_input(args.package), indent=2))
    elif args.command == "delta-verify-package":
        print(json.dumps(verify_delta_package(args.package), indent=2))
    elif args.command == "delta-export-return":
        print(json.dumps(export_delta_return(args.output), indent=2))
    elif args.command == "delta-import-return":
        print(json.dumps(import_delta_return(args.package), indent=2))
    elif args.command == "migration-prepare":
        print(json.dumps(prepare_source_migration(), indent=2))
    elif args.command == "migration-validate":
        print(json.dumps(validate_vps_migration(), indent=2))
    elif args.command == "evaluate-gates":
        print(json.dumps(evaluate_gates(), indent=2))
    elif args.command == "report":
        generate_reports()
    elif args.command == "figures":
        generate_figures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
