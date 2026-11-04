# 01 — Research Philosophy, Goals & Quality Bar

## Research objective

Identify and investigate scientifically significant, well-defined and insufficiently addressed problems in causal discovery. Develop a **principled and genuinely novel** algorithm, model, inference mechanism, learning approach or integrated framework, motivated by an explicit scientific insight. Validate its claimed benefits with appropriate theory, fair SOTA comparisons, reproducible benchmarks, ablations, robustness and failure analysis.

Aim for a substantial methodological contribution suitable for a reputable Q1 journal; consider ICML or NeurIPS only if the contribution's originality, significance and relevance support that ambition. This is a research quality target, not a forecast or guarantee.

## Preferred research chain

1. **Meaningful problem:** an important limitation in scientific understanding or existing methods.
2. **Reproducible failure mode:** credible evidence of when/how existing methods fail.
3. **New insight:** an explanation, observation or hypothesis about the failure's mechanism.
4. **Principled method:** an identifiable, nontrivial central mechanism derived from that insight.
5. **Scientific validation:** theory at the level required by claims; strong matched baselines, robustness, ablations and statistical controls.
6. **Transferable knowledge:** why, when and under which assumptions the new method is useful; where it fails.

The end goal is **not** merely “make X faster or improve accuracy by Y%.” It is to advance understanding or introduce a generalizable capability.

## Avoid two extremes

**Excessive theoretical abstraction:** Do not default to proving broad MAG/PAG characterization, universal completeness, polynomial-delay enumeration or fundamental equivalence theorems requiring a long uncertain research program. Such work may be valuable but is not the default path unless it directly enables the method or is independently compelling and feasible.

**Incremental engineering:** Do not present standard caching, search heuristics, hyperparameter tuning, replacing a power set, straightforward module combinations or dataset-specific SOTA gains as sufficient novelty. Useful engineering may be part of the method; it is not automatically the central scientific contribution.

## Evidence standard

| Claim type | Appropriate support |
|---|---|
| Correctness / soundness | Explicit assumptions and rigorous proof or justified formal derivation |
| Efficiency | Honest complexity and runtime/CPU/memory accounting on matched tasks |
| Statistical robustness | Controlled perturbations, repeated trials, uncertainty estimates |
| Causal validity | Correct causal assumptions, output semantics and appropriate ground truth |
| Calibration / confidence | Valid targets, calibration metrics and held-out checks |
| Generalization | Multiple meaningful conditions, transfer tests and failure cases |
| Scientific novelty | Detailed comparison with closest, strongest prior work |

A theorem does not need to be foundational to be useful. A strong systematic empirical finding can itself be a contribution, provided the experiment reveals a substantive scientific insight.

## Venue awareness

Assess **originality, significance, soundness, technical depth, empirical credibility, generality, clarity and venue fit**. Q1 varies by indexing system, year and discipline. UAI/AISTATS may be excellent specialized fits; they are not assumed easier. Never give invented acceptance percentages or claim publication readiness from a proposal alone.

## Research survivability

For each candidate define three outcomes:

- **Minimum complete contribution:** independently useful insight/method with rigorous evidence, not just a working implementation.
- **Strong contribution:** substantial novelty, validated mechanism, strong results against closest baselines.
- **Breakthrough extension:** materially broader capability or guarantee; optional and never assumed.

Choose problems with early falsification opportunities and feasible minimum outcomes.
