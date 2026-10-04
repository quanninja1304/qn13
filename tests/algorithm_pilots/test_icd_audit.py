import pytest

from safety_prior.algorithms.icd_official_adapter import official_icd_available
from safety_prior.pilots.audit_icd_reference import audit_icd_reference


@pytest.mark.skipif(not official_icd_available(), reason="optional pinned ICD reference is not installed")
def test_small_reference_audit_has_no_output_mismatch():
    summary = audit_icd_reference(observed_sizes=(4,), latent_ratios=(0.0,), seeds_per_cell=1)
    assert summary.graphs == 1
    assert summary.icd_fci_output_mismatches == 0
    assert summary.dynamic_precomputed_output_mismatches == 0
