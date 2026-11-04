import json

from safety_prior.cli import main
from safety_prior.pilots.audit_stable_epoch import audit_stable_epoch, evaluate_g2


def test_exhaustive_truth_table_audit_passes_gate_g2():
    summary = audit_stable_epoch(seed=17, schedule_permutations=2)

    assert summary.status == "PASS"
    assert summary.truth_table_count == 64
    assert summary.audited_schedule_count == 128
    assert not summary.first_failures


def test_gate_g2_rejects_an_underpowered_audit():
    summary = audit_stable_epoch(seed=18, schedule_permutations=1)

    gate = evaluate_g2(summary)

    assert summary.status == "PASS"
    assert gate["status"] == "FAIL"
    assert gate["metrics"]["audited_schedule_count"] == 64


def test_stable_epoch_audit_cli_writes_atomic_json(tmp_path):
    output = tmp_path / "stable_epoch.json"

    exit_code = main(
        [
            "stable-epoch-audit",
            "--seed",
            "19",
            "--permutations",
            "4",
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["gate"]["status"] == "PASS"
    assert payload["audit"]["audited_schedule_count"] == 256
    assert payload["reproducibility"]["git_revision"]
    assert payload["reproducibility"]["config_digest"]
    assert payload["reproducibility"]["dependency_lock"]
    assert not output.with_suffix(".json.tmp").exists()
