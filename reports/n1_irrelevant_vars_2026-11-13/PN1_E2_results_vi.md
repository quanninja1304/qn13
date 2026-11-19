# Kết quả E2 của P-N1: cơ chế nào đứng sau mức hại khi thêm cột độc lập? (19/11/2026)

> **Luật đọc:** [v2](PN1_reading_rules_vi.md) cộng [v2.1](PN1_rules_v2_1_amendment_vi.md). Cách đọc tác nghiệp của E2 được ghi vào §4 của v2.1 và commit (`fde4fa4`, 19/11 12:50) **trước khi** chạy `analyze_e2.py` và xem bất kỳ metric E2 nào.
> **Phạm vi E2:** 80 hệ exploratory như E1. AVICI, CDFM, PC, GES: bốn kiểu đệm A, B, C, D × k ∈ {5, 10, 20, 30} (1 200 job mỗi thuật toán). FoundCause: lưới rút gọn đăng ký trước (A tại k ∈ {5, 10, 30}; B, C, D tại k = 20; 480 job).
> **Nhãn:** [Verified-run] cho số liệu. Mọi diễn giải về cơ chế ở §5 là **giả thuyết**. Toàn bộ là **exploratory**: 18 phép thử chữ ký (3 model × 2 estimand × M1–M3), trong đó chỉ **15 là khác nhau** vì hai estimand của AVICI trùng hệt nhau (không decoder riêng), nên không được coi là hai lần xác nhận độc lập; không kiểm soát familywise. Chỉ held-out mới xác nhận.
> **Code và output:** `artifacts/n1_runs/pn1/{integrity_e2,analyze_e2}.py` → `artifacts/n1_runs/pn1_out/{integrity_e2,e2_<model>}.json` (git-ignored).

## 1. Kiểm toàn vẹn (đều đạt)

| Kiểm | AVICI | CDFM | FoundCause | PC | GES |
|---|---|---|---|---|---|
| Job E2 đủ / thiếu / thừa | 1200 / 0 / 0 | 1200 / 0 / 0 | 480 / 0 / 0 | 1200 / 0 / 0 | 1200 / 0 / 0 |
| File hỏng, NaN, sai shape, lỗi log | 0 | 0 | 0 | 0 | 0 |
| Tổng file (DEV + E1 + E2) | 42 + 160 + 1200 | 42 + 160 + 1200 | 58 + 160 + 480 | 32 + 160 + 1200 | 32 + 160 + 1200 |
| Tổng thời gian tính | 1,3 h | 2,2 h | 54,1 h | 0,1 h | 2,2 h |

- **Mã băm input:** tạo lại toàn bộ 1 200 input bằng `assemble` và so với mã băm lưu trong từng file: khớp mọi job, mọi thuật toán. Input giống nhau giữa các thuật toán chạy cùng job (480 job có đủ 5 thuật toán, 720 job có 4).
- **Khối đích:** target_sha không đổi trong mỗi hệ và trùng với k = 0 của E1, cho 80/80 hệ và cả ba model.
- **PC và GES có ít hơn 10 file** vì DEV của mốc cổ điển không có 10 job hoán vị (equivariance chỉ kiểm cho model). Đúng theo thiết kế.
- **Thời gian bất thường:** 3 job FoundCause (65 phút, 2,9 giờ, 39 phút; median cùng d là 7 phút) do cửa sổ PowerShell bị dừng ở chế độ QuickEdit. Output không bị ảnh hưởng vì kiểm ở trên đạt. GES chạy lâu (tới 573 s) ở kiểu B, k = 30 vì khối đệm dày, như đã đo ở resource check.
- **Kiểm chéo với E1:** ô (A, k = 20) tính lại trong `analyze_e2.py` cho đúng H_NATIVE và H_FIXED của E1 ở cả ba model (đến 4 chữ số).

## 2. Chữ ký cơ chế (RN3, tại k = 20, 80 hệ)

Hiệu ghép cặp theo hệ, trung bình [CI 95%]. Dấu + nghĩa là vế đầu hại hơn. Ngưỡng: M1 CI nằm trọn ngoài ±0.03; M3 nằm trọn ngoài ±0.05; M2 ba hiệu nằm trọn trong ±0.03 và Δp_A tăng theo k.

