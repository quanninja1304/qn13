# P-N5: kết quả kiểm tính nhất quán trên dữ liệu thật, gap 2 (22/11/2026)

> **Luật:** [P-N5 v1](PN5_rules_vi.md), khóa ở commit `99197d8` (push lúc 2026-11-22T05:28:35Z). Code đóng băng cùng các phụ thuộc và mã băm của hai file dữ liệu ở `b1a9f29` (push lúc 05:47:08Z), trước khi chạy model nào trên hai bảng thật.
> **Chạy:** 616 job, gồm 164 job mỗi thuật toán cho AVICI, CDFM và PC, và 124 job cho GES. Thời gian: 05:48:27 đến 07:08:50 UTC ngày 22/11 (80 phút).
> **Đọc:** bằng `analyze5.py` đã đóng băng, sau khi kiểm hoàn tất đạt (§1).
> **Nhãn:**
>
> - [Verified-run] cho số liệu.
> - CONFIRMED / NOT_CONFIRMED chỉ áp cho **tám** giả thuyết, qua Holm ở mức familywise 0.05.
> - §3 là **mô tả**, không thuộc bộ Holm. §4 là **kiểm tra hậu nghiệm ngoài luật**, không phải căn cứ xác nhận.
>
> **Phạm vi:**
>
> - hai bảng thật đã cố định: Sachs CD3/CD28 và Wine trắng; mỗi bảng 500 hàng chọn trước, normal-score theo hạng;
> - AVICI `scm-v0` và CDFM; PC và GES là đối chứng thực nghiệm;
> - k ∈ {0, 20, 40}, đệm Gauss (e = 0) và đệm ER–RFF có cấu trúc (e = 2);
> - 20 lần sinh đệm mỗi điều kiện.
>
> Mọi suy luận có điều kiện trên từng bảng, cách chọn hàng và tiền xử lý đã cố định. 20 lần sinh đệm **không** phải 20 bộ dữ liệu thật. Không có câu nào về độ chính xác.

## 1. Hoàn tất và toàn vẹn (đạt hết)

Script đóng băng `completeness5.py` (luật §7) cho `ok: true`, không có vấn đề nào ([`checks/pn5_completeness.json`](checks/pn5_completeness.json)):

- **Trạng thái job:** 616/616 job có đúng một trạng thái kết thúc, và cả 616 đều `ok`. Không có `timeout`, `error` hay `budget_stop`.
- **Input:** mã băm input của mọi output khớp input sinh lại. Ở mọi input, khối thật trùng từng bit với X_R đã lưu. Mã băm X_R khớp số G1: Sachs `4e51d469…`, Wine `9cd901fb…`.
- **Dữ liệu:** SHA-256 của hai file khớp manifest, ở đầu và cuối lượt.
- **Cổng đóng băng:**
  - `pn5_start` và `pn5_end` đều `ok: true`, cùng commit `b1a9f29`, cùng mã băm `SHA256SUMS` và cùng mã băm phụ thuộc ([`checks/pn5_run_header.json`](checks/pn5_run_header.json));
  - một lần gọi `precheck` trước lượt chạy cũng `ok`; kiểm hoàn tất không dùng nó.
- **Tất định:** với cả bốn thuật toán và cả hai bảng, hai lần chạy ở k0 trùng từng bit.
- **Ngân sách và bộ nhớ:**
  - 80 phút tính từ mốc `pn5_start`, dưới mốc 3 giờ; G7 đã ước tính 1.83 giờ;
  - bộ nhớ đỉnh: AVICI 1.22 GB, CDFM 0.47 GB, PC 0.19 GB, GES 0.09 GB (PC và GES đo trong tiến trình con).
- **Kiểm lại độc lập** (agent; script riêng, không import code P-N5; [`posthoc/recheck_pn5.py`](posthoc/recheck_pn5.py)):
  - tính lại tám contrast từ output thô theo định nghĩa ở luật §4–§5;
  - kết quả khớp bản đọc: 160 giá trị theo lần sinh, t, p, thứ tự và nhãn Holm, m0, cùng lần chạy lại k0 trùng từng bit ([`posthoc/posthoc_output.txt`](posthoc/posthoc_output.txt)).

