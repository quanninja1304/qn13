# Repository audit (2026-09-19)

At audit time the directory contained only three Vietnamese design documents,
no VCS metadata, code, package manager configuration, tests, artifacts, or
instructions (`AGENTS.md` was absent). The workspace was therefore initialized
as a Python package. Existing documents were not modified.

| Item | Current state | Reusable | Missing | Risk |
|---|---|---|---|---|
| Graph representation | causal-learn `GeneralGraph`; NetworkX full DAG | Yes | independently checked MAG class | medium |
| DAG/MAG/PAG conversion | oracle FCI operational PAG reference | partial | independent latent projection/PAG oracle | high |
| FCI | causal-learn 0.1.4.8 rules, locally adapted FAS | Yes | upstream pin/characterization | medium |
| RFCI | no implementation found in workspace/backend | no | complete RFCI-stable baseline | high/open |
| Stable variant | upstream FAS defaults `stable=True`, batch removal by depth | Yes | stable Possible-D-SEP scheduling hook | medium |
| Oracle CI | NetworkX d-separation on full DAG | Yes | motif verification | low after tests |
| Finite-sample CI | causal-learn Fisher-Z | Yes | phase-3 validation | medium |
| Experiment runner | absent initially | no | implemented in this package | low |
| Metrics | absent initially | no | skeleton/endpoints/budget/gates implemented | medium |
| Provenance logging | absent initially | no | query and graph-decision JSONL implemented | low |
| Reproducibility | no seeds/configs initially | no | split seeds/manifests/digests implemented | low |

Configuration uses YAML; pytest is the test framework. Artifacts live under
`artifacts/kill_test`, reports under `reports/kill_test`. Git revision is recorded
as `UNAVAILABLE_NOT_A_GIT_REPOSITORY` until the user initializes version control.

