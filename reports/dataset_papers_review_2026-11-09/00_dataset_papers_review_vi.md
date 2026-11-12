# Rà soát các bài báo dataset/benchmark cho causal (09/11/2026)

> **Yêu cầu của user:** tìm dữ liệu từ các **bài báo dataset/benchmark** (kiểu CLadder, CausalBench), không tải gì, chỉ đọc báo. User sẽ tự tải PDF sau khi review.
> **Thay thế** `reports/data_first_gap_2026-11-07/DATASET_SHORTLIST_2026-11-09_vi.md`. Danh sách đó lấy từ các bộ dữ liệu sinh học lẻ, không xuất phát từ bài dataset.
> **Cách đọc:** đọc bản arXiv HTML hoặc trang abstract của từng bài. Nhiều phần dài chỉ đọc được qua bản tóm tắt của công cụ.
> **Nhãn:**
> - **[Verified]**: đã đọc nguyên văn đoạn liên quan.
> - **[Verified-summary]**: chỉ qua phần tóm tắt do công cụ trích từ chính bài.
> - **[Verified-search]**: chỉ qua kết quả tìm kiếm hoặc trang abstract của bên thứ ba.
> - **[Inference]**, **[Hypothesis]**.
>
> **Chưa tải dữ liệu nào, chưa chạy gì.** Causal Chambers bị loại theo yêu cầu.

---

## 1. Tóm tắt

1. Các bài dataset/benchmark về causal chia thành **bốn họ**:
   - (A) benchmark lập luận nhân quả cho LLM, như CLadder và Corr2Cause;
   - (B) benchmark học cấu trúc trên dữ liệu dạng bảng;
   - (C) benchmark perturbation đơn tế bào, như CausalBench;
   - (D) benchmark chuỗi thời gian.
2. **Quan sát xuyên suốt [Verified trên các bài đã đọc]:** **chưa benchmark nào trong số đã đọc đánh giá phương pháp cho phép biến ẩn (FCI/PAG, LPCMCI) trên dữ liệu thật.**
   - CausalBench không có FCI, và tự thừa nhận causal sufficiency có thể không đúng.
   - CausalArena ghi "latent confounding" là việc tương lai.
   - CausalRivers có confounding do thời tiết nhưng không chạy phương pháp biến ẩn nào.
   - CausalTime giả định sufficiency.
   - Corr2Cause loại biến ẩn ngay từ thiết kế ("no hidden variables").
   - Ngoại lệ là TimeGraph (KDD 2025) và CausalDynamics (NeurIPS 2025). Cả hai có biến ẩn, nhưng dữ liệu là **tổng hợp hoặc mô phỏng**.
3. Đây là **khoảng trống của các benchmark**, chưa phải gap phương pháp. Lý do khả dĩ [Inference]: chấm PAG trên dữ liệu thật rất khó khi không biết biến ẩn. Nhưng chính điều đó gợi ra một hướng đo được bằng dữ liệu (§4, G1): **dùng can thiệp giữ lại để kiểm chứng các claim tổ tiên của PAG**, vì claim "X là tổ tiên của Y" có thể kiểm tra bằng do(X) mà không cần biết toàn bộ graph.

---

## 2. Ma trận các bài dataset/benchmark

### Họ A — Lập luận nhân quả của LLM (dữ liệu là văn bản sinh từ graph)

