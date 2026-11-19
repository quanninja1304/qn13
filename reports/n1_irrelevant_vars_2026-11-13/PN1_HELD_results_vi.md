# Kết quả held-out của P-N1 (RN5): hại có lặp lại không, cơ chế có lặp lại không? (20/11/2026)

> **Luật đọc:** [v2.2](PN1_rules_v2_2_amendment_vi.md), đóng băng ở commit `4d789de`. GitHub ghi lần push lúc 2026-11-19T07:33:36Z, trước khi chạy job held-out đầu tiên (14:47 giờ máy). Bằng chứng lưu ở `artifacts/n1_runs/pn1_out/freeze_evidence_v2_2.json`.
> **Đọc bằng code đã đóng băng:** `analyze_held.py`, không sửa gì sau khi đóng băng. Output: `artifacts/n1_runs/pn1_out/held_{avici,cdfm,foundcause}.json`, `held_decision.json`.
> **Nhãn:** [Verified-run] cho số liệu và nhãn. Diễn giải ở §4–§5 là suy luận. Các kết luận là **theo từng model và estimand**, không phải một claim đã kiểm soát familywise.

## 1. Toàn vẹn (đều đạt)

- **Job:** AVICI 240/240, CDFM 560/560, PC 560/560, GES 560/560, FoundCause 72/72; 1 992 dòng `ok`, 0 lỗi.
- **Cổng đóng băng:** đạt ở cả `held_start` (14:47) và `held_end` (23:17), cùng commit `4d789de`, cùng mã băm `SHA256SUMS` (`95cd342f…`). Working tree sạch.
- **Mã băm input:** khớp manifest ở 1 992/1 992 output. `analyze_held.py` kiểm lại điều này cho từng output nó đọc, và kiểm seed dùng thật của từng hệ. FoundCause chạy 4 luồng ở mọi job.
- **Một lỗi trong manifest của tôi, không ảnh hưởng dữ liệu.** Trường `target_sha` của manifest băm khối đích **trước** bước chuẩn hóa lại, còn runner băm khối đó **sau** khi chuẩn hóa lại (`zscore(x)`, đổi vài bit float32). Vì vậy 872 output model "lệch" trường này. Kiểm theo đúng định nghĩa của từng bên thì khớp 80/80 hệ. Mã băm input, vốn chứa trọn khối đích, khớp ở mọi output. Code đã đóng băng không dùng trường này, nên không sửa.
- **Một chỗ diễn đạt của code đã đóng băng.** `decide` in ra "NO GO on held-out". Văn bản ràng buộc là v2.2 §3.4: "không đạt GO mechanism validation; báo theo từng model; quyết định tiếp theo là của user". Báo cáo này theo văn bản luật.

## 2. Phán quyết theo từng model

| | AVICI (80 hệ) | CDFM (80 hệ) | FoundCause (24 hệ) |
|---|---|---|---|
| CHANGE tại A20 (score, graph native, graph fixed) | MEANINGFUL × 3 | MEANINGFUL × 3 | MEANINGFUL × 3 |
| HARM H_NATIVE | **0.068 [0.047, 0.091]** | **0.085 [0.067, 0.104]** | **0.093 [0.052, 0.138]** |
| HARM H_FIXED | 0.068 [0.047, 0.091] | 0.087 [0.069, 0.106] | 0.092 [0.053, 0.136] |
| BEYOND_CLASSICAL NATIVE (hệ tuyến tính) | **PASS** +0.104 [0.070, 0.136] (40) | **PASS** +0.053 [0.025, 0.076] (40) | **PASS** +0.085 [0.009, 0.169] (12) |
| BEYOND_CLASSICAL FIXED | PASS +0.104 | PASS +0.061 [0.030, 0.089] | PASS +0.084 [0.008, 0.168] |
| Lead | M1 dấu −: δ = H_A − H_B = **−0.050 [−0.074, −0.024]** | M2_FIXED: A−B **+0.034 [+0.019, +0.050]**, A−C +0.016 [+0.004, +0.029], B−C −0.018 [−0.033, −0.003]; Δp(30) − Δp(5) +0.064 [0.057, 0.074], không giảm | (không có lead) |
| Nhãn lead | **INCONCLUSIVE** (CI chứa −0.03) | **INCONCLUSIVE** (INCONCLUSIVE_H; phần Δp đạt) | — |
| **RN5** | **INCONCLUSIVE** | **INCONCLUSIVE** | — |
| Nhánh phụ B20 (NATIVE, A − B) | — | — | **SIGN_CONFIRMED** +0.073 [+0.028, +0.122]; cận dưới chưa vượt 0.03 |

