from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class CIResult:
    independent: bool | None
    p_value: float | None
    statistic: float | None = None
    effect: float | None = None
    numerical_status: str = "ok"
    decision_margin: float | None = None


class UndefinedCIResultError(RuntimeError):
    """Raised when an undefined CI result would otherwise mutate a graph."""

    def __init__(
        self,
        query_id: str,
        numerical_status: str,
        query_record: dict | None = None,
    ):
        self.query_id = query_id
        self.numerical_status = numerical_status
        self.failure_artifact = {
            "terminal_status": "failed",
            "failure_type": "undefined_ci_result",
            "query_id": query_id,
            "numerical_status": numerical_status,
            "query_record": query_record,
        }
        super().__init__(
            f"CI query {query_id!r} is undefined ({numerical_status}); graph mutation aborted"
        )

    def as_dict(self) -> dict:
        return dict(self.failure_artifact)


class OracleCI:
    backend = "oracle"

    def __init__(self, dag: nx.DiGraph, observed: Iterable[int]):
        self.dag = dag.copy()
        self.observed = frozenset(int(v) for v in observed)

    def test(self, i: int, j: int, conditioning_set: Iterable[int]) -> CIResult:
        z = frozenset(int(v) for v in conditioning_set)
        if i not in self.observed or j not in self.observed or not z <= self.observed:
            raise ValueError("Oracle CI endpoints and conditioning variables must be observed")
        if i in z or j in z:
            raise ValueError("CI endpoints cannot be conditioned on")
        independent = bool(nx.is_d_separator(self.dag, {int(i)}, {int(j)}, set(z)))
        return CIResult(independent, 1.0 if independent else 0.0, None)

    def __call__(self, i: int, j: int, conditioning_set=()) -> float:
        return self.test(i, j, conditioning_set).p_value


class GaussianCI:
    backend = "gaussian"

    def __init__(
        self,
        data: np.ndarray,
        alpha: float = 0.05,
        *,
        input_kind: str = "samples",
        n_samples: int | None = None,
        inversion: str = "strict",
        ridge: float = 0.0,
    ):
        if not 0.0 < float(alpha) < 1.0:
            raise ValueError("alpha must lie strictly between zero and one")
        if input_kind not in {"samples", "covariance", "correlation"}:
            raise ValueError("input_kind must be samples, covariance, or correlation")
        if inversion not in {"strict", "ridge", "pinv"}:
            raise ValueError("inversion must be strict, ridge, or pinv")
        if inversion == "ridge" and float(ridge) <= 0.0:
            raise ValueError("ridge inversion requires a positive ridge value")
        if inversion != "ridge" and float(ridge) != 0.0:
            raise ValueError("a ridge value is only valid with inversion='ridge'")

        array = np.asarray(data, dtype=float)
        if array.ndim != 2 or not np.isfinite(array).all():
            raise ValueError("Gaussian CI requires a complete finite 2D array")

        self.alpha = float(alpha)
        self.input_kind = input_kind
        self.inversion = inversion
        self.ridge = float(ridge)
        self.backend = {
            "strict": "gaussian_strict",
            "ridge": "gaussian_ridge",
            "pinv": "gaussian_pinv_diagnostic",
        }[inversion]

        if input_kind == "samples":
            if array.shape[1] < 2:
                raise ValueError("Gaussian CI samples require at least two columns")
            if n_samples is not None and int(n_samples) != array.shape[0]:
                raise ValueError("n_samples must match the number of sample rows")
            self.data = array
            self.matrix = None
            self.n_samples = int(array.shape[0])
            self.n_variables = int(array.shape[1])
        else:
            if array.shape[0] != array.shape[1] or array.shape[0] < 2:
                raise ValueError("covariance/correlation input must be a square matrix")
            if not np.allclose(array, array.T, rtol=1e-10, atol=1e-12):
                raise ValueError("covariance/correlation input must be symmetric")
            if n_samples is None or int(n_samples) <= 0:
                raise ValueError("matrix input requires a positive n_samples")
            if input_kind == "covariance":
                variances = np.diag(array)
                if np.any(variances <= 0.0):
                    raise ValueError("covariance diagonal must be positive")
                scale = np.sqrt(variances)
                array = array / np.outer(scale, scale)
            elif not np.allclose(np.diag(array), 1.0, rtol=1e-10, atol=1e-12):
                raise ValueError("correlation matrix diagonal must equal one")
            self.data = None
            self.matrix = array
            self.n_samples = int(n_samples)
            self.n_variables = int(array.shape[0])

    def _query_columns(
        self, i: int, j: int, conditioning_set: Iterable[int]
    ) -> tuple[int, int, tuple[int, ...]]:
        i, j = int(i), int(j)
        raw = tuple(map(int, conditioning_set))
        if i == j:
            raise ValueError("CI endpoints must be distinct")
        if len(raw) != len(set(raw)):
            raise ValueError("conditioning set contains a duplicate column")
        z = tuple(sorted(raw))
        if i in z or j in z:
            raise ValueError("CI endpoint cannot occur in the conditioning set")
        if min((i, j, *z), default=0) < 0 or max((i, j, *z), default=0) >= self.n_variables:
            raise IndexError("CI query references an invalid column")
        return i, j, z

    @staticmethod
    def _undefined(status: str) -> CIResult:
        return CIResult(None, None, None, None, status, None)

    def test(self, i: int, j: int, conditioning_set: Iterable[int]) -> CIResult:
        i, j, z = self._query_columns(i, j, conditioning_set)
        degrees_of_freedom = self.n_samples - len(z) - 3
        if degrees_of_freedom <= 0:
            return self._undefined("insufficient_df")

        columns = [i, j, *z]
        if self.input_kind == "samples":
            corr = np.asarray(np.corrcoef(self.data[:, columns], rowvar=False), dtype=float)
        else:
            corr = np.asarray(self.matrix[np.ix_(columns, columns)], dtype=float)
        if corr.ndim == 0:
            corr = np.asarray([[float(corr)]])
        if not np.isfinite(corr).all():
            return self._undefined("nonfinite_correlation")

        status = "ok"
        try:
            if self.inversion == "strict":
                if np.linalg.matrix_rank(corr) < corr.shape[0]:
                    return self._undefined("singular")
                precision = np.linalg.solve(corr, np.eye(corr.shape[0]))
            elif self.inversion == "ridge":
                precision = np.linalg.solve(
                    corr + self.ridge * np.eye(corr.shape[0]), np.eye(corr.shape[0])
                )
                status = "regularized_ridge"
            else:
                precision = np.linalg.pinv(corr, rcond=1e-12)
                status = "diagnostic_pinv"
        except np.linalg.LinAlgError:
            return self._undefined("singular")

        denominator_square = float(precision[0, 0] * precision[1, 1])
        if not np.isfinite(denominator_square) or denominator_square <= 0.0:
            return self._undefined("invalid_precision")
        rho = float(-precision[0, 1] / np.sqrt(denominator_square))
        if not np.isfinite(rho) or abs(rho) > 1.0 + 1e-10:
            return self._undefined("invalid_partial_correlation")
        rho = float(np.clip(rho, -np.nextafter(1.0, 0.0), np.nextafter(1.0, 0.0)))
        statistic = float(abs(np.arctanh(rho)) * np.sqrt(degrees_of_freedom))
        p_value = float(2.0 * norm.sf(statistic))
        return CIResult(
            p_value > self.alpha,
            p_value,
            statistic,
            rho,
            status,
            p_value - self.alpha,
        )
