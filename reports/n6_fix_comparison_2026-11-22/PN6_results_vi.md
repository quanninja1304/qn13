# P-N6: kết quả so sánh cách sửa, gap 3 (22/11/2026)

> **Luật:** [P-N6 v1](PN6_rules_vi.md), khóa ở commit `678f55f` (push lúc 2026-11-22T09:32:14Z). Code đóng băng cùng các phụ thuộc và hai mức α ở `98266e7` (push lúc 10:20:14Z). Lúc đó chưa sinh input held-out nào, và chưa chạy R-L hay R-H của P-N6 trên hai bảng thật. Output plain trên hai bảng đã có từ P-N5.
> **Chạy:** 2 930 job, gồm 442 lần tính p-value HSIC, và cho mỗi model AVICI và CDFM: 360 job plain, 442 job R-L, 442 job R-H. Thời gian: 10:21:23 đến 12:40:03 UTC ngày 22/11 (2 giờ 18 phút 40 giây).
> **Đọc:** bằng `analyze6.py` đã đóng băng, sau khi kiểm hoàn tất đạt (§1).
> **Nhãn:**
>
> - [Verified-run] cho số liệu.
> - CONFIRMED / NOT_CONFIRMED chỉ áp cho **sáu** giả thuyết, qua Holm ở mức familywise 0.05.
> - §3–§8 là **mô tả** theo luật §6, không thuộc bộ Holm. §9 là **hậu nghiệm ngoài luật** (POST-HOC), không phải căn cứ xác nhận.
>
> **Phạm vi:**
>
> - 120 hệ tổng hợp held-out mới (seed base 480000), 15 hệ mỗi ô. Có 8 ô: d_T ∈ {10, 20}, e_T ∈ {1, 2}, tuyến tính và RFF; đồ thị ER; n = 500;
> - k = 20 cột thêm vào, độc lập với khối đích theo thiết kế: A20 là đệm Gauss, S20 là đệm có cấu trúc cùng họ cơ chế với khối đích;
> - AVICI `scm-v0` và CDFM; α_L = 10⁻⁴ và α_H = 0.01, chọn trên DEV6 bằng J, không dùng output model;
> - hai bảng thật của P-N5, chỉ mô tả độ đổi. Không có thước đo chất lượng và không có câu nào về độ chính xác.

## 0. Tóm tắt

- **5/6 CONFIRMED.**
  - R-L không làm giảm F1 skeleton trung bình quá biên 0.03 so với output ban đầu, cả ở k0 lẫn khi có 20 cột Gauss. Điều này được xác nhận ở AVICI (tuyến tính và RFF) và ở CDFM trên hệ RFF.
  - Ở đệm có cấu trúc, output của R-L lệch khỏi output ban đầu của CDFM ít hơn FROZEN, ở cả hai họ.
- **P6-1C-lin NOT_CONFIRMED** (CDFM, tuyến tính). Đây là ô mà hồ sơ power đã báo trước là yếu (0.21).
  - Ước lượng điểm nằm trong biên: Q0 = −0.024. Nhưng cận dưới của CI vượt biên: [−0.042, −0.005].
  - Không xác nhận được không có nghĩa là đã chứng minh tổn thất vượt biên.
- **R-L không giữ nguyên output ban đầu.** Ngay ở k0, nó đã cho một output khác plain: φ(k0) từ 4 đến 8 cặp ở 3 trong 4 nhóm model × họ. Khi thêm đệm, R-L giữ được output của chính nó: σ = 0 ở mọi input không có trộn đích với đệm, đã kiểm từng bit.
- **Chỗ hỏng còn lại của R-L là gộp nhầm.**
  - A20: 11/120 hệ có gộp, mỗi hệ đúng 1 cột.
  - S20: 12/120 hệ có gộp, nhưng mỗi hệ kéo theo 15–20 cột, tức gần như cả khối đệm.
  - Số cặp chéo bị bác bỏ cao hơn cận trên danh nghĩa của kỳ vọng, tức cận đúng khi p-value hợp lệ (§9.4).
- **R-H** trộn ít hơn R-L nhưng tách thêm cạnh đích khi có đệm. Tỉ lệ hệ có σ > 0 của R-H cao hơn R-L ở cả 8 nhóm model × họ × input.
- **Hậu nghiệm:** với CDFM tuyến tính, phần lớn giá ở k0 nằm bên trong các thành phần, không ở cặp bị tách.
  - Kế toán F1 (user tính, agent tính lại): khoảng −0.008 ở cặp bị tách và −0.015 đến −0.016 trong thành phần, tùy thứ tự thay thế.
  - Lấy τ(k0) làm mốc, phần tăng cạnh sai trong thành phần trùng với việc CDFM chọn ngưỡng thấp hơn trên thành phần nhỏ.
  - Đây là kế toán, chưa xác định nguyên nhân. Nó không cho thấy phép kiểm kết hợp ở luật §12 chỉ xử lý phần nhỏ của vấn đề, vì đổi phân hoạch sẽ đổi cả input, điểm và ngưỡng bên trong thành phần.
  - Chưa làm phép kiểm đó là để giữ phạm vi bài, không phải vì ứng viên đã bị bác bỏ.

## 1. Hoàn tất và toàn vẹn (đạt hết)

Script đóng băng `completeness6.py` (luật §7) cho `ok: true`, không có vấn đề nào ([`checks/pn6_completeness.json`](checks/pn6_completeness.json)):

- **Trạng thái job:** 2 930/2 930 job có đúng một bản ghi `ok`. Không có `error` hay `budget_stop`, và không có bản ghi nào ngoài danh sách job.
- **Input:**
  - mã băm input của mọi output và mọi p-value đã lưu khớp input sinh lại;
  - khối đích trùng từng bit giữa các input của mỗi hệ;
  - 82 input bảng thật khớp mã băm trong `checks/inputs5.json` của P-N5.
- **Cổng đóng băng** ([`checks/pn6_run_header.json`](checks/pn6_run_header.json)):
  - `pn6_start` và `pn6_end` đều `ok: true`, cùng commit `98266e7`, cùng mã băm `SHA256SUMS` (`55dd00d0…`) và cùng mã băm phụ thuộc (`485005e1…`);
  - dữ liệu khớp manifest ở cả đầu lẫn cuối lượt;
  - một lần gọi `precheck` trước lượt chạy cũng `ok`.
- **Quyết định của R-L giữa các cặp đích** trùng chính xác với k0 ở **320/320** input có đệm: 240 input tổng hợp và 80 input bảng thật.
- **Phát biểu có điều kiện của R-L** (luật §1, §7): output trên khối đích trùng R-L ở k0 từng bit, ở **572/572** trường hợp (model × input) thỏa điều kiện.
  - 34 input có đệm nằm ngoài điều kiện vì có ít nhất một thành phần trộn đích với đệm: 23 input tổng hợp và 11 input bảng thật.
  - Hai model có cùng 34 input này, vì sàng lọc không phụ thuộc model.
- **Ngân sách:** 8 320 s (2.31 giờ) tính từ mốc `pn6_start`, dưới mốc 3 giờ. G9 đã ước tính 2.6 giờ.
- **Bộ nhớ đỉnh** (đỉnh tích lũy của từng tiến trình):
  - AVICI: plain 1.27 GB, R-L 2.01 GB, R-H 1.78 GB. CDFM: 0.63–0.64 GB.
  - Đỉnh của AVICI ở R-L **vượt số đo DEV6** (1.44 GB). Bộ nhớ không phải điều kiện của cổng, lượt chạy không lỗi, và mức này không làm mất tính hợp lệ của lượt chạy.
  - Đỉnh rơi vào input S20 của hệ `PN6-c6-r5`, nơi cả 40 cột thành một thành phần.
  - Suy luận chưa kiểm: đỉnh tăng theo bậc vì JAX biên dịch lại cho mỗi cỡ thành phần mới.
