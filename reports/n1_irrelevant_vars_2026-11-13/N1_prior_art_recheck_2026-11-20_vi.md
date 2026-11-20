# N1: kiểm lại prior art sau held-out, trước nghiên cứu cơ chế (20/11/2026)

> **Mục đích:** user chọn hướng 2 (nghiên cứu cơ chế mới) và yêu cầu kiểm prior art trước. Lượt này trả lời hai câu: (1) đã có ai báo cáo đúng phát hiện đã lặp lại của N1 chưa; (2) các đòn bẩy dự định cho nghiên cứu cơ chế đã có tiền lệ chưa, kể cả ở lĩnh vực gần (tabular foundation model, causal discovery cổ điển).
> **Phạm vi:** bổ sung cho [audit 1](../direction_scan_2026-11-13/N1_prior_art_audit_vi.md) và [audit 2](../direction_scan_2026-11-13/N1_prior_art_second_audit_vi.md) (13/11, 13 nguồn, 6 truy vấn). Lượt này có 21 truy vấn mới; 7 bài đọc trực tiếp qua agent đọc trang (phần lớn nguyên văn, một số đoạn chỉ có tóm tắt, ghi rõ ở dưới); mã và config của AVICI, CDFM đọc trên máy; khoảng 9 nguồn chỉ ở mức kết quả tìm kiếm hoặc abstract. **Đây không phải systematic review;** "không thấy" nghĩa là không thấy trong các nguồn này.
> **Nhãn mức đọc:** [V-text] đọc nội dung bài; [V-code] đọc mã hoặc config; [V-search] chỉ abstract hoặc snippet; [Not-read] chưa đọc được.
> **Đính chính 20/11, sau review của user:** §1–§6 được sửa tại chỗ; danh sách thay đổi và lý do ở §7. Bản trước đính chính là commit `940b50e`. Các đoạn nguồn bị review nêu đã được đọc lại (Noise Immunity v2, FoundCause v2 App. C, E, G) hoặc kiểm trong mã (CDFM, AVICI).

## 1. Kết luận

1. **Không tìm thấy bài nào báo cáo đúng phát hiện của N1:** thêm cột độc lập vào một khối đích cố định làm mô hình causal discovery học sẵn đổi và làm xấu output cấu trúc của khối đích, trong khi PC/GES gần như không đổi.
   - Benchmark mới nhất cho đúng nhóm model này (CausalArena, 09/2026, gồm AVICI, CDFM, FoundCause) **không có phép đối sánh giữ nguyên khối đích rồi thêm khối khác**.
   - Bộ lọc "no isolated variables" của CausalArena loại kiểu đệm như A (cột cô lập). Theo câu chữ, nó không loại một khối độc lập có cạnh như B (suy luận).
   - Kết luận này chỉ trong phạm vi các nguồn đã đọc.
2. **Nguyên lý đánh giá đã có từ trước.** Self-Compatibility (Faller et al., AISTATS 2024) kiểm xem output của một thuật toán CD chạy trên các tập con biến có tương thích với nhau không.
   - Phép so k0 với k = 20 của N1 là một trường hợp riêng. Tập lớn là đích ∪ đệm; vì đệm độc lập, đồ thị biên trên khối đích không đổi, nên output trên khối đích phải trùng nhau.
   - N1 không được claim nguyên lý này. Phần có thể đóng góp là phép thử cụ thể, failure đã lặp lại và lời giải thích cơ chế.
3. **Hiện tượng gần đã được biết rõ ở bài toán dự đoán:** mạng nơ-ron cho dữ liệu bảng và TabPFN tệ đi khi thêm feature vô thông tin (Grinsztajn et al. NeurIPS 2022; Hollmann et al. ICLR 2023). Hai bài này dùng **đúng** hai kiểu đệm của mình: Gauss độc lập (≈ A) và cột thật bị xáo trộn (≈ C). Ở causal discovery cổ điển đã có Aliferis et al. 2010 (thêm 7 990 biến không liên quan) và Runge et al. 2019 (điều kiện trên biến không liên quan làm giảm power). Vì vậy N1 **không** được trình bày là "mạng nơ-ron bị feature thừa làm hại" hay "lần đầu thêm biến không liên quan".
4. **Phần có thể mới**, ở mức suy luận:
   - đo trên **output cấu trúc** của khối đích, với đối chứng cổ điển gần bất biến;
   - khối đệm có cấu trúc (B) làm đổi việc chọn cạnh ở khối đích **khác nhau giữa các model**:
     - Theo F1: AVICI tệ hơn với B; CDFM và FoundCause đỡ hơn. Dấu này lặp lại ở held-out.
     - Theo số cạnh: AVICI và CDFM cùng chiều (ít cạnh hơn với B); FoundCause ngược lại.
     - Phân tích hậu nghiệm ([PN1_HELD_posthoc_rank_level_vi.md](PN1_HELD_posthoc_rank_level_vi.md)) cho thấy chênh lệch F1 giữa AVICI và CDFM chủ yếu đến từ điểm xuất phát (ở k0, AVICI dự đoán thiếu cạnh, CDFM dự đoán thừa). Ở CDFM, việc đổi ngưỡng NATIVE góp thêm một phần, nhưng dấu của contrast B − A phụ thuộc cách chọn ngưỡng. Dữ liệu không cho thấy hai cơ chế ngược nhau, và cũng không cho thấy hai model cùng cơ chế.
   - prior mật độ gắn với d trong bộ sinh huấn luyện đã được xác minh trên tài liệu (§3), nhưng **chưa** có phép thử trực tiếp. Riêng số biến không giải thích hết hiện tượng, vì A và B đã khác nhau ở cùng D.
