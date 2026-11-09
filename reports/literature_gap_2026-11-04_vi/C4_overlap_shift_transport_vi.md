# Topic card C4 — Feature transport giữa overlapping cohorts có mechanism shift

> Status: **Exploratory / identifiability unresolved**, chưa pilot. Ngày 04/11/2026.

## One-sentence research question

Khi nhiều cohort chỉ đo các tập biến chồng lấp và không chắc cùng một MAG do selection/mechanism shift, có thể xác định những ancestral/adjacency features nào thật sự transportable trước khi ghép CI evidence, thay vì ép một graph chung không?

## Problem & significance

Multi-cohort biomedical data thường không có tất cả biến cùng được đo và populations khác nhau. Việc ghép CI facts thiếu common target có thể tạo khẳng định giả. Tầm quan trọng thực tiễn cao, nhưng một graph chung có thể hoàn toàn không identifiable từ overlap ít.

## Closest prior art & gap

| Source | Contribution | Assumption/limitation | Threat |
|---|---|---|---|
| [tFCI/tIOD 2025](<../../docs/papers/tFCI & tIOD.pdf>) | Ghép overlapping datasets với tiered knowledge, latent. | Giả định một MAG chung, không selection; paper nêu finite-sample inconsistency trên overlap. | “Multi-cohort FCI” đã có. |
| [JCI, JMLR 2020](https://jmlr.org/papers/v21/17-123.html) | Context variables cho multi-context discovery. | Phụ thuộc JCI assumptions/background knowledge. | “Thêm context vào FCI” đã có. |
| [CD-NOD, JMLR 2020](https://jmlr.org/papers/v21/19-232.html) | Heterogeneous/nonstationary causal discovery. | Assumptions về pseudo-confounders/changing modules. | “Heterogeneity giúp orient edges” đã có. |
| [fedCI-IOD, arXiv 2603.05149](https://arxiv.org/abs/2603.05149) | Federated evidence + overlapping panels với latent. | Shared structure và model/GLM assumptions. | Hạ novelty của đơn thuần pooling/federation. |

**Gap [Giả thuyết]:** có thể thiếu một **feature-level transport witness** khi common-graph assumption không đáng tin. Chưa kiểm forward/backward prior art về data fusion/selection transport đầy đủ.

## Reproducible failure

- **Symptom:** `[Giả thuyết]` ghép two-cohort CI cho một MAG chung tạo false common features khi một mechanism đổi.
- **Conditions:** overlap ít, latent, unknown site-specific selection/intervention.
- **Mechanism:** CI statements ở khác populations không có một m-separation model chung.
- **Evidence:** tIOD tr. 13 nêu common-MAG assumption; repo [heterogeneity audit](../reassessment_2026-11-03_vi/source_audit_heterogeneity.md).
- **Strongest remedy:** JCI, tIOD với common MAG, stratified/per-cohort FCI intersection, ψ-FCI ở soft-intervention setting.
- **Smallest reproduction:** hai cohort oracle, 3–5 observed nodes, một shifted mechanism; tìm graph pairs bất khả phân biệt.

## New scientific insight & method

- **Insight [Giả thuyết]:** từng feature có thể transportable dù toàn graph không chung; chỉ ghép CI evidence khi có witness qua overlap.
- **Mechanism:** chứng nhận feature qua intersection của admissible cohort-specific MAG sets và local invariance/selection witness; abstain nếu witness thiếu.
- **Why not routine:** chỉ mới nếu witness có soundness và cho thêm feature hơn simple per-cohort intersection dưới assumptions rõ; nếu chỉ set intersection thì không có mechanism mới.
- **Prediction:** recover subset đáng kể common features khi common-MAG tIOD sai, giữ false transfer thấp.
- **Boundary:** overlap không đủ, arbitrary shifts indistinguishable, selection unobserved.

## Required evidence

- **Theory:** identifiability/counterexample first; sound witness under explicit shift class.
- **Baselines:** tIOD; JCI-FCI; per-cohort FCI intersection; pooled FCI negative control; fedCI-IOD nếu data type matched.
- **Synthetic:** oracle first then finite sample, cohorts với overlap/missingness/mechanism shift factorial.
- **Public:** Causal Chambers/cross-context data only after measurement subsets and graph truth pinned.
- **Real caveat:** multi-cohort patient data has no full graph truth; evaluate stability or known interventions only.
- **Metrics:** false common-feature rate, recall conditional identifiable, list size, abstention, CI tests/time, paired cohort-generation seeds.

## Minimal falsification pilot

- **Cheap test:** oracle 2-cohort counterexample and simple intersection; identify whether any useful witness exists.
- **Positive:** nonempty sound transportable features beyond simple intersection in a justified shift class.
- **No-go:** witness collapses to JCI/tIOD or output empty under realistic overlap.
- **Resources:** small graph enumeration before data/model implementation.

## Research outcomes

- **Minimum:** reproducible identifiability boundary, only if it changes practice.
- **Strong:** transport-witness method with finite-sample/benchmark evidence.
- **Optional:** federated implementation after central semantics validated.
- **Publication fit:** highly conditional; not yet a recommended topic.

## Decision

**Exploratory/no-go until oracle witness survives**. Do not revive generic multi-environment FCI.