**Quyết định dự án (v2.2 §3.4): không đạt điều kiện "GO mechanism validation"** vì không lead nào REPLICATED. Theo luật, quyết định tiếp theo là của user (§5).

## 3. Cái gì lặp lại, cái gì chưa

**Lặp lại trên dữ liệu mới, ở cả ba model:** thêm 20 cột độc lập vào một bảng có khối đích cố định làm cả ba checkpoint đổi kết luận về khối đích và làm F1 skeleton giảm 0.07–0.09. Mức giảm này lớn hơn của PC và GES trên cùng hệ tuyến tính: PC ≈ 0.000, GES ≤ 0.005 trên 80 hệ; trên 24 hệ của FoundCause, GES là 0.020.
- Ở CDFM, H_NATIVE lần này cũng đạt BEYOND_CLASSICAL. Ở E1, ô này là ô duy nhất trong 6 không đạt (+0.032).
- So với E1, mức hại ở held-out tương đương hoặc lớn hơn (AVICI 0.075 → 0.068; CDFM 0.064 → 0.085; FoundCause 0.064 → 0.093).

**Chưa xác lập — cơ chế:**
- **AVICI M1:** dấu lặp lại và CI loại 0: đệm có cấu trúc (B) hại hơn đệm Gauss (0.118 so với 0.068). Nhưng hiệu thu nhỏ từ −0.076 (E2) xuống −0.050, và cận trên −0.024 chưa vượt biên −0.03. Theo luật là INCONCLUSIVE, **không phải** NOT_REPLICATED. Mức thu nhỏ này đúng loại đã cảnh báo trước (lead chọn từ E2 nên ước lượng E2 có thể lạc quan).
- **CDFM M2:** phần Δp đạt (Δp tăng theo k). Phần "ba kiểu đệm hại như nhau" không đạt: A − B = +0.034 có CI loại 0, nghĩa là đệm Gauss hại hơn đệm có cấu trúc. Nhưng cận dưới 0.019 chưa vượt 0.03, nên không thành CONTRARY. Đọc trung thực: dữ liệu **nghiêng về** việc các kiểu đệm không tương đương ở CDFM, nhưng chưa đủ để bác pattern pha loãng theo biên đã khóa.
- **FoundCause:** giả thuyết sinh từ E2 (B ít hại hơn A) được xác nhận về dấu trên 24 hệ mới. Đây là nhánh phụ chọn sau E2, nên không đổi nhãn UNEXPLAINED của E2.

## 4. Mô tả: một pattern lặp lại về dấu (không phải nhãn)

Hiệu H_A20 − H_B20 (NATIVE), E2 → held-out:

| Model | E2 (80 hệ) | Held-out | Chiều |
|---|---|---|---|
| AVICI | −0.076 [−0.102, −0.051] | −0.050 [−0.074, −0.024] | đệm có cấu trúc hại **hơn** |
| CDFM | +0.019 [−0.002, +0.040] | +0.036 [+0.015, +0.057] | đệm có cấu trúc hại **kém** |
| FoundCause | +0.044 [+0.025, +0.063] | +0.073 [+0.028, +0.122] | đệm có cấu trúc hại **kém** |

Thay đổi so với k = 0 (NATIVE, trung bình mỗi hệ, held-out):

| | A20: ΔTP / ΔFP / Δrecall / Δprecision | B20: ΔTP / ΔFP / Δrecall / Δprecision |
|---|---|---|
| AVICI | −1.65 / +1.18 / −0.081 / −0.038 | −3.96 / −1.41 / −0.176 / +0.024 |
| CDFM | −0.25 / **+7.30** / −0.003 / −0.101 | −2.46 / −0.91 / −0.100 / −0.020 |
| FoundCause | −3.33 / −0.88 / **−0.137** / −0.004 | +0.21 / +1.83 / +0.001 / −0.040 |

- **FoundCause:** đệm độc lập làm mất recall; đệm có cấu trúc trả lại recall nhưng thêm cạnh sai. Lặp lại pattern của E2.
- **CDFM:** đệm Gauss làm tăng cạnh sai (mất precision); đệm có cấu trúc làm mất cạnh thật. Lặp lại pattern của E2. Mức giảm F1 giống nhau che hai hành vi khác nhau.
- **AVICI:** đệm có cấu trúc làm mất recall mạnh, như E2. Ở đệm Gauss, held-out cho thấy **cả** mất recall **lẫn** thêm cạnh sai (ΔFP +1.18; ở E2 là −0.46). Vì vậy câu "hại của AVICI chủ yếu là mất recall" chỉ đúng cho đệm có cấu trúc; với đệm Gauss phải sửa lại.
- Chiều của hiệu A − B ở held-out trùng E2 ở cả ba model. Đây là mô tả hậu nghiệm cho hai model không có lead về dấu (CDFM, FoundCause ngoài nhánh phụ), nên **không** được coi là bằng chứng xác nhận.