| Model | Estimand | H_A | H_B | H_C | H_D | M1: H_A − H_B | M3: H_D − H_A | M2 | **Chữ ký đạt** |
|---|---|---|---|---|---|---|---|---|---|
| AVICI | NATIVE = FIXED | 0.075 | **0.151** | 0.077 | 0.102 | **−0.076 [−0.102, −0.051]** | +0.027 [+0.002, +0.051] | không (A−B, B−C ngoài ±0.03) | **M1, dấu −** |
| CDFM | NATIVE | 0.064 | 0.045 | 0.048 | 0.027 | +0.019 [−0.002, +0.040] | −0.036 [−0.058, −0.015] | không (CI A−B tới 0.040, A−C tới 0.036) | **không có (UNEXPLAINED)** |
| CDFM | FIXED | 0.070 | 0.056 | 0.062 | 0.033 | +0.014 [−0.000, +0.029] | −0.037 [−0.052, −0.023] | **có** | **M2** |
| FoundCause | NATIVE | 0.064 | **0.020** | 0.057 | 0.067 | +0.044 [+0.025, +0.063] | +0.003 [−0.009, +0.015] | không (A−B, B−C ngoài ±0.03) | **không có (UNEXPLAINED)** |
| FoundCause | FIXED | 0.064 | 0.020 | 0.056 | 0.066 | +0.044 [+0.026, +0.064] | +0.001 [−0.010, +0.013] | không | **không có (UNEXPLAINED)** |

Đường Δp theo k (kiểu A, median): mọi model đều không giảm và Δp(30) − Δp(5) có CI trên 0 (AVICI +0.018 [+0.014, +0.025]; CDFM +0.060 [+0.052, +0.068]; FoundCause +0.061 [+0.057, +0.067]). M4 (E1): không đạt ở CDFM và FoundCause; không áp dụng cho AVICI.

**Phán quyết theo model (exploratory):**
- **AVICI:** M1 đạt ở cả hai estimand (trùng nhau vì AVICI không có decoder riêng). Thêm khối đệm **có cấu trúc** (B) hại gấp đôi đệm Gauss độc lập (0.151 so với 0.075). Dấu ghi lại: **−** (B hại hơn A).
- **CDFM:** M2 đạt ở FIXED; NATIVE không có chữ ký. Hại gần như như nhau giữa A, B, C và tăng theo k, khớp với pattern pha loãng. Ở NATIVE, hai hiệu lọt khỏi biên ±0.03 một chút (cận trên 0.040 và 0.036), nên không đạt.
- **FoundCause:** không chữ ký nào đạt, UNEXPLAINED ở cả hai estimand. Hiệu A − B = +0.044 vượt 0 rõ, nhưng cận dưới 0.025 chưa vượt biên 0.03. Đây là **near-miss**, không được đổi nhãn.
- **M3 (phân phối đệm) không đạt ở model nào.** Ở CDFM, đệm đuôi nặng (D) lại **ít hại hơn** A (CI trọn dưới 0, chưa tới biên −0.05).

## 3. Liều lượng và mô tả (RN4)

H_NATIVE trung bình trên 80 hệ (FoundCause chỉ có các ô của lưới rút gọn):

| Kiểu, k | AVICI | CDFM | FoundCause | PC | GES |
|---|---|---|---|---|---|
| A, 5 / 10 / 20 / 30 | 0.023 / 0.042 / 0.075 / 0.100 | 0.014 / 0.036 / 0.064 / 0.093 | 0.008 / 0.017 / 0.064 / 0.095 | ≈ 0 | ≈ 0 |
| B, 5 / 10 / 20 / 30 | 0.035 / 0.085 / 0.151 / 0.199 | 0.011 / 0.014 / 0.045 / 0.054 | — / — / 0.020 / — | ≈ 0 | ≈ 0 |
| C, 5 / 10 / 20 / 30 | 0.032 / 0.048 / 0.077 / 0.116 | 0.013 / 0.019 / 0.048 / 0.066 | — / — / 0.057 / — | ≈ 0 | ≈ 0 |
| D, 5 / 10 / 20 / 30 | 0.029 / 0.044 / 0.102 / 0.133 | −0.004 / 0.015 / 0.027 / 0.056 | — / — / 0.067 / — | ≈ 0 | ≈ 0 |