| Benchmark | Venue | Dữ liệu và quy mô | Ground truth | Biến ẩn | Phát hiện chính | Ghi chú |
|---|---|---|---|---|---|---|
| **CLadder** (Jin et al.) | NeurIPS 2023 [Verified-search] | **Tổng hợp**: graph nhỏ 3–4 biến ("three to four variables", §3), causal Bayesian network Bernoulli, diễn đạt thành câu chuyện. 10 112 mẫu (v1.5), chia đều 3 bậc của Pearl [Verified, Table 1] | "oracle causal inference engine" theo do-calculus và counterfactual [Verified, §1, §3.1] | Câu hỏi được dựng để luôn **identifiable**; không có biến ẩn như một yếu tố thiết kế [Verified] | GPT-4 đạt 62.03%; GPT-4 + CausalCoT đạt 70.40%; random 49.27% [Verified, Table 2] | HF `causalNLP/cladder` |
| **Corr2Cause** (Jin et al.) | ICLR 2024 [Verified, arXiv comments] | **Tổng hợp**: liệt kê mọi DAG 2–6 nút (6 325 DAG, 2 376 MEC); 207 972 mẫu [Verified, Table 1, Table 3] | d-separation và Markov equivalence class trên DAG đã liệt kê (§3.4–3.5): suy luận kiểu PC [Verified] | **Loại bỏ**: "no hidden variables" (§3.6) [Verified] | Zero-shot F1 tốt nhất 33.38%, nhiều mô hình kém hơn đoán ngẫu nhiên; fine-tune đạt 94.74% F1 nhưng giảm tới 39.29 điểm khi diễn đạt lại [Verified/Verified-summary] | HF `causalnlp/corr2cause` |
| **CausalBN-Bench** (Zhou et al., arXiv tên cũ "CausalBench") | IEEE Trans. AI 2026 [Verified, abs page] | 15 mạng **bnlearn** (2–109 nút), hỏi LLM về correlation, skeleton, hướng cạnh [Verified, §II-A] | Graph bnlearn [Verified] | Không | LLM gần bằng thuật toán cổ điển ở mạng nhỏ, kém xa trên 50 nút; yếu ở collider [Verified] | Dùng tên biến thật nên có nguy cơ "tra cứu" thay vì lập luận |
| **CaLM** (Chen et al.) | Preprint 2024 [Verified] | 126 334 mẫu, 92 causal target, 28 mô hình; trộn dữ liệu tự dựng và nguồn mở (COPA, e-CARE, CLadder…) [Verified/Verified-summary] | Chưa đọc tới phần định nghĩa [—] | Chưa rõ | 50 phát hiện; các bài đánh giá cũ chỉ phủ khoảng 10% task [Verified] | 315 trang |
| e-CARE, COPA | e-CARE: ACL 2022 [Verified-search] | Câu hỏi trắc nghiệm nhân quả kiểu thường thức | Gán nhãn bởi người | Không | — | Bài review chê là giải được bằng **tra cứu kiến thức** |
| **Critical review** (Yang et al. 2024) | Preprint [Verified] | Rà soát 39 benchmark | — | — | Nhiều benchmark "can likely be solved through the retrieval of domain knowledge"; đề xuất 4 tiêu chí: causal chứ không chỉ correlation, open-ended, scalable, **non-retrievable** [Verified] | Thước đo để đánh giá họ A |

### Họ B — Học cấu trúc trên dữ liệu dạng bảng

| Benchmark | Venue | Dữ liệu | Tham chiếu | Biến ẩn | Phát hiện chính |
|---|---|---|---|---|---|
| **CausalArena** (Li et al.) | Preprint 09/2026 [Verified] | 1 000 SCM tổng hợp; 200 SCM "có ngữ nghĩa" do LLM hỗ trợ dựng; **13 bảng thật** (Abalone, Auto MPG, Arrhythmia, Concrete, DWD, Ozone, Sachs, PetShop ×4, Chamber ×2) [Verified, §4–5.2] | Graph công bố, "not independently verified unique true DAGs" [Verified] | **Không**; "latent confounding" là việc tương lai [Verified-summary, §7.3] | "the synthetic ranking does not carry over" sang dữ liệu thật; không phương pháp nào thắng mọi lát cắt; 18 phương pháp, **không có FCI** [Verified] |
| **causalAssembly** (Göbler et al.) | CLeaR 2024 [Verified-search] | **Bán tổng hợp** từ dây chuyền Bosch (distributional random forest) | Graph chuyên gia | Có thí nghiệm ẩn biến (gián tiếp qua bài khác) | Thuật toán hiện có gặp khó |
| **Tübingen pairs** (Mooij et al.) | JMLR 2016 [Verified-search] | 100–108 cặp nguyên nhân–kết quả thật, 37 bộ dữ liệu | Nhãn chuyên gia | — | Chỉ hai biến; bài review ghi nhận GPT-3.5/4 **đã thuộc lòng** bộ này |
| **CSuite** (Geffner et al. 2022) | Preprint/MS Research [Verified-search] | Tổng hợp, 2–12 nút, có tập can thiệp | Graph sinh | Có biến thể "mixed confounding" | — |
| **Landscape** (Brouillard et al.) | CLeaR 2025 [Verified, đọc hôm trước] | Tổng quan dữ liệu thật: Sachs, Dixit, Replogle K562/RPE1, Frangieh, Wille | — | "causal sufficiency never holds" trong sinh học [Verified] | Dưới 10% nghiên cứu dùng metric can thiệp [Verified] |

