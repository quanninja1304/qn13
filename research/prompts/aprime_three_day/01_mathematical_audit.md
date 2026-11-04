# DAY 1 — Independent Mathematical Audit of A′

## Role and objective
Act as an independent research mathematician/statistician and adversarial reviewer. Your assignment is **to assess, not to defend**, the mathematical formulation of A′ (*dependence-aware causal feature scoring*). All earlier propositions, labels such as “Verified”, and claimed novelty are **claims to verify**, not accepted premises. A valid outcome may be preservation, modification, or rejection of A′.

**Do not implement the full solver, run a benchmark, or manufacture a theorem.** Do not move to Day 2 merely because a schedule says so.

## Required source material
Read `AGENTS.md` and relevant research instructions, then locate and read:
- `A1_gap_confirmation_and_proof_sketch_vi.md` (especially definitions, assumptions A1–A2 and P1–P7);
- `A1_next_steps_plan_vi.md` (definitions of D, A′-P0 through P7, GA0–GA6 and unit tests);
- `00_final_reassessment_vi.md`, related source audits and available topic card(s).
If paths differ, locate content by title. Missing files must be listed; distinguish what can be audited without them. Read available primary sources when a claim materially depends on them; mark unavailable sources **UNVERIFIED**. Preserve original proposal and decision log; write a new version rather than silently overwriting.

## Step 1 — Reconstruct an explicit mathematical contract
Without relying on the proposal's prose, independently state:
1. Target output: ancestry, endpoint, adjacency, or other feature; feature truth and identifiability relative to an admissible graph/model family.
2. Inputs: observed variables, statistical model, allowed MAG/PAG/ancestral structures, latent/selection assumptions, finite query family Q, whether Q is fixed before seeing data or selected adaptively, effect of query duplication.
3. Random variables: each CI test statistic, its population counterpart, scaling with sample size, covariance matrix and estimator, joint asymptotic regime (fixed/growing p and K), dependence on overlapping samples.
4. For each graph m, the *actual distribution-level attainable parameter set* versus the coordinatewise proposed region `R_n(m)`; state whether equality, subset or relaxation is known.
5. Exact loss and feature score: one-sided distance versus signed difference between restricted optima; specify empty or nonidentifiable cases and appropriate outputs.
6. The role, availability and sensitivity of beta-min η; distinguish faithfulness from a known uniform lower bound.
Produce a notation table including units/dimensions, quantifier order and an explicit list of assumptions. If any definition is underspecified, offer at least two mathematically distinct interpretations and describe how conclusions change; do not secretly choose one.

## Step 2 — Audit assumptions and possible failure modes
For each item, **attempt both proof and counterexample**; an unresolved result is acceptable.
- **Model identifiability:** Construct small graphs or observationally equivalent models; determine whether the score can discriminate features not identifiable from Q. Check whether the candidate set has both f and ¬f models, and whether they share Q-patterns.
- **Statistical realizability:** Determine whether independent coordinate constraints on partial correlations/Fisher-z can describe a joint population distribution. Test positive-definiteness/consistency constraints and whether `R_n(m)` includes impossible statistic vectors. Distinguish a convenient working-model relaxation from exact MAG likelihood.
- **Beta-min:** Check necessity for P1/P2, finite-sample behavior for unknown η, behavior as η→0, η misspecification, and whether the assumption is meaningful for dependence measured by each proposed CI statistic.
- **Covariance:** Establish when Σ is positive definite, singular, or merely estimable. In Gaussian models inspect rank bounds caused by mapping sample covariance to many partial-correlation statistics. Distinguish duplicate queries, near-duplicates and other linear dependencies. Examine pseudoinverse support constraints, shrinkage, numerical conditioning and how each alters the objective.
- **Adaptive querying:** Assess whether standard joint asymptotics for a fixed Q remain valid when FCI/ACI chooses Q using the same data. Identify what would require data splitting, conditional/selective inference or a restricted claim.
- **Nonparametric extension:** If GCM/kernel/mixed-data statistics are mentioned, list exact null/alternative and joint-CLT/estimator conditions; do not assume a zero residual product implies conditional independence under arbitrary distributions.

## Step 3 — Re-derive propositions P1–P7
For each Pk, create a proposition ledger with: original statement; full assumptions; result (PROVED / VALID WITH MODIFICATION / COUNTEREXAMPLE / UNRESOLVED); independent derivation or smallest counterexample; implications for implementation and research claims.
Special checks:
- P1: finite-n positivity/negativity/zero versus an infinity claim in a planned unit test. Handle empty model families, finite/closed sets, true-model inclusion and the exact meaning of Q-identifiable.
- P2: asymptotic rate and eigenvalue bounds; fixed Q/model family versus sequences growing with n; beta-min and consistent Σhat.
- P3: distinguish reduction to an **ACI-type** additive weighted-disagreement objective from equivalence to ACI's published weights, thresholds, and confidence interpretation. Specify whether equality concerns loss values, optimizers or feature ordering.
- P4: independently recompute the 2-statistic correlated Gaussian example, including the required inactive constraints. Test whether the CI-pattern pair can be realized by admissible MAGs/queries; distinguish algebraic nonseparability from causal novelty.
- P5: exact duplicate with singular covariance: prove or refute under the chosen pseudoinverse/support convention; investigate continuity for near-duplicates without assuming it.
- P6: distinguish a GLR for a **working Gaussian statistic model** from an LR for an actual Gaussian MAG model; clarify distributional calibration and any nonconvex union-of-regions issue.
- P7: check inequality direction for restricted candidate search, including separate approximations on f and ¬f; decide what can be called a safe bound and what cannot.
No theorem may be described as independently verified unless its proof has actually been checked.

## Step 4 — Explore alternatives without defending one
If a fatal issue is found, compare the **minimum necessary** repairs: redefining the attainable region, restricting feature/model/query classes, replacing absolute “confidence” with fragility/ranking, different score, nuisance-parameter profile likelihood, conditional evidence, etc. Report what each repair buys and what scientific question it changes. These are candidates for assessment, not mandatory solutions. Distinguish standard GLS/constrained inference from a genuinely causal-specific insight.

## Step 5 — Independent verdict and handoff
Classify each blocker as FATAL / REFORMULABLE / TESTABLE / UNKNOWN. Give a **Day 2 authorization**:
- **TOY-ONLY:** mathematical score is coherent enough for algebraic/numerical sanity checks;
- **TOY-WITH-CAVEATS:** only specified components are testable, with exact caveats;
- **STOP-AND-REFORMULATE:** no interpretable score yet; Day 2 may test counterexamples only, not comparative performance.
Do not approve a full A′ framework, confirmatory benchmark or publication claim.

## Required artifact
Write `A1_mathematical_contract_v2.md` with sections: executive verdict; reconstructed contract; assumption ledger; P1–P7 proof audit; counterexamples; implementation test specification (expected outputs and tolerances); alternative formulations; blockers; Day 2 authorization; citation/evidence register. Provide equation numbers, reproducible symbolic/numeric examples and source/page/theorem references where available. Update decision log by appending the outcome, not editing history.

**Response language: Vietnamese, retaining English mathematical terminology. Do not invent sources, proofs, experimental evidence, or an optimistic conclusion.**
