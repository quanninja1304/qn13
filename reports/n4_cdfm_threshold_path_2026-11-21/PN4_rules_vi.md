# P-N4: kiểm chứng đường ảnh hưởng qua bộ chọn ngưỡng của CDFM trên seed mới (luật v1, khóa ngày 21/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này. Commit được push trên nhánh công khai trước khi sinh bất kỳ input P-N4 nào, kể cả DEV4. v1 là bản nháp v0 (`7745a29`) cộng ba chỉnh sửa và một câu, theo duyệt của user ngày 21/11 (§11). Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §11 kèm lý do, và không được dựa trên metric đã thấy.
> **Nguồn:**
>
> - gap 1 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2;
> - [P-N3 phần A](../n3_mechanism_pilot_2026-11-21/PN3_results_vi.md) §1 (exploratory, EXP2);
> - [HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md): HC1 (§2) và phân rã mô tả (§3);
> - quyết định của user ngày 21/11: tiêu chí (c), dự đoán trực tiếp về khối chéo, đọc riêng từng k, khóa cỡ mẫu và xử lý đa giả thuyết.
>
> **Phạm vi:**
>
> - CDFM, họ RFF, đồ thị ER, n = 500, d_T ∈ {10, 20}, e_T ∈ {1, 2}.
> - k = 20: lặp lại trên seed mới. k = 40: mở rộng ra ngoài phạm vi đã có.
> - P-N4 kiểm đường ảnh hưởng qua một hàm đã biết (bộ chọn ngưỡng). Nó **không** giải thích vì sao CDFM sinh ra các thay đổi điểm, và không nói gì về AVICI hay FoundCause.

## 0. Quy trình

1. User duyệt bản nháp này. Khóa: commit và push trên nhánh công khai. Nhánh này xuất phát từ `e4d5396` và không chứa bản thảo.
2. Viết code dưới dạng file mới trong `artifacts/n4_runs/pn4/` (git-ignored).
   - Import nguyên trạng các module đã đóng băng: `common.py` (P-N1) và `common2.py` (P-N2).
   - Các hàm của bộ chọn ngưỡng được chép từ `partA_cdfm.py` (P-N3), vì file đó chạy toàn bộ phân tích ngay khi được import. Bản chép phải tái lập kết quả cũ (cổng G3, G4).
3. Chạy các cổng khả thi (§8) trên DEV4 và trên output cũ. Đóng băng code **cùng các phụ thuộc được dùng**:
   - snapshot `code/` kèm `SHA256SUMS`, gồm code mới và bản chép của `common.py`, `common2.py`;
   - mã băm của các file nguồn gói `cdfm` và của checkpoint CDFM, được cổng kiểm đối chiếu ở đầu và cuối lượt chạy.

   Commit, push.
4. Chạy P-N4. Input chỉ được sinh ra lúc chạy, sau bước 3.
5. Kiểm hoàn tất (§7), rồi mới đọc kết quả bằng code đã đóng băng.

## 1. Dữ liệu

- **Hệ:** seed = 440000 + 1000·c + r.
  - c ∈ {1, 3, 5, 7} là bốn ô RFF trong thứ tự ô của P-N1.
  - r = 0, …, 19: 20 hệ mỗi ô, **80 hệ** tổng (§6).
  - Base 440000 đã đặt chỗ trong bảng claim. Nó không trùng tập nào trước đó: P-N1 dùng 100000, 150000, 200000, 300000; P-N2 dùng 410000, 420000, 430000.
  - Hệ đích sinh bằng `target()` của P-N1, như P-N2. Hệ đích không có cạnh được thay bằng seed + 500.
- **DEV4:** chỉ dùng cho cổng, không dùng để ước lượng hiệu ứng. Base 450000, 2 hệ mỗi ô RFF, 8 hệ tổng.
- **Khối đệm:** bộ sinh lồng nhau của P-N2 (`pad_params`, `pad_graph`, `pad_data` trong `common2.py`), với s = 1, ở hai mức e = 0 và e = e_T của ô.
  - k = 20: gọi đúng `padding2` của P-N2, không đổi gì.
  - k = 40: cùng ba hàm, với tham số k = 40. Khi đó p_e = min(2e/39, 0.99).
  - Luồng ngẫu nhiên giữ khóa `SeedSequence([seed, 20261120, 2])` cho cả hai k. Vì vậy, với cùng một hệ, khối đệm k = 20 và k = 40 rút từ cùng một luồng và không độc lập với nhau. Cả hai đều độc lập với khối đích theo cách sinh.
