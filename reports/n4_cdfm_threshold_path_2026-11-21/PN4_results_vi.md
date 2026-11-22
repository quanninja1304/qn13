# P-N4: kết quả kiểm chứng đường ảnh hưởng qua bộ chọn ngưỡng của CDFM (21–22/11/2026)

> **Luật:** [P-N4 v1](PN4_rules_vi.md), khóa ở commit `05b6945` (push lúc 2026-11-21T13:52:57Z). Code đóng băng cùng các phụ thuộc ở `159479d` (push lúc 16:55:18Z), trước khi sinh input P-N4 nào.
> **Chạy:** 80 hệ (20 mỗi ô RFF) × 5 input = 400 lần chạy CDFM, từ 16:56:24 đến 17:52:13 UTC ngày 21/11 (56 phút).
> **Đọc:** bằng `analyze4.py` đã đóng băng, sau khi kiểm hoàn tất đạt (§1).
> **Nhãn:**
>
> - [Verified-run] cho số liệu.
> - Nhãn CONFIRMED / NOT_CONFIRMED chỉ áp cho **tám** giả thuyết, qua Holm ở mức familywise 0.05.
> - Mọi phần khác (§3–§4) là **mô tả**, không thuộc bộ Holm.
> - Phạm vi: CDFM, họ RFF, đồ thị ER, n = 500, d_T ∈ {10, 20}, e_T ∈ {1, 2}, k ∈ {20, 40}.

## 1. Hoàn tất và toàn vẹn (đạt hết)

Script đóng băng `completeness4.py` (luật §7) cho kết quả ([`checks/pn4_completeness.json`](checks/pn4_completeness.json)):

- **Đủ output:** 400 output CDFM, 400 dòng log, 0 job lỗi.
- **Mã băm input:** 0 lệch khi sinh lại toàn bộ 400 input. Khối đích trùng từng bit giữa năm input của mọi hệ.
- **Bộ chọn ngưỡng chép lại:** tái tạo mọi ngưỡng đã lưu, sai lệch tuyệt đối tối đa 4.4e-16.
- **Cổng đóng băng:** `pn4_start` và `pn4_end` đều `ok: true`, cùng commit `159479d`, cùng mã băm `SHA256SUMS` và cùng mã băm phụ thuộc ([`checks/pn4_run_header.json`](checks/pn4_run_header.json)).
- **Kiểm phụ của code đọc:** số cạnh NATIVE tính từ ma trận kề của CDFM khớp quy tắc m(A, τ) ở mọi hệ và mọi k.

## 2. Tám giả thuyết: cả tám CONFIRMED

Kiểm một phía trên trung bình cân bằng theo ô, sai số chuẩn phân tầng theo ô, df Welch–Satterthwaite. p của giả thuyết tổng hợp là p lớn nhất của các thành phần; Holm 0.05 trên cả tám (luật §4). Số liệu đầy đủ ở [`checks/pn4_reading_summary.json`](checks/pn4_reading_summary.json).

| ID | Thành phần | θ̂ [CI 95%] | t (df) | p một phía | p của giả thuyết | Hạng, ngưỡng Holm | Nhãn | Cỡ |
|---|---|---|---|---|---|---|---|---|
| N4-a(20) | D1 (điểm khối chéo) | −0.190 [−0.200, −0.181] | 40.25 (56.7) | 1.1e-43 | 1.1e-43 | 2, 0.0071 | **CONFIRMED** | LARGE |
| N4-b(20) | D2 (ngưỡng NATIVE) | +0.193 [+0.180, +0.205] | 31.19 (48.1) | 7.2e-34 | 7.2e-34 | 4, 0.0100 | **CONFIRMED** | LARGE |
| N4-x(20) | D3a (ngưỡng, chỉ đổi khối chéo) | +0.126 [+0.120, +0.132] | 40.85 (63.4) | 1.5e-47 | 1.3e-12 | 7, 0.0250 | **CONFIRMED** | LARGE |
| | D3b (số cạnh đích, chỉ đổi khối chéo) | −18.63 [−22.31, −14.94] | 10.25 (36.7) | 1.3e-12 | | | | LARGE |
| N4-c(20) | T, so với −1.5 | −19.24 [−22.01, −16.46] | 12.85 (48.6) | 1.5e-17 | 5.6e-12 | 8, 0.0500 | **CONFIRMED** | LARGE |
| | T + S | −19.36 [−23.52, −15.20] | 9.41 (39.9) | 5.6e-12 | | | | LARGE |
| | T − S | −19.11 [−22.84, −15.39] | 10.36 (41.2) | 2.5e-13 | | | | LARGE |
| N4-a(40) | D1 | −0.161 [−0.172, −0.151] | 30.73 (54.2) | 2.7e-36 | 2.7e-36 | 3, 0.0083 | **CONFIRMED** | LARGE |
| N4-b(40) | D2 | +0.227 [+0.219, +0.234] | 57.68 (55.1) | 3.2e-51 | 3.2e-51 | 1, 0.0063 | **CONFIRMED** | LARGE |
| N4-x(40) | D3a | +0.089 [+0.084, +0.094] | 34.71 (61.3) | 2.6e-42 | 4.3e-13 | 6, 0.0167 | **CONFIRMED** | LARGE |
| | D3b | −16.10 [−18.95, −13.25] | 11.51 (31.4) | 4.3e-13 | | | | LARGE |
| N4-c(40) | T, so với −1.5 | −26.04 [−29.47, −22.61] | 14.60 (30.4) | 1.4e-15 | 5.6e-14 | 5, 0.0125 | **CONFIRMED** | LARGE |
| | T + S | −20.73 [−24.24, −17.21] | 11.99 (33.6) | 5.6e-14 | | | | LARGE |
| | T − S | −31.35 [−36.55, −26.15] | 12.14 (44.5) | 5.1e-16 | | | | LARGE |

