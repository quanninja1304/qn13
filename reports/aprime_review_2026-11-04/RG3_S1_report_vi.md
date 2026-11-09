# RG3 và S1: phép thử rẻ trước RG2

> Ngày 2026-11-05. Do user yêu cầu sau khi duyệt RG1 là PASS có điều kiện. Script: `RG3_S1_checks.py`; số: `RG3_S1_outputs.json`, `RG3_S1_run_log.txt` (6378 giây).
> **Không phải RG2 hay pilot nhân quả.** RG3 là tính bậc một trong working model; phần kiểm chứng và S1 là mô phỏng thăm dò trên SCM tự sinh. RG2 sau này phải dùng seed và SCM mới.
> Họ mô hình M: DAG trên V cộng tối đa một latent confounder. Đây là các latent projection đó, không phải mọi MAG. Q đủ bậc ≤ 2 (K = 24 ở p = 4, K = 70 ở p = 5).

## 1. Kết luận

**Theo các tiêu chí khai báo trước, A′ không bị dừng, nhưng lý do để giữ nó khác với giả định trước đây, và tín hiệu còn yếu.**

| Tiêu chí (ghi trong script trước lần chạy đầy đủ) | Kết quả |
|---|---|
| S1: có (SCM, h) với FWER_CT ≥ 0.05 + 3 SE và R1 chứng nhận ≥ 0.20 | **Đạt, nhưng hẹp:** 2 trong 761 cặp (SCM, h), đều ở h = 3 |
| Chi-square có lợi thế: ≥ 20% SCM có gain ≥ 1.25 so với box tốt nhất | **T đạt** ở mọi ô. **Hybrid không đạt ở ô nào** (gain = 1, 0% SCM) |
| Kiểm chứng: R1 hơn BL1 ≥ 0.10 ở một n nào đó, FWER đúng mức | **Đạt** ở n = 500 và n = 2000, nhưng khoảng tin cậy rộng |
| "Tín hiệu thực chất một tọa độ": trung vị ENC_range < 1.5 | **Đúng ở mọi ô** |

**Ba điều đổi so với RG1 §10:**
1. **Hybrid không có lợi thế nào:** đối thủ khó nhất gần như luôn bị bác bỏ qua phía D, nơi hybrid chính là thủ tục dạng hộp. Ưu tiên "hybrid" ở RG1 §10.1 là sai hướng.
2. **Thủ tục có tín hiệu là thống kê T trên toàn vector** (d² đến vùng R(m′) với metric ridge), kể cả ngưỡng chiếu. Dự đoán trước đó của tôi nghiêng về ngưỡng chiếu thua xa, nhưng phần bù đến từ d² lớn hơn nhiều.
3. **Cơ chế có lẽ là whitening toàn vector, không phải hình dạng χ²** [Inference]. ENC_range ≈ 1 nghĩa là một tọa độ sau whitening mang gần hết tín hiệu. Vậy một vùng tin cậy **dạng hộp sau whitening trên toàn vector** có thể ngang hoặc hơn T. **Đối thủ này chưa được đo**, và nó quyết định phần lớn câu hỏi.

> **Cập nhật 2026-11-06:** điểm 3 ở trên **không được `RG3b_report_vi.md` ủng hộ**. Với các hộp whitening giữ được size, gần như không có thêm gì so với một ngưỡng MaxT đơn giản ở n ≥ 1000, và T vẫn nhỉnh hơn chúng.

**Một mâu thuẫn tiêu chí cần nêu rõ.** Trước khi chạy, trong trao đổi với user, tôi nói nên dừng A′ "nếu đối thủ gần nhất chủ yếu khác ở một tọa độ". Script lại chỉ quy định dừng khi S1 thất bại hoặc không có lợi thế được kiểm chứng. Hai cách viết cho kết luận khác nhau: ENC_range ≈ 1 thỏa câu trong trao đổi, còn luật trong script thì không dừng. Tôi không chọn cách viết có lợi hơn: phát hiện này được chuyển thành phép thử quyết định ở §5.

## 2. RG3: cỡ mẫu cần cho power 90%

n* là cỡ mẫu cần để đạt power 90% trước đối thủ khó nhất của mỗi feature đúng Q-identifiable, tại η = β. Ô box lấy theo BL1 vì BL1, Bonferroni theo mô hình và MaxT theo khối gần như trùng nhau ở đây. Gain = n*_box / n*_T, tính trung bình theo feature trong SCM.