## 5. Ý nghĩa và các lựa chọn cho user

**Điều có thể nói** (trong phạm vi: ba checkpoint, dữ liệu tổng hợp ER tuyến tính và RFF, n = 500, d_T ∈ {10, 20}): ở cả ba model, hại do cột độc lập đã lặp lại trên held-out, lớn hơn mốc cổ điển, và tăng theo k (E2). **Cơ chế chưa xác lập** ở model nào: hai lead INCONCLUSIVE, và ba model phản ứng với đệm có cấu trúc theo hai chiều ngược nhau.

**Không được nói:**
- "đã xác nhận prior mật độ" hay "đã xác nhận pha loãng";
- "mọi mô hình học sẵn đều bị";
- "đây là lần đầu thêm biến không liên quan vào causal discovery" (Aliferis et al. 2010 đã làm cho local causal discovery);
- đổi biên hoặc thêm seed để biến INCONCLUSIVE thành REPLICATED.

**Lựa chọn:**

1. **Dừng N1 ở mức phát hiện đã lặp lại.** Hồ sơ hiện có đủ cho một báo cáo kỹ thuật. Một bài Q1 thì còn thiếu cơ chế, và cần kiểm lại prior art: gap statement của N1 mới ở mức "đủ để pilot, chưa đủ để claim ưu thế xuất bản" ([đối sánh audit](N1_audit_reconciliation_vi.md) §1).
2. **Mở một nghiên cứu cơ chế mới, có luật riêng và held-out riêng** (không phải cứu nhãn INCONCLUSIVE). Câu hỏi được lựa chọn này mở ra: vì sao cùng một khối đệm có cấu trúc làm AVICI tệ hơn mà làm FoundCause và CDFM đỡ hơn. Đòn bẩy sạch và rẻ:
   - giữ k cố định, thay **số cạnh trong khối đệm** (0 → mật độ của hệ đích → dày hơn): kiểm trực tiếp giả thuyết "model ước lượng mật độ từ toàn bảng";
   - giữ cấu trúc, thay **tương quan biên** giữa các cột đệm: tách "có cạnh" khỏi "có tương quan".

   AVICI và CDFM chạy vài phút đến một giờ; FoundCause là phần tốn kém (vài giờ cho mỗi 24 hệ × điều kiện).
3. **Chuyển sang C1** (backup), giữ N1 như một phát hiện phụ.

**Khuyến nghị của tôi: 2, kèm kiểm lại prior art song song.**
- Hiện tượng đã đủ bền (ba model, held-out, vượt mốc cổ điển); phần thiếu cho một bài theo kiểu "phát hiện + cơ chế + audit" là câu trả lời cho "vì sao".
- Sự trái chiều giữa các model với đệm có cấu trúc là một câu "vì sao" cụ thể, đo được bằng đòn bẩy mình kiểm soát hoàn toàn.
- **Điều kiện dừng đề xuất:** nếu pilot mật độ đệm ở AVICI và CDFM, chạy trên tập exploratory mới, không cho đường liều–đáp ứng rõ theo số cạnh đệm (hiệu < 0.03 trên toàn dải), thì giả thuyết mật độ bị loại cho hai model đó. Khi đó N1 nên dừng ở lựa chọn 1.
- Trước khi viết luật cho pilot đó, cần một lượt prior art tập trung vào "amortized / foundation causal discovery + irrelevant hoặc independent variables". Không viết bài cho đến khi lượt này xong.

## 6. Giới hạn

- FoundCause chỉ có 24 hệ (12 tuyến tính): CI của BEYOND_CLASSICAL rộng (+0.085 [+0.009, +0.169]).
- Một họ dữ liệu tổng hợp; một bản rút đệm mỗi (hệ, kiểu, k); metric chính là skeleton.
- Kiểu B khớp ngân sách cạnh kỳ vọng, không khớp chính xác mật độ; A so với B đổi cùng lúc "có cạnh" và "có tương quan giữa cột đệm".
- Không kiểm soát familywise. Ở held-out có 2 lead + 1 nhánh phụ + 12 phép kiểm lại HARM và BEYOND_CLASSICAL.