## 2. Tám giả thuyết: 7 CONFIRMED, 1 NOT_CONFIRMED

Phép kiểm theo luật §5: t ghép cặp một phía qua 20 lần sinh (df = 19), rồi Holm 0.05 trên tám p-value. Số liệu đầy đủ, gồm giá trị của từng lần sinh, ở [`checks/pn5_reading.json`](checks/pn5_reading.json).

| ID | Bảng | Model, điều kiện | Ước lượng [CI 95%] | t | p một phía | Hạng, ngưỡng Holm | Nhãn | Cỡ (mô tả) | Lần sinh +/0/− | Số giá trị khác nhau |
|---|---|---|---|---|---|---|---|---|---|---|
| P5-1S-A | Sachs | AVICI, k = 20 Gauss | +2.65 [+2.24, +3.06] | 13.54 | 1.6e-11 | 4, 0.0100 | **CONFIRMED** | LARGE | 20/0/0 | 4 |
| P5-1S-C | Sachs | CDFM, k = 20 Gauss | +1.30 [+0.84, +1.76] | 5.94 | 5.1e-6 | 6, 0.0167 | **CONFIRMED** | UNCLEAR | 17/3/0 | 5 |
| P5-1W-A | Wine | AVICI, k = 20 Gauss | +5.30 [+3.00, +7.60] | 4.82 | 6.0e-5 | 7, 0.0250 | **CONFIRMED** | LARGE | 20/0/0 | 11 |
| P5-1W-C | Wine | CDFM, k = 20 Gauss | +10.90 [+9.81, +11.99] | 20.86 | 7.4e-15 | 2, 0.0071 | **CONFIRMED** | LARGE | 20/0/0 | 7 |
| P5-2S-20 | Sachs | CDFM, k = 20 | −0.007 [−0.031, +0.017] | −0.61 | 0.72 | 8, 0.0500 | NOT_CONFIRMED | UNCLEAR | 9/0/11 | 20 |
| P5-2S-40 | Sachs | CDFM, k = 40 | +0.125 [+0.103, +0.147] | 11.76 | 1.8e-10 | 5, 0.0125 | **CONFIRMED** | LARGE | 20/0/0 | 20 |
| P5-2W-20 | Wine | CDFM, k = 20 | +0.180 [+0.159, +0.201] | 18.11 | 9.6e-14 | 3, 0.0083 | **CONFIRMED** | LARGE | 20/0/0 | 20 |
| P5-2W-40 | Wine | CDFM, k = 40 | +0.191 [+0.180, +0.202] | 36.61 | 2.2e-19 | 1, 0.0063 | **CONFIRMED** | LARGE | 20/0/0 | 20 |

- Không giả thuyết nào DEGENERATE. Chỉ P5-2S-20 có ước lượng điểm ngược phía dự đoán.
- **CONFIRMED chỉ xác nhận dấu** của trung bình có điều kiện qua các lần sinh đệm, trên bảng đã cố định.
- **Nhãn cỡ** dùng biên 1 cặp cho flips và 0.03 cho ngưỡng (luật §5):
  - LARGE: CI nằm hẳn ngoài biên;
  - SMALL: CI nằm hẳn trong [−biên, +biên];
  - còn lại là UNCLEAR.
  - P5-1S-C là UNCLEAR vì CI [0.84, 1.76] chứa biên 1 cặp. P5-2S-20 là UNCLEAR, không phải SMALL, vì cận dưới −0.0310 vượt −0.03 một chút.
  - CI và nhãn cỡ là mô tả; Holm không bảo vệ chúng đồng thời.
- **Mức rời rạc** (luật §5): P5-1S-A chỉ có 4 giá trị khác nhau qua 20 lần sinh, và P5-1S-C có 5 giá trị, trong đó có 3 lần sinh bằng 0. Vì vậy phép t ở các giả thuyết này là xấp xỉ. §4 báo thêm một kiểm tra dấu hậu nghiệm về tính nhất quán của hướng thay đổi. Kiểm tra này không thay nhãn đã khóa, và không thay thế phép kiểm về trung bình.

### 2.1 P5-1: ý nghĩa và bốn thành phần

