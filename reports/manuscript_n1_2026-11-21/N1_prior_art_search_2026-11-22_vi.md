# N1: rà prior art có ghi ngày (22/11/2026)

> **Mục đích** (theo user, lượt 8):
>
> - kiểm xem các claim mới còn đứng vững không;
> - viết rõ khác biệt với các công trình gần nhất.
>
> **Phạm vi:**
>
> - một lượt tìm có mục tiêu, **không phải systematic review**, và không mở lại quá trình tìm hướng;
> - đọc kỹ phần thí nghiệm và phụ lục của các công trình gần nhất.
>
> **Công cụ:**
>
> - tìm kiếm web;
> - đọc trang arXiv (abstract và bản HTML), Crossref, trang JMLR và proceedings NeurIPS qua công cụ fetch;
> - nhiều trang dài chỉ đọc được nguyên văn một phần. Phạm vi đọc ghi ở từng dòng: "nguyên văn" là văn bản đọc trực tiếp; "tóm tắt" là phần do công cụ tóm tắt, không dùng làm căn cứ;
> - bổ sung 23/11: với các PDF mà công cụ fetch đã lưu về máy, văn bản được trích bằng một script chỉ dùng thư viện chuẩn của Python (giải nén stream, đọc ToUnicode CMap). Không cài thêm gì. Văn bản trích theo cách này được tính là "nguyên văn"; công thức và bảng có thể bị méo.
>
> **Bản trước:**
>
> - [rà prior art lần 1](../direction_scan_2026-11-13/N1_prior_art_audit_vi.md) và [lần 2](../direction_scan_2026-11-13/N1_prior_art_second_audit_vi.md) (13/11);
> - [kiểm lại 20/11](../n1_irrelevant_vars_2026-11-13/N1_prior_art_recheck_2026-11-20_vi.md);
> - [cập nhật 21/11](N1_prior_art_update_2026-11-21_vi.md).

## 1. Truy vấn (22/11/2026)

| # | Truy vấn | Chế độ | Kết quả chính |
|---|---|---|---|
| 1 | pretrained causal discovery model adding irrelevant variables robustness | extended | Không có bài thêm biến không liên quan vào model học sẵn. Gần nhất: CauScale (ẩn nút), PTCD (chuỗi thời gian), TCD-Arena |
| 2 | amortized causal discovery transformer invariance appended independent variables marginalization | extended | AVICI, CAASL, Montagna et al., ACD chuỗi thời gian; không có phép thử thêm biến |
| 3 | causal discovery foundation model benchmark robustness distractor variables 2026 | extended | CausalArena, FoundCause, DAG-FM, HEURESIS; không có thí nghiệm distractor |
| 4 | causal foundation model zero-shot structure learning sensitivity extra columns arXiv 2026 | extended | Arrow, CDFM, TabFM, survey "Causal Foundation Models"; không có |
| 5 | divide and conquer causal discovery partition variables marginal independence components | extended | SADA, Shah et al. (TMLR 2025), Cai và Hara, DiCoLa, CausalSteward, Local Discovery by Partitioning |
| 6 | self-compatibility causal discovery variable subsets evaluation without ground truth follow-up | standard | Chỉ thấy Faller et al. (AISTATS 2024); không thấy bài tiếp nối |
| 7 | "Causal discovery needs explicit epistemic standards" | standard | Bài quan điểm, NeurIPS 2026 (position paper track) |
| 8 | Montagna Demystifying amortized causal discovery with transformers venue 2025 | standard | TMLR 2025 (bản ghi ISTA), khớp với trích dẫn trong bản thảo |
| 9 (23/11) | Lần theo trích dẫn (snowballing): related work và Bảng 1 của FoundCause v2 | — | Bốn bài chưa có trong log này: DCD-PFN, Kim et al. (TMLR 2025), Yin et al. (2025), TabPFN-CFM. DCD-PFN đã có trong lần kiểm 20/11 |

**Quy tắc chọn bài để đọc kỹ:**

- model causal discovery học sẵn, công bố từ 2026, có thí nghiệm về độ bền hoặc về số biến;
- benchmark của các model đó;
- phương pháp chia biến rồi chạy discovery trên từng phần, vì đó là prior art cho cách sửa ở §8 của bài;
- survey và bài quan điểm gần nhất.

## 2. Model học sẵn: có thí nghiệm nối biến độc lập vào một input cố định không?

Câu hỏi cho từng bài: có thí nghiệm nào nối thêm vào bảng input các biến độc lập với, hoặc không liên quan tới, đồ thị được đánh giá, rồi đo thay đổi của cấu trúc dự đoán trên các biến gốc không?

