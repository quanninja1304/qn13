from pathlib import Path

import pytest

from safety_prior.runner import ROOT, canonical_project_reference, resolve_project_reference


def test_current_absolute_reference_becomes_relative():
    target = ROOT / "artifacts" / "kill_test" / "example.jsonl"
    assert canonical_project_reference(target) == "artifacts/kill_test/example.jsonl"


def test_legacy_windows_root_is_deterministically_remapped():
    legacy = r"D:\REsearch\causal multi-agent\safety_prior\artifacts\kill_test\example.jsonl"
    expected = ROOT / "artifacts" / "kill_test" / "example.jsonl"
    assert resolve_project_reference(legacy) == expected.resolve()


def test_relative_reference_is_resolved_under_project_root():
    expected = ROOT / "artifacts" / "kill_test" / "example.jsonl"
    assert resolve_project_reference("artifacts/kill_test/example.jsonl") == expected.resolve()


def test_parent_traversal_is_rejected():
    with pytest.raises(ValueError):
        resolve_project_reference("../outside.json")


def test_unknown_absolute_reference_is_rejected():
    unknown = Path("C:/unrelated/artifact.json")
    with pytest.raises(ValueError):
        resolve_project_reference(unknown)