5. **Hai rủi ro cho tính đáng kể của bài:**
   - (a) một bước tiền xử lý cổ điển rẻ (sàng lọc phụ thuộc biên, tách thành phần liên thông, chạy model trên từng thành phần) có thể xóa phần lớn mức hại.
     - Nếu vậy, bài phải đóng khung là "failure + cơ chế + cách sửa rẻ". Đó vẫn là kết quả có ích, nhưng không còn là "vấn đề chưa giải".
     - Cách sửa này chưa chắc thắng: kiểm nhiều cặp sẽ sinh cạnh giả, có thể nối hai khối lại (§5, nhánh R);
   - (b) cách sửa ở phía prior đã được đề xuất cho TabPFN (đưa feature vô thông tin vào prior huấn luyện), nên không thể claim là ý mới.

**Quyết định đề xuất:** đủ cơ sở để thiết kế nghiên cứu cơ chế; chưa đủ để claim ưu thế xuất bản. Thiết kế phải có **nhánh cách sửa cổ điển** làm baseline (§5).

## 2. Ma trận bằng chứng (nguồn mới so với audit 13/11)

| Nguồn, trạng thái, DOI | Bài làm gì | Liên quan tới N1 | Giới hạn hoặc ghi chú | Mức đọc |
|---|---|---|---|---|
| **CausalArena**, Li, Liu, Wang, Ye; preprint v1 10/9/2026; `10.48550/arXiv.2609.11897` | Benchmark causal discovery thời foundation model; 10 họ đồ thị; stressor quan sát (warping, outlier, missing, corruption); đánh giá Arrow, AVICI, CauScale, CDFM, FoundCause, SEA, TabCausal | **Không có** phép đối sánh giữ nguyên khối đích rồi thêm khối khác. App. A.1: "candidate graphs are resampled until they are DAGs with no isolated variables". Bộ lọc này loại cột cô lập như kiểu A. Theo câu chữ, nó không loại khối độc lập có cạnh như kiểu B (suy luận) | Phần giữa bài (§4.2–6) chỉ có tóm tắt của agent | V-text (một phần) |
| **Self-Compatibility: Evaluating Causal Discovery without Ground Truth**, Faller, Vankadara, Mastakouri, Locatello, Janzing; **AISTATS 2024** (PMLR 238:4132–4140); `10.48550/arXiv.2307.09552` | Đánh giá CD không cần ground truth: "causal learning should seek stability across subsets of variables". Chạy thuật toán trên các tập con biến, kiểm các đồ thị có cùng là latent projection của một DAG chung | Nguyên lý "output phải nhất quán khi đổi tập biến" đã có. Phép so k0 với k = 20 của N1 là trường hợp riêng với tập lớn = đích ∪ đệm. Đệm độc lập nên đồ thị biên trên khối đích không đổi và output phải trùng | Phần đã đọc (tới §2.3) chỉ bàn tập con, không bàn thêm khối độc lập. Thuật toán nêu trong phần lý thuyết là PC, FCI, RCD; không thấy model học sẵn. Phần thí nghiệm chưa đọc | V-text (tới §2.3) |
| **Causal Foundation Models** (tutorial), Stith, Rahmani, Cresswell; preprint v1 2/9/2026; `10.48550/arXiv.2609.03003` | Giới thiệu CFM cho ước lượng hiệu ứng; §5.3 tổng quan causal discovery | Không bàn biến thừa hay tính nhất quán khi thêm biến. §3.2: "no research has been published on the quality of priors for CFMs"; §5.5 nêu bài toán mở "automatic detection of mismatch between the target DGP and the training prior" | Chủ yếu về ước lượng hiệu ứng | V-text |
| **TabPFN**, Hollmann, Müller, Eggensperger, Hutter; **ICLR 2023** (trang poster ICLR); `10.48550/arXiv.2207.01848` | Dự đoán phân loại bằng PFN | §B.3.2: "Uninformative features are generated by copying existing features and shuffling their values" (≈ kiểu C); "TabPFN and MLPs are less robust to uninformative features than LightGBM"; cách sửa: "including more uninformative features in the used prior"; App. A: "we did not consider the existence of many uninformative features in our prior" | Dự đoán, không phải học cấu trúc | V-text |
| **Why do tree-based models still outperform deep learning on typical tabular data?**, Grinsztajn, Oyallon, Varoquaux; **NeurIPS 2022 Datasets & Benchmarks** (trang proceedings); `10.48550/arXiv.2207.08815` | So sánh cây và mạng nơ-ron trên dữ liệu bảng | §5.3 "Finding 2: Uninformative features affect more MLP-like NNs"; feature thêm vào "sampled from standard Gaussians uncorrelated with the target and with other features" (≈ kiểu A) | Dự đoán | V-text |
| **Noise Immunity in In-Context Tabular Learning: An Empirical Robustness Analysis of TabPFN's Attention Mechanisms**, Hu, Ghelichi; preprint v2 7/4/2026; `10.48550/arXiv.2604.04868` | TabPFN với feature ngẫu nhiên (§3.2.1) và feature tương quan (§3.2.2), dữ liệu `make_classification` với 2 feature có thông tin | Feature tương quan được sinh từ biến đổi phi tuyến của 2 feature có thông tin (App. A), tức là dư thừa với tín hiệu, **không** phải một khối độc lập với đích như kiểu B. ROC-AUC không giảm ở cả hai loại: "ROC-AUC again remains high without any performance drop". Attention dịch dần sang cột dư thừa: ở lớp 12, tỉ lệ attention của feature có thông tin so với phần còn lại giảm từ 81 xuống 6.2 khi có 128 cột tương quan (App. B, Bảng 4). **Không** phải bằng chứng rằng đệm có phụ thuộc làm giảm chất lượng. Có ích theo hướng khác: attention dồn sang cột thừa mà hiệu năng không giảm, nên chỉ đo attention thì không đủ để quy nguyên nhân | Dự đoán; chỉ chẩn đoán attention, không can thiệp; phân phối của feature ngẫu nhiên không được nêu | V-text (HTML v2, đọc lại 20/11) |
| **FoundCause** v2, Blöbaum, Balasubramanian, Kasiviswanathan; preprint, **v2 17/11/2026**; `10.48550/arXiv.2606.17516` | Model của mình | §2: "we sample problems with D∈[2,50] variables". App. G: hai đường sinh. Đường DoWhy "is produced by the DoWhy path described in Appendix G.1 with probability 0.5ζ" (ζ: độ khó của task); "the other tasks use a custom diverse-graph generator" (Barabási–Albert, Watts–Strogatz, SBM, geometric, star/hub, deep single-root, biological). App. G.1 (DoWhy): "q=min(q0, k/(Dtot−1))", với q0 đều trên [0.10 − 0.08ζ, 0.40] và k = max(1, round(a)), a phân phối mũ trung bình 3. Mỗi nút không phải gốc nhận 1 + round(q(Dtot − 2)) cha; "the graph is connected"; "the same q is passed to the diverse-graph generator". App. E: "variable dropout" chỉ lúc huấn luyện (20% task che toàn bộ quan sát của một biến). App. C: cột hằng hoặc quá thưa "returned as isolated nodes", cột trùng lặp không nối với bản sao, chỉ lúc suy luận. **Không** có phép thử thêm biến | Mật độ thực tế và tính liên thông của bộ sinh đa dạng không được nêu, mà đường này chiếm ít nhất một nửa số task. "Mật độ ∝ 1/(D − 1)" chỉ đúng khi trần k/(Dtot − 1) nhỏ hơn q0; khi D nhỏ, q = q0 và số cha tăng theo D. App. I–J chưa đọc | V-text (App. C, E, G nguyên văn, đọc lại 20/11) |
| **CDFM**, Qiao et al.; preprint v1 13/7/2026; `10.48550/arXiv.2607.11508` | Model của mình | §5.4: sáu họ đồ thị (ER, SF, SFT, WS, SBM, GRG), d ~ U[2, 100], "expected number of edges per variable is uniformly sampled from {1,2,3}"; kết nối không được nói. §5.3: "b0 is a learned global bias representing the baseline sparsity prior". Trong mã, đó là **một tham số vô hướng cố định** (`final_bias`, khởi tạo −3.0) cộng như nhau vào mọi logit, nên tự nó không tạo khác biệt A–B. Ngưỡng NATIVE do `suggest_threshold` chọn từ 10 đặc trưng tính trên **toàn** ma trận D×D (mean, std, các percentile, logD, median gap, max gap, knee). §6.2: quét D từ 10 đến 100, không phải can thiệp có đối chứng | Bảng 7–8, phụ lục chưa đọc. `suggest_threshold_by_density` (mặc định 2/D) là hàm phụ; runner của mình không dùng | V-text, V-code (`graph_inference.py`, `utils.py`) |
| **AVICI `scm-v0`**, Lorch et al.; config huấn luyện của tác giả | Model của mình | `config/train/scm-v0.yaml` tại `40fb30d`: d ∈ {2, …, 100}; ER, SF, SF-transpose, SBM với `edges_per_var` ∈ {1, 2, 3}; SBM `damp` 0.1; thêm WS và GRG | ER với 1 cạnh/nút tự nhiên có nút cô lập; SBM có khối nối yếu | V-code |
| **DCD-PFN**, Guan et al. (Kuang); preprint v1 19/6/2026; `10.48550/arXiv.2606.21212` | Foundation model **cục bộ**: tìm Markov boundary rồi ghép đồ thị | Lý do làm cục bộ là precision và chi phí, **không** phải biến thừa; không có phép thử thêm biến; chỉ so với AVICI ở d ≤ 20 | Một kiến trúc có thể bền hơn theo thiết kế: ứng viên baseline cách sửa | V-text |
| **A Knowledge-Informed Pretrained Model for Causal Discovery**, Xu et al. (Cui); preprint 3/2026; `10.48550/arXiv.2603.20842` | Model học sẵn dùng thêm prior knowledge, curriculum theo độ mạnh prior và mật độ | Không về biến thừa | — | V-search |
| **CauScale**, Peng et al.; ICML 2026 (trang poster); `10.48550/arXiv.2602.08629` | Mở rộng neural CD tới 1 000 nút | Không thấy phép thử biến thừa | — | V-search |
| **Since Faithfulness Fails**, Olko et al.; ICML 2025 (PMLR v267); `10.48550/arXiv.2502.16056` | Giới hạn của neural CD do faithfulness | Không về biến thừa | — | V-search |
| **PCMCI**, Runge et al.; Science Advances 2019; `10.1126/sciadv.aau4996` | Chuỗi thời gian, cổ điển | Điều kiện trên biến không liên quan làm giảm effect size và power: hiệu ứng hữu hạn mẫu ở phía cổ điển | Chuỗi thời gian | V-search |
| **NoisyCausal**; preprint 2026; `10.48550/arXiv.2605.04313` | Benchmark suy luận nhân quả của LLM dưới nhiễu có cấu trúc, gồm distractor | Tương tự ở mức văn bản | Khác hẳn đầu vào | V-search |
| Luận văn **Lechuga**, TU Wien 2026; `10.34726/hss.2026.137306` | So sánh AVICI, BCNP, DiBS, BayesDAG dưới shift (đồ thị, cơ chế, nhiễu, số nút, n) | Shift số nút không phải append trên khối đích cố định | Chưa đọc toàn văn | V-search |
| **TabPFN v2**, Hollmann et al.; Nature 2025; `10.1038/s41586-024-08328-6` | — | Chưa kiểm được phần về feature vô thông tin (trang yêu cầu đăng nhập) | — | Not-read |