- **Estimand:** E_r[flips_M,r − max(flips_PC,r, flips_GES,r)] ở k = 20 với đệm Gauss, có điều kiện trên bảng đã cố định.
- Max lấy theo từng lần sinh. Vì vậy, ở mỗi lần sinh, model được so với đối chứng đổi nhiều hơn ở chính lần sinh đó.
- Vì E[max] ≥ max của hai trung bình, contrast này chặt hơn việc so với trung bình riêng của từng đối chứng. Ở Sachs, trung bình của max là 0.20, lớn hơn max của hai trung bình là 0.15.
- flips đếm trên 55 cặp không thứ tự của khối thật.

| Bảng | m0: AVICI / CDFM / PC / GES | flips AVICI [CI 95%] | flips CDFM [CI 95%] | flips PC | flips GES | max(PC, GES) |
|---|---|---|---|---|---|---|
| Sachs | 4 / 9 / 7 / 5 | 2.85 [2.47, 3.23] | 1.50 [1.11, 1.89] | 0.15 | 0.05 | 0.20 |
| Wine | 5 / 38 / 16 / 23 | 5.40 [3.13, 7.67] | 11.00 [9.92, 12.08] | 0.00 | 0.10 | 0.10 |

- Ở Wine, PC không đổi cặp nào ở cả 20 lần sinh, nên max chính là flips của GES.
- PC và GES đổi tối đa 1 cặp ở bất kỳ lần sinh nào.
- **Độ ổn định không chứng minh độ chính xác.** PC và GES có thể ít đổi vì luôn cho cùng một output, kể cả khi output đó sai.

**Câu được viết** (luật §9):

- Trên 500 hàng đã chọn của bảng Sachs, với tiền xử lý đã khóa, thêm 20 cột Gauss độc lập làm skeleton của AVICI trên khối thật đổi trạng thái trung bình 2.85 trong 55 cặp. Đối chứng cổ điển đổi nhiều hơn ở từng lần sinh (max của PC và GES theo từng lần sinh) đổi trung bình 0.20 cặp. Mức đổi của AVICI lớn hơn mức này, trung bình 2.65 cặp.
- Với CDFM trên Sachs, mức đổi là 1.50 cặp, lớn hơn max theo từng lần sinh trung bình 1.30 cặp.
- Trên 500 hàng đã chọn của bảng Wine, mức đổi của AVICI là 5.40 cặp và của CDFM là 11.00 cặp. Hai mức này lớn hơn max theo từng lần sinh (trung bình 0.10 cặp) lần lượt 5.30 và 10.90 cặp.

### 2.2 P5-2: ngưỡng NATIVE của CDFM

| Bảng | τ ở k0 | k = 20: Gauss → có cấu trúc | k = 40: Gauss → có cấu trúc |
|---|---|---|---|
| Sachs | 0.751 | 0.809 → 0.802 | 0.704 → 0.829 |
| Wine | 0.493 | 0.613 → 0.793 | 0.645 → 0.836 |

- **Wine:** ở cả hai k, ngưỡng với đệm có cấu trúc cao hơn với đệm Gauss trong cùng lần sinh, ở cả 20 lần sinh.
- **Sachs, k = 40:**
  - CONFIRMED (+0.125);
  - đệm Gauss làm ngưỡng *thấp hơn* k0 (−0.047), còn đệm có cấu trúc làm ngưỡng cao hơn (+0.078);
  - contrast +0.125 gồm cả hai chiều này.
- **Sachs, k = 20:**
  - NOT_CONFIRMED;
  - cả hai kiểu đệm đều nâng ngưỡng lên khoảng 0.80, tức +0.058 với đệm Gauss và +0.051 với đệm có cấu trúc so với k0;
  - ở 9 lần sinh contrast dương, ở 11 lần sinh contrast âm.
- **So với P-N4,** trên khối đích tổng hợp với e = e_T ∈ {1, 2}: D2 là +0.193 ở k = 20 và +0.227 ở k = 40.
  - Ước lượng điểm ở Wine gần các giá trị đó; ở Sachs thì nhỏ hơn.
  - Đây chỉ là so sánh ước lượng điểm giữa hai thiết kế khác nhau, không có phép kiểm.

**Câu được viết:**

