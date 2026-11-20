# Held-out của P-N1, phân tích hậu nghiệm: hại nằm ở số cạnh hay ở thứ hạng? (20/11/2026)

> **Loại:** mô tả hậu nghiệm trên output held-out đã dùng cho các phép kiểm đăng ký ([v2.2](PN1_rules_v2_2_amendment_vi.md)). **Không** phải phép kiểm, không đổi nhãn nào của P-N1. Kết quả chỉ dùng để sinh giả thuyết cho P-N2, và phải được kiểm trên seed mới.
> **Lý do làm:** review của user ngày 20/11 chỉ ra rằng khi đổi đệm A → B, AVICI và CDFM đều dự đoán ít cạnh hơn ở khối đích, dù F1 đi ngược chiều (tính từ [báo cáo held-out §4](PN1_HELD_results_vi.md)). Câu hỏi tiếp theo: thay đổi nằm ở **mức điểm** (số cạnh vượt ngưỡng) hay ở **thứ hạng** cạnh đúng so với cạnh sai?
> **Code và số liệu:** [`posthoc/posthoc_rank_level.py`](posthoc/posthoc_rank_level.py) đọc module và output đã đóng băng, không sửa gì; kết quả ở [`posthoc/posthoc_rank_level.json`](posthoc/posthoc_rank_level.json). Trung bình theo hệ, CI bootstrap 95% theo hệ (2000 lần, seed 20261114). AVICI, CDFM: 80 hệ; FoundCause: 24 hệ.

## 1. Cách phân tách

Trên khối đích, skeleton, điểm của cặp (i, j) là max(p_ij, p_ji). Gọi m0 là số cạnh NATIVE của model ở k0, và F1_m0 là F1 khi lấy m0 cặp có điểm cao nhất. Với mỗi điều kiện c:

H(c) = F1_native(k0) − F1_native(c) = **[F1_m0(k0) − F1_m0(c)]** + **[F1_m0(c) − F1_native(c)]**

- **Phần thứ hạng** (ngoặc thứ nhất): giữ số cạnh như ở k0. Phần này chỉ khác 0 khi thứ tự cạnh đúng/sai thay đổi.
- **Phần số cạnh** (ngoặc thứ hai): tác động của việc model dự đoán nhiều hoặc ít cạnh hơn k0, tức mức điểm, hiệu chỉnh hoặc ngưỡng.
- Ở k0, với cả ba model, F1 của tập cạnh NATIVE bằng F1 của m0 cặp điểm cao nhất (chênh trung bình và CI đều là 0.000), nên tổng hai phần bằng đúng H.
- Kèm theo: ΔAUROC trên các cặp của khối đích (không phụ thuộc ngưỡng) và Δ số cạnh. Với CDFM thêm cách đọc FROZEN (giữ ngưỡng của k0) và độ đổi của ngưỡng NATIVE.

## 2. Kết quả

**Bảng 1. Thay đổi so với k0 (NATIVE).**

| Model, điều kiện | H | Phần thứ hạng | Phần số cạnh | Δ số cạnh | ΔAUROC |
|---|---|---|---|---|---|
| AVICI A20 | 0.068 [0.047, 0.091] | 0.050 [0.033, 0.068] | 0.019 [0.004, 0.034] | −0.5 [−1.6, +0.9] | −0.028 [−0.036, −0.021] |
| AVICI B20 | 0.118 [0.093, 0.143] | 0.041 [0.025, 0.057] | 0.077 [0.054, 0.103] | −5.4 [−6.6, −4.2] | −0.024 [−0.033, −0.015] |
| CDFM A20 | 0.085 [0.067, 0.104] | 0.024 [0.014, 0.036] | 0.060 [0.045, 0.076] | +7.1 [+2.3, +11.9] | −0.018 [−0.028, −0.009] |
| CDFM B20 | 0.049 [0.032, 0.066] | 0.050 [0.036, 0.065] | −0.001 [−0.014, +0.011] | −3.4 [−6.4, −0.5] | −0.035 [−0.048, −0.022] |
| CDFM C20 | 0.055 [0.040, 0.071] | 0.032 [0.022, 0.042] | 0.023 [0.010, 0.036] | +1.4 [−2.5, +4.9] | −0.019 [−0.029, −0.009] |
| FoundCause A20 | 0.093 [0.052, 0.138] | 0.050 [0.026, 0.075] | 0.043 [0.003, 0.089] | −4.2 [−7.1, −1.5] | −0.024 [−0.038, −0.011] |
| FoundCause B20 | 0.020 [0.001, 0.039] | 0.006 [−0.011, 0.024] | 0.014 [−0.004, 0.032] | +2.0 [+0.1, +4.0] | +0.000 [−0.014, +0.013] |

