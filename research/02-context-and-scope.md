# 02 — Background, Scope & Anti-Anchoring Guidance

## Research background

Earlier work centered on dcFCI candidate generation under uncertain CI evidence and latent confounding. The preliminary “old Direction C” proposed:

- Pair-domain selection of separating sets instead of unnecessary power-set combinations.
- Backtracking with graph-consistency pruning rules T1–T3.
- Persistent-premise propagation for colliders, ancestry and mandatory m-connecting paths.
- Conditional exact preservation of reference search/selection behavior.
- Profiling generation, orientation, graph validation, CI execution, cache, scores and deduplication.
- Possible partial-assignment extendibility and output-sensitive enumeration results.

A subsequent theoretical reassessment proposed **D1** incremental extendibility, **D2** distinct-MEC enumeration, **D3** search-budget effects on causal uncertainty, and **D4** restricted-CI MAG equivalence.

These are **prior explorations**, not binding topic choices. The current research goal is a different positioning: **problem-driven methodological work supported by empirical and focused theoretical evidence**.

## Allowed use of prior work

Prior dcFCI research can contribute:

- Familiarity with FCI/RFCI/dcFCI and uncertain CI inputs.
- Understanding of PAGs, MAGs, m-separation and latent confounding.
- Potential baseline implementations, profiling tools and failure-mode hypotheses.
- Awareness that code optimization alone may have weak novelty.

Do **not** assume:

- dcFCI must be the central method or central research question.
- A T1–T3 pruning implementation should be built before profiling a bottleneck.
- The search must target abstract MAG extendibility as its principal contribution.
- D2 is preferred because an earlier agent recommended it.
- A restricted-CI representation theorem is essential for a publication.

## Reference repositories (inspect only when relevant)

- dcFCI: https://github.com/adele/dcFCI — previously examined commit `a27c495acc28810a1e8e95878d535d90f82faaaf`.
- FCI.Utils: https://github.com/adele/FCI.Utils — previously examined commit `361e8904feb448d5d8069af694670e16e96a9e1f`.

When auditing implementation, pin dependencies and actual graph/CI/scoring semantics. Do not assume code behavior from a paper description alone. Note that these specific commits identify past research context, not a requirement to use outdated code.

## Search scope

Prioritize modern **robust and efficient causal discovery**, including:

- unreliable finite-sample CI evidence,
- latent confounding and structural uncertainty,
- computationally budgeted / anytime inference,
- heterogeneous or shifting environments.

Remain open to a stronger adjacent question. Reframe the scientific objective rather than merely expanding a narrow implementation task. For all candidates, distinguish **statistical uncertainty**, **structural ambiguity**, **search incompleteness**, and **implementation artifacts**.
