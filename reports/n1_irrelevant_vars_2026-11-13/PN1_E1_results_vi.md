# Kết quả E1 của P-N1: thêm 20 cột độc lập có làm mô hình causal discovery học sẵn đổi kết luận không? (16/11/2026)

> **Luật đọc:** [v2](PN1_reading_rules_vi.md) cộng [bản sửa v2.1](PN1_rules_v2_1_amendment_vi.md), khóa 14/11/2026. Mã phân tích `artifacts/n1_runs/pn1/analyze_e1.py` viết và dùng trước khi xem bất kỳ output E1 nào. Output: `artifacts/n1_runs/pn1_out/e1_{avici,cdfm,foundcause}.json`.
> **Phạm vi E1:** 80 hệ exploratory (8 ô × 10 seed; d_T ∈ {10, 20}; ER edges/node ∈ {1, 2}; tuyến tính Gauss hoặc RFF), n = 500; so k = 0 với kiểu đệm **A** (Gauss độc lập), **k = 20**. Đây là contrast chính định trước.
> **Nhãn:** [Verified-run]. Mọi CI là bootstrap theo hệ, 2 000 lần, percentile 95%, seed 20261114. Đây là kết quả **exploratory**; xác nhận chỉ đến từ held-out (A9).

## 1. Cổng RN0 (đều đạt)

| | AVICI `scm-v0` | CDFM | FoundCause |
|---|---|---|---|
| Tất định (τ_rep) | 0 | 0 | 0 |
| τ_sched (FoundCause, đổi lịch ensemble) | — | — | Δp 0.0116; flips 2.0 (fixed) / 2.25 (native) |
| Equivariance | max 1.6·10⁻⁶ ≤ 10⁻⁴ | max 1.7·10⁻⁶ ≤ 10⁻⁴ | p95 5.3·10⁻⁶ ≤ τ_sched |
| Adapter parity (A5) | — | — | đạt trên 16/16 hệ DEV |
| Năng lực nền (A10): F1 tuyến tính DEV, FIXED, k = 0 | 0.73 | 0.57 | 0.78 |
| (đồ thị đầy đủ: 0.36; PC 0.73; GES 0.78) | đạt | đạt | đạt |
| Oracle-PC (RN0.5) | 40/40 bất biến chính xác | | |
| Kiểm bitwise tensor đích (RN0.4) | đạt mọi input | | |

Job: E1 160/160 cho mỗi model và cho PC, GES; 0 lỗi.

## 2. Phán quyết theo từng model (A, k = 20, 80 hệ)

| | AVICI | CDFM | FoundCause |
|---|---|---|---|
| τ dùng cho nhãn (Δp; flips) | 0; 0 | 0; 0 | 0.0116; 2.0–2.25 |
| **SCORE_CHANGE** (median Δp) | 0.027 [0.021, 0.036] **MEANINGFUL** | 0.126 [0.117, 0.134] **MEANINGFUL** | 0.087 [0.075, 0.094] **MEANINGFUL** |
| **GRAPH_CHANGE_NATIVE** (flips/hệ) | 7.1 [5.5, 8.9] **MEANINGFUL** | 20.7 [16.3, 25.2] **MEANINGFUL** | 10.1 [8.3, 12.0] **MEANINGFUL** |
| **GRAPH_CHANGE_FIXED** | 7.1 [5.5, 8.9] **MEANINGFUL** | 22.7 [18.5, 26.8] **MEANINGFUL** | 10.1 [8.3, 12.1] **MEANINGFUL** |
| F1 ở k = 0 (native / fixed) | 0.765 / 0.765 | 0.673 / 0.568 | 0.730 / 0.730 |
| **H_NATIVE** | 0.075 [0.056, 0.094] **HARM** | 0.064 [0.044, 0.085] **HARM** | 0.065 [0.045, 0.084] **HARM** |
| **H_FIXED** | 0.075 [0.056, 0.094] **HARM** | 0.070 [0.054, 0.087] **HARM** | 0.064 [0.045, 0.083] **HARM** |
| **BEYOND_CLASSICAL, H_NATIVE** (40 hệ tuyến tính) | +0.122 [0.097, 0.147] **PASS** | +0.032 [0.010, 0.055] **không đạt** (điểm < 0.05) | +0.092 [0.061, 0.120] **PASS** |
| **BEYOND_CLASSICAL, H_FIXED** | +0.122 [0.097, 0.147] **PASS** | +0.064 [0.038, 0.091] **PASS** | +0.092 [0.061, 0.121] **PASS** |
| M4 decoder | không áp dụng | H_N − H_FROZEN = −0.002 [−0.022, +0.018]: **không đạt** | H_N − H_F = +0.000 [−0.001, +0.002]: **không đạt** |
| Cạnh dự đoán đích↔đệm X (trung bình/hệ; đúng là 0): FIXED / native | 4.3 / 4.3 | 165.0 / **71.0** | 0.24 / 0.22 |