| p | Mật độ | Latent | SCM có feature / đã thử | Trung vị η | Trung vị n* box | Hybrid | T@ĉ | T@1df (cận lạc quan, không valid) | Tỷ lệ n* ≤ 5000: box / T | Gain T (trung vị) | SCM gain ≥ 1.25 | ENC_range | Phần d² từ null Σ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | .3 | không | 135 / 181 | 0.260 | 247 | 245 | 85 | 39 | 0.92 / 0.94 | 2.65 | 94% | 0.98 | 0.16 |
| 4 | .3 | có | 200 / 230 | 0.084 | 2130 | 2120 | 929 | 426 | 0.63 / 0.73 | 2.46 | 88% | 1.36 | 0.09 |
| 4 | .6 | không | 200 / 325 | 0.081 | 2640 | 2630 | 1500 | 688 | 0.64 / 0.68 | 1.82 | 61% | 0.98 | 0.12 |
| 4 | .6 | có | 200 / 359 | 0.053 | 5970 | 5900 | 3840 | 1760 | 0.48 / 0.53 | 1.82 | 60% | 0.99 | 0.09 |
| 5 | .3 | không | **3** / 3 | 0.105 | 1960 | 1960 | 871 | 313 | 0.74 / 0.74 | 2.20 | 100% | 0.94 | 0.33 |
| 5 | .3 | có | **3** / 3 | 0.064 | 5240 | 5230 | 1480 | 532 | 0.36 / 0.71 | 2.85 | 100% | 1.06 | 0.25 |
| 5 | .6 | không | 21 / 27 | 0.016 | 83200 | 82500 | 91300 | 32700 | 0.10 / 0.18 | 1.25 | 48% | 0.98 | 0.29 |
| 5 | .6 | có | 25 / 29 | 0.016 | 83100 | 83000 | 139800 | 50300 | 0 / 0 | 1.22 | 48% | 0.99 | 0.30 |

**Đọc bảng:**
- **Hai ô p = 5 thưa chỉ có 3 SCM**, do giới hạn thời gian 600 giây mỗi ô; không nên kết luận từ chúng.
- Ở **p = 5 dày, η ≈ 0.016 và n* cỡ 80000 trở lên với mọi thủ tục**: không thủ tục nào dùng được ở cỡ mẫu thực tế. Đây là cái giá của strong faithfulness, đúng như Uhler et al. gợi ý.
- Ở p = 4 dày, 35–44% SCM không có feature Q-identifiable nào, nên không thủ tục nào có gì để chứng nhận.
- Null Σ chỉ đóng góp 9–33% d². Tức lợi thế không chủ yếu đến từ các ràng buộc đại số giữa query.
- Trung vị T ở p = 5 dày lớn hơn box, dù trung bình gain theo SCM vẫn trên 1: gain phân tán mạnh theo feature.

## 3. Kiểm chứng trên dữ liệu Gaussian (p = 4, K = 24)

24 SCM ngẫu nhiên, 100 replicate mỗi SCM, η = β, λ = max(n^{-1/3}, 0.1). Mô hình chưa quyết định được bị tính là còn sống, nên chứng nhận của R1 là cận dưới. BL1 là đối chứng duy nhất ở đây.

| n | Chứng nhận R1 | Chứng nhận BL1 | Chênh (SE theo SCM) | SCM R1 hơn / BL1 hơn | FWER R1 | FWER BL1 |
|---|---|---|---|---|---|---|
| 200 | 0.201 | 0.154 | 0.046 (0.029) | 5 / 4 | 0.0004 | 0 |
| 500 | 0.357 | 0.233 | **0.124** (0.052) | 8 / 3 | 0 | 0 |
| 1000 | 0.514 | 0.428 | 0.085 (0.046) | 9 / 7 | 0 | 0.0008 |
| 2000 | 0.658 | 0.535 | **0.123** (0.065) | 8 / 4 | 0 | 0 |
| 5000 | 0.737 | 0.697 | 0.040 (0.041) | 7 / 8 | 0 | 0 |

**Đọc bảng:**
- Phù hợp với gain cỡ 2 lần của RG3: R1 ở n = 1000 ≈ BL1 ở n = 2000; R1 ở n = 2000 ≈ BL1 ở n = 5000 (so sánh bằng mắt, không phải ước lượng chính thức).
- **Tín hiệu yếu:** luật "ở một n nào đó" chọn trong 5 giá trị n, khoảng tin cậy rộng, và nhiều SCM hòa.
- FWER gần 0 cho thấy R1 **dùng rất ít ngân sách α**, nên ngưỡng chặt hơn có thể tăng power.
- Dùng η = β thật là **trường hợp tốt nhất**, thực tế không biết β. Con số này không phải hiệu năng của R2.
- Đối chứng là BL1, **chưa phải đối thủ valid mạnh nhất**.

## 4. S1: tìm kịch bản

Duyệt 181 cấu trúc p = 4 (DAG + tối đa một confounder, sai khác hoán vị), trọng số đều, n = 2000, h ∈ {2, 3, 4, 5, 6}; đo lại trên dữ liệu mới ở bước 2.

| h | Số cặp | FWER_CT lớn nhất | Tỷ lệ vượt α + 3 SE |
|---|---|---|---|
| 2 | 178 | 0.296 | 33% |
| 3 | 166 | 0.156 | 5% |
| 4 | 156 | 0.047 | 0% |
| 5 | 140 | 0.013 | 0% |
| 6 | 121 | 0.004 | 0% |

