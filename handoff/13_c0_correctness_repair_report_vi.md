# Sprint C0 — Correctness repair và Gate G0

**Trạng thái:** `G0_CORRECTNESS_BASELINE = PASS`

**Ngày đánh giá:** 2026-10-05

**Base revision:** `c26cdc95ee6e36d6a7d7ad039a1f596a2588ff79`

**Phạm vi:** chỉ WP0/G0 trong `12_certified_blockwise_icd_implementation_plan_vi.md`.

## 1. Kết quả ngắn gọn

Sprint C0 đã sửa hai correctness blocker phải được loại bỏ trước khi xây batching, block executor hoặc GPU backend:

1. `GaussianCI` không còn tính p-value rồi luôn trả `dependent`;
2. skeleton discovery không còn union nhiều separating witness của cùng một cặp cạnh.

Không có thay đổi nào về candidate semantics của ICD, batching, GPU, cache thiết bị hay benchmark hiệu năng trong sprint này.

## 2. Sửa GaussianCI

### 2.1 Semantics quyết định

Với truy vấn `(X_i, X_j | S)`, implementation scalar hiện dùng:

```text
df = n - |S| - 3
z  = |atanh(rho_ij.S)| * sqrt(df)
p  = 2 * NormalSurvival(z)
independent <=> p > alpha
```

`alpha` là tham số bắt buộc phải nhất quán giữa CI backend và discovery runner. Nếu hai phía khác nhau, runner dừng ngay thay vì để skeleton và Possible-D-SEP áp dụng hai ngưỡng khác nhau.

### 2.2 Input contract

`GaussianCI` phân biệt tường minh ba loại input:

| `input_kind` | Dữ liệu | Yêu cầu |
|---|---|---|
| `samples` | ma trận hàng-mẫu/cột-biến | suy ra `n` từ số hàng |
| `covariance` | ma trận hiệp phương sai | phải truyền `n_samples`; chuẩn hóa sang correlation |
| `correlation` | ma trận tương quan | phải truyền `n_samples`; đường chéo bằng 1 |

Query contract từ chối endpoint trùng nhau, conditioning set chứa phần tử lặp, endpoint nằm trong conditioning set và column index ngoài miền. Conditioning set được canonicalize bằng thứ tự tăng dần sau khi đã kiểm tra duplicate.

### 2.3 Numerical modes và ranh giới claim

| Mode | Backend label | Hành vi | Được dùng cho equality claim? |
|---|---|---|---|
| `strict` | `gaussian_strict` | solve ma trận khả nghịch; singular trả undefined | Có |
| `ridge` | `gaussian_ridge` | cộng `lambda I`, với `lambda > 0` tường minh | Không đồng nhất với strict |
| `pinv` | `gaussian_pinv_diagnostic` | Moore–Penrose pseudoinverse | Chỉ diagnostic |

Không còn `max(1, df)` hoặc pseudoinverse mặc định. `df <= 0`, singular, correlation không hữu hạn, precision không hợp lệ và partial correlation ngoài miền đều sinh `CIResult(independent=None, ...)` cùng `numerical_status` cụ thể.

Mỗi kết quả hợp lệ lưu:

- `effect`: partial correlation `rho`;
- `statistic`: trị tuyệt đối Fisher-Z;
- `p_value`;
- `decision_margin = p_value - alpha`;
- `numerical_status`.

### 2.4 Undefined không được âm thầm biến thành dependent

Provenance ghi query với `ci_decision="undefined"`, sau đó discovery ném `UndefinedCIResultError` trước mọi graph mutation. Exception mang một failure artifact JSON-serializable gồm terminal status, failure type, query ID, numerical status và query record đầy đủ. Điều này ngăn undefined bị diễn giải sai thành bằng chứng giữ cạnh.

## 3. Sửa separating-set witness

### 3.1 Lỗi cũ

Trong một frozen depth epoch, nếu cùng cặp `(X,Y)` có nhiều CI query độc lập với các set `S1`, `S2`, code cũ lưu `S1 union S2`. Phép union này không bảo toàn d-separation nói chung.

Phản ví dụ regression dùng đường:

```text
X -> C1 <- M -> C2 <- Y
```

`{C1}` và `{C2}` riêng lẻ đều chặn đường vì còn một collider đóng. `{C1,C2}` mở cả hai collider và làm đường hoạt động. Vì vậy union hai witness hợp lệ có thể tạo một non-witness.