- **Kiểm lại độc lập** (agent; [`posthoc/recheck_pn6.py`](posthoc/recheck_pn6.py), output ở [`posthoc/recheck_output.txt`](posthoc/recheck_output.txt)):
  - **Cách làm:**
    - script không import `measures6.py`, `stats6.py`, `analyze6.py`, `screen.py` hay `metrics.py` của P-N1;
    - phân hoạch được dựng lại từ p-value đã lưu và hai mức α đã ghi;
    - chỉ dùng bộ sinh của P-N1 để lấy đồ thị đích thật, và bộ chọn ngưỡng của P-N4 để định nghĩa đối chứng LOCAL.
  - **Kết quả:** khớp bản đọc.
    - Ước lượng điểm lệch 0; CI lệch tối đa 3.6e−15; p lệch tối đa 8.7e−19.
    - Nhãn và hạng Holm, nhãn cỡ, tỉ lệ σ > 0, |Δm| lớn nhất, chỉ số sàng lọc và số bảng thật: không có chỗ nào lệch.
    - Phân hoạch dựng lại trùng phân hoạch đã lưu ở mọi input.

## 2. Sáu giả thuyết: 5 CONFIRMED, 1 NOT_CONFIRMED

Phép kiểm theo luật §5:

- t phân tầng theo ô: w_c = 1/4 trong một họ, SE² = Σ w_c² s_c² / n_c, df Welch–Satterthwaite;
- P6-1: t = (θ̂ + 0.03)/SE cho từng thành phần, và p của giả thuyết là p lớn hơn của hai thành phần;
- Holm 0.05 trên sáu p-value.

Số liệu đầy đủ ở [`checks/pn6_reading.json`](checks/pn6_reading.json).

| ID | Model, họ | Thành phần | Ước lượng [CI 95%] | t (df) | p một phía | p giả thuyết | Hạng, ngưỡng Holm | Nhãn |
|---|---|---|---|---|---|---|---|---|
| P6-1A-lin | AVICI, tuyến tính | Q0 | +0.0198 [−0.0049, +0.0446] | 4.11 (30.6) | 1.36e−4 | 1.42e−4 | 4, 0.0167 | **CONFIRMED** |
| | | Q(A20) | +0.0197 [−0.0051, +0.0444] | 4.10 (30.6) | 1.42e−4 | | | |
| P6-1A-rff | AVICI, RFF | Q0 | −0.0069 [−0.0172, +0.0035] | 4.57 (30.7) | 3.78e−5 | 4.00e−5 | 3, 0.0125 | **CONFIRMED** |
| | | Q(A20) | −0.0069 [−0.0173, +0.0035] | 4.53 (31.3) | 4.00e−5 | | | |
| P6-1C-lin | CDFM, tuyến tính | Q0 | −0.0235 [−0.0423, −0.0048] | 0.69 (43.8) | 0.246 | 0.246 | 6, 0.0500 | NOT_CONFIRMED |
| | | Q(A20) | −0.0221 [−0.0413, −0.0028] | 0.83 (44.7) | 0.205 | | | |
| P6-1C-rff | CDFM, RFF | Q0 | −0.0014 [−0.0195, +0.0168] | 3.25 (26.9) | 1.56e−3 | 2.82e−3 | 5, 0.0250 | **CONFIRMED** |
| | | Q(A20) | −0.0029 [−0.0214, +0.0156] | 3.01 (26.3) | 2.82e−3 | | | |
| P6-2C-lin | CDFM, tuyến tính | φ_FROZEN(S20) − φ_R-L(S20) | +8.73 [+5.93, +11.54] | 6.48 (20.8) | 1.08e−6 | 1.08e−6 | 2, 0.0100 | **CONFIRMED** |
| P6-2C-rff | CDFM, RFF | như trên | +10.33 [+8.14, +12.53] | 9.76 (22.5) | 7.55e−10 | 7.55e−10 | 1, 0.0083 | **CONFIRMED** |

- **Không giả thuyết nào DEGENERATE.**
- **Cách đọc:** CI là CI 95% hai phía, chỉ để mô tả. Holm không bảo vệ CI hay nhãn cỡ của các giả thuyết đồng thời. CONFIRMED ở P6-2 chỉ xác nhận dấu.
- **P6-2:** φ của FROZEN và R-L ở S20 là 18.00 và 9.27 cặp (tuyến tính), 17.32 và 6.98 cặp (RFF). Phép so tính cả giá ở k0 của R-L, nên nghiêng về phía bất lợi cho R-L (luật §5).
- **P6-1C-lin:**
  - ước lượng điểm của cả hai thành phần nằm trong biên (−0.0235 và −0.0221 > −0.03), nhưng cận dưới CI vượt biên (−0.042 và −0.041);
  - đây đúng là ô mà hồ sơ power đã báo trước (luật §10): power khoảng 0.21 ở mức Holm chặt nhất nếu R-L có giá như R-B;
  - không xác nhận được không chứng minh R-L gây tổn thất vượt biên;
  - **mô tả:** CI của Q0 nằm hẳn dưới 0 (dấu NEG). Ngay ở k0, F1 của CDFM trên hệ tuyến tính dưới R-L thấp hơn output ban đầu, ước lượng 0.024. §9.1–§9.2 xem phần này đến từ đâu.

**Câu được viết** (luật §9):

- Trên 120 hệ tổng hợp mới, R-L không làm giảm F1 skeleton trung bình quá 0.03 so với output ban đầu, ở k0 cũng như khi có 20 cột Gauss. Điều này đúng với AVICI trên hệ tuyến tính và RFF, và với CDFM trên hệ RFF. Với CDFM trên hệ tuyến tính, điều này chưa được xác nhận.
- Mức giữ nguyên cấu trúc của R-L, lần lượt cho AVICI tuyến tính, AVICI RFF, CDFM tuyến tính, CDFM RFF:
  - φ(k0) = 4.03, 0.85, 8.37, 4.78 cặp;
  - σ(A20) = 0.07, 0.03, 0.18, 0.72;
  - σ(S20) = 1.45, 0.77, 1.97, 2.90 (§3).
- Ở đệm có cấu trúc, output của R-L lệch khỏi output ban đầu của CDFM ít hơn FROZEN: 9.27 so với 18.00 cặp ở hệ tuyến tính, 6.98 so với 17.32 cặp ở hệ RFF. Phép so này đã tính cả giá ở k0 của R-L.

## 3. Mức giữ nguyên cấu trúc: φ và σ (mô tả)

φ so f(c) với **plain ở k0**; σ so f(c) với **chính f ở k0**. Trung bình theo t phân tầng, kèm [CI 95%].

