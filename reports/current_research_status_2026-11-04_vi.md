# Tiến độ và đánh giá hướng nghiên cứu hiện tại

**Ngày rà soát:** 04/11/2026. **Phạm vi:** trạng thái của repository và hướng nghiên cứu tại thời điểm này; không phải kết quả của một pilot nhân quả mới.  
**Quy ước:** **[Đã kiểm tra]** là thông tin đối chiếu trực tiếp với file, mã hoặc phép chạy trong lần rà soát này; **[Theo báo cáo]** là kết quả có artifact trong repo nhưng không chạy lại toàn bộ; **[Suy luận]** là đánh giá từ các nguồn; **[Giả thuyết]** cần chứng minh hoặc đo; **[Chưa rõ]** chưa đủ bằng chứng.

## 1. Tóm tắt quyết định

**Hướng chính hiện tại là A′ đã cải biên: R1 — chứng nhận đồng thời các quan hệ tổ tiên (*ancestral features*) trong MAG có biến ẩn từ một tập CI query cố định, và R2 — báo cáo độ nhạy theo ngưỡng strong-faithfulness η.** Đây là một **hướng nghiên cứu có điều kiện**, chưa phải phương pháp đã được xác nhận về hiệu quả hay đóng góp đủ mạnh cho bài báo. A′ gốc, dựa trên score dạng hiệu `D(f)` và luận điểm rằng hiệp phương sai đầy đủ sẽ giữ calibration, đã **STOP** sau phản ví dụ toán và toy test. [Lịch sử quyết định](../RESEARCH_HISTORY_vi.md), [review handoff](aprime_review_2026-11-04/A1_review_handoff.md).

**Gate nguồn RG0 đã được agent đánh giá PASS** sau khi đọc các nguồn gần nhất; tình trạng *HOLD FOR SOURCE* đã được bỏ. **RG1 (chứng minh hoàn chỉnh) và RG2 (kill test về power) chưa hoàn thành.** Không có pilot MAG/FCI, so sánh nhân quả, hay bằng chứng R1 vượt baseline có cùng target. Hướng dự phòng vẫn là **T4** về xác nhận các CI premise theo selection population trong dữ liệu thiếu. [Nguồn và kết luận RG0](aprime_review_2026-11-04/A1_missing_references_register.md), [gates](aprime_review_2026-11-04/A1_pilot_readiness.md).

**Đánh giá độc lập [Suy luận]:** RG0 chỉ cho phép *tiếp tục kiểm tra* A′, chưa xác lập đóng góp khoa học mạnh. Phép chiếu confidence set lên feature đã có trong Wang–Kolar–Drton; minimum-distance/GLS là kỹ thuật cổ điển. Điểm mới khả dĩ hiện chỉ là **một thủ tục chứng nhận có bảo đảm cho setting latent, CI-based, Markov-equivalent**, nếu nó có power hữu ích và tốt hơn các baseline hợp lệ. Nếu RG2 không cho tín hiệu, nên dừng A′ và kiểm tra T4; không mở rộng framework để cứu một giả thuyết đã thất bại.

## 2. Repository và mức hoàn thành

