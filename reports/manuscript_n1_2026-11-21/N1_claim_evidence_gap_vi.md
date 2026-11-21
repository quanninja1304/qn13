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
> **Mức bằng chứng:**
>
> - **XÁC NHẬN:** kiểm trên dữ liệu held-out theo luật đã khóa;
> - **EXPLORATORY:** pha chọn giả thuyết;
> - **MÔ TẢ:** hậu nghiệm, hoặc không thuộc bộ kiểm;
> - **PRIOR ART:** nguồn ngoài.

## 1. Bảng claim

| # | Claim (dạng sẽ viết trong bài) | Mức | Bằng chứng chính | Phần còn thiếu, rủi ro |
|---|---|---|---|---|
| C1 | Thêm 20 cột độc lập vào một bảng có khối đích cố định làm ba mô hình causal discovery học sẵn đổi output trên khối đích và giảm F1 skeleton. Mức giảm lớn hơn của PC/GES trên cùng hệ tuyến tính | **XÁC NHẬN** (P-N1 RN5, held-out) | H tại k = 20: AVICI 0.068 [0.047, 0.091]; CDFM 0.085 [0.067, 0.104]; FoundCause 0.093 [0.052, 0.138]. BEYOND_CLASSICAL PASS ở mọi estimand. Trên hệ tuyến tính, nơi đối chứng đúng giả định: PC 0.000; GES 0.009 trên 40 hệ, 0.034 trên 12 hệ của FoundCause ([held-out P-N1](../n1_irrelevant_vars_2026-11-13/PN1_HELD_results_vi.md) §2–§3; số theo hệ tuyến tính tính lại từ `held_*.json`) | Phạm vi: dữ liệu tổng hợp ER, n = 500, d_T ∈ {10, 20}, k ≤ 30; mỗi model một checkpoint. FoundCause chỉ có 24 hệ. Chưa có kiểm tính nhất quán trên dữ liệu thật (gap 2) |
| C2 | Ở pha exploratory, mức hại tăng theo số cột thêm vào ở cả ba model. Ở held-out chỉ có kết quả hai đầu cho CDFM | EXPLORATORY (P-N1 E2); held-out chỉ có kết quả hai đầu của CDFM | E2, kiểu A, H_NATIVE ở k = 5 / 10 / 20 / 30: AVICI 0.023 / 0.042 / 0.075 / 0.100; CDFM 0.014 / 0.036 / 0.064 / 0.093; FoundCause 0.008 / 0.017 / 0.064 / 0.095 ([E2](../n1_irrelevant_vars_2026-11-13/PN1_E2_results_vi.md) §3). Held-out, CDFM, kiểu A, 80 hệ: median theo hệ của Δp(30) − Δp(5) = +0.064 [0.057, 0.074], với Δp là trung bình \|p(k) − p(k0)\| trên các cặp của khối đích (phần Δp của M2) | Kết quả hai đầu **không chứng minh** tăng đơn điệu. Điều kiện "median Δp không giảm qua k = 5, 10, 20, 30" của luật M2 chỉ xét ước lượng điểm, không phải phép kiểm. Held-out không kiểm H theo k, và chỉ có CDFM. Claim rộng giữ ở mức exploratory |
| C3 | Ở cùng D, đệm có cấu trúc (e = e_T) so với đệm độc lập (e = 0) làm đổi quyết định trên khối đích theo các chiều xác định | **XÁC NHẬN về dấu** (P-N2 HELD2, Holm 0.05, 5/5) | HA1: AVICI tuyến tính Δm −6.05 [−8.18, −3.92]. HA2: AVICI RFF −1.93 [−2.85, −1.02]. HC1: ngưỡng CDFM RFF +0.175 [+0.159, +0.191]. HA5: top-m0 AVICI RFF −0.027. HC4: AUROC CDFM RFF −0.014 ([HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md) §2) | Chỉ HA1 và HC1 vượt biên thực tiễn; HC4 nhỏ theo biên; HA2, HA5 UNCLEAR. Đã thấy hiệu ứng thu nhỏ từ EXP2 sang HELD2 |
| C4 | Chỉ đọc F1 có thể gây hiểu nhầm. Khi đổi A → B, AVICI và CDFM cùng dự đoán ít cạnh hơn, nhưng F1 đi ngược chiều. AVICI bỏ cạnh đúng và cạnh sai với số lượng gần nhau, và F1 giảm; CDFM bỏ chủ yếu cạnh sai, và F1 tăng | MÔ TẢ (P-N1 hậu nghiệm); cùng chiều ở HELD2 (mô tả, ngoài bộ Holm) | P-N1 held-out, B − A, NATIVE, 80 hệ: AVICI ΔTP −2.31 [−2.95, −1.67], ΔFP −2.59 [−3.98, −1.45] (Δm −4.9), ΔF1 −0.050 [−0.074, −0.024]; CDFM ΔTP −2.21 [−3.15, −1.22], ΔFP −8.21 [−11.93, −4.81] (Δm −10.4), ΔF1 +0.036 [+0.015, +0.057]. CI của ΔTP, ΔFP: bootstrap ghép cặp của P-N1 (2000 lần, seed 20261114) trên các hàng theo hệ của `held_*.json`; user tính, agent tái lập khớp; mô tả, chưa hiệu chỉnh đa kiểm định. Phân rã theo mốc m0: phần thứ hạng AVICI +0.008 [−0.014, +0.031], CDFM −0.026 [−0.041, −0.012]; phần số cạnh, lấy hiệu, khoảng −0.058 và +0.061 (sai số làm tròn ±0.001) ([hậu nghiệm](../n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md) Bảng 1–2). HELD2, REP: AVICI tuyến tính TP −2.45, FP −3.60, F1 −0.049; CDFM RFF TP −3.33, FP −12.23, F1 +0.030 | Phân rã là kế toán theo mốc m0, không phải nguyên nhân. Riêng số cạnh ở k0 (AVICI 17.5, CDFM 33.0, cạnh thật 22.4) **không đủ** giải thích chiều của F1: chiều này phụ thuộc vào việc cạnh bị bỏ là cạnh đúng hay cạnh sai. Không quy nguyên nhân chỉ cho việc dự đoán thiếu hay thừa |
| C5 | Ở CDFM RFF, **theo phép phân rã lấy ngưỡng e = 0 làm mốc**, phần lớn mức giảm số cạnh NATIVE trên khối đích nằm ở phần do ngưỡng | MÔ TẢ trên HELD2 (phân rã ghi sẵn trong luật HELD2 §4, ngoài bộ Holm); HC1 XÁC NHẬN | HELD2: Δm NATIVE −15.57; phần do ngưỡng −17.87 [−19.86, −15.87], phần do điểm +2.30 [−0.15, +4.75]. EXP2: −17.25 và +2.00 (tổng −15.25) | Phân rã theo mốc đã chọn, không phải nguyên nhân, và **không loại trừ** mọi ảnh hưởng của điểm khối đích: CI của phần do điểm rộng, thứ hạng vẫn giảm (HC4), và đổi mốc sẽ đổi hai phần. Tỉ lệ phần do ngưỡng trên tổng ở đây khoảng 115%, vì phần do điểm ngược dấu. Vì vậy "phần lớn" phải định nghĩa không qua tỉ lệ (gap 1) |
| C6 | Bộ chọn ngưỡng tăng ngưỡng chủ yếu qua đặc trưng `mean`, với trọng số âm. Khi đệm có cấu trúc, xác suất trung bình của các cặp chéo (đích × đệm, đều là không-cạnh theo thiết kế) giảm. Khối chéo đóng góp lớn nhất vào Δℓ ở cấu hình này | EXPLORATORY (P-N3 phần A, EXP2, 20 hệ RFF) | Δℓ +0.855 [+0.679, +1.032]; Shapley khối chéo +0.513 (60%), khối đệm +0.352 (41%), khối đích −0.010. Trọng số `mean` −8.56. Xác suất trung bình của khối chéo 0.362 → 0.189 (mô tả hậu nghiệm) ([P-N3](../n3_mechanism_pilot_2026-11-21/PN3_results_vi.md) §1) | **Chưa kiểm trên seed mới.** Trung bình của khối đệm (0.546 → 0.405) **gộp cả cạnh thật** của khối đệm ở e_T, nên không dùng được để kết luận về riêng các cặp không-cạnh của khối đệm; chỉ khối chéo cho kết luận về không-cạnh. Thứ hạng giữa khối chéo và khối đệm phụ thuộc cấu hình, vì tỉ lệ số cặp chéo/đệm là 2·d_T/(k − 1). Chưa giải thích vì sao CDFM cho các cặp chéo điểm cao hơn khi đệm độc lập |
| C7 | Ở AVICI: số cạnh giảm rõ ở cả hai họ; ở RFF có mất thứ hạng; ở tuyến tính, thay đổi thứ hạng chưa rõ | XÁC NHẬN (HA1, HA2, HA5), MÔ TẢ (thứ hạng ở tuyến tính) | Như C3. AUROC ở tuyến tính +0.027 [+0.011, +0.044] ở HELD2, nhưng không thuộc bộ kiểm | Ở tuyến tính, không được claim chiều của thứ hạng |
| C8 | **Kết quả âm:** can thiệp attention (value zeroing, knockout, theo lớp) chưa phân biệt được cơ chế của AVICI | EXPLORATORY (P-N3 phần B) | Không có ứng viên. Các can thiệp xóa nhiều hiệu ứng nhất không đạt tiêu chí sàng lọc về chất lượng; V0-8 chỉ vừa vượt ngưỡng (−0.0313 [−0.0639, +0.0012]). KO-all là kiểm tra kỹ thuật | Báo như một giới hạn. Không được claim "attention không liên quan" |
| C9 | Một bước rẻ (sàng lọc phụ thuộc biên, rồi chạy theo thành phần) đưa các contrast trung bình xuống dưới biên. Có đánh đổi chất lượng ở một ô | MÔ TẢ (phân tích phụ ở HELD2) | Mọi REP sau R đều SMALL. Là cách sửa có ích ở 3/4 ô; với CDFM tuyến tính, giá tại k0 là −0.018 [−0.031, −0.005]. Không bất biến ở từng hệ (một hệ đổi 11 cạnh) | Không được Holm xác nhận. α_HSIC là mức danh nghĩa (đuôi gamma dễ dãi). Kết quả có được khi cột thêm vào **độc lập với khối đích theo thiết kế** (cột tổng hợp). Điều đó vẫn đúng khi thêm cột tổng hợp vào dữ liệu thật (gap 2), nhưng không áp dụng được cho các biến có sẵn trong dữ liệu thật mà không biết có liên quan hay không. Chưa so với các cách sửa khác theo thông tin mỗi cách dùng (gap 3) |
| C10 | Định vị: nguyên lý nhất quán khi đổi tập biến đã có. Đóng góp là failure cụ thể với đáp án biết trước, đường ảnh hưởng đã cô lập ở CDFM, và phạm vi của cách sửa | PRIOR ART | Self-Compatibility (AISTATS 2024); Grinsztajn (NeurIPS 2022); TabPFN (ICLR 2023 §B.3.2); Noise Immunity (2026); Aliferis 2010; CausalArena (2026, không có phép đối sánh này). Montagna et al. (TMLR 2025) chỉ là khung diễn giải về prior huấn luyện. [Cập nhật 21/11](N1_prior_art_update_2026-11-21_vi.md) | Chưa phải systematic review; phải lặp lại tìm kiếm trước khi gửi |

