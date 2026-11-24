# N1: bảng claim, bằng chứng, phần còn thiếu (bước đầu của bản thảo, 21/11/2026)

> **Quyết định của user (21/11, lượt 1):**
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
> **Quyết định của user (21/11, lượt 2):**
>
> - **GO viết bản thảo ngay.** Gap 1 là kiểm chứng bổ sung trước khi chốt bài; không chờ gap 1 xong mới viết.
> - **Thứ tự khoa học:** gap 1 → dữ liệu thật → so sánh cách sửa → thêm model.
> - **Gom thống kê trong lúc viết:** mỗi bảng ghi bộ dữ liệu, giả thuyết đã khóa, phép kiểm và mức bằng chứng.
> - Bản sửa này chỉ đổi cách viết claim và kế hoạch; **số liệu không đổi**. Nhật ký ở §4.
>
> **Quyết định của user (21/11, lượt 3):**
>
> - Bản thảo chưa công khai. Nhánh công khai cho luật mới xuất phát từ `e4d5396`.
> - Đồng ý tiêu chí (c), theo cách hiểu chính xác ghi ở gap 1.
> - GO viết luật gap 1, kèm giả thuyết trực tiếp về khối chéo.
>
> **Quyết định của user (22/11, lượt 4):**
>
> - Duyệt kết quả P-N4. User đã tính lại các contrast chính, CI, p-value và Holm, và kết quả khớp.
> - Cập nhật C5 và tách C6 thành C6a (xác nhận) và C6b (mô tả). Nhãn cũ của EXP2 và HELD2 không đổi.
> - Chuyển sang gap 2 với hai bảng thật: Sachs CD3/CD28 và Wine trắng. Đồng ý tải về.
>
> **Quyết định của user (22/11, lượt 5):**
>
> - Duyệt kết quả P-N5. User đã tính độc lập từ output thô: 160 contrast, CI, t, p và nhãn Holm đều khớp; mã băm của 15 file đóng băng và 155 phụ thuộc cũng khớp. Push kết quả cùng commit đính chính diễn đạt (`2f668b3`).
> - Cập nhật C1, C3 và C5; thêm C11 (skeleton trên bảng thật) và C12 (ngưỡng CDFM trên bảng thật), giữ ranh giới bằng chứng.
> - Bổ sung phân rã thăm dò trên output có sẵn của P-N5, không chạy model mới. Sau đó chuyển sang luật P-N6 (gap 3).
>
> **Quyết định của user (22/11, lượt 6):**
>
> - Duyệt kết quả P-N6 và **đóng gap 3**. User đã tái tính sáu phép kiểm, CI và nhãn 5/6, và xác nhận các kiểm tra 320/320 và 572/572 cùng mã băm của 23 file đóng băng và 54 phụ thuộc. Push kết quả (`2f013d6`) cùng một commit đính chính.
> - Thêm C13–C15 theo cách viết của user. C9 giữ nhãn cũ và dẫn sang các claim mới.
> - Chưa làm phép kiểm kết hợp Fisher-z và HSIC, để giữ phạm vi bài; ứng viên chưa bị bác bỏ.
> - **Bước tiếp:**
>   - hoàn thiện bản thảo trước khi mở nghiên cứu mới: viết §8, ghép bản thảo đầy đủ, rà xem claim nào còn thiếu bằng chứng;
>   - GO cho thiết kế thu gọn của gap 4, nếu việc thêm model kiểm được một claim cụ thể; đo ngân sách trước lượt chạy chính; gap 4 không chặn việc viết;
>   - nghiên cứu ngưỡng theo thành phần là hướng tiếp nối, chưa mở thành pha mới.
>
> **Quyết định của user (23/11, lượt 8):**
>
> - Duyệt kết quả P-N7 và **đóng gap 4**. User đã tính lại từ output thô: 40 contrast, CI, p-value và nhãn Holm đều khớp; mã băm code và phụ thuộc cũng đạt. Push `8d05651` và `b53ca72` (2026-11-23T00:55:44Z, GitHub activity API).
> - Kết quả giữ nguyên: Wine CONFIRMED, Sachs NOT_CONFIRMED. Sachs giúp xác định giới hạn của phát hiện. Không mở thêm thí nghiệm cho gap này.
> - `b53ca72` công bố bổ sung ba run header (Study 1 held-out, EXP2, HELD2), cùng nội dung với bản gốc (Git lưu với kết thúc dòng LF; bản checkout trên Windows trùng từng byte). Đây là nhật ký máy được công bố bổ sung: lần push này **không** tạo bằng chứng thời gian bên ngoài cho các lượt chạy trước đó.
> - Cập nhật C11 theo câu của user.
> - **Bước tiếp:** bản thảo v0.6 và S1–S3 trên nhánh riêng, rồi rà số liệu, claim và hình một lượt cuối. Phần thí nghiệm bắt buộc ở phạm vi hiện tại đã đủ.
>
> **Quyết định của user (23/11, Study 7):**
>
> - Duyệt kết quả P-N8 (SEA) và đưa Study 7 vào bài. User đã tính lại Δ từ output `.npz`, các phép kiểm và hạng Holm: khớp, sai khác số học tối đa khoảng 1.4 × 10⁻¹⁴. Log có đủ 1090 job `ok`; ba file kiểm trùng từng byte với bản trong `artifacts/`.
> - Thêm C16 riêng theo câu của user; không nhập vào C1 hay C11. Kết quả bổ sung bằng chứng cho một pipeline tổng hợp trên tập con; chưa xác định thêm cơ chế.
> - Push `86d39fe`, `bb4658e` và commit đính chính `6586ce0` (2026-11-23T16:47:33Z, GitHub activity API).
> - Đóng phần mở rộng SEA. Pattern của ô c2 và của độ phủ đưa vào phần thảo luận; không mở thêm lượt thí nghiệm.
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
| C1 | **Trên dữ liệu tổng hợp,** thêm 20 cột độc lập vào một bảng có khối đích cố định làm ba mô hình causal discovery học sẵn đổi output trên khối đích và giảm F1 skeleton. Mức giảm lớn hơn của PC/GES trên cùng hệ tuyến tính | **XÁC NHẬN** (P-N1 RN5, held-out) | H tại k = 20: AVICI 0.068 [0.047, 0.091]; CDFM 0.085 [0.067, 0.104]; FoundCause 0.093 [0.052, 0.138]. BEYOND_CLASSICAL PASS ở mọi estimand. Trên hệ tuyến tính, nơi đối chứng đúng giả định: PC 0.000; GES 0.009 trên 40 hệ, 0.034 trên 12 hệ của FoundCause ([held-out P-N1](../n1_irrelevant_vars_2026-11-13/PN1_HELD_results_vi.md) §2–§3; số theo hệ tuyến tính tính lại từ `held_*.json`) | Phạm vi: dữ liệu tổng hợp ER, n = 500, d_T ∈ {10, 20}, k ≤ 30; mỗi model một checkpoint. FoundCause chỉ có 24 hệ. **Phần giảm F1 chỉ có trên dữ liệu tổng hợp.** Trên hai bảng thật, P-N5 chỉ xác nhận độ đổi skeleton của AVICI và CDFM, không đo chất lượng: xem C11, và C12 cho ngưỡng CDFM |
| C2 | Ở pha exploratory, mức hại tăng theo số cột thêm vào ở cả ba model. Ở held-out chỉ có kết quả hai đầu cho CDFM | EXPLORATORY (P-N1 E2); held-out chỉ có kết quả hai đầu của CDFM | E2, kiểu A, H_NATIVE ở k = 5 / 10 / 20 / 30: AVICI 0.023 / 0.042 / 0.075 / 0.100; CDFM 0.014 / 0.036 / 0.064 / 0.093; FoundCause 0.008 / 0.017 / 0.064 / 0.095 ([E2](../n1_irrelevant_vars_2026-11-13/PN1_E2_results_vi.md) §3). Held-out, CDFM, kiểu A, 80 hệ: median theo hệ của Δp(30) − Δp(5) = +0.064 [0.057, 0.074], với Δp là trung bình \|p(k) − p(k0)\| trên các cặp của khối đích (phần Δp của M2) | Kết quả hai đầu **không chứng minh** tăng đơn điệu. Điều kiện "median Δp không giảm qua k = 5, 10, 20, 30" của luật M2 chỉ xét ước lượng điểm, không phải phép kiểm. Held-out không kiểm H theo k, và chỉ có CDFM. Claim rộng giữ ở mức exploratory |
| C3 | Ở cùng D, đệm có cấu trúc (e = e_T) so với đệm độc lập (e = 0) làm đổi quyết định trên khối đích theo các chiều xác định | **XÁC NHẬN về dấu** (P-N2 HELD2, Holm 0.05, 5/5) | HA1: AVICI tuyến tính Δm −6.05 [−8.18, −3.92]. HA2: AVICI RFF −1.93 [−2.85, −1.02]. HC1: ngưỡng CDFM RFF +0.175 [+0.159, +0.191]. HA5: top-m0 AVICI RFF −0.027. HC4: AUROC CDFM RFF −0.014 ([HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md) §2). **P-N5, hậu nghiệm** (mô tả, ngoài bộ kiểm): trên hai bảng thật, số cạnh của AVICI với đệm có cấu trúc thấp hơn với đệm Gauss ở cả bốn ô (k = 20 và 40): Sachs −1.05 [−1.47, −0.63] và −0.70 [−1.25, −0.15]; Wine −5.20 [−7.30, −3.10] và −6.35 [−8.25, −4.45]. Cùng chiều HA1/HA2 ([P-N5](../n5_real_data_consistency_2026-11-22/PN5_results_vi.md) §4) | Chỉ HA1 và HC1 vượt biên thực tiễn; HC4 nhỏ theo biên; HA2, HA5 UNCLEAR. Đã thấy hiệu ứng thu nhỏ từ EXP2 sang HELD2. P-N5 không kiểm lại năm giả thuyết của C3; ghi chú hậu nghiệm chỉ nói về số cạnh của AVICI. Ở Sachs, số cạnh của AVICI đã gần sàn |
| C4 | Chỉ đọc F1 có thể gây hiểu nhầm. Khi đổi A → B, AVICI và CDFM cùng dự đoán ít cạnh hơn, nhưng F1 đi ngược chiều. AVICI bỏ cạnh đúng và cạnh sai với số lượng gần nhau, và F1 giảm; CDFM bỏ chủ yếu cạnh sai, và F1 tăng | MÔ TẢ (P-N1 hậu nghiệm); cùng chiều ở HELD2 (mô tả, ngoài bộ Holm) | P-N1 held-out, B − A, NATIVE, 80 hệ: AVICI ΔTP −2.31 [−2.95, −1.67], ΔFP −2.59 [−3.98, −1.45] (Δm −4.9), ΔF1 −0.050 [−0.074, −0.024]; CDFM ΔTP −2.21 [−3.15, −1.22], ΔFP −8.21 [−11.93, −4.81] (Δm −10.4), ΔF1 +0.036 [+0.015, +0.057]. CI của ΔTP, ΔFP: bootstrap ghép cặp của P-N1 (2000 lần, seed 20261114) trên các hàng theo hệ của `held_*.json`; user tính, agent tái lập khớp; mô tả, chưa hiệu chỉnh đa kiểm định. Phân rã theo mốc m0: phần thứ hạng AVICI +0.008 [−0.014, +0.031], CDFM −0.026 [−0.041, −0.012]; phần số cạnh, lấy hiệu, khoảng −0.058 và +0.061 (sai số làm tròn ±0.001) ([hậu nghiệm](../n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md) Bảng 1–2). HELD2, REP: AVICI tuyến tính TP −2.45, FP −3.60, F1 −0.049; CDFM RFF TP −3.33, FP −12.23, F1 +0.030 | Phân rã là kế toán theo mốc m0, không phải nguyên nhân. Riêng số cạnh ở k0 (AVICI 17.5, CDFM 33.0, cạnh thật 22.4) **không đủ** giải thích chiều của F1: chiều này phụ thuộc vào việc cạnh bị bỏ là cạnh đúng hay cạnh sai. Không quy nguyên nhân chỉ cho việc dự đoán thiếu hay thừa |
| C5 | Ở CDFM RFF, **theo phép phân rã lấy ngưỡng e = 0 làm mốc**, ở cả k = 20 và k = 40: đóng góp trung bình của ngưỡng mang dấu âm, vượt 1.5 cạnh, và lớn hơn độ lớn đóng góp trung bình của điểm | **XÁC NHẬN trong phạm vi P-N4** (N4-c, Holm 0.05 trên 8 giả thuyết). HELD2 và EXP2 giữ nhãn MÔ TẢ cũ. Trên hai bảng thật (P-N5): EXPLORATORY | P-N4, 80 hệ mới. k = 20: T −19.24 [−22.01, −16.46], T + S −19.36 [−23.52, −15.20], T − S −19.11 [−22.84, −15.39]. k = 40: T −26.04 [−29.47, −22.61], T + S −20.73 [−24.24, −17.21], T − S −31.35 [−36.55, −26.15] ([P-N4](../n4_cdfm_threshold_path_2026-11-21/PN4_results_vi.md) §2). HELD2, mô tả: phần do ngưỡng −17.87 [−19.86, −15.87], phần do điểm +2.30 [−0.15, +4.75]. **P-N5, EXPLORATORY** (tính sau khi xem kết quả; mốc e = 0; đếm trên 55 cặp của khối thật): Wine T −19.70 [−21.58, −17.82], S +0.60 (k = 20) và T −23.85 [−26.25, −21.45], S +6.45 (k = 40), khớp mẫu hình (c); Sachs k = 40 T −10.45 [−13.96, −6.94], S +10.95 [+7.28, +14.62], T + S +0.50, tức hai phần bù nhau; Sachs k = 20 T +0.55, S −0.50. Mốc đảo: Sachs k = 40 T′ −0.45, S′ +0.95; Wine T′ −19.45 và −21.60 ([phân rã thăm dò](../n5_real_data_consistency_2026-11-22/PN5_decomposition_exploratory_vi.md)) | Kết luận về trung bình, không về từng hệ: phần do ngưỡng vượt phần do điểm ở 81% (k = 20) và 89% (k = 40) số hệ. Phụ thuộc mốc: với mốc là ngưỡng ở e_T, phần do điểm là +5.38 ở k = 20 (mô tả). Phân rã không phải nguyên nhân. Phạm vi: CDFM, RFF, ER, n = 500, k ∈ {20, 40}. **Phạm vi xác nhận của P-N4 giữ nguyên.** Trên bảng thật chỉ có kết quả EXPLORATORY: phân rã kế toán phụ thuộc mốc, chưa phải hai nguyên nhân tách biệt. Ở Sachs k = 40, số cạnh gần như giữ nguyên không có nghĩa ngưỡng ít ảnh hưởng, và kết quả phụ thuộc mạnh vào mốc |
| C6a | **Đường ảnh hưởng qua khối chéo:** thay riêng khối chéo (lấy từ e_T đưa vào ma trận e = 0), giữ cố định điểm đích và khối đệm, đủ làm ngưỡng NATIVE tăng và số cạnh đích giảm. Đi cùng là điểm của khối chéo giảm và ngưỡng NATIVE tăng | **XÁC NHẬN trong phạm vi P-N4** (N4-a, N4-b, N4-x, Holm 0.05). P-N3 phần A giữ nhãn EXPLORATORY | k = 20: D1 −0.190 [−0.200, −0.181], D2 +0.193 [+0.180, +0.205], D3a +0.126 [+0.120, +0.132], D3b −18.63 [−22.31, −14.94]. k = 40: D1 −0.161, D2 +0.227, D3a +0.089, D3b −16.10 [−18.95, −13.25] ([P-N4](../n4_cdfm_threshold_path_2026-11-21/PN4_results_vi.md) §2) | Ma trận lai là input phản thực cho một hàm đã biết, không phải output thật của model. Đây là một đường ảnh hưởng tính toán qua bộ chọn ngưỡng; nó không giải thích vì sao model sinh ra các thay đổi điểm |
| C6b | **Phân bổ đóng góp:** nhóm dẫn đầu đổi theo k (k = 20: khối chéo 57%, khối đệm 44%; k = 40: khối đệm 65%, khối chéo 31%). Điểm của các cặp không-cạnh trong khối đệm giảm (0.553 → 0.344 ở k = 20; 0.529 → 0.312 ở k = 40); điểm của các cặp có cạnh tăng (0.554 → 0.639; 0.529 → 0.636). Ngưỡng tăng chủ yếu qua đặc trưng `mean`, với trọng số −8.56 | MÔ TẢ (P-N4, ngoài bộ Holm). P-N3 phần A (EXP2: khối chéo 60%, khối đệm 41%) giữ nhãn EXPLORATORY | Shapley và trung bình theo khối ([P-N4](../n4_cdfm_threshold_path_2026-11-21/PN4_results_vi.md) §3.3–§3.4) | Việc đổi nhóm dẫn đầu phù hợp với thay đổi của tỉ lệ số cặp chéo/đệm, 2·d_T/(k − 1), nhưng chưa chứng minh số lượng cặp là nguyên nhân duy nhất. Không thuộc bộ Holm. Chưa giải thích vì sao CDFM cho các cặp không-cạnh ngoài khối đích điểm cao hơn khi đệm độc lập |
| C7 | Ở AVICI: số cạnh giảm rõ ở cả hai họ; ở RFF có mất thứ hạng; ở tuyến tính, thay đổi thứ hạng chưa rõ | XÁC NHẬN (HA1, HA2, HA5), MÔ TẢ (thứ hạng ở tuyến tính) | Như C3. AUROC ở tuyến tính +0.027 [+0.011, +0.044] ở HELD2, nhưng không thuộc bộ kiểm | Ở tuyến tính, không được claim chiều của thứ hạng |
| C8 | **Kết quả âm:** can thiệp attention (value zeroing, knockout, theo lớp) chưa phân biệt được cơ chế của AVICI | EXPLORATORY (P-N3 phần B) | Không có ứng viên. Các can thiệp xóa nhiều hiệu ứng nhất không đạt tiêu chí sàng lọc về chất lượng; V0-8 chỉ vừa vượt ngưỡng (−0.0313 [−0.0639, +0.0012]). KO-all là kiểm tra kỹ thuật | Báo như một giới hạn. Không được claim "attention không liên quan" |
| C9 | Một bước rẻ (sàng lọc phụ thuộc biên, rồi chạy theo thành phần) đưa các contrast trung bình xuống dưới biên. Có đánh đổi chất lượng ở một ô | MÔ TẢ (phân tích phụ ở HELD2) | Mọi REP sau R đều SMALL. Là cách sửa có ích ở 3/4 ô; với CDFM tuyến tính, giá tại k0 là −0.018 [−0.031, −0.005]. Không bất biến ở từng hệ (một hệ đổi 11 cạnh) | Không được Holm xác nhận. α_HSIC là mức danh nghĩa (đuôi gamma dễ dãi). Kết quả có được khi cột thêm vào **độc lập với khối đích theo thiết kế** (cột tổng hợp). Điều đó vẫn đúng khi thêm cột tổng hợp vào dữ liệu thật (gap 2), nhưng không áp dụng được cho các biến có sẵn trong dữ liệu thật mà không biết có liên quan hay không. R ở đây (R-B) còn dùng họ cơ chế để chọn phép kiểm. **Gap 3 đã đóng (22/11):** biến thể chỉ dùng input là R-L của P-N6, xem C13–C15. C9 giữ nhãn cũ |
| C10 | Định vị: nguyên lý nhất quán khi đổi tập biến đã có. Đóng góp là failure cụ thể với đáp án biết trước, đường ảnh hưởng đã cô lập ở CDFM, và phạm vi của cách sửa | PRIOR ART | Self-Compatibility (AISTATS 2024); Grinsztajn (NeurIPS 2022); TabPFN (ICLR 2023 §B.3.2); Noise Immunity (2026); Aliferis 2010; CausalArena (2026, không có phép đối sánh này). Montagna et al. (TMLR 2025) chỉ là khung diễn giải về prior huấn luyện. [Cập nhật 21/11](N1_prior_art_update_2026-11-21_vi.md) | Chưa phải systematic review; phải lặp lại tìm kiếm trước khi gửi |
| C11 | **Bảng thật, skeleton:** khi thêm 20 cột Gauss độc lập vào hai bảng cố định (Sachs CD3/CD28 và Wine trắng; mỗi bảng 500 hàng chọn trước, normal-score), số cặp trong skeleton đích thay đổi trung bình của AVICI và CDFM lớn hơn đối chứng cổ điển ở cả hai bảng (Study 4). Với pipeline mặc định của FoundCause tại base 42, kết quả này được xác nhận trên Wine, nhưng không được xác nhận trên Sachs (Study 6). *Chú thích:* đối chứng là max(PC, GES) theo từng lần sinh; hai study có family Holm riêng; kết quả đo độ bất ổn, không đo độ chính xác | **XÁC NHẬN trong phạm vi từng study:** P-N5 4/4 (P5-1; Holm 0.05 trên 8 giả thuyết); P-N7 1/2 (P7-1; Holm 0.05 trên 2 giả thuyết): Wine CONFIRMED, Sachs NOT_CONFIRMED | Contrast flips_M − max(flips_PC, flips_GES) qua 20 lần sinh. P-N5: Sachs AVICI +2.65 [+2.24, +3.06], CDFM +1.30 [+0.84, +1.76]; Wine AVICI +5.30 [+3.00, +7.60], CDFM +10.90 [+9.81, +11.99]. P-N7 (FoundCause): Wine +15.90 [+14.51, +17.29], 20/20 lần sinh dương; Sachs +0.05 [−0.23, +0.33]. PC và GES đổi tối đa 1 cặp ở mọi lần sinh. Mô tả: ở Sachs, AVICI có 4 cạnh ở k0, và 40 cột có cấu trúc xóa cả 4 cạnh ở cả 20 lần sinh ([P-N5](../n5_real_data_consistency_2026-11-22/PN5_results_vi.md) §2–§3); ở Wine, số cạnh của FoundCause tăng ròng trung bình 15.6 mỗi lần sinh (thêm 15.8, bỏ 0.2; m0 = 8) ([P-N7](../n7_foundcause_real_tables_2026-11-22/PN7_results_vi.md) §2) | Chỉ đo độ bất ổn, không đo độ chính xác; không gọi là tác hại; ổn định không chứng minh đúng. Suy luận có điều kiện trên từng bảng, cách chọn hàng và tiền xử lý; 20 lần sinh đệm không phải 20 bộ dữ liệu. Chỉ hai bảng; cột thêm vào là cột tổng hợp. Cỡ hiệu ứng của CDFM trên Sachs là UNCLEAR theo biên 1 cặp; CI và nhãn cỡ không được Holm bảo vệ. P-N7 dùng lại input của P-N5, không phải held-out mới; nó không tách tác động của thông tin cột thêm vào khỏi thay đổi tính toán nội bộ khi D đổi. Sachs không được xác nhận không chứng minh FoundCause ổn định ở đó. Không so sánh giữa các model |
| C12 | **Bảng thật, ngưỡng CDFM:** ngưỡng NATIVE của CDFM với đệm có cấu trúc cao hơn với đệm Gauss trong cùng lần sinh, ở Wine với cả k = 20 và k = 40, và ở Sachs chỉ với k = 40 | **XÁC NHẬN trong phạm vi P-N5** ở 3/4 ô (P5-2; Holm 0.05). Sachs k = 20: NOT_CONFIRMED | Wine +0.180 [+0.159, +0.201] (k = 20) và +0.191 [+0.180, +0.202] (k = 40); Sachs k = 40 +0.125 [+0.103, +0.147]; Sachs k = 20 −0.007 [−0.031, +0.017], với 9 lần sinh dương và 11 âm ([P-N5](../n5_real_data_consistency_2026-11-22/PN5_results_vi.md) §2.2) | NOT_CONFIRMED không chứng minh không có hiệu ứng; CI ở Sachs k = 20 không nằm gọn trong biên ±0.03. Ở Sachs k = 40, đệm Gauss làm ngưỡng thấp hơn k0, nên contrast gồm cả hai chiều. Ngưỡng tăng không kéo theo mất cạnh NATIVE ở Sachs (xem C5, thăm dò). Phạm vi như C11 |
| C13 | **Cách sửa chỉ dùng input, mức F1:** trên hệ tổng hợp held-out, R-L không làm giảm F1 skeleton trung bình quá 0.03 so với output ban đầu, tại k0 và tại A20 (20 cột Gauss). Xác nhận cho AVICI trên hệ tuyến tính và RFF, và cho CDFM trên hệ RFF. R-L là sàng lọc HSIC mọi cặp ở mức cố định 10⁻⁴, chỉ dùng bảng input, rồi chạy model theo từng thành phần | **XÁC NHẬN trong phạm vi P-N6** ở 3/4 (P6-1: phép kiểm không kém quá biên, Holm 0.05 trên 6 giả thuyết). CDFM tuyến tính: **NOT_CONFIRMED** | Q0 và Q(A20): AVICI tuyến tính +0.020 [−0.005, +0.045] và +0.020 [−0.005, +0.044]; AVICI RFF −0.007 [−0.017, +0.003] và −0.007 [−0.017, +0.003]; CDFM RFF −0.001 [−0.019, +0.017] và −0.003 [−0.021, +0.016]; CDFM tuyến tính −0.024 [−0.042, −0.005] và −0.022 [−0.041, −0.003] ([P-N6](../n6_fix_comparison_2026-11-22/PN6_results_vi.md) §2) | **Không mở rộng kết luận sang S20** (đệm có cấu trúc), vì S20 không thuộc phép kiểm này. Đọc là "không kém mốc ban đầu quá biên đã chọn", không phải tương đương hay giữ nguyên output: R-L đổi output ngay ở k0 (C15). NOT_CONFIRMED ở CDFM tuyến tính không chứng minh tổn thất vượt biên: ước lượng điểm nằm trong biên, CI vượt biên, power đã báo trước là thấp (0.21). Phạm vi: ER, n = 500, d_T ∈ {10, 20}, k = 20; α_L chọn trên DEV6. CI không được Holm bảo vệ |
| C14 | **Giữ gần output ban đầu hơn FROZEN:** tại S20, R-L có φ trung bình (số cặp đích khác output ban đầu của CDFM) nhỏ hơn FROZEN, ở cả hai họ | **XÁC NHẬN về dấu trong phạm vi P-N6** (P6-2, 2/2, Holm 0.05) | Chênh lệch theo chiều FROZEN − R-L: tuyến tính +8.73 [+5.93, +11.54] cặp (18.00 so với 9.27); RFF +10.33 [+8.14, +12.53] cặp (17.32 so với 6.98) ([P-N6](../n6_fix_comparison_2026-11-22/PN6_results_vi.md) §2) | Đây là giữ gần output ban đầu hơn, **không** phải xác nhận độ chính xác cao hơn. φ của R-L đã tính cả giá ở k0. Chỉ CDFM, chỉ S20. FROZEN chỉ cố định ngưỡng; điểm của khối đích vẫn đổi. Không viết "FROZEN vô dụng" |
| C15 | **Bất biến có điều kiện, tần suất gộp nhầm, đánh đổi.** (i) Tính chất của thuật toán: với mức cố định mỗi cặp, quyết định giữa các cặp đích của R-L không phụ thuộc số cột thêm vào; khi không có thành phần nào trộn đích với đệm, output trên khối đích giữ nguyên như ở k0. (ii) Quan sát: trộn xảy ra ở 11/120 hệ với A20 (1 cột mỗi hệ) và 12/120 hệ với S20 (15–20 cột mỗi hệ, gần cả khối đệm). (iii) Đánh đổi: R-H (Bonferroni trên toàn bảng) trộn ít hơn nhưng tách thêm cạnh đích khi có đệm; R-H có nhiều hệ đổi output hơn R-L, nhưng mức đổi trung bình không luôn lớn hơn. (iv) R-L đổi output ngay ở k0 | MÔ TẢ (P-N6 §3–§4, ngoài bộ Holm). (i) là tính chất toán học; **572/572 là kiểm tra cài đặt, không phải kết luận thống kê mới**. Nguồn gốc của giá ở k0: POST-HOC (P-N6 §9) | Kiểm tra cài đặt: 320/320 input có đệm giữ quyết định giữa các cặp đích; 572/572 trường hợp thỏa điều kiện trùng từng bit. Số hệ có σ > 0 trên 60, R-L so với R-H: A20 1–8 so với 5–10; S20 5–7 so với 8–11. σ trung bình ở S20: R-H nhỏ hơn R-L ở 3/4 nhóm (ví dụ CDFM RFF 2.70 so với 2.90); ở A20, R-H lớn hơn ở cả 4 nhóm. φ(k0) của R-L: 4.03, 0.85, 8.37, 4.78 cặp. Số cặp chéo bị bác bỏ vượt cận trên danh nghĩa (đúng khi p-value hợp lệ) từ 1.7 đến 24 lần ([P-N6](../n6_fix_comparison_2026-11-22/PN6_results_vi.md) §3–§4, §9) | Tần suất trộn và cỡ gộp là mô tả, không có phép kiểm; CI Clopper–Pearson rộng. Khi cả bảng thành một thành phần, R-L trùng plain. Gộp nhầm có thể do đuôi gamma của HSIC dễ dãi (suy luận). Nguồn gốc của giá ở k0 là kế toán hậu nghiệm, chưa xác định nguyên nhân. Chỉ với cột tổng hợp độc lập theo thiết kế; không áp dụng cho biến có sẵn trong dữ liệu thật |
| C16 | **Pipeline tổng hợp trên tập con (SEA, Study 7):** Với một checkpoint SEA tổng hợp các ước lượng FCI trên tập con biến, trên 120 hệ tổng hợp mới, việc thêm một khối 20 biến độc lập với khối đích — Gauss hoặc có cấu trúc nội bộ — làm tăng khoảng cách trung bình từ skeleton đích tới các output k0 tham chiếu. Với đệm Gauss, F1 skeleton giảm trung bình; trên các hệ tuyến tính, mức giảm vượt đối chứng PC/GES theo contrast đã khóa. Hai kết luận F1 được xác nhận về dấu, chưa xác lập vượt biên thực tiễn 0,05. Trên hai bảng thật cố định, kết quả về khoảng cách được xác nhận ở Wine, nhưng không được xác nhận ở Sachs | **XÁC NHẬN trong phạm vi Study 7** (P-N8; Holm 0.05 trên 6 giả thuyết, family riêng): P8-1, P8-1S, P8-2, P8-3, P8-4W CONFIRMED; P8-4S NOT_CONFIRMED. Hai kết luận F1 (P8-2, P8-3) chỉ áp dụng cho đệm Gauss A20 và chỉ ở mức dấu (Size UNCLEAR). Với đệm có cấu trúc, chỉ giả thuyết về Δ (P8-1S) được xác nhận | Δ = khoảng cách trung bình tới 4 output k0 tham chiếu ở seed khác, trừ khoảng cách của output k0 cùng seed tới chính các output đó. A20 +5.84 [+5.06, +6.61], S20 +4.50 [+3.86, +5.13] (LARGE, biên 1 cặp); H (A20) +0.049 [+0.035, +0.063]; H_SEA − max(H_PC, H_GES) trên hệ tuyến tính +0.065 [+0.041, +0.088] (cả hai UNCLEAR, biên 0.05); Wine +5.88 [+4.82, +6.93] (LARGE); Sachs +0.18 [−0.07, +0.42] (SMALL). Mô tả: SEA chủ yếu bỏ cạnh (số cạnh giảm ở 97/120 hệ với A20; Wine 20.85 → 14.0); ô c2 (d_T = 10, e_T = 2, tuyến tính) đóng góp khoảng 52% mức giảm F1 trung bình, bảy ô còn lại trung bình 0.0269 (hậu nghiệm); cách đọc phụ 1 − P(không cạnh) > 0.5 cho các ước lượng cùng dấu, P8-2 SMALL ([P-N8](../n8_sea_model_coverage_2026-11-23/PN8_results_vi.md) §0, §2) | Một model, một checkpoint (FCI, huấn luyện trên dữ liệu tổng hợp), code đã phát hành. Dữ liệu tổng hợp sinh bằng simulator của AVICI. Không xác lập rằng toàn bộ điều kiện thử nằm trong phân phối huấn luyện của SEA: RFF không có trong các cơ chế huấn luyện; mỗi tập huấn luyện có N = 10, 20 hoặc 100 biến và 1000N hàng, còn ở đây n = 500 hàng (bằng kích thước lô) và D = 30, 40 (phần A) hoặc 31 (phần B) sau khi thêm đệm. Δ chỉ đọc một chiều: phân phối không đổi thì E[Δ] = 0, không suy ngược; kết quả trung bình phần A không xác nhận thay đổi cho từng hệ và không phải phép kiểm phân phối đồ thị sau khi gộp các hệ. Kênh gây thay đổi chưa xác định: thứ tự S20 so với A20 không phù hợp với giải thích đơn giản rằng độ phủ càng giảm thì Δ càng tăng, nhưng chưa loại trừ vai trò của độ phủ. Phần B dùng lại input của Study 4. Sachs không được xác nhận không chứng minh SEA ổn định ở đó. Không so sánh với các model khác |

