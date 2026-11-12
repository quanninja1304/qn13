# Kết quả P-A và quyết định D1 cho hướng P17 (13/11/2026)

> **Luật đọc:** [`PA_PB_reading_rules_vi.md`](PA_PB_reading_rules_vi.md), khóa ngày 12/11. Các mục 9–28 ở §7 được ghi **trước** khi tính metric. Mã phân tích được commit trước lời gọi đầu tiên (`31afdbe`); bản sửa Q-PAIR v2 commit ở `9ef3048`, trước khi chạy lại và trước khi tính metric.
>
> **Số liệu:**
> - `PA_analysis_outputs.json` và `PA_analysis_log.txt`.
> - Câu trả lời thô nằm trong `artifacts/llm_prior_p17/llm_raw/`, không commit.
>
> **Nhãn:** [Verified-run] là số đo được; [Descriptive] là bảng RA4, không dùng để quyết định; [Inference] và [Hypothesis] chưa được kiểm.

## 1. Trạng thái chạy

| Họ | Model, kênh | Q-GRAPH đọc được | Q-PAIR v2 đọc được | Dùng cho RA1? |
|---|---|---|---|---|
| OpenAI | gpt-4.1-mini-2025-04-14, API gốc | 38/38 | 1450/1452 | Có |
| Meta | Llama 3.3 70B, OpenRouter, CoreWeave fp16 | 37/38 | 1452/1452 | Có |
| DeepSeek | V4.1-Flash-1017, OpenRouter, nhà cung cấp DeepSeek, không thinking | **28/38 (74%)** | 1450/1452 | **Không** (RA0; §7 mục 28) |

- Tổng chi phí khoảng **2.1 USD**, gồm cả lượt Q-PAIR v1 bị hỏng.
- DeepSeek từ chối đoán đồ thị khi tên biến là từ vô nghĩa ở 9–10/19 đơn vị PSEUDO; với tên thật nó trả lời đủ. Vì RA0 không đạt, ngưỡng RA1 thành **2/2** trên OpenAI và Llama.

## 2. Đọc theo luật

| Luật | OpenAI | Llama | DeepSeek (chỉ mô tả, bị loại) |
|---|---|---|---|
| **RA1:** ΔFP = FP_B − FP_N, KEEP, Q-GRAPH | **+0.005**, CI [−0.07, +0.06] | **+0.063**, CI [−0.01, +0.14] | +0.22, CI [+0.04, +0.50] |
| RA1 đạt? | Không | Không | (Có) |
| **RA2:** ΔFP(KEEP) − ΔFP(PSEUDO) | −0.07, CI [−0.37, +0.12] | −0.23, CI [−0.60, +0.12] | −0.06, CI [−0.61, +0.33] |
| RA2 đạt? | Không | Không | Không |
| **RA3:** FP_B(Q-GRAPH) − FP_B(Q-PAIR) | +0.00 | +0.08 | +0.37, CI [+0.18, +0.57] |
| RA3 | NOT FIXABLE BY ASKING | NOT FIXABLE BY ASKING | (FIXABLE) |

**Phán quyết: H-TYPE NOT CONFIRMED.**
- Không họ hợp lệ nào cho thấy LLM nối cạnh ở cặp bị confound (B) nhiều hơn rõ rệt so với cặp không liên quan (N) trong cùng một đơn vị.
- DeepSeek, họ bị loại, có chênh lệch dương. Nhưng RA2 của chính nó cũng không đạt: chênh lệch dưới tên vô nghĩa lớn ngang dưới tên thật. Vì vậy, kể cả với DeepSeek, chênh lệch không đến từ nghĩa của tên biến.

## 3. Quyết định D1 theo bảng §5 của luật đọc

| P-A | P-B | Ô của bảng |
|---|---|---|
| H-TYPE NOT CONFIRMED | NO LATENT-SPECIFIC HARM | **Đóng hướng, ghi vào sổ do-not-redo. Câu hỏi của mentor đúng toàn phần.** |

