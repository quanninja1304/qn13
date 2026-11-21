# Held-out của P-N1, phân tích hậu nghiệm: hại nằm ở số cạnh hay ở thứ hạng? (20/11/2026)

> **Loại:** mô tả hậu nghiệm trên output held-out đã dùng cho các phép kiểm đăng ký ([v2.2](PN1_rules_v2_2_amendment_vi.md)). **Không** phải phép kiểm, không đổi nhãn nào của P-N1. Kết quả chỉ dùng để sinh giả thuyết cho P-N2, và phải được kiểm trên seed mới.
> **Lý do làm:** review của user ngày 20/11 chỉ ra rằng khi đổi đệm A → B, AVICI và CDFM đều dự đoán ít cạnh hơn ở khối đích, dù F1 đi ngược chiều (tính từ [báo cáo held-out §4](PN1_HELD_results_vi.md)). Câu hỏi tiếp theo: thay đổi nằm ở **mức điểm** (số cạnh vượt ngưỡng) hay ở **thứ hạng** cạnh đúng so với cạnh sai?
> **Code và số liệu:** [`posthoc/posthoc_rank_level.py`](posthoc/posthoc_rank_level.py) đọc module và output đã đóng băng, không sửa gì; kết quả ở [`posthoc/posthoc_rank_level.json`](posthoc/posthoc_rank_level.json). Bảng 5 tính từ `held_cdfm.json` đã đóng băng. Trung bình theo hệ, CI bootstrap 95% theo hệ (2000 lần, seed 20261114). AVICI, CDFM: 80 hệ; FoundCause: 24 hệ.
> **Đính chính lần 2 (20/11, sau review thứ hai của user):** sửa §1, §3 mục 2–4, §4, §5 và thêm Bảng 5. Danh sách ở §6.

## 1. Cách phân tách

Trên khối đích, skeleton, điểm của cặp (i, j) là max(p_ij, p_ji). Gọi m0 là số cạnh NATIVE của model ở k0, và F1_m0 là F1 khi lấy m0 cặp có điểm cao nhất. Với mỗi điều kiện c:

H(c) = F1_native(k0) − F1_native(c) = **[F1_m0(k0) − F1_m0(c)]** + **[F1_m0(c) − F1_native(c)]**

- **Phần thứ hạng** (ngoặc thứ nhất): giữ số cạnh như ở k0. Phần này chỉ khác 0 khi thứ tự cạnh đúng/sai thay đổi.
- **Phần số cạnh** (ngoặc thứ hai): tác động của việc model dự đoán nhiều hoặc ít cạnh hơn k0, tức mức điểm, hiệu chỉnh hoặc ngưỡng.
- Ở k0, với cả ba model, F1 của tập cạnh NATIVE bằng F1 của m0 cặp điểm cao nhất (chênh trung bình và CI đều là 0.000), nên tổng hai phần bằng đúng H.
- Kèm theo: ΔAUROC trên các cặp của khối đích (không phụ thuộc ngưỡng) và Δ số cạnh. Với CDFM thêm cách đọc FROZEN (giữ ngưỡng của k0) và độ đổi của ngưỡng NATIVE.

**Đây là phân rã kế toán theo mốc m0 đã chọn, không phải chia hại thành hai nguyên nhân độc lập.**

- Chọn mốc khác, ví dụ số cạnh thật, sẽ cho tỉ lệ khác giữa hai phần.
- FROZEN cũng không phải phép đo thuần thứ hạng: ngưỡng cố định vẫn để số cạnh đổi khi điểm dịch.
- Câu hỏi về thứ hạng được trả lời bằng F1 ở top-m0, AUROC và AP.

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

Trung bình **|Δ số cạnh|** (B − A) lớn hơn nhiều so với Δ trung bình ở một số ô, vì thay đổi dương và âm triệt tiêu nhau. Ví dụ CDFM tuyến tính: Δ trung bình −1.9 cạnh, trung bình |Δ| 10.5 cạnh. Các ô còn lại: CDFM RFF 19.0, AVICI tuyến tính 8.0, AVICI RFF 3.0.

**Bảng 4. CDFM: ngưỡng so với k0.** H FROZEN dùng ngưỡng mà CDFM tự chọn ở k0 cho cùng hệ.

| Điều kiện | H NATIVE | H FROZEN | NATIVE − FROZEN | Δ ngưỡng NATIVE |
|---|---|---|---|---|
| A20 | 0.085 | 0.062 [0.047, 0.077] | +0.023 [+0.007, +0.040] | +0.054 [+0.025, +0.083] |
| B20 | 0.049 | 0.073 [0.058, 0.088] | −0.024 [−0.040, −0.008] | +0.154 [+0.137, +0.173] |
| C20 | 0.055 | 0.071 [0.056, 0.086] | −0.016 [−0.028, −0.003] | +0.103 [+0.080, +0.126] |

Ở A20, ngưỡng đổi ngược chiều theo họ: tuyến tính +0.144 [+0.112, +0.177] (số cạnh −3.0), RFF −0.037 [−0.059, −0.014] (số cạnh +17.1 [+11.7, +23.3]).