- **Liều lượng:** với cả ba model, mức hại tăng gần đơn điệu theo k ở mọi kiểu đệm đã chạy. FoundCause có bước nhảy giữa k = 10 (0.017) và k = 20 (0.064).
- **Mốc cổ điển:** ở mọi (kiểu, k), CI của H_PC nằm trong [−0.004, +0.002] và của H_GES trong [−0.002, +0.009], tức **F1 gần tương đương** theo A4. Flips của PC có cận trên ≤ 0.11 cặp mỗi hệ (**output gần bất biến**); GES có cận trên ≤ 1.01 (D, k = 30), tức hơi vượt biên 1 cặp ở ô đó.
- **Hơn mốc cổ điển trên 40 hệ tuyến tính, k = 20, mô tả:** AVICI +0.10 đến +0.20 ở mọi kiểu; FoundCause +0.08 đến +0.09 ở A, C, D nhưng chỉ +0.025 [+0.000, +0.049] ở B; CDFM +0.03 đến +0.07.
- **Cạnh chéo đích ↔ đệm (FIXED, k = 20):** AVICI 0.2–7.7; CDFM 22 (B) đến 165 (A), native 0.4–71; FoundCause ≤ 0.4. FoundCause gần như không nối đệm với đích, nhưng khối đích vẫn bị hại.
- **Số cạnh dự đoán trong khối đích (thật: 23,0):** AVICI giảm từ 18,2 (k = 0) xuống 12,3 ở B, k = 20; FoundCause tăng từ 30,2 lên 33,2 ở B nhưng giảm xuống 27,4 ở A; CDFM dự đoán quá nhiều cạnh ngay từ k = 0 (59,5 ở FIXED) và tăng theo k.

## 4. Phân tách precision và recall (post hoc, không thuộc luật khóa)

Mức giảm so với k = 0, chế độ NATIVE, k = 20, trung bình [CI 95%]:

| | AVICI | CDFM | FoundCause |
|---|---|---|---|
| k = 0: precision / recall | 0.857 / 0.712 | 0.578 / 0.836 | 0.742 / 0.745 |
| A: giảm precision / recall | +0.005 / **+0.112** | **+0.074** / +0.005 | +0.012 / **+0.094** |
| B | −0.006 / **+0.202** | +0.028 / +0.079 | **+0.043** / −0.011 |
| C | +0.004 / **+0.115** | +0.048 / +0.034 | +0.004 / **+0.086** |
| D | +0.036 / **+0.123** | −0.026 / +0.099 | +0.009 / **+0.101** |

- **AVICI và FoundCause** với đệm độc lập (A, C, D): hại gần như toàn bộ đến từ **mất recall**. Model bỏ cạnh thật của khối đích chứ không bịa thêm cạnh.
- **Đệm có cấu trúc (B) đẩy hai model ngược chiều:** AVICI mất recall gấp đôi, còn FoundCause giữ nguyên recall và chỉ mất ít precision.
- **CDFM** với đệm Gauss (A): hại đến từ **mất precision**. Model thêm cạnh sai vào khối đích, khớp với việc nó nối rất nhiều cạnh sang cột Gauss.

## 5. Diễn giải (giả thuyết, chưa kiểm)

