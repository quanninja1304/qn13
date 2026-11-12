# Danh sách dữ liệu thay thế Causal Chamber (09/11/2026)

> **ĐÃ BỊ THAY THẾ cùng ngày** bởi [`../dataset_papers_review_2026-11-09/00_dataset_papers_review_vi.md`](../dataset_papers_review_2026-11-09/00_dataset_papers_review_vi.md). User yêu cầu lấy dữ liệu từ các bài dataset/benchmark (kiểu CLadder, CausalBench) thay vì các bộ dữ liệu lẻ. File này giữ lại để truy vết.

> **Lý do:** user đánh giá Causal Chamber (hệ vật lý được thiết kế) xa lĩnh vực và khó thuyết phục reviewer. Cần dữ liệu thật, được cộng đồng causal discovery/ML dùng và chấp nhận, có tham chiếu kiểm chứng được.
> **Nhãn:** [Verified] đã đối chiếu nguồn gốc trong phiên này; [Verified-search] chỉ qua kết quả tìm kiếm hoặc tóm tắt; [Inference]; [Hypothesis].
> **Chưa tải dữ liệu nào.** Chưa chạy gì trên các bộ này.

## 1. Tiêu chí lọc

1. Dữ liệu **thật**, không phải mẫu sinh từ mạng do chuyên gia vẽ (loại bnlearn, SERGIO, NetSim).
2. Có **tham chiếu độc lập với thuật toán**. Ưu tiên tham chiếu từ **can thiệp giữ lại** (held-out interventions). Theo Brouillard et al. (CLeaR 2025, §2, §6), đây là cách đánh giá "closest to what most practitioners care about", nhưng < 10% nghiên cứu dùng.
3. Có **confounding không đo được** một cách tự nhiên, vì đề tài là discovery có biến ẩn. Brouillard et al. §5.1: "causal sufficiency never holds" trong dữ liệu sinh học.
4. Đã được dùng ở venue mạnh, để reviewer không hỏi "vì sao chọn bộ này".
5. Chạy được trên máy 7.8 GB RAM, có thể sau khi chọn tập con.

## 2. Ứng viên

| # | Bộ dữ liệu | Lĩnh vực | Quy mô | Tham chiếu | Biến ẩn | Đã dùng ở | Khả thi | Đánh giá |
|---|---|---|---|---|---|---|---|---|
| **D1** | **Kemmeren et al. 2014** (Cell 157:740), yeast deletion mutants | Biểu hiện gene | 6170 gene; **160 mẫu quan sát (wild-type) + 1479 mẫu can thiệp** (mỗi mẫu xoá 1 gene) [Verified, Meinshausen et al. 2016, tr. 7364] | **Strong intervention effect (SIE)** trên block can thiệp giữ lại (chia 5 block, train 4 + toàn bộ quan sát, test 1); 10 757 SIE trên 9 125 430 cặp [Verified, tr. 7364] | Có. Paper so ICP với **hiddenICP** (cho phép biến ẩn) [Verified, tr. 7364] | **PNAS 2016** (Meinshausen, Hauser, Mooij, Peters, Versteeg, Bühlmann), so với **PC, RFCI**, GES, GIES, Lasso; về sau dùng trong causal Dantzig, BIP-VI [Verified-search] | **Cao**: ~6170 × 1639 số thực, khoảng 80 MB | **Ưu tiên 1** |
| **D2** | **Replogle et al. 2022** (Cell) qua **CausalBench** (Chevalley et al., Communications Biology 2025) | Perturb-seq đơn tế bào (CRISPRi) | K562: 1158 can thiệp, 310 385 tế bào, 8552 gene. RPE1: 651 can thiệp, 247 914 tế bào, 8833 gene [Verified, Brouillard et al. Table 2] | Metric can thiệp của CausalBench, không cần graph đúng [Verified-search; tên metric chưa xác minh] | Có (nhân tố tế bào, chu kỳ tế bào…) [Inference] | Comms Biology 2025, cuộc thi CausalBench (PMLR 2025), dùng rộng ở ICLR/NeurIPS [Verified-search] | **Có điều kiện**: phải chọn tập gene con và tải theo khối; toàn bộ ma trận không vừa RAM | **Ưu tiên 2**, quy mô "top venue" |
| D3 | **Sachs et al. 2005** (Science) | Flow cytometry, tế bào T | 11 biến, 5846–7466 tế bào, 6–9 điều kiện [Verified, Brouillard §5.1, Table 2; hai con số chưa khớp nhau] | Mạng đồng thuận, **bị tranh cãi**: "ground truth provided is not definitive" (Brouillard §4) | Có | Bộ thật được dùng nhiều nhất | Cao; đã có sẵn trong repo | Giữ để **liên tục với pilot cũ**, không làm trụ chính |
| D4 | **Dixit et al. 2016** Perturb-seq | Đơn tế bào | 8 can thiệp, 14 427 tế bào, 24 gene [Verified, Brouillard Table 2] | Can thiệp | Có | Có trong Brouillard Table 2 | Cao (nhỏ) | Bộ nhỏ để thử nhanh pipeline |
| D5 | **Frangieh et al. 2021** Perturb-CITE-seq | Đơn tế bào, đo **cả RNA và protein** | 249 can thiệp, 218 331 tế bào, 1000 biến [Verified, Brouillard Table 2] | Can thiệp | Có | Có trong Brouillard Table 2 | Thấp–trung bình (lớn) | **[Hypothesis]** Hai lớp đo (mRNA, protein) của cùng gene có thể là dạng "đo lường dư thừa" giống C1, nhưng trong sinh học. **Chưa kiểm tra.** |
| D6 | **DREAM5 E. coli** (Marbach et al. 2012) | Microarray | 805 mẫu, 4511 gene, 334 TF; 2066 tương tác chuẩn từ RegulonDB [Verified-search] | Cơ sở dữ liệu tuyển chọn (RegulonDB) | Có | DREAM5, rất phổ biến trong GRN | Cao | Tham chiếu yếu: một nghiên cứu 2018 cho thấy mạng RegulonDB không nhất quán với dữ liệu biểu hiện [Verified-search]. **Phụ** |
| D7 | **CausalRivers** (ICLR 2025) | Lưu lượng sông, chuỗi thời gian | 494 trạm (Bavaria) + đông Đức [Verified-search] | Graph dựng từ nhiều nguồn địa lý | Có (thời tiết là confounder) [Verified-search] | ICLR 2025 | Cao | Thật và mới, nhưng là **chuỗi thời gian**: đổi bài toán so với FCI i.i.d. Để sau |
| D8 | **causalAssembly** (CLeaR 2024, Bosch) | Dây chuyền sản xuất | — | Graph chuyên gia; **dữ liệu sinh lại** bằng distributional random forest | Không đảm bảo | CLeaR 2024 | Cao | **Bán tổng hợp**, không đạt tiêu chí 1. Chỉ làm đối chứng |