| Model, họ | Cách | φ(k0) | φ(A20) | φ(S20) | σ(A20) | σ(S20) |
|---|---|---|---|---|---|---|
| AVICI, tuyến tính | plain | 0 | 10.75 [9.34, 12.16] | 11.28 [9.64, 12.93] | = φ | = φ |
| | R-L | 4.03 [2.81, 5.25] | 4.10 [2.88, 5.32] | 4.85 [3.48, 6.22] | 0.07 [−0.08, 0.21] | 1.45 [−0.04, 2.94] |
| | R-H | 4.08 [2.81, 5.36] | 4.75 [3.35, 6.15] | 5.05 [3.51, 6.59] | 0.83 [0.03, 1.64] | 1.67 [0.14, 3.19] |
| AVICI, RFF | plain | 0 | 2.33 [1.85, 2.82] | 5.23 [4.41, 6.05] | = φ | = φ |
| | R-L | 0.85 [0.53, 1.17] | 0.88 [0.56, 1.21] | 1.55 [0.81, 2.29] | 0.03 [−0.02, 0.08] | 0.77 [0.05, 1.49] |
| | R-H | 0.82 [0.50, 1.13] | 0.87 [0.56, 1.18] | 1.22 [0.67, 1.77] | 0.15 [0.01, 0.29] | 0.57 [0.06, 1.08] |
| CDFM, tuyến tính | plain | 0 | 19.03 [15.50, 22.57] | 17.72 [15.35, 20.08] | = φ | = φ |
| | R-L | 8.37 [6.18, 10.55] | 8.32 [6.14, 10.50] | 9.27 [6.98, 11.55] | 0.18 [−0.11, 0.48] | 1.97 [−0.34, 4.27] |
| | R-H | 8.38 [6.19, 10.58] | 8.95 [6.72, 11.18] | 9.20 [6.78, 11.62] | 0.73 [0.05, 1.42] | 1.78 [−0.35, 3.91] |
| CDFM, RFF | plain | 0 | 20.63 [18.05, 23.22] | 14.03 [11.91, 16.16] | = φ | = φ |
| | R-L | 4.78 [3.39, 6.17] | 4.83 [3.49, 6.18] | 6.98 [3.97, 10.00] | 0.72 [0.16, 1.28] | 2.90 [0.35, 5.45] |
| | R-H | 4.83 [3.44, 6.23] | 5.48 [4.08, 6.89] | 6.40 [3.74, 9.06] | 1.42 [0.41, 2.42] | 2.70 [0.51, 4.89] |

**Tỉ lệ hệ có σ > 0** (k/60, CI 95% Clopper–Pearson):

| Model, họ | plain A20 | plain S20 | R-L A20 | R-L S20 | R-H A20 | R-H S20 |
|---|---|---|---|---|---|---|
| AVICI, tuyến tính | 60 [0.94, 1] | 60 [0.94, 1] | 1 [0.000, 0.089] | 5 [0.028, 0.184] | 7 [0.048, 0.226] | 8 [0.059, 0.246] |
| AVICI, RFF | 46 [0.64, 0.87] | 53 [0.77, 0.95] | 2 [0.004, 0.115] | 5 [0.028, 0.184] | 5 [0.028, 0.184] | 8 [0.059, 0.246] |
| CDFM, tuyến tính | 60 [0.94, 1] | 60 [0.94, 1] | 3 [0.010, 0.139] | 5 [0.028, 0.184] | 8 [0.059, 0.246] | 9 [0.071, 0.266] |
| CDFM, RFF | 60 [0.94, 1] | 60 [0.94, 1] | 8 [0.059, 0.246] | 7 [0.048, 0.226] | 10 [0.083, 0.285] | 11 [0.095, 0.304] |

- **σ của R-L tách theo có hay không có trộn** (luật §6): ở 8/8 nhóm, mọi hệ có σ > 0 đều là hệ có trộn. Điều này khớp với phát biểu có điều kiện đã kiểm từng bit ở §1.

  | Nhóm | Số hệ có σ > 0 / số hệ có trộn | Hệ không trộn có σ > 0 |
  |---|---|---|
  | AVICI tuyến tính | A20 1/3; S20 5/5 | 0/57 và 0/55 |
  | AVICI RFF | A20 2/8; S20 5/7 | 0/52 và 0/53 |
  | CDFM tuyến tính | A20 3/3; S20 5/5 | 0/57 và 0/55 |
  | CDFM RFF | A20 8/8; S20 7/7 | 0/52 và 0/53 |

- **Về trung bình, φ của R-L chủ yếu là giá ở k0.** Vì φ và σ là khoảng cách Hamming nên φ(c) ≤ φ(k0) + σ(c), và φ(c) = φ(k0) khi σ(c) = 0.
  - Ví dụ CDFM tuyến tính: φ(S20) = 9.27, trong đó φ(k0) = 8.37 và σ(S20) = 1.97.
  - Vậy R-L không giữ output ban đầu. Nó cho một output khác ngay ở k0, rồi giữ output đó khi thêm đệm, trừ khi có trộn.
- **Nhãn cỡ** (biên 1.5 cặp): φ(k0) của R-L là LARGE ở 3/4 nhóm; ở AVICI RFF là SMALL. σ(A20) của R-L là SMALL ở cả 4 nhóm. σ(S20) là UNCLEAR ở 3 nhóm và SMALL ở AVICI RFF.

## 4. R-L và R-H: đánh đổi (mô tả)

Chỉ số sàng lọc là trung bình qua 60 hệ mỗi họ. Sàng lọc không phụ thuộc model.

| Họ | Cách | Input | Cột đệm bị gộp | Cạnh đích bị tách | Cặp chéo bị bác bỏ | Hệ có trộn |
|---|---|---|---|---|---|---|
| tuyến tính | R-L | k0 / A20 / S20 | 0 / 0.05 / 1.57 | 0.95 / 0.95 / 0.95 | 0 / 0.05 / 0.18 | 0 / 3 / 5 |
| tuyến tính | R-H | k0 / A20 / S20 | 0 / 0.02 / 0.67 | 0.95 / 1.13 / 1.13 | 0 / 0.02 / 0.05 | 0 / 1 / 2 |
| RFF | R-L | k0 / A20 / S20 | 0 / 0.13 / 2.22 | 1.17 / 1.17 / 1.17 | 0 / 0.18 / 0.33 | 0 / 8 / 7 |
| RFF | R-H | k0 / A20 / S20 | 0 / 0.05 / 1.25 | 1.18 / 1.42 / 1.42 | 0 / 0.05 / 0.12 | 0 / 3 / 4 |

- **Khớp với đánh đổi ở luật §1:**
  - với R-L, số cạnh đích bị tách không đổi khi thêm đệm;
  - với R-H, số đó tăng khi có đệm (0.95 → 1.13; 1.18 → 1.42), vì mức cho mỗi cặp thắt lại theo D.
- **R-L trộn đích với đệm nhiều hơn R-H:** ở S20, 5 so với 2 hệ (tuyến tính) và 7 so với 4 hệ (RFF).
- **Kết quả trên σ:** R-H có nhiều hệ có σ > 0 hơn R-L ở cả 8 nhóm model × họ × input (§3).
- **Trên F1,** hai cách gần nhau (§5): Q(A20) và Q(S20) của chúng chênh nhau tối đa 0.010.
- Không cách nào trội hơn ở mọi thước đo. Đây là đánh đổi giữa giữ quyết định cục bộ và hạn chế gộp nhầm, không phải lỗi của R-H.

## 5. F1 so với mốc ban đầu (mô tả)

Q = F1_f − F1_plain(k0), tức mức so với output ban đầu; G = F1_f(c) − F1_plain(c), tức lợi ích so với plain trên cùng input.