| Bài | Nối biến độc lập vào input cố định? | Các thí nghiệm về độ bền | Phạm vi đọc |
|---|---|---|---|
| FoundCause v2 (Blöbaum et al., arXiv 2606.17516v2) | **Không** (đã đọc cả App. I và J, 23/11). Thí nghiệm gần nhất là đoạn "Control With Observed Common Causes" ở App. J, xem dưới bảng | Dữ liệu thiếu (10%, 30%, có chọn lọc); ẩn biến hub và ẩn 15% biến (§5.3); ablation lúc huấn luyện. Benchmark tới D = 46 | Nguyên văn: tóm tắt tới §6, App. A–H (tới Bảng 12); App. I–J trích từ PDF ngày 23/11 |
| CDFM (Qiao et al., 2607.11508) | Không. Số biến đổi bằng cách sinh bộ dữ liệu mới | N, D (10–100); 15 họ cơ chế; dữ liệu thiếu MCAR; Causal Chamber, Tübingen | Nguyên văn: tới §7, App. A; App. B chỉ có tóm tắt |
| Arrow (Thompson et al., 2605.07204) | Không ("we draw 100 datasets … randomized") | Số quan sát và số biến; OOD (small-world, spline, gamma noise); BN Repository; Sachs | Nguyên văn: toàn văn tới App. F |
| DAG-FM v2 (Chen et al., 2607.11510) | Không (mỗi lần chỉ đổi một siêu tham số khi sinh dữ liệu) | Cỡ mẫu, số đặc trưng, mật độ, discretization, OOD; Sachs; Causal Chamber (bỏ cột hằng) | Nguyên văn: phần lớn, trừ cuối App. D.4 |
| CauScale v2 (Peng et al., 2602.08629) | Không. §5.6 **bỏ bớt** nút để mô phỏng confounder ẩn | Quy mô đồ thị, chu trình, OOD, confounder ẩn, sai số prior, cỡ mẫu | Nguyên văn: phần lớn; App. F chỉ có tóm tắt |
| TabCausal v2 (Li et al., 2605.31156v2) | Không (đồ thị mới cho mỗi d) | Bảy họ tổng hợp; N; d ∈ {50, 100, 300}; OOD; can thiệp | Nguyên văn: gần như toàn văn |
| Loscar (2610.29530) | Không | 19 benchmark hai biến; nhiễu hỗn hợp; d = 6 và 12; Sachs | Nguyên văn: toàn văn |
| CausalArena (Li et al., 2609.11897, chỉ có v1) | Không. Bộ sinh tổng hợp loại đồ thị có nút cô lập | Stress test về tín hiệu yếu, nhiễu, warping, outlier, dữ liệu thiếu, can thiệp | Đối chiếu App. A.1–A.2 ngày 13/11 (Verified-fetch); 22/11 chỉ đọc lại tóm tắt, không có gì mới |

**Kết luận (suy luận từ các bài đã đọc):**

- Các bài gần nhất chỉ thay đổi số biến bằng cách sinh đồ thị và dữ liệu mới, hoặc bằng cách ẩn bớt biến.
- Chưa thấy bài nào giữ một khối đích cố định rồi nối thêm biến độc lập. Claim chính của bài (C1, C11) chưa bị một công trình đã đọc làm trùng.
- Kết luận này kèm điều kiện về các preprint ra sau ngày 22/11. Điều kiện về FoundCause v2 App. I–J đã gỡ ngày 23/11 (xem dưới).

**FoundCause v2, App. I và J (nguyên văn, trích từ PDF ngày 23/11):**

- **App. I "Missing Data":** mọi copy được làm bằng cách xóa ô của các biến đích; không thêm cột nào. Hai cơ chế: "Purely random missingness (missing completely at random, MCAR)" và "Selection-driven missingness (missing at random, MAR)", ở mức 10% và 30%, trên 14 bộ benchmark.
- **App. J "Latent Confounder Recovery: Protocol and Results":** ba setting, đều tạo confounder bằng cách bỏ biến:
  - in-distribution: 40 task từ bộ sinh;
  - semi-synthetic: 5 mạng với "round(0.15D) hub variables hidden";
  - benchmark: 14 bộ với "round(0.15D) variables hidden, drawn uniformly at random".