- **Input mỗi hệ** (năm input):
  - k0;
  - k = 20 với e = 0 và với e = e_T;
  - k = 40 với e = 0 và với e = e_T.

  Tổng 400 lần chạy CDFM; DEV4 có 40 lần.
- **Model:** CDFM, gọi như P-N1 và P-N2: cùng checkpoint, `standardize=False` sau khi z-score bên ngoài, chạy trên CPU, không chạy song song với model khác. Mỗi output lưu ma trận xác suất, ngưỡng NATIVE và mã băm input.
- **Chi phí dự trù:** khoảng 1–1.5 giờ; đo lại ở cổng G7.

## 2. Định nghĩa

Với một hệ và một giá trị k:

- P⁰ và P¹ là ma trận xác suất D × D của CDFM ở e = 0 và ở e = e_T.
- Ma trận có ba nhóm phần tử:
  - khối đích: d_T × d_T;
  - khối đệm: k × k;
  - khối chéo: hai khối d_T × k và k × d_T. Mọi phần tử của khối chéo là không-cạnh theo thiết kế.
- **Ma trận lai** H(a, b, c), với a, b, c ∈ {0, 1}: khối đích lấy từ Pᵃ, khối đệm từ Pᵇ, khối chéo từ Pᶜ. Như vậy H(0, 0, 0) = P⁰ và H(1, 1, 1) = P¹.
- **thr(·):** ngưỡng NATIVE do `suggest_threshold` của CDFM tính từ một ma trận D × D, với trọng số đã lưu trong checkpoint. Ký hiệu τ⁰ = thr(P⁰) và τ¹ = thr(P¹).
- **m(A, τ):** số cặp không thứ tự {i, j} của khối đích có max(A_ij, A_ji) > τ (so sánh chặt). Đây là quy tắc NATIVE đã dùng ở P-N2 và P-N3.
- **Bộ điểm đích dùng để đếm cạnh:** Đ⁰ là khối đích của P⁰, Đ¹ là khối đích của P¹.

**Biến đo theo hệ:**

| Ký hiệu | Định nghĩa | Ý nghĩa |
|---|---|---|
| D1 | trung bình xác suất trên mọi phần tử của khối chéo, ở P¹ trừ ở P⁰ | điểm của khối chéo đổi thế nào |
| D2 | τ¹ − τ⁰ | ngưỡng NATIVE đổi thế nào (như HC1) |
| D3a | thr(H(0, 0, 1)) − τ⁰ | chỉ đổi khối chéo: ngưỡng đổi thế nào |
| D3b | m(Đ⁰, thr(H(0, 0, 1))) − m(Đ⁰, τ⁰) | chỉ đổi khối chéo: số cạnh đích đổi thế nào, **trên điểm đích ở e = 0**, tức chính khối đích của ma trận lai |
| S | m(Đ¹, τ⁰) − m(Đ⁰, τ⁰) | phần do điểm, mốc là ngưỡng ở e = 0 |
| T | m(Đ¹, τ¹) − m(Đ¹, τ⁰) | phần do ngưỡng, cùng mốc |
| T + S | m(Đ¹, τ¹) − m(Đ⁰, τ⁰) | mức đổi ròng số cạnh NATIVE |
| T − S | hiệu của hai phần | dùng cho tiêu chí (c) |

Mốc của phân rã giữ nguyên là ngưỡng ở e = 0, như luật HELD2 §4.

## 3. Giả thuyết (khóa)

Mỗi giả thuyết được đọc riêng cho từng k ∈ {20, 40}. Tổng cộng 8 giả thuyết: 4 cho k = 20 và 4 cho k = 40.

| ID | Biến đo | Dự đoán | Dạng |
|---|---|---|---|
| N4-a(k) | D1 | âm | đơn |
| N4-b(k) | D2 | dương | đơn |
| N4-x(k) | D3a, D3b | D3a dương **và** D3b âm | tổng hợp, 2 thành phần |
| N4-c(k) | T, T + S, T − S | μ_T < −1.5 **và** μ_(T+S) < 0 **và** μ_(T−S) < 0 | tổng hợp, 3 thành phần |

Ở đây μ là trung bình cân bằng theo ô của biến đo (§4).

**Diễn giải N4-c:**

