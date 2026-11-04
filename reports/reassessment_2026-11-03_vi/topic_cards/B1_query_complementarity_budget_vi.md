# Research Topic Card — B′: Query complementarity cho causal-feature decisions dưới ngân sách CI

> Status: **Hypothesis**, **đã bị hạ ưu tiên**. Chi tiết: `../source_audit_budget.md` §§4–5. Pilot **chưa chạy**.
> Owner/date: reassessment 03-11-2026.

## One-sentence research question

Ở fixed CI budget, chọn **bundle** 2–3 query cùng hoàn thành chứng cứ cho một feature có cho số kết luận được chứng thực nhiều hơn so với single-query scheduling và ICD completed-iteration output không?

## Problem & significance

Ngân sách CI bị giới hạn khi n lớn hoặc khi test đắt (kernel). Nhưng phần lớn các cơ chế tổng quát đã có: ICD (NeurIPS 2021), k-PC (NeurIPS 2023), C-PC (UAI 2025), CCPG (ICML 2024), GAS (arXiv 2026), Dseptor (IJCAI 2017).

## Closest prior art & gap

ICD (anytime, sound tại completed iteration); GAS (ancestry-guided, ít query hơn); ABCD (batched active design với submodularity, dùng interventions). **Gap [Hypothesis]:** rollback về completed iteration có thể lãng phí query, và các query có tính bổ sung lẫn nhau. Cả hai điều này đều chưa được chứng minh là đáng kể.

## Reproducible failure

- Mất query đã trả tiền giữa iteration của ICD (chưa đo). Reproduction: 6–10 nút, oracle, ngân sách 10–75%.

## New scientific insight & method

- **Insight:** giá trị của query phụ thuộc vào việc hoàn thành chứng cứ **chung** (complementarity).
- **Mechanism:** chọn bundle theo mức giảm ambiguity của quyết định trên mỗi đơn vị cost, với witness/counter-witness models; chỉ công bố kết luận khi mọi mô hình tương thích đều đồng ý.
- **Why maybe not routine:** nguy cơ cao trùng batched active learning / weighted set cover.

## Required evidence

- **Baselines (≥3):** ICD; random/low-order/cheapest-first; single-query uncertainty-per-cost; closure-aware greedy singleton; GAS trong causally sufficient arm.
- **Metrics:** số feature được chứng thực và đúng theo ngân sách; false assertions; CI count/time.

## Minimal falsification pilot (chưa chạy)

- **Kill:** lợi ích biến mất khi singleton greedy được dùng cùng closure/compute; không có complementarity ngoài toy graphs.

## Research outcomes

- **Minimum:** characterization về khi nào complementarity quan trọng.
- **Fit:** UAI/AISTATS nếu thành công; nguy cơ trượt sang engineering/D3.

## Decision

**No-go cho framework độc lập; Conditional/low** cho một pilot oracle nhỏ, chỉ khi A′ và T4 đều thất bại.