Điểm xuất phát ở k0 (trung bình mỗi hệ): AVICI dự đoán 17.5 cạnh, CDFM 33.0 cạnh, trong khi số cạnh thật là 22.4 (80 hệ). FoundCause dự đoán 23.8 cạnh, số cạnh thật 21.6 (24 hệ).

**Bảng 2. B − A.** Cột ΔF1 NATIVE trùng với hiệu H_A − H_B đã báo cáo ở held-out (kiểm chéo).

| Model | Δ số cạnh | ΔF1 NATIVE | ΔF1 ở số cạnh của k0 (thứ hạng) | ΔAUROC |
|---|---|---|---|---|
| AVICI | −4.9 [−6.6, −3.4] | −0.050 [−0.074, −0.024] | +0.008 [−0.014, +0.031] | +0.004 [−0.007, +0.015] |
| CDFM | −10.4 [−14.9, −6.4] | +0.036 [+0.015, +0.057] | −0.026 [−0.041, −0.012] | −0.017 [−0.027, −0.008] |
| FoundCause | +6.3 [+3.0, +9.9] | +0.073 [+0.028, +0.122] | +0.044 [+0.018, +0.071] | +0.025 [+0.001, +0.044] |

**Bảng 3. B − A theo họ dữ liệu.**

| Model | Họ | Δ số cạnh | ΔF1 NATIVE | ΔF1 ở số cạnh của k0 | ΔAUROC |
|---|---|---|---|---|---|
| AVICI | tuyến tính (40) | −7.2 [−10.0, −4.7] | −0.029 [−0.069, +0.012] | +0.052 [+0.020, +0.087] | +0.028 [+0.012, +0.044] |
| AVICI | RFF (40) | −2.6 [−4.1, −1.3] | −0.072 [−0.100, −0.044] | −0.036 [−0.056, −0.017] | −0.020 [−0.032, −0.007] |
| CDFM | tuyến tính (40) | −1.9 [−6.0, +2.6] | +0.021 [−0.001, +0.042] | −0.010 [−0.028, +0.008] | −0.004 [−0.016, +0.008] |
| CDFM | RFF (40) | −18.9 [−25.5, −12.9] | +0.050 [+0.016, +0.085] | −0.042 [−0.062, −0.021] | −0.030 [−0.044, −0.017] |
| FoundCause | tuyến tính (12) | +4.1 [+0.5, +7.9] | +0.087 [+0.027, +0.166] | +0.048 [+0.013, +0.083] | +0.031 [+0.017, +0.047] |
| FoundCause | RFF (12) | +8.4 [+3.6, +14.3] | +0.059 [−0.001, +0.120] | +0.041 [+0.002, +0.078] | +0.018 [−0.028, +0.054] |

**Bảng 4. CDFM: kênh ngưỡng.** H FROZEN dùng ngưỡng mà CDFM tự chọn ở k0 cho cùng hệ.

| Điều kiện | H NATIVE | H FROZEN | NATIVE − FROZEN | Δ ngưỡng NATIVE |
|---|---|---|---|---|
| A20 | 0.085 | 0.062 [0.047, 0.077] | +0.023 [+0.007, +0.040] | +0.054 [+0.025, +0.083] |
| B20 | 0.049 | 0.073 [0.058, 0.088] | −0.024 [−0.040, −0.008] | +0.154 [+0.137, +0.173] |
| C20 | 0.055 | 0.071 [0.056, 0.086] | −0.016 [−0.028, −0.003] | +0.103 [+0.080, +0.126] |

Ở A20, ngưỡng đổi ngược chiều theo họ: tuyến tính +0.144 [+0.112, +0.177] (số cạnh −3.0), RFF −0.037 [−0.059, −0.014] (số cạnh +17.1 [+11.7, +23.3]).

**Phụ: logit trung bình** (nhạy với đuôi phân phối; xác suất đã kẹp ở [10⁻⁶, 1 − 10⁻⁶]). Với AVICI, điểm giảm khi có đệm: A20 cặp đúng −0.49, cặp sai −0.88; B20 −1.07 và −0.58. Với CDFM, điểm tăng gần đều ở cả hai loại cặp: A20 +0.61 và +0.57; B20 +0.48 và +0.46.

## 3. Đọc (suy luận từ mô tả, chưa kiểm)