- Không thành phần nào DEGENERATE, và không ước lượng nào ngược phía dự đoán.
- **Kiểm tra độ nhạy** (không phải căn cứ xác nhận): CI bootstrap phân tầng của cả 14 thành phần đều nằm hẳn về phía dự đoán so với mốc. Ví dụ, T ở k = 20 có [−22.03, −16.84], và D3b ở k = 40 có [−18.96, −13.54].
- Nhãn cỡ theo biên thực tiễn của luật §5 (1.5 cạnh; 0.03 cho ngưỡng và cho xác suất trung bình): cả 14 thành phần đều LARGE. Đây là phân loại theo CI và biên đã chọn, không phải 14 kết luận riêng đã kiểm soát familywise. Bộ Holm chỉ gồm tám giả thuyết.

**Câu được viết** (luật §9), cho cả k = 20 và k = 40:

- Đường ảnh hưởng từ khối chéo, qua bộ chọn ngưỡng, tới quyết định trên khối đích được xác nhận: N4-a, N4-b và N4-x đều CONFIRMED.
- Theo phép phân rã lấy ngưỡng e = 0 làm mốc, phần do ngưỡng chiếm phần lớn mức đổi trung bình số cạnh NATIVE: N4-c CONFIRMED. Câu này nói về trung bình, không nói về từng hệ (§3.1).

## 3. Mô tả (không thuộc bộ Holm)

### 3.1 Theo từng hệ

| | k = 20 | k = 40 |
|---|---|---|
| Tỉ lệ hệ có T_i < −\|S_i\| | 81% | 89% |
| Tỉ lệ hệ có D3b_i < 0 | 99% | 93% |
| Tỉ lệ hệ có D2_i > 0 | 100% | 100% |

Phần do ngưỡng lớn hơn phần do điểm ở đa số hệ, nhưng không ở mọi hệ.

### 3.2 So với các pha trước, ở k = 20

| Biến đo | EXP2 (20 hệ) | HELD2 (60 hệ) | P-N4 (80 hệ) |
|---|---|---|---|
| D1 | −0.173 | −0.180 | −0.190 |
| D2 | +0.159 | +0.175 | +0.193 |
| D3a | +0.108 | +0.115 | +0.126 |
| D3b | −13.75 | −16.55 | −18.63 |
| S | +2.00 | +2.30 | −0.13 [−2.91, +2.66] |
| T | −17.25 | −17.87 | −19.24 |
| Shapley khối chéo / khối đệm | 60% / 41% | — | 57% / 44% |

Cột EXP2 và HELD2 là mô tả, tính lại trên output đã đóng băng ([`design/pn4_design_inputs.json`](design/pn4_design_inputs.json); P-N3 phần A). Trên seed mới, ước lượng điểm của D1, D2, D3a, D3b và T có cùng chiều, với cỡ bằng hoặc lớn hơn ở EXP2 và HELD2. Đây chỉ là so sánh ước lượng điểm; chưa có phép kiểm so sánh cỡ hiệu ứng giữa các pha. Phần do điểm ở k = 20 lần này gần 0, với CI chứa 0.

### 3.3 Nhóm nào của ma trận làm ngưỡng tăng

| | k = 20 | k = 40 |
|---|---|---|
| Δℓ (logit ngưỡng) | +1.02 [+0.96, +1.08] | +1.26 [+1.21, +1.30] |
| Shapley khối đích | −0.006 (−1%) | +0.044 (3.5%) |
| Shapley khối đệm | +0.448 (44%) | +0.820 (65%) |
| Shapley khối chéo | +0.579 (57%) | +0.392 (31%) |