- Hai điều kiện μ_(T+S) < 0 và μ_(T−S) < 0 cùng nhau tương đương μ_T < −|μ_S|. Nghĩa là đóng góp trung bình của ngưỡng mang dấu âm và lớn hơn độ lớn đóng góp trung bình của điểm.
- Điều kiện μ_T < −1.5 thêm mức ý nghĩa thực tiễn, theo biên 1.5 cạnh của P-N2.
- Kết luận áp cho trung bình, không chứng minh ngưỡng chi phối ở từng hệ.

**Diễn giải N4-x:**

- H(0, 0, 1) không phải output thật của model. Nó là input phản thực cho một hàm đã biết.
- N4-x kiểm trực tiếp rằng chỉ riêng thay đổi của khối chéo, qua bộ chọn ngưỡng, đủ làm ngưỡng tăng và làm mất cạnh đích khi điểm đích giữ nguyên.
- Nếu chỉ có N4-a, N4-b và N4-c, đường ảnh hưởng từ khối chéo vẫn chưa được xác nhận trực tiếp.

## 4. Phép kiểm (khóa)

**Cho mỗi thành phần**, với contrast theo hệ D_i trong 4 ô RFF, mỗi ô n_c = 20 hệ:

1. **Ước lượng:** θ̂ = Σ_c w_c · D̄_c, với w_c = 1/4.
2. **Sai số chuẩn theo ô thiết kế:** SE² = Σ_c a_c, với a_c = w_c² · s_c² / n_c, trong đó s_c² là phương sai mẫu trong ô (ddof = 1).
3. **Bậc tự do Welch–Satterthwaite:** df = (Σ_c a_c)² / Σ_c [a_c² / (n_c − 1)].
4. **p-value một phía,** tính bằng `scipy.stats.t.sf(t, df)`:
   - dự đoán dương: t = θ̂ / SE;
   - dự đoán âm: t = −θ̂ / SE;
   - thành phần μ_T < −1.5: t = (−1.5 − θ̂) / SE.
   - **Trường hợp suy biến SE = 0:** ghi nhãn **DEGENERATE**, dùng p = 1 trong Holm, và không xác nhận thành phần đó. Giả thuyết tổng hợp chứa thành phần đó vì vậy cũng không được xác nhận. Lý do: phương sai mẫu bằng 0 chưa chứng minh phương sai quần thể bằng 0. Quy tắc này chỉ áp cho P-N4; kết quả của các pha cũ giữ nguyên.

**Giả thuyết tổng hợp:** p của giả thuyết là giá trị lớn nhất trong các p của thành phần (kiểm intersection–union). Với N4-x: p = max(p_D3a, p_D3b). Với N4-c: p = max(p_T, p_(T+S), p_(T−S)).

**Đa giả thuyết:** Holm ở mức familywise 0.05 trên **đúng 8** p-value, gồm cả hai k:

- sắp p tăng dần: p_(1) ≤ … ≤ p_(8);
- bác bỏ H_(j) khi p_(j) ≤ 0.05 / (8 − j + 1);
- dừng ở lần không bác bỏ đầu tiên.

**Nhãn:**

- **CONFIRMED:** bị Holm bác bỏ, tức xác nhận dự đoán;
- **NOT_CONFIRMED:** không bị bác bỏ.

Không có nhãn "bác bỏ giả thuyết". Nếu θ̂ của một thành phần ngược dấu, ghi thêm "ước lượng ngược dấu".

**Khoảng tin cậy:**

- CI 95% hai phía theo t, với sai số chuẩn và df như trên.
- Tính **trực tiếp** trên từng contrast theo hệ (D1, D2, D3a, D3b, S, T, T + S, T − S) của cùng các hệ. Không cộng hay trừ đầu mút của các CI khác.

**Đọc riêng từng k:**

- Nhãn của k = 20 (lặp lại) và của k = 40 (mở rộng) được báo riêng; không gộp hai k.
- Kết quả ở k = 40 không đổi cách đọc ở k = 20, và ngược lại.

**Giả định và giới hạn của phép kiểm:**

- Đây là phép kiểm xấp xỉ mẫu lớn trên trung bình theo ô, chịu được phương sai khác nhau giữa các ô. Nó cần xấp xỉ chuẩn của các trung bình ô (n_c = 20).
- Số cạnh là rời rạc và có thể lệch, nên có thêm phép kiểm độ nhạy ở §5. Phép kiểm độ nhạy không thay quyết định Holm.