- **Đoạn "Control With Observed Common Causes"** là thí nghiệm gần nhất với phép thử của bài:
  - nguyên văn: "We also scored the pairs and labels of the benchmark setting with the outputs of FoundCause and FCI on the complete tables, in which the common cause of every confounded pair is observed."
  - kết quả: FoundCause gắn cờ "19.0% of the pairs on the complete tables and 19.2% with the variables hidden".
  - khác với phép thử của bài (suy luận):
    - các biến được trả lại gồm nguyên nhân chung của mọi cặp bị confound, nên câu trả lời đúng về confounding trên các cặp đó đổi giữa hai input;
    - thứ được so là tỉ lệ cờ, recall và F1, không phải output trên một khối cố định có đáp án không đổi.

## 2b. Bốn bài tìm qua related work của FoundCause v2 (23/11)

| Bài | Trạng thái (đã kiểm) | Cách dùng tập con biến | Có nối biến độc lập vào input cố định? | Phạm vi đọc |
|---|---|---|---|---|
| **DCD-PFN**, Guan, Chen, He, Tong, Hu, Qian, Wu, Kuang | arXiv 2606.21212, chỉ có v1 (19/6/2026), "11 pages"; preprint. Đã có trong lần kiểm 20/11 | PFN học "sample-wise decoupling weights that enable Markov boundary (MB) identification" từ cả bảng; ghép đồ thị bằng thủ tục DCD rồi luật Meek, ra CPDAG (§3.4) | Không. Thí nghiệm: đồ thị SF mới với d ∈ {10, 15, 20}, n = 800, 25 seed (§4.2); Sachs (§4.3) | Nguyên văn: toàn văn (PDF v1) |
| **Kim, Gibbs, Yun, Song, Cho**, "Large-Scale Targeted Cause Discovery via Learning from Simulated Data" | Trang 1 PDF: "Published in Transactions on Machine Learning Research (10/2025)"; arXiv 2408.16218 v1 29/8/2024, v2 7/4/2025, v3 30/9/2025, Comments "TMLR 2025". Trang OpenReview chặn công cụ fetch | Chạy mạng trên tập con biến ngẫu nhiên cỡ n′ cố định có chứa biến đích, rồi lấy trung bình điểm ("subsampled-ensemble inference", §4.2). Nhãn huấn luyện là tổ tiên của biến đích trong tập con; theo Proposition 2, tập này không phụ thuộc tập con khi tập con chứa mọi biến gốc | Không. §5.4 quét cỡ ensemble T và cỡ tập con n′, đo độ chính xác (Hình 9), không đo thay đổi output khi nối cột | Nguyên văn: §1–§5.4 và phần Proposition 2 (PDF v3) |
| **Yin, Gao, Yu**, "Learning Causal Graphs at Scale: A Foundation Model Approach" (ADAG) | arXiv 2506.18285; dấu trên PDF là v1, 23/6/2025; chưa xem trang abs. Preprint | Không dùng tập con. Nhiều domain trên **cùng** d biến, SEM tuyến tính; d ∈ {5, 10, 20} | Không | Nguyên văn: §4 và các tiêu đề mục (PDF v1) |
| **TabPFN-CFM**, Zhu, Mansoldo, Wang, Groha | arXiv 2606.26467; dấu trên PDF là v1, 25/6/2026; chưa xem trang abs. Preprint, bài ngắn | Không dùng tập con. Dự đoán cả cấu trúc (adjacency, ancestral, confounding) và outcome | Không. 500 bộ cho mỗi setting tổng hợp (trong phân phối; OOD với hàm Fourier ngẫu nhiên); hai bộ thật (Amazon Sales, Law School) | Nguyên văn: toàn văn phần chính, App. D (PDF v1) |

**Hệ quả (suy luận):**

- Kim et al. là bài gần nhất về tinh thần: model học sẵn được thiết kế để nhất quán qua các tập con biến (nhãn nhất quán, trung bình qua tập con). Nhưng họ không đo output trên một khối cố định khi nối cột độc lập. Claim C1 và C11 không bị trùng.
- Trung bình qua tập con biến ngẫu nhiên là một cách sửa phía input khác với R-L; bài chưa so sánh. Đã ghi vào danh sách "không claim" ở §8 của bản thảo.

## 3. Prior art cho cách sửa: chia biến rồi chạy discovery trên từng phần