- Ở k = 40, **khối đệm** đóng góp nhiều nhất, không còn là khối chéo. Điều này khớp với tỉ lệ số cặp chéo/đệm 2·d_T/(k − 1), tức 0.51 hoặc 1.03 ở k = 40. Đây là lý do luật không khóa "khối chéo luôn đứng đầu".
- Cả hai nhóm tác động chủ yếu qua đặc trưng `mean`. Ở khối chéo, phần qua `mean` là +0.79 (k = 20) và +0.54 (k = 40); ở khối đệm là +0.47 và +0.88. Khối đệm còn góp qua `knee_T` (+0.25 và +0.37) và `std` (−0.16 và −0.27).
- Tương tác nhỏ. Lớn nhất là tương tác đích × đệm ở k = 40 (−0.078).

### 3.4 Xác suất trung bình theo khối

| Khối | k = 20: e = 0 → e_T | Đổi [CI 95%] | k = 40: e = 0 → e_T | Đổi [CI 95%] |
|---|---|---|---|---|
| Đích | 0.416 → 0.459 | +0.043 [+0.031, +0.056] | 0.426 → 0.525 | +0.099 [+0.086, +0.113] |
| Chéo (đều là không-cạnh) | 0.373 → 0.183 | −0.190 [−0.200, −0.181] | 0.364 → 0.203 | −0.161 [−0.172, −0.151] |
| Đệm, cặp không-cạnh | 0.553 → 0.344 | −0.210 [−0.225, −0.194] | 0.529 → 0.312 | −0.218 [−0.228, −0.207] |
| Đệm, cặp có cạnh ở e_T | 0.554 → 0.639 | +0.085 [+0.068, +0.102] | 0.529 → 0.636 | +0.107 [+0.096, +0.118] |
| Toàn ma trận | 0.435 → 0.295 | −0.140 [−0.148, −0.132] | 0.453 → 0.294 | −0.159 [−0.167, −0.151] |

- Cặp có cạnh và cặp không-cạnh của khối đệm được tách theo đồ thị đệm ở e_T và so trên cùng các cặp ở e = 0 (luật §5).
- **Điều này làm rõ giới hạn đã ghi ở C6.** Trung bình gộp của khối đệm trước đây (0.546 → 0.405 ở EXP2) trộn hai chiều ngược nhau. Khi tách ra, các cặp không-cạnh của khối đệm cũng giảm điểm mạnh, như khối chéo, còn cạnh thật của khối đệm tăng điểm.
- Khi đệm độc lập (e = 0), các cặp giữa hai cột đệm có xác suất trung bình khoảng 0.53–0.55, cao hơn trung bình của khối đích (khoảng 0.42), dù tất cả đều là không-cạnh.

### 3.5 Số cạnh đích dưới ma trận lai (đếm trên điểm đích ở e = 0)

| Ma trận lai (đích, đệm, chéo) | k = 20 | k = 40 |
|---|---|---|
| (0, 0, 0): toàn bộ ở e = 0 | 48.0 | 52.4 |
| (0, 0, 1): chỉ đổi khối chéo | 29.4 | 36.3 |
| (0, 1, 0): chỉ đổi khối đệm | 34.4 | 28.7 |
| (0, 1, 1): đổi khối đệm và khối chéo | 22.6 | 21.4 |
| (1, 1, 1): ngưỡng của e_T | 23.3 | 22.1 |

Chỉ đổi khối đệm làm ngưỡng tăng +0.108 [+0.096, +0.120] ở k = 20 và +0.180 [+0.172, +0.188] ở k = 40; số cạnh đích giảm 13.6 và 23.7.

### 3.6 Phân rã với mốc khác (ngưỡng ở e_T)

| | k = 20 | k = 40 |
|---|---|---|
| S′ (phần do điểm) | +5.38 [+3.95, +6.80] | +9.56 [+7.71, +11.42] |
| T′ (phần do ngưỡng) | −24.74 [−29.12, −20.36] | −30.29 [−34.14, −26.44] |

- Đổi mốc làm thay đổi hai phần. Ở k = 20, phần do điểm là −0.13 với mốc e = 0, nhưng +5.38 với mốc e_T.
- Với cả hai mốc, độ lớn trung bình của phần do ngưỡng vượt độ lớn của phần do điểm. Điều này chỉ là mô tả; phép kiểm (c) chỉ dùng mốc e = 0.

### 3.7 Chất lượng và so sánh hai k

