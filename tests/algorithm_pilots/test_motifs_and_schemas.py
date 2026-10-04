import pytest

from safety_prior.pilots.equality import canonical_conditioning_set, compare_canonical_pags
from safety_prior.pilots.motifs import common_motif_catalog
from safety_prior.pilots.schemas import BLOCK_RUN_FIELDS, validate_run_record


def test_common_motif_catalog_has_unique_valid_dags():
    motifs = common_motif_catalog()
    assert len({motif.name for motif in motifs}) == len(motifs)
    assert {"diamond", "future_confounder_claim", "latent_diamond", "dynamic_snapshot_trace_gap"}.issubset(
        {motif.name for motif in motifs}
    )
    assert all(motif.to_dag().number_of_nodes() == len(motif.observed) + len(motif.latent) for motif in motifs)


def test_run_schema_reports_missing_fields():
    with pytest.raises(ValueError, match="Missing block_icd"):
        validate_run_record({"run_id": "incomplete"}, "block_icd")


def test_complete_block_schema_is_accepted():
    record = {field: None for field in BLOCK_RUN_FIELDS}
    validate_run_record(record, "block_icd")


def test_pag_comparison_separates_skeleton_from_endpoint_equality():
    left = {"nodes": ["X1", "X2"], "endpoint_matrix": [[0, 2], [2, 0]], "is_pag": True}
    right = {"nodes": ["X1", "X2"], "endpoint_matrix": [[0, 1], [-1, 0]], "is_pag": True}
    comparison = compare_canonical_pags(left, right)
    assert comparison.skeleton_equal
    assert not comparison.endpoint_matrix_equal
    assert not comparison.exact


def test_conditioning_set_canonicalization_rejects_duplicates():
    assert canonical_conditioning_set([3, 1, 2]) == (1, 2, 3)
    with pytest.raises(ValueError, match="duplicate"):
        canonical_conditioning_set([1, 1])