| Bài | Cách chia | Chạy gì trên từng phần, ghép thế nào | Lỗi do chia hoặc gộp sai | Áp lên model học sẵn? |
|---|---|---|---|---|
| SADA (Cai, Zhang, Hao; arXiv 1707.01283) | "causal cut" tìm bằng phép kiểm độc lập có điều kiện, dưới giả định cấu trúc thưa | Một causal solver bất kỳ (thí nghiệm dùng LiNGAM); hợp cạnh, bỏ cạnh yếu nhất khi có chu trình | Có bàn (§V, chỉ có tóm tắt) | Không |
| Shah et al. (TMLR 03/2025; arXiv 2406.06348) | Phủ chồng lấn từ một superstructure (ví dụ do PC tìm), qua phát hiện cộng đồng rồi mở rộng biên | Learner PAG đầy đủ và nhất quán; giữ cạnh có mặt ở mọi tập con | Có: vi phạm giả định khi học trên tập con; giá của việc chia (§6.4, tóm tắt) | Không |
| Cai và Hara (arXiv 2403.14125; DOI liên quan 10.1007/s00180-025-01633-2) | Nhóm theo quan hệ tổ tiên (RCD), giả định LiNGAM | DirectLiNGAM trên mỗi nhóm, rồi hợp | Có: chu trình khi ghép; lỗi loại II của phép kiểm làm sót quan hệ | Không |

**Hệ quả cho bài:**

- Ý tưởng chia biến theo quan hệ độc lập rồi chạy discovery trên từng phần đã có từ lâu với learner cổ điển.
- Đóng góp của §8 không phải ý tưởng đó, mà là đánh giá một phép sàng lọc chỉ dùng input làm cách sửa cho model học sẵn, trong thiết kế khối đích cố định. Ba thứ được đo:
  - giá ở k0;
  - độ ổn định sau sửa, với tính chất có điều kiện của mức cố định cho mỗi cặp;
  - rủi ro gộp nhầm.
- Related work và §8 phải trích các bài này.

## 4. Survey và bài quan điểm

| Bài | Có bàn tính bất biến khi thêm biến, hay coi đó là khoảng hở? | Phạm vi đọc |
|---|---|---|
| Stith, Rahmani, Cresswell, "Causal Foundation Models" (arXiv 2609.03003, v1). Trang arXiv mô tả là "a practical introduction", không gọi là survey | Không, trong phần đọc nguyên văn (§1–§3.2) và theo tóm tắt phần còn lại. Mục hướng tương lai nói về phát hiện lệch giữa quá trình sinh dữ liệu đích và prior huấn luyện (tóm tắt) | Nguyên văn khoảng 80k/176k ký tự đầu |
| "Causal discovery needs explicit epistemic standards" (arXiv 2611.03166; NeurIPS 2026, position paper track) | Không. Bài giả định causal sufficiency và không bàn model học sẵn. Luận điểm "benchmark không trung lập" có thể dùng khi định vị bài | Nguyên văn tới đầu §4; phần sau chỉ có tóm tắt |

## 5. Điểm chưa giải quyết

- ~~**FoundCause v2, Appendix I và J**~~: **đã giải quyết ngày 23/11.**
  - Văn bản được trích từ bản PDF mà công cụ fetch đã lưu ngày 22/11, bằng script chỉ dùng thư viện chuẩn (xem §1). Không cần tải mã nguồn TeX.
  - Nội dung ghi ở §2.
- **Còn mở:**
  - trang OpenReview của Kim et al. chặn công cụ fetch. Venue lấy từ dòng in trên trang 1 của PDF v3 và từ trường Comments trên arXiv;
  - trang abs của Yin et al. và TabPFN-CFM chưa xem, nên chưa biết các bài đó có bản sau v1 hay không.

## 6. Việc kéo theo cho bản thảo (nhánh riêng)

- Related work: thêm đoạn về phương pháp chia biến (SADA; Shah et al., 2025; Cai và Hara).
- Thêm câu: trong các bài đã đọc, các thí nghiệm "thêm biến" đều sinh dữ liệu mới, hoặc ẩn bớt biến. Trích CDFM, Arrow, DAG-FM, CauScale, TabCausal và FoundCause.
- §8: nói rõ khác biệt với nhóm chia biến.
- Có thể trích bài quan điểm NeurIPS 2026 khi bàn về vai trò của benchmark.
- Lặp lại lượt tìm này ngay trước khi nộp.
- **Đã làm trên nhánh riêng:**
  - 22/11: đoạn "Partition-based discovery", câu về cách các bài đổi số biến, các model mới;
  - 23/11:
    - câu về đoạn đối chứng ở App. J của FoundCause;
    - Kim et al. trong đoạn "Partition-based discovery";
    - TabPFN-CFM trong danh sách model học sẵn chưa thử;
    - một dòng "không claim" ở §8.2 về cách trung bình qua tập con biến.