## 5. Báo cáo mô tả đi kèm (không thuộc bộ Holm)

- **Cho mọi biến đo ở §2:** θ̂, CI 95% và nhãn cỡ.
  - Biên thực tiễn: 1.5 cạnh cho số cạnh; 0.03 cho ngưỡng; 0.03 cho xác suất trung bình của một khối.
  - CI bootstrap phân tầng (lấy mẫu lại trong từng ô, 2000 lần, seed 20261122) làm kiểm độ nhạy.
  - Tách theo ô và theo d_T.
- **Theo từng hệ:** tỉ lệ hệ có T_i < −|S_i|, tỉ lệ hệ có D3b_i < 0, và tỉ lệ hệ có D2_i > 0.
- **Thiết kế 2³ đầy đủ, như P-N3 phần A:**
  - Δℓ, đóng góp Shapley của ba nhóm (đích, đệm, chéo) và tách theo đặc trưng;
  - hiệu ứng chính và tương tác;
  - số cạnh đích dưới cả 8 ma trận lai, với hai bộ điểm đích Đ⁰ và Đ¹.
- **Chỉ đổi khối đệm:** thr(H(0, 1, 0)) − τ⁰ và số cạnh tương ứng trên Đ⁰.
- **Xác suất trung bình:**
  - khối đích;
  - khối đệm, **tách cặp không-cạnh và cặp có cạnh** theo đồ thị đệm ở e_T (dạng skeleton), so trên cùng các cặp ở e = 0;
  - toàn ma trận.
- **Phân rã với mốc khác** (ngưỡng ở e_T), chỉ để cho thấy phân rã phụ thuộc mốc:
  - S′ = m(Đ¹, τ¹) − m(Đ⁰, τ¹);
  - T′ = m(Đ⁰, τ¹) − m(Đ⁰, τ⁰).
- **Chất lượng:** F1 skeleton NATIVE ở k0, e = 0 và e = e_T cho từng k; H = F1(k0) − F1(e = 0) ở k = 20 và ở k = 40.
- **So sánh hai k:** hiệu k = 40 − k = 20 của mọi biến đo ở §2, ghép cặp theo hệ. Phép so này chỉ là mô tả vì nó được chọn nằm ngoài bộ giả thuyết chính, không phải vì hai khối đệm phụ thuộc nhau. Một phép so ghép cặp vẫn có thể kiểm định nếu được thiết kế trước.
- **Không tính trong P-N4:** FROZEN, FIXED, ngưỡng cục bộ và nhánh R. Đó là phần của gap 3, có luật riêng. Output xác suất của P-N4 chỉ được gap 3 dùng lại theo luật đã khóa của gap 3.

## 6. Cỡ mẫu (khóa) và căn cứ

**Chốt 80 hệ, 20 mỗi ô.**

**Căn cứ.** Tính lại trên output đã đóng băng của HELD2 (60 hệ RFF, 15 mỗi ô) và EXP2. Đây là phép tính mô tả, chỉ để thiết kế. Hồ sơ thiết kế nằm ở [`design/`](design/):

- [`pn4_design_inputs.py`](design/pn4_design_inputs.py) → [`pn4_design_inputs.json`](design/pn4_design_inputs.json): trung bình, độ lệch chuẩn và cỡ theo ô của mọi biến đo ở §2;
- [`pn4_power.py`](design/pn4_power.py) → [`pn4_power.json`](design/pn4_power.json): power theo kịch bản.

- Phép tính tái lập đúng các số đã báo của HELD2:
  - D2 = +0.1745 [+0.1586, +0.1905], khớp HC1;
  - S = +2.30 [−0.15, +4.75];
  - T = −17.87 [−19.86, −15.87].
- Số mới, đều là mô tả trên HELD2:
  - D1 = −0.180 [−0.195, −0.166];
  - D3a = +0.115 [+0.106, +0.123];
  - D3b = −16.55 [−19.19, −13.91];
  - T + S = −15.57 [−18.30, −12.83];
  - T − S = −20.17 [−23.72, −16.61];
  - 80% số hệ có T_i < −|S_i|; 90% số hệ có D3b_i < 0.
- Trên EXP2 (20 hệ RFF), cùng phép tính cho D3a = +0.108 [+0.090, +0.126] và D3b = −13.75 [−19.75, −7.75].