**Đọc:** cả ba model đều đổi output trên khối đích ở mức MEANINGFUL theo cả ba nhãn, và đều mất chất lượng (HARM) theo cả hai estimand. Năm trên sáu so sánh "tệ hơn cổ điển" đạt; ngoại lệ là CDFM ở chế độ native. Decoder không giải thích được thay đổi ở CDFM hay FoundCause (M4 không đạt): thay đổi nằm ở **điểm thô**, tức ở phần mã hóa hoặc prior, không ở bước cắt ngưỡng.

Số so sánh chính là 6 (3 model × 2 estimand); kết quả "≥ 1 trong 6 đạt" chưa kiểm soát familywise. Đây vẫn là bằng chứng exploratory.

## 3. Mốc cổ điển (giống nhau cho cả ba model)

| | H (tuyến tính) | F1 gần tương đương? | Flips/hệ | Output gần bất biến? | Cạnh đích↔đệm |
|---|---|---|---|---|---|
| PC, tuyến tính | −0.001 [−0.005, 0.002] | **có** | 0.05 [0, 0.13] | **có** | 1.9 |
| GES, tuyến tính | +0.003 [−0.002, 0.008] | **có** | 0.95 [0.45, 1.53] | **không** (cận trên ≥ 1) | 5.3 |
| PC, RFF (diagnostic, misspecified) | −0.002 | có | 0.03 | có | 3.6 |
| GES, RFF (diagnostic, misspecified) | +0.002 | có | 0.30 | có | 5.3 |

PC ở n = 500 gần như bất biến cả về F1 lẫn output. GES giữ F1 nhưng output đổi trung bình khoảng 1 cặp mỗi hệ. Mô hình học sẵn đổi 7–23 cặp mỗi hệ.

## 4. Mô tả theo ô (exploratory, không dùng để quyết định)

- **AVICI:** hại tập trung ở hệ **tuyến tính** (H 0.08–0.15) và gần 0 ở RFF (0.00–0.05). Số cạnh dự đoán trong khối đích **giảm** khi thêm đệm (ví dụ d_T = 10, 2 cạnh/nút, tuyến tính: 23.6 → 13.1).
- **CDFM:** số cạnh trong khối đích **tăng** (ví dụ d_T = 20, 1 cạnh/nút, RFF: 66 → 105), và mô hình nối **rất nhiều cạnh giữa đích và đệm độc lập** (34–392 mỗi hệ tùy ô). Ngưỡng thích nghi trung bình tăng từ 0.68 lên 0.74, nhưng đóng băng nó không đổi H.
- **FoundCause:** hại ở cả tuyến tính (0.09–0.12) lẫn RFF (0.01–0.08); gần như không nối đích với đệm (X ≈ 0.2); số cạnh trong khối đích giảm nhẹ.
- Ba model đổi theo **ba hướng khác nhau** (AVICI tỉa bớt cạnh, CDFM thêm cạnh và nối sang đệm, FoundCause đổi cạnh mà gần như không nối sang đệm). Đây là quan sát mô tả, chưa phải cơ chế.

## 5. Hệ quả theo luật

- **Điều kiện mở E2 của FoundCause (v2.1 §2): ĐẠT** (cả ba nhãn đều MEANINGFUL với τ = max(τ_rep, τ_sched)). Theo phương án user chọn ngày 14/11, FoundCause chạy **E2 rút gọn**: 480 job (A tại k ∈ {5, 10, 30}; B, C, D tại k = 20).
- AVICI, CDFM, PC, GES chạy **E2 đầy đủ**: 1 200 job mỗi model.
- Sau E2: đọc RN2 (liều lượng), RN3 (chữ ký M1–M3), chọn lead cơ chế cho từng model theo luật; đóng băng lead, contrast và dấu; rồi mở **24 hệ held-out** (A9). Quyết định dự án chỉ đến sau held-out.

## 6. Giới hạn của kết quả này
- Exploratory, chưa qua held-out; 6 so sánh chính chưa hiệu chỉnh familywise.
- Hại đo trên skeleton; F1 có hướng chưa đọc.
- "Tệ hơn cổ điển" chỉ có nghĩa trên 40 hệ tuyến tính Gauss.
- Một checkpoint mỗi model, một bộ sinh, n = 500.
- Mỗi (hệ, kiểu, k) chỉ một bản rút đệm.

## 7. Review độc lập sau khi chạy (16/11/2026, làm lại theo yêu cầu của user)