**Bảng 5. CDFM: chênh F1 B − A theo cách chọn ngưỡng** (thêm ở đính chính lần 2).

| Họ | NATIVE (tự chọn theo input) | FIXED (luôn 0.5) | FROZEN (ngưỡng của k0) | Đóng góp của việc đổi ngưỡng (NATIVE − FROZEN) |
|---|---|---|---|---|
| Gộp (80) | +0.036 [+0.015, +0.057] | +0.034 [+0.019, +0.050] | −0.012 [−0.026, +0.003] | +0.047 [+0.025, +0.071] |
| Tuyến tính (40) | +0.021 [−0.001, +0.042] | +0.037 [+0.021, +0.055] | +0.008 [−0.011, +0.028] | +0.013 [−0.010, +0.035] |
| RFF (40) | +0.050 [+0.016, +0.085] | +0.031 [+0.008, +0.056] | −0.031 [−0.051, −0.011] | +0.082 [+0.047, +0.117] |

**Phụ: logit trung bình** (nhạy với đuôi phân phối; xác suất đã kẹp ở [10⁻⁶, 1 − 10⁻⁶]). Với AVICI, điểm giảm khi có đệm: A20 cặp đúng −0.49, cặp sai −0.88; B20 −1.07 và −0.58. Với CDFM, điểm tăng gần đều ở cả hai loại cặp: A20 +0.61 và +0.57; B20 +0.48 và +0.46.

## 3. Đọc (suy luận từ mô tả, chưa kiểm)

1. **Review đúng, và còn rõ hơn.** Khi đổi A → B, AVICI và CDFM đều dự đoán ít cạnh hơn (−4.9 và −10.4). F1 đi ngược chiều vì điểm xuất phát khác nhau. Ở k0, AVICI dự đoán thiếu (17.5 so với 22.4 cạnh thật), còn CDFM dự đoán thừa (33.0 so với 22.4). Cùng một dịch chuyển "ít cạnh hơn" kéo AVICI ra xa số cạnh thật và kéo CDFM lại gần.
2. **Ở cùng số cạnh, chưa thể nói AVICI và CDFM cùng cơ chế.** Dữ liệu chỉ cho thấy hai model cùng chiều ở số cạnh.
   - **AVICI:** con số gộp gần 0 (+0.008) che hai chiều ngược nhau giữa các họ: tuyến tính +0.052, RFF −0.036. Vì vậy con số gộp **không** phải bằng chứng rằng thứ hạng không đổi.
   - **CDFM:** B kém A (−0.026), rõ ở RFF.
   - **FoundCause:** B tốt hơn A (+0.044).
3. **Phân rã theo mốc m0 (kế toán, không phải nguyên nhân).**
   - Phần thứ hạng lớn hơn phần số cạnh ở AVICI-A (0.050 trong 0.068) và ở CDFM-B (0.050 trong 0.049).
   - Phần số cạnh lớn hơn ở AVICI-B (0.077 trong 0.118) và CDFM-A (0.060 trong 0.085).
   - Nếu phép thử có đối chứng xác nhận hai trường hợp này, chúng sẽ cần hai cách sửa khác nhau. Phân rã này chưa đủ để kết luận điều đó.
4. **CDFM: ngưỡng có đóng góp rõ, nhưng không phải nguyên nhân duy nhất** (Bảng 5).
   - Ngưỡng NATIVE tăng khi có đệm, mạnh nhất ở B (+0.154). Điều này khớp với việc `suggest_threshold` tính đặc trưng trên toàn ma trận D×D.
   - *(Bổ sung 21/11 từ [P-N3 phần A](../n3_mechanism_pilot_2026-11-21/PN3_results_vi.md))* Chiều cụ thể là:
     - khi đệm có cấu trúc, xác suất trung bình **toàn ma trận giảm**, chủ yếu do điểm của các cặp chéo giảm;
     - trọng số của `mean` là âm (−8.56), nên ngưỡng tăng;
     - đó không phải "cạnh của khối đệm đẩy điểm lên".
   - So với ngưỡng của k0, việc đổi ngưỡng đóng góp +0.047 [+0.025, +0.071] F1 vào contrast B − A. Phần lớn đóng góp này nằm ở RFF (+0.082).
   - Dấu của contrast B − A còn phụ thuộc cách chọn ngưỡng:
     - FIXED 0.5: B vẫn tốt hơn A (+0.034), kể cả khi không có ngưỡng thích nghi;
     - FROZEN: gộp −0.012, CI chứa 0; riêng RFF −0.031, CI loại 0.
   - Vậy đây là tương tác giữa phân bố điểm và vị trí ngưỡng. Bản trước viết "chiều 'B đỡ hơn A' đến từ ngưỡng" và "với ngưỡng k0, B hại nhiều hơn A". Cả hai câu đều quá mức và đã bị bỏ.