Đã loại khỏi bằng chứng: các kết quả về "noise variables" theo nghĩa nhiễu ngoại sinh, invariance qua môi trường (ICP), ước lượng hiệu ứng amortized (ACTIVA, Cond-FiP).

## 3. Sổ claim

| Claim | Nhãn | Bằng chứng | Điều giới hạn | Kiểm tiếp |
|---|---|---|---|---|
| Chưa có bài nào đo việc thêm cột độc lập vào khối đích cố định ở mô hình CD học sẵn | **Inference** (tìm có giới hạn) | §2; audit 2 §7 | Không phải systematic review; preprint mới ra liên tục (FoundCause v2 ra 17/11) | Lặp lại tìm kiếm ngay trước khi viết bài |
| Nguyên lý "output CD phải nhất quán khi đổi tập biến" là mới | **Bác** (prior art) | Self-Compatibility, AISTATS 2024 | Phép thử của N1 là trường hợp riêng có đáp án biết trước (đệm độc lập) | Trích trong related work; nêu rõ phần nào là của N1 |
| Mạng nơ-ron và PFN cho dữ liệu bảng tệ đi với feature vô thông tin (bài toán dự đoán) | **Verified** | Grinsztajn §5.3; TabPFN §B.3.2 | Hu & Ghelichi 2026: ROC-AUC của TabPFN không giảm khi tổng số feature tăng từ 4 lên 512 (2 feature có thông tin) hoặc khi thêm tới 128 feature tương quan | Trích trong related work |
| AVICI `scm-v0` và CDFM được huấn luyện với số cạnh/nút ∈ {1, 2, 3}, d tới 100 | **Verified** | config `scm-v0.yaml`; CDFM §5.4 | Phân phối số cạnh thực tế còn phụ thuộc họ đồ thị | — |
| FoundCause: đường DoWhy (dùng với xác suất 0.5ζ) sinh đồ thị liên thông với q = min(q0, k/(Dtot − 1)) | **Verified** | FoundCause v2 App. G, G.1 | Bộ sinh đa dạng nhận cùng q, nhưng mật độ thực tế và tính liên thông không được nêu; "∝ 1/(D − 1)" chỉ khi trần chặn | Nếu FoundCause vào P-N2: đọc App. I–J, đo mật độ thực tế bằng mã nếu có |
| CDFM có bias độ thưa toàn cục và ngưỡng NATIVE phụ thuộc log D | **Verified** | CDFM §5.3; mã | Bias là hằng; logD như nhau ở A20 và B20. Khác biệt A–B phải đi qua xác suất (biểu diễn phụ thuộc dữ liệu) hoặc các đặc trưng toàn ma trận của bộ chọn ngưỡng. Hậu nghiệm: ngưỡng NATIVE tăng khi có đệm, nhiều nhất ở B (+0.154). Việc đổi ngưỡng đóng góp +0.047 F1 vào contrast B − A, nhưng ở FIXED 0.5 thì B vẫn tốt hơn A (+0.034): đây là tương tác điểm × ngưỡng | Đọc CDFM theo NATIVE, FROZEN và FIXED riêng |
| AVICI và CDFM có cơ chế ngược chiều với đệm có cấu trúc | **Chưa xác lập** | Held-out §4; phân tích hậu nghiệm | F1 ngược chiều, nhưng số cạnh cùng chiều (ít hơn với B); ở cùng số cạnh: con số gộp của AVICI gần 0 nhưng che hai chiều ngược nhau (tuyến tính +0.052, RFF −0.036); CDFM B kém A | P-N2 đo số cạnh và thứ hạng, không chỉ F1, theo từng họ |
| Hại của N1 do model học được "d lớn thì mỗi cặp ít khả năng có cạnh" | **Hypothesis H1'** | Suy từ prior đã xác minh | Không giải thích được khác biệt A–B ở cùng D. L1 giữ D cố định nên **không** kiểm H1'. Trong mạng của cả hai model không có đầu vào d tường minh; D chỉ vào qua số token trong attention, nên ở mức mạng, H1' khó tách khỏi pha loãng attention. Với CDFM, D còn vào qua logD của bộ chọn ngưỡng | Kiểm trực tiếp cần đổi D mà giữ nội dung khối đệm, hoặc can thiệp vào logD của bộ chọn ngưỡng CDFM; chưa thiết kế |
| Với FoundCause, cột cô lập nằm ngoài vùng huấn luyện | **Hypothesis H3** | Đường DoWhy không có nút cô lập (mỗi nút không gốc có ít nhất 1 cha; đồ thị liên thông). Hậu nghiệm: B gần như trả lại k0 (H = 0.020), A hại 0.093 | Đường DoWhy chỉ dùng với xác suất 0.5ζ; bộ sinh đa dạng chưa rõ; variable dropout che biến (thiếu dữ liệu), không tạo cột độc lập | L1 tại e_P = 0 so với e_P > 0, đọc theo số nút đệm cô lập |
| Đòn bẩy "có cạnh khác có tương quan" tách được bằng dữ liệu | **Bị bác (suy luận toán)** ở hệ tuyến tính Gauss | Khối DAG tuyến tính Gauss và phân phối Gauss cùng hiệp phương sai là **một** phân phối | Chỉ hệ RFF mới tách được phần nào | Thay bằng đòn bẩy cường độ L2 |
| Sàng lọc phụ thuộc biên rồi chạy model theo thành phần liên thông xóa phần lớn hại | **Hypothesis** | Hiểu biết cổ điển; Aliferis 2010; divide-and-conquer CD | Với d_T = 20, k = 20 có 400 cặp chéo; ở α = 0.05 không hiệu chỉnh, kỳ vọng khoảng 20 phát hiện giả dưới độc lập, đủ để nối hai khối. Hiệu chỉnh quá chặt lại có thể tách mất cạnh yếu trong đích | Nhánh R ở §5: Fisher-z / HSIC, Bonferroni; α chọn trên DEV theo tiêu chí J; đo lỗi gộp và lỗi tách, đo thời gian |