- **F1 skeleton NATIVE:** k0 0.677. Ở k = 20: 0.583 (e = 0) và 0.641 (e_T). Ở k = 40: 0.551 và 0.599.
- **Mức hại do đệm độc lập** H = F1(k0) − F1(e = 0): 0.093 [0.075, 0.111] ở k = 20 và 0.125 [0.104, 0.147] ở k = 40.
- **So sánh hai k** (k = 40 − k = 20, ghép cặp theo hệ). Chỉ là mô tả, vì phép so nằm ngoài bộ giả thuyết chính:
  - D2: +0.034 [+0.023, +0.045]: ngưỡng tăng nhiều hơn;
  - D3a: −0.037 [−0.043, −0.032]: hiệu ứng của riêng khối chéo lên ngưỡng nhỏ hơn;
  - S: +5.4 [+2.4, +8.5];
  - T: −6.8 [−9.3, −4.3];
  - T + S: −1.4 [−4.2, +1.5]. Chưa thấy chênh lệch rõ về mức đổi ròng số cạnh; kết quả này chưa chứng minh tương đương.
- **Theo d_T:** mức đổi số cạnh lớn hơn nhiều ở d_T = 20, nơi có nhiều cặp đích hơn. Ví dụ, D3b ở k = 20 là −7.1 (d_T = 10) và −30.2 (d_T = 20). Ở cả hai k, cả bốn ô đều có D3b và T âm.

## 4. Không được nói

- "Cơ chế bên trong CDFM đã được xác lập." P-N4 phân tích một hàm đã biết trên output của model. Nó không giải thích vì sao CDFM cho các cặp không-cạnh điểm thấp hơn khi khối đệm có cấu trúc.
- "Ngưỡng chi phối ở từng hệ." Tỉ lệ hệ là 81% và 89%.
- "Khối chéo luôn đóng góp nhiều nhất." Ở k = 40, khối đệm đóng góp nhiều nhất.
- "Phần do điểm bằng 0." Ở k = 20, CI của S chứa 0 nhưng rộng; với mốc e_T thì S′ = +5.38. Ở k = 40, S dương.
- Kết quả khái quát được cho k, n hay họ đồ thị khác, hay cho CDFM trên dữ liệu thật.
- Bất kỳ điều gì về AVICI hay FoundCause.

## 5. Ý nghĩa cho bài và bước tiếp (để user quyết)

- **Gap 1 đã có kết quả xác nhận.** Đường ảnh hưởng của CDFM được kiểm trên seed mới theo luật khóa trước, ở k = 20 (lặp lại) và k = 40 (mở rộng). Chuỗi gồm: điểm của các cặp không-cạnh ngoài khối đích giảm khi đệm có cấu trúc; trung bình toàn ma trận giảm; ngưỡng tăng; cạnh đích mất đi khi điểm đích giữ nguyên.
- **Hệ quả cho bản thảo:**
  - §6.1 và §6.3 có thể chuyển từ "exploratory, dự kiến" sang kết quả xác nhận của P-N4;
  - giới hạn của C6 được làm rõ: cặp không-cạnh của khối đệm cũng giảm điểm;
  - vị trí đứng đầu giữa khối chéo và khối đệm phụ thuộc k, nên bài cần viết đúng như vậy.
- **Còn mở:**
  - vì sao CDFM sinh ra các thay đổi điểm đó (câu hỏi bên trong model);
  - cơ chế của AVICI;
  - gap 2 (dữ liệu thật), gap 3 (so sánh cách sửa), gap 4 (thêm model).
- **Bước tiếp theo thứ tự đã chốt:** gap 2, tức kiểm tính nhất quán trên dữ liệu thật. Cần user chọn và duyệt việc tải bộ dữ liệu.

## 6. Đính chính diễn đạt (22/11, sau review của user)

Số liệu và tám nhãn CONFIRMED không đổi. User đã tính lại các contrast chính từ output thô, cùng CI, p-value và Holm, và kết quả khớp toàn bộ. User cũng xác nhận snapshot và 44 file phụ thuộc khớp mã băm.

| # | Chỗ | Bản trước (`70eb7c5`) | Sửa thành |
|---|---|---|---|
| 1 | §3.7, T + S giữa hai k | "mức đổi ròng số cạnh tương đương" | Chưa thấy chênh lệch rõ; kết quả này chưa chứng minh tương đương |
| 2 | §3.2 | "hiệu ứng có cùng chiều và cỡ tương đương hoặc lớn hơn; không thấy thu nhỏ" | Chỉ nói về ước lượng điểm của D1, D2, D3a, D3b và T; chưa có phép kiểm so sánh cỡ hiệu ứng giữa các pha |
| 3 | §2 | "cả 14 thành phần đều LARGE" | Đây là phân loại theo CI và biên, không phải 14 kết luận riêng đã kiểm soát familywise |