### Họ C — Perturbation đơn tế bào

| Benchmark | Venue | Dữ liệu | Tham chiếu | Biến ẩn | Phát hiện chính |
|---|---|---|---|---|---|
| **CausalBench** (Chevalley et al.) | Communications Biology 2025 [Verified-search]; đã đọc bản arXiv v2 | Perturb-seq CRISPRi (Replogle 2022). K562: 162 751 mẫu, 10 691 quan sát, 622 can thiệp. RPE1: 162 733, 11 485, 383 [Verified, Table 1, §4] | **Không có graph đúng** ("true causal graph is unknown", §5). Hai loại đánh giá: (i) sinh học (CORUM, STRING, ChIP-seq); (ii) thống kê: mean Wasserstein giữa P(B \| do A) và P(B), cùng false omission rate [Verified, §5.1–5.2] | SCM có biến không quan sát 𝕌, nhưng **không phương pháp nào mô hình hóa**; "causal sufficiency may not hold" [Verified §3.1 / Verified-summary §6.4] | **"methods that use interventional information do not outperform those that only use observational data"**; khả năng mở rộng kém [Verified, Abstract]. Phương pháp: PC, GES, NOTEARS, GIES, DCDI…, **không có FCI** [Verified] |
| **scPerturb** (Peidli et al.) | Nature Methods 2024 [Verified-search] | 44 bộ perturbation đơn tế bào đã chuẩn hóa (RNA, protein, ATAC) | E-distance cho hiệu ứng perturbation | — | Nguồn dữ liệu, không phải benchmark discovery |

### Họ D — Chuỗi thời gian

| Benchmark | Venue | Dữ liệu | Tham chiếu | Biến ẩn | Phát hiện chính |
|---|---|---|---|---|---|
| **CausalRivers** (Stein et al.) | ICLR 2025 [Verified-search]; đã đọc arXiv v1 | **Thật**: lưu lượng sông, Bavaria 494 trạm, đông Đức 666 trạm, 2019–2023, mỗi 15 phút [Verified, Table 2] | Topology sông, dựng bán tự động rồi kiểm tay [Verified, §3.1] | Confounding do mưa; tập con "Confounder" bỏ nút cha chung để mô phỏng biến ẩn [Verified, §4.1] | Baseline ngây thơ thường **ngang** phương pháp causal; **không chạy phương pháp biến ẩn nào** [Verified, §4.1, §5] |
| **CausalTime** (Cheng et al.) | ICLR 2024 [Verified-search] | Bán tổng hợp từ dữ liệu thật (AQI, Traffic, MIMIC-IV) bằng mạng nơ-ron | Graph suy ra từ mô hình fit, "not the ground truth" [Verified-summary] | **Giả định sufficiency** [Verified] | Điểm trên dữ liệu "thật" thấp hơn nhiều so với dữ liệu tổng hợp |
| **CausalDynamics** (Herdeanu et al.) | NeurIPS 2025 D&B [Verified-search] | Mô phỏng: hơn 5 300 graph từ ODE/SDE và hai mô hình khí hậu lý tưởng, trên 50 triệu mẫu | Graph sinh | **Có unobserved confounders** | Phương pháp đơn giản thường thắng phương pháp deep learning |
| **TimeGraph** (Ferdous et al.) | KDD 2025 D&B [Verified-search] | Tổng hợp, có biến thể có hoặc không có confounder U | Graph sinh | **Có** | Có chạy LPCMCI |
| **CauseMe** (Runge et al.) | Nature Communications 2019 [Verified-search] | Nền tảng benchmark khí hậu | Hỗn hợp | Có một phần | — |

**Loại khỏi phạm vi:** Causal Chambers (theo yêu cầu); CausalVerse (NeurIPS 2025, causal representation learning từ ảnh); CLEVRER và CausalWorld (video/robot); bnlearn đứng riêng (dữ liệu sinh từ mạng chuyên gia).

---

## 3. Đánh giá theo tiêu chí "dữ liệu trước"

