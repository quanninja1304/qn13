# Research Topic Reassessment & Methodological Research Discovery — Báo cáo tổng hợp A–J

Ngày: **03-11-2026**. Báo cáo này là **literature reassessment**. **Không có baseline, pilot hay framework nào được chạy.** Mọi pilot dưới đây chỉ là thiết kế, ghi rõ *chưa chạy*.

Nguồn đầu vào: `source_audit_ci.md`, `source_audit_budget.md`, `source_audit_heterogeneity.md`, `source_audit_missingness.md`, `source_audit_supplement.md` (cùng thư mục) và `topic_cards/`.

Nhãn: **[Verified]** nội dung đã đối chiếu primary source (không có nghĩa đã tái lập); **[Verified-abstract]** chỉ đối chiếu metadata/abstract; **[Summary-only]** chỉ đọc qua bản trích xuất tự động; **[Inference]**, **[Hypothesis]**, **[Unresolved]**.

---

## Tóm tắt quyết định

- **Primary (Conditional): A′ — Dependence-aware feature confidence.** Thay loss cộng tính, giả định test độc lập của ACI/HEJ bằng khoảng cách Mahalanobis trên vector Fisher-z, dùng để xếp hạng độ tin cậy của ancestral/endpoint features. Novelty đã bị thu hẹp tới **một yếu tố duy nhất** (hiệp phương sai off-diagonal giữa các CI statistic tính trên cùng mẫu), vì "forced-feature distance" chính là **ACI Eq. 16** (NeurIPS 2016).
- **Backup (Conditional): T4 — xác nhận selection cục bộ theo từng orientation proof dưới missing data.** Failure đã được xác minh ở oracle level (M1 §10.1); kill test thuần lý thuyết.
- **Thứ ba: C-S** (breakdown radius trước coordinated shifts) — gap chưa kiểm tra trước hai preprint 2024/2026.
- **Hạ ưu tiên: B′** (query complementarity); **không khôi phục** D1–D4 hay dcFCI pruning.
- **Cập nhật cùng ngày** (xem `A1_gap_confirmation_and_proof_sketch_vi.md`):
  - Đã đọc full text Guo–Wu–Yiu: gap của A′ còn sống.
  - Đã đọc full text BSC-D (`docs/papers/bscd.pdf`): gap còn sống nhưng hẹp hơn. BSC-D báo cáo dependence **không** đổi thứ tự PAG và không đổi SHD, nên hypothesis chính của A′ chuyển sang **calibration ở cấp feature**.
  - Đã có chứng minh rút gọn: với Σ chéo thì score trùng đúng ACI; novelty nằm hoàn toàn ở off-diagonal.
  - Đe dọa mới: feature posterior dựa trên full likelihood. A′ được định vị lại cho CI statistics tổng quát (kernel/GCM/mixed).
- **Plan các bước tiếp theo của A′** (phases, gates, decision log để backtrack): `A1_next_steps_plan_vi.md`.
- **Chưa candidate nào đạt Go.** Bằng chứng không thể thiếu trước khi đầu tư nhiều tháng là đọc full text của Guo–Wu–Yiu (UAI 2026) và BSC-D, sau đó chạy reduction test của A′ (§H).

---

## Report A — Research landscape (22 công trình cốt lõi)

Chi tiết assumptions, theorem và hạn chế nằm trong các audit nhánh (cột ID). "Closest" cho biết candidate mà công trình là đối thủ gần nhất.

