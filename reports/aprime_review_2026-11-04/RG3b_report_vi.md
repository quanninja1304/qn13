# RG3b: T so với hộp sau whitening

> Ngày 2026-11-06. Script: `RG3b_T_vs_whitened_box.py`; số: `RG3b_outputs.json`, `RG3b_run_log.txt`. Kiểm tra lại K = 70: `RG3b_k70_recheck.py`, `RG3b_k70_recheck.json`, `RG3b_k70_recheck_log.txt`.
> **Không phải RG2 hay pilot nhân quả.** Thăm dò trên SCM tự sinh, dùng η = β thật (trường hợp tốt nhất), với họ DAG cộng tối đa một confounder. Lần chạy đầu bị hệ thống dừng vì thiếu RAM sau 8 SCM và đã chạy tiếp theo seed cố định.

## 1. Kết luận

**Theo luật khai báo trước: "không có khác biệt rõ" giữa T và hộp whitening, và ít nhất một trong hai hơn BL1.** Luật đó dẫn tới: *hình dạng χ² không cần thiết, đánh giá lại novelty trước khi đầu tư*. Không rơi vào nhánh negative-result.

| Luật | Kết quả |
|---|---|
| T hơn rõ (≥ 0.05, ±2 SE không chứa 0, ở ≥ 2/3 n) | **Không**: đạt 0/3 |
| Hộp hơn rõ | **Không**: đạt 0/3 |
| Cả hai không hơn BL1 | **Sai**: T hơn BL1 ở n = 500 và n = 1000; hộp innovated hơn BL1 ở n = 500 |
| Validity | Hộp đạt. T vượt nhẹ giới hạn size ở n = 500 (0.066 so với 0.065); FWER của T ≤ 0.001 |

**Sắc thái mà luật không thể hiện:** T nhỉnh hơn nhất quán ở K = 24 (+0.04 đến +0.06, 13–14 SCM T hơn so với 4–5 SCM hộp hơn, còn lại hòa), nhưng chưa đạt ngưỡng đã khai báo. Ở K = 70 hai bên gần như hòa. Tức T có lợi thế thật nhưng nhỏ, và có vẻ không tăng theo K.

**Khuyến nghị [Inference]: không đầu tư tiếp A′ như hướng chính, chuyển sang kiểm tra T4.** Lý do ở §5. Đây là quyết định của user.

## 2. Bước đo size (trước khi đo power)

Size lớn nhất trên các truth, 3000 replicate, mức danh nghĩa 0.05.

| Thủ tục | K | λ = 0.1 | 0.25 | 0.5 | 1 | 2 |
|---|---|---|---|---|---|---|
| Hộp innovated, n = 500 | 24 | **0.398** | 0.129 | 0.071 | 0.055 | 0.052 |
| Hộp innovated, n = 1000 | 24 | 0.240 | 0.088 | 0.067 | 0.062 | 0.061 |
| Hộp ZCA, n = 500 | 24 | 0.060 | 0.054 | 0.054 | 0.053 | 0.054 |
| Hộp innovated, n = 1000 | 70 | **0.810** | 0.343 | 0.153 | 0.084 | 0.058 |
| Hộp ZCA, n = 1000 | 70 | 0.088 | 0.060 | 0.056 | 0.056 | 0.053 |

Luật chọn cho: innovated λ = 1 (K = 24), λ = 2 (K = 70); ZCA λ = 0.1 (K = 24), λ = 0.25 (K = 70). **Hộp innovated không dùng được λ nhỏ**: sai số bậc hai trong null Σ bị nhân 1/λ (với T chỉ là 1/√λ khi tính trên căn của thống kê). Vì thế nó mất phần lớn lợi ích whitening mà ENC ở RG3 đã ngụ ý.

## 3. So sánh chính: 40 SCM mới, p = 4, K = 24

Trung bình 49–50 replicate mỗi cặp (SCM, n), tối thiểu 14. Mô hình chưa quyết định được tính là còn sống (trung bình tối đa 0.023 mô hình mỗi replicate với T), nên đây là cận dưới rất sát.

| n | T | Innovated | ZCA | BoxMaxT (không whitening) | BL1 | Size T / Innovated |
|---|---|---|---|---|---|---|
| 500 | 0.504 | 0.467 | 0.467 | 0.399 | 0.370 | 0.066 / 0.055 |
| 1000 | 0.583 | 0.525 | 0.527 | 0.517 | 0.497 | 0.055 / 0.054 |
| 2000 | 0.671 | 0.630 | 0.633 | 0.626 | 0.616 | 0.054 / 0.054 |

Chênh lệch ghép cặp theo SCM (SE):

| n | T − Innovated | T − BoxMaxT | T − BL1 | Innovated − BoxMaxT | Innovated − BL1 |
|---|---|---|---|---|---|
| 500 | +0.037 (0.018) | +0.104 (0.039) | +0.134 (0.048) | +0.067 (0.029) | +0.097 (0.040) |
| 1000 | +0.058 (0.036) | +0.066 (0.034) | +0.086 (0.038) | +0.008 (0.007) | +0.028 (0.018) |
| 2000 | +0.041 (0.016) | +0.045 (0.025) | +0.055 (0.030) | +0.004 (0.021) | +0.014 (0.024) |

**Đọc bảng:**
- **Whitening dạng hộp gần như không thêm gì so với một ngưỡng MaxT đơn giản ở n ≥ 1000.** Suy luận ở RG3 §1 rằng cơ chế nằm ở "whitening toàn vector" **không được ủng hộ** với các hộp giữ được size.
- T hơn BoxMaxT ở 17 SCM và thua ở 2–3 SCM, tức lợi thế có thật dù nhỏ. Khoảng một nửa số SCM hòa, vì mọi thủ tục cùng chứng nhận hết hoặc cùng không chứng nhận được gì.
- Khoảng cách thu hẹp khi n tăng.

