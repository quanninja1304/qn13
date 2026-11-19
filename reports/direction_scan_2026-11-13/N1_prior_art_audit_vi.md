# Audit prior art cho N1: "Dữ liệu không liên quan có làm mô hình causal discovery học sẵn đổi kết luận không?" (13/11/2026)

> **Câu hỏi audit:** đã có ai đo xem một mô hình causal discovery **học sẵn** (amortized / foundation model, đọc cả bảng dữ liệu một lần) có thay đổi dự đoán cho một hệ đích khi ta **thêm các biến độc lập** với hệ đó vào bảng hay chưa? Và kiến trúc của các mô hình này có bảo đảm tính bất biến đó không?
>
> **Phạm vi:** 7 lượt tìm kiếm; 8 bài đọc có mục tiêu qua agent fetch (AVICI 2022; Montagna et al. TMLR 2025; CausalArena 2026; Arrow 2026; DAG-FM 2026; FoundCause 2026; survey Causal Foundation Models 2026; SEA 2024). Phần lớn bài chỉ đọc được 40k ký tự đầu nguyên văn, phần sau qua tóm tắt của agent; chỗ nào dựa vào tóm tắt được ghi [summary].
> **Nhãn:** [Verified-fetch] có trích nguyên văn; [summary]; [Verified-search]; [Inference]; [Hypothesis].

## 1. Kết luận audit

**Gap đứng vững trong phạm vi đã quét.** Không bài nào trong tám bài, và không kết quả tìm kiếm nào, thử nghiệm việc thêm biến độc lập vào một bảng cố định rồi đo thay đổi dự đoán trên khối biến đích. Hơn thế:

1. **Benchmark mới nhất loại trường hợp này ra khỏi thiết kế.** CausalArena (2026), benchmark cho 7 mô hình học sẵn (AVICI, SEA, Arrow, CauScale, CDFM, FoundCause, TabCausal) cộng 11 phương pháp cổ điển, có bộ lọc hợp lệ từ chối đồ thị có "no isolated variables" và bỏ các cặp gần trùng, đồng thời loại "low-information variables" khi kiểm soát đa dạng [Verified-fetch, App. A.1, A.2]. Nghĩa là nếu lỗi tồn tại, benchmark hiện hành **không thể thấy** nó. Đây đúng là loại "thiết kế đánh giá không tách được hai thứ" mà bộ lọc của ta tìm.
2. **DAG-FM tự ghi "we perform no feature dropout to strictly satisfy the causal sufficiency assumption"** [Verified-fetch, §4.2]: mô hình chưa từng thấy biến thừa trong huấn luyện.
3. **Kiến trúc không bảo đảm bất biến.** Mọi mô hình đều có self-attention softmax **trên trục biến**: AVICI "alternates in attending over the observation and the variable dimension"; Arrow có context transformer để "each embedding incorporate information from all other embeddings"; FoundCause "alternating attention over samples and variables" [Verified-fetch]. Tính chất được các tác giả nêu chỉ là **permutation equivariance** ("permuting variables relabels the outputs accordingly"), không phải bất biến khi **thêm** biến: một cột mới đi vào mọi softmax và mọi tóm tắt gộp, nên logit của các cặp cũ có thể đổi [Inference từ kiến trúc, các tác giả không bàn].
4. **Hiệu ứng tương tự đã được xác lập ở bài toán dự báo trên bảng**: TabPFN v1 "less robust to uninformative features than LightGBM" (Hollmann et al. 2022), TabPFN v2 được báo cáo là "very robust to uninformative features" (Nature 2025), và có hẳn một bài 2026 đo riêng tính "noise immunity" theo số cột ngẫu nhiên [Verified-search]. Tức là cộng đồng tabular FM coi đây là một trục đánh giá chuẩn; cộng đồng causal-discovery FM chưa đo nó.
5. **Điểm đối chứng lý thuyết sạch:** với PC, FCI, GES, thêm biến độc lập **không đổi output tiệm cận** (các biến đó bị tách ở bậc 0 và không bao giờ vào tập điều kiện của các cặp đích; điểm BIC tách rời theo nút) [Inference, kết quả chuẩn]. Ở mẫu hữu hạn chỉ có lỗi kiểm định bội. Vậy có một mốc tham chiếu rõ: mô hình học sẵn có giữ được tính chất mà thuật toán cổ điển có "miễn phí" hay không.

