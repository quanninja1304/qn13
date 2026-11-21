# N1: bảng claim, bằng chứng, phần còn thiếu (bước đầu của bản thảo, 21/11/2026)

> **Quyết định của user (21/11):**
>
> - **GO** viết bản thảo; dừng nhánh can thiệp V0/KO của AVICI.
> - Kỳ vọng Q1: **chưa chốt**, sẽ đánh giá novelty và mức độ khái quát sau khi dựng bản thảo.
>
> **Trọng tâm câu chuyện** (theo user):
>
> - kết luận về khối đích phụ thuộc vào các biến độc lập được thêm vào;
> - phân biệt thay đổi về điểm và thứ hạng với thay đổi do bộ chọn ngưỡng;
> - R là cách giảm tác động, có đánh đổi chất lượng, và vẫn là bằng chứng phụ.
>
> **Mức bằng chứng:**
>
> - **XÁC NHẬN:** kiểm trên dữ liệu held-out theo luật đã khóa;
> - **EXPLORATORY:** pha chọn giả thuyết;
> - **MÔ TẢ:** hậu nghiệm, hoặc không thuộc bộ kiểm;
> - **PRIOR ART:** nguồn ngoài.

## 1. Bảng claim

| # | Claim (dạng sẽ viết trong bài) | Mức | Bằng chứng chính | Phần còn thiếu, rủi ro |
|---|---|---|---|---|
| C1 | Thêm 20 cột độc lập vào một bảng có khối đích cố định làm ba mô hình causal discovery học sẵn đổi output trên khối đích và giảm F1 skeleton. Mức giảm lớn hơn của PC/GES trên cùng hệ tuyến tính | **XÁC NHẬN** (P-N1 RN5, held-out) | H tại k = 20: AVICI 0.068 [0.047, 0.091]; CDFM 0.085 [0.067, 0.104]; FoundCause 0.093 [0.052, 0.138]. BEYOND_CLASSICAL PASS ở mọi estimand. PC khoảng 0.000, GES ≤ 0.005 ([held-out P-N1](../n1_irrelevant_vars_2026-11-13/PN1_HELD_results_vi.md) §2–§3) | Phạm vi: dữ liệu tổng hợp ER, n = 500, d_T ∈ {10, 20}, k ≤ 30; mỗi model một checkpoint. FoundCause chỉ có 24 hệ. Chưa có kiểm trên dữ liệu thật |
| C2 | Mức thay đổi tăng theo số cột thêm vào | EXPLORATORY (E2), một phần XÁC NHẬN | E2: hại tăng theo k. Held-out: với CDFM, Δp(30) − Δp(5) = +0.064 [0.057, 0.074] (thành phần Δp của M2) | Không có phép kiểm xác nhận riêng cho đường liều theo k |
| C3 | Ở cùng D, đệm có cấu trúc (e = e_T) so với đệm độc lập (e = 0) làm đổi quyết định trên khối đích theo các chiều xác định | **XÁC NHẬN về dấu** (P-N2 HELD2, Holm 0.05, 5/5) | HA1: AVICI tuyến tính Δm −6.05 [−8.18, −3.92]. HA2: AVICI RFF −1.93 [−2.85, −1.02]. HC1: ngưỡng CDFM RFF +0.175 [+0.159, +0.191]. HA5: top-m0 AVICI RFF −0.027. HC4: AUROC CDFM RFF −0.014 ([HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md) §2) | Chỉ HA1 và HC1 vượt biên thực tiễn; HC4 nhỏ theo biên; HA2, HA5 UNCLEAR. Đã thấy hiệu ứng thu nhỏ từ EXP2 sang HELD2 |
| C4 | Chỉ đọc F1 có thể gây hiểu nhầm. AVICI và CDFM cùng giảm số cạnh khi đổi A → B, nhưng F1 đi ngược chiều vì điểm xuất phát khác nhau ở k0 | MÔ TẢ (P-N1 hậu nghiệm), lặp lại ở EXP2 | k0: AVICI dự đoán 17.5 cạnh, CDFM 33.0, số cạnh thật 22.4. B − A: Δm −4.9 và −10.4 ([hậu nghiệm](../n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md)) | Là điểm phương pháp. Cần giữ ở mức mô tả |
| C5 | Ở CDFM RFF, phần lớn mức giảm số cạnh NATIVE đi qua bộ chọn ngưỡng toàn bảng, không qua điểm của khối đích | MÔ TẢ trên dữ liệu XÁC NHẬN (phân rã hậu nghiệm ở HELD2), cùng XÁC NHẬN HC1 | HELD2: phần do ngưỡng −17.87 [−19.86, −15.87], phần do điểm +2.30 [−0.15, +4.75]. EXP2: −17.25 và +2.00 | Phân rã theo mốc ngưỡng ở e = 0, không phải nguyên nhân |
| C6 | Bộ chọn ngưỡng tăng ngưỡng chủ yếu qua đặc trưng `mean`, với trọng số âm. Khi đệm có cấu trúc, điểm của các cặp không-cạnh ngoài khối đích giảm; khối chéo đóng góp lớn nhất ở cấu hình này | EXPLORATORY (P-N3 phần A, EXP2) | Δℓ +0.855; Shapley khối chéo 60%, khối đệm 41%, khối đích khoảng 0. Trọng số `mean` −8.56. Xác suất trung bình: khối chéo 0.362 → 0.189, khối đệm 0.546 → 0.405 ([P-N3](../n3_mechanism_pilot_2026-11-21/PN3_results_vi.md) §1) | **Chưa kiểm trên seed mới.** Thứ hạng giữa khối chéo và khối đệm phụ thuộc cấu hình, vì tỉ lệ số cặp chéo/đệm là 2·d_T/(k − 1). Chưa giải thích vì sao CDFM cho không-cạnh điểm cao hơn khi đệm độc lập |
| C7 | Ở AVICI: số cạnh giảm rõ ở cả hai họ; ở RFF có mất thứ hạng; ở tuyến tính, thay đổi thứ hạng chưa rõ | XÁC NHẬN (HA1, HA2, HA5), MÔ TẢ (thứ hạng ở tuyến tính) | Như C3. AUROC ở tuyến tính +0.027 [+0.011, +0.044] ở HELD2, nhưng không thuộc bộ kiểm | Ở tuyến tính, không được claim chiều của thứ hạng |
| C8 | **Kết quả âm:** can thiệp attention (value zeroing, knockout, theo lớp) chưa phân biệt được cơ chế của AVICI | EXPLORATORY (P-N3 phần B) | Không có ứng viên. Các can thiệp xóa nhiều hiệu ứng nhất không đạt tiêu chí sàng lọc về chất lượng; V0-8 chỉ vừa vượt ngưỡng (−0.0313 [−0.0639, +0.0012]). KO-all là kiểm tra kỹ thuật | Báo như một giới hạn. Không được claim "attention không liên quan" |
| C9 | Một bước rẻ (sàng lọc phụ thuộc biên, rồi chạy theo thành phần) đưa các contrast trung bình xuống dưới biên. Có đánh đổi chất lượng ở một ô | MÔ TẢ (phân tích phụ ở HELD2) | Mọi REP sau R đều SMALL. Là cách sửa có ích ở 3/4 ô; với CDFM tuyến tính, giá tại k0 là −0.018 [−0.031, −0.005]. Không bất biến ở từng hệ (một hệ đổi 11 cạnh) | Không được Holm xác nhận. α_HSIC là mức danh nghĩa (đuôi gamma dễ dãi). Cần giả định đệm độc lập đúng, điều không có ở dữ liệu thật. Chưa so với cách sửa khác (MambaPFN, chính sách ngưỡng cục bộ) |
| C10 | Định vị: nguyên lý nhất quán khi đổi tập biến đã có. Đóng góp là failure cụ thể với đáp án biết trước, đường ảnh hưởng đã cô lập ở CDFM, và phạm vi của cách sửa | PRIOR ART | Self-Compatibility (AISTATS 2024); Grinsztajn (NeurIPS 2022); TabPFN (ICLR 2023 §B.3.2); Noise Immunity (2026); Aliferis 2010; CausalArena (2026, không có phép đối sánh này). [Cập nhật 21/11](N1_prior_art_update_2026-11-21_vi.md) | Chưa phải systematic review; phải lặp lại tìm kiếm trước khi gửi |