| Thành phần | Trạng thái ngày 04/11 | Bằng chứng và giới hạn |
|---|---|---|
| Quy trình nghiên cứu | **[Đã kiểm tra]** `AGENTS.md`, `research/01`–`08`, topic cards, evidence matrix và lịch sử chuyển hướng đã có. | [AGENTS](../AGENTS.md), [protocol](../research/README.md), [pivot log](../RESEARCH_HISTORY_vi.md). |
| Literature reassessment | **[Đã kiểm tra]** Báo cáo A–J ngày 03/11 đã khảo sát 22 công trình cốt lõi và chọn A′ có điều kiện, T4 dự phòng, C-S thứ ba, B′ hạ ưu tiên. | Đây là **ảnh chụp trước review 04/11**; các claim về A′ gốc đã bị sửa hoặc bác bỏ. [Báo cáo 03/11](reassessment_2026-11-03_vi/00_final_reassessment_vi.md). |
| Review A′ | **[Đã kiểm tra]** Có contract toán v2, toy script, log/JSON/kết quả, memo readiness, register nguồn và handoff. | 192/192 assertion trong **một lần chạy toy được báo cáo**, không phải chứng minh trên MAG hay so sánh SOTA. [Toy report](aprime_review_2026-11-04/A1_toy_results.md). |
| Corpus | **[Đã kiểm tra]** 40 PDF hiện có trong `docs/papers/`; gồm 5 tài liệu từng thiếu, Wang–Kolar–Drton và supplement 29 trang, các prior art mở rộng. | PDF không được Git theo dõi. Phần đầu của [download status](../docs/papers/DOWNLOAD_STATUS_2026-11-04.md) là trạng thái hiện hành; các bảng bên dưới là nhật ký tải **cũ**. Zhang 2008 và sách Silvapulle–Sen đã có file; Zhang chưa đọc sâu, sách là OCR có lỗi ký hiệu. |
| Code hiện có | **[Đã kiểm tra]** `src/safety_prior/` là hạ tầng kill test scheduler-only prior, reference ICD, batch CI, frozen stable epoch; chưa có `aprime/`, MAG enumeration hay R1/BL1/BL9. | [README](../README.md), `src/safety_prior/`, [readiness §8](aprime_review_2026-11-04/A1_pilot_readiness.md). |
| Kết quả cũ | **[Theo báo cáo]** K0 220/220; K1 snapshot 675/800 run, 133 graph, tiết kiệm trung vị 23,60% **cho oracle FAS-stable**; G0–G2 của ICD PASS. | K1 formal gate chưa đóng, K2–K4 chưa chạy; các số này **không chứng minh** prior thực tế hay R1 hiệu quả. [Lịch sử §1–§4](../RESEARCH_HISTORY_vi.md). |
| Thử nghiệm hiện tại | **[Đã kiểm tra]** Chỉ có toy cho A′; benchmark S0–S4, public và real-world vẫn là protocol đề xuất. | [Readiness §6–§7](aprime_review_2026-11-04/A1_pilot_readiness.md). Không có graph truth nhân quả được đo cho R1. |

Lần rà soát này không thay đổi thuật toán hoặc dữ liệu. Git working tree sạch trước khi tạo báo cáo này. Kết quả `pytest` được ghi ở §9.

## 3. Vấn đề khoa học và cách R1 dự định giải

**Bài toán.** Từ dữ liệu quan sát có latent confounding, các CI test thường cho bằng chứng nhiễu và các graph trong cùng lớp tương đương có thể khác nhau về quan hệ tổ tiên. Một điểm số feature không kèm ý nghĩa tần suất có thể gây ra khẳng định quá tự tin. Mục tiêu của R1 là chỉ phát biểu một quan hệ tổ tiên `f` khi **mọi MAG phủ định `f`** đều không tương thích với một vùng tin cậy chung của vector CI statistics. Truth và *Q-identifiability* được định nghĩa **tương đối với họ MAG `M` và tập query `Q`**, không được đánh đồng với khả định từ toàn bộ phân phối. [Contract §1](aprime_review_2026-11-04/A1_mathematical_contract_v2.md).

**Thiết lập cụ thể [Theo báo cáo/Derived].** Cho `Q={X_k ⟂ Y_k | S_k}` cố định trước dữ liệu, `z_k=√(n−|S_k|−3) atanh(ρ̂_k)`, vector mean tiệm cận `ζ_n` và covariance `Σ`. Mỗi MAG `m` sinh một pattern `π(m)` của các CI facts và một vùng tọa độ thư giãn `R_n(m)`: tọa độ độc lập bằng 0, tọa độ phụ thuộc có `|ζ_k|≥δ_{n,k}`. Đặt `M_¬f` là các MAG phủ định feature. R1 sử dụng

`T(f) = inf_{m∈M_¬f, u∈R_n(m)} (z−u)ᵀ Σ⁺ (z−u)`

