# Research Topic Card — T4: Premise CI gắn selection set — xác nhận cục bộ theo từng orientation proof dưới missing data

> Status: **Hypothesis**. Failure ở oracle level đã **source-verified** (M1 §10.1 manuscript); cơ chế mới chưa có. Pilot **chưa chạy**.
> Owner/date: reassessment 03-11-2026.

## One-sentence research question

Trong FCI/RFCI với dữ liệu thiếu không ngẫu nhiên (latent, acyclic, missingness indicators không có hậu duệ substantive như M1), có tồn tại một **điều kiện đủ cục bộ, theo từng orientation proof**, cho phép kết hợp các CI premises đo trên các selection populations khác nhau mà vẫn giữ đúng target của M1, đồng thời dùng nhiều mẫu hơn so với xác nhận listwise toàn cục không?

## Problem & significance

Dữ liệu y sinh/cohort gần như luôn thiếu. Test-wise deletion giữ được nhiều mẫu, nhưng mỗi CI lại thuộc một selection population khác nhau. [Verified, M1 §10.1] Ghép trực tiếp các premise này có thể định hướng sai **ngay cả với oracle**. Remedy của M1 phải xác nhận lại ở listwise regime, và cái giá là mất mẫu khi missingness lan rộng.

## Closest prior art & gap