- Trên 500 hàng đã chọn của bảng Wine, với tiền xử lý đã khóa, ngưỡng NATIVE của CDFM với đệm có cấu trúc cao hơn với đệm Gauss trong cùng lần sinh: trung bình +0.180 ở k = 20 và +0.191 ở k = 40.
- Trên Sachs, điều này được xác nhận ở k = 40 (+0.125), nhưng không ở k = 20 (−0.007; CI chứa 0).

## 3. Mô tả (không thuộc bộ Holm)

### 3.1 Bối cảnh ở k0

| Thuật toán | Sachs: m0 trên 55 cặp | Wine: m0 trên 55 cặp |
|---|---|---|
| AVICI | 4 | 5 |
| CDFM (NATIVE; FIXED 0.5) | 9; 10 | 38; 38 |
| PC | 7 | 16 |
| GES | 5 | 23 |

- AVICI cho skeleton rất thưa trên cả hai bảng.
- CDFM cho skeleton dày trên Wine (38/55 cặp, với ngưỡng τ(k0) = 0.493).
- Ở k0, cách đọc FROZEN trùng NATIVE ở cả hai bảng: ma trận kề NATIVE đúng bằng p > τ(k0) ngoài đường chéo. Vì vậy hai cách đọc dùng chung m0.

### 3.2 flips theo điều kiện: trung bình [nhỏ nhất, lớn nhất] qua 20 lần sinh

| Thuật toán | Sachs k20 Gauss | Sachs k20 có cấu trúc | Sachs k40 Gauss | Sachs k40 có cấu trúc | Wine k20 Gauss | Wine k20 có cấu trúc | Wine k40 Gauss | Wine k40 có cấu trúc |
|---|---|---|---|---|---|---|---|---|
| AVICI | 2.85 [1, 4] | 4.00 [3, 5] | 4.30 [2, 8] | 4.00 [4, 4] | 5.40 [1, 16] | 3.60 [3, 5] | 6.20 [1, 12] | 3.95 [3, 6] |
| CDFM | 1.50 [1, 4] | 3.95 [0, 11] | 2.50 [1, 7] | 5.90 [3, 13] | 11.00 [7, 16] | 20.60 [15, 29] | 11.00 [7, 15] | 19.90 [12, 28] |
| PC | 0.15 [0, 1] | 0 [0, 0] | 0.25 [0, 1] | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | 0.10 [0, 1] | 0 [0, 0] |
| GES | 0.05 [0, 1] | 0 [0, 0] | 0.20 [0, 1] | không chạy | 0.10 [0, 1] | 0.10 [0, 1] | 0 [0, 0] | không chạy |

- **Δp** trung bình (AVICI; CDFM), theo thứ tự bốn cột của mỗi bảng như trên:
  - Sachs: AVICI 0.039, 0.047, 0.057, 0.052; CDFM 0.067, 0.260, 0.121, 0.381.
  - Wine: AVICI 0.069, 0.154, 0.105, 0.149; CDFM 0.151, 0.186, 0.178, 0.243.
- **Contrast kiểu P5-1 ở các điều kiện khác** (mô tả; ở k = 40 với đệm có cấu trúc chỉ so với PC):
  - dương ở cả 20 lần sinh, trừ CDFM trên Sachs ở k20 có cấu trúc và k40 Gauss (18/2/0 mỗi điều kiện);
  - AVICI trên Sachs ở k40 có cấu trúc có contrast bằng 4 ở cả 20 lần sinh. Nếu kiểm, contrast hằng này sẽ là DEGENERATE; điều kiện này không thuộc bộ Holm.
- **Độ biến thiên theo lần sinh:** AVICI trên Wine với đệm Gauss đổi từ 1 đến 16 cặp ở k = 20, tùy lần sinh đệm.

### 3.3 Số cạnh trên khối thật

- **AVICI, Sachs** (m0 = 4):
  - m trung bình ở bốn điều kiện: 1.15, 0.10, 0.70, 0.00;
  - số lần sinh có m = 0: 3, 18, 13 và 20;
  - ở k20 Gauss, mọi thay đổi đều là mất cạnh, vì trung bình flips bằng trung bình −Δm;
  - ở k40 có cấu trúc, cả 4 cạnh ở k0 đều mất ở cả 20 lần sinh.