## 2. Phần còn thiếu, theo thứ tự user đã chốt

1. **Gap 1: kiểm chứng bổ sung cho CDFM, trước khi chốt bài** (không chặn việc viết). **Đã chạy ngày 21/11: cả tám giả thuyết CONFIRMED** (Holm 0.05), ở cả k = 20 và k = 40. Ở k = 40, khối đệm đóng góp nhiều hơn khối chéo. Cặp không-cạnh của khối đệm cũng giảm điểm. Xem [kết quả P-N4](../n4_cdfm_threshold_path_2026-11-21/PN4_results_vi.md). User đã duyệt kết quả ngày 22/11; C5, C6a và C6b đã cập nhật theo đó.
   - **Dữ liệu:** seed mới, base 440000. Giữ n = 500 và họ đồ thị ER; họ cơ chế RFF như P-N3 phần A. Hai cấu hình:
     - k = 20: mốc lặp lại phần A trên seed mới;
     - k = 40: cấu hình ngoài phạm vi hiện tại. Không mở đồng thời n hay SF.
   - **Đo:**
     - Δℓ và Shapley theo khối T, P, X (thiết kế 2³ như phần A);
     - **phép đổi riêng X:** giữ T và P ở e = 0, chỉ lấy khối X từ e_T; đo ngưỡng và số cạnh khối đích;
     - phần do điểm (S) và phần do ngưỡng (T), **báo riêng, giữ dấu**;
     - xác suất trung bình của khối chéo; với khối đệm, tách cặp không-cạnh và cặp có cạnh (sửa giới hạn của C6).
   - **Luật:** [P-N4 v1](../n4_cdfm_threshold_path_2026-11-21/PN4_rules_vi.md), **đã khóa** ngày 21/11 (v0 cộng ba chỉnh sửa của user: SE = 0 thành DEGENERATE với p = 1; hồ sơ power trong `design/`; G5 đối chiếu giá trị đầy đủ). Theo quyết định của user ngày 21/11 (lượt 3):
     - bốn giả thuyết cho mỗi k: (a) điểm khối chéo giảm; (b) ngưỡng NATIVE tăng; (x) chỉ đổi khối chéo thì ngưỡng tăng và số cạnh đích giảm, đếm trên điểm đích ở e = 0; (c) phần do ngưỡng chiếm phần lớn;
     - tiêu chí (c): μ_T < −1.5, μ_(T+S) < 0 và μ_(T−S) < 0. Hai điều sau tương đương μ_T < −|μ_S|. CI tính trực tiếp trên từng contrast của cùng các hệ. Kết luận áp cho trung bình, không cho từng hệ. Mốc phân rã giữ ở e = 0;
     - (x) và (c) là giả thuyết tổng hợp, với p bằng giá trị lớn nhất của các thành phần. Holm 0.05 trên cả 8 giả thuyết của hai k; đọc riêng từng k;
     - cỡ mẫu đề xuất 80 hệ (20 mỗi ô RFF), theo power tính từ HELD2.
   - **Không** khóa "khối chéo luôn đứng đầu". Tỉ lệ số cặp chéo/đệm là 2·d_T/(k − 1); ở k = 40 là 0.51 (d_T = 10) và 1.03 (d_T = 20), nên lợi thế về số lượng của khối chéo gần như mất.
   - **Quy trình:** user duyệt v0, rồi khóa và push trước khi sinh dữ liệu, như P-N2 và P-N3.