**Hai kết quả đã biết được giao nhau:** (a) độ nhạy của tabular foundation model với cột không liên quan (đã đo cho dự báo); (b) tính bất biến của thuật toán causal discovery cổ điển với biến độc lập (đã biết). Chưa ai đo (a) cho causal discovery và so với (b).

## 2. Bảng prior art

| Bài | Thử thay đổi d? | Thử thêm biến độc lập? | Điều liên quan | Nhãn |
|---|---|---|---|---|
| AVICI, Lorch et al., NeurIPS 2022 | Có: huấn luyện d ∈ [2, 50], thử d = 100 | **Không** | Attention luân phiên trên hai trục; equivariant; chuẩn hóa từng biến; OOD về graph type, noise, mechanism | Verified-fetch (§4.2, §5.1); phần OOD [summary] |
| Montagna et al., *Demystifying amortized causal discovery with transformers*, TMLR 2025 | Không (chỉ hai biến) | Không | "the training distribution implicitly defines a prior on the causal model of the test observations"; CSIvA "can not generalize to classes of causal models unseen during training" | Verified-fetch |
| CausalArena, 2026 (arXiv 2609.11897) | Có: d ∈ {10, 20, 30, 50, 100} | **Không; loại biến cô lập khỏi benchmark** | Stress test về weak signal, noise, warping, outlier, missing, intervention; cảnh báo "a test score may reflect not only causal structure-learning ability" | Verified-fetch |
| Arrow, Thompson et al., 2026 (2605.07204) | Có: p ∈ [2, 100] huấn luyện, thử tới 107 | Không | "we will soon publicly release its weights" | Verified-fetch; OOD [summary] |
| DAG-FM, Chen et al., 2026 (2607.11510) | Có: d tới 500 [summary] | Không; "no feature dropout" | Mật độ đồ thị huấn luyện lấy mẫu từ [0, 1] | Verified-fetch |
| FoundCause, Amazon, 2026 (2606.17516) | Có: D ∈ [2, 50] huấn luyện, thử 100 [summary] | Không | Dự đoán DAG + ma trận confounding; permutation augmentation chống shortcut [summary, chưa xác minh]; checkpoint 1.6 GB trên GitHub (repo đã archive 06/2026) | Verified-fetch một phần |
| SEA, Wu et al., ICLR-W 2024 (2402.01929) | — | Không | Dùng thống kê cổ điển trên tập con rồi gộp; **có thể gần bất biến**, là đối chứng tốt; mã công khai | Verified-search |
| Survey *Causal Foundation Models*, 2026 (2609.03003) | — | Không nêu là open problem | Open problem được nêu: "quantitative measures of causal prior coverage" | [summary] |
| TabPFN v1 2022, v2 Nature 2025; *Noise immunity in in-context tabular learning* 2026 (2604.04868) | — | **Có, cho dự báo** | Trục đánh giá chuẩn trong tabular FM | Verified-search |

**Lỗ hổng của audit:** chưa đọc nguyên văn phần OOD của AVICI và Arrow, chưa đọc TabCausal (2605.31156) và CDFM (2607.11508), chưa tìm trong các bài về "size generalization" của GNN. Rủi ro còn lại là một phụ lục ở đâu đó đã có "random noise columns" như một ablation nhỏ. Mức rủi ro: trung bình-thấp; kể cả có, chưa ai đặt nó thành câu hỏi với cơ chế và đối chứng cổ điển.