## 2. Phần còn thiếu, xếp theo ưu tiên (đề xuất, chờ user quyết)

1. **CDFM trên seed mới và một cấu hình ngoài phạm vi hiện tại** (theo ưu tiên của user). Dự đoán khóa trước:
   - (a) điểm trung bình của khối chéo giảm khi đệm có cấu trúc;
   - (b) ngưỡng NATIVE tăng;
   - (c) phần do ngưỡng chiếm phần lớn mức đổi số cạnh NATIVE trên khối đích.

   **Không** khóa "khối chéo luôn đứng đầu". Base seed là 440000. Cấu hình ngoài phạm vi chọn **một** trong ba: k = 40, n = 1000, hoặc họ đồ thị SF.
2. **Kiểm tính nhất quán trên dữ liệu thật, không cần ground truth.**
   - Thêm cột độc lập tổng hợp vào một bộ dữ liệu thật công khai, rồi đo **độ đổi** output trên khối thật: số cạnh đổi trạng thái, Δm, ngưỡng của CDFM.
   - Đáp án đúng (output không đổi) đã biết mà không cần ground truth của khối thật, nên không phải "bịa ground truth".
   - Cần user duyệt việc tải dữ liệu.
3. **So sánh cách sửa:** R, chính sách ngưỡng cục bộ của CDFM, ngưỡng cố định, và có thể chọn biến bằng PFN (MambaPFN). Mỗi cách đo cả độ đổi lẫn chất lượng tại k0.
4. **Phạm vi model:** FoundCause mới ở mức P-N1. Có thể thêm một model khác (ví dụ TabCausal) cho C1, nếu có checkpoint công khai.
5. **Gom phần thống kê:** bảng tổng hợp các pha (EXP → HELD), các luật đã khóa với mốc thời gian push, và các cổng toàn vẹn. Đây là điểm mạnh về phương pháp, có thể đưa vào appendix.

## 3. Khung bản thảo đề xuất (tiếng Anh, để duyệt trước khi viết)

1. **Introduction:** target-block conclusions of pretrained causal discovery models depend on appended, provably irrelevant variables.
2. **Related work:** consistency across variable sets (self-compatibility); robustness of tabular foundation models to uninformative features; amortized causal discovery and training priors.
3. **Setup:** an invariance test with a known required answer; models; padding families; measures that separate edge count, ranking and threshold; the locked exploratory → held-out protocol.
4. **Failure** (C1, C2).
5. **Padding structure at fixed D** (C3, C4, C7).
6. **Channels** (C5, C6, C8): CDFM's global threshold selector; what attention interventions on AVICI could and could not show.
7. **Mitigation and its scope** (C9).
8. **Limitations:** synthetic scope, two to three checkpoints, nominal HSIC level, no internal mechanism, the open real-data check.