2. **Gap 2: yêu cầu nhất quán cần kiểm tra trên dữ liệu thật.** **Đã chạy ngày 22/11 (P-N5): 7/8 giả thuyết CONFIRMED** (Holm 0.05; có điều kiện trên hai bảng đã cố định).
   - Trên cả hai bảng, khi thêm 20 cột Gauss, skeleton khối thật của AVICI và CDFM đổi nhiều hơn max(PC, GES) theo từng lần sinh (4/4).
   - Ngưỡng CDFM cao hơn khi đệm có cấu trúc ở Wine (k = 20 và 40) và ở Sachs (k = 40); Sachs k = 20 NOT_CONFIRMED.
   - Xem [kết quả P-N5](../n5_real_data_consistency_2026-11-22/PN5_results_vi.md). User đã duyệt kết quả ngày 22/11 (lượt 5). C1, C3 và C5 đã cập nhật; đã thêm C11 và C12. Phân rã thăm dò (EXPLORATORY): [PN5_decomposition_exploratory_vi.md](../n5_real_data_consistency_2026-11-22/PN5_decomposition_exploratory_vi.md).
   - **Logic:** cột thêm vào là cột tổng hợp, độc lập với khối thật theo thiết kế. Quan hệ thật trong khối thật vì vậy không đổi. Nhưng một bộ ước lượng hữu hạn mẫu không bắt buộc cho output trùng hệt. Vì không có ground truth, phép thử chỉ đo **độ bất ổn**, không đo độ chính xác.
   - **Yêu cầu thiết kế:**
     - giữ nguyên khối thật và tiền xử lý; khối thật trùng từng bit giữa các input;
     - lặp lại việc sinh khối đệm (nhiều bản rút cho mỗi bộ dữ liệu và mỗi kiểu đệm);
     - kiểm soát randomness của model: seed cố định, đo τ_rep như P-N1;
     - có đối chứng cổ điển (PC, GES) trên đúng các input đó, làm mốc bất ổn hữu hạn mẫu;
     - **không dùng độ ổn định thay cho độ chính xác:** một model ổn định vẫn có thể sai.
   - **Biến đo:** số cặp đổi trạng thái, Δm, |Δm|, ngưỡng CDFM; theo từng bản rút đệm.
   - **Dữ liệu** (user chọn và duyệt tải ngày 22/11; [manifest](../n5_real_data_consistency_2026-11-22/DATA_MANIFEST_vi.md)):
     - chính: Sachs, riêng điều kiện CD3/CD28 (`Data Files/cd3cd28.csv`, 853 tế bào × 11 biến), bản phát hành Zenodo của MaRDI;
     - bổ trợ: UCI Wine Quality, rượu trắng (4 898 hàng; dùng 11 biến lý–hóa, bỏ `quality`).
   - **Phạm vi user đề xuất cho luật P-N5:**
     - AVICI và CDFM; PC/GES là đối chứng thực nghiệm, không phải đáp án đúng;
     - mỗi bảng chọn trước 500 hàng; lựa chọn và tiền xử lý cố định trước khi xem output;
     - k = 0, 20, 40; đệm Gauss và đệm ER–RFF có cấu trúc, độc lập; 20 lần sinh đệm mỗi điều kiện;
     - báo Δp, số cặp đổi trạng thái, Δm, |Δm|, ngưỡng và số cạnh tại k0; không gọi thay đổi là giảm độ chính xác;
     - các lần sinh đệm đo biến thiên có điều kiện trên bảng thật đã cố định, không phải 20 bộ dữ liệu thật độc lập.
