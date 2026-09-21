# Safe Imperfect Priors kill test

Reproducible, offline experiments testing whether an imperfect prior can safely
schedule conditional-independence queries in FCI. A prior may rank eligible
queries; it cannot answer CI queries or modify/orient graph edges.

The frozen scientific contract is in `docs/kill_test/03_scientific_contract.md`.
Install with `python -m pip install -e .[test]`, run tests with `pytest`, and see
`python -m safety_prior.cli --help` for experiment commands.

For the Windows-to-Linux execution handoff, follow
`docs/kill_test/vps_migration.md`. The source and target gates are:

```text
python -m safety_prior.cli migration-prepare
python -m safety_prior.cli migration-validate
```
