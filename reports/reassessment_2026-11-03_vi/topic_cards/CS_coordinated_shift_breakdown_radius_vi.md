# Research Topic Card — C-S: Breakdown radius của confounding declarations trước coordinated mechanism shifts

> Status: **Hypothesis**; gap **[Unresolved]** (chưa đọc S7/S8). Pilot **chưa chạy**. Chi tiết gốc: `../source_audit_heterogeneity.md` §4.
> Owner/date: reassessment 03-11-2026.

## One-sentence research question

Với known environment labels và exogenous latent roots, có thể trả về các confounding declarations vẫn đúng khi tối đa một tỉ lệ η môi trường chứa coordinated observed-mechanism changes không? Câu hỏi đi kèm: lượng contamination tối thiểu đủ để giải thích một declaration (breakdown radius) có phải là một estimand identifiable và hữu ích không?

## Problem & significance

CoCo (Mameche et al., AISTATS 2024) diễn giải sự đồng biến của mechanism-shift partitions là bằng chứng của latent confounding, dưới giả định shifts độc lập/sparse. Trong thực nghiệm sinh học và kỹ thuật, các can thiệp thường **được điều phối** (một treatment ảnh hưởng nhiều module). Khi đó có nguy cơ khẳng định sai confounding.

## Closest prior art & gap

| Source | Contribution | Limitation | Consequence |
|---|---|---|---|
| H5 CoCo, AISTATS 2024 | Confounder sets từ partition dependence | Independent/sparse shifts | Đây là target gốc. |
| H1 JCI, JMLR 2020 | Context variables trong FCI | Không đo sensitivity | Baseline cấu trúc. |
| S7 Reddy–Balasubramanian 2024 (preprint) | Đo confounding qua mechanism shifts | Chưa đọc | Có thể chặn gap. |
| S8 StruBI 2026 (chưa xác minh primary) | Confounding + selection | Chưa đọc | Có thể chặn gap. |
| S9 Robust-FILM/DRO/anchor | Robust trước outlier environments | Prediction/effect | Baseline family "trimming". |

**Gap ([Unresolved]):** chưa có hit trực tiếp nào về sensitivity của confounding declarations trước coordinated shifts.

## Reproducible failure

- **Symptom ([Hypothesis]):** CoCo báo confounding giả khi hai observed mechanisms đổi đồng thời mà không có latent.
- **Smallest reproduction (chưa chạy):** 3–6 nút; arm (a) latent thay đổi, arm (b) không latent nhưng có coordinated interventions; dùng oracle partitions trước.
- **Strongest remedy:** JCI-FCI với đầy đủ context/design variables; leave-k-environments-out CoCo.

## New scientific insight & method

- **Insight:** sức mạnh của một declaration = contamination tối thiểu đủ để giải thích nó mà không cần latent cause.
- **Mechanism:** tìm contamination mask nhỏ nhất trên các environments (exhaustive khi E ≤ 8) → breakdown radius / abstention tại một η định trước.
- **Why not routine:** chỉ là cơ chế mới nếu radius phân biệt được design uncertainty với latent evidence **tốt hơn** trimming đơn giản.
- **Failure boundary:** coordinated shifts có thể không phân biệt được về mặt quan sát → radius = 0 khắp nơi.

## Required evidence

- **Proof obligations:** identifiability dưới contamination model; phản ví dụ indistinguishable; validity khi admissible set chứa truth.
- **Baselines (≥3):** CoCo; trimmed/leave-k-out CoCo; bootstrap consensus; JCI-FCI trên shared ancestry subtask; UT-LVCE trong stratum linear-Gaussian.
- **Data:** CoCo generator; Causal Chamber (ancestry validation, không có shared-latent truth); Sachs chỉ để kiểm tra consistency.
- **Metrics:** declaration FPR, recall tại fixed risk, risk–coverage, phân phối radius.

## Minimal falsification pilot (chưa chạy)

- **Cheap decisive test:** phân tích identifiability ở oracle level + kiểm tra radius có trùng trimming hay không.
- **Positive:** declarations hữu ích còn sống ở η > 0 trong positive arm; abstain trong coordinated arm; trimming không làm được điều tương tự.
- **No-go:** radius ≈ 0 kể cả ở các case thuận lợi; trùng trimming; hoặc S7/S8 đã xử lý.

## Research outcomes

- **Minimum:** phân tích failure boundary định lượng + một sensitivity target identifiable.
- **Strong:** sensitivity method vượt matched trimming.
- **Ambitious:** chọn intervention batches để tăng radius.
- **Fit:** UAI/CLeaR/AISTATS; niche hơn A′.

## Decision

**Conditional, ưu tiên thứ ba.** Gap chưa được kiểm tra trước S7/S8, và rủi ro identifiability cao.