| Model, họ | Cách | Q0 | Q(A20) | Q(S20) | G(A20) | G(S20) |
|---|---|---|---|---|---|---|
| AVICI, tuyến tính | plain | 0 | −0.107 [−0.136, −0.078] | −0.152 [−0.196, −0.107] | 0 | 0 |
| | R-L | +0.020 [−0.005, +0.045] | +0.020 [−0.005, +0.044] | +0.004 [−0.024, +0.033] | +0.127 [+0.095, +0.159] | +0.156 [+0.113, +0.200] |
| | R-H | +0.022 [−0.003, +0.047] | +0.009 [−0.017, +0.036] | +0.001 [−0.028, +0.030] | +0.117 [+0.082, +0.152] | +0.153 [+0.110, +0.196] |
| AVICI, RFF | plain | 0 | −0.034 [−0.055, −0.014] | −0.085 [−0.108, −0.062] | 0 | 0 |
| | R-L | −0.007 [−0.017, +0.003] | −0.007 [−0.017, +0.003] | −0.015 [−0.029, −0.002] | +0.028 [+0.006, +0.049] | +0.070 [+0.047, +0.093] |
| | R-H | −0.009 [−0.019, +0.001] | −0.007 [−0.018, +0.004] | −0.012 [−0.024, +0.000] | +0.028 [+0.006, +0.050] | +0.074 [+0.049, +0.098] |
| CDFM, tuyến tính | plain | 0 | −0.066 [−0.084, −0.049] | −0.045 [−0.067, −0.024] | 0 | 0 |
| | R-L | −0.024 [−0.042, −0.005] | −0.022 [−0.041, −0.003] | −0.029 [−0.047, −0.010] | +0.044 [+0.021, +0.068] | +0.017 [−0.006, +0.040] |
| | R-H | −0.026 [−0.045, −0.006] | −0.028 [−0.046, −0.011] | −0.030 [−0.048, −0.012] | +0.038 [+0.017, +0.059] | +0.016 [−0.008, +0.039] |
| CDFM, RFF | plain | 0 | −0.102 [−0.127, −0.077] | −0.044 [−0.063, −0.026] | 0 | 0 |
| | R-L | −0.001 [−0.019, +0.017] | −0.003 [−0.021, +0.016] | −0.009 [−0.025, +0.007] | +0.099 [+0.070, +0.128] | +0.035 [+0.018, +0.052] |
| | R-H | −0.000 [−0.018, +0.018] | +0.002 [−0.017, +0.022] | −0.001 [−0.018, +0.016] | +0.105 [+0.075, +0.134] | +0.043 [+0.026, +0.060] |

- **Plain** mất F1 khi thêm đệm ở cả 8 ô model × họ × input, từ −0.034 đến −0.152. Mẫu hình này giống C1 trên các hệ held-out mới, nhưng chỉ là mô tả, vì P-N6 không kiểm lại C1.
- **R-L** thu hẹp phần mất đó ở mọi nhóm. G dương với CI không chứa 0 ở 7/8 ô; ngoại lệ là CDFM tuyến tính ở S20: +0.017 [−0.006, +0.040].
- **Q của R-L so với Q0 của chính nó:**
  - ở A20, Q gần bằng Q0 ở cả bốn nhóm, chênh tối đa 0.0015;
  - ở S20, Q thấp hơn Q0 từ 0.005 đến 0.015 (AVICI tuyến tính −0.015, AVICI RFF −0.009, CDFM tuyến tính −0.005, CDFM RFF −0.008);
  - phần chênh này chỉ đến từ các hệ có trộn, vì ở hệ không trộn σ = 0 nên skeleton không đổi;
  - với CDFM tuyến tính, phần lớn mức Q(S20) = −0.029 là giá ở k0 (−0.024).
- **Q(S20) của R-L ở AVICI RFF** là −0.015 [−0.029, −0.002]: dấu NEG, cỡ SMALL. Đại lượng này không thuộc giả thuyết nào, vì P6-1 chỉ dùng Q0 và Q(A20).

## 6. Đối chứng decoder của CDFM (mô tả)

Tính từ output plain, không chạy thêm model. Ở k0, FROZEN và ngưỡng cục bộ trùng plain theo cách dựng: Q0 = 0 và φ(k0) = 0. G5 đã kiểm điều này cho ngưỡng cục bộ.

| Họ | Cách | Q0 | Q(A20) | Q(S20) | G(A20) | G(S20) | φ(A20) | φ(S20) | Hệ có σ > 0 (A20; S20) |
|---|---|---|---|---|---|---|---|---|---|
| tuyến tính | plain | 0 | −0.066 | −0.045 | 0 | 0 | 19.03 | 17.72 | 60; 60 |
| | R-L | −0.024 | −0.022 | −0.029 | +0.044 | +0.017 | 8.32 | 9.27 | 3; 5 |
| | FIXED 0.5 | −0.094 | −0.163 | −0.138 | −0.097 | −0.093 | 33.48 | 28.95 | 58; 58 |
| | FROZEN | 0 | −0.087 | −0.069 | −0.020 | −0.023 | 18.45 | 18.00 | 59; 58 |
| | ngưỡng cục bộ | 0 | −0.123 | −0.086 | −0.056 | −0.041 | 24.82 | 21.17 | 59; 58 |
| RFF | plain | 0 | −0.102 | −0.044 | 0 | 0 | 20.63 | 14.03 | 60; 60 |
| | R-L | −0.001 | −0.003 | −0.009 | +0.099 | +0.035 | 4.83 | 6.98 | 8; 7 |
| | FIXED 0.5 | −0.120 | −0.195 | −0.174 | −0.093 | −0.130 | 40.85 | 35.47 | 60; 60 |
| | FROZEN | 0 | −0.050 | −0.078 | +0.052 | −0.033 | 13.05 | 17.32 | 60; 60 |
| | ngưỡng cục bộ | 0 | −0.072 | −0.103 | +0.030 | −0.059 | 15.80 | 22.83 | 60; 60 |

CI đầy đủ ở [`checks/pn6_reading.json`](checks/pn6_reading.json). Trừ Q0 = 0 theo cách dựng của FROZEN và ngưỡng cục bộ, mọi Q và G của ba đối chứng trong bảng đều có CI không chứa 0.

- **FROZEN và ngưỡng cục bộ** dùng nhiều thông tin hơn R-L, theo hai cách khác nhau.
  - Chỉ **FROZEN** cố định ngưỡng, ở τ(k0).
  - **Ngưỡng cục bộ** vẫn tính lại ngưỡng, từ điểm của khối đích. Nó chỉ bỏ điểm của các cặp ngoài khối đích khỏi bộ chọn ngưỡng.
- **Ở S20:**
  - φ của FROZEN là 18.00 (tuyến tính) và 17.32 (RFF), ngang hoặc lớn hơn plain (17.72 và 14.03). Cố định ngưỡng không làm giảm số cặp đổi trạng thái so với plain, vì điểm của khối đích vẫn đổi (luật §5);
  - φ của ngưỡng cục bộ là 21.17 và 22.83, lớn hơn plain.
- **Ở A20:**
  - trên hệ RFF, φ của cả hai thấp hơn plain: 13.05 và 15.80 so với 20.63;
  - trên hệ tuyến tính, φ ngang hoặc lớn hơn plain: 18.45 và 24.82 so với 19.03.
- **So với R-L:** ở mọi ô, φ của cả hai lớn hơn φ của R-L (4.8–9.3 cặp).
- **Δm của FROZEN** dương ở cả bốn ô, từ +6.7 đến +16.4 cạnh: ở ngưỡng cũ, có nhiều cặp vượt ngưỡng hơn.
- **F1:** ở S20, F1 của FROZEN và ngưỡng cục bộ thấp hơn plain ở cả hai họ (G từ −0.023 đến −0.059). Ở A20 trên hệ RFF, cả hai lại tăng F1 (+0.052 và +0.030).
- **FIXED 0.5:**
  - F1 thấp nhất và φ (so với output ban đầu) lớn nhất trong mọi cách đọc, ở mọi ô, ngay từ k0 (Q0 −0.094 và −0.120; φ(k0) 20.32 và 25.32);
  - không phải thước đo nào cũng kém nhất: tỉ lệ hệ đổi output là 58/60 ở hệ tuyến tính, thấp hơn plain (60/60); σ(A20) ở hệ tuyến tính là 16.90, thấp hơn plain (19.03).