**Trả lời câu hỏi của mentor bằng số** (trong phạm vi của hai pilot):
- Chèn LLM vào FCI dưới biến ẩn **không** gặp một loại lỗi đặc thù nào khiến cách chèn "tự nhiên" trở nên sai theo cách riêng của biến ẩn.
- Về phía LLM, lỗi không tập trung ở cặp ↔ (P-A).
- Về phía FCI, lỗi đặc thù biến ẩn lan **ít** hơn lỗi đảo chiều thông thường (P-B).
- Vì vậy, vấn đề còn lại chỉ là tối ưu prior thông thường, đúng chỗ mà Guess2Graph và các bài tương tự đã chiếm.

## 4. [Descriptive] Những gì đáng giữ dù hướng đóng

1. **Tên biến mang gần hết khả năng nhận cạnh thật** [Verified-run]. Tỉ lệ cạnh trực tiếp đoán đúng chiều (TP_D) giảm mạnh khi đổi sang tên vô nghĩa ở các mạng lớn:

   | Mạng | KEEP → PSEUDO, OpenAI | KEEP → PSEUDO, Llama |
   |---|---|---|
   | alarm | 0.28 → 0.04 | 0.22 → 0.07 |
   | hailfinder | 0.22 → 0.01 | 0.09 → 0.02 |
   | insurance | 0.31 → 0.05 | 0.20 → 0.06 |
   | asia | 0.67 → 0.00 | 0.83 → 0.33 |

   Điều này khớp với một tài liệu tham khảo nội bộ và với các audit thuộc lòng bnlearn đã có; không mới.

2. **Khi không có thông tin nghĩa, mỗi model "đoán mặc định" theo một kiểu khác nhau** [Verified-run]. Với Q-PAIR dưới PSEUDO:
   - **gpt-4.1-mini trả lời "có nguyên nhân chung ẩn" (d) cho khoảng 80% mọi cặp**, bất kể loại thật. Dưới KEEP, nó chỉ trả lời (d) cho 6% số cặp D.
   - DeepSeek và Llama trả lời "không liên quan" (e) cho khoảng 80–85%.

   Gộp với P-B, nơi kiểu lỗi "→ thành ↔" (T3) là kiểu **im lặng nhất** (khoảng 60% không phát hiện được): một quy trình hỏi LLM kiểu tương thích MAG, áp lên biến ít nghĩa, có thể sinh hàng loạt lỗi T3 mà dữ liệu không bắt được. Đây là [Hypothesis] từ hai mô tả. Chưa có đo đầu cuối; luật đọc không cho phép dùng nó để cứu hướng.

3. **Dưới KEEP, model hiếm khi trả lời "confounded" ngay cả ở cặp thật sự bị confound** [Verified-run]. Tỉ lệ cặp B được trả lời (d): OpenAI 26%, DeepSeek 18%, Llama 3%. Lựa chọn phổ biến nhất ở mọi loại cặp là "gián tiếp" (c).

4. **Phát hiện phụ từ P-B:** `dag2pag` của causal-learn 0.1.4.8 không sound (79 claim sai trên 40 đồ thị). Đây là phát hiện độc lập với P17 và đáng báo cho causal-learn; user quyết định có báo hay không.

## 5. Giới hạn của phán quyết

- **Ít đơn vị:** 19 đơn vị từ 10 mạng; RA1 chỉ dùng các đơn vị có cả cặp B và cặp N, và CI bootstrap theo mạng rất rộng. "Không xác nhận" ở đây nghĩa là không thấy hiệu ứng ≥ 0.10 với độ tin cậy cần thiết. Nó **không** chứng minh hiệu ứng bằng 0: cận trên CI của Llama là +0.14.
- Một model mỗi nhà phát triển, đều là bản nhỏ hoặc trung bình. Mạng bnlearn có thể đã bị thuộc lòng.
- Q-PAIR được chạy lại (v2) sau khi v1 hỏng do thiết kế; thay đổi được ghi và commit trước khi chạy lại, và v1 không được dùng.
- Ở các mạng lớn, mức biến ẩn 25% tạo ra rất nhiều cặp B. Phân phối loại cặp vì thế khác với một ứng dụng thực tế có ít biến ẩn.