### 3.2 Semantics mới

Mỗi kết quả độc lập tạo một `SeparationWitness` riêng:

```text
(canonical_pair, conditioning_set, query_id, canonical_rank)
```

`canonical_rank` được gán từ candidate list đã đóng băng trước khi scheduler sắp thứ tự. Khi epoch hoàn tất, witness được commit là:

```text
argmin_witness (canonical_rank, query_id)
```

Do đó lựa chọn không phụ thuộc execution order của scheduler. Các witness khác vẫn tồn tại trong query log với `independence_witness=true`, nhưng chỉ witness được chọn có:

- `separating_set_recorded=true`;
- `edge_removed=true`;
- query ID xuất hiện trong `evidence_query_ids` của edge-removal event.

Graph event lưu thêm `witness_query_id`, `witness_count` và `selection_policy`. Nếu budget dừng giữa epoch, không witness nào được commit và không cạnh nào bị xóa tại epoch đó.

## 4. Thay đổi provenance/schema tối thiểu

`QueryRecord` được mở rộng tương thích ngược bằng các field có default:

- `independence_witness`;
- `ci_effect`;
- `ci_numerical_status`;
- `ci_decision_margin`.

Field cũ `separating_set_recorded` nay mang nghĩa chặt: witness thực sự được chọn để commit, không phải mọi query trả độc lập. Legacy K0 output graph không bị thay đổi; query-level provenance mới chính xác hơn nên query signature của run mới có thể khác artifact cũ nếu signature bao gồm các cờ evidence.

## 5. Verification evidence

### 5.1 Targeted regression

```text
python -m pytest tests/test_gaussian_ci.py \
  tests/test_discovery_conformance.py tests/test_provenance_gates.py -q
22 passed
```

Coverage gồm:

- Gaussian unconditional, chain, fork và collider;
- đối chiếu công thức precision/Fisher-Z thủ công;
- covariance/correlation input và conditioning-order invariance;
- strict `p > alpha` tại boundary;
- insufficient degrees of freedom;
- singular strict mode và explicit ridge/pinv modes;
- query validation;
- collider counterexample cho sepset union;
- canonical witness bất biến giữa `stable_default` và `random_valid`;
- structured undefined failure trước graph mutation;
- alpha mismatch fail-fast.

### 5.2 Full suite

```text
python -m pytest
67 passed, 15 skipped in 25.12s
```

Các test skip là optional/reference-environment tests đã tồn tại; sprint không chuyển skip thành pass giả.

### 5.3 K0 oracle regression

Toàn bộ 220 run có `phase=0, scope=main` trong `artifacts/kill_test/runs.parquet` được replay in-memory bằng code C0. Digest của canonical output được so với artifact trước sprint:

```text
checked = 220
digest_mismatches = 0
```

Không cập nhật expected output để ép test xanh. K0 canonical graph output vì vậy không đổi sau correctness repair.

Machine-readable gate record: `reports/algorithm_sprints/g0_correctness_baseline.json`.

## 6. Gate G0 checklist

| Điều kiện | Kết quả | Bằng chứng |
|---|---|---|
| Mỗi skeleton deletion có đúng witnessed sepset ID | PASS | event regression + selected-query flags |
| Không union sepset trong evidence path | PASS | collider counterexample + scheduler-invariance test |
| Scalar Gaussian tests pass | PASS | `tests/test_gaussian_ci.py` |
| Oracle/K0 canonical output không đổi | PASS | 220/220 digest match |
| Full suite pass | PASS | 67 passed, 15 skipped |
| Numerical undefined tạo structured failure và dừng trước mutation | PASS | undefined-CI regression |

## 7. Những gì G0 chưa chứng minh

G0 không chứng minh final-PAG finite-sample correctness, GPU equivalence, block completeness, ICD equivalence hay speedup. Nó chỉ xác nhận baseline scalar và evidence semantics đủ sạch để bước sang WP1. Không được dùng kết quả này để tuyên bố `GaussianCI` finite-sample sound dưới singular/high-dimensional regimes; các regime đó hiện fail closed hoặc phải chọn một backend regularized có label riêng.

## 8. Bước kế tiếp được phép

Sau khi commit C0, sprint kế tiếp là WP1: khóa authoritative reference, artifact schema 0.2.0, canonical equality target và reference modes. Chưa nên bắt đầu tensor/GPU kernel trước khi WP1 hoàn tất.
