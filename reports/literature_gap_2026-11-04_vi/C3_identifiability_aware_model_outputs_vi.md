# Topic card C3 — Identifiability-aware selective outputs cho causal foundation models

> Status: **Exploratory hypothesis**, chưa reproduction, chưa cơ chế mới xác lập. Ngày 04/11/2026.

## One-sentence research question

Khi một mô hình causal discovery pretrained trên synthetic SCM đưa directed-edge/latent scores cho dữ liệu observational thực, có thể phân biệt và báo cáo phần quan hệ tổ tiên được hỗ trợ bởi CI/MAG evidence với phần chỉ phụ thuộc vào prior học từ simulation, rồi abstain khi shift làm prediction không đáng tin không?

## Problem & significance

AI/ML có xu hướng amortized/foundation causal discovery; người dùng có thể đọc edge probability như độ chắc nhân quả. Dưới Markov equivalence, nhiều hướng cạnh không được xác định bằng CI; dưới distribution shift, synthetic prior có thể lệch ứng dụng. Đây là **deployment concern [Suy luận]**, chưa có failure reproduction trong repo.

## Closest prior art & gap

| Source | Contribution | Threat/limitation | Consequence |
|---|---|---|---|
| [FoundCause 2026, preprint](https://arxiv.org/html/2606.17516v1) | Latent-aware amortized discovery, missingness tests, temperature calibration/thresholding. | Main metrics edge-F1/AUROC/SHD; “coverage”=completion. | Không claim paper bỏ qua missingness; cần kiểm decision-level claims trực tiếp. |
| [CDFM 2026, preprint](https://arxiv.org/html/2607.11508v1) | Zero-shot synthetic pretraining, threshold calibrator trên synthetic set. | Synthetic calibration không là real-OOD guarantee. | Calibration wrapper chung không mới. |
| [Reuter et al., ICML 2026](https://proceedings.mlr.press/v306/reuter26a.html) | CFM dùng partial graph/ancestral knowledge. | Cơ chế conditional CFM đã có. | Không claim “partial ancestry + foundation model” là mới. |
| [Wang–Kolar–Drton](<../../docs/papers/Confidence Sets for Causal Orderings.pdf>) | Confidence set có ancestry sub/superset. | Assumptions identifiable/sufficient. | Selective output/test inversion đã có trong setting khác. |

**Gap [Giả thuyết]:** decision-level false ancestry assertion/risk-coverage dưới synthetic-to-real shift chưa được định nghĩa/đo nhất quán trong các nguồn đã audit. Không chứng minh field trống.

## Reproducible failure

- **Observed symptom:** chưa đo; paper FoundCause nêu dimension extrapolation làm F1 định hướng giảm, nhưng đó chưa là failure calibration.
- **Conditions:** latent, observational equivalence, mechanism shift, missingness, imperfect graph labels.
- **Mechanism hypothesis:** probability của edge trực tiếp từ synthetic prior bị đọc như xác suất một causal feature identifiable trong real population.
- **Evidence:** nguồn trên; [Smoke and Mirrors 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2e098001625a8b8f22bf6c1aef09c4e5-Abstract-Conference.html) cho metric mismatch ở **task effect estimation khác**.
- **Strongest remedy:** output PAG/invariant features, holdout CI checks, synthetic calibration, WKD/R1 certificate trong assumptions đúng.
- **Smallest reproduction:** frozen FoundCause/CDFM trên simulation matched vs shifted, cùng feature truth, so raw score với simple holdout filter.

## New scientific insight & method

- **Insight [Giả thuyết]:** uncertainty của model có ít nhất hai nguồn có semantics khác nhau: statistical evidence trong dataset và prior do synthetic training.
- **Mechanism đề xuất:** assumption-indexed claim report ghi rõ prediction từ model, CI/MAG-invariant support, và abstention khi hai nguồn mâu thuẫn.
- **Novelty risk:** có thể chỉ là R1/screening ghép với model. Chỉ theo tiếp nếu một witness/diagnostic mới phân biệt đúng source-of-confidence và thắng simple filter.
- **Prediction:** selective output giảm false causal assertions tại matched retained-feature rate dưới shift.
- **Boundary:** CI test yếu/invalid, latent functional asymmetry đúng nhưng CI không nhận dạng, không có public truth.

## Required evidence

- **Theory:** semantics của feature và assumptions của model/CI; nếu claim coverage phải có sample split hoặc valid selective theory.
- **Baselines:** frozen FoundCause; frozen CDFM; temperature/threshold trên held-out synthetic; simple holdout CI/PAG filter; R1 ở Gaussian stratum.
- **Synthetic:** train-prior matched vs mechanism/noise/latent/missingness shift; không retrain test.
- **Public:** Causal Chambers physical validation, CausalBench downstream intervention consistency khi target phù hợp.
- **Real caveat:** không coi published reference DAG là truth đầy đủ.
- **Metrics:** false assertion vs retained-feature rate, expected set size, calibration plots với independent units, runtime/memory, domain-stratified results.

## Minimal falsification pilot

- **Cheap test:** first verify executable frozen checkpoints and exact output; evaluate simple filter on small held-out SCMs.
- **Positive:** reproducible decision-level failure not fixed by simple calibration/filter, with specific mechanism evidence.
- **No-go:** no failure, no clean labels, or method = off-the-shelf wrapper.
- **Resources:** may require model download/GPU; do not undertake expensive compute before scoped pilot plan.

## Research outcomes

- **Minimum:** rigorous negative/positive diagnostic of decision-level uncertainty if reproducible and transferable.
- **Strong:** new selective mechanism with matched evidence across shifts and real physical checks.
- **Optional:** intervention-efficient acquisition to resolve abstained features, only with extra data.
- **Publication fit:** could be ML-relevant if mechanism and benchmarks strong; currently speculative.

## Decision

**Exploratory only**; no commitment.
