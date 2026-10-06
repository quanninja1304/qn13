from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import psutil
from scipy.stats import norm

from .ci import CIResult, GaussianCI
from .models import CIQuery


@dataclass(frozen=True)
class BatchMemoryPlan:
    local_size: int
    padded_size: int
    query_count: int
    batch_capacity: int
    waves: int
    bytes_per_query: int
    peak_workspace_bytes: int
    budget_bytes: int


@dataclass(frozen=True)
class BatchDiagnostics:
    backend: str
    device: str
    dtype: str
    batching_strategy: str
    query_count: int
    bucket_count: int
    wave_count: int
    peak_workspace_bytes: int
    observed_peak_rss_bytes: int
    memory_budget_bytes: int
    ci_arithmetic_work: int
    gathered_matrix_elements: int
    shared_factorization_count: int
    shared_work_saved_estimate: int
    bucket_sizes: tuple[tuple[int, int], ...]


def _power_of_two(value: int) -> int:
    return 1 << (value - 1).bit_length()


def plan_batch_memory(
    local_size: int,
    query_count: int,
    budget_bytes: int,
    *,
    padded_size: int | None = None,
    dtype: np.dtype | type = np.float64,
    safety_factor: float = 1.25,
) -> BatchMemoryPlan:
    if local_size < 2:
        raise ValueError("local_size must be at least two")
    if query_count < 0:
        raise ValueError("query_count cannot be negative")
    if budget_bytes <= 0:
        raise ValueError("budget_bytes must be positive")
    if safety_factor < 1.0:
        raise ValueError("safety_factor must be at least one")
    padded = local_size if padded_size is None else int(padded_size)
    if padded < local_size:
        raise ValueError("padded_size cannot be smaller than local_size")

    itemsize = np.dtype(dtype).itemsize
    # Input/gather matrix, factorization/solve copy, output precision workspace,
    # two RHS columns, and fixed per-query result buffers.
    scalar_slots = 3 * padded * padded + 4 * padded + 16
    bytes_per_query = int(math.ceil(safety_factor * itemsize * scalar_slots))
    capacity = budget_bytes // bytes_per_query
    if query_count and capacity < 1:
        raise MemoryError(
            f"memory budget {budget_bytes} cannot fit one {padded}x{padded} CI workspace"
        )
    batch_capacity = min(query_count, capacity) if query_count else 0
    waves = math.ceil(query_count / batch_capacity) if query_count else 0
    peak = batch_capacity * bytes_per_query
    return BatchMemoryPlan(
        local_size,
        padded,
        query_count,
        batch_capacity,
        waves,
        bytes_per_query,
        peak,
        budget_bytes,
    )