3. **Gap 3: so sánh cách sửa, ghi rõ thông tin mỗi cách dùng.** **Đã đóng** (22/11, user duyệt, lượt 6). Luật P-N6 v1: [PN6_rules_vi.md](../n6_fix_comparison_2026-11-22/PN6_rules_vi.md).
   - **Kết quả:** [PN6_results_vi.md](../n6_fix_comparison_2026-11-22/PN6_results_vi.md).
     - 5/6 CONFIRMED. P6-1C-lin (CDFM, tuyến tính) là NOT_CONFIRMED.
     - Đã thêm C13–C15 theo cách viết của user; C9 dẫn sang các claim mới.
     - Phép kiểm kết hợp Fisher-z và HSIC chưa làm, để giữ phạm vi bài. Nghiên cứu ngưỡng theo thành phần là hướng tiếp nối.
   - User chọn R-L làm cách sửa chính, giữ R-H để so sánh, 120 hệ; bảng thật chỉ mô tả.
   - P6-1 dùng phép kiểm không kém quá biên (0.03) cho cả giá ở k0 lẫn mức ở A20; P6-2 so R-L với FROZEN ở đệm có cấu trúc.
   - Bản nháp sửa dòng R trong bảng dưới: R của P-N2 còn dùng họ cơ chế để chọn phép kiểm (Fisher-z cho hệ tuyến tính, HSIC cho RFF).
   - Bản nháp tách cách này thành R-B và đề xuất hai biến thể chỉ dùng input: R-H (Bonferroni trên toàn bảng) và R-L (mức cố định mỗi cặp). Với R-L, quyết định giữa các cặp đích không phụ thuộc số cột thêm vào. Output trên khối đích chỉ được giữ nguyên khi không có thành phần nào trộn đích với đệm (phát biểu có điều kiện, luật v1 §1).

   | Cách | Thông tin dùng | Vai trò |
   |---|---|---|
   | R (sàng lọc rồi chạy theo thành phần) | dữ liệu input, và họ cơ chế để chọn phép kiểm; không biết khối nào là đích | cách sửa ứng viên |
   | FIXED 0.5 | không dùng thêm thông tin; bỏ bộ chọn ngưỡng của CDFM | đối chứng decoder |
   | Ngưỡng cục bộ của CDFM | biết khối đích: đặc trưng ngưỡng chỉ tính trên khối đích | **đối chứng**, không ngang hàng với R |
   | FROZEN | dùng lần chạy k0 trên riêng khối đích | **đối chứng**, không ngang hàng với R |
   | R-oracle | biết ranh giới đích/đệm | kiểm sanity; trùng k0 theo cấu trúc |

   - Mỗi cách đo cả độ đổi lẫn chất lượng tại k0.
   - MambaPFN không vào so sánh: chỉ ở related work ([cập nhật prior art](N1_prior_art_update_2026-11-21_vi.md) §2).
