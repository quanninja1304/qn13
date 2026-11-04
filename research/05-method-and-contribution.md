# 05 — Scientific Insight, Novel Method & Theory

## Six-question Scientific Contribution Test

Every candidate topic must answer:

1. **Problem:** What scientifically important capability or understanding is missing, and who cares?
2. **Gap:** What exactly remains insufficient under the strongest closest prior work?
3. **Insight:** What new explanation, observation or hypothesis about the failure motivates action?
4. **Mechanism:** Which identifiable methodological idea is genuinely nontrivial relative to prior art and simple baselines?
5. **Evidence:** Which theoretical, empirical and diagnostic results would establish or falsify the main claims?
6. **Transferability:** Under which assumptions, classes of graphs/data and tasks does the insight apply — and where does it fail?

If **Insight** or **Mechanism** is vague, label the item an *engineering/preliminary idea*, not an established scientific proposal.

## Method proposal format

**Observation → hypothesized failure mechanism → conceptual insight → proposed method → prediction → falsification criterion.**

A method may be a new algorithm, inference rule, uncertainty representation, learning objective, search policy, optimization routine or integrated framework. For multi-module systems, identify the scientifically novel **interaction**; “combining GNN + Bayesian + FCI” is not sufficient.

## Adversarial novelty audit

- Name the **closest** competing method (not merely famous SOTA systems).
- Precisely state differences in assumptions, input/output task and core method.
- Ask whether a simple heuristic, cache, ensemble, thresholding or stronger implementation matches the proposed gain.
- Identify exactly what evidence would show the new central mechanism matters (ablation / alternative explanation controls).
- Trace novelty to a new capability or scientific understanding, not architectural complexity.
- Separate **correctness**, **usefulness**, and **originality**: each needs independent support.

## Appropriate technical depth

New foundational theorems are **not mandatory**. Match formal work to claims:

- Soundness/guarantees for proposed inference operations where claimed.
- Statistical consistency/calibration guarantees only under clearly stated conditions.
- Runtime/complexity analysis when efficiency is a key claim.
- Structural or mechanistic explanation of observed performance and failure boundaries.
- Systematic, reproducible empirical finding if that is the actual core scientific contribution.

Do not invent an “Eureka theorem” merely to elevate paper positioning. Conversely, do not call a method principled without spelling out the reasoning that justifies it.

## Research survivability

For each candidate define:

- **Minimum complete publishable-science outcome:** smallest independent new insight + adequate evidence (not a guarantee of journal acceptance).
- **Strong outcome:** substantial method, robust controls, validated mechanism, competitive results.
- **Ambitious extension:** higher generality, new guarantee or broader ability, optional.

Require a cheap **kill test** before major implementation. If strong prior art resolves the core mechanism or the observed failure disappears under matched conditions, pivot/stop rather than expand the framework.