**Loại:** bnlearn (mẫu sinh từ mạng chuyên gia), Tübingen pairs (chỉ hai biến), fMRI/NetSim ("no ground-truth graphs for most datasets", Brouillard §5.2). Dữ liệu y tế: chưa tìm được bộ nào có tham chiếu đáng tin về biến ẩn [Verified-search, một lượt tìm].

## 3. Khuyến nghị

- **Chính: D1 Kemmeren.** Đáp ứng cả 5 tiêu chí.
  - Tham chiếu dựa trên can thiệp giữ lại, đúng loại metric mà Brouillard et al. kêu gọi.
  - Nền baseline có sẵn và uy tín: PNAS 2016 đã chạy **PC và RFCI** trên đúng dữ liệu này, nên kết quả về FCI/RFCI so sánh trực tiếp được.
  - Biến ẩn được thừa nhận trong chính paper (hiddenICP).
  - Nhỏ, chạy được ngay.
- **Phụ, để có quy mô lớn: D2 CausalBench/Replogle.** Uy tín ML rất cao nhưng nặng. Chỉ làm sau khi D1 cho tín hiệu.
- **D3 Sachs** giữ để đối chiếu với pilot 07/11.
- **D5** đáng để mắt riêng vì có thể có hiện tượng giống C1 trong sinh học. Chỉ là giả thuyết.

## 4. Điều cần nói rõ

- **C1 được phát hiện trên Chamber; không tự động chuyển sang dữ liệu mới.** Theo quy trình dữ liệu trước, cần **đo lại failure từ đầu** trên D1/D2 với luật đọc khai báo trước, không mang giả định "đo lường dư thừa" sang.
- Câu hỏi đo đầu tiên đề xuất cho D1: trong các cặp có SIE trên block giữ lại, FCI/RFCI giữ hoặc định hướng được bao nhiêu so với PC, GES và một phương pháp lai (BOSS-FCI/GFCI), ở cùng tập gene. Ở những cặp bị mất, tập tách gồm gì.
- Chọn tập gene con là một **quyết định ảnh hưởng kết quả**; phải khai báo trước (ví dụ: gene bị xoá trong dữ liệu cộng với các gene đích có nhiều SIE).

## 5. Tài liệu cần bổ sung vào `docs/papers/`

| Ưu tiên | Bài | Link |
|---|---|---|
| 1 | Meinshausen et al., *Methods for causal inference from gene perturbation experiments and validation*, PNAS 113(27) 2016 | [doi:10.1073/pnas.1510493113](https://doi.org/10.1073/pnas.1510493113) (bản tác giả: [Mooij](https://staff.science.uva.nl/j.m.mooij/articles/7361.full.pdf)) |
| 1 | Kemmeren et al., *Large-scale genetic perturbations reveal regulatory networks and an abundance of gene-specific repressors*, Cell 157(3) 2014 | [PubMed 24766815](https://pubmed.ncbi.nlm.nih.gov/24766815/); GEO GSE42215, GSE42217, GSE42240, GSE42241, GSE42526, GSE42527 [Verified-search; chưa xác minh series nào chứa ma trận deletion] |
| 1 | Brouillard et al., *The Landscape of Causal Discovery Data*, CLeaR 2025 | [PMLR v275](https://proceedings.mlr.press/v275/brouillard25a.html); danh sách dữ liệu: [github.com/kurowasan/cd_datasets](https://github.com/kurowasan/cd_datasets) |
| 2 | Chevalley et al., *CausalBench*, Communications Biology 2025 | [arXiv 2210.17283](https://arxiv.org/pdf/2210.17283) |
| 2 | Replogle et al., *Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq*, Cell 185 (2022) | [PMC9380471](https://pmc.ncbi.nlm.nih.gov/articles/9380471) |
| 2 | Rothenhäusler et al., *Causal Dantzig* | [arXiv 1706.06159](https://arxiv.org/pdf/1706.06159) |
| 3 | Frangieh et al. 2021 (Perturb-CITE-seq); Dixit et al. 2016 (Perturb-seq) | tìm theo tên |
| 3 | Marbach et al., *Wisdom of crowds for robust gene network inference*, Nature Methods 2012 (DREAM5) | [PDF](https://dream.broadinstitute.org/papers/Marbach2012.pdf) |

Danh sách ưu tiên 1 của `PAPERS_TO_ADD_vi.md` (Ramsey et al. 2025 về BOSS-FCI, GFCI, FCIT) **vẫn cần**, vì đó là baseline lai bất kể dùng dữ liệu nào.