## 4. So sánh failure mode

Phân tích hậu nghiệm ([PN1_HELD_posthoc_rank_level_vi.md](PN1_HELD_posthoc_rank_level_vi.md)) phân rã hại theo mốc m0 thành hai phần. Đây là phân rã kế toán, không phải hai nguyên nhân độc lập; đổi mốc thì tỉ lệ đổi.

- **Phần thứ hạng** (cạnh đúng không còn được xếp trên cạnh sai) chiếm phần lớn ở AVICI-A và gần như toàn bộ ở CDFM-B.
- **Phần số cạnh** (mức điểm, hiệu chỉnh, ngưỡng) chiếm phần lớn ở AVICI-B và CDFM-A.

| Failure mode | Cách sửa đã có | Vì sao chưa đủ | Tái hiện rẻ nhất | Đối chứng có thể bác gap |
|---|---|---|---|---|
| FM1: cột độc lập cô lập làm mất recall hoặc thêm cạnh sai ở khối đích | Đưa feature vô thông tin vào prior (đề xuất cho TabPFN); làm sạch cột hằng/trùng (FoundCause); khám phá cục bộ (DCD-PFN); sàng lọc trước (cổ điển) | Chưa ai đo cho CD học sẵn; làm sạch của FoundCause không bắt được cột độc lập có phương sai | Pipeline P-N1, A tại k = 20 | **Sàng lọc + chạy theo thành phần (R).** Nếu R xóa được hại với chi phí thấp, bài đổi khung thành "failure + cơ chế + cách sửa rẻ". Đó vẫn là kết quả có ích, không phải "chỉ là quên tiền xử lý". R chưa chắc thắng vì cạnh giả từ đa kiểm định có thể nối hai khối |
| FM2: khối đệm có cấu trúc làm đổi số cạnh và thứ hạng ở khối đích, khác nhau giữa các model | Không thấy | Sàng lọc biên tách được hai khối độc lập trong quần thể, nhưng hữu hạn mẫu thì không chắc. Cơ chế chưa rõ: ở CDFM có ít nhất một phần do ngưỡng toàn ma trận | P-N1, B tại k = 20 | L1 với contrast định trước, đọc kèm CI, theo số cạnh và thứ hạng. Nếu không thấy tín hiệu thì chỉ dừng ngân sách cho đòn bẩy này; failure đã lặp lại không bị bác |