| Source | Closest contribution | Limitation | Consequence |
|---|---|---|---|
| M1 Strobl–Visweswaran–Spirtes, IJDSA 2018 ([DOI](https://doi.org/10.1007/s41060-017-0094-6)) | Test-wise + listwise re-check; Theorem 1 oracle | Rule toàn cục theo từng CI | Đây là baseline và remedy mạnh nhất. |
| M2 MVPC, Tu et al., AISTATS 2019 ([PMLR](https://proceedings.mlr.press/v89/tu19a.html)) | Sửa chọn lọc các CI có thể sinh cạnh giả | Causal sufficiency | "Selective correction" không mới. |
| M3 Witte–Foraita–Didelez, Stat Med 2022 | Testwise vs MI, điều kiện recoverability | Không có phương pháp thắng đều | Chặn mọi claim về recoverability tổng quát. |
| M4 PAIR-CI, arXiv 2605.04838 (preprint) | Calibrated CI sau imputation | MNAR bị giới hạn | Đối chứng ở tầng CI test. |
| M5 Versteeg–Mooij–Zhang, CLeaR 2022 | Local Y-structure claims dưới selection | Local-only | "Local certificate under selection" không mới. |

**Defensible gap claim ([Hypothesis]):** chưa thấy một rule **theo từng proof** (collider/discriminating-path) chỉ ra những premise nào cần chung một selection population, vượt khỏi rule theo từng CI của M1. Nếu rule đó trùng m-separation chuẩn trên augmented graph với missingness graph đã biết, thì gap không tồn tại.

## Reproducible failure

- **Symptom:** [Verified] orientation sai ở oracle khi ghép premise test-wise (M1 §10.1). [Inference] Remedy listwise làm mất mẫu.
- **Conditions:** missingness phụ thuộc biến quan sát/latent, tỉ lệ thiếu cao trên nhiều biến.
- **Suspected mechanism:** premise A đúng trên population S_A, premise B đúng trên S_B; kết luận chỉ hợp lệ trên S_A ∩ S_B nếu không có transport.
- **Strongest remedy:** M1 Algorithm 1; MVPC trong causally sufficient stratum; MI + PC/FCI.
- **Smallest reproduction:** tái lập ví dụ oracle của M1 §10.1, sau đó dùng finite sample với p=5–6.

## New scientific insight & method

- **Insight ([Hypothesis]):** cái cần xác nhận chung không phải từng CI, mà là **tập premise tối thiểu của một orientation proof**. Nhiều proof chỉ cần một xác nhận nhỏ hơn listwise.
- **Mechanism:** gắn với mỗi CI fact selection set R_S của nó; với mỗi orientation rule, tính "selection support" của proof; chỉ xác nhận lại trên S_proof = ∩ selection sets của các premise cần thiết, và **chỉ khi** một điều kiện transport (cần chứng minh) không thỏa; nếu thiếu thông tin thì abstain.
- **Why not routine:** chỉ là cơ chế mới nếu chứng minh được một lemma transport theo proof, mạnh hơn rule theo CI. Nếu không → caching/engineering.
- **Predicted effect:** tăng effective sample size cho các orientation khi missingness tập trung trên một vài biến.
- **Failure boundary:** missingness graph không biết; self-masking; MNAR không identifiable.

## Required evidence

- **Proof obligations:** lemma transport cho R0/R4 (collider, discriminating path) dưới assumptions M1; oracle equivalence với target của M1.
- **Baselines (≥3):** M1 wrapper; naive test-wise FCI (negative control); listwise FCI; MI + FCI; MVPC (chỉ trong stratum causally sufficient).
- **Synthetic:** latent DAG + missingness mechanisms (MCAR/MAR/MNAR không self-masking), tỉ lệ thiếu 10–50%.
- **Public:** bnlearn networks với missingness được tiêm (ghi rõ adaptation); dataset cohort thật chỉ dùng để đánh giá stability (IDEFICS chưa có quyền truy cập).
- **Metrics:** endpoint errors so với reference PAG của target M1; effective sample size cho mỗi orientation; runtime.

## Minimal falsification pilot (chưa chạy)

- **Cheap decisive test:** trên giấy, định nghĩa rule cho R0 và thử chứng minh hoặc tìm phản ví dụ, rồi so sánh với m-separation trên augmented graph.
- **Positive signal:** rule không tầm thường (khác M1, khác m-separation chuẩn) + mô phỏng cho thấy effective-n tăng ≥ một mức định trước mà endpoint error không tăng.
- **No-go:** rule rút về m-separation chuẩn; hoặc lợi ích về mẫu không đáng kể dưới các missingness pattern thực tế.
- **Resource:** chủ yếu là theory; CPU nhỏ.

## Research outcomes

- **Minimum:** lemma + bằng chứng định lượng về lượng mẫu thu lại được.
- **Strong:** missingness-aware FCI với per-proof confirmation và đánh giá công bằng.
- **Ambitious:** kết hợp với missingness graph được học (có uncertainty).
- **Publication fit:** Q1 journal về statistics/epidemiology methods là phù hợp nhất; top ML venue khó.

## Decision

**Conditional (backup).** Failure có thật ở oracle level; kill test thuần lý thuyết và rẻ. Rủi ro chính: rule chỉ là m-separation chuẩn.

## Cập nhật 2026-11-06 (append, không sửa phần trên)

Kill test đã chạy, xem [`T4_kill_test_vi.md`](../../../archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md).

- **Đính chính:** M1 Appendix 10.1 chỉ giải thích vì sao R1 có thể hỏng với heuristic; không có đồ thị phản ví dụ tường minh. Các dòng "[Verified, M1 §10.1]" ở trên cần đọc theo nghĩa này.
- **Quyết định theo card này: NO-GO** cho mục tiêu giữ đúng target với luật cục bộ chỉ dùng CI giữa biến O (có phản ví dụ).
- **Hướng hẹp hơn còn lại:** T4-L, GO có điều kiện, chờ user.
- **Cập nhật sau pilot (2026-11-06):** T4-L cho NO-GO theo luật đã khai báo, chờ user xác nhận đóng. Xem [`T4L_pilot_report_vi.md`](../../../archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md).
- **Đóng 2026-11-07:** user quyết định đóng T4-L. Toàn bộ báo cáo T4 đã chuyển vào `archive/2026-11_t4_selection_indexed/`. Xem X27, X29 trong `RESEARCH_HISTORY_vi.md`.