1. **H1, prior mật độ toàn bảng.** Model ước lượng "bảng này thưa đến đâu" từ toàn bộ cột. Thêm cột độc lập làm bảng trông thưa hơn, nên model hạ xác suất cạnh ở cả khối đích, dẫn đến mất recall. Giả thuyết này giải thích được FoundCause: đệm B có cạnh nên khôi phục mật độ, và recall trở lại. Nó **không** giải thích AVICI, vì AVICI hại nhiều hơn với B. Chữ ký M1 của AVICI có dấu ngược với hướng H1 dự đoán cho FoundCause.
2. **H2, ngân sách cạnh hoặc cạnh tranh chú ý (AVICI).** Nếu AVICI ngầm phân bổ một lượng "cạnh" hoặc chú ý cố định trên toàn bảng, thì khối đệm có cấu trúc thật sẽ lấy bớt phần của khối đích. Chưa có kiểm nào tách H2 khỏi các giải thích khác.
3. **CDFM** có pattern pha loãng (M2 ở FIXED) cộng với một vấn đề riêng: nối mạnh với cột Gauss. Việc D ít hại hơn A gợi ý CDFM nhạy với độ "giống Gauss" của cột thêm, nhưng M3 không đạt, nên đây chỉ là quan sát.

Ba điểm trên là cơ sở thiết kế bước sau (can thiệp vào model), **không phải kết luận**. Luật v2 §RN3 nói rõ chữ ký không phải bằng chứng cơ chế.

## 6. Đề xuất đóng băng cho held-out (cần user duyệt trước khi chạy)

Theo đề xuất mặc định đã ghi trước khi xem số (§4 v2.1, mục 6): **mọi chữ ký đạt đều đi tiếp, không chọn**. Held-out = 24 hệ (3 mỗi ô), seed theo `SETS['HELD']` trong `common.py`, adapter và số luồng như E1/E2, nối đệm sau như cũ.

| Model | Lead (đã đóng băng: dấu, estimand) | Điều kiện held-out (luôn gồm k = 0) | Lệnh gọi | Thời gian ước tính |
|---|---|---|---|---|
| AVICI | **M1**, dấu − (H_B > H_A), NATIVE = FIXED; kèm HARM và BEYOND_CLASSICAL ở A, k = 20 | A20, B20 | 72 | vài phút |
| CDFM | **M2** ở FIXED; NATIVE kiểm lại HARM ở A, k = 20 (nhãn UNEXPLAINED) | A5, A10, A20, A30, B20, C20 | 168 | khoảng 20 phút |
| FoundCause | **Không có lead** (UNEXPLAINED); chỉ kiểm lại CHANGE, HARM và BEYOND_CLASSICAL ở A, k = 20 | A20 | 48 | khoảng 4 giờ |
| PC, GES | Mốc cho mọi điều kiện trên | hợp các điều kiện | 168 mỗi thuật toán | dưới 1 giờ |

Nếu RN5 cho AVICI REPLICATED (HARM-BEYOND-CLASSICAL và M1 cùng dấu −) thì theo A9, quyết định dự án là **"GO mechanism validation"**, tức thiết kế can thiệp để tách H1 và H2. Kết quả của CDFM và FoundCause báo kèm, theo từng model.

**Một lựa chọn để user quyết (không phải mặc định):** thêm B20 cho FoundCause ở held-out (+24 lệnh gọi, khoảng 2 giờ) như một **điều kiện mô tả có nhãn post hoc**, vì near-miss A − B có ý nghĩa cho H1. Nó không được dùng để đổi nhãn UNEXPLAINED của E2, và nếu chạy phải ghi rõ là chọn sau khi đã xem E2.

## 7. Giới hạn

- Exploratory, 18 phép thử chữ ký, không kiểm soát familywise. Một chữ ký đạt (AVICI M1) và một chữ ký đạt ở một estimand (CDFM M2) có thể là may mắn; held-out quyết định.
- Ba checkpoint, một họ dữ liệu tổng hợp (ER, tuyến tính hoặc RFF, n = 500); chưa có hệ thật.
- Kiểu B chỉ khớp **ngân sách cạnh kỳ vọng** với hệ đích, không kiểm soát chính xác mật độ (A7). A so với B đổi cả "có cấu trúc" lẫn "có tương quan giữa các cột đệm"; contrast này không tách được hai thứ đó.
- Kiểu C không hoàn toàn độc lập vô điều kiện (cùng mẫu thực nghiệm).
- Mỗi (hệ, kiểu, k) chỉ có một bản rút đệm.
- Metric chính là skeleton; lỗi về hướng không được đo trong các nhãn.