## 5. Hệ quả cho thiết kế nghiên cứu cơ chế (đề xuất, chưa khóa)

**Câu hỏi của P-N2.** Vì sao một khối dữ liệu độc lập với khối đích lại làm model đổi cách chọn cạnh trong khối đích? Thay đổi ấy làm mất cạnh đúng hay loại cạnh sai? Nó nằm ở mức điểm (số cạnh) hay ở thứ hạng cạnh đúng/sai? Và vì sao khác nhau giữa các model? Câu hỏi này giữ phát hiện ban đầu mà không khóa nghiên cứu vào một cách giải thích chưa xác lập.

**Biến đo** (mọi nhánh; trên khối đích, skeleton):

- số cạnh dự đoán: NATIVE; với CDFM thêm FROZEN (ngưỡng của k0), FIXED (0.5) và chính ngưỡng NATIVE;
- phần thứ hạng: AUROC trên các cặp của khối đích, và F1 ở số cạnh của k0;
- phần số cạnh: H trừ phần thứ hạng (phân tách chính xác, xem file hậu nghiệm);
- TP, FP, F1; logit trung bình của cặp đúng và cặp sai (biến phụ).

Phân tích riêng tuyến tính và RFF, có thêm bản gộp.

Cần phân biệt hai trường hợp, vì chúng dẫn tới hai cách sửa khác nhau:

- điểm dịch nhưng thứ hạng giữ nguyên: nghiêng về vấn đề hiệu chỉnh hoặc ngưỡng;
- thứ hạng cạnh đúng/sai bị đảo: nghiêng về mất khả năng phân biệt cấu trúc.

**L1: cấu trúc khối đệm ở cùng D (đòn bẩy chính).**

