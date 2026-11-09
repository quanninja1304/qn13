# Topic card C2 — Proof-specific selection transport khi dữ liệu thiếu

> Status: **Hypothesis / backup**, chưa pilot. Ngày 04/11/2026. Bắt buộc so với Strobl Algorithm 1, không so chỉ với listwise thô.

## One-sentence research question

Trong FCI/RFCI dưới điều kiện missingness của Strobl, có thể chứng minh một orientation proof từ các CI premises trên selection populations khác nhau bằng cách recheck **ít nhất nhưng đủ** các premise, nhằm giữ đúng target và tăng effective sample size so với test-wise FCI/RFCI hiện có không?

## Problem & significance

Clinical/cohort data thường thiếu không ngẫu nhiên; complete-case listwise bỏ nhiều mẫu, còn test-wise CI có thể thuộc các populations khác nhau. Mục tiêu là endpoint/ancestry assertions đúng với target population, không chỉ số CI tests ít hơn.

## Closest prior art & gap

| Source | Contribution | Limitation/threat | Consequence |
|---|---|---|---|
| [Strobl et al. 2018](https://arxiv.org/html/1705.09031) | Test-wise FCI/RFCI + listwise confirmation; Lemma 1–2, Algorithm 1. | Đã xử lý một phần lớn failure; thêm heuristic chỉ ~1.05% sample/CI ở cohort được báo cáo. | Phải tìm lemma/benefit **beyond M1**. |
| [Tu et al. 2019](https://proceedings.mlr.press/v89/tu19a.html) | MVPC với correction dưới m-graphs. | PC/causal sufficiency. | Không claim selective correction là mới. |
| [Witte et al. 2022](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.9535) | Recoverability conditions; so test-wise/MI/hybrid trong cohort. | Mixed data: không một method thắng mọi setting. | Kiểm lemma đề xuất với điều kiện recoverability đã biết. |
| [Gain–Shpitser 2018](https://proceedings.mlr.press/v72/gain18a.html) | Structure learning với missingness/selection. | Khung khác nhưng relevant. | Tránh diễn giải “missingness structure learning” là gap mới. |

**Gap claim [Giả thuyết]:** M1 có thể recheck nhiều hơn mức cần thiết cho **một orientation proof cụ thể**. Chưa chứng minh rằng recheck tối thiểu khác M1 hay tạo sample gain đáng kể.

## Reproducible failure

- **Symptom:** CI premise từ selection populations khác nhau có thể làm orientation oracle sai; listwise confirm mất mẫu.
- **Conditions:** MNAR/MAR theo assumptions, nhiều biến với missingness pattern khác nhau.
- **Mechanism:** một proof dùng các premise không cùng target; hoặc M1 recheck CI không tham gia proof.
- **Evidence:** Strobl §4–§7 và repo [T4 card cũ](../reassessment_2026-11-03_vi/topic_cards/T4_selection_indexed_premises_missingness_vi.md).
- **Strongest remedy:** M1 Algorithm 1; MVPC/MI ở stratum phù hợp.
- **Smallest reproduction:** oracle R0/R4 motif, liệt kê premise, selection indicators, so full M1.

## New scientific insight & method

- **Insight [Giả thuyết]:** một orientation chỉ cần các CI premises trong **proof witness** được vận chuyển nhất quán, không nhất thiết toàn bộ CI history.
- **Mechanism:** gắn provenance/selection set vào mỗi premise; proof search chọn witness có thể transport; nếu thiếu, recheck trên intersection hoặc abstain.
- **Why not routine:** chỉ có contribution nếu lemma mới cho phép giữ assertion mà M1 bỏ hoặc giảm recheck **mà không đổi target**. Logging/caching đơn thuần không đủ.
- **Prediction:** trong missingness tập trung, effective-n cho certified orientations tăng so với M1, error không tăng.
- **Boundary:** missingness graph không biết, self-masking, no transport witness, endpoint không identifiable.

## Required evidence

- **Theory:** lemma transport R0/R4; oracle equivalence to M1 target; counterexample cho naive composition.
- **Baselines:** M1 test-wise confirmation; Witte test-wise/MI hybrid; listwise FCI; naive test-wise FCI negative control; MVPC causally sufficient stratum.
- **Synthetic:** latent DAG + missingness indicator graph, p=5–6, varying 10–50% missingness.
- **Public:** generated missingness on bnlearn/Causal Chambers = adaptation, label clearly.
- **Real:** IDEFICS/cohort only if access; no full graph truth claim.
- **Metrics:** false endpoint assertions vs target PAG, effective-n/orientation, abstention, CI count/runtime; paired graph seeds; missingness mechanisms and MI model misspecification.

## Minimal falsification pilot

- **Cheap test:** paper proof/counterexample R0 first, then R4; no full framework.
- **Positive:** a provably sound witness not reducible to M1, with meaningful n-gain in small simulation.
- **No-go:** proof collapses to M1/standard augmented m-separation, or gain negligible vs M1.
- **Resources:** CPU small, oracle enumeration; no cohort processing yet.

## Research outcomes

- **Minimum:** theorem/negative characterization + reproducible sample-efficiency comparison, if scientifically nontrivial.
- **Strong:** sound proof-indexed FCI with measurable improvement over M1.
- **Optional:** learned missingness graph with honest uncertainty.
- **Publication fit:** conditional Q1 methods/epidemiology; no guarantee.

## Decision

**Conditional backup**; first solve oracle proof question.