1. **Review đúng, và còn rõ hơn.** Khi đổi A → B, AVICI và CDFM đều dự đoán ít cạnh hơn (−4.9 và −10.4). F1 đi ngược chiều vì điểm xuất phát khác nhau. Ở k0, AVICI dự đoán thiếu (17.5 so với 22.4 cạnh thật), còn CDFM dự đoán thừa (33.0 so với 22.4). Cùng một dịch chuyển "ít cạnh hơn" kéo AVICI ra xa số cạnh thật và kéo CDFM lại gần.
2. **Ở cùng số cạnh, ba model khác nhau.** Khi giữ số cạnh như k0: với AVICI, B ≈ A (+0.008); với CDFM, B kém A (−0.026); với FoundCause, B tốt hơn A (+0.044). Vì vậy cũng chưa thể nói AVICI và CDFM "cùng cơ chế"; dữ liệu chỉ cho thấy chúng cùng chiều ở số cạnh.
3. **Hai loại hại xuất hiện ở những ô khác nhau.**
   - Phần thứ hạng chiếm phần lớn ở AVICI-A (0.050 trong 0.068) và gần như toàn bộ ở CDFM-B (0.050 trong 0.049, phần số cạnh ≈ 0).
   - Phần số cạnh chiếm phần lớn ở AVICI-B (0.077 trong 0.118) và CDFM-A (0.060 trong 0.085).

   Hai loại này dẫn tới hai cách sửa khác nhau: hiệu chỉnh hoặc chọn ngưỡng, so với sửa biểu diễn.
4. **CDFM có thêm kênh ngưỡng.** Ngưỡng NATIVE tăng khi có đệm, mạnh nhất ở B (+0.154). Điều này khớp với việc `suggest_threshold` tính đặc trưng trên toàn ma trận D×D: các cạnh riêng của khối đệm B đẩy phân phối điểm lên. Khi giữ ngưỡng của k0, B hại CDFM **nhiều hơn** A (0.073 so với 0.062). Chiều "B đỡ hơn A" của CDFM ở NATIVE đến từ ngưỡng.
5. **Họ dữ liệu quan trọng.**
   - Hiệu M1 của AVICI (B tệ hơn A) gần như hoàn toàn đến từ RFF (−0.072). Ở hệ tuyến tính, khi cùng số cạnh, B còn xếp hạng tốt hơn A (+0.052).
   - Ở CDFM, chênh lệch tập trung ở RFF: số cạnh −18.9, F1 +0.050.

   Review đúng ở điểm phải phân tích riêng hai họ.
6. **FoundCause.** Với B, output khối đích gần trở về k0 (H = 0.020, AUROC không đổi). Với A, model mất cả thứ hạng lẫn số cạnh. Kết quả này phù hợp với giả thuyết H3 (cột cô lập là trường hợp đặc biệt với FoundCause), nhưng chỉ trên 24 hệ.

## 4. Hệ quả cho P-N2

- **Biến đo chính** là số cạnh dự đoán và phần thứ hạng (F1 ở số cạnh của k0, AUROC); F1 chỉ là biến phụ. Với CDFM đọc cả NATIVE, FROZEN, FIXED (0.5) và chính ngưỡng NATIVE. Phân tích riêng tuyến tính và RFF.
- **Hướng dự đoán sinh từ dữ liệu này** (hậu nghiệm, phải kiểm trên seed mới, ghi vào luật P-N2 trước khi chạy):
  - AVICI: số cạnh khối đích giảm khi khối đệm có nhiều cạnh hơn; phần thứ hạng đổi theo họ.
  - CDFM: ngưỡng NATIVE tăng và số cạnh NATIVE giảm khi khối đệm có nhiều cạnh hơn; ở ngưỡng FROZEN, phần thứ hạng xấu đi, rõ nhất ở RFF.
  - FoundCause (bước sau): số cạnh tăng khi khối đệm có cạnh; nếu H3 đúng, hại đi theo số nút đệm cô lập.

## 5. Giới hạn

- Hậu nghiệm, trên dữ liệu đã dùng cho phép kiểm; không kiểm soát familywise. Mọi chiều nêu ở §3 là giả thuyết.
- Chọn m0 = số cạnh ở k0 là một lựa chọn; nếu thay bằng số cạnh thật, phần thứ hạng sẽ đổi giá trị.
- AUROC chỉ tính trên các cặp trong khối đích. Logit trung bình nhạy với đuôi.
- FoundCause chỉ có 24 hệ (12 mỗi họ).
