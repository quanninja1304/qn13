# Danh sách tài liệu cần bổ sung vào `docs/papers`

> Ngày 2026-11-07. `docs/papers` hiện gần như toàn lý thuyết, không có bài benchmark thực nghiệm nào. Tất cả đều chưa có trong thư mục đó.
> **Mức đã đọc:** A = phần liên quan trong nguồn gốc; B = tóm tắt và quét từ khóa trong nguồn gốc; C = chỉ qua kết quả tìm kiếm hoặc trích dẫn từ bài khác. Trạng thái xuất bản lấy từ nguồn đã thấy; bài ghi "preprint" nghĩa là tôi chưa thấy bản đã bình duyệt.

## Ưu tiên 1: cần để chạy cổng R1, R4 (đọc trước)

| Bài | Trạng thái | Link | Vì sao cần | Mức đọc |
|---|---|---|---|---|
| Ramsey, Andrews, Spirtes: *Efficient Latent Variable Causal Discovery: Combining Score Search and Targeted Testing* | Preprint 2025 | [arXiv 2510.04263](https://arxiv.org/pdf/2510.04263) | **Đối thủ trực tiếp của C1**: BOSS-FCI, GRaSP-FCI, FCIT, LV-Dumb | B |
| Ogarrio, Spirtes, Ramsey: *A Hybrid Causal Search Algorithm for Latent Variable Models* (GFCI) | PGM 2016 | Tìm theo tên; chỉ thấy qua bài trên | Phương pháp lai đầu tiên | C |
| *On Causal Discovery in the Presence of Deterministic Relations* (DGES) | NeurIPS 2024 | [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/ec52572b9e16b91edff5dc70e2642240-Paper-Conference.pdf) | Có thể trùng một phần C1 | B |
| Lemeire: *Causal Inference on Data Containing Deterministic Relations* | Báo cáo 2008 | [PDF](http://parallel.vub.ac.be/~jan/papers/JanLemeire_CausalInferenceWithDeterministicRelations2008.pdf) | Adjacency-faithfulness khi có tất định | C |
| Lee et al.: *Constraint-based Causal Discovery from a Collection of Conditioning Sets* | UAI 2025 | [PMLR](https://proceedings.mlr.press/v286/lee25a.html) | Hạn chế tập điều kiện vì gần tất định, baseline | C |
| *On Different Notions of Redundancy in Conditional-Independence-Based Discovery of Graphical Models* | Preprint 2025 | [arXiv 2502.08531](https://arxiv.org/pdf/2502.08531) | Trùng từ khóa "redundancy", cần kiểm tra | C |
| Lam, Andrews, Ramsey: *Greedy Relaxations of the Sparsest Permutation Algorithm* (GRaSP) | UAI 2022 | [arXiv 2206.05421](https://arxiv.org/abs/2206.05421) | Vì sao permutation-based giữ được cạnh | C |
| Andrews et al.: *Fast Scalable and Accurate Discovery of DAGs Using the Best Order Score Search and Grow-Shrink Trees* (BOSS) | NeurIPS 2023 | [arXiv 2310.17679](https://arxiv.org/pdf/2310.17679) | Như trên | C |
| Solus, Wang, Uhler: *Consistency Guarantees for Greedy Permutation-Based Causal Inference Algorithms* | Biometrika 2021 | [arXiv 1702.03530](https://arxiv.org/abs/1702.03530) | Nền cho hai bài trên | C |
| Scheines, Ramsey: *Measurement Error and Causal Discovery* | 2016–2017, cần kiểm tra chính xác | [PMC5340263](https://pmc.ncbi.nlm.nih.gov/articles/PMC5340263) | Sai số đo làm hỏng tập tách | C |
| Zhang et al.: *Causal Discovery in the Presence of Measurement Error: Identifiability Conditions* | Preprint 2017 | [arXiv 1706.03768](https://arxiv.org/pdf/1706.03768) | Như trên | C |
| Saeed et al.: *Anchored Causal Inference in the Presence of Measurement Error* (tên tác giả chưa xác minh) | Cần kiểm tra | [arXiv 1906.00928](https://ar5iv.arxiv.org/html/1906.00928) | Như trên | C |

## Ưu tiên 2: benchmark thực và bằng chứng failure

| Bài | Trạng thái | Link | Vì sao cần | Mức đọc |
|---|---|---|---|---|
| Gamella, Peters, Bühlmann: *Causal chambers as a real-world physical testbed for AI methodology* | Nature Machine Intelligence 2025 | [arXiv 2404.11341](https://arxiv.org/pdf/2404.11341) | **Dữ liệu chính.** Đọc kỹ App. V về ngữ nghĩa ground truth | A |
| Brouillard et al.: *The Landscape of Causal Discovery Data* | CLeaR 2025 | [arXiv 2412.01953](https://arxiv.org/pdf/2412.01953) | Tổng quan dữ liệu; < 5% dùng metric can thiệp | A |
| Jonnalagedda et al.: *Where Causal Discovery Breaks on Real Data* | Preprint 10/2026 | [arXiv 2611.00484](https://arxiv.org/pdf/2611.00484) | Rất mới, cùng tinh thần đo giả định trên dữ liệu thật | A (phần đầu) |
| Reisach, Seiler, Weichwald: *Beware of the Simulated DAG!* | NeurIPS 2021 | [arXiv 2102.13647](https://arxiv.org/pdf/2102.13647) | Tiền lệ phát hiện thực nghiệm mạnh | C |
| Reisach et al.: *A Scale-Invariant Sorting Criterion...* (R²-sortability) | NeurIPS 2023 | [arXiv 2303.18211](https://arxiv.org/abs/2303.18211) | Như trên | C |
| Chevalley et al.: *CausalBench* | Communications Biology 2025 | [arXiv 2210.17283](https://arxiv.org/pdf/2210.17283) | Benchmark perturbation lớn | B |
| *The CausalBench Challenge* | PMLR 2025 | [arXiv 2308.15395](https://arxiv.org/pdf/2308.15395) | Khoảng cách synthetic–real | B |
| Stein et al.: *CausalRivers* | ICLR 2025 | [arXiv 2503.17452](https://arxiv.org/pdf/2503.17452) | Benchmark chuỗi thời gian thực | B |
| Göbler et al.: *causalAssembly* | Cần kiểm tra venue | [arXiv 2306.10816](https://arxiv.org/pdf/2306.10816) | Dữ liệu sản xuất | B |
| Li et al.: *CausalArena* | Preprint 2026 | [arXiv 2609.11897](https://arxiv.org/pdf/2609.11897) | Có real-data check, danh sách dữ liệu thật | B |
| Zhang et al.: *Consistency evaluation of benchmarks used for causal discovery* | Preprint 2026 | [arXiv 2606.01789](https://arxiv.org/pdf/2606.01789) | Chất lượng graph benchmark, bằng LLM | B |
| Montagna et al.: *Assumption violations in causal discovery and the robustness of score matching* | NeurIPS 2023 | [arXiv 2310.13387](https://arxiv.org/pdf/2310.13387) | Vi phạm giả định, trên dữ liệu mô phỏng | C |
| Ramsey, Andrews: *FASK with Interventional Knowledge Recovers Edges from the Sachs Model* | Preprint 2018 | [arXiv 1805.03108](https://arxiv.org/abs/1805.03108) | Tranh cãi ground truth Sachs | C |
| Sachs et al.: *Causal Protein-Signaling Networks Derived from Multiparameter Single-Cell Data* | Science 2005 | **Cần bạn lấy, có thể trả phí** | Nguồn gốc dữ liệu; cần để xác minh thứ tự các điều kiện | C |

## Ưu tiên 3: cho C2 (chọn điểm vận hành, không có truth)

| Bài | Trạng thái | Link | Vì sao cần | Mức đọc |
|---|---|---|---|---|
| Biza et al.: *Out-of-Sample Tuning for Causal Discovery* (OCT) | IEEE TNNLS 2022 | [DOI, **có thể cần bạn lấy**](https://doi.org/10.1109/tnnls.2022.3185842) | Đối thủ trực tiếp của C2 | C |
| Schkoda et al.: *Cross-validating causal discovery via Leave-One-Variable-Out* | CLeaR 2025 | [arXiv 2411.05625](https://arxiv.org/pdf/2411.05625) | LOVO, có phần dữ liệu thật | A |
| Faller et al.: *Self-Compatibility* | AISTATS 2024 | [arXiv 2307.09552](https://arxiv.org/pdf/2307.09552) | Chưa đánh giá trong E3 | B |
| *AutoCD* | Cần kiểm tra | [OpenReview](https://openreview.net/pdf?id=tAgrza91RA) | AutoML cho discovery | C |
| *Effect-Level Validation for Causal Discovery* | Preprint 2026 | [arXiv 2602.08340](https://arxiv.org/pdf/2602.08340) | Chưa đọc | C |
| *Internal Incoherency Scores for Constraint-based Causal Discovery Algorithms* | Preprint 2025 | [arXiv 2502.14719](https://arxiv.org/pdf/2502.14719) | Phát hiện vi phạm faithfulness từ output | C |
| Gentzel, Garant, Jensen: *The Case for Evaluating Causal Models Using Interventional Measures and Empirical Data* | NeurIPS 2019 | [arXiv 1910.05387](https://arxiv.org/pdf/1910.05387) | Metric can thiệp | C |
| Eigenmann et al.: *Evaluation of Causal Structure Learning Algorithms via Risk Estimation* | UAI 2020 | [arXiv 2006.15387](https://arxiv.org/pdf/2006.15387) | Như trên | C |
| Sato et al.: *Practical Causal Evaluation Metrics for Biological Networks* | Preprint 2025 | [arXiv 2511.12805](https://arxiv.org/pdf/2511.12805) | Metric theo độ lớn hiệu ứng | B |
| *Interpretable, multi-dimensional Evaluation Framework for Causal Discovery* | Preprint 2024 | [arXiv 2409.19377](https://arxiv.org/pdf/2409.19377) | Khung đánh giá | B |
| *Conditional Independence Tests for Constraint-Based Causal Discovery: A Survey* | TMLR 2026 | [arXiv 2608.11156](https://arxiv.org/pdf/2608.11156) | Open problems §10 | A (mục 10) |
| White: *Maximum Likelihood Estimation of Misspecified Models* | Econometrica 1982 | **Cần bạn lấy** | Nền cho Failure B; biết qua survey trên | C |

## Cách làm tiện nhất

- **Hầu hết là arXiv**, bạn tải được ngay. Nếu muốn tôi có thể tải các PDF công khai vào `docs/papers` và cập nhật `download_manifest`; bạn chỉ cần lấy các bài ghi "cần bạn lấy".
- **Bài cần nhất nếu chỉ đọc vài bài:** Ramsey et al. 2025, DGES, Gamella et al. (App. V), GFCI, OCT.