và chứng nhận `f` khi `T(f)>χ²_{r,1−α}`, với `r=rank(Σ)`; việc dùng seminorm `Σ⁺` cần được cố định rõ trong proof và code. Vì mọi MAG đúng thuộc `M`, `ζ_n∈R_n(m*)`, một confidence ellipsoid chung chứa `ζ_n` sẽ ngăn **đồng thời mọi chứng nhận sai**. Lập luận này cho upper bound tiệm cận `α+o(1)` dưới joint CLT, rank ổn định/ước lượng nhất quán, query cố định, và điều kiện vùng đúng. Vùng `R_n(m)` chỉ là **relaxation** của các mean Gaussian thật; tính thư giãn có thể làm giảm power nhưng không phá logic bảo thủ của R1. Đây hiện là **proof sketch**, chưa qua RG1. [Contract §1, §7, §10b](aprime_review_2026-11-04/A1_mathematical_contract_v2.md).

**R2.** `η*(f)=inf{η: f được chứng nhận ở mức α}` được đề xuất như một *sensitivity profile* đối với ngưỡng strong-faithfulness. Với một phân phối faithful cố định và `Q` hữu hạn, có thể chọn `η_n→0` nhưng `√nη_n→∞` để có validity **pointwise tiệm cận** mà không cần biết η cố định. Guarantee **uniform/hữu hạn mẫu** vẫn đòi hỏi giả định beta-min hoặc kết luận có điều kiện theo η. R2 chưa có định nghĩa và đánh giá đủ chặt để coi là đóng góp chính. [Erratum §10b](aprime_review_2026-11-04/A1_mathematical_contract_v2.md).

**Phạm vi hẹp hiện tại:** Gaussian/Fisher-z, `Q` chốt trước hoặc chọn trên mẫu khác, `M` hữu hạn có MAG thật, ancestral relations. Việc mở rộng sang endpoint feature, adaptive FCI trên cùng mẫu, GCM phi tham số hoặc selection bias rộng hơn **chưa được bảo đảm**. Zhang 2008 đã có file nhưng chưa được dùng để chốt semantics của endpoint. Joint CLT cho **vector** GCM chưa được chứng minh trong repo. [Contract §2.5–§2.6](aprime_review_2026-11-04/A1_mathematical_contract_v2.md).

## 4. Vì sao A′ gốc bị dừng: kết quả và ý nghĩa

1. **[Derived + toy] Covariance Fisher-z suy biến cấu trúc.** Với `p` biến Gaussian, rank tiệm cận của `Σ` không vượt `p(p−1)/2`. Ở `p=3`, sáu query bậc ≤1 chỉ có rank 3. Cặp `X⊥Y` và `X⊥Y|Z` có tương quan tiệm cận `√(1−ρ²_XZ)` khi `Y⊥(X,Z)`; nó bằng 1 nếu `Z` độc lập. Quy ước pseudo-inverse có ràng buộc support trong A′ gốc gán `+∞` cho **mô hình đúng** ở 100% replicate của toy trường hợp đó. [Contract §2.4](aprime_review_2026-11-04/A1_mathematical_contract_v2.md), [toy §4](aprime_review_2026-11-04/A1_toy_results.md).
2. **[Toy] Score dạng hiệu `D(f)=d²(z,M_¬f)−d²(z,M_f)` không giữ calibration như đã kỳ vọng.** Ở một cấu hình `δ=3`, false assertion rate của full-Σ là 0,110 và diag là 0,105; ở cấu hình khác diag không trôi. Một metric `Δ_FAR` trong plan cũ còn phạt chính thủ tục được hiệu chỉnh đúng. Đây là bằng chứng chống **framing và protocol cũ**, không chứng minh R1 hữu ích. [Toy §3](aprime_review_2026-11-04/A1_toy_results.md).
3. **[Toy] Ước lượng Σ là nút thắt thực.** Với covariance ước lượng nhiễu từ Wishart ở `K=8`, `r=0,9`, FAR của `T_full` tại `ν=20` là 0,337 dù mức danh nghĩa 0,05. Quy ước ridge/support/pseudo-inverse cũng đổi kết quả mạnh gần suy biến. [Toy §3.4–§4.2](aprime_review_2026-11-04/A1_toy_results.md).
4. **[Toy + suy luận] Lợi ích biểu kiến có thể đến từ thông tin ngoài `Q`.** Một residual của full-Σ tương quan `−0,9998` với thống kê của query `Y⊥Z|X` không nằm trong `Q`. Cần đối chứng trên *Q-closure* để tách hiệu quả covariance khỏi việc ngầm thêm query. Đây là cảnh báo về task equivalence, chưa là kết quả tổng quát. [Toy §4.3](aprime_review_2026-11-04/A1_toy_results.md).
5. **[Toy] η đặt sai có thể làm `D` sai dấu ngày càng chắc.** Trong toy với hiệu ứng thật `atanhρ=0,1`, `η=0,3` cho xác suất sai dấu tiến tới 1 khi `n=5000`. Điều này là cảnh báo cho score cũ và các tuyên bố uniform; không được gán nguyên xi cho R1 pointwise với `η_n→0`. [Toy §5](aprime_review_2026-11-04/A1_toy_results.md).