4. **Gap 4: phạm vi model.**
   - FoundCause mới ở mức P-N1.
   - TabCausal: checkpoint `tabcausal-base.pt` có sẵn trong bản clone ở máy, chưa cài ([manifest](../n1_irrelevant_vars_2026-11-13/DATA_MANIFEST_vi.md) §1). Chỉ dùng cho C1, nếu cài được trong venv riêng.
   - **GO cho thiết kế thu gọn** (user, 22/11, lượt 6), với điều kiện thêm model kiểm được một claim cụ thể. Ngân sách phải đo trước lượt chính. Gap 4 không chặn việc viết.
   - **Luật P-N7 v1 đã khóa** (22/11, lượt 7): [PN7_rules_vi.md](../n7_foundcause_real_tables_2026-11-22/PN7_rules_vi.md).
     - Nội dung: FoundCause trên hai bảng thật của P-N5, tức kiểm C11 cho model thứ ba. Phương án B: mỗi bảng đủ 20 lần sinh, hai lượt.
     - P7-1 kiểm độ bất ổn của toàn bộ pipeline mặc định, có điều kiện trên lịch base 42. Nó không tách tác động của thông tin cột thêm vào khỏi thay đổi tính toán nội bộ khi D đổi.
     - Input là input của P-N5 được dùng lại, không phải held-out mới. Hai giả thuyết là một family Holm riêng.
     - Tham chiếu bốn base ở k0 đo biến động của toàn bộ lịch suy luận. Nó không phải đối chứng riêng cho hoán vị cột, không phải ngưỡng, và không được lấy trừ khỏi flips.
     - Chỉ k = 20. D ∈ [2, 50] là dải huấn luyện được công bố (đã xác minh ở FoundCause v2), không phải giới hạn kỹ thuật.
     - P-N7 không mở rộng kết luận về cơ chế ngưỡng của CDFM hay cách sửa R-L sang FoundCause.
   - **P-N7 đã chạy xong (23/11):** [PN7_results_vi.md](../n7_foundcause_real_tables_2026-11-22/PN7_results_vi.md).
     - P7-1W (Wine) CONFIRMED; P7-1S (Sachs) NOT_CONFIRMED, trong family Holm riêng của P-N7.
   - **Đã đóng** (user, 23/11, lượt 8). C11 đã cập nhật theo câu của user. Không mở thêm thí nghiệm cho gap này; TabCausal không thêm.
   - **Phần mở rộng sau khi đóng gap 4: Study 7 (P-N8, SEA)**, theo đề xuất ba bước của user (23/11): [luật v1](../n8_sea_model_coverage_2026-11-23/PN8_rules_vi.md), [kết quả](../n8_sea_model_coverage_2026-11-23/PN8_results_vi.md).
     - Một pipeline tổng hợp các ước lượng FCI trên tập con biến, một checkpoint. Thiết kế riêng: 120 hệ tổng hợp mới; Δ so với 4 output k0 tham chiếu ở seed khác; hai bảng thật của Study 4 với input dùng lại.
     - 5/6 CONFIRMED trong family Holm riêng; Sachs NOT_CONFIRMED. C16 thêm theo câu của user.
     - **Đã đóng** (user, 23/11). Không mở thêm lượt thí nghiệm.