## 2. Phần còn thiếu, theo thứ tự user đã chốt

1. **Gap 1: kiểm chứng bổ sung cho CDFM, trước khi chốt bài** (không chặn việc viết).
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
2. **Gap 2: yêu cầu nhất quán cần kiểm tra trên dữ liệu thật.**
   - **Logic:** cột thêm vào là cột tổng hợp, độc lập với khối thật theo thiết kế. Quan hệ thật trong khối thật vì vậy không đổi. Nhưng một bộ ước lượng hữu hạn mẫu không bắt buộc cho output trùng hệt. Vì không có ground truth, phép thử chỉ đo **độ bất ổn**, không đo độ chính xác.
   - **Yêu cầu thiết kế:**
     - giữ nguyên khối thật và tiền xử lý; khối thật trùng từng bit giữa các input;
     - lặp lại việc sinh khối đệm (nhiều bản rút cho mỗi bộ dữ liệu và mỗi kiểu đệm);
     - kiểm soát randomness của model: seed cố định, đo τ_rep như P-N1;
     - có đối chứng cổ điển (PC, GES) trên đúng các input đó, làm mốc bất ổn hữu hạn mẫu;
     - **không dùng độ ổn định thay cho độ chính xác:** một model ổn định vẫn có thể sai.
   - **Biến đo:** số cặp đổi trạng thái, Δm, |Δm|, ngưỡng CDFM; theo từng bản rút đệm.
   - Cần user duyệt việc chọn và tải bộ dữ liệu.
