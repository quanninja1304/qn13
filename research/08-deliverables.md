# 08 — Required Outputs & Final Research Decision

**Language:** Vietnamese with precise English research terminology. **Evidence:** links to primary sources; label verified/inference/hypothesis/unresolved. Never present a proposed experiment as completed. Quality > document length.

## Reports A–J

### A. Research landscape

Table of ~15–25 relevant works: verified venue/status, problem, assumptions, central insight, method, theorem, SOTA baselines, benchmark, limitation, direct citation/URL. Highlight closest prior work for each candidate.

### B. Reproducible failure modes

2–3 dossiers: observation, conditions, hypothesized cause, evidence, strongest remedies, minimal reproduction, significance, what would falsify the problem.

### C. Methodological opportunities

3–5 **scientifically distinct** candidates, each in the order **Problem → Gap → Insight → Method → Evidence → Contribution**. Include a clear falsifiable methodological hypothesis.

### D. Novelty and depth audit

For each: comparison with the closest method; possible equivalence to old technique; claim of scientific novelty and its supporting evidence; minimum relevant theory; assumptions, open proof obligations and incremental-engineering risk.

### E. Evaluation strategy

Specified synthetic/semi-synthetic, relevant public benchmarks and real-world datasets; matched SOTA baselines (≥3 where applicable), metrics/output conventions, robustness axes, ablations, statistical controls and reproducibility requirements. If datasets are only candidates, mark them unverified.

### F. Comparative decision matrix

Compare significance, gap credibility, central insight, methodological originality, theoretical burden, empirical feasibility, benchmark availability, generality, research survivability, risk, time-to-first-evidence and Q1/top-conference fit. Explain judgments, not just unexplained numeric scores.

### G. Recommended direction

One **primary**, one **backup**, and one **ambitious optional extension only if justified**. Explicitly justify why the choice wins against both closest prior work and the other candidates. It's legitimate to recommend **no commitment yet** pending decisive evidence.

### H. First 4–6 week roadmap

Stage tasks, source-reading plan, minimal reproductions, baselines, cheap pilots, output artifacts, decision gates and conditions for stop/continue/pivot. Distinguish work completed from future tasks.

### I. Publication-oriented paper concept

For the primary direction: tentative title; one-sentence research question; precise problem statement; closest related work; scientific insight; central novel mechanism; three **potential** contributions; proof obligations; experimental hypotheses; SOTA comparisons; dataset/robustness plan; limitations; **150–200-word hypothetical abstract** with no invented results.

### J. Critical final verdict

Answer directly:

1. What is the most scientifically important candidate problem?
2. Which proposed mechanism has the strongest defensible novelty?
3. What is realistically executable with current resources?
4. Which option offers the best quality/risk balance for a strong Q1 paper?
5. What **conditional** outcome would be competitive at ICML/NeurIPS?
6. What first evidence is indispensable before investing months?
7. Which topics should be abandoned/deprioritized, and why?

## Mandatory per-topic minimum

Use [`../templates/topic-card.md`](../templates/topic-card.md). Every serious candidate needs **(a)** a reproducible failure, **(b)** a concrete new mechanism, **(c)** at least three relevant baseline categories where feasible, **(d)** a fair benchmark/robustness plan, **(e)** an early falsification test and **(f)** a research-survivability scenario.

## Final decision principle

Answer:

> Which scientifically significant and insufficiently addressed problem in modern causal discovery offers the strongest opportunity for a genuinely new methodological contribution, backed by rigorous empirical evidence and theory appropriate to its claims, within realistic research resources?

Neither the most abstract theorem nor the easiest speedup is the target. **Gap first; mechanism second; validation third; full implementation last.**
