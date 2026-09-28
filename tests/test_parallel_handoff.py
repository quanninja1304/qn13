import json
from pathlib import Path

import pytest

from safety_prior import delta_handoff, phase1_parallel


def test_atomic_claim_is_exclusive(tmp_path):
    claim = tmp_path / "claim.json"
    payload = {"worker_id": "worker-1"}
    assert phase1_parallel._atomic_claim(claim, payload)
    assert not phase1_parallel._atomic_claim(claim, {"worker_id": "worker-2"})
    assert json.loads(claim.read_text(encoding="utf-8")) == payload


def test_stale_local_claim_is_recovered(tmp_path, monkeypatch):
    claim_dir = tmp_path / "claims"
    slot_dir = tmp_path / "slots"
    claim_dir.mkdir()
    slot_dir.mkdir()
    stale = claim_dir / "g104.json"
    stale.write_text(
        json.dumps(
            {
                "hostname": phase1_parallel.platform.node(),
                "pid": 99999999,
                "process_create_time": 0,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(phase1_parallel, "CLAIM_DIR", claim_dir)
    monkeypatch.setattr(phase1_parallel, "SLOT_DIR", slot_dir)
    monkeypatch.setattr(phase1_parallel, "ROOT", tmp_path)
    recovered = phase1_parallel.recover_stale_claims()
    assert recovered == ["claims/g104.json"]
    assert not stale.exists()


def test_three_worker_slots_are_enforced(tmp_path, monkeypatch):
    slot_dir = tmp_path / "slots"
    monkeypatch.setattr(phase1_parallel, "SLOT_DIR", slot_dir)
    paths = [phase1_parallel._acquire_slot(f"worker-{index}") for index in range(3)]
    with pytest.raises(RuntimeError, match="three authorized worker slots"):
        phase1_parallel._acquire_slot("worker-4")
    for path in paths:
        path.unlink()


def test_delta_package_detects_tampering(tmp_path):
    package = tmp_path / "package"
    package.mkdir()
    payload = package / "payload.txt"
    payload.write_text("frozen", encoding="utf-8")
    delta_handoff._write_package_manifest(
        package,
        {"kind": "phase1_delta_input", "code_revision": "abc"},
    )
    assert delta_handoff.verify_delta_package(package)["status"] == "PASS"
    payload.write_text("tampered", encoding="utf-8")
    result = delta_handoff.verify_delta_package(package)
    assert result["status"] == "FAIL"
    assert result["mismatched"] == ["payload.txt"]


def test_output_package_must_be_outside_project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setattr(delta_handoff, "ROOT", root)
    with pytest.raises(ValueError, match="outside the project root"):
        delta_handoff._prepare_output(root / "package")


def test_input_install_only_overwrites_frozen_environment_provenance(tmp_path, monkeypatch):
    root = tmp_path / "project"
    package = tmp_path / "package"
    root_env = root / "env"
    package_env = package / "env"
    root_env.mkdir(parents=True)
    package_env.mkdir(parents=True)
    destination = root_env / "windows_source_environment.json"
    source = package_env / "windows_source_environment.json"
    destination.write_text("old", encoding="utf-8")
    source.write_text("new", encoding="utf-8")
    monkeypatch.setattr(delta_handoff, "ROOT", root)
    assert delta_handoff._copy_package_into_project(package, allow_return=False) == 1
    assert destination.read_text(encoding="utf-8") == "new"

    protected_destination = root / "README.md"
    protected_source = package / "README.md"
    protected_destination.write_text("tracked", encoding="utf-8")
    protected_source.write_text("changed", encoding="utf-8")
    with pytest.raises(RuntimeError, match="package collision"):
        delta_handoff._copy_package_into_project(package, allow_return=False)