5. **Họ dữ liệu quan trọng.**
   - Hiệu M1 của AVICI (B tệ hơn A) gần như hoàn toàn đến từ RFF (−0.072). Ở hệ tuyến tính, khi cùng số cạnh, B còn xếp hạng tốt hơn A (+0.052).
   - Ở CDFM, chênh lệch tập trung ở RFF: số cạnh −18.9, F1 +0.050.

   Review đúng ở điểm phải phân tích riêng hai họ.
6. **FoundCause.** Với B, output khối đích gần trở về k0 (H = 0.020, AUROC không đổi). Với A, model mất cả thứ hạng lẫn số cạnh. Kết quả này phù hợp với giả thuyết H3 (cột cô lập là trường hợp đặc biệt với FoundCause), nhưng chỉ trên 24 hệ.

## 4. Hệ quả cho P-N2

- **Biến đo chính:**
  - số cạnh dự đoán: Δ trung bình, kèm trung bình |Δ|, số cặp đổi trạng thái, và tách theo d_T hoặc chia cho d_T;
  - thứ hạng: F1 ở top-m0, AUROC, AP.

  F1 chỉ là biến phụ. Với CDFM, đọc F1 và số cạnh theo cả NATIVE, FROZEN và FIXED (0.5), cùng chính ngưỡng NATIVE. Phân tích riêng tuyến tính và RFF; con số gộp chỉ để tham chiếu.
- **Hướng dự đoán sinh từ dữ liệu này** (hậu nghiệm, phải kiểm trên seed mới, ghi vào luật P-N2 trước khi chạy):
  - AVICI: số cạnh khối đích giảm khi khối đệm có nhiều cạnh hơn. Thứ hạng đổi ngược chiều theo họ (tuyến tính tốt lên, RFF xấu đi).
  - CDFM: ngưỡng NATIVE tăng và số cạnh NATIVE giảm khi khối đệm có nhiều cạnh hơn. Thứ hạng (top-m0, AUROC, AP) xấu đi, rõ nhất ở RFF. Dấu của F1 phụ thuộc cách chọn ngưỡng, nên không dùng F1 làm giả thuyết chính.
  - FoundCause (bước sau): số cạnh tăng khi khối đệm có cạnh. Nếu H3 đúng, hại đi theo số nút đệm cô lập.

## 5. Giới hạn

- Hậu nghiệm, trên dữ liệu đã dùng cho phép kiểm; không kiểm soát familywise. Mọi chiều nêu ở §3 là giả thuyết.
- Phân rã ở §1 là kế toán theo mốc m0. Đổi mốc (ví dụ số cạnh thật) sẽ đổi giá trị hai phần, và phân rã không tách nguyên nhân.
- AUROC chỉ tính trên các cặp trong khối đích. Logit trung bình nhạy với đuôi.
- FoundCause chỉ có 24 hệ (12 mỗi họ).

## 6. Nhật ký đính chính

| Lần | Chỗ | Bản trước | Sửa thành | Căn cứ |
|---|---|---|---|---|
| 2 (20/11) | §3 mục 4 | "Chiều 'B đỡ hơn A' của CDFM ở NATIVE đến từ ngưỡng"; "với ngưỡng k0, B hại CDFM nhiều hơn A (0.073 so với 0.062)" | Ngưỡng đóng góp +0.047 nhưng không phải nguyên nhân duy nhất: ở FIXED 0.5, B vẫn tốt hơn; ở FROZEN, hiệu gộp −0.012 có CI chứa 0. Thêm Bảng 5 | Review thứ hai; tính lại từ `held_cdfm.json` |
| 2 | §1, §3 mục 3, §5 | "Hai loại hại xuất hiện ở những ô khác nhau ... dẫn tới hai cách sửa khác nhau" | Phân rã kế toán theo mốc m0, không phải hai nguyên nhân độc lập. FROZEN không phải phép đo thuần thứ hạng | Review thứ hai |
| 2 | §3 mục 2 | "với AVICI, B ≈ A (+0.008)" | Con số gộp che hai chiều ngược nhau (tuyến tính +0.052, RFF −0.036); không phải bằng chứng thứ hạng không đổi | Review thứ hai; Bảng 3 |
| 2 | §2, §4 | (không có) | Thêm trung bình \|Δ số cạnh\|. Biến đo P-N2 gồm \|Δ\|, số cặp đổi trạng thái, tách theo d_T | Review thứ hai (CDFM tuyến tính: Δ −1.9, \|Δ\| 10.5) |
| 3 (21/11) | §3 mục 4 | Bản đầu (`9dbb072`) viết "các cạnh riêng của khối đệm B đẩy phân phối điểm lên"; câu này đã bỏ ở lần 2 | Chiều ngược lại. Khi đệm có cấu trúc, xác suất trung bình ở khối đệm (0.546 → 0.405) và khối chéo (0.362 → 0.189) giảm, nên trung bình toàn ma trận giảm; trọng số âm của `mean` làm ngưỡng tăng | P-N3 phần A, EXP2 RFF |
