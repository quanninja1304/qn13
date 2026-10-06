import numpy as np
import pytest
from scipy.stats import norm

from safety_prior.ci import GaussianCI


def _orthogonal_columns(rows: int = 400, columns: int = 4) -> np.ndarray:
    rng = np.random.default_rng(20261005)
    raw = rng.normal(size=(rows, columns))
    raw -= raw.mean(axis=0, keepdims=True)
    basis, _ = np.linalg.qr(raw)
    return basis


def test_gaussian_ci_unconditional_decision_uses_configured_alpha():
    data = _orthogonal_columns(columns=2)
    result = GaussianCI(data, alpha=0.05).test(0, 1, ())

    assert result.independent is True
    assert result.p_value == pytest.approx(1.0)
    assert result.decision_margin == pytest.approx(result.p_value - 0.05)
    assert result.numerical_status == "ok"


def test_gaussian_ci_chain_is_dependent_marginally_and_independent_conditionally():
    basis = _orthogonal_columns(columns=3)
    z, ex, ey = basis.T
    data = np.column_stack((z + 0.35 * ex, z + 0.35 * ey, z))
    ci = GaussianCI(data, alpha=0.05)

    assert ci.test(0, 1, ()).independent is False
    conditional = ci.test(0, 1, (2,))
    assert conditional.independent is True
    assert conditional.effect == pytest.approx(0.0, abs=1e-12)


def test_gaussian_ci_matches_manual_precision_and_fisher_z_formula():
    rng = np.random.default_rng(17)
    data = rng.normal(size=(300, 4))
    data[:, 1] = 0.45 * data[:, 0] + 0.25 * data[:, 2] + data[:, 1]
    alpha = 0.025
    result = GaussianCI(data, alpha=alpha).test(0, 1, (2, 3))

    correlation = np.corrcoef(data[:, [0, 1, 2, 3]], rowvar=False)
    precision = np.linalg.inv(correlation)
    rho = -precision[0, 1] / np.sqrt(precision[0, 0] * precision[1, 1])
    statistic = abs(np.arctanh(rho)) * np.sqrt(data.shape[0] - 2 - 3)
    p_value = 2.0 * norm.sf(statistic)

    assert result.effect == pytest.approx(rho)
    assert result.statistic == pytest.approx(statistic)
    assert result.p_value == pytest.approx(p_value)
    assert result.independent is bool(p_value > alpha)


def test_gaussian_ci_fork_and_collider_patterns():
    basis = _orthogonal_columns(columns=4)
    cause, ex, ey, noise = basis.T

    fork = np.column_stack((cause + 0.3 * ex, cause + 0.3 * ey, cause))
    fork_ci = GaussianCI(fork)
    assert fork_ci.test(0, 1, ()).independent is False
    assert fork_ci.test(0, 1, (2,)).independent is True

    collider = np.column_stack((ex, ey, ex + ey + 0.3 * noise))
    collider_ci = GaussianCI(collider)
    assert collider_ci.test(0, 1, ()).independent is True
    assert collider_ci.test(0, 1, (2,)).independent is False


def test_gaussian_ci_matrix_input_and_conditioning_order_are_explicit():
    rng = np.random.default_rng(23)
    samples = rng.normal(size=(250, 4))
    covariance = np.cov(samples, rowvar=False)
    scale = np.sqrt(np.diag(covariance))
    correlation = covariance / np.outer(scale, scale)

    from_covariance = GaussianCI(
        covariance, input_kind="covariance", n_samples=len(samples)
    ).test(0, 1, (3, 2))
    from_correlation = GaussianCI(
        correlation, input_kind="correlation", n_samples=len(samples)
    ).test(0, 1, (2, 3))

    assert from_covariance.effect == pytest.approx(from_correlation.effect)
    assert from_covariance.p_value == pytest.approx(from_correlation.p_value)


def test_gaussian_ci_uses_strict_greater_than_at_decision_threshold():
    rng = np.random.default_rng(29)
    data = rng.normal(size=(120, 2))
    observed_p = GaussianCI(data, alpha=0.05).test(0, 1, ()).p_value

    assert GaussianCI(data, alpha=observed_p).test(0, 1, ()).independent is False


def test_gaussian_ci_reports_insufficient_df_instead_of_clamping():
    result = GaussianCI(_orthogonal_columns(rows=5, columns=4)).test(0, 1, (2, 3))

    assert result.independent is None
    assert result.p_value is None
    assert result.statistic is None
    assert result.numerical_status == "insufficient_df"


def test_gaussian_ci_strict_mode_reports_singular_local_matrix():
    basis = _orthogonal_columns(columns=2)
    data = np.column_stack((basis[:, 0], basis[:, 1], basis[:, 0]))
    result = GaussianCI(data).test(0, 1, (2,))

    assert result.independent is None
    assert result.p_value is None
    assert result.numerical_status == "singular"


def test_gaussian_ci_rejects_noncanonical_or_invalid_queries():
    ci = GaussianCI(_orthogonal_columns(columns=4))

    with pytest.raises(ValueError, match="distinct"):
        ci.test(0, 0, ())
    with pytest.raises(ValueError, match="duplicate"):
        ci.test(0, 1, (2, 2))
    with pytest.raises(ValueError, match="endpoint"):
        ci.test(0, 1, (0,))
    with pytest.raises(IndexError, match="column"):
        ci.test(0, 7, ())


def test_gaussian_ci_requires_explicit_regularization_mode():
    basis = _orthogonal_columns(columns=2)
    data = np.column_stack((basis[:, 0], basis[:, 1], basis[:, 0]))

    strict = GaussianCI(data).test(0, 1, (2,))
    ridge = GaussianCI(data, inversion="ridge", ridge=1e-6).test(0, 1, (2,))
    diagnostic = GaussianCI(data, inversion="pinv").test(0, 1, (2,))

    assert strict.numerical_status == "singular"
    assert ridge.numerical_status == "regularized_ridge"
    assert diagnostic.numerical_status == "diagnostic_pinv"