Các thí nghiệm trên chủ yếu dùng **working model** `z∼N(ζ,Σ)` và một SCM Gaussian 3 biến; 192 assertion PASS là kiểm tra nội bộ tính toán/đại số, **không phải** 192 thành công nhân quả độc lập. Chưa có kết quả R1 versus Bonferroni về certification power. [Toy report](aprime_review_2026-11-04/A1_toy_results.md).

## 5. Prior art và tính mới còn lại

| Nguồn gần nhất | Nội dung đã kiểm tra trong repo | Hệ quả cho claim R1 |
|---|---|---|
| [ACI, NeurIPS 2016](https://proceedings.neurips.cc/paper_files/paper/2016/hash/f3d9de86462c28781cbe5c47ef22c3e5-Abstract.html) | Có score forced-feature dạng hiệu trên ancestral statements; loss cộng tính. | “Feature confidence” và score dạng hiệu không mới; reduction của A′ chỉ về **loss kiểu ACI**, không trùng công thức weights của paper. |
| [Wang–Kolar–Drton, JASA, DOI](https://doi.org/10.1080/01621459.2025.2542552) và supplement | Test inversion cho tập causal orderings; Lemma 3 suy ra ancestral sub/superset từ confidence set. Theo bản đã đọc, giả định causal sufficiency, SEM identifiable với additive errors; tác giả nêu latent là hướng mở. | **Phép chiếu từ tập mô hình sang feature đã có**. Novelty R1 chỉ còn ở setting và thủ tục CI/MAG cụ thể, nếu power thực sự có ích. |
| [Triantafillou et al., PGM 2014](https://doi.org/10.1007/978-3-319-11433-0_32) | PROPeR/BiND dùng posterior p-value cho adjacency/non-adjacency của skeleton; không có ancestral feature hoặc frequentist validity. | Không subsume R1, nhưng là baseline/related work cho confidence cấp feature. |
| [Browne 1984, DOI](https://doi.org/10.1111/j.2044-8317.1984.tb00789.x), [Berger 1982, DOI](https://doi.org/10.1080/00401706.1982.10487790) | GLS/minimum-discrepancy cho cấu trúc covariance; intersection–union testing. | Cấu trúc kiểm định và phép chiếu không phải lý thuyết mới. |
| [Chang–Guo–Malinsky, arXiv](https://arxiv.org/abs/2405.06763), [Guo–Wu–Yiu, UAI 2026](https://proceedings.mlr.press/v337/guo26a.html) | Inference sau discovery; target là causal effect. Chang có resampling/screening trên PC; Guo xét FCI và selection. | R1 không thể bỏ qua selection của adaptive `Q`; adaptation của resampling sang feature là baseline **đề xuất**, validity của bản chuyển thể chưa tự động có. |
| [Zhang–Spirtes 2003](https://arxiv.org/abs/1212.2506), [Uhler et al. 2013](https://doi.org/10.1214/12-AOS1080) | Strong-faithfulness và giới hạn uniform consistency. | Không được coi `η` là chi tiết kỹ thuật nhỏ; R2 phải định vị trong dòng sensitivity/strong-faithfulness này. |

**RG0 [Theo báo cáo] PASS trong tập nguồn đã đọc**, theo [register §4–§5](aprime_review_2026-11-04/A1_missing_references_register.md). Phát biểu chính xác là: *trong các nguồn đã đối chiếu, chưa thấy một thủ tục chứng nhận frequentist cho ancestral feature ở MAG có latent từ vector CI statistics với cùng assumptions và target*. Đây **không** chứng minh không có prior art khác. Triển vọng Q1/ICML/NeurIPS chưa thể đánh giá từ “chưa thấy” và proof sketch; cần một cơ chế có giá trị thực tế rõ ràng, bằng chứng cơ chế và đối chứng mạnh.

## 6. Thiết kế đánh giá đã có; phần chưa thực hiện

**Estimand chính E1:** (i) family-wise false certification rate `P(∃f được assert sai)` ở mức `α`; (ii) certification power trên **feature đúng và Q-identifiable**. Đơn vị độc lập là SCM, không phải feature hoặc query. R2/η-profile là estimand phụ. [Readiness §4](aprime_review_2026-11-04/A1_pilot_readiness.md).

**Baseline cùng target cần ưu tiên:** BL1 Bonferroni per-test IUT; BL9 chuyển thể resampling/screening của Chang sang feature **nếu định nghĩa và validity được chứng minh**; BL2 diagonal covariance là negative/control và **không valid nói chung**, nên không được coi là đối thủ ngang hàng ở cùng α. BL3 Q-closure làm đối chứng thông tin nhưng input lớn hơn, phải báo cáo chi phí và so sánh tách riêng. ACI, bootstrap FCI frequency, BSC-D có output/assumptions khác và chỉ nên dùng trong bảng mô tả hoặc đánh giá phụ. WKD cũng khác mô hình và causal sufficiency. [Readiness §5, §11](aprime_review_2026-11-04/A1_pilot_readiness.md).

**Bộ thí nghiệm đề xuất, chưa chạy:** RG2 toy `K=2–6` để kiểm power ở cùng mức error; S0 tính rank/correlation bằng delta method trên SCM `p=4–5`; S1 pilot Gaussian có latent với `n∈{500,2000,5000}` và SCM làm đơn vị; S2 stress adaptive `Q`; S3 η misspecification; S4 phi tham số chỉ sau joint CLT GCM. Dữ liệu public/real chỉ mở rộng sau S1; Sachs không phải causal ground truth đầy đủ. [Readiness §6–§7](aprime_review_2026-11-04/A1_pilot_readiness.md).

**Tính khả thi chưa biết:** số MAG ở `p=4–5`, độ đúng của latent projection/m-separation implementation, chi phí tối ưu khi `K` tới khoảng 70, xử lý rank gần suy biến, và ổn định `Σ̂`. Solver active-set toy có chi phí tăng theo `3^{#dependent}` nên không thể mặc nhiên chuyển vào pilot lớn. [Readiness §8](aprime_review_2026-11-04/A1_pilot_readiness.md).

## 7. Các gate và quyết định kế tiếp

| Gate | Điều kiện cần và artifact | Trạng thái |
|---|---|---|
| **RG0 — nguồn** | Đọc prior art gần nhất, so assumptions/target/mechanism. | **PASS theo agent**; corpus hiện đủ, nhưng không phải chứng nhận novelty toàn cục. |
| **RG1 — toán** | Proof đầy đủ cho R1 rank-aware/seminorm/estimated Σ, `Q` cố định, pointwise `η_n`; chứng minh độ đơn điệu R2 và điều kiện power; rà soát độc lập. | **Chưa xong.** |
| **RG2 — kill test power** | Toy có alternative thật, so R1 với BL1 cùng α và BL2 như control; thêm BL9 nếu chuyển thể được đúng target. Định nghĩa trước hiệu ứng tối thiểu có ý nghĩa. | **Chưa chạy.** Nếu R1 không vượt baseline valid ở regime liên quan, **STOP A′**. |
| **RG3 — prevalence** | S0 đo tương quan, rank và cặp query gây ảnh hưởng thật trong suy luận feature. | **Chưa chạy.** Nếu hiệu ứng hiếm, claim cơ chế yếu. |
| **RG4 — pilot nhân quả** | Chỉ sau RG1–RG3 dương; so với baseline cùng target, kiểm false certification và power trên SCM có latent. | **Chưa chạy.** |

**Đề xuất ưu tiên [Suy luận]:** trước tiên khóa RG1 và thiết kế RG2; đây là hai công việc rẻ nhất và có khả năng bác bỏ hướng. Không nên xây `src/safety_prior/aprime/` hay chạy hàng nghìn SCM lúc này. Một kết quả RG2 dương vẫn chỉ là điều kiện mở RG3/RG4, chưa là kết luận công bố. Quyết định này phù hợp [research gates](../research/07-workflow-and-decision-gates.md) và phần cập nhật mới nhất của [readiness](aprime_review_2026-11-04/A1_pilot_readiness.md).

## 8. Hướng dự phòng và các hướng đã hạ ưu tiên

**T4 — selection-indexed premises under missing data** vẫn là dự phòng có failure oracle đã được nguồn M1 ghi nhận: ghép CI premises từ các selection populations khác nhau có thể làm orientation sai. Cơ chế đề xuất là xác nhận theo *proof* thay cho xác nhận listwise toàn cục; nhưng **lemma transport theo proof chưa có** và có nguy cơ rút về m-separation trên augmented graph. Kill test đầu tiên là thử chứng minh hoặc tìm phản ví dụ cho R0/R4, rồi đo effective sample size và endpoint error so với M1 wrapper/listwise/MI. **Chưa có pilot T4.** [Topic card T4](reassessment_2026-11-03_vi/topic_cards/T4_selection_indexed_premises_missingness_vi.md).

C-S (*coordinated-shift breakdown radius*) đứng thứ ba vì identifiability và prior art còn mở; B′ (*query complementarity*) bị hạ ưu tiên do prior art dày. D1–D4/dcFCI pruning và lập lịch CI bằng LLM/prior không được khôi phục làm đóng góp chính chỉ vì code đã có. [Reassessment](reassessment_2026-11-03_vi/00_final_reassessment_vi.md), [do-not-redo registry](../RESEARCH_HISTORY_vi.md).

## 9. Kiểm tra kỹ thuật trong lần rà soát này

- [Đã kiểm tra] Git working tree sạch **trước** khi viết báo cáo; 5 commit mới nhất kết thúc bằng cập nhật README/lịch sử ngày 04/11.
- [Đã kiểm tra] 40 PDF trong `docs/papers/`, gồm file Zhang 2008 và Silvapulle–Sen 2005; chỉ số lượng/file hiện diện, không có kiểm toán lại 551 trang sách.
- [Đã kiểm tra] `src/safety_prior/` chưa có module R1; `A1_toy_outputs.json`, `A1_toy_run_log.txt` hiện diện. Không chạy lại toy 312 giây vì không có rủi ro mới cần giải quyết.
- [Đã kiểm tra] `python -m pytest -q` kết thúc với **exit code 0**; output hiển thị các test chạy qua và một số test bị skip. Đây là test suite của code nền `safety_prior`, **không** kiểm chứng R1.

## 10. Kết luận khoa học

**Vấn đề đáng theo đuổi nhất hiện tại** là chứng nhận được các quan hệ tổ tiên dưới latent confounding khi bằng chứng CI có nhiễu và graph không định danh duy nhất. **R1 là đề xuất có target và kiểm soát lỗi rõ**, nhưng cơ chế toán trung tâm phần lớn đã có prior art; vì vậy chất lượng đóng góp phụ thuộc vào việc thủ tục thực sự tạo **power hữu ích và lợi ích có thể giải thích** trong setting MAG/CI mà các phương pháp gần nhất không giải quyết. **T4** là phương án dự phòng nếu RG2 hoặc RG3 âm.

**Trạng thái cuối:** *REFORMULATE / chưa GO*. Bằng chứng không thể thiếu trước khi đầu tư vài tháng là: proof RG1 được rà soát, kill test RG2 vượt baseline valid cùng target, và RG3 cho thấy regime đó xuất hiện trong bài toán nhân quả thực tế. Nếu một trong ba thất bại, ghi negative-result memo và chuyển hướng thay vì mở rộng phạm vi claim.