3. **Gap 3: so sánh cách sửa, ghi rõ thông tin mỗi cách dùng.**

   | Cách | Thông tin dùng | Vai trò |
   |---|---|---|
   | R (sàng lọc rồi chạy theo thành phần) | chỉ dữ liệu input; không biết khối nào là đích | cách sửa ứng viên |
   | FIXED 0.5 | không dùng thêm thông tin; bỏ bộ chọn ngưỡng của CDFM | đối chứng decoder |
   | Ngưỡng cục bộ của CDFM | biết khối đích: đặc trưng ngưỡng chỉ tính trên khối đích | **đối chứng**, không ngang hàng với R |
   | FROZEN | dùng lần chạy k0 trên riêng khối đích | **đối chứng**, không ngang hàng với R |
   | R-oracle | biết ranh giới đích/đệm | kiểm sanity; trùng k0 theo cấu trúc |

   - Mỗi cách đo cả độ đổi lẫn chất lượng tại k0.
   - MambaPFN không vào so sánh: chỉ ở related work ([cập nhật prior art](N1_prior_art_update_2026-11-21_vi.md) §2).
4. **Gap 4: phạm vi model.**
   - FoundCause mới ở mức P-N1.
   - TabCausal: checkpoint `tabcausal-base.pt` có sẵn trong bản clone ở máy, chưa cài ([manifest](../n1_irrelevant_vars_2026-11-13/DATA_MANIFEST_vi.md) §1). Chỉ dùng cho C1, nếu cài được trong venv riêng.