**Power** của từng thành phần, kiểm một phía ở mức 0.05/8 (mức chặt nhất của Holm). Cách tính là **xấp xỉ noncentral-t**:

- SE lấy từ độ lệch chuẩn theo ô của HELD2, nhân hệ số tăng độ lệch chuẩn của kịch bản; df theo Welch–Satterthwaite;
- độ lệch của thống kê là hướng × (θ − mốc) / SE, với θ là trung bình của HELD2 nhân hệ số co hiệu ứng của kịch bản;
- cận dưới power của giả thuyết tổng hợp là 1 − Σ(1 − power của từng thành phần).

Đây là xấp xỉ dựa trên trung bình và phương sai của HELD2, cùng giả định co hiệu ứng và tăng phương sai. Nó không phải power tính trực tiếp từ toàn bộ phân phối thực nghiệm, và không bảo đảm power ở k = 40.

| Kịch bản | n mỗi ô | D3b | T (< −1.5) | T + S | T − S | D1, D2, D3a |
|---|---|---|---|---|---|---|
| Hiệu ứng như HELD2 | 15 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Hiệu ứng giảm một nửa, độ lệch chuẩn × 1.5 | 15 | 0.94 | 0.99 | 0.88 | 0.88 | 1.00 |
| Hiệu ứng giảm một nửa, độ lệch chuẩn × 1.5 | **20** | **0.99** | **1.00** | **0.96** | **0.96** | **1.00** |

- Ở k = 20, cỡ 15 mỗi ô đã đủ. k = 40 chưa có dữ liệu nào, nên kịch bản bi quan (hiệu ứng giảm một nửa, độ lệch chuẩn tăng 1.5 lần) là căn cứ chọn cỡ mẫu.
- Trong kịch bản đó, cận dưới power của N4-c là 0.748 với 15 hệ mỗi ô và 0.926 với 20 hệ mỗi ô. Của N4-x là 0.938 và 0.987. User đã tính lại cận dưới của N4-c và khớp.
- Chi phí thêm của 20 hệ so với 15 hệ khoảng 15–20 phút.

## 7. Kiểm hoàn tất trước khi đọc (khóa)

Chỉ đọc kết quả khi tất cả các điều sau đều đạt:

- đủ 400 output CDFM (80 hệ × 5 input);
- 0 job lỗi trong log;
- mã băm input của mọi output khớp input sinh lại;
- cổng đóng băng ghi `ok: true` ở cả đầu và cuối lượt, cùng commit đóng băng và cùng mã băm `SHA256SUMS`;
- khối đích trùng từng bit giữa năm input của mỗi hệ;
- ngưỡng tính lại (cổng G3) khớp ngưỡng đã lưu trên mọi output có đệm, sai lệch tuyệt đối tối đa ≤ 1e-12.

Script kiểm là một file riêng, nằm trong snapshot.

## 8. Cổng khả thi (trước khi đóng băng)

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Ở k = 20, khối đệm của code P-N4 trùng `padding2` của P-N2 trên các hệ DEV4 | trùng từng bit |
| G2 | Ở k = 40, trên DEV4: khối đệm sinh riêng trùng khối đệm trong bảng ghép; tham số như nhau giữa hai mức; đồ thị đúng là U < p_e; khớp phép tính gốc của AVICI như cổng G6 của P-N2; ghi số cạnh đệm và số nút cô lập; khối đích trùng từng bit với k0 | trùng từng bit; sai lệch tương đối ≤ 1e-9 |
| G3 | Bộ chọn ngưỡng chép lại tái tạo ngưỡng đã lưu trên output HELD2 và DEV4 | sai lệch tuyệt đối ≤ 1e-12 |
| G4 | Code đọc tái lập số cũ: HELD2 (D2, S, T, D3a, D3b như §6) và P-N3 phần A trên EXP2 (Δℓ +0.855, φ của khối chéo +0.513, số cạnh 43.8, 30.6, 35.9, 25.5, 26.5) | trùng tới số chữ số đã báo |
| G5 | Code kiểm định tái lập các giá trị **đầy đủ** của HC1 trong `held2_held2_reading.json`: θ̂, SE, df, t, CI và p. Kèm bốn ca kiểm: (i) p tổng hợp bằng giá trị lớn nhất của các thành phần; (ii) Holm dừng ở lần không bác bỏ đầu tiên, kể cả khi một p phía sau nhỏ hơn ngưỡng của nó; (iii) SE = 0 cho DEGENERATE, p = 1, không xác nhận, và giả thuyết tổng hợp chứa nó cũng không; (iv) mốc dịch tính đúng t = (−1.5 − θ̂) / SE | θ̂, SE, df, t, CI: \|Δ\| ≤ 1e-10 · max(1, \|giá trị gốc\|). p: sai số tương đối ≤ 1e-9. Bốn ca kiểm cho đúng kết quả định trước |
| G6 | CDFM tất định ở D = 50 và D = 60: chạy lại 2 input DEV4 | trùng từng bit |
| G7 | Thời gian chạy CDFM ở D = 30, 40, 50, 60; ước tính tổng | báo user trước khi chạy nếu ước tính vượt 3 giờ |
| G8 | Bộ nhớ của CDFM ở D = 60 | ghi peak RSS; dừng và báo nếu không chạy được |