Mã: `artifacts/n1_runs/pn1/review_e1_independent.py`. Script này **không** dùng `metrics.py` hay `analyze_e1.py`: nó đọc thẳng file `.npz`, sinh lại ground truth và tính lại.

**Kiểm tính toàn vẹn** [Verified-run]:
- Transcript FoundCause: 215 dòng `ok` = 55 job DEV còn lại + 160 job E1; không có dòng lỗi, cảnh báo bộ nhớ hay traceback; cổng RN0 in `True` trước khi E1 bắt đầu.
- Log: 58/58 và 160/160 `ok`, tất cả 4 luồng. Thời gian chạy ổn định theo d (145 s, 232 s, 330 s, 416 s cho d = 10, 20, 30, 40), không có job bất thường.
- 160 job E1: `input_sha` trùng nhau giữa cả năm thuật toán ở mọi job (cùng một bảng dữ liệu cho mọi model); `target_sha` ở k = 0 và k = 20 trùng nhau ở 80/80 hệ; kích thước output đúng (d_T và d_T + 20).
- **Tính lại độc lập khớp tuyệt đối** với `analyze_e1.py` cho cả ba model: median Δp, flips (fixed, native), H_FIXED, H_NATIVE, và hiệu so với mốc cổ điển.

**Sửa một con số trong §2 và §4:** "165 cạnh đích↔đệm" của CDFM là ở chế độ **FIXED 0.5**. Ở chế độ **native** (ngưỡng thích nghi, output người dùng thật sự nhận), con số là **71** mỗi hệ. Cả hai đều rất xa 0, nhưng 165 phóng đại hành vi mặc định của gói. Ngưỡng 0.5 không phải bộ giải mã hợp lý cho CDFM (F1 ở k = 0 chỉ 0.57 so với 0.67 native), nên với CDFM nên đọc estimand native là chính.

**Kiểm độ bền [Post hoc, không thuộc luật khóa, không đổi phán quyết]:**

| | AVICI | CDFM | FoundCause |
|---|---|---|---|
| Tỉ lệ hệ có H_NATIVE > 0 / = 0 / < 0 | 74% / 15% / 11% | 74% / 6% / 20% | 79% / 4% / 18% |
| Median H_NATIVE | 0.047 | 0.044 | 0.057 |
| Giảm AUPRC skeleton (không phụ thuộc ngưỡng) | 0.034 [0.021, 0.048] | 0.036 [0.024, 0.050] | 0.050 [0.034, 0.065] |
| H_NATIVE, hệ tuyến tính | 0.125 [0.099, 0.151] | 0.036 [0.015, 0.057] | 0.095 [0.066, 0.124] |
| H_NATIVE, hệ RFF | 0.025 [0.010, 0.043] | 0.092 [0.059, 0.126] | 0.034 [0.015, 0.053] |
| Số cạnh native trong khối đích, k = 0 → k = 20 (thật: 23.0) | 18.2 → 15.4 | 34.9 → 38.9 | 22.6 → 19.8 |

- Hại **không do vài hệ ngoại lai** (khoảng ba phần tư số hệ tệ đi) và **không do chọn ngưỡng** (AUPRC cũng giảm, CI không chứa 0).
- AVICI và FoundCause hại chủ yếu ở hệ **tuyến tính**; CDFM ngược lại, hại chủ yếu ở **RFF**. Đây là lý do CDFM native không đạt "tệ hơn cổ điển": tiêu chí đó chỉ tính trên hệ tuyến tính.
- CDFM dự đoán thừa cạnh ngay ở k = 0 (34.9 so với 23.0 thật): nền của nó yếu hơn hai model kia.
- **Nhiễu lịch ensemble của FoundCause trong F1** (DEV, k = 0, base 42 trừ base 1042): trung bình −0.007, độ lệch chuẩn 0.018. Nhỏ so với H = 0.065 và không có dấu hệ thống, nên không giải thích được mức hại. Lưu ý: luật khóa chỉ so Δp và flips với τ_sched, không so H; đây là kiểm bổ sung.

**Điều review này không giải quyết được (đúng theo thiết kế, chờ E2 và held-out):**
1. E1 chỉ có kiểu đệm A. Chưa tách được "thêm biến độc lập" khỏi "bảng lớn hơn với thống kê khác" (cần kiểu B, C, D của E2).
2. Vẫn là exploratory; sáu so sánh chính chưa hiệu chỉnh familywise.
3. Log của PC/GES không ghi `target_sha`; tính toàn vẹn của chúng được kiểm qua `input_sha` trùng với model.

**Kết luận review:** không tìm thấy lỗi pipeline hay lỗi phân tích; phán quyết ở §2 giữ nguyên, với một chỉnh sửa về cách báo số cạnh chéo của CDFM. Bước kế tiếp không đổi: E2.