- P6-2 chỉ so φ ở S20. Bảng này không cho phép viết rằng FROZEN vô dụng.

## 7. Bảng thật (mô tả; không có thước đo chất lượng)

Mốc của φ là output plain ở k0 của P-N5. Cột "plain (P-N5)" là flips khi thêm đệm Gauss, đã báo ở P-N5 §3.2; ở mọi điều kiện, cả 20 lần sinh đều có flips ≥ 1. Ngoặc vuông là CI 95% Clopper–Pearson cho tỉ lệ lần sinh có σ > 0.

| Bảng | Model | plain (P-N5): k20; k40 | R-L φ(k0) | R-L σ k20 (lần sinh > 0) | R-L σ k40 (lần sinh > 0) | R-H φ(k0) | R-H σ k20 | R-H σ k40 |
|---|---|---|---|---|---|---|---|---|
| Sachs | AVICI | 2.85; 4.30 | 4 | 0 (0/20 [0, 0.17]) | 0.15 (2/20 [0.01, 0.32]) | 4 | 0 (0/20) | 0 (0/20) |
| Sachs | CDFM | 1.50; 2.50 | 1 | 0 (0/20 [0, 0.17]) | 0 (0/20 [0, 0.17]) | 1 | 0 (0/20) | 0 (0/20) |
| Wine | AVICI | 5.40; 6.20 | 0 | 0.70 (2/20 [0.01, 0.32]) | 0.15 (2/20 [0.01, 0.32]) | 0 | 0.30 (1/20 [0.00, 0.25]) | 0 (0/20) |
| Wine | CDFM | 11.00; 11.00 | 0 | 0.55 (2/20 [0.01, 0.32]) | 0.95 (3/20 [0.03, 0.38]) | 0 | 0.30 (1/20 [0.00, 0.25]) | 0 (0/20) |

- **Phân hoạch ở k0** (§9.6):
  - Sachs được chia thành 4 thành phần, cột {0, 1}, {2, 3, 4}, {5, 6, 7}, {8, 9, 10} theo thứ tự cột đã khóa ở P-N5. R-L và R-H cho cùng phân hoạch này.
  - Wine là một thành phần duy nhất, nên ở k0 cả R-L lẫn R-H trùng plain (φ(k0) = 0).
- **Trên Sachs,** mọi cạnh của plain ở k0 nằm trong các thành phần. φ(k0) đến từ việc chạy model trên từng thành phần: AVICI từ 4 thành 6 cạnh (4 cặp đổi), CDFM từ 9 thành 10 cạnh (1 cặp).
- **σ > 0** chỉ xảy ra ở lần sinh có trộn. Trên Wine, chỉ một cột đệm bị gộp vào thành phần duy nhất cũng đủ làm 5–8 cặp đổi trạng thái ở k = 20 (AVICI 6 và 8; CDFM 5 và 6).
- **So với plain,** chỉ để mô tả: plain đổi ở 20/20 lần sinh của mọi điều kiện, còn R-L đổi ở 0–3/20.
- **Không có câu nào về độ chính xác.** φ(k0) trên Sachs là độ lệch khỏi output plain, không phải sai số. Phân hoạch không được so với đồ thị tham chiếu nào.

## 8. Chi phí (mô tả)

**Lượt chính** chỉ tính output đích (các thành phần có biến đích):

| Bước | Số job | Thời gian (s) |
|---|---|---|
| p-value HSIC (mọi cặp, một lần mỗi input; R-L, R-H và hai model dùng chung) | 442 | 211 |
| AVICI plain (chỉ tổng hợp; plain trên bảng thật lấy từ P-N5) | 360 | 1 332 |
| AVICI R-L (tổng hợp + bảng thật) | 442 | 969 (840 + 129) |
| AVICI R-H | 442 | 915 (791 + 124) |
| CDFM plain | 360 | 2 242 |
| CDFM R-L | 442 | 1 309 (1 110 + 199) |
| CDFM R-H | 442 | 1 260 (1 064 + 196) |

**Pipeline đầy đủ** chạy mọi thành phần có từ 2 biến trở lên, tức chi phí thật của một cách sửa không biết khối đích. Phần này chỉ đo trên DEV6, với 48 input mỗi model (G9; [`checks/gates6.json`](checks/gates6.json)):

| Model | plain | R-L, chỉ thành phần đích | R-L đầy đủ (đích + thành phần khác) | p-value | R-L đầy đủ + p-value, so với plain |
|---|---|---|---|---|---|
| AVICI | 203.7 s | 129.8 s | 196.4 s (104.3 + 92.0) | 22.4 s | × 1.07 |
| CDFM | 307.9 s | 138.5 s | 197.5 s (136.4 + 60.9) | 22.4 s | × 0.71 |

- R-H gần bằng R-L: pipeline đầy đủ tốn 195.9 s (AVICI) và 195.8 s (CDFM), chưa cộng p-value.
- **Phạm vi:** D ≤ 40 ở dữ liệu tổng hợp và D ≤ 51 ở bảng thật; n = 500; CPU, 2 luồng. Chưa đo với D hoặc n lớn hơn.
- Thời gian của từng biến thể có cả thời gian biên dịch của JAX. Vì vậy so giữa các biến thể chỉ gần đúng (suy luận).

## 9. Hậu nghiệm ngoài luật (POST-HOC; mô tả; không có phép kiểm)

Script [`posthoc/posthoc_pn6.py`](posthoc/posthoc_pn6.py) chỉ đọc output đã lưu, không chạy model. Output ở [`posthoc/posthoc_output.json`](posthoc/posthoc_output.json) và [`posthoc/posthoc_output.txt`](posthoc/posthoc_output.txt). Các số dưới đây không thay nhãn nào đã khóa.

### 9.1 Giá ở k0 của R-L: cặp bị tách và cặp trong cùng thành phần

Mỗi cặp đích ở k0 thuộc một trong hai loại:

- **cặp bị tách:** phân hoạch đặt hai biến vào hai thành phần khác nhau, nên R-L ép cặp đó thành không-cạnh;
- **cặp trong cùng thành phần:** model chạy trên tập cột của thành phần đó.

Bảng dưới là trung bình qua 60 hệ mỗi họ. ΔTP và ΔFP là chênh lệch số cạnh đúng và cạnh sai của R-L ở k0 so với plain ở k0.

| Model, họ | φ(k0) | trên cặp bị tách | trong thành phần | cạnh thật bị tách | ΔTP / ΔFP, cặp bị tách | ΔTP / ΔFP, trong thành phần |
|---|---|---|---|---|---|---|
| AVICI, tuyến tính | 4.03 | 0.85 | 3.18 | 0.95 | −0.48 / −0.37 | +0.70 / +0.32 |
| AVICI, RFF | 0.85 | 0.28 | 0.57 | 1.17 | −0.20 / −0.08 | +0.07 / 0.00 |
| CDFM, tuyến tính | 8.37 | 1.55 | 6.82 | 0.95 | −0.63 / −0.92 | +0.52 / +3.07 |
| CDFM, RFF | 4.78 | 1.25 | 3.53 | 1.17 | −0.33 / −0.92 | 0.00 / 0.00 |

