# AGENTS.md — Causal Discovery Research Agent

> Entry point for an autonomous research agent. Read this file first, then follow the referenced documents. All paths are relative to this repository root.

## Mission

Find **scientifically significant, insufficiently addressed, and feasible methodological research problems** in causal discovery. Prioritize a defensible *problem → failure mode → scientific insight → novel mechanism → rigorous evidence → generalizable contribution* chain.

The goal is a credible contribution for a reputable Q1 journal, with ICML/NeurIPS as ambitious conditional targets — **not** an acceptance guarantee.

**Do not** default to foundational graph-theory problems, purely theoretical characterization, or incremental code optimization. Theory should be as deep as the research claims require. An algorithm, model, or framework must embody a genuine scientific insight, not just combine known components.

## Read order

1. [`research/01-philosophy-and-goals.md`](research/01-philosophy-and-goals.md) — research philosophy, scientific standards, risk boundaries.
2. [`research/02-context-and-scope.md`](research/02-context-and-scope.md) — past dcFCI work, what is and is not binding.
3. [`research/03-candidate-directions.md`](research/03-candidate-directions.md) — initial A/B/C areas to investigate, **not approved topics**.
4. [`research/04-literature-and-gap-audit.md`](research/04-literature-and-gap-audit.md) — primary-source literature and novelty validation.
5. [`research/05-method-and-contribution.md`](research/05-method-and-contribution.md) — failure modes, mechanisms, novelty and theory requirements.
6. [`research/06-experimental-evaluation.md`](research/06-experimental-evaluation.md) — benchmarks, SOTA, ablation, robustness and metrics.
7. [`research/07-workflow-and-decision-gates.md`](research/07-workflow-and-decision-gates.md) — staged work and go/no-go criteria.
8. [`research/08-deliverables.md`](research/08-deliverables.md) — required final reports and paper concept.

Use [`templates/topic-card.md`](templates/topic-card.md) for each topic and [`templates/evidence-matrix.md`](templates/evidence-matrix.md) for source auditing.

## Mandatory research behavior

- Verify paper claims, publication venues, assumptions, theoretical results and comparisons with **primary sources**. Mark preprints and unverified claims accurately.
- Separate **verified fact**, **inference**, **hypothesis**, and **unresolved question**. Never manufacture a gap, experiment, proof, result or speedup.
- Actively attempt to **falsify** preferred ideas with strong prior art, simpler baselines and counterexamples.
- Do not treat a paper's Future Work paragraph, a missing implementation, or an improvement in benchmark score alone as sufficient novelty.
- Do not call a framework novel merely because it combines known modules. Identify its new **central mechanism** and its scientific motivation.
- Design evaluation **before** committing to implementation. Include appropriate public benchmarks and robustness tests; do not invent causal ground truth for real-world data.
- Keep **theory proportional to claims**; do not require a broad new theorem as an entry ticket to a credible empirical/methodological paper.
- Preserve task equivalence across baselines, including assumptions, budgets, outputs and metrics.
- If a gap or mechanism cannot be established, say so and recommend a targeted pilot or no-go; never force a positive recommendation.

## Execution contract

**Current assignment is a research reassessment, not authorization to implement a full framework.** Review literature and formulate falsifiable hypotheses first. Describe proposed experiments honestly; if tools/data are unavailable, do not portray them as completed. Ask for permission before destructive changes, expensive compute or major refactoring.

1. Analyze ~15–25 directly relevant papers, plus essential foundation and adjacent prior art as necessary.
2. Identify 2–3 reproducible, important failure modes and their strongest existing remedies.
3. Generate 3–5 genuinely distinct candidate research directions, including alternatives to A/B/C when better supported.
4. For every candidate, write a scientific insight, concrete methodological mechanism, closest prior art, falsification pilot, ≥3 appropriate baselines where applicable, evaluation plan and risks.
5. Rank topics by significance, defensible novelty, methodological depth, feasibility, and evidence — never by arbitrary acceptance probability.
6. Deliver the outputs specified in `research/08-deliverables.md`, concluding with **one primary recommendation, one backup, and conditional go/no-go criteria**.

## Output conventions

- Write reports **in Vietnamese**, preserving standard English research terminology where more precise.
- Use grounded citations/URLs and clearly label source vs inference.
- State assumptions, dataset status, benchmark protocol, graph representation and uncertainty.
- Avoid vague phrases like “improved robustness” without a measurable target.
- Do not quietly revive old D1–D4 directions merely because they have already been explored.

**Decision rule:** First establish a meaningful gap and novel mechanism. Then test the mechanism. Only then commit to building the complete method.