- **Thiết lập:** k = 20, khối đích giữ nguyên từng bit; số cạnh/nút của khối đệm e_P ∈ {0, 0.5, 1, 2, 3}.
- **Ghép cặp randomness giữa các mức:**
  - dùng chung ma trận nhiễu, thứ tự topo và trọng số cho mỗi cạnh ứng viên; tập cạnh lồng nhau (e_P = 0.5 ⊂ 1 ⊂ 2 ⊂ 3);
  - bộ sinh của AVICI rút tham số và nhiễu theo thứ tự phụ thuộc đồ thị, nên cần bộ sinh riêng cho khối đệm. Bộ sinh này **giữ nguyên họ cơ chế** của AVICI (RFF đa biến, tuyến tính):
    - sinh trước thứ tự topo và một ma trận uniform chung, chọn cạnh bằng ngưỡng p_e = 2e/(k − 1);
    - sinh trước tham số cho mọi cha ứng viên;
    - ở mỗi mức chỉ lấy tọa độ của các cha đang có cạnh.

    Chi tiết ở [luật P-N2](../n2_context_mechanism_2026-11-20/PN2_rules_exploratory_vi.md) §3;
  - kiểm trên DEV trước khi khóa.
- **Ghi lại** số cạnh đệm thực tế và số nút đệm cô lập. Với ER ở k = 20, tỉ lệ nút cô lập vào khoảng 36%, 12%, 1% và dưới 0.1% ở e_P = 0.5, 1, 2, 3.
- **L1 kiểm gì:** đổi cấu trúc thống kê của khối đệm ở cùng D có làm đổi output của khối đích không, và theo hướng nào.
  - L1 **không** kiểm H1' (prior gắn với d), vì D giữ nguyên.
  - Đổi số cạnh đệm đồng thời đổi mức phụ thuộc, độ dư thừa và hình dạng phân phối chung. Một đường liều–đáp ứng rõ chỉ xác lập độ nhạy với cấu trúc khối đệm, chưa quy được nguyên nhân cho prior huấn luyện.
- **Hướng dự đoán:** sinh hậu nghiệm từ held-out của P-N1, nên phải kiểm trên seed mới.
  - AVICI: số cạnh khối đích giảm khi e_P tăng; phần thứ hạng đổi theo họ (tuyến tính: B xếp hạng tốt hơn A; RFF: kém hơn).
  - CDFM: ngưỡng NATIVE tăng và số cạnh NATIVE giảm khi e_P tăng. Thứ hạng (top-m0, AUROC, AP) xấu đi, rõ nhất ở RFF. Dấu của F1 phụ thuộc cách chọn ngưỡng, nên F1 không phải giả thuyết chính.
  - FoundCause (bước sau): số cạnh tăng khi e_P tăng. Nếu H3 đúng, hại giảm mạnh từ e_P = 0 sang e_P nhỏ và đi theo số nút đệm cô lập.

**L2: cường độ phụ thuộc trong khối đệm.**

- **Thiết lập:** e_P = 2, x_j = s · f_j(pa_j) + ε_j. Tức là nhân phần tín hiệu từ cha, giữ nguyên nhiễu, rồi mới chuẩn hóa cột. Không nhân cả cột rồi chuẩn hóa, vì bước chuẩn hóa sẽ xóa tác động.
- **Mức:** s ∈ {0, 0.25, 0.5, 1}.
  - s = 0 là điểm mất phụ thuộc: không còn cạnh hữu hiệu. Với nhiễu Gauss, phân phối khi đó trùng e_P = 0 của L1, nên có sẵn một phép kiểm nhất quán.
  - s = 1 trùng e_P = 2 của L1 nếu dùng cùng bộ sinh.
- **Trước khi khóa:** kiểm cách bộ sinh tham số hóa trọng số và nhiễu.

**R: sàng lọc và tách thành phần (bắt buộc, chạy sớm).**

- **R-data:**
  - kiểm phụ thuộc biên từng cặp: Fisher-z cho tuyến tính; HSIC cho RFF, Spearman làm đối chứng rẻ;
  - Bonferroni là bản chính, BH báo thêm. α chọn trên DEV theo tiêu chí J ở luật P-N2.
    - p-value của HSIC lấy theo xấp xỉ gamma. Với 999 hoán vị, p-value nhỏ nhất là 10⁻³, không đạt ngưỡng Bonferroni 0.05/780 ≈ 6.4 × 10⁻⁵ khi D = 40.
    - Thời gian đo trên DEV; chưa coi nhánh R là rẻ;
  - tách thành phần liên thông rồi chạy model trên từng thành phần.
- **Báo:** H sau R; lỗi gộp (biến đệm bị gộp vào thành phần chứa biến đích); lỗi tách (cạnh thật của đích bị chia sang hai thành phần).
- **Đối chứng:**
  - R-oracle (biết trước ranh giới đích/đệm) chạy model trên đúng khối đích, nên trùng k0 theo cấu trúc. Nó chỉ là kiểm sanity.
  - R-data chạy tại k0 (không đệm) đo cái giá của việc tách chính khối đích.

**Can thiệp attention (bước sau, khi L1, L2, R đã có kết quả).**

- **Khả thi:** CDFM có sẵn `row_attn_mask` cho các khối attention theo trục biến. AVICI dùng `hk.MultiHeadAttention`, lớp này nhận mask nhưng cần nối vào model.
- **Mask toàn phần là đối chứng kênh.** Mask toàn phần nghĩa là token đích không đọc key/value của token đệm ở mọi lớp theo trục biến.
  - Đã kiểm trong mã: mọi phép tính khác của hai model chạy theo từng biến hoặc từng cặp (layer norm theo trục feature, pooling theo trục mẫu, head bilinear hoặc tích vô hướng). Vì vậy xác suất của khối đích trở về đúng k0 theo cấu trúc phép tính.
  - Kết quả đó xác nhận kênh, nhưng không phân biệt được prior mật độ với pha loãng attention.