| Tiêu chí | Họ A (LLM) | Họ B (bảng) | Họ C (perturbation) | Họ D (chuỗi thời gian) |
|---|---|---|---|---|
| Dữ liệu thật | Không: văn bản sinh từ graph nhỏ | Một phần (13 bảng của CausalArena) | **Có** | Có (CausalRivers); còn lại mô phỏng |
| Tham chiếu kiểm chứng được | Có, chính xác (oracle) | Yếu, graph công bố | **Can thiệp** (Wasserstein, FOR) | Topology (CausalRivers) |
| Liên quan biến ẩn (thế mạnh lâu nay của dự án) | Corr2Cause loại bỏ; CLadder không xét | Không | **Thừa nhận nhưng chưa ai đánh giá** | Có ở bộ mô phỏng; thật thì chưa |
| Uy tín venue | NeurIPS, ICLR | CLeaR, JMLR, preprint | **Comms Bio, Nature Methods, Cell** | ICLR, NeurIPS D&B, KDD D&B |
| Khả thi trên 7.8 GB RAM | Cao | Cao | Có điều kiện (lọc gene) | Cao |
| Liên hệ registry "không làm lại" | X5: "LLM + discovery" rộng đã bị SUBSUMED. Phải hẹp hơn nhiều | — | — | — |

---

## 4. Các khoảng trống có thể đo bằng dữ liệu (giả thuyết, chưa đo)

| # | Khoảng trống | Bằng chứng hiện có | Phép thử dữ liệu đầu tiên | Rủi ro |
|---|---|---|---|---|
| **G1** | **Discovery có biến ẩn chưa từng được đánh giá trên benchmark perturbation thật.** Câu hỏi: cho phép biến ẩn (FCI, BOSS-FCI, GFCI) có làm đổi kết luận của CausalBench không? Claim tổ tiên của PAG có được can thiệp giữ lại xác nhận nhiều hơn claim của DAG không? | CausalBench không có FCI; tác giả thừa nhận causal sufficiency có thể sai; phát hiện "interventional không hơn observational" chưa được giải thích [Verified] | Trên tập gene con của K562: chạy PC, GES, FCI, BOSS-FCI. Chấm **claim tổ tiên** bằng Wasserstein trên can thiệp giữ lại. Luật đọc kết quả khai báo trước | Có thể đã có bài làm việc này mà tôi chưa tìm thấy. FCI có thể không chạy nổi ở quy mô lớn. Kết quả có thể chỉ là "không khác" |
| G2 | **Lập luận của LLM khi có biến ẩn**: mở rộng kiểu Corr2Cause sang PAG/MAG | Corr2Cause loại biến ẩn; CLadder chỉ dùng câu hỏi identifiable [Verified] | Sinh câu hỏi từ MAG nhỏ (không cần dữ liệu thật). Đo xem LLM có phân biệt được "có confounder" với "có cạnh" không | Không phải dữ liệu thật, nên trái tinh thần "dữ liệu trước". Họ "LLM + causal" rất đông; X5. Có thể là bài D&B, khó thành gap phương pháp |
| G3 | **Confounding trong chuỗi thời gian thật**: LPCMCI chưa được chạy trên CausalRivers | CausalRivers có tập con "Confounder", không phương pháp biến ẩn nào [Verified] | Chạy LPCMCI và PCMCI trên tập Confounder và Random | Graph topology không phải truth về hiệu ứng; đổi sang bài toán chuỗi thời gian |

**Khuyến nghị tạm:** **G1 là ứng viên chính.**
- Dữ liệu thật từ benchmark uy tín, đúng yêu cầu của bạn.
- Tham chiếu bằng can thiệp, đúng điều Landscape khuyến nghị.
- Nằm ngay thế mạnh tích lũy của dự án (FCI/PAG, claim tổ tiên).
- Phép thử đầu tiên có thể dứt khoát.

G3 là dự phòng. G2 chỉ nên làm nếu bạn muốn chuyển sang hướng LLM, và khi đó phải audit lại X5.

**Chưa phải gap đã chứng minh.** Cần audit văn liệu: đã có ai chạy FCI hay phương pháp biến ẩn trên CausalBench/Replogle chưa (ví dụ các bài trong cuộc thi CausalBench Challenge).

---

## 5. Danh sách bài cần tải vào `docs/papers/`

