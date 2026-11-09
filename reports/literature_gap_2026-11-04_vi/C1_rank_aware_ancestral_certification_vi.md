# Topic card C1 — Rank-aware ancestral certification từ CI evidence có latent

> Status: **Conditional / RG0 PASS theo agent, RG1–RG2 chưa chạy**. Ngày 04/11/2026. Đây là R1 đã cải biên, không hồi sinh score D(f) gốc.

## One-sentence research question

Với Gaussian observational data, latent MAG thật nằm trong họ M và tập CI query Q cố định, liệu có thể chứng nhận đồng thời các ancestral features với family-wise false certification tiệm cận ≤ α mà vẫn có power hữu ích hơn Bonferroni IUT?

## Problem & significance

Nhà nghiên cứu dùng ancestry để chọn giả thuyết/can thiệp, nhưng PAG và score confidence từ CI có thể mơ hồ hoặc quá tự tin. Đầu ra cần là **assert/abstain với error target**, không phải best graph.

## Closest prior art & gap

| Source | Contribution | Assumption/limitation | Novelty consequence |
|---|---|---|---|
| [ACI](<../../docs/papers/ACI_2016.pdf>) | Forced-feature loss/score trên ancestry. | Không frequentist family-wise guarantee. | Score-feature không mới. |
| [Wang–Kolar–Drton](<../../docs/papers/Confidence Sets for Causal Orderings.pdf>) + [supplement](<../../docs/papers/Wang_Kolar_Drton_2026_Supplementary_Material.pdf>) | Test inversion → ancestry sub/superset (Lemma 3). | Identifiable additive SEM, causal sufficiency. | Projection-to-feature không mới. |
| [Browne](<../../docs/papers/Asymptotically Distribution-Free Methods for the Analysis of Covariance Structures.pdf>), [Berger](<../../docs/papers/Multiparameter Hypothesis Testing and Acceptance Sampling.pdf>) | GLS/minimum-distance và IUT. | Kỹ thuật thống kê tổng quát. | Full-Σ/IUT không là mechanism mới. |
| [Chang–Guo–Malinsky](<../../docs/papers/Post-selection Inference for Causal Effects After Causal Discovery.pdf>) | Resampling/screening graph cho effect CI. | Chủ yếu PC/causal sufficiency; target effect. | Adaptation sang feature là baseline cần chứng minh. |

**Defensible gap claim [Suy luận]:** chưa thấy trong các nguồn đã đọc một thủ tục **vừa** giữ error control cho ancestral assertions trong MAG latent từ CI vector **vừa** có power đáng dùng ở n hữu hạn. Vế power chưa có bằng chứng.

## Reproducible failure

- **Observed symptom:** [Theo toy repo] score D(f) gốc không calibrated; Σ Fisher-z suy biến; ước lượng Σ nhiễu có FAR cao.
- **Specific conditions:** cùng mẫu cho nhiều CI tests, Q gần trùng; n vừa, K tương đối lớn.
- **Suspected mechanism:** tương quan và rank thấp làm inverse covariance/naive threshold sai; projection đúng mức có thể quá bảo thủ.
- **Evidence:** [contract](../aprime_review_2026-11-04/A1_mathematical_contract_v2.md), [toy](../aprime_review_2026-11-04/A1_toy_results.md).
- **Strongest remedy:** valid Bonferroni IUT; confidence-set projection WKD trong setting khác; graph resampling Chang chuyển thể nếu hợp lệ.
- **Smallest reproduction:** toy `K=2–6` với alternative biết truth; R1 vs Bonferroni cùng α.

## New scientific insight & method

- **Insight [Giả thuyết]:** tương quan CI chỉ đáng dùng nếu hình học vùng phủ định feature cho thêm power sau khi rank và mức lỗi đã được xử lý đúng.
- **Mechanism:** một joint confidence ellipsoid rank-aware; chiếu lên hợp vùng MAG phủ định feature; assert chỉ khi mọi mô hình phủ định bị loại.
- **Why not routine:** hiện **chưa chứng minh được** khác biệt cơ chế đủ mạnh; projection/GLS đã có. Nghiên cứu chỉ sống nếu power/feasibility cho latent feature là capability mới có giá trị.
- **Prediction:** một số regime correlated queries trong SCM thực sẽ cho tỷ lệ certified true features cao hơn IUT ở cùng family-wise error.
- **Boundary:** weak effects, Q adaptive cùng mẫu, Σ̂ không ổn, high K hoặc M thiếu truth.
- **Blocker RG1 sơ bộ:** `RG1_numeric_run_log.txt` mới xuất hiện trong workspace báo seminorm `Σ⁺` có thể cho khoảng cách 0 trên nhiều CI-pattern DAG dù vi phạm rõ; chưa có independent review hoặc kết quả feature-level. Cần loại blindness bằng một metric hợp lệ, hoặc dừng formulation này.

## Required evidence

- **Theory:** joint CLT; seminorm/rank; estimated Σ; η_n pointwise vs η fixed uniform; monotonicity/profile nếu R2 đi kèm.
- **Baselines:** Bonferroni IUT; Chang-style resampling cùng target sau proof; diag/covariance-shuffled control; ACI/BSC-D descriptive khác semantics.
- **Synthetic:** latent Gaussian SCM `p=4–5`, n=500/2000/5000; graph seeds độc lập, Q cố định.
- **Public:** Causal Chambers hoặc causalAssembly sau latent projection đã kiểm; chưa tải/pin.
- **Real truth caveat:** Sachs chỉ plausibility/interventional consistency, không full graph truth.
- **Metrics/control:** family-wise false certification, power trên true Q-identifiable features, per-SCM paired CI, CI/QP/runtime/RSS, Q-closure ablation, Σ̂ noise, η misspecification.

## Minimal falsification pilot

- **Cheap decisive test:** RG1 proof **và seminorm-blindness audit**, chỉ sau đó RG2 toy power vs Bonferroni.
- **Positive signal:** validity giữ α và power gain đáng kể ở một regime SCM có prevalence đo được.
- **No-go:** không vượt valid baseline hoặc gain chỉ do query ngoài Q; RG1 không đóng.
- **Resource:** CPU nhỏ trước RG4; chưa triển khai MAG enumeration/full framework.

## Research outcomes

- **Minimum:** characterization trung thực về lúc nào certification có ích, cùng prototype và matched evaluation.
- **Strong:** phương pháp latent-MAG feature certification có power/feasibility và diagnostic rõ.
- **Optional:** mixed/nonparametric arm chỉ khi joint CLT/Σ̂ đứng vững.
- **Publication fit:** Q1 chuyên ngành chỉ là khả năng có điều kiện; top ML cần mechanism/evidence rộng hơn.

## Decision

**Conditional primary để falsify**, chưa Go xây method. RG2 là kill test.