- **CDFM:** ngưỡng NATIVE vẫn dùng thống kê toàn ma trận. Dưới mask toàn phần, phần hại NATIVE còn lại chính là kênh ngưỡng, nên đọc riêng FIXED/FROZEN và NATIVE.
- **Can thiệp phân biệt cơ chế:**
  - mask theo lớp;
  - tách đóng góp value của token đệm khỏi ảnh hưởng của chúng lên mẫu số softmax (pha loãng).
- **Lưu ý:** Hu & Ghelichi cho thấy attention dồn sang cột thừa mà hiệu năng không giảm. Chỉ đo attention thì không đủ để quy nguyên nhân.

**Đọc kết quả và điều kiện dừng.**

- **Contrast định trước** cho mỗi model và họ, đọc kèm CI:
  - e_P = 3 so với e_P = 0;
  - xu hướng trên cả năm mức, để không bỏ sót đường không đơn điệu;
  - áp cho số cạnh, phần thứ hạng và F1.
- **Ngưỡng thực tiễn:** giữ 0.03 cho F1, nhưng chỉ gọi là "phẳng" khi CI nằm trong ±0.03. Ước lượng điểm nhỏ mà CI rộng thì là INCONCLUSIVE. Với số cạnh: hiệu ứng **trung bình theo hệ**, trong từng model và họ dữ liệu, được coi là nhỏ về thực tiễn khi toàn bộ CI nằm trong [−1.5, +1.5] cạnh. Đây là lựa chọn thực tiễn cho phạm vi này, không phải tiêu chuẩn thống kê phổ quát, và không có nghĩa "số cạnh không đổi ở mỗi hệ". Báo kèm trung bình |Δ|, số cặp đổi trạng thái, và kết quả theo d_T.
- **Đọc TP và FP**, không chỉ F1, vì F1 ít đổi vẫn có thể che việc TP và FP cùng đổi mạnh.
- **Phạm vi của kết quả pilot:** chỉ quyết ngân sách cho đòn bẩy đó. Nó **không** bác failure của N1 đã lặp lại, và không đổi nhãn INCONCLUSIVE của P-N1.

**Dữ liệu, model, chi phí.**

- **Dữ liệu:** tập exploratory mới và held-out mới, với seed base mới. Không dùng lại EXP/HELD của P-N1 để xác nhận. Luật exploratory (40 hệ) được khóa trước khi chạy. Cỡ mẫu và luật held-out (kế hoạch ban đầu 80 hệ) chốt sau exploratory, trước khi sinh hay chạy held-out.
- **Model:**
  - Pilot đầu với AVICI và CDFM, khoảng vài phút đến một giờ mỗi lưới.
  - FoundCause vào bước sau với ít điều kiện chọn trước (khoảng 6 phút mỗi lệnh gọi), đặc biệt để kiểm chiều tăng số cạnh.

## 6. Quyết định

**Đã quyết ngày 20/11** (review của user):

- giữ L1 (chính), L2 và R;
- can thiệp attention để bước sau, đọc theo §5;
- pilot đầu chỉ AVICI và CDFM; FoundCause vào sau khi đã chọn được phép thử phân biệt cơ chế;
- push `940b50e` kèm commit đính chính, không viết lại lịch sử;
- giữ nguyên nhãn INCONCLUSIVE của P-N1.

Tên nghiên cứu là **P-N2**, theo đúng tên review dùng; thư mục đề xuất là `reports/n2_context_mechanism_2026-11-20/`.

**Đã quyết thêm** (review thứ hai của user, cùng ngày):

- exploratory 40 hệ;
- 80 hệ held-out là kế hoạch ban đầu; cỡ mẫu và luật held-out chốt sau exploratory, dùng phương sai ước lượng từ exploratory;
- biên ±1.5 cạnh cho hiệu ứng trung bình;
- nhánh R: Fisher-z cho tuyến tính, HSIC cho RFF, Bonferroni là bản chính;
- bộ sinh lồng nhau giữ nguyên họ RFF hiện tại.

Thiết kế chi tiết và các điểm còn mở nằm trong [bản nháp luật P-N2](../n2_context_mechanism_2026-11-20/PN2_rules_exploratory_vi.md).

## 7. Nhật ký đính chính (20/11, sau review của user)

