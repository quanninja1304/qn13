# DAY 3 — Independent Pilot Readiness, Novelty Audit and Decision Memo

## Role and purpose
Act as an independent research advisor, methodology reviewer and reproducibility auditor. **Your job is to decide what research is justified next, not to ensure A′ survives.** This stage should integrate Day 1's mathematical audit and Day 2's toy findings, separate actual results from proposed work, and produce a falsifiable pilot design only if justified.

This is a **planning and evidence-evaluation stage**, not authorization to run confirmatory benchmarks, make claims of calibrated confidence, or publish results.

## Required inputs
Read `AGENTS.md`, research instructions, `00_final_reassessment_vi.md`, source audits, available topic cards, `A1_gap_confirmation_and_proof_sketch_vi.md`, `A1_next_steps_plan_vi.md`, and the new Day 1/Day 2 artifacts. Read the research decision log without rewriting past entries. If Day 1/2 is incomplete, explicitly mark dependent conclusions NOT ASSESSED and write a reduced plan; do not fabricate their outcomes.

## Workstream 1 — Claim and prior-art register
Build a table mapping every intended scientific claim to: precise mathematical/statistical meaning, closest prior work, what those works actually prove/test, hypothesized residual novelty, primary evidence needed, current verification tier, and a minimal falsification test.
Mandatory comparisons where relevant:
- ACI: additive constraint loss and forced-feature optimization; published weighting and inference target;
- BSC-D: bootstrap-dependent CI facts and graph/PAG scoring; distinguish the original method from any **newly proposed BSC-D-to-feature adaptation**;
- Guo–Wu–Yiu: geometry of FCI selection events and causal-effect selective inference, not automatically feature-level inference;
- published feature-confidence/neighborhood methods, including the requested PGM 2014 paper, once available;
- classical constrained GLS, GLR, multivariate testing, covariance-aware scoring, and full-likelihood/BIC alternatives.
For each unavailable full text, say precisely which novelty claim or mathematical step is blocked. Never treat paper titles, abstracts, automated extracts or Future Work paragraphs as proofs of nonexistence of prior work. Any new novelty claim must survive an adversarial “could a known method already do this?” analysis.

## Workstream 2 — Missing references and dependency register
For the five requested sources record: bibliographic identity/DOI, access state (FULL TEXT VERIFIED / PARTIAL / ABSTRACT ONLY / MISSING), reason needed, exact theorem/algorithm/evaluation question, potential impact on A′, and the task that can proceed without it:
1. *Learning Neighborhoods of High Confidence in Constraint-Based Causal Discovery*;
2. Zhang (2008), *On the completeness of orientation rules for causal discovery in the presence of latent confounders and selection bias*;
3. Silvapulle & Sen, *Constrained Statistical Inference* (book);
4. *Multiparameter Hypothesis Testing and Acceptance Sampling*;
5. *Correlations Redux*.
Do not claim a source is a hard blocker without specifying the exact blocked decision. Do not claim to have read an unavailable source.

## Workstream 3 — Define a testable pilot question (not an assumed result)
Make explicit distinctions among:
- feature *ranking/fragility* versus probabilistic confidence;
- fixed threshold error rate, empirical threshold transfer and formal frequentist coverage;
- structural accuracy versus uncertainty quality;
- fixed-query inference versus adaptive query selection;
- Gaussian partial correlations versus generalized/nonparametric CI statistics.
Specify the **target estimand** and the *primary hypothesis* only after considering Day 1/2 evidence. Do not mandate H-cal, any preselected 5% threshold, or a claimed new theorem if they are statistically unsupported. If multiple estimands remain plausible, provide alternatives and state what data/derivation would decide among them.