| ID | Công trình (venue/status) | Problem → output | Central insight / mechanism | Giới hạn chính | Closest |
|---|---|---|---|---|---|
| CI01 | Colombo et al., RFCI — *Ann. Stat.* 2012 [DOI](https://doi.org/10.1214/11-AOS940) | Latent/selection → RFCI-PAG | Bỏ Possible-D-SEP; kiểm tra khi orientation | Ít thông tin hơn FCI; không có finite-sample confidence | nền |
| CI02 | Colombo & Maathuis, *JMLR* 2014 [PDF](https://www.jmlr.org/papers/volume15/colombo14a/colombo14a.pdf) | Order-independence | Stable + conservative/majority rules | Không phải calibration | A′ baseline |
| CI03 | Claassen & Heskes, BCCD — IJCAI 2013 / UAI 2012 [link](https://ijcai.org/proceedings/2013/443) | Ancestral statements có xác suất | Posterior cục bộ → logical statements theo reliability | Subset cap, phụ thuộc prior | A′ |
| CI04 | Hyttinen–Eberhardt–Järvisalo, HEJ — UAI 2014 [PDF](https://www.its.caltech.edu/~fehardt/papers/HEJ_UAI2014.pdf) | Weighted conflict resolution | ASP min weighted violations | NP-hard, nhỏ | A′ |
| **S1** | **Magliacane–Claassen–Mooij, ACI — NeurIPS 2016** [HTML](https://arxiv.org/html/1606.07035v3) | Ancestral relations + confidence | **Eq. 16: C(f)=min L(¬f) − min L(f)**, loss cộng tính | Giả định test độc lập; không selection/cycles; n ≤ 9 | **A′ (closest)** |
| CI05 | Jabbari et al., BSC-D — ECML-PKDD 2017 [DOI](https://doi.org/10.1007/978-3-319-71246-8_9) | Rank PAGs | Dependence giữa CI facts qua bootstrap | Discrete; thường cùng best PAG với BSC-I | **A′ (closest)** |
| CI06 | Ribeiro & Heider, dcFCI — arXiv 2025 (preprint) [abs](https://arxiv.org/abs/2505.06542) | Candidate r-PAG + score | MEC-targeted hypotheses, Fréchet bounds | Truncation; không calibration | A′ baseline |
| CI07 | Zhou et al., DAGPA — NeurIPS 2025 [record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bc688efcf83bb744e1283897bfd4afa0-Abstract-Conference.html) | Differentiable low-order d-sep | Percolation soft logic | Causal sufficiency, order ≤1 | adj. |
| CI08 | Malinsky, cautious model selection — arXiv 2024 v3 (Stat. Sci. forthcoming) [HTML](https://arxiv.org/html/2404.18232v3) | Skeleton supergraph | Equivalence tests | δ₀ chưa biết; PC | A′ |
| CI09 | Faller & Janzing — AISTATS 2026 [PMLR](https://proceedings.mlr.press/v300/faller26b.html) | Các loại redundancy, MMD | Phân biệt redundancy GA/GM | DAG/tree | A′ |
| S3 | Guo–Wu–Yiu — UAI 2026 [PMLR](https://proceedings.mlr.press/v337/guo26a.html) | Selective inference sau FCI | Selection event = polyhedron trong Fisher-z (abstract) | Target effect | **A′ (threat)** |
| S4 | Chang–Guo–Malinsky — *Biometrika* 2026 (theo EconPapers) [arXiv](https://arxiv.org/abs/2405.06763) | Post-selection effect inference | Resampling | Target effect | A′ |
| B01 | Rohekar et al., ICD — NeurIPS 2021 [PDF](https://proceedings.neurips.cc/paper/2021/file/144a3f71a03ab7c4f46f9656608efdb2-Paper.pdf) | Anytime PAG | Conditioning size gắn PDS radius | Sound ở completed iteration | B′ |
| B02 | Kocaoglu, k-PC — NeurIPS 2023 | k-essential graph | Restricted CI semantics | Causal sufficiency | B′ |
| B03 | Lee–Ribeiro–Kocaoglu, C-PC — UAI 2025 [PMLR](https://proceedings.mlr.press/v286/lee25a.html) | C-essential graph | Conditioning collections | Có phản ví dụ cho các naive variants | B′ |
| B04 | Shiragur–Zhang–Uhler — ICML 2024 [PMLR](https://proceedings.mlr.press/v235/shiragur24a.html) | CCPG với ít test | Prefix sets | Output thô hơn | B′ |
| B11 | Franquesa Monés–Zhang–Uhler, GAS — arXiv 2603.21844 (preprint) | Số CI test | Ancestry-first | DAG-faithful | B′ |
| H1 | Mooij–Magliacane–Claassen, JCI — *JMLR* 2020 [link](https://jmlr.org/papers/v21/17-123.html) | Multi-context discovery | Context variables | Không calibration | C-S |
| H5 | Mameche–Vreeken–Kaltenpoth, CoCo — AISTATS 2024 [PMLR](https://proceedings.mlr.press/v238/mameche24a.html) | Confounding từ mechanism shifts | Partition dependence | Independent/sparse shifts | **C-S (closest)** |
| H6 | Mameche et al., CMM — NeurIPS 2025 | Causal mixtures | Latent-aware BIC | EM consistency mới là conjecture | C-S |
| M1 | Strobl–Visweswaran–Spirtes — *IJDSA* 2018 [DOI](https://doi.org/10.1007/s41060-017-0094-6) | FCI với missingness | Test-wise + listwise re-check | Mất mẫu | **T4 (closest)** |
| M2 | Tu et al., MVPC — AISTATS 2019 [PMLR](https://proceedings.mlr.press/v89/tu19a.html) | PC với missingness | Selective correction | Causal sufficiency | T4 |

Ngoài bảng (adjacent, chỉ đọc một phần): H2 CD-NOD, H3 ψ-FCI, H4 UT-LVCE, H7 fedCI-IOD, B05 GPS, B06 Dseptor, B07 MAGLIST-POLY, M3 Witte et al., M4 PAIR-CI, M5 Versteeg et al., S5 Strieder et al., S6 Gradu et al., S7 Reddy–Balasubramanian, S8 StruBI (chưa xác minh primary). Xem các audit nhánh và supplement.

---

## Report B — Reproducible failure modes

| Dossier | Quan sát / điều kiện | Cơ chế giả thuyết | Bằng chứng | Remedy mạnh nhất | Reproduction tối thiểu (chưa chạy) | Điều làm sụp vấn đề |
|---|---|---|---|---|---|---|
| **F-A1′: Đếm trùng evidence tương quan trong feature confidence** | n vừa, conditioning sets chồng lấp, đồ thị dày, có latent | Fisher-z statistics trên cùng hàng dữ liệu có tương quan; loss cộng tính (ACI Eq. 13) coi chúng là độc lập → confidence bị thổi phồng | [Verified] loss cộng tính; [Summary-only] tác giả ACI thừa nhận giả định độc lập là sai; [Inference] tương quan tiệm cận là thật về toán; **mức ảnh hưởng tới ranking chưa biết** | BSC-D; bootstrap ACI/FCI; CFCI-stable | p=4–5 exhaustive, một latent; so C(f) với query universe tối thiểu và có thêm các test gần dư thừa | Ranking gần như không đổi giữa full-Σ và GLS-reweighted ACI (Kendall τ≈1) trên các regime thực tế |
| **F-T4: Ghép premise từ các selection population khác nhau** | Missingness không ngẫu nhiên, test-wise deletion | Premise A đúng trên S_A, B trên S_B; kết luận chỉ hợp lệ trên S_A∩S_B | [Verified] phản ví dụ oracle M1 §10.1 | M1 Algorithm 1 (listwise re-check) | Tái lập ví dụ oracle, sau đó finite sample p=5–6 | Rule theo proof rút về m-separation chuẩn; lượng mẫu thu lại không đáng kể |
| **F-C: Coordinated shifts bị đọc nhầm là latent confounding** | Môi trường có can thiệp được điều phối | Partition dependence không do latent | [Hypothesis]; CoCo assumptions loại trừ trường hợp này | JCI-FCI với design variables; leave-k-out | 3–6 nút, oracle partitions, hai arm | Không phân biệt được ở oracle level; trimming đã giải được |

Ghi chú phụ: **F-B** (ICD rollback lãng phí query) là [Hypothesis] chưa có mức ảnh hưởng (xem `source_audit_budget.md` §4).

---

## Report C — Methodological opportunities (Problem → Gap → Insight → Method → Evidence → Contribution)

Chi tiết đầy đủ theo template nằm trong `topic_cards/`.

### C1. A′ — Dependence-aware feature confidence ([card](topic_cards/A1_dependence_aware_feature_confidence_vi.md))
- **Problem:** feature-level confidence quyết định hành động downstream; nếu đếm trùng evidence, người dùng sẽ tự tin quá mức.
- **Gap ([Hypothesis], hẹp):** ACI/HEJ dùng loss cộng tính; BSC-D mô hình dependence ở cấp graph score, không ở cấp feature ranking; S3 có joint Fisher-z geometry nhưng target là effect.
- **Insight:** độ tin cậy = khoảng cách Mahalanobis từ z quan sát tới vùng các vector thống kê tương thích với ¬f.
- **Method:** D(f) = min_{m ⊨ ¬f} min_{z' ∈ R(m)} (z−z')ᵀΣ̂⁻¹(z−z'), với Σ̂ closed-form hoặc bootstrap.
- **Falsifiable hypothesis:** ở regime chồng lấp/dày, full-Σ D(f) giảm false ancestry assertions so với GLS-ACI và bootstrap ở cùng coverage và compute.
- **Contribution:** score mới + reduction theorem + characterization về khi nào co-errors quan trọng.

### C2. T4 — Per-proof selection confirmation ([card](topic_cards/T4_selection_indexed_premises_missingness_vi.md))
- **Problem:** missing data làm mất mẫu (listwise) hoặc làm sai orientation (naive test-wise).
- **Gap:** M1 xác nhận theo từng CI; chưa thấy rule theo từng proof.
- **Insight:** chỉ tập premise tối thiểu của một proof cần chung một population.
- **Method:** gắn selection set cho từng premise; xác nhận lại trên ∩ của các premise cần thiết, trừ khi một lemma transport (cần chứng minh) cho phép bỏ qua.
- **Hypothesis:** tăng effective-n cho orientations mà endpoint error không tăng.
- **Contribution:** lemma + missingness-aware FCI.

### C3. C-S — Breakdown radius ([card](topic_cards/CS_coordinated_shift_breakdown_radius_vi.md))
- **Problem:** báo confounding giả khi shifts được điều phối.
- **Gap:** [Unresolved] (S7/S8 chưa đọc).
- **Insight:** contamination tối thiểu đủ để giải thích một declaration.
- **Method:** minimal contamination mask → radius/abstention.
- **Hypothesis:** radius tách được hai arm tốt hơn trimming.

### C4. B′ — Query complementarity ([card](topic_cards/B1_query_complementarity_budget_vi.md))
- Hạ ưu tiên; chỉ một pilot oracle nhỏ nếu các hướng khác thất bại.

---

## Report D — Novelty & depth audit

| Candidate | Closest method | Có thể tương đương kỹ thuật cũ? | Claim novelty còn lại + bằng chứng cần có | Theory tối thiểu | Rủi ro incremental |
|---|---|---|---|---|---|
| A′ | ACI Eq. 16; BSC-D; S3 | **Có**: với Σ̂ chéo → ACI có weights bình phương; với bootstrap → gần BSC-D | Chỉ off-diagonal dependence ở cấp feature ranking; cần bằng chứng là ranking thay đổi có ý nghĩa | Oracle soundness; duplicate-invariance; reduction theorem | **Cao** nếu lợi ích nhỏ; thành "reweighting" |
| T4 | M1 Algorithm 1; m-separation trên augmented graph | Có thể là m-separation chuẩn | Lemma transport theo proof, mạnh hơn rule theo CI | Lemma cho R0/R4; oracle equivalence với target M1 | Trung bình |
| C-S | CoCo; trimming; S7/S8 | Có thể là robust trimming | Estimand radius identifiable + vượt trimming | Identifiability + phản ví dụ | Trung bình–cao (identifiability) |
| B′ | ICD; GAS; ABCD | Batched active learning / set cover | Complementarity đáng kể | Construction chỉ ra singleton thất bại | Cao |

Đã loại: "multi-environment FCI", "joint graph+partition learning", "anytime latent discovery", "restricted-CI semantics", "forced-feature confidence", "weighted conflict resolution". Tất cả đều đã có prior art trực tiếp (xem claim registers).

---

## Report E — Evaluation strategy

- **Synthetic (bắt buộc, truth đã biết):** latent DAG → MAG/PAG bằng implementation đã kiểm tra; ER/scale-free; p=4–8 cho exhaustive, p=10–20 cho approximate; n ∈ {100, 300, 1000}; latent fraction ∈ {0, 0.2}; linear-Gaussian trước, nonlinear/mixed là robustness arm (ở arm này CI test bị misspecified).
- **Semi-synthetic:** bnlearn (ALARM/CHILD/ASIA) với biến bị ẩn hoặc missingness được tiêm; causalAssembly (adaptation, cần pin version). **Chưa tải.**
- **Public/real:** Causal Chamber (NMI 2025, CC-BY 4.0) cho ancestry đã được validation; Sachs chỉ để kiểm tra intervention consistency; CausalBench chỉ là optional application. **Tất cả chưa tải, chưa pin version.**
- **Baselines theo candidate:** xem cards. Mỗi candidate có ≥3 nhóm baseline; A′ luôn gồm ACI, BSC-D (adaptation), bootstrap FCI và GLS-ACI.
- **Metrics:** false definite assertions tại matched coverage; risk–coverage AUC; precision@k; endpoint/ancestry errors theo semantics phù hợp (không chấm RFCI như FCI); runtime/CPU/RSS; số CI test.
- **Statistical controls:** đơn vị độc lập là SCM; paired comparison theo SCM; tách seeds pilot và confirmatory; báo CI 95%; báo cả các run thất bại hoặc timeout.
- **Task equivalence:** cùng query universe, cùng CI test, cùng α, cùng output semantics, cùng compute budget giữa các phương pháp.
- **Reproducibility:** pin dependencies; lưu raw CI tables; config-driven runs.

---

## Report F — Comparative decision matrix

| Tiêu chí | A′ | T4 | C-S | B′ |
|---|---|---|---|---|
| Significance | Cao: confidence cấp feature ảnh hưởng mọi ứng dụng downstream | Cao trong y sinh; hẹp hơn ở ML | Trung bình: chỉ trong setting multi-context | Trung bình |
| Gap credibility | Thấp–trung bình: chỉ còn một yếu tố, hai threat chưa đọc | Trung bình: failure oracle đã xác minh, rule mới chưa có | Thấp: [Unresolved] | Thấp |
| Central insight | Rõ, toán học cụ thể | Rõ nhưng có thể tầm thường | Rõ, có rủi ro không identifiable | Mơ hồ |
| Originality | Phụ thuộc toàn bộ vào off-diagonal | Phụ thuộc vào lemma | Phụ thuộc vào S7/S8 | Thấp |
| Theoretical burden | Thấp–vừa | Vừa (proof là cốt lõi) | Vừa–cao | Thấp |
| Empirical feasibility | Cao (Gaussian, CPU, exhaustive nhỏ) | Cao | Cao (oracle) | Cao |
| Benchmark availability | Tốt | Trung bình (truth của missingness là synthetic) | Hạn chế (không có shared-latent truth thật) | Tốt |
| Generality | Mọi constraint-based method có weights | FCI-family + missingness | Hẹp | Trung bình |
| Survivability | Có negative result hợp lệ, nhưng khó publish | Lemma đứng được riêng | Có thể chỉ còn "limitation" | Thấp |
| Time-to-first-evidence | **Ngắn nhất** (reduction trên giấy + pilot p≤5) | Ngắn (trên giấy) | Trung bình | Trung bình |
| Fit Q1 / top ML (conditional) | UAI/AISTATS/IJAR; top ML chỉ khi có guarantee | Q1 stats/epi | UAI/CLeaR | yếu |

**Lý giải:** A′ thắng vì có time-to-first-evidence ngắn nhất, kill test sắc nét, và câu hỏi ảnh hưởng tới mọi phương pháp weighted constraint-based. Nó **không** thắng nhờ novelty đã được chứng minh. T4 là backup vì failure đã được xác minh và chi phí kiểm tra thấp, nhưng mức tổng quát thấp hơn. C-S đứng sau vì gap chưa kiểm tra và rủi ro identifiability.

---

## Report G — Recommended direction

- **Primary: A′ (Conditional).** Thắng so với closest prior art chỉ khi off-diagonal dependence thay đổi feature ranking một cách có ý nghĩa. So với các candidate khác, A′ cho bằng chứng quyết định sớm nhất.
- **Backup: T4 (Conditional).** Chọn nếu A′ bị reduction test hoặc S3/BSC-D chặn.
- **Ambitious optional extension (chỉ khi pilot A′ dương):** feature statements hợp lệ theo selective inference, dùng polyhedral Fisher-z geometry (nối với S3).
- **Không cam kết framework nào ở thời điểm này.** Đây là một khuyến nghị chính đáng theo `08-deliverables.md` §G.

---

## Report H — Roadmap 4–6 tuần (toàn bộ là việc tương lai; chưa có gì được làm ngoài literature)

| Tuần | Việc | Artifact | Gate |
|---|---|---|---|
| 1 | Đọc full text S3 (Guo–Wu–Yiu), BSC-D, HEJ (cần công cụ trích xuất PDF); kiểm tra lại các mục [Summary-only] của ACI §6 | Bổ sung supplement | **G1:** S3/BSC-D có định nghĩa cùng feature score không? Có → A′ no-go, chuyển sang T4 |
| 2 | Reduction trên giấy: Σ̂ chéo ⇒ ACI; điều kiện để off-diagonal thay đổi argmin. Song song: chứng minh/bác bỏ lemma T4 cho R0 | Ghi chú toán | **G2:** reduction cho thấy D(f) ≡ GLS-ACI trong mọi trường hợp → A′ no-go |
| 3 | Pilot A′: p=4–5 exhaustive, 50 SCM, ACI vs GLS-ACI vs full-Σ vs bootstrap; tách seeds | Raw CI tables, Kendall τ, risk–coverage | **G3:** τ≈1 hoặc không có lợi ích ở matched coverage → no-go |
| 4 | Controls: matched compute, abstention-matched, misspecified arm; tái lập ACI baseline | Evidence table | **G4:** lợi ích độc lập, lặp lại được ở ≥2 regime |
| 5–6 | Nếu G4 đạt: scalable approximation, bnlearn adaptation, Causal Chamber; viết paper concept. Nếu không đạt: pivot sang T4 (lemma + pilot) | Decision memo | **G5:** adversarial review |

Stop/continue/pivot: hai gate thất bại liên tiếp ở A′ → chuyển sang T4. T4 thất bại ở G2 → báo cáo **không có gap khả thi** trong scope hiện tại thay vì ép một recommendation.

---

## Report I — Paper concept (cho A′; mọi contribution đều là *tiềm năng*)

- **Tentative title:** *Counting Evidence Once: Dependence-Aware Confidence for Causal Features under Latent Confounding*
- **Research question:** dependence giữa các CI statistic tính trên cùng mẫu có làm sai lệch feature-confidence ranking của weighted constraint-based discovery không, và một khoảng cách thống kê chung có sửa được điều đó không?
- **Problem statement:** cho trước query universe Q, model family M (ancestral/MAG) và vector Fisher-z z cùng hiệp phương sai Σ, hãy xếp hạng các features f theo mức fragility trước những dao động thống kê hợp lý.
- **Closest work:** ACI (NeurIPS 2016), BSC-D (2017), HEJ (2014), Guo–Wu–Yiu (UAI 2026), bootstrap FCI.
- **Insight:** confidence nên được đo trong hình học chung của các thống kê, không phải bằng tổng các weight biên.
- **Central mechanism:** Mahalanobis distance tới vùng feature-negating.
- **Potential contributions:** (1) reduction theorem và oracle soundness; (2) characterization thực nghiệm về khi nào co-errors làm sai ranking; (3) một approximation có thể mở rộng, có báo cáo search gap.
- **Proof obligations:** soundness; duplicate-invariance; reduction; (extension) selective validity.
- **Experimental hypotheses:** H1: lợi ích tăng theo mức chồng lấp của conditioning sets; H2: lợi ích biến mất khi các test gần độc lập; H3: lợi ích không tái tạo được bằng GLS-ACI hoặc bootstrap với cùng compute.
- **SOTA comparisons / datasets:** như Report E.
- **Limitations:** Gaussian asymptotics; δ chưa biết; scalability.
- **Hypothetical abstract (không chứa kết quả bịa):**

> Constraint-based causal discovery methods that reconcile conflicting conditional-independence (CI) evidence, such as Ancestral Causal Inference, score causal features by adding up independent per-test weights. Yet CI statistics computed on the same sample with overlapping conditioning sets are strongly dependent, so additive scores may count one random fluctuation several times. We ask whether this dependence distorts the confidence ranking of ancestral and endpoint features under latent confounding. We propose to measure feature confidence as a joint statistical distance from the observed vector of Fisher-z statistics to the set of statistic vectors compatible with a model that negates the feature, using the full asymptotic or bootstrap covariance of the statistics. We state the conditions under which this score reduces to existing additive scores, establish its oracle soundness, and plan to characterize, across graph density, sample size and query redundancy, when dependence-aware scoring changes risk–coverage trade-offs relative to additive, bootstrap and dependence-modeling baselines under matched budgets. We also delineate the regimes, such as misspecified CI tests and nearly independent queries, in which no benefit should be expected.

---

## Report J — Critical final verdict

1. **Vấn đề quan trọng nhất về mặt khoa học:** độ tin cậy ở cấp feature của causal discovery khi CI evidence không đáng tin (A). Vấn đề này có ý nghĩa với mọi ứng dụng downstream.
2. **Cơ chế có novelty dễ bảo vệ nhất:** không có candidate nào mạnh. Defensible nhất là lemma per-proof selection của T4 (nếu chứng minh được), vì nó là một rule suy luận mới thay vì một reweighting. A′ có novelty hẹp và bị đe dọa trực tiếp.
3. **Thực hiện được với tài nguyên hiện tại:** cả A′ và T4 (CPU, Gaussian, exhaustive nhỏ, chủ yếu là theory). Repo hiện chưa có implementation của ACI/BSC-D; phải tự viết hoặc tái lập.
4. **Cân bằng chất lượng/rủi ro tốt nhất cho Q1:** T4 nếu lemma đúng (Q1 stats/epi); A′ nếu reduction test dương.
5. **Điều kiện để cạnh tranh ở ICML/NeurIPS:** A′ cộng với feature statements hợp lệ theo selective inference (có guarantee), lợi ích thực nghiệm nhất quán trên nhiều regime, và approximation có thể mở rộng. Hiện tại không có bằng chứng nào cho điều này.
6. **Bằng chứng không thể thiếu trước khi đầu tư nhiều tháng:** (a) đọc full text S3 và BSC-D; (b) reduction trên giấy; (c) pilot p≤5 đo Kendall τ và false assertions ở matched coverage so với GLS-ACI.
7. **Nên bỏ hoặc hạ ưu tiên:** B′ (prior art dày đặc: ICD/k-PC/C-PC/CCPG/GAS); general multi-environment FCI; joint graph+partition learning; "forced-feature confidence" (đã là ACI); D1–D4 và dcFCI pruning (không khôi phục vì sunk cost).

---

## Checklist đối chiếu yêu cầu

| Yêu cầu | Vị trí |
|---|---|
| AGENTS.md 1: 15–25 papers | Report A (22 cốt lõi + adjacent) |
| AGENTS.md 2: 2–3 failure modes + remedies | Report B |
| AGENTS.md 3: 3–5 candidates riêng biệt | Report C (4) |
| AGENTS.md 4: insight, mechanism, prior art, pilot, ≥3 baselines, eval, risks | `topic_cards/` + Report D/E |
| AGENTS.md 5: xếp hạng có lý giải | Report F |
| AGENTS.md 6: primary/backup/go-no-go | Report G/H/J |
| 08 §A–J | Đủ các mục A–J |
| Không trình bày pilot như đã chạy | Mọi pilot ghi *chưa chạy* |
| Nguồn primary + status | Bảng A + supplement; preprints được ghi rõ |