- Ở cả bốn nhóm, phần lớn φ(k0) nằm **trong thành phần**, không ở cặp bị tách.
- **CDFM tuyến tính:**
  - trong thành phần, cạnh sai tăng 3.07;
  - ở cặp bị tách, R-L vừa mất 0.63 cạnh đúng vừa bớt 0.92 cạnh sai.

**Kế toán F1 của Q0** (thêm sau review của user; user tính, agent tính lại và ra cùng số).

- Cách tính: thay trạng thái của R-L ở k0 vào plain ở k0, trên một loại cặp trước rồi loại kia, theo cả hai thứ tự.
- Trung bình qua 60 hệ. Mỗi thứ tự cộng lại đúng Q0.

| Model, họ | Q0 | Cặp bị tách trước: tách / trong | Trong thành phần trước: trong / tách |
|---|---|---|---|
| AVICI, tuyến tính | +0.0198 | −0.0102 / +0.0300 | +0.0303 / −0.0104 |
| AVICI, RFF | −0.0069 | −0.0069 / +0.0001 | +0.0003 / −0.0072 |
| CDFM, tuyến tính | −0.0235 | −0.0078 / −0.0157 | −0.0154 / −0.0082 |
| CDFM, RFF | −0.0014 | −0.0005 / −0.0008 | −0.0015 / +0.0002 |

- **CDFM tuyến tính:** khoảng −0.008 ở cặp bị tách và −0.015 đến −0.016 trong thành phần. Ước lượng điểm khớp với nhận xét rằng phần trong thành phần lớn hơn.
- **Hai nhóm khác:**
  - với AVICI tuyến tính, phần trong thành phần dương (+0.030) và lớn hơn phần mất ở cặp bị tách;
  - với AVICI RFF, gần như toàn bộ Q0 nằm ở cặp bị tách.
- Đây vẫn là kế toán hậu nghiệm, chưa xác định nguyên nhân.

**Hệ quả cho ghi chú ở luật §12** (phép kiểm kết hợp Fisher-z và HSIC, mỗi phép ở α_L/2):

- điều kiện kích hoạt đã xảy ra, vì P6-1C-lin không được xác nhận;
- kế toán ở trên **không** đủ để đánh giá ứng viên này, vì hai lẽ:
  - đổi phân hoạch sẽ đổi cả input, điểm và ngưỡng bên trong các thành phần, chứ không chỉ các cặp bị tách;
  - chia α_L/2 cho mỗi phép kiểm có thể vừa thêm vừa bỏ liên kết so với HSIC ở α_L, nên phép kết hợp không tự động "mạnh hơn";
- chưa làm phép kiểm này lúc này là để giữ phạm vi bài; ứng viên chưa bị bác bỏ.

### 9.2 CDFM: kế toán bên trong thành phần, lấy τ(k0) làm mốc

Đây là phân rã kế toán phụ thuộc mốc, chưa phải hai nguyên nhân tách biệt:

- **bước 1 (phần điểm):** xác suất của R-L đọc ở τ(k0) của plain, so với plain ở k0;
- **bước 2 (phần ngưỡng):** cách đọc NATIVE theo từng thành phần, so với cách đọc ở τ(k0).

Chưa tính với mốc đảo.

| Họ | Cạnh trong thành phần: plain / R-L ở τ(k0) / R-L NATIVE | Số flips ở hai bước thay thế: plain → R-L ở τ(k0) / R-L ở τ(k0) → R-L NATIVE | ΔFP: phần điểm / phần ngưỡng | Hệ bị tách có gọi model | Ngưỡng thành phần − τ(k0), trên các hệ đó |
|---|---|---|---|---|---|
| tuyến tính | 36.40 / 32.25 / 39.98 | 7.52 / 7.73 | −2.42 / +5.48 | 42/60 | −0.153 (thấp hơn ở 42/42; khoảng −0.489 đến −0.020) |
| RFF | 27.52 / 25.70 / 27.52 | 3.85 / 2.32 | −1.22 / +1.22 | 38/60 | −0.157 (thấp hơn ở 32/38; khoảng −0.425 đến +0.016) |

- **Hai số flips là khoảng cách Hamming của hai bước thay thế** và không cộng thành tổng số flips trong thành phần (6.82 và 3.53 ở §9.1). Một cặp có thể đổi ở bước đầu rồi đổi lại ở bước sau. Phân rã có dấu của ΔFP thì cộng được: −2.42 + 5.48 = +3.07, đúng bằng ΔFP trong thành phần ở §9.1.
- **Hệ tuyến tính:** theo mốc này, cạnh sai tăng trong thành phần nằm ở phần ngưỡng (+5.48), còn phần điểm lại bớt cạnh sai (−2.42). Trên thành phần nhỏ hơn bảng gốc, CDFM chọn ngưỡng NATIVE thấp hơn τ(k0) ở mọi hệ tuyến tính bị tách.
- **Ví dụ xấu nhất,** hệ `PN6-c6-r12` (d_T = 20, e_T = 2, tuyến tính):
  - R-L ở k0 tách đúng một biến ra;
  - trên 19 biến còn lại, CDFM chọn ngưỡng 0.622 thay vì 0.681, và cho 91 cạnh thay vì 64;
  - Δm = +26, toàn bộ ở k0.
- **Suy luận chưa kiểm:** giá ở k0 của R-L với CDFM gắn với cùng loại nhạy cảm của bộ chọn ngưỡng trước tập cột mà N1 đo (C5, C12). Chỉ khác là ở đây cột bị bớt đi chứ không thêm vào. Bảng này không cho phép viết rằng ngưỡng là nguyên nhân.

### 9.3 Cỡ gộp nhầm: hai cực

| Cách, input | Hệ có gộp / 120 | Cỡ gộp mỗi hệ (số cột đệm) | Theo ô |
|---|---|---|---|
| R-L, A20 | 11 | 1 ở cả 11 hệ | rải ở 7/8 ô |
| R-L, S20 | 12 | 15, 17, 19 (5 hệ), 20 (5 hệ) | 9/12 ở ô e_T = 2 |
| R-H, A20 | 4 | 1 | — |
| R-H, S20 | 6 | 17, 19, 19, 20, 20, 20 | 5/6 ở ô e_T = 2 |

- Khớp cảnh báo ở luật §1: với đệm có cấu trúc, một cạnh nối giả có thể kéo gần cả khối đệm vào thành phần đích.
- Khi mọi cột thuộc một thành phần, input của model trùng input của plain (cùng cột, cùng thứ tự), nên theo cấu trúc output của R-L ở input đó trùng plain.
  - Đã kiểm trực tiếp: output trùng plain từng bit ở 170/170 trường hợp (model × cách × input) mà cả bảng là một thành phần.
  - Trong số đó, 8 trường hợp là input S20 bị gộp đủ 20 cột: 4 cặp input × cách sửa (3 với R-L, 1 với R-H), nhân hai model. 162 trường hợp còn lại là input k0.
  - Ở 4 cặp input × cách sửa đó, cách sửa không còn tác dụng.

### 9.4 Cặp chéo bị bác bỏ so với cận trên danh nghĩa

Nếu từng p-value hợp lệ, mức mỗi cặp nhân số cặp chéo là **cận trên** của số bác bỏ nhầm kỳ vọng (luật §1). Cận này không nhất thiết bằng kỳ vọng: với p-value bảo thủ, kỳ vọng nhỏ hơn cận.