| Ưu tiên | Bài | Venue | Link | Vì sao |
|---|---|---|---|---|
| **1** | Chevalley et al., *CausalBench: A Large-scale Benchmark for Network Inference from Single-cell Perturbation Data* | Communications Biology 2025 | [Nature](https://www.nature.com/articles/s42003-025-07764-y) · [arXiv 2210.17283](https://arxiv.org/abs/2210.17283) | Trụ của G1; cần bản journal (đã đọc bản arXiv v2) |
| **1** | *The CausalBench Challenge* (các phương pháp tham gia) | PMLR 2025 | [arXiv 2308.15395](https://arxiv.org/pdf/2308.15395) | Kiểm tra ai đã thử biến ẩn |
| **1** | Replogle et al., *Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq* | Cell 2022 | [PMC9380471](https://pmc.ncbi.nlm.nih.gov/articles/9380471) | Nguồn dữ liệu |
| **1** | Brouillard et al., *The Landscape of Causal Discovery Data* | CLeaR 2025 | [PMLR v275](https://proceedings.mlr.press/v275/brouillard25a.html) | Khung đánh giá bằng can thiệp |
| **1** | Ramsey, Andrews, Spirtes, *Efficient Latent Variable Causal Discovery* (BOSS-FCI, GFCI, FCIT) | Preprint 2025 | [arXiv 2510.04263](https://arxiv.org/pdf/2510.04263) | Phương pháp biến ẩn có thể mở rộng quy mô |
| 2 | Jin et al., *CLadder* | NeurIPS 2023 | [arXiv 2312.04350](https://arxiv.org/pdf/2312.04350) | Họ A |
| 2 | Jin et al., *Corr2Cause* | ICLR 2024 | [arXiv 2306.05836](https://arxiv.org/pdf/2306.05836) | Họ A; G2 |
| 2 | Yang et al., *A Critical Review of Causal Reasoning Benchmarks for LLMs* | Preprint 2024 | [arXiv 2407.08029](https://arxiv.org/pdf/2407.08029) | Thước đo cho họ A |
| 2 | Li et al., *CausalArena* | Preprint 2026 | [arXiv 2609.11897](https://arxiv.org/pdf/2609.11897) | Họ B; synthetic không chuyển sang thật |
| 2 | Stein et al., *CausalRivers* | ICLR 2025 | [arXiv 2503.17452](https://arxiv.org/pdf/2503.17452) | G3 |
| 2 | Herdeanu et al., *CausalDynamics* | NeurIPS 2025 D&B | [arXiv 2505.16620](https://arxiv.org/pdf/2505.16620) | Có biến ẩn (mô phỏng) |
| 2 | Ferdous et al., *TimeGraph* | KDD 2025 D&B | [arXiv 2506.01361](https://arxiv.org/abs/2506.01361) | Có LPCMCI, có biến ẩn |
| 3 | Zhou et al., *CausalBN-Bench* | IEEE TAI 2026 | [arXiv 2404.06349](https://arxiv.org/abs/2404.06349) | Họ A dùng bnlearn |
| 3 | Chen et al., *CaLM* | Preprint 2024 | [arXiv 2405.00622](https://arxiv.org/abs/2405.00622) | Họ A, rất dài |
| 3 | Cheng et al., *CausalTime* | ICLR 2024 | [arXiv 2310.01753](https://arxiv.org/abs/2310.01753) | Họ D |
| 3 | Göbler et al., *causalAssembly* | CLeaR 2024 | [arXiv 2306.10816](https://arxiv.org/pdf/2306.10816) | Họ B |
| 3 | Peidli et al., *scPerturb* | Nature Methods 2024 | [PubMed 38279009](https://pubmed.ncbi.nlm.nih.gov/38279009/) | Nguồn dữ liệu phụ cho G1 |
| 3 | Mooij et al., *Distinguishing cause from effect…* | JMLR 2016 | [JMLR](https://jmlr.org/papers/v17/14-518.html) | Họ B |

---

## 6. Giới hạn

- Phần lớn bài chỉ đọc được một phần nguyên văn; phần sau dựa vào tóm tắt của công cụ (đã gắn nhãn). Bài CausalBench bản journal không đọc được vì bị chặn đăng nhập; đã đọc bản arXiv v2 (07/2023), con số có thể khác.
- Venue của CLadder, CausalTime, CausalRivers, CausalDynamics, TimeGraph chỉ xác nhận qua trang proceedings trong kết quả tìm kiếm, chưa qua chính PDF.
- **Chưa audit văn liệu cho G1–G3.** "Chưa thấy trong các bài đã đọc" không có nghĩa là chưa ai làm.
- Đây là rà soát có mục tiêu khoảng 18 bài, không phải systematic review.