5. **Gom thống kê trong lúc viết** (không phải bước riêng):
   - mỗi bảng của bài ghi bộ dữ liệu (P-N1 EXP/HELD, EXP2, HELD2), giả thuyết đã khóa (file luật), phép kiểm và mức bằng chứng;
   - bảng các pha và cổng toàn vẹn đưa vào appendix;
   - mã commit và thời điểm push được ghi trong tài liệu bổ sung về nguồn gốc và tính toàn vẹn.

## 3. Khung bản thảo (tiếng Anh; bản nháp đang viết)

1. **Introduction:** target-block conclusions of pretrained causal discovery models depend on appended, provably irrelevant variables.
2. **Related work:** consistency across variable sets (self-compatibility); robustness of tabular foundation models to uninformative features; amortized causal discovery and training priors.
3. **Setup:** an invariance test with a known required answer; models; padding families; measures that separate edge count, ranking and threshold; the locked exploratory → held-out protocol.
4. **Failure on synthetic data** (C1, C2).
5. **Padding structure at fixed D** (C3, C4, C7).
6. **Channels** (C5, C6, C8): CDFM's global threshold selector; what attention interventions on AVICI could and could not show.
7. **Two real tables** (C11, C12): instability of the target-block output on two fixed real tables, against classical controls, with no accuracy claim; exploratory decomposition of the CDFM change (C5).
8. **Mitigation and its scope** (C13–C15; C9 as the earlier variant): the cost at k0, the stability after the fix, and the risk of false merges.
9. **Limitations:** harm (F1) is measured on synthetic data only; two to three checkpoints; nominal HSIC level, with false cross rejections above the nominal bound; the input-only fix changes the output at k0 and is not confirmed for CDFM on linear systems. We identify the influence path through CDFM's threshold selector, but we do not explain why the model produces those score changes, and we do not distinguish AVICI's mechanism. The real-data check covers two fixed tables and measures instability, not accuracy.