## 3. Câu hỏi "vì sao" và cơ chế có thể kiểm

Nếu mô hình không bất biến, có ba cơ chế ứng viên, mỗi cái có đòn bẩy riêng [Hypothesis]:

| Cơ chế | Dự đoán | Đòn bẩy phân biệt |
|---|---|---|
| **M1. Prior về mật độ.** Mô hình học "số cạnh kỳ vọng theo d" từ dữ liệu huấn luyện (ER với O(d) cạnh); thêm k biến độc lập làm d tăng nhưng số cạnh không, nên mô hình hạ ngưỡng hoặc thêm cạnh để khớp prior | Số cạnh dự đoán trong khối đích **tăng** theo k; cạnh giả nối đích với biến thêm xuất hiện | So "thêm k biến độc lập" với "thêm k biến tạo thành khối có cấu trúc riêng" (cùng d, khác mật độ) |
| **M2. Pha loãng attention.** Softmax trên trục biến chia khối lượng cho nhiều biến hơn, làm biểu diễn của biến đích mờ đi | Xác suất cạnh đích **giảm đều** theo k, không phụ thuộc cấu trúc của biến thêm | So biến thêm độc lập với biến thêm là bản hoán vị của chính các cột đích (cùng phân phối biên) |
| **M3. Thống kê toàn cục.** Nếu mô hình dùng tóm tắt toàn bảng (như CDFM, SEA dùng thống kê cổ điển), biến thêm đổi tóm tắt | Nhạy với **phân phối** của biến thêm (Gauss so với đuôi nặng) hơn là với số lượng | Thay phân phối của biến thêm, giữ k |

Mô hình cổ điển (PC, GES, FCI) chạy cùng dữ liệu cho mốc "chỉ có lỗi kiểm định bội".

## 4. Thiết kế pilot P-N1 (sơ bộ; luật đọc sẽ viết riêng và khóa trước khi chạy)

- **Mô hình:** AVICI (3 checkpoint công khai, JAX, chạy CPU được), CDFM (checkpoint HF, Apache 2.0), FoundCause (checkpoint GitHub), SEA (mã công khai; đối chứng "gần bất biến"), Arrow nếu kịp phát hành. Cổ điển: PC, GES, FCI (causal-learn, đã có).
- **Hệ đích:** (i) DAG tổng hợp trong phân phối huấn luyện của từng mô hình (ER, d_target ∈ {10, 20}, n = 1000), để lỗi không thể đổ cho OOD; (ii) Sachs (11 biến, đồ thị đồng thuận); (iii) cấu trúc bnlearn đã có trong repo với SEM tuyến tính.
- **Đòn bẩy:** nối thêm k ∈ {0, 5, 10, 20, 40} cột: (a) Gauss độc lập; (b) khối độc lập có cấu trúc riêng; (c) bản hoán vị hàng của chính các cột đích; (d) độc lập đuôi nặng. Mỗi điều kiện giữ **nguyên** n hàng của hệ đích. Chuẩn hóa từng cột như mô hình yêu cầu, nên tiền xử lý không đổi theo k (loại trừ rủi ro mà bảng N1 đã nêu).
- **Đo trên khối đích:** trung bình |Δp_ij| so với k = 0; ΔF1 và ΔSHD trong khối đích; số cạnh dự đoán trong khối đích (cho M1); số cạnh giả đích↔thêm; với mô hình có hoán vị test-time, trung bình trên K hoán vị.
- **Luật đọc (dự kiến):** "KHÔNG BẤT BIẾN" nếu ΔF1 trong khối đích ở k = 20 vượt 0.05 với cận dưới CI > 0 (bootstrap theo hệ đích) ở ít nhất 2/3 mô hình học sẵn, trong khi PC/GES thay đổi dưới 0.02; cơ chế đọc theo bảng §3. Mọi nhánh báo cáo được: bất biến thì là claim dương về khả năng "biên hóa" của mô hình học sẵn, và CausalArena nên thêm trục này.
- **Chi phí:** không cần GPU, không cần R hay Java; cần `pip install` JAX CPU, torch CPU, và tải checkpoint (FoundCause 1.6 GB). RAM 7.8 GB đủ cho d ≤ 60.