## Workstream 4 — Comparable baselines and dataset protocol
Produce a baseline contract for each **feasible, same-target** comparator: original ACI; correct diagonal-weight control; bootstrap or stability selection of causal features; relevant dependence-aware model (BSC-D only where task can be matched or via a clearly labeled adaptation); forced-feature Gaussian likelihood/BIC if meaningful, and simple no-correction/covariance controls. Include method provenance, required inputs, output semantics, data type, assumptions, compute/sample/query budgets, tuning and reproduction status. State explicitly when comparisons would be apples-to-oranges; do not demand an arbitrary list of SOTA methods with incompatible outputs.

Build a **benchmark registry**, initially proposed rather than executed: controlled SCMs with known causal graphs/latent projections and fixed Q; a held-out adaptive-Q stress test; public benchmarks for the correct target; real-world data only for appropriately justified plausibility/stability claims. Include p, n, density, latent rate, dependence strength, CI type, heterogeneity, seeds, training/calibration/test split boundaries, graph-truth convention, official provenance and potential confounders. Do not use ground-truth graph for model selection or call best-of-list SHD a deployable output.

## Workstream 5 — Metrics and robustness
For each hypothesis propose at least one interpretable primary metric and adverse control. Possible candidates, **only if defensible**: feature-level selective risk at matched coverage, fixed-threshold false assertion rates with precisely stated reference population, risk–coverage curves, ranking correlations, structural orientation errors, covariance-estimation errors, CI-count/runtime/memory costs. State definitions, denominator, independent experimental unit (SCM vs dataset vs feature), uncertainty intervals and seed pairing. Flag multiple feature correlations and leakage from using the same samples to select Q and score features.

Predefine a rationale for robustness regimes and negative controls. Avoid arbitrary mandatory success thresholds; if proposing go/no-go thresholds, label them project-management choices and provide a rationale. Distinguish exploratory pilot from preregistered confirmatory evaluation; do not claim pre-registration has been locked until committed and approved.

## Workstream 6 — Resource and feasibility assessment
Estimate qualitatively/empirically when supported: effort to reproduce ACI, implement covariance estimation and constrained optimization, enumerate candidate MAGs, build bootstrap/BSC-D adaptations, and evaluate nonparametric statistics. Identify independent reference implementations and expected failure points; quantify only from grounded benchmarks/microbenchmarks. Mark unknown compute requirements instead of guessing. Include data/software licensing where relevant and actual reproducibility needs (seeds, versions, configurations, raw score outputs, failures/timeouts).

## Workstream 7 — Adversarial decision and branching
Evaluate at least four outcomes:
- **GO TO MINIMAL CAUSAL PILOT:** mathematical target valid, toy evidence relevant, residual novelty plausible, and a same-target baseline protocol exists;
- **REFORMULATE:** core issue solvable but research question/score/estimand must change;
- **HOLD FOR SOURCE:** one or more decisive primary references not available; identify bounded work still possible;
- **STOP / PIVOT:** no defensible gap, invalid objective or no meaningful measurable target.
Specify what evidence would reverse the decision. Do not choose GO merely because the schedule reached Day 3. Preserve possibility of investigating T4 or another direction without treating it as automatically novel.

## Deliverables
1. `A1_pilot_readiness.md`: executive verdict; claim/novelty ledger; causal/statistical assumptions; selected or competing estimands; baseline contracts; proposed experiment matrix; metrics/robustness; resource and risk matrix; phase gates; precise next action.
2. `A1_missing_references_register.md`: five-source table with access levels, exact blocked claims, reading priorities and questions for each paper/book.
3. Append-only entry in the decision log: what was examined, source/artifact links, outcome, outstanding evidence, who has/has not approved.
4. `A1_review_handoff.md`: concise one-page handoff to a new independent agent stating what is proved, contradicted, merely observed, proposed, and unverified. No paper-ready abstract unless the evidence warrants it.

**Write in Vietnamese, using English technical terms. Cite exact local artifact paths and primary-source sections where possible. Clearly distinguish source facts, independent derivations, hypotheses and not-yet-run experiments. Do not produce fictional benchmarks or optimistic publication predictions.**