Có 38 ứng viên vừa có CT vượt α vừa có feature Q-identifiable. **Hai kịch bản đạt tiêu chí:**

| Cấu trúc | h | FWER_CT | Chứng nhận R1 (cận dưới) | FWER R1 | Chứng nhận BL1 | Replicate |
|---|---|---|---|---|---|---|
| 3→0, 3→1, 3→2, 0→2, 1→2, confounder (0,2) | 3 | 0.063 | **0.61** | 0 | 0 | 300 |
| 0→3, 1→2 | 3 | 0.071 | **0.83** | 0 | 0 | **42** (giới hạn thời gian) |

Các ứng viên h = 3 còn lại chứng nhận 0.03–0.14; ở h = 2 tối đa 0.01.

**Đọc bảng:**
- S1 không còn là "không có bằng chứng": R1 thực sự có power trong khi CT vượt α. Nhưng **cửa sổ rất hẹp**: chỉ ở h ≈ 3, CT vượt α chỉ nhẹ, và hai kịch bản này là kết quả tìm kiếm trên 761 cặp. Ở h ≥ 4, CT không vượt α ở cấu trúc nào trên họ này.
- Dòng 42 replicate kém chắc; kết luận dựa chủ yếu vào dòng 300 replicate.
- BL1 bằng 0 ở đây **một phần do cấu trúc**: với h = 3 < t_K = 3.08, nó không thể bác bỏ một đối thủ chỉ nhờ phía D. Điều này cho thấy R1 hoạt động được ở nơi hộp Bonferroni không thể, nhưng chưa nói gì về hộp đã whitening.
- Trọng số đều và cấu trúc được chọn có chủ đích, nên đây không phải tỷ lệ xuất hiện trong thực tế.

## 5. Khuyến nghị

**Chưa chuyển sang T4, nhưng cũng chưa chạy RG2 đầy đủ. Làm một phép thử quyết định trước:**

> **So T với vùng tin cậy dạng hộp sau whitening trên toàn vector** (cùng cấu trúc test inversion, chỉ đổi ellipsoid thành hộp đã whitening, valid theo union bound), trên 24 SCM mới và các kịch bản S1, cùng các chỉ số ở §3.

Tôi ước tính ở K = 24 hai thủ tục gần hòa; ở K = 70 hộp whitening có thể tốt hơn khoảng 25%, nhưng T có thêm phần null [Inference từ ENC_range, chưa đo].

| Kết quả | Ý nghĩa | Việc tiếp theo |
|---|---|---|
| T hơn rõ rệt | Hình dạng χ² có giá trị | RG2 với T và ngưỡng chi-bar |
| Hộp whitening ngang hoặc hơn | χ² không cần thiết; thứ có giá trị là whitening toàn vector kết hợp R_n. Đây vẫn là test inversion cổ điển với một vùng tin cậy khác | RG2 với thủ tục hộp. Novelty hẹp hơn nữa, cần đánh giá lại trước khi đầu tư |
| Cả hai không hơn BL1 khi kiểm chứng trên SCM mới | Tín hiệu ở §3 là nhiễu | Negative-result memo, chuyển T4 |

**Dù kết quả thế nào, các giới hạn sau vẫn còn:** cần β hoặc η (chỉ có bảo đảm có điều kiện theo η); ở p = 5 dày n* cỡ 80000; 35–44% SCM p = 4 dày không có feature Q-identifiable; và novelty vẫn hẹp (RG1 §9). Đánh giá của tôi [Inference]: ngay cả khi phép thử dương, đây là đóng góp hạng phương pháp/công cụ ở vùng thưa, cỡ mẫu vừa; chưa có cơ sở để kỳ vọng ICML/NeurIPS.

## 6. Giới hạn và minh bạch

- Bản quick đầu tiên cho ENC ≈ 0.06 (sai định nghĩa khi Σ suy biến) và dùng tìm kiếm cục bộ cho d². Trước lần chạy đầy đủ, tôi đã đổi sang ENC_range + frac_null, branch and bound chính xác (0/200 sai khác so với duyệt hết orthant) và thêm luật kiểm chứng. Các thay đổi này ghi trong đầu script, nhưng diễn ra **sau khi đã thấy số quick**, nên không phải pre-registration chặt.
- RG3 xét từng đối thủ riêng và bỏ qua hiệu ứng hữu hạn mẫu. T@ĉ dùng công thức xấp xỉ (√c + z_β)² hơi thuận lợi cho T.
- Tiêu chí 0.20, 1.25, 0.10 là lựa chọn quản lý dự án, không phải tiêu chuẩn thống kê.
- Mô phỏng bị giới hạn thời gian ở vài ứng viên có nhiều mô hình chưa quyết định; số replicate ghi trong JSON.
- Chưa xét: mọi MAG, p > 5, K thích nghi, dữ liệu không Gaussian, baseline Chang-style (BL9).