- **AVICI, Wine** (m0 = 5): m trung bình 8.90, 3.70, 9.00, 2.65. Đệm Gauss thêm cạnh (tối đa 19), còn đệm có cấu trúc bớt cạnh.
- **CDFM, ba cách đọc** (m trung bình; FIXED có mốc riêng ở k0):

  | Bảng, điều kiện | NATIVE | FROZEN τ(k0) | FIXED 0.5 |
  |---|---|---|---|
  | Sachs k0 | 9 | 9 | 10 |
  | Sachs k20 Gauss | 9.50 | 9.75 | 11.10 |
  | Sachs k20 có cấu trúc | 9.55 | 12.25 | 30.00 |
  | Sachs k40 Gauss | 8.60 | 8.30 | 11.05 |
  | Sachs k40 có cấu trúc | 9.10 | 13.80 | 43.00 |
  | Wine k0 | 38 | 38 | 38 |
  | Wine k20 Gauss | 40.20 | 48.45 | 48.05 |
  | Wine k20 có cấu trúc | 21.10 | 49.25 | 48.90 |
  | Wine k40 Gauss | 41.20 | 50.95 | 50.60 |
  | Wine k40 có cấu trúc | 23.80 | 54.00 | 53.85 |

  - **Wine:** với ngưỡng giữ ở τ(k0), số cạnh tăng ở mọi điều kiện. Với ngưỡng NATIVE, số cạnh giảm khi đệm có cấu trúc (38 → khoảng 21–24), vì ngưỡng tăng nhiều hơn.
  - **Sachs:** số cạnh NATIVE trung bình gần như không đổi ở mọi điều kiện. Nhưng với đệm có cấu trúc, nhiều cặp vượt ngưỡng cố định hơn: theo FIXED, 10 → 30 ở k = 20 và 10 → 43 ở k = 40. Với ngưỡng NATIVE, flips vẫn là 3.95 và 5.90: cạnh được sắp lại, không chủ yếu mất đi.
  - Đây là mô tả trên trung bình. Phép phân rã của P-N4 (phần do điểm và phần do ngưỡng, mốc e = 0) **chưa chạy** trên P-N5.

### 3.4 Theo từng cặp: cặp có tần suất đổi ≥ 0.5

- **AVICI, Sachs:**
  - Erk–Akt đổi ở 100% lần sinh, ở cả bốn điều kiện.
  - P38–Jnk và PKC–Jnk đổi ở 65–100% lần sinh, ở cả bốn điều kiện.
  - PKC–P38 đổi ở 85–100% lần sinh ở ba điều kiện còn lại, nhưng dưới 50% ở k20 Gauss.
  - Ở k20 Gauss, chỉ 4 cặp từng đổi.
- **CDFM, Sachs:** Plcg–PIP3 đổi ở 90% lần sinh ở k20 Gauss. Với đệm có cấu trúc, 22 cặp (k = 20) và 34 cặp (k = 40) từng đổi ít nhất một lần.
- **AVICI, Wine:**
  - k20 Gauss: residual sugar–density 0.70, total sulfur dioxide–density 0.60, fixed acidity–citric acid 0.50;
  - với đệm có cấu trúc: fixed acidity–density và chlorides–alcohol đổi ở 100% lần sinh, ở cả hai k.
- **CDFM, Wine:**
  - ở k20 Gauss, 37/55 cặp từng đổi, trong đó 6 cặp có tần suất ≥ 0.5; đứng đầu là volatile acidity–chlorides với 0.95;
  - với đệm có cấu trúc, 23 cặp có tần suất ≥ 0.5 ở cả hai k.
- **PC và GES:** tối đa 2 cặp từng đổi, không cặp nào có tần suất ≥ 0.5.
- Không so cặp nào với một đồ thị tham chiếu.

### 3.5 Chênh lệch ghép cặp (mô tả; CI 95% theo t qua các lần sinh)

- **flips, đệm có cấu trúc trừ đệm Gauss:**
  - CDFM: Sachs +2.45 [+1.17, +3.73] (k = 20) và +3.40 [+1.89, +4.91] (k = 40); Wine +9.60 [+7.27, +11.93] và +8.90 [+6.65, +11.15];
  - AVICI: Sachs +1.15 [+0.80, +1.50] và −0.30 [−0.93, +0.33]; Wine −1.80 [−4.06, +0.46] và −2.25 [−3.99, −0.51].