## 5. Rủi ro

| Rủi ro | Mức | Giảm thế nào |
|---|---|---|
| Mô hình mạnh (Arrow, CDFM) hóa ra bất biến như TabPFN v2 | Trung bình | Vẫn là kết quả; bài thành "những mô hình nào bất biến và nhờ cơ chế gì", kèm đề xuất trục cho CausalArena |
| Nhóm CausalArena thêm trục này vào bản sau | Trung bình | Pilot trong 1–2 tuần; preprint phần đo lường sớm |
| Hiệu ứng do tiền/hậu xử lý | Thấp | Chuẩn hóa theo cột không phụ thuộc k; ngưỡng cạnh dùng theo mặc định của từng mô hình và báo cả đường cong AUPRC |
| Checkpoint không chạy trên Windows CPU | Thấp-trung bình | AVICI JAX có bản CPU; dự phòng WSL |
| Reviewer: "chỉ là một ablation" | Trung bình | Trụ phải là cơ chế (M1–M3) và đối chứng cổ điển, không chỉ con số |

## 6. So với C1 sau audit

- **Gap:** cả hai đều đứng; C1 có chữ của tác giả, N1 có bằng chứng "benchmark loại trường hợp này ra" cộng tương tự đã biết ở tabular FM.
- **Trần:** N1 cao hơn (đối tượng là foundation model, có 7 mô hình để đo, có cơ chế để giải thích). C1 là metric cộng xếp hạng lại.
- **Chi phí khởi động:** N1 cần cài model; C1 dùng được 70% mã có sẵn. Cả hai không cần GPU; chỉ C1 cần R và Java ở pilot thứ hai.
- **Khuyến nghị:** **N1 làm hướng chính, C1 dự phòng có pilot thiết kế sẵn.**

## 7. Bài cần tải thêm cho N1

| # | Bài | Nguồn | Vai trò |
|---|---|---|---|
| 1 | Lorch, Sussex, Rothfuss, Krause, Schölkopf, *Amortized inference for causal structure learning* | NeurIPS 2022; arXiv `2205.12934` | Mô hình đầu tiên; đọc §4.2, §6, App. C, E |
| 2 | Montagna et al., *Demystifying amortized causal discovery with transformers* | TMLR 2025; arXiv `2405.16924` | Lý thuyết "training distribution là prior" (nền cho M1) |
| 3 | Li et al., *CausalArena: benchmarking causal discovery in the foundation model era* | arXiv `2609.11897` | Benchmark; bộ lọc loại biến cô lập |
| 4 | Thompson et al., *Arrow* | arXiv `2605.07204` | Mô hình mạnh nhất 2026 |
| 5 | Chen et al., *DAG-FM* | arXiv `2607.11510` | "no feature dropout" |
| 6 | *FoundCause* | arXiv `2606.17516` | Có latent; checkpoint |
| 7 | Wu, Bao, Barzilay, Jaakkola, *Sample, estimate, aggregate* | ICLR-W 2024; arXiv `2402.01929` | Đối chứng gần bất biến |
| 8 | Qiao et al., *CDFM* | arXiv `2607.11508` | Checkpoint HF |
| 9 | Li et al., *TabCausal* | arXiv `2605.31156` | Chưa audit |
| 10 | Hollmann et al., TabPFN, *Nature* 2025 | `10.1038/s41586-024-08328-6` | Tiền lệ "uninformative features" |
| 11 | *Noise immunity in in-context tabular learning* | arXiv `2604.04868` | Thiết kế trục irrelevant features |
| 12 | Ke et al., *Learning to induce causal structure* (CSIvA) | ICLR 2022; arXiv `2204.04875` | Bối cảnh |