**Cập nhật 23/11 (Study 7):** khung trên là khung ban đầu; cấu trúc hiện tại của bản thảo nằm trên nhánh riêng. Bản thảo thêm Study 7 (C16) thành một mục riêng với bảng riêng (Label và Size). Sự không đồng đều giữa các ô nằm trong văn bản chính; bảng theo ô và cách đọc phụ ở phụ lục; pattern của ô c2 và của độ phủ ở phần thảo luận. Kết quả Study 1 giữ phạm vi ba checkpoint ban đầu.

## 4. Nhật ký sửa (21/11, sau review của user)

Số liệu không đổi. Bản trước là `b62b8da`.

| # | Chỗ | Bản trước | Sửa thành |
|---|---|---|---|
| 1 | C2 | "Mức thay đổi tăng theo số cột thêm vào"; "một phần XÁC NHẬN" | Claim rộng ở mức exploratory; held-out chỉ có kết quả hai đầu của CDFM, không chứng minh tăng đơn điệu |
| 2 | C4 | "F1 đi ngược chiều vì điểm xuất phát khác nhau ở k0" | Riêng số cạnh ở k0 không đủ giải thích; chiều của F1 phụ thuộc loại cạnh bị bỏ. Thêm TP/FP và phân rã |
| 3 | C5 | "phần lớn mức giảm ... đi qua bộ chọn ngưỡng ..., không qua điểm của khối đích" | "theo phép phân rã lấy ngưỡng e = 0 làm mốc"; không loại trừ ảnh hưởng của điểm khối đích; tỉ lệ có thể vượt 100% |
| 4 | C6 | "điểm của các cặp không-cạnh ngoài khối đích giảm" dựa trên cả khối chéo lẫn khối đệm | Khối chéo là không-cạnh theo thiết kế; trung bình của khối đệm gộp cả cạnh thật ở e_T, nên không dùng cho không-cạnh của khối đệm |
| 5 | C9 | "Cần giả định đệm độc lập đúng, điều không có ở dữ liệu thật" | Cột tổng hợp độc lập theo thiết kế, kể cả khi thêm vào dữ liệu thật; không áp dụng cho biến có sẵn |
| 6 | §2 gap 1 | Một trong ba cấu hình ngoài phạm vi; dự đoán (c) "chiếm phần lớn" chưa định nghĩa | k = 40 kèm mốc k = 20 trên seed mới; phép đổi riêng X; báo S và T riêng; tiêu chí (c) không dùng tỉ lệ |
| 7 | §2 gap 2 | "Kiểm tính nhất quán ... Đáp án đúng (output không đổi) đã biết" | "Yêu cầu nhất quán cần kiểm tra": hữu hạn mẫu không bắt buộc output trùng hệt; đo độ bất ổn, không đo độ chính xác; năm yêu cầu thiết kế |
| 8 | §2 gap 3 | So R, ngưỡng cục bộ, ngưỡng cố định, MambaPFN | Bảng thông tin mỗi cách dùng; ngưỡng cục bộ và FROZEN là đối chứng; bỏ MambaPFN khỏi so sánh |
| 9 | §2 | "xếp theo ưu tiên (đề xuất, chờ user quyết)" | Thứ tự user đã chốt: gap 1 → dữ liệu thật → cách sửa → thêm model; gom thống kê trong lúc viết |
| 10 | §3 mục 8 | "no internal mechanism" | Câu limitations theo đúng diễn đạt của user |

**Lượt 3 (21/11, sau review của user):**

| # | Chỗ | Bản trước (`e4d5396`) | Sửa thành |
|---|---|---|---|
| 11 | C1 | "PC khoảng 0.000, GES ≤ 0.005": số gộp cả hệ RFF, nơi GES sai giả định | Số trên hệ tuyến tính: PC 0.000; GES 0.009 (40 hệ) và 0.034 (12 hệ của FoundCause). User tính, agent tái lập từ `held_*.json` |
| 12 | C4 | "CI của ΔTP, ΔFP cho B − A chưa tính" | Thêm CI bootstrap (mô tả, chưa hiệu chỉnh đa kiểm định). User tính, agent tái lập khớp |
| 13 | §2 gap 1 | Dự đoán (a), (b), (c) đề xuất; "phép kiểm và cỡ mẫu chốt ở luật đó" | Trỏ sang luật P-N4 v0 (nháp): thêm giả thuyết trực tiếp về khối chéo; (c) theo cách hiểu chính xác của user; Holm trên 8 giả thuyết; 80 hệ |

**Lượt 4 (22/11, sau khi user duyệt kết quả P-N4):**