5. **Gom thống kê trong lúc viết** (không phải bước riêng):
   - mỗi bảng của bài ghi bộ dữ liệu (P-N1 EXP/HELD, EXP2, HELD2), giả thuyết đã khóa (file luật), phép kiểm và mức bằng chứng;
   - bảng các pha và cổng toàn vẹn đưa vào appendix;
   - mã commit và thời điểm push để ở tài liệu bổ sung, vì bài có thể được review ẩn danh.

## 3. Khung bản thảo (tiếng Anh; bản nháp đang viết)

1. **Introduction:** target-block conclusions of pretrained causal discovery models depend on appended, provably irrelevant variables.
2. **Related work:** consistency across variable sets (self-compatibility); robustness of tabular foundation models to uninformative features; amortized causal discovery and training priors.
3. **Setup:** an invariance test with a known required answer; models; padding families; measures that separate edge count, ranking and threshold; the locked exploratory → held-out protocol.
4. **Failure** (C1, C2).
5. **Padding structure at fixed D** (C3, C4, C7).
6. **Channels** (C5, C6, C8): CDFM's global threshold selector; what attention interventions on AVICI could and could not show.
7. **Mitigation and its scope** (C9).
8. **Limitations:** synthetic scope; two to three checkpoints; nominal HSIC level. We identify the influence path through CDFM's threshold selector, but we do not explain why the model produces those score changes, and we do not distinguish AVICI's mechanism. The real-data consistency check is open.

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