Output DEV4 chỉ dùng cho các cổng này. Không tính contrast nào trên DEV4 để chỉnh luật.

## 9. Đọc kết quả

- Báo nhãn CONFIRMED hoặc NOT_CONFIRMED cho từng giả thuyết, kèm p của từng thành phần, p tổng hợp, ngưỡng Holm, θ̂, CI và nhãn cỡ.
- **Câu được viết cho từng k:**
  - "Đường ảnh hưởng từ khối chéo, qua bộ chọn ngưỡng, tới quyết định trên khối đích được xác nhận ở k" chỉ khi N4-a(k), N4-b(k) và N4-x(k) đều CONFIRMED.
  - "Theo phép phân rã lấy ngưỡng e = 0 làm mốc, phần do ngưỡng chiếm phần lớn mức đổi trung bình ở k" chỉ khi N4-c(k) CONFIRMED.
  - Hai câu này chỉ là cách đọc các giả thuyết đã kiểm, không thêm phép kiểm mới.
- **Không được viết:**
  - "cơ chế bên trong CDFM đã được xác lập";
  - "ngưỡng chi phối ở từng hệ";
  - "khối chéo luôn đóng góp nhiều nhất". Tỉ lệ số cặp chéo/đệm là 2·d_T/(k − 1), tức 0.51 hoặc 1.03 ở k = 40;
  - kết quả ở k = 40 khái quát được cho k, n hay họ đồ thị khác;
  - bất kỳ điều gì về AVICI hay FoundCause.

## 10. Ngân sách

- **CDFM:** 400 lần chạy (P-N4) và 40 lần (DEV4). Ước tính 1–1.5 giờ, đo lại ở G7.
- **Phân tích:** vài phút. Bộ chọn ngưỡng là hàm đã biết, không cần chạy lại model cho các ma trận lai.

## 11. Nhật ký (append-only sau khi khóa)

- **v0, 21/11/2026 (`7745a29`):** bản nháp, theo quyết định của user ngày 21/11 (tiêu chí (c), dự đoán trực tiếp về khối chéo, đọc riêng từng k).
- **v1, 21/11/2026 (khóa):** user duyệt thiết kế với 80 hệ và cho GO sau ba chỉnh sửa, không cần thêm vòng duyệt. Các thay đổi so với v0:
  1. **§4, SE = 0:** thay "p = 0 nếu đúng chiều" bằng DEGENERATE, p = 1 trong Holm, không xác nhận. Kết quả các pha cũ giữ nguyên.
  2. **§6, power:** lưu script và bảng đầu vào/kết quả vào `design/`. Ghi rõ đây là xấp xỉ noncentral-t từ trung bình và phương sai của HELD2, với giả định co hiệu ứng và tăng phương sai, không phải power tính từ toàn bộ phân phối thực nghiệm.
  3. **§8, G5:** đối chiếu với các giá trị đầy đủ trong `held2_held2_reading.json` theo dung sai đã khóa; p rất nhỏ dùng sai số tương đối. Thêm các ca kiểm cho p tổng hợp, bước dừng Holm và SE = 0.
  4. **Một câu ở §1 và §5:** so sánh giữa hai k là mô tả vì được chọn ngoài bộ giả thuyết chính, không phải vì hai khối đệm phụ thuộc nhau.
  5. **§0, bước 3:** đóng băng cả các phụ thuộc được dùng (theo trình tự user duyệt).
  - **Trình tự đã duyệt:** sửa luật, khóa và push, viết code, chạy G1–G8, đóng băng code cùng phụ thuộc, rồi chạy. Nếu các cổng đạt và ước tính không vượt 3 giờ thì không cần xin lại quyết định chạy.
  - **Mốc khóa:** `05b6945`, push lúc 2026-11-21T13:52:57Z (GitHub activity API).