- **flips, k = 40 trừ k = 20, đệm Gauss:** AVICI Sachs +1.45 [+0.80, +2.10]; CDFM Sachs +1.00 [+0.17, +1.83]; AVICI Wine +0.80 [−2.11, +3.71]; CDFM Wine 0.00 [−1.50, +1.50].
- **Ngưỡng, k = 40 trừ k = 20:**
  - Sachs: đệm Gauss −0.105 [−0.126, −0.084]; đệm có cấu trúc +0.027 [+0.012, +0.043].
  - Wine: đệm Gauss +0.032 [+0.015, +0.049]; đệm có cấu trúc +0.043 [+0.030, +0.056].
- GES không chạy ở k = 40 với đệm có cấu trúc, nên các chênh lệch cần điều kiện đó để trống cho GES (luật §6).

### 3.6 Timeout và hàng trùng

- **Timeout:** 0 ở mọi thuật toán, bảng và điều kiện. Mọi thống kê dùng đủ 20 lần sinh.
- **Hàng trùng của Wine** (giữ như bản phát hành):
  - trong file có 937 hàng dư sau khi loại trùng trên 11 biến dùng;
  - trong 500 hàng đã chọn có 10 hàng dư, tức 490 vector khác nhau.
- **Sachs:** không có hàng trùng.

## 4. Kiểm tra hậu nghiệm (ngoài luật; không phải căn cứ xác nhận)

Script: [`posthoc/posthoc_pn5.py`](posthoc/posthoc_pn5.py); output: [`posthoc/posthoc_output.txt`](posthoc/posthoc_output.txt). Các kiểm tra này được làm sau khi đã thấy kết quả và không thuộc luật đã khóa.

- **Kiểm tra dấu hậu nghiệm** (`binomtest`, nhị thức chính xác, một phía; bỏ các lần sinh có contrast bằng 0):
  - Sáu giả thuyết có 20/0/0: p = 9.5e-7.
  - P5-1S-C (17 dương, 3 bằng 0): p = 7.6e-6.
  - P5-2S-20 (9 dương, 11 âm): p = 0.75.
  - Holm 0.05 trên tám p-value này cho cùng mẫu hình 7/8.
  - **Cách đọc:** kiểm tra dấu hậu nghiệm cho cùng mẫu hình 7/8, bổ sung bằng chứng về tính nhất quán của hướng thay đổi. Nhãn xác nhận về trung bình vẫn dựa trên phép kiểm đã khóa.
  - **Giới hạn:**
    - Vì các lần sinh bằng 0 bị bỏ, phép này kiểm xác suất dấu dương trong các lần sinh khác 0, không trực tiếp kiểm trung bình.
    - Nó không chứng minh rằng kết luận về trung bình độc lập với xấp xỉ t.
    - Khi có giá trị bằng nhau (ties), cũng không nên diễn đạt nó đơn giản là "trung vị dương".
- **Số cạnh của AVICI,** m(có cấu trúc) − m(Gauss) trong cùng lần sinh:

  | Bảng | k = 20 [CI 95%]; +/0/− | k = 40 [CI 95%]; +/0/− |
  |---|---|---|
  | Sachs | −1.05 [−1.47, −0.63]; 1/2/17 | −0.70 [−1.25, −0.15]; 0/13/7 |
  | Wine | −5.20 [−7.30, −3.10]; 1/1/18 | −6.35 [−8.25, −4.45]; 0/2/18 |

  - Cả bốn ô cùng chiều với C3 (HA1, HA2: AVICI cho ít cạnh hơn với đệm có cấu trúc).
  - Ở Sachs, số cạnh đã gần sàn: với đệm Gauss ở k = 40, m = 0 ở 13/20 lần sinh.
- **Số cạnh NATIVE của CDFM,** cùng phép so:
  - Wine: −19.10 [−23.21, −14.99] ở k = 20 (0/0/20) và −17.40 [−20.99, −13.81] ở k = 40 (1/0/19).
  - Sachs: +0.05 [−1.74, +1.84] ở k = 20 (4/3/13) và +0.50 [−1.34, +2.34] ở k = 40 (9/4/7). Chưa thấy chiều rõ.

## 5. Không được viết

