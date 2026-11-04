# Decision addendum A-001 / Spec 06

**Ngày:** 21/10/2026  
**Trạng thái:** `REVIEW_PENDING`  
**Mục đích:** hợp nhất các điểm đã thống nhất sau review Amendment A-001 và Spec 06.  
**Phạm vi:** chỉ K0–K4 và hạ tầng cache CI; không mở rộng sang Blockwise ICD, Robust Envelope, GPU hoặc benchmark bán tổng hợp.

## 1. Quyết định tổng thể

1. Dùng Amendment A-001 làm cơ sở cho giao thức `REDUCED_SCALE`.
2. Dùng Spec 06 làm cơ sở cho cache kết quả CI.
3. Không gọi kết quả reduced là formal `PASS`.
4. Không bật cache trước khi hoàn tất audit tương đương.
5. Không chạy K4 trước khi V5 về checkpoint ngân sách được giải quyết trong contract.

Các tài liệu cũ của dự án vẫn được giữ để truy vết; addendum này chỉ ghi các điểm đã sửa hoặc làm rõ.

## 2. Quy tắc quyết định theo stage

### 2.1. Stage 1

Stage 1 chỉ được trả về:

```text
FAIL          nếu CI 99% nằm hoàn toàn phía thất bại;
INCONCLUSIVE  trong các trường hợp còn lại.
```

Không được trả về `PASS` ở stage 1.

### 2.2. Stage cuối

- Nếu stage cuối là full matrix: có thể trả về formal `PASS` hoặc `FAIL` theo contract.
- Nếu stage cuối vẫn là ma trận rút gọn: mã phải là `PASS_REDUCED_EXPLORATORY`, không phải formal `PASS`.
- K3 stage 2 của A-001 chỉ có seed prefix `[5,10)`, không phải full matrix; vì vậy stage này không thể tạo formal PASS.

Hai lần xem dữ liệu vẫn có thể làm thay đổi xác suất quyết định sai. Cụ thể, kill sớm ở CI 99% tại stage 1 rồi đánh giá lại các trường hợp `INCONCLUSIVE` ở CI 95% tại stage sau làm xác suất `FAIL` oan tích lũy lớn hơn một lần kiểm định đơn lẻ. Báo cáo phải ghi rõ sequential look, không được trình bày CI pilot như CI danh định của một thử nghiệm duy nhất, và không được diễn giải `FAIL` pilot như kết luận cuối nếu chưa có xác nhận theo full contract.

### 2.3. ID phân tích K1

K1 phải phân biệt ba phân tích chồng lấn:

```text
K1-S = snapshot 133 graph hoàn chỉnh, chỉ mô tả;
K1-P = prefix 80 graph theo seed index, REDUCED_SCALE;
K1-F = full 160 graph, formal target.
```

Không gộp ba tập này, không coi chúng là mẫu độc lập và không dùng snapshot K1-S làm bằng chứng formal.

## 3. K1, K2, K3 và K4

### 3.1. K1

Ưu tiên vẫn là hoàn tất 125 row còn thiếu của K1-F. Nếu máy không đủ khả năng, K1-P dùng prefix seed index `[0,10)` ở cả 8 cell. Quy tắc chọn prefix phải cố định trước khi phân tích reduced.

### 3.2. K2 — hiệu chỉnh Prior B trước khi chạy gate

Không chờ tới lúc chạy graph đánh giá mới phát hiện AUC không hợp lệ.

Quy trình bắt buộc:

1. Dùng graph calibration riêng với seed ngoài vùng đánh giá, ví dụ seed `[1000,1020)` mỗi cell.
2. Hiệu chỉnh noise để Prior B đạt AUC mục tiêu `0.65 ± 0.02` trên calibration set.
3. Khóa tham số prior/noise.
4. Chỉ dùng graph đánh giá để xác nhận realized AUC và tính metric K2.
5. Nếu AUC đánh giá ngoài dung sai, trạng thái là `INVALID_PRIOR_CALIBRATION`, không phải `FAIL`.

### 3.3. Baseline `best_prior_free`

Việc chọn baseline trên cùng graph đánh giá có thể tạo winner's curse bất lợi cho prior, dẫn tới thiên lệch về `FAIL` hoặc `INCONCLUSIVE`, không phải làm claim dương giả.

Quy tắc mới:

- tạo `baseline_lock.json` trước khi chạy K2;
- ưu tiên chọn trên K1 seed `[10,20)` và đánh giá K2 stage 1 trên `[0,10)`;
- nếu K1 chưa đủ, chọn trên `[0,10)` nhưng phải ghi rõ hướng thiên lệch;
- báo cáo thêm so sánh với cả `random_valid`, `cost_only` và `graph_only`.

### 3.4. K3

K3 vẫn dùng toàn bộ 8 cell K1:

```text
p ∈ {10,20}
latent_ratio ∈ {0.2,0.4}
mean_degree ∈ {2,4}
```

Alias `same_as_K1` phải được khai triển tường minh trong YAML để tránh hiểu sai. Với stage 1 chỉ có 5 graph/cell, kết quả theo từng cell hoặc từng nhóm chỉ mang tính mô tả; quyết định pilot dùng phân tích gộp.

Thiếu `rfci_stable` hoặc `fcit_or_targeted` phải trả về `BLOCKED_BACKEND`, không được bỏ qua im lặng.