class GaussianBatchCI:
    """NumPy float64 batch backend with scalar-compatible CI semantics."""

    device = "cpu"
    dtype = "float64"

    def __init__(
        self,
        data: np.ndarray,
        alpha: float = 0.05,
        *,
        input_kind: str = "samples",
        n_samples: int | None = None,
        inversion: str = "strict",
        ridge: float = 0.0,
        batching_strategy: str = "exact_size",
        memory_budget_bytes: int = 256 * 1024 * 1024,
        memory_safety_factor: float = 1.25,
        shared_s_min_reuse: int | None = None,
    ):
        if batching_strategy not in {"exact_size", "power_of_two"}:
            raise ValueError("batching_strategy must be exact_size or power_of_two")
        if memory_budget_bytes <= 0:
            raise ValueError("memory_budget_bytes must be positive")
        if shared_s_min_reuse is not None and shared_s_min_reuse < 2:
            raise ValueError("shared_s_min_reuse must be at least two")

        scalar_contract = GaussianCI(
            data,
            alpha,
            input_kind=input_kind,
            n_samples=n_samples,
            inversion=inversion,
            ridge=ridge,
        )
        self.alpha = scalar_contract.alpha
        self.input_kind = input_kind
        self.inversion = inversion
        self.ridge = scalar_contract.ridge
        self.n_samples = scalar_contract.n_samples
        self.n_variables = scalar_contract.n_variables
        self.batching_strategy = batching_strategy
        self.memory_budget_bytes = int(memory_budget_bytes)
        self.memory_safety_factor = float(memory_safety_factor)
        self.shared_s_min_reuse = shared_s_min_reuse
        self.backend = f"gaussian_cpu_batch_{batching_strategy}_{inversion}"
        self._single_counter = 0

        if input_kind == "samples":
            self.correlation = np.asarray(
                np.corrcoef(scalar_contract.data, rowvar=False), dtype=np.float64
            )
        else:
            self.correlation = np.asarray(scalar_contract.matrix, dtype=np.float64)
        self.last_diagnostics = BatchDiagnostics(
            self.backend,
            self.device,
            self.dtype,
            self.batching_strategy,
            0,
            0,
            0,
            0,
            psutil.Process().memory_info().rss,
            self.memory_budget_bytes,
            0,
            0,
            0,
            0,
            (),
        )

    def _validate_query(self, query: CIQuery) -> None:
        columns = (query.x, query.y, *query.conditioning_set)
        if min(columns) < 0 or max(columns) >= self.n_variables:
            raise IndexError(f"CI query {query.query_id!r} references an invalid column")

    @staticmethod
    def _undefined(status: str) -> CIResult:
        return CIResult(None, None, None, None, status, None)

    def _result_from_precision(
        self,
        precision_00: float,
        precision_01: float,
        precision_11: float,
        degrees_of_freedom: int,
        status: str,
    ) -> CIResult:
        denominator_square = float(precision_00 * precision_11)
        if not np.isfinite(denominator_square) or denominator_square <= 0.0:
            return self._undefined("invalid_precision")
        rho = float(-precision_01 / np.sqrt(denominator_square))
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

    def _evaluate_wave(
        self,
        query_indices: Sequence[int],
        queries: Sequence[CIQuery],
        padded_size: int,
        output: list[CIResult | None],
    ) -> None:
        solvable: list[tuple[int, CIQuery, np.ndarray, int]] = []
        for index in query_indices:
            query = queries[index]
            degrees_of_freedom = self.n_samples - len(query.conditioning_set) - 3
            if degrees_of_freedom <= 0:
                output[index] = self._undefined("insufficient_df")
                continue
            columns = (query.x, query.y, *query.conditioning_set)
            local = np.asarray(self.correlation[np.ix_(columns, columns)], dtype=np.float64)
            if not np.isfinite(local).all():
                output[index] = self._undefined("nonfinite_correlation")
                continue
            if self.inversion == "strict" and np.linalg.matrix_rank(local) < local.shape[0]:
                output[index] = self._undefined("singular")
                continue
            solvable.append((index, query, local, degrees_of_freedom))

        if not solvable:
            return

        matrices = np.repeat(np.eye(padded_size, dtype=np.float64)[None, :, :], len(solvable), axis=0)
        for position, (_, _, local, _) in enumerate(solvable):
            size = local.shape[0]
            matrices[position, :size, :size] = local

        status = "ok"
        if self.inversion == "ridge":
            matrices = matrices + self.ridge * np.eye(padded_size, dtype=np.float64)[None, :, :]
            status = "regularized_ridge"
        try:
            if self.inversion == "pinv":
                precision = np.linalg.pinv(matrices, rcond=1e-12)
                values = precision[:, :2, :2]
                status = "diagnostic_pinv"
            else:
                rhs = np.zeros((len(solvable), padded_size, 2), dtype=np.float64)
                rhs[:, 0, 0] = 1.0
                rhs[:, 1, 1] = 1.0
                solved = np.linalg.solve(matrices, rhs)
                values = solved[:, :2, :2]
        except np.linalg.LinAlgError:
            # A batched failure must not contaminate otherwise valid queries.
            for index, query, _, _ in solvable:
                scalar = GaussianCI(
                    self.correlation,
                    self.alpha,
                    input_kind="correlation",
                    n_samples=self.n_samples,
                    inversion=self.inversion,
                    ridge=self.ridge,
                )
                output[index] = scalar.test(query.x, query.y, query.conditioning_set)
            return

        for position, (index, _, _, degrees_of_freedom) in enumerate(solvable):
            output[index] = self._result_from_precision(
                float(values[position, 0, 0]),
                float(values[position, 0, 1]),
                float(values[position, 1, 1]),
                degrees_of_freedom,
                status,
            )

    def _evaluate_shared_group(
        self,
        query_indices: Sequence[int],
        queries: Sequence[CIQuery],
        output: list[CIResult | None],
    ) -> None:
        conditioning_set = queries[query_indices[0]].conditioning_set
        if self.inversion == "pinv":
            raise RuntimeError("shared-S is not available for diagnostic pinv mode")
        z = tuple(conditioning_set)
        conditional = self.correlation[np.ix_(z, z)] if z else np.empty((0, 0))
        if z and not np.isfinite(conditional).all():
            for index in query_indices:
                output[index] = self._undefined("nonfinite_correlation")
            return
        if self.inversion == "ridge" and z:
            conditional = conditional + self.ridge * np.eye(len(z))

        for index in query_indices:
            query = queries[index]
            degrees_of_freedom = self.n_samples - len(z) - 3
            if degrees_of_freedom <= 0:
                output[index] = self._undefined("insufficient_df")
                continue
            columns = (query.x, query.y, *z)
            local = np.asarray(self.correlation[np.ix_(columns, columns)], dtype=np.float64)
            if not np.isfinite(local).all():
                output[index] = self._undefined("nonfinite_correlation")
                continue
            if self.inversion == "strict" and np.linalg.matrix_rank(local) < local.shape[0]:
                output[index] = self._undefined("singular")
                continue
            endpoint = np.asarray(local[:2, :2], dtype=np.float64)
            status = "ok"
            if self.inversion == "ridge":
                endpoint = endpoint + self.ridge * np.eye(2)
                status = "regularized_ridge"
            if z:
                cross = np.asarray(local[:2, 2:], dtype=np.float64)
                try:
                    residual = endpoint - cross @ np.linalg.solve(conditional, cross.T)
                except np.linalg.LinAlgError:
                    output[index] = self._undefined("singular")
                    continue
            else:
                residual = endpoint
            determinant = float(np.linalg.det(residual))
            if not np.isfinite(determinant) or determinant <= 0.0:
                output[index] = self._undefined("singular")
                continue
            # Inverse of the 2x2 Schur complement; the common determinant
            # cancels from the partial-correlation ratio.
            output[index] = self._result_from_precision(
                float(residual[1, 1]),
                float(-residual[0, 1]),
                float(residual[0, 0]),
                degrees_of_freedom,
                status,
            )

    def test_many(self, queries: Sequence[CIQuery]) -> list[CIResult]:
        canonical = tuple(queries)
        if len({query.query_id for query in canonical}) != len(canonical):
            raise ValueError("CI query IDs must be unique within a batch")
        for query in canonical:
            self._validate_query(query)

        output: list[CIResult | None] = [None] * len(canonical)
        remaining = set(range(len(canonical)))
        shared_factorizations = 0
        shared_work_saved = 0
        wave_count = 0
        peak_workspace = 0
        process = psutil.Process()
        observed_peak_rss = process.memory_info().rss
        bucket_sizes: list[tuple[int, int]] = []
        if self.shared_s_min_reuse is not None and self.inversion != "pinv":
            by_set: dict[tuple[int, ...], list[int]] = {}
            for index, query in enumerate(canonical):
                by_set.setdefault(query.conditioning_set, []).append(index)
            for conditioning_set, indices in by_set.items():
                if conditioning_set and len(indices) >= self.shared_s_min_reuse:
                    local_size = canonical[indices[0]].local_size
                    plan = plan_batch_memory(
                        local_size,
                        len(indices),
                        self.memory_budget_bytes,
                        dtype=np.float64,
                        safety_factor=self.memory_safety_factor,
                    )
                    self._evaluate_shared_group(indices, canonical, output)
                    observed_peak_rss = max(observed_peak_rss, process.memory_info().rss)
                    remaining.difference_update(indices)
                    shared_factorizations += 1
                    shared_work_saved += (len(indices) - 1) * len(conditioning_set) ** 3
                    wave_count += plan.waves
                    peak_workspace = max(peak_workspace, plan.peak_workspace_bytes)
                    bucket_sizes.append((local_size, len(indices)))

        buckets: dict[int, list[int]] = {}
        for index in sorted(remaining):
            local_size = canonical[index].local_size
            padded_size = (
                local_size
                if self.batching_strategy == "exact_size"
                else _power_of_two(local_size)
            )
            buckets.setdefault(padded_size, []).append(index)

        for padded_size, indices in sorted(buckets.items()):
            planner_size = (
                canonical[indices[0]].local_size
                if self.batching_strategy == "exact_size"
                else padded_size
            )
            plan = plan_batch_memory(
                planner_size,
                len(indices),
                self.memory_budget_bytes,
                padded_size=padded_size,
                dtype=np.float64,
                safety_factor=self.memory_safety_factor,
            )
            bucket_sizes.append((padded_size, len(indices)))
            wave_count += plan.waves
            peak_workspace = max(peak_workspace, plan.peak_workspace_bytes)
            for start in range(0, len(indices), plan.batch_capacity):
                self._evaluate_wave(
                    indices[start : start + plan.batch_capacity],
                    canonical,
                    padded_size,
                    output,
                )
                observed_peak_rss = max(observed_peak_rss, process.memory_info().rss)

        unresolved = [index for index, result in enumerate(output) if result is None]
        if unresolved:
            raise RuntimeError(f"batch backend left unresolved query results: {unresolved}")
        self.last_diagnostics = BatchDiagnostics(
            self.backend,
            self.device,
            self.dtype,
            self.batching_strategy,
            len(canonical),
            len(buckets) + shared_factorizations,
            wave_count,
            peak_workspace,
            observed_peak_rss,
            self.memory_budget_bytes,
            sum(query.local_size**3 for query in canonical),
            sum(query.local_size**2 for query in canonical),
            shared_factorizations,
            shared_work_saved,
            tuple(bucket_sizes),
        )
        return [result for result in output if result is not None]

    def test(self, i: int, j: int, conditioning_set=()) -> CIResult:
        self._single_counter += 1
        query = CIQuery(
            query_id=f"single:{self._single_counter}:{int(i)}:{int(j)}",
            x=int(i),
            y=int(j),
            conditioning_set=tuple(map(int, conditioning_set)),
            phase="scalar_adapter",
            epoch_id="single",
            pair_order=0,
            canonical_rank=0,
        )
        return self.test_many((query,))[0]