- "AVICI hay CDFM sai trên Sachs hay Wine", "PC và GES đúng hơn", hay "giảm độ chính xác". P-N5 chỉ đo độ đổi.
- "Ổn định hơn nên đúng hơn." PC và GES ít đổi không có nghĩa là đúng hơn.
- "Trên dữ liệu thật nói chung" hay "trên các bảng thật". Kết quả chỉ gồm hai bảng, một cách chọn hàng và một cách tiền xử lý.
- "20 bộ dữ liệu." Đây là 20 lần sinh đệm trên cùng một bảng cố định.
- Rằng CI hay nhãn cỡ của từng giả thuyết được Holm bảo vệ.
- Bất kỳ so sánh nào với một đồ thị tham chiếu, kể cả `GroundTruth.csv` của Sachs; không gọi một cặp đổi trạng thái là "cạnh đúng" hay "cạnh sai".
- "Ở Sachs k = 20, kiểu đệm không ảnh hưởng tới ngưỡng." NOT_CONFIRMED không chứng minh không có hiệu ứng, và CI [−0.031, +0.017] không nằm gọn trong biên ±0.03.
- "N4-b lặp lại trên dữ liệu thật" mà không kèm điều kiện. Kết quả là 3/4 ô; Sachs k = 20 không xác nhận.
- "Bộ chọn ngưỡng chi phối mức đổi trên bảng thật" (như C5). Phép phân rã của P-N4 chưa chạy trên P-N5; ở Sachs, số cạnh NATIVE gần như không đổi, trong khi số cạnh theo FIXED tăng mạnh.
- "Normal-score làm giả định của PC và GES đúng" (luật §1).
- Bất kỳ điều gì về FoundCause; model này không chạy ở P-N5.
- Dùng kiểm tra dấu ở §4 làm căn cứ cho nhãn, hay nói rằng nó chứng minh kết luận về trung bình không phụ thuộc xấp xỉ t.
- Gọi độ đổi trên bảng thật là "tác hại" hay "failure" về độ chính xác.

## 6. Ý nghĩa cho bài và bước tiếp (để user quyết)

- **Gap 2 có kết quả xác nhận, có điều kiện trên hai bảng thật đã cố định:**
  - Độ bất ổn trước việc thêm biến độc lập xuất hiện trên cả hai bảng và ở cả hai model: output trên khối thật đổi khi thêm cột độc lập. P-N5 chưa chứng minh tác hại về độ chính xác.
  - Ở điều kiện chuẩn của P-N1 (20 cột Gauss), mức đổi vượt đối chứng cổ điển đổi nhiều hơn ở từng lần sinh (P5-1, 4/4).
  - Kết quả này bổ sung cho phần "đổi output" của C1. Nó không bổ sung cho phần F1, vì không có ground truth.
- **N4-b trên bảng thật: 3/4 ô.** Bài phải ghi rõ ngoại lệ ở Sachs k = 20.
- **Hai điểm mô tả cần đưa vào bài:**
  - Trên Sachs, AVICI chỉ có 4 cạnh ở k0, và 40 cột có cấu trúc xóa cả 4 cạnh ở cả 20 lần sinh. Đây là một minh họa trực tiếp cho câu "kết luận về khối đích phụ thuộc vào biến độc lập được thêm vào", có điều kiện trên bảng này.
  - Phạm vi của C5 trên bảng thật chưa rõ. Ở Wine, ngưỡng tăng đi cùng mất nhiều cạnh NATIVE, giống dữ liệu tổng hợp. Ở Sachs, ngưỡng tăng ở k = 40 nhưng số cạnh NATIVE không giảm, vì nhiều cặp vượt ngưỡng cố định hơn.