## 4. Mô tả phụ

**Hai kịch bản S1** (n = 2000, h = 3). Chúng đã được chọn từ phép thử trước theo điều kiện R1 chứng nhận ≥ 0.20, nên **có thiên lệch chọn lọc về phía T**.

| Cấu trúc | Replicate | T | Innovated | ZCA | BoxMaxT | BL1 | FWER T |
|---|---|---|---|---|---|---|---|
| 0→3, 1→2 | 181 | 0.837 | 0.682 | 0.699 | 0.557 | 0 | 0.017 |
| 3→0, 3→1, 3→2, 0→2, 1→2, confounder (0,2) | 200 | 0.613 | 0.087 | 0.110 | 0.115 | 0 | 0 |

Tức có những cấu trúc mà T hơn hẳn. Chưa biết chúng phổ biến đến đâu.

**K = 70, 12 SCM p = 5 thưa, họ DAG cục bộ.** Lần chạy chính cho T = 0.28 ở n = 1000, nhưng **đó là sản phẩm của solver**: T để lại nhiều mô hình chưa quyết định. Kiểm tra lại cùng SCM và seed, giới hạn node 3000, cho cận dưới và cận trên:

| n | T (cận dưới – cận trên) | ZCA | Innovated | BoxMaxT | BL1 |
|---|---|---|---|---|---|
| 1000 | **0.425 – 0.570** | 0.565 | 0.561 | 0.521 | 0.482 |
| 5000 | **0.755** (chính xác) | 0.740 | 0.728 | 0.669 | 0.651 |

Vậy ở K = 70 **gần như hòa**. Số T của kiểm tra lại có số replicate ít hơn ở vài SCM khó (4–7 replicate do giới hạn thời gian), nên khoảng ở n = 1000 kém chắc. Các cột khác lấy từ lần chạy chính.

**Chi phí tính toán là khác biệt thật:** BoxMaxT có dạng đóng; hộp whitening cần LP nhỏ; T cần branch and bound, ở K = 70 có SCM tốn hơn 40 giây mỗi replicate mà vẫn chưa giải xong hết.

## 5. Khuyến nghị

**[Inference] Không đầu tư tiếp A′ như hướng chính; chuyển sang kiểm tra T4.** A′ không bị bác bỏ: thủ tục chạy đúng và có lợi hơn Bonferroni. Nhưng tiêu chí của dự án là một chuỗi có cơ chế mới và đóng góp đủ mạnh, và bằng chứng không đi theo hướng đó:

| Câu hỏi | Trạng thái |
|---|---|
| Có bảo đảm đúng không? | Có, có điều kiện theo η (RG1). Kỹ thuật lõi đã có trong văn liệu |
| Có hơn baseline đơn giản không? | Có, nhưng nhỏ: +0.05 đến +0.13 so với BL1, +0.05 đến +0.10 so với BoxMaxT; so với hộp whitening chưa đạt ngưỡng đã khai báo |
| Có cơ chế khoa học mới không? | Chưa thấy. Hình dạng χ² chỉ nhỉnh hơn, và không phải whitening như tôi đã đoán |
| Dùng được ở quy mô thực tế không? | Hạn chế: chi phí tăng nhanh theo K; ở p = 5 dày n* cỡ 80000 |

**Nếu muốn giữ phần giá trị đã có:** RG1 và các phép thử này đủ cho một ghi chú phương pháp ngắn về confidence-set projection cho ancestral feature, gồm cả kết quả âm về seminorm. Đây là khả năng, chưa phải đánh giá về nơi đăng.

**Những gì có thể đổi kết luận nhưng chưa làm:** ngưỡng chi-bar cho T (c̄_m ≤ ĉ_n, có thể mở rộng khoảng cách nhưng tốn 2^{|D|}), BL9 kiểu Chang, MAG đầy đủ, đo mức phổ biến của các cấu trúc ở §4. Tôi không đề xuất làm tiếp các việc này trước T4, vì chúng khó thay đổi đánh giá về novelty.

## 6. Giới hạn và minh bạch

- **Validity của hộp whitening** chỉ có lập luận phác thảo: với λ cố định, Ω̂ → Ω, s_k bị chặn dưới bởi 1/(K+λ), và max của Gaussian có phân phối liên tục, nên ngưỡng MaxT mô phỏng hội tụ; bao hàm của Thm 1 không đổi. Size được đo ở §2 nhưng chưa có người hay agent nào rà chứng minh này.
- Quick-run trước đó làm đổi hai chi tiết (N của bước size, giới hạn size theo SE), được ghi trong đầu script. Tiêu chí "T hơn rõ" không đổi. Chỉ quick-run mới thấy số trước khi chốt, 6 SCM và rất ít replicate.
- **Kết luận nhạy với ngưỡng.** 0.05 cho "rõ rệt" là lựa chọn quản lý dự án. Nếu ngưỡng là 0.03, T đạt cả hai điều kiện ở n = 500 và n = 2000 (2/3 n), tức sẽ được xếp là "T hơn rõ", trừ cờ size rất sát ở n = 500. Tôi giữ nguyên luật đã khai báo, nhưng không nên đọc "không có khác biệt rõ" thành "hai bên bằng nhau".
- Bảng đuôi và ngưỡng MaxT dùng mẫu chung (common random numbers), gây lệch cố định nhỏ.
- SCM ngẫu nhiên có phân phối trọng số do tôi chọn. Không có dữ liệu thật. Giả định Gaussian, Q cố định, biết β.