- **Đóng băng code, 21/11/2026,** trước khi sinh bất kỳ input P-N4 nào.
  - **Code mới** trong `artifacts/n4_runs/pn4/`: `common4.py`, `selector4.py` (chép từ `partA_cdfm.py`), `stats4.py`, `measures4.py`, `run4.py`, `gates4.py`, `analyze4.py`, `completeness4.py`, `verify_freeze4.py`, `freeze4.py`, `run_pn4.sh`.
  - **Snapshot** [`code/`](code/):
    - `SHA256SUMS` có 15 file: 11 file code và 4 phụ thuộc (`common.py`, hai YAML của các ô RFF, `common2.py`). Bốn phụ thuộc khớp mã băm của snapshot P-N1 và P-N2;
    - `DEPS_SHA256.json` có 44 mã băm (nguồn gói `cdfm` và `avici`, checkpoint CDFM) cùng phiên bản gói.
  - **Cách cài đặt τ⁰, τ¹** (làm rõ, không đổi luật): dùng ngưỡng NATIVE mà CDFM lưu trong output, tức chính `suggest_threshold` của CDFM. Ngưỡng của ma trận lai dùng bản chép. G3 xác nhận hai cách trùng nhau.
  - **DEV4** (base 450000, 8 hệ, 40 lần chạy CDFM, 0 lỗi), chỉ dùng cho cổng.
  - **Cả tám cổng đạt** ([`checks/gates4.json`](checks/gates4.json)):
    - G1: 16/16 input k = 20 của đường sinh tổng quát trùng từng bit với `padding2` và `assemble2`.
    - G2: ở k = 40, trên 16 input: khối đệm sinh riêng trùng khối đệm trong bảng ghép; tham số như nhau giữa hai mức; đồ thị đúng là U < p_e; khối đích trùng từng bit. Sai lệch tương đối so với code AVICI tối đa 7.8e-15. Số cạnh đệm ở e_T là 27–50 (e = 1) và 72–98 (e = 2).
    - G3: bộ chọn ngưỡng chép lại tái tạo ngưỡng đã lưu trên 200 output (EXP2, HELD2, DEV4), sai lệch tối đa 3.3e-16.
    - G4: đạt cả 23 phép đối chiếu. Gồm: HELD2 (tám biến đo so với hồ sơ thiết kế; S và T so với `held2_held2_reading.json`); P-N3 phần A trên EXP2 (Δℓ, φ của ba nhóm, các số cạnh 43.8, 30.6, 35.9, 25.5, 26.5, S và T); số cạnh NATIVE từ ma trận kề khớp quy tắc m(A, τ).
    - G5: θ̂, SE, df, t, CI và p của HC1 trùng từng bit với giá trị đầy đủ; bốn ca kiểm cho đúng kết quả định trước.
    - G6: CDFM tất định ở D = 50 và D = 60, trùng từng bit.
    - G7: thời gian trung vị mỗi lần chạy là 2.3 s (D = 10), 4.3 s (20), 6.6 s (30), 8.6 s (40), 11.2 s (50), 13.7 s (60). Ước tính tổng 3 889 s, khoảng 1.1 giờ, dưới 3 giờ.
    - G8: bộ nhớ đỉnh 679 MB ở D = 60; RAM trống khoảng 0.94 GB lúc đo.
  - **Kiểm code đọc, không xem số:**
    - `analyze4.py --set DEV4 --smoke` chạy hết đường đọc (8 giả thuyết, Holm, phần mô tả) mà không ghi hay in giá trị contrast nào;
    - `completeness4.py --set DEV4` chạy đúng: 40 output, 0 lỗi, 0 lệch mã băm, tái tạo ngưỡng sai lệch tối đa 2.2e-16. Nó chỉ báo thiếu cổng đóng băng, đúng như dự kiến.
    - Hai tùy chọn `--smoke` (chạy hết đường đọc) và `--set DEV4` (cho kiểm hoàn tất) được thêm trước khi đóng băng, chỉ để kiểm code.
