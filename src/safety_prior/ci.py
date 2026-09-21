from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class CIResult:
    independent: bool
    p_value: float
    statistic: float | None = None


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

    def __init__(self, data: np.ndarray):
        self.data = np.asarray(data, dtype=float)
        if self.data.ndim != 2 or np.isnan(self.data).any():
            raise ValueError("Gaussian CI requires a complete 2D array")

    def test(self, i: int, j: int, conditioning_set: Iterable[int]) -> CIResult:
        cols = [int(i), int(j), *sorted(set(map(int, conditioning_set)))]
        corr = np.corrcoef(self.data[:, cols], rowvar=False)
        precision = np.linalg.pinv(corr, rcond=1e-12)
        rho = float(-precision[0, 1] / np.sqrt(max(1e-30, precision[0, 0] * precision[1, 1])))
        rho = float(np.clip(rho, -0.999999999, 0.999999999))
        stat = abs(np.arctanh(rho)) * np.sqrt(max(1, self.data.shape[0] - len(cols) - 1))
        p = float(2 * (1 - norm.cdf(stat)))
        return CIResult(False, p, stat)