- R-L: α_L · d_T · k mỗi hệ;
- R-H: α_H / (D(D − 1)/2) · d_T · k mỗi hệ.

| Cách | Họ | Input | Quan sát (tổng 60 hệ) | Cận trên danh nghĩa | Quan sát / cận | Hệ có ≥ 1 |
|---|---|---|---|---|---|---|
| R-L | tuyến tính | A20 | 3 | 1.80 | 1.7 | 3 |
| R-L | tuyến tính | S20 | 11 | 1.80 | 6.1 | 5 |
| R-L | RFF | A20 | 11 | 1.80 | 6.1 | 8 |
| R-L | RFF | S20 | 20 | 1.80 | 11.1 | 7 |
| R-H | tuyến tính | A20 | 1 | 0.29 | 3.4 | 1 |
| R-H | tuyến tính | S20 | 3 | 0.29 | 10.3 | 2 |
| R-H | RFF | A20 | 3 | 0.29 | 10.3 | 3 |
| R-H | RFF | S20 | 7 | 0.29 | 24.0 | 4 |

- Số đếm nhỏ nên tỉ số rất nhiễu, và không có phép kiểm. Cặp chéo vô hiệu theo thiết kế, nên mọi bác bỏ ở đây là bác bỏ nhầm.
- Mẫu hình khớp cảnh báo ở luật §1: đuôi gamma của HSIC dễ dãi. Ở G9 của P-N2, tỉ lệ bác bỏ thực tế đã gấp 3–4 lần mức danh nghĩa 0.001.
- Suy luận chưa kiểm: xấp xỉ gamma kém hơn ở đuôi xa, tức mức 10⁻⁴ và nhỏ hơn.

### 9.5 Trường hợp xấu nhất

|Δm| lớn nhất theo hệ, lấy trên cả A20 và S20:

| Model, họ | Cách | Hệ (d_T, e_T, họ) | Input | Δm | Δm ở k0 (R so với plain) | σ | Cột bị gộp |
|---|---|---|---|---|---|---|---|
| AVICI, tuyến tính | R-L và R-H | c6-r13 (20, 2, tuyến tính) | S20 | −23 | +8 | 35 | 20 |
| AVICI, RFF | R-L | c7-r13 (20, 2, RFF) | S20 | −16 | 0 | 16 | 19 |
| AVICI, RFF | R-H | c3-r14 (10, 2, RFF) | S20 | −7 | 0 | 7 | 19 |
| CDFM, tuyến tính | R-L và R-H | c6-r12 (20, 2, tuyến tính) | A20 | +26 | +26 | 0 | 0 |
| CDFM, RFF | R-L và R-H | c7-r6 (20, 2, RFF) | S20 | −37 | −18 | 53 | 20 |

- Mọi trường hợp xấu nhất đều ở ô e_T = 2.
- Bốn trong năm trường hợp là gộp gần đủ khối đệm có cấu trúc. Trường hợp còn lại, CDFM tuyến tính, nằm hoàn toàn ở k0 (§9.2).
- So với plain, |Δm| lớn nhất là 29, 17, 98 và 57 (AVICI tuyến tính, AVICI RFF, CDFM tuyến tính, CDFM RFF). Dưới R-L, các số đó là 23, 16, 26 và 37.

### 9.6 Bảng thật: phân hoạch ở k0, và σ > 0 so với trộn

- **Phân hoạch ở k0** như §7.
  - Sachs: plain không có cạnh nào trên cặp bị tách, ở cả hai model.
  - Wine: một thành phần duy nhất.
- **Mọi lần sinh có σ > 0 đều có trộn.**

  | Cách | Bảng, k | Lần sinh có trộn | σ > 0: AVICI | σ > 0: CDFM |
  |---|---|---|---|---|
  | R-L | Sachs, k40 | 6 | 2 | 0 |
  | R-L | Wine, k20 | 2 | 2 | 2 |
  | R-L | Wine, k40 | 3 | 2 | 3 |
  | R-H | Sachs, k40 | 1 | 0 | 0 |
  | R-H | Wine, k20 | 1 | 1 | 1 |

  Các điều kiện còn lại không có lần sinh nào trộn.

## 10. HELD2 chỉ để tham khảo

Số dưới đây không so trực tiếp với P-N6, vì seed và điều kiện khác nhau. Chênh lệch cũng không được quy cho thông tin về họ cơ chế (luật §0, §9).

| Đại lượng | HELD2 (R-B) | P-N6 (R-L) |
|---|---|---|
| φ ở S20 (e = e_T): FROZEN và R | tuyến tính 19.90 và 6.85; RFF 18.87 và 4.43 | tuyến tính 18.00 và 9.27; RFF 17.32 và 6.98 |
| Q0, AVICI (tuyến tính; RFF) | −0.000; +0.007 | +0.020; −0.007 |
| Q0, CDFM (tuyến tính; RFF) | −0.018; +0.000 | −0.024; −0.001 |

## 11. Không được viết

Theo luật §9, cộng thêm các mục từ kết quả này:

- "R-L tương đương mốc ban đầu", hay "R-L sửa được vấn đề", mà không kèm phạm vi;
- "R-L giữ nguyên output ban đầu": φ(k0) là 4–8 cặp ở 3/4 nhóm;
- "R-L bất biến ở mọi hệ": σ > 0 ở 1–8 trên 60 hệ mỗi nhóm, luôn khi có trộn;
- rằng R-L áp dụng được cho biến có sẵn trong dữ liệu thật;
- "R-L tốt hơn mọi cách sửa"; "FROZEN vô dụng";
- rằng chênh lệch với R-B của HELD2 là do thông tin về họ cơ chế;
- trên bảng thật:
  - "R-L đúng hơn", hay bất kỳ câu nào về độ chính xác;
  - rằng phân hoạch của R-L trên Sachs phản ánh cấu trúc thật;
- với P6-1C-lin:
  - "R-L gây tổn thất vượt biên";
  - "R-L không kém mốc ban đầu" cho CDFM trên hệ tuyến tính;
- rằng CI hay nhãn cỡ được Holm bảo vệ;
- số hậu nghiệm ở §9 như kết quả đã xác nhận;
- "giá ở k0 của CDFM là do ngưỡng" như một quan hệ nhân quả: đó là kế toán theo một mốc;
- "R-L rẻ hơn plain" ngoài phạm vi đã đo (DEV6; D ≤ 40; n = 500);
- về phép kiểm kết hợp Fisher-z và HSIC:
  - "sẽ sửa được P6-1C-lin";
  - "đã bị bác bỏ", hay "chỉ xử lý phần nhỏ của vấn đề";
  - "mạnh hơn HSIC ở α_L";
- "FROZEN và ngưỡng cục bộ đều chặn kênh ngưỡng": chỉ FROZEN cố định ngưỡng;
- "FIXED kém ở mọi thước đo";
- số flips ở hai bước thay thế (§9.2) như hai phần cộng thành tổng.

## 12. Hệ quả và bước tiếp (đề xuất; chờ user quyết)

> **Cập nhật sau review:** user đã duyệt kết quả, đóng gap 3 và duyệt C13–C15 với cách viết khác bảng đề xuất dưới đây. Bản chính thức nằm ở [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md); quyết định ghi ở §13. Bảng và danh sách dưới đây giữ nguyên làm bản ghi đề xuất ban đầu; riêng bước 3 đã được làm mềm theo review.

**Bảng claim:** chưa thêm claim nào. Ba dòng đề xuất:

| Đề xuất | Nội dung | Mức bằng chứng |
|---|---|---|
| C13 (P6-1) | Trên hệ tổng hợp held-out, R-L không làm giảm F1 skeleton trung bình quá 0.03 so với output ban đầu, ở k0 và khi có 20 cột Gauss. R-L là sàng lọc HSIC mọi cặp ở mức cố định 10⁻⁴, chỉ dùng bảng input; model chạy trên từng thành phần. Áp cho AVICI (tuyến tính, RFF) và CDFM (RFF) | XÁC NHẬN 3/4; CDFM tuyến tính NOT_CONFIRMED (Q0 −0.024 [−0.042, −0.005]) |
| C14 (P6-2) | Ở đệm có cấu trúc, output của R-L lệch khỏi output ban đầu của CDFM ít hơn FROZEN | XÁC NHẬN 2/2 (dấu) |
| C15 (mô tả) | R-L giữ output của chính nó (σ = 0) ở mọi input không có trộn: theo cấu trúc, và đã kiểm từng bit. Có trộn ở 11/120 hệ với A20 và 12/120 hệ với S20; với đệm có cấu trúc, mỗi lần trộn gần như kéo cả khối đệm vào. R-H tách thêm khi có đệm và có nhiều hệ có σ > 0 hơn. Giá ở k0: φ(k0) là 4–8 cặp ở 3/4 nhóm | MÔ TẢ (P-N6 §3, §4); phần nguồn gốc của giá ở k0 là POST-HOC (§9) |

Ngoài ra, C9 (R của HELD2) sẽ trỏ sang P-N6 cho biến thể chỉ dùng input. Dòng gap 3 ở §2 của bảng claim sẽ đổi trạng thái sau khi user duyệt.

**Bước tiếp:**

1. **Khuyến nghị: đóng gap 3 với kết quả này** sau khi user duyệt.
   - Việc cần làm: cập nhật bảng claim, viết §8 của bản thảo trên nhánh riêng, rồi chuyển sang gap 4 (phạm vi model).
   - Lý do: câu hỏi chính của gap 3 đã có câu trả lời kèm phạm vi rõ. Hai giới hạn còn lại được báo như giới hạn của bài: giá ở k0 của CDFM tuyến tính, và gộp nhầm với đệm có cấu trúc.
2. **Dự phòng, nếu user muốn xử lý CDFM tuyến tính:** một nghiên cứu mới nhắm vào cách đọc ngưỡng theo thành phần của CDFM, không phải phép kiểm sàng lọc (§9.1–§9.2).
   - Phải có luật mới, khóa trước, và seed held-out mới, vì ý tưởng này nảy ra sau khi xem P6-1C-lin.
   - Chưa có ứng viên cụ thể nào chỉ dùng input mà không phụ thuộc tập cột.
3. **Chưa làm lúc này:** phép kiểm kết hợp Fisher-z và HSIC (luật §12).
   - Lý do: giữ phạm vi bài.
   - Ứng viên chưa bị bác bỏ: kế toán ở §9.1 không đủ để đánh giá nó.
4. **Có cơ sở nhưng tốn compute:** hiệu chỉnh p-value HSIC để giảm gộp nhầm, ví dụ permutation cho các cặp gần ngưỡng (§9.4). Chỉ nên làm nếu gộp nhầm trở thành điểm chính của bài.

## 13. Sau review của user (22/11)

**Quyết định:**

- Duyệt kết quả P-N6 và **đóng gap 3**.
- User tái tính sáu phép kiểm, CI và nhãn 5/6, và xác nhận các kiểm tra 320/320 và 572/572. Mã băm của 23 file đóng băng và 54 phụ thuộc cũng khớp.
- Duyệt push `2f013d6` cùng một commit đính chính. Các chỗ sửa không đổi kết quả chính.
- **C13–C15** được duyệt với cách viết của user và đã vào [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md):
  - C13 không mở rộng sang S20;
  - C14 là giữ gần output ban đầu hơn, không phải xác nhận độ chính xác cao hơn;
  - C15 tách tính chất bất biến có điều kiện của thuật toán khỏi tần suất gộp nhầm và đánh đổi quan sát được; 572/572 là kiểm tra cài đặt, không phải kết luận thống kê mới.
- C9 của HELD2 giữ nhãn cũ và dẫn sang C13–C15.
- **Phép kiểm kết hợp Fisher-z và HSIC:** chưa làm, để giữ phạm vi bài; ứng viên chưa bị bác bỏ (§9.1).
- **Bước tiếp:**
  - hoàn thiện bản thảo trước khi mở nghiên cứu mới: cập nhật claim, viết §8, ghép bản thảo đầy đủ và rà xem claim nào còn thiếu bằng chứng;
  - GO cho thiết kế thu gọn của gap 4, nếu việc thêm model kiểm được một claim cụ thể; đo ngân sách trước lượt chạy chính; gap 4 không chặn việc viết;
  - giữ nghiên cứu ngưỡng theo thành phần làm hướng tiếp nối, chưa mở thành pha mới.

**Nhật ký đính chính.** Nhãn và số liệu của sáu giả thuyết không đổi.

| # | Chỗ | Trước | Sau |
|---|---|---|---|
| 1 | Mở đầu | "chưa chạy model nào trên hai bảng thật" | "chưa chạy R-L hay R-H của P-N6 trên hai bảng thật"; output plain đã có từ P-N5 |
| 2 | §6 | Gọi cả FROZEN lẫn ngưỡng cục bộ là "chặn kênh ngưỡng" | Chỉ FROZEN cố định ngưỡng; ngưỡng cục bộ tính lại ngưỡng từ điểm của khối đích |
| 3 | §6 | "FIXED 0.5 kém ở mọi thước đo" | F1 thấp nhất và φ lớn nhất. Tỉ lệ hệ đổi output không luôn cao hơn plain (58/60 so với 60/60 ở hệ tuyến tính) |
| 4 | §9.2 | "Flips: phần điểm / phần ngưỡng" | "Số flips ở hai bước thay thế". Hai khoảng cách Hamming không cộng thành tổng; ΔFP có dấu thì cộng được |
| 5 | §9.3 | "4 trường hợp là input S20 …; còn lại là input k0" | 8 trường hợp (4 cặp input × cách sửa, nhân hai model); 162 là input k0 |
| 6 | §0, §9.4 | "Kỳ vọng danh nghĩa" | "Cận trên danh nghĩa" của kỳ vọng, đúng khi p-value hợp lệ; không nhất thiết bằng kỳ vọng |
| 7 | §0, §9.1, §11, §12 | Phép kiểm kết hợp "chỉ tác động trực tiếp lên phần nhỏ hơn"; "không khuyến nghị" | Chưa đủ cơ sở để kết luận như vậy. Đổi phân hoạch đổi cả input, điểm và ngưỡng trong thành phần, và mức α/2 có thể vừa thêm vừa bỏ liên kết. Dừng nhánh này để giữ phạm vi bài. Thêm kế toán F1 (user tính, agent tính lại) |
| 8 | §1 | Bộ nhớ đỉnh 2.01 GB | Giữ số đo thật; nói rõ mức này không làm mất tính hợp lệ; giải thích về JAX vẫn là suy luận |
| 9 | §3, bảng φ và σ, AVICI-RFF, R-L, φ(k0) | CI [0.54, 1.17] | [0.53, 1.17]: cận dưới trong `pn6_reading.json` là 0.5345, làm tròn thành 0.53. Lỗi làm tròn khi chép số, phát hiện ở lượt rà cuối ngày 23/11; nhãn và kết luận không đổi |