- **Đề xuất cập nhật bảng claim** (chưa sửa; chờ user duyệt kết quả):
  - **C1:** thay câu "Chưa có kiểm tính nhất quán trên dữ liệu thật (gap 2)" bằng tham chiếu tới claim mới cho dữ liệu thật.
  - **Claim mới, P5-1:** trên hai bảng thật đã cố định, thêm 20 cột Gauss độc lập làm skeleton khối thật của AVICI và CDFM đổi nhiều hơn đối chứng cổ điển đổi nhiều hơn ở từng lần sinh. Mức: XÁC NHẬN trong phạm vi P-N5 (4/4).
  - **Claim mới, P5-2:** ngưỡng NATIVE của CDFM cao hơn khi đệm có cấu trúc so với đệm Gauss, khi khối đích là bảng thật. Mức: XÁC NHẬN ở 3/4 ô; NOT_CONFIRMED ở Sachs k = 20.
  - **C3:** thêm ghi chú mô tả hậu nghiệm: AVICI cho ít cạnh hơn với đệm có cấu trúc ở cả bốn ô của bảng thật (§4).
  - **C5:** thêm giới hạn: trên Sachs, số cạnh NATIVE không giảm dù ngưỡng tăng (mô tả); phép phân rã chưa chạy trên bảng thật.
- **Bước tiếp:**
  1. User xem kết quả. Nếu duyệt: push commit kết quả, cập nhật bảng claim, và viết phần dữ liệu thật của bản thảo trên nhánh riêng.
  2. Tùy chọn, user quyết: chạy phép phân rã của P-N4 (phần do điểm, phần do ngưỡng, mốc e = 0) trên output đã có của P-N5.
     - Không cần chạy model mới.
     - Nhãn sẽ là EXPLORATORY, vì kết quả P-N5 đã được xem.
     - Phép này giúp trả lời vì sao Sachs khác Wine.
  3. Theo thứ tự đã chốt: gap 3, so sánh cách sửa (R, FIXED, ngưỡng cục bộ, FROZEN, R-oracle). Cần luật P-N6 mới.

## 7. Đính chính diễn đạt (22/11, sau review của user)

Số liệu và tám nhãn không đổi. User đã tính độc lập từ output thô: 160 contrast, CI, t, p và nhãn Holm đều khớp. Mã băm của 15 file đóng băng và 155 phụ thuộc cũng khớp.

| # | Chỗ | Bản trước (`dab19eb`) | Sửa thành |
|---|---|---|---|
| 1 | §6 | "Failure của N1, tức output trên khối đích đổi khi thêm cột độc lập, xuất hiện trên cả hai bảng" | "Độ bất ổn trước việc thêm biến độc lập xuất hiện trên cả hai bảng". P-N5 chưa chứng minh tác hại về độ chính xác |
| 2 | §4 | Phép kiểm dấu "hỏi chiều của trung vị" và "không dựa vào xấp xỉ t" | Kiểm tra dấu hậu nghiệm cho cùng mẫu hình 7/8, bổ sung bằng chứng về tính nhất quán của hướng thay đổi; nhãn xác nhận về trung bình vẫn dựa trên phép kiểm đã khóa. Vì bỏ các lần sinh bằng 0, phép này kiểm xác suất dấu dương trong các lần sinh khác 0, không trực tiếp kiểm trung bình; khi có ties, không diễn đạt là "trung vị dương" |
| 3 | §2 và §5, đi kèm #2 | "§4 kiểm thêm bằng phép kiểm dấu" | "§4 báo thêm một kiểm tra dấu hậu nghiệm về tính nhất quán của hướng thay đổi"; §5 thêm hai câu không được viết, khớp với #1 và #2 |

## 8. Sau review: bảng claim và phân rã thăm dò (22/11)

- **Bảng claim:** user duyệt các cập nhật, giữ ranh giới bằng chứng.
  - C1 tách phần giảm F1 trên dữ liệu tổng hợp khỏi độ đổi skeleton trên bảng thật.
  - C3 có ghi chú hậu nghiệm, chỉ về số cạnh của AVICI.
  - Hai claim mới: C11 (skeleton, 4/4) và C12 (ngưỡng; Wine ở cả hai k, Sachs chỉ ở k = 40).
  - Chi tiết: [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md).
- **Phân rã thăm dò** (EXPLORATORY, không chạy model mới):
  - Theo mốc e = 0, phần do ngưỡng và phần do điểm ở Sachs k = 40 là −10.45 và +10.95; hai phần bù nhau.
  - Với mốc đảo, hai phần còn −0.45 và +0.95.
  - Wine phù hợp với mẫu hình C5 ở cả hai mốc.
  - Chi tiết: [PN5_decomposition_exploratory_vi.md](PN5_decomposition_exploratory_vi.md).
