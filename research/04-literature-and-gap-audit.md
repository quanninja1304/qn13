# 04 — Literature Landscape & Novelty Audit

## Scope

Review approximately **15–25 directly relevant papers**, expanding for essential prior art; favor recent ICML, NeurIPS, ICLR, UAI, AISTATS, and reputable Q1 journals, alongside older foundational papers and adjacent methodological literature. Read primary proceedings, appendices and repos when claims depend on detail.

Do not treat previously produced literature reviews as verified without rechecking. Identify preprints versus published papers accurately.

## For each paper record

- Full title, authors, year, venue/status, DOI/official source URL.
- Exact problem and intended output (DAG, CPDAG, MAG, PAG, confidence set, causal features, etc.).
- Assumptions (causal sufficiency, latent variables, selection bias, stationarity, faithfulness, CI oracle, finite sample, data type).
- Core insight and novel method, not just pipeline components.
- Theorems and scope of guarantees; do not generalize past assumptions.
- Baselines, datasets, official benchmark suite, metrics and experimental controls.
- Failure conditions, limitations, unanswered questions and what follows *in fact* from the evidence.
- Relationship to our candidate gap: already solved / partially addressed / genuinely different / unclear.

Populate [`../templates/evidence-matrix.md`](../templates/evidence-matrix.md).

## Strong-prior-work check

For any claim that seems new, ask whether it already exists as:

- graph consistency / m-separation reasoning;
- conservative, bootstrap, probabilistic or weighted CI decision making;
- active learning / query selection / anytime inference;
- invariant and heterogeneous causal discovery;
- SAT/ASP/CSP/MaxSAT or projected enumeration;
- a simple baseline, data-processing fix or standard regularization trick.

Useful starting leads to verify (not an exhaustive bibliography): dcFCI, FCI/RFCI, MAGLIST, GPS, Dseptor, k-PC, C-PC, recent differentiable constraint-based causal discovery, uncertainty-aware and robust FCI variants, active causal discovery, invariant learning. Their precise claims must be verified in the current literature audit.

## Defensible gap statement

For each shortlisted gap produce a sentence with citations:

> Under assumptions **A**, the strongest known methods **X/Y** can achieve **P**, but available evidence indicates an unresolved limitation **L** under condition **B**. The proposed research investigates whether mechanism **M** can overcome **L** without sacrificing **C**.

Indicate explicitly if part of that sentence remains a hypothesis.

## Failure-mode dossier

Identify 2–3 important, **reproducible** failures. Record:

1. What fails, on which exact task/output?
2. Under what conditions, settings and assumptions?
3. What is the suspected causal/statistical/computational mechanism?
4. What primary evidence supports this claim?
5. Which strongest existing remedies are relevant?
6. What minimal experiment would reproduce it and isolate its cause?
7. What scientific or applied capability would improve if fixed?
8. What result would show the “gap” is unimportant or already solved?

Avoid using only an author's Future Work section or cherry-picked toy cases as the basis for a novel topic.

## Evidence labels

Mark statements as **[Verified]**, **[Inference]**, **[Hypothesis]**, or **[Unresolved]**. Cite supporting source sections/theorems/figures where possible. If evidence is inaccessible, admit the limitation; do not silently replace it with guesswork.