| # | Chỗ | Bản trước | Sửa thành |
|---|---|---|---|
| 14 | C5 | MÔ TẢ trên HELD2; "phần lớn" chưa định nghĩa | XÁC NHẬN trong phạm vi P-N4: đóng góp trung bình của ngưỡng âm, vượt 1.5 cạnh, lớn hơn độ lớn đóng góp trung bình của điểm, theo mốc e = 0, ở cả hai k |
| 15 | C6 → C6a | Một claim EXPLORATORY gộp đường ảnh hưởng và phân bổ đóng góp | C6a: XÁC NHẬN trong phạm vi P-N4 rằng thay riêng khối chéo đủ làm ngưỡng tăng và số cạnh đích giảm |
| 16 | C6 → C6b | "Khối chéo đóng góp lớn nhất"; trung bình khối đệm gộp cả cạnh thật | C6b, mô tả: nhóm dẫn đầu đổi theo k; cặp không-cạnh của khối đệm giảm điểm, cặp có cạnh tăng; đổi nhóm dẫn đầu phù hợp với tỉ lệ số cặp nhưng chưa chứng minh đó là nguyên nhân duy nhất |
| 17 | §2 gap 2 | "Cần user duyệt việc chọn và tải bộ dữ liệu" | Hai bảng đã chọn, đã tải, có manifest; phạm vi đề xuất của user cho luật P-N5 |

**Lượt 5 (22/11, sau khi user duyệt kết quả P-N5):**

| # | Chỗ | Bản trước | Sửa thành |
|---|---|---|---|
| 18 | C1 | "Chưa có kiểm tính nhất quán trên dữ liệu thật (gap 2)" | Claim ghi rõ "trên dữ liệu tổng hợp"; phần giảm F1 chỉ có trên dữ liệu tổng hợp; trên hai bảng thật chỉ có độ đổi skeleton, dẫn sang C11 và C12 |
| 19 | C3 | Không có kết quả trên bảng thật | Ghi chú hậu nghiệm, chỉ về số cạnh của AVICI: cùng chiều HA1/HA2 ở cả bốn ô. P-N5 không kiểm lại năm giả thuyết của C3 |
| 20 | C5 | Chỉ có dữ liệu tổng hợp | Thêm phân rã trên bảng thật ở mức EXPLORATORY, kèm độ nhạy theo mốc; phạm vi xác nhận của P-N4 giữ nguyên |
| 21 | C11 (mới) | — | Skeleton trên bảng thật: XÁC NHẬN 4/4 so sánh tại k = 20 với đệm Gauss, trên hai bảng và tiền xử lý đã cố định |
| 22 | C12 (mới) | — | Ngưỡng CDFM trên bảng thật: câu claim nêu rõ Wine ở cả hai k, Sachs chỉ ở k = 40; Sachs k = 20 giữ NOT_CONFIRMED |
| 23 | §2 gap 2 | "bảng claim sẽ cập nhật sau khi user xem kết quả" | User đã duyệt; trỏ tới phân rã thăm dò |
| 24 | §3 | "Failure (C1, C2)"; "The real-data consistency check is open" | Mục 4 ghi "on synthetic data"; thêm mục 7 cho hai bảng thật (C11, C12); limitations: hai bảng, đo độ bất ổn, không đo độ chính xác |
| 25 | §2 gap 3, dòng R | "chỉ dữ liệu input" | "dữ liệu input, và họ cơ chế để chọn phép kiểm". Agent phát hiện khi soạn P-N6 (`run2.py` chọn Fisher-z hay HSIC theo họ). Đây là sửa về sự kiện; các phép so mới ở P-N6 còn chờ user duyệt |
| 26 | §2 gap 3 | "R-L (mức cố định mỗi cặp, bất biến theo cấu trúc trên phân hoạch đích)" | Quyết định giữa các cặp đích không phụ thuộc số cột thêm vào; output chỉ giữ nguyên khi không có trộn đích với đệm. Câu cũ còn sót từ nháp v0; luật v1 đã sửa theo review của user |
| 27 | §2 gap 3 | — | Thêm trạng thái lượt chính P-N6 và trỏ tới kết quả. Chưa thêm claim; claim chờ user duyệt |
| 28 | C13, C14, C15 (mới) | — | Theo cách viết của user (lượt 6). C13: k0 và A20, không mở rộng sang S20. C14: giữ gần output ban đầu, không phải độ chính xác. C15: tách tính chất có điều kiện của thuật toán khỏi tần suất gộp nhầm và đánh đổi; 572/572 là kiểm tra cài đặt; R-H có nhiều hệ đổi hơn nhưng mức đổi trung bình không luôn lớn hơn |
| 29 | C9 | "Chưa so với các cách sửa khác theo thông tin mỗi cách dùng (gap 3)" | Giữ nhãn cũ; ghi R-B dùng họ cơ chế; dẫn sang C13–C15 |
| 30 | §2 gap 3 | "chờ user duyệt" | Đã đóng (lượt 6); phép kiểm kết hợp chưa làm để giữ phạm vi bài, ứng viên chưa bị bác bỏ |
| 31 | §3, mục 8–9 | "Mitigation and its scope (C9)" | Mục 8 dùng C13–C15; limitations thêm giá ở k0, CDFM tuyến tính chưa xác nhận, và bác bỏ chéo vượt cận danh nghĩa |
| 32 | §2 gap 4 | "FoundCause mới ở mức P-N1" | Thêm quyết định GO thiết kế thu gọn và trỏ tới nháp P-N7 v0 (C11 cho FoundCause); chưa khóa |
| 33 | §2 gap 4 | "Nháp luật P-N7 v0 … chờ user duyệt" | Luật v1 đã khóa (lượt 7): phương án B; phạm vi của P7-1; input dùng lại; tham chiếu lịch chỉ để mô tả |
| 34 | §2 gap 4 | "Luật P-N7 v1 đã khóa" | Thêm dòng trạng thái: P-N7 đã chạy xong (Wine CONFIRMED, Sachs NOT_CONFIRMED); C11 chưa đổi, chờ user duyệt |
| 35 | C11 | "skeleton khối thật của AVICI và CDFM đổi nhiều hơn … FoundCause không chạy" | Câu của user (lượt 8): AVICI và CDFM ở cả hai bảng (Study 4); FoundCause tại base 42 xác nhận trên Wine, không xác nhận trên Sachs (Study 6); chú thích về đối chứng, hai family Holm riêng, độ bất ổn chứ không phải độ chính xác |
| 36 | §2 gap 4 | "P-N7 đã chạy xong, chờ user duyệt" | Đã đóng (lượt 8); không mở thêm thí nghiệm |
| 37 | C11, cột bằng chứng | "FoundCause thêm trung bình 15.6 cạnh" | "tăng ròng 15.6 (thêm 15.8, bỏ 0.2)", theo chỉnh của user (lượt 9), để phân biệt với số cạnh được thêm; tính lại từ output thô |

**Study 7 (23/11, sau khi user duyệt kết quả P-N8):**

| # | Chỗ | Bản trước | Sửa thành |
|---|---|---|---|
| 38 | C16 (mới) | — | Câu của user: khoảng cách tới các output k0 tham chiếu tăng với cả hai loại đệm; hai kết luận F1 chỉ cho đệm Gauss A20 và chỉ ở mức dấu; Wine xác nhận, Sachs không. Trạng thái từng giả thuyết và giới hạn ghi riêng; không nhập vào C1 hay C11 |
| 39 | §2 gap 4 | "Đã đóng (lượt 8)" | Thêm phần mở rộng Study 7 (P-N8): thiết kế, kết quả 5/6, C16; đã đóng, không mở thêm lượt |
| 40 | §3 | Khung ban đầu, chưa có Study 7 | Ghi chú: Study 7 là mục riêng với bảng riêng; không đồng đều giữa các ô trong văn bản chính; pattern của ô c2 và độ phủ ở phần thảo luận |
