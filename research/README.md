# Research protocol — Causal Discovery Research Agent

This folder is a **modular replacement for a single, long research prompt**. It instructs an AI research agent to reassess research topics before full implementation, with a focus on **scientifically motivated methodological innovation** and rigorous empirical validation.

## Start here

- Agent with repository instruction-file support: point it to **[`AGENTS.md`](../AGENTS.md)** or open the repository root.
- Agent without such support: send `AGENTS.md` as the first message, then supply the referenced Markdown files or the whole folder as context.
- **Read [`RESEARCH_HISTORY_vi.md`](../RESEARCH_HISTORY_vi.md) first** so you do not reopen a direction that was already rejected.
- Supply previous dcFCI formulation/review PDFs or Markdown notes when available. They are background, **not binding decisions**.

## Files

| File | Responsibility |
|---|---|
| `../AGENTS.md` | Compact role, mission, read order and non-negotiable rules |
| `01-philosophy-and-goals.md` | Research values, contribution standard, venue ambition |
| `02-context-and-scope.md` | Prior dcFCI work, deliberate reset away from D1–D4 |
| `03-candidate-directions.md` | A: unreliable CI; B: budget-aware; C: heterogeneity |
| `04-literature-and-gap-audit.md` | Literature and defensible research-gap protocol |
| `05-method-and-contribution.md` | Scientific mechanism and novelty tests |
| `06-experimental-evaluation.md` | Data, baselines, robustness, metrics and ablations |
| `07-workflow-and-decision-gates.md` | Research stages, pilots, stopping rules |
| `08-deliverables.md` | Reports A–J and paper concept |
| `../templates/topic-card.md` | One-page template for each idea |
| `../templates/evidence-matrix.md` | Table for evidence-backed paper review |
| `prompts/aprime_three_day/` | Three gated review prompts used for the 2026-11-04 A′ review |

## Scope and priorities

Candidates A and B have **initial** priority, but the agent must reassess them critically. Candidate C and outside alternatives are allowed. The older dcFCI pruning and D1–D4 proposals remain valuable technical context, not mandatory research directions.

A framework is not sufficient on its own: its novelty should be traced to a reproducible failure and central scientific insight. Strong benchmarks and robustness are required, but dataset count and speedup do not substitute for scientific significance.

## How to use the output

The first useful result is **not** full implementation: it is an evidence-backed shortlist, a reproducible failure-mode dossier, the strongest baselines, and inexpensive go/no-go pilots. A larger project begins only when a topic passes those gates.
