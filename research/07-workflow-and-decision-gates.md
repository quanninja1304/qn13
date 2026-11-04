# 07 — Research Workflow & Decision Gates

## Stage 1 — Paper-driven landscape

Analyze ~15–25 closely related primary papers, including strongest adjacent-methodology prior art. Capture assumptions, contribution, evidence, benchmarks and limitations. Write a claim-vs-prior-work matrix.

**Gate 1:** Can at least one meaningful, citation-supported candidate gap be stated with explicit uncertainty? If not, continue literature search or report no viable gap.

## Stage 2 — Reproducible failures

Identify 2–3 candidate failures and the cheapest protocol to reproduce each. Control alternative explanations (e.g., test choice, sample size, dataset artifact, graph semantics, implementation).

**Gate 2:** Is the failure real and consequential beyond a contrived example? Has the best existing remedy been tested or carefully accounted for?

## Stage 3 — Mechanism-oriented ideation

Write a new hypothesis for each credible failure using the format in `05-method-and-contribution.md`. Compare closest prior work, simple baselines and technical prerequisites. Shortlist 3–5 distinct research directions.

**Gate 3:** Is a central insight/mechanism identifiable and potentially novel, rather than a routine combination or hyperparameter fix?

## Stage 4 — Minimal falsification pilot

When execution is possible: reproduce a matching baseline; implement/test the **smallest** novel component; measure whether the failure and mechanism behave as predicted. Preserve raw evidence and failed tests. If no compute/data/source is available, **design the pilot**, label it not run, and do not invent results.

**Gate 4:** Does the hypothesized mechanism show an independent, repeatable benefit or reveal an important new limitation? If it fails, stop/pivot or revise the hypothesis, not just stack extra modules.

## Stage 5 — Publication-oriented design

Only after Gates 1–4: propose full model/framework, necessary theory, baseline suite, public benchmarks, ablations, robustness, real-world evaluation and reproducibility plan.

**Gate 5:** Can the paper's central contribution survive an adversarial review for significance, novelty, soundness, mechanism evidence and venue fit?

## Suggested first 4–6 weeks (not work already done)

| Period | Priority | Required artifact |
|---|---|---|
| Week 1 | Scope and primary-source landscape | 15–25-paper matrix, 3–5 tentative gaps |
| Week 2 | Critically investigate strongest gaps and reproduce key failures where feasible | 2–3 failure-mode dossiers, baseline definitions |
| Week 3 | Novelty and mechanism audit; simplest falsification pilots | Topic cards, pilot protocols, first evidence if run |
| Week 4 | Compare strongest controls/baselines; counterexamples | Evidence table, failure analysis, decision checkpoint |
| Weeks 5–6 | Expand only a surviving candidate; design robust benchmark | 4–6-week decision memo, paper concept and experiment plan |

The schedule is provisional; proof-heavy or inaccessible datasets can delay results. Do not turn it into a promised completion date.

## Go / no-go policy

**Go** if the gap is credible; central mechanism is differentiated; there is measurable relevance; correct evaluation is available; and pilot/strong baseline evidence or solid preliminary theory justifies investment.

**Conditional** if a decisive piece of evidence remains missing: specify one test to resolve it, not a sprawling roadmap.

**No-go** if strong prior work already resolves the task, evidence is only artificial, evaluation cannot be conducted, or the mechanism is equivalent to standard engineering optimizations.

Avoid sunk-cost bias toward past dcFCI pruning/D1–D4 work. End with a concrete decision, including uncertainties and remaining falsification tests.