| # | Chỗ | Bản `940b50e` | Sửa thành | Căn cứ |
|---|---|---|---|---|
| 1 | §1.1, §2 CausalArena | "nó **lọc bỏ** đồ thị có biến cô lập", dễ đọc thành "loại luôn bối cảnh của N1" | Bộ lọc chỉ loại cột cô lập (≈ A). Điều thiếu là phép đối sánh giữ nguyên khối đích | Review; câu chữ App. A.1 |
| 2 | §2, §3 Noise Immunity | "khó hơn với feature gây nhiễu có tương quan: tiền lệ cho đòn bẩy đệm có phụ thuộc"; "TabPFN (bản mới) gần như miễn nhiễm" | Feature tương quan sinh từ feature có thông tin; ROC-AUC không giảm; attention dịch chuyển. Không dùng làm bằng chứng cho đệm có phụ thuộc | Review; §3.2.1–3.2.2, App. A, App. B Bảng 1, 3, 4 (đọc lại) |
| 3 | §2, §3 FoundCause; tin nhắn chat 20/11 | "mật độ ∝ 1/(D − 1)", "nhánh DoWhy luôn sinh đồ thị liên thông, mật độ tỉ lệ 1/(D − 1)", "mật độ của nhánh thứ hai không được mô tả" | Công thức đầy đủ; "∝ 1/(D − 1)" chỉ khi trần chặn; cùng q truyền sang bộ sinh đa dạng; đường DoWhy chỉ dùng với xác suất 0.5ζ | Review; App. G, G.1 nguyên văn (đọc lại). Phần "0.5ζ" là kiểm thêm của agent |
| 4 | §2, §3 CDFM | "bias độ thưa toàn cục"; ghi chú `suggest_threshold_by_density` | Bias là tham số vô hướng cố định, không tự tạo khác biệt A–B. Ngưỡng NATIVE từ `suggest_threshold` với 10 đặc trưng toàn ma trận | Review; mã `graph_inference.py`, `utils.py`, `run_model.py` |
| 5 | §1, §2, §3 | (không có) | Thêm Self-Compatibility (AISTATS 2024): nguyên lý nhất quán khi đổi tập biến đã có | Review; trang PMLR, arXiv (đọc tới §2.3) |
| 6 | §1.3, §5 | "chiều phụ thuộc model"; dự đoán có dấu theo hại F1 (AVICI tăng, CDFM/FoundCause giảm theo e_P) | Câu hỏi đặt lại theo việc chọn cạnh; dự đoán chuyển sang số cạnh và thứ hạng | Review; held-out §4; phân tích hậu nghiệm (mới) |
| 7 | §5 L1 | "giả thuyết mật độ bị loại" | L1 kiểm độ nhạy với cấu trúc khối đệm ở cùng D; không kiểm H1' | Review |
| 8 | §5 L2 | "nhân độ mạnh của cơ chế (hệ số cạnh; output scale)" | Cùng ý, nay ghi rõ: nhân phần tín hiệu từ cha, giữ nhiễu, chuẩn hóa sau; s = 0 là điểm mất phụ thuộc | Review (làm rõ, không phải lỗi) |
| 9 | §5 attention | "Hại biến mất thì đường tác động là attention; hại còn thì nằm ở chuẩn hóa, pooling toàn cục, bias độ thưa" | Mask toàn phần là đối chứng kênh, trở về k0 theo cấu trúc. Bỏ ba kênh thay thế vì chuẩn hóa và pooling chạy theo từng biến và bias là hằng. Kênh thay thế thật ở CDFM là ngưỡng NATIVE | Review; mã `avici/model.py`, `cdfm_model.py` |
| 10 | §4, §5 điều kiện dừng | "\|Δ\| < 0.03 thì giả thuyết bị loại; FM2 chỉ là nhiễu riêng của từng checkpoint" | Contrast định trước, đọc kèm CI; kết quả pilot chỉ quyết ngân sách, không bác failure đã lặp lại | Review |
| 11 | §3, §5 R | "sàng lọc (ví dụ Fisher-z từng cặp)" | Thêm R-data/R-oracle, rủi ro đa kiểm định (400 cặp chéo × 0.05 ≈ 20 cạnh giả), lỗi gộp/tách, R tại k0 | Review |

Điều kiện dừng cũ cũng xuất hiện ở [báo cáo held-out §5](PN1_HELD_results_vi.md); ở đó đã thêm ghi chú đính chính trỏ về §5 của file này.

**Lần 2 (20/11, sau review thứ hai của user):**

| # | Chỗ | Bản trước | Sửa thành | Căn cứ |
|---|---|---|---|---|
| 12 | §1.4, §3 | Chênh F1 AVICI/CDFM "đến từ điểm xuất phát và từ ngưỡng NATIVE của CDFM"; "ở cùng số cạnh: AVICI B ≈ A" | Ngưỡng chỉ góp thêm một phần; dấu B − A ở CDFM phụ thuộc cách chọn ngưỡng (FIXED 0.5: B vẫn tốt hơn). Con số gộp của AVICI che hai họ ngược chiều | Review thứ hai; [hậu nghiệm](PN1_HELD_posthoc_rank_level_vi.md) Bảng 3, Bảng 5 |
| 13 | §4 | Hai phần hại "xuất hiện ở những ô khác nhau" | Phân rã kế toán theo mốc m0, không phải hai nguyên nhân | Review thứ hai |
| 14 | §5 L1 | "với RFF cần dạng cộng theo từng cha" | Giữ nguyên họ RFF đa biến của AVICI; lồng nhau bằng ma trận uniform chung và tham số sinh trước cho mọi cha ứng viên | Review thứ hai; mã `avici/synthetic/rff.py`, `linear.py`, `graph.py`, `utils.py` |
| 15 | §5 hướng dự đoán | CDFM: "ở ngưỡng FROZEN, phần thứ hạng xấu đi" | FROZEN không đo thuần thứ hạng; thứ hạng đo bằng top-m0, AUROC, AP | Review thứ hai |
| 16 | §5 R, đọc kết quả, dữ liệu; §6 | Phép kiểm RFF "chọn trên DEV"; biên số cạnh "chốt sau"; "luật held-out khóa trước khi chạy" | HSIC (xấp xỉ gamma) + Bonferroni; biên ±1.5 cho hiệu ứng trung bình; held-out chốt sau exploratory | Review thứ hai |
| 17 | Tin nhắn chat 20/11 | "40 hệ cho CI khoảng ±0.02" | Con số đó là cho contrast gộp. Phân tích riêng từng họ, 40 hệ (20 mỗi họ) cho nửa độ rộng CI khoảng ±0.026 đến ±0.048 trên F1 ở top-m0, theo phương sai của P-N1 | Review thứ hai; tính lại từ Bảng 3 của hậu nghiệm |