### 3.5. K4

Runner phải từ chối chạy K4 cho tới khi V5 xác nhận checkpoint ngân sách. Nếu contract dùng số CI tuyệt đối thay vì tỷ lệ weighted cost, toàn bộ lưới checkpoint phải được thay đổi theo contract.

Pilot K4 vẫn giữ cả `n=500` và `n=2000`. Pre-check độ chính xác chạy trước stage 1; nếu nửa độ rộng ước lượng của `Δh` lớn hơn `0.10`, phải đánh dấu trước rằng stage 1 gần như chắc chắn `INCONCLUSIVE` và lên kế hoạch stage 2.

K4 PASS là giao của bốn điều kiện: hai cỡ mẫu × `{endpoint harm, saving}`. Không được thay giao này bằng trung bình hoặc chỉ kiểm tra một cỡ mẫu.

## 4. Quyết định về Spec 06 — cache CI

### 4.1. `ci_key` bắt buộc

Không dùng `query_id` làm cache key. Trong repo, `query_id` có thể chứa counter/adapter context và chỉ dùng cho provenance.

```text
ci_key = (min(x,y), max(x,y), tuple(sorted(S)))
```

### 4.2. Alpha và giá trị cache

`alpha` không nằm trong cache key. Cache lưu các đại lượng không phụ thuộc alpha:

```text
p_value, statistic, effect, df, numerical_status
```

Khi đọc cache, wrapper tính lại:

```text
independent = p_value > alpha
decision_margin = p_value - alpha
```

Nếu một backend không thể tái dựng decision từ raw result, alpha phải được đưa vào khóa riêng của backend đó.

### 4.3. Digest của implementation

Không đưa mọi Git commit vào cache key. Thay vào đó dùng:

```text
ci_impl_digest = BLAKE2b(
    source bytes của danh sách module CI cố định
    || semantic_version
    || phiên bản numpy/scipy/networkx
)
```

`ci_impl_digest` phải nằm trong `backend_config_digest`. Metadata `code_revision` chỉ là thông tin truy vết, không thay thế digest.

Thêm test T11:

```text
đổi một byte trong source module CI → cache miss bắt buộc.
```

### 4.4. Cache không thay đổi evaluator

Thêm lint/regression test bảo đảm evaluator gate không đọc:

```text
ci_cache_*
*_ns
```

Các trường này chỉ phục vụ execution diagnostics và thời gian quy đổi; không được tham gia K1–K4 scientific decision.

### 4.5. Xác minh cache

Giữ T1–T10 của Spec 06 và thêm:

- `verify --full` trên các audit graph p=10, tối đa khoảng 11.520 query cho mỗi cấu hình phù hợp;
- `verify --full` trên 64 truth tables của C2;
- T11 cho source digest.

Verify 1%/tối thiểu 200 chỉ là kiểm tra vận hành định kỳ, không phải bằng chứng duy nhất của tương đương.

## 5. Thứ tự chạy thực tế

Không cần chờ cache mới hoàn tất K1.

### Giai đoạn A — hoàn tất K1

- chạy K1-F không cache, một worker;
- resume 125 row còn thiếu;
- chạy qua đêm nếu cần;
- giữ các row không cache làm reference cho T1 cache/no-cache.

### Giai đoạn B — audit cache ban ngày

- audit chỉ đọc;
- implement cache mặc định tắt;
- chạy T1–T11 và `verify --full`;
- chạy `estimate` trên graph pilot.

### Giai đoạn C — quyết định bật cache

Không dùng hit ratio 20% làm ngưỡng cứng. Quyết định dựa trên:

```text
estimated_compute_time_saved
    so với
chi phí phát triển + audit + rủi ro vận hành
```

Ưu tiên đo thời gian CI tiết kiệm, có trọng số theo `compute_ns`, không chỉ đếm số hit. Query có `|S|` lớn có thể tốn hơn nhiều query nhỏ.

### Giai đoạn D — K2/K3/K4

Chỉ bật cache sau khi gate hạ tầng đạt. Cache hit vẫn tính là một CI query logic, giữ nguyên weighted cost, budget và provenance.

## 6. Trạng thái hiện tại

```text
A-001: REVIEW_PENDING
Spec 06: REVIEW_PENDING
K0: PASS đã có từ ma trận chính thức
K1: ưu tiên hoàn tất full matrix; K1-S/K1-P chỉ là phân tích phụ
K2: chờ calibration Prior B
K3: có thể BLOCKED nếu thiếu RFCI/FCIT baseline
K4: BLOCKED cho tới khi V5 được giải quyết
CI cache: chưa bật, chưa thay đổi config_digest
```

## 7. Kết luận quyết định

Phản hồi review mới được chấp nhận ở các điểm sau:

- sửa quy tắc PASS stage;
- tách K1-S/K1-P/K1-F;
- chặn K4 cho tới khi V5 rõ;
- sửa chiều winner's curse của baseline;
- calibration Prior B trước K2;
- thêm T11 và verify full;
- chạy K1 trước cache;
- quyết định cache theo thời gian CI tiết kiệm, không theo hit ratio tùy ý.

Chưa có code hoặc gate nào được thay đổi bởi addendum này. Đây là quyết định thiết kế ở trạng thái `REVIEW_PENDING` để chủ dự án duyệt trước khi triển khai.
