# P-N4 code snapshot (frozen before the P-N4 run)

Reference copy of the code that runs from `artifacts/n4_runs/pn4/` (git-ignored), with the dependencies it uses. Rules: [`../PN4_rules_vi.md`](../PN4_rules_vi.md) (v1, locked).

- `pn4/`: P-N4 code (inputs, CDFM runner, copied threshold selector, statistics, measures, gates, reading, completeness, freeze gate, snapshot builder, run script).
- `deps/`: byte copies of the frozen P-N1 `common.py`, the two RFF target-generator configs and the frozen P-N2 `common2.py`. The freeze gate also checks them against the P-N1 and P-N2 snapshots.
- `SHA256SUMS`: hashes of everything in `pn4/` and `deps/`. `verify_freeze4.py` checks each hash in this snapshot and at the live location, at the start and the end of the run.
- `DEPS_SHA256.json`: hashes of the `cdfm` and `avici` package sources and of the CDFM checkpoint, plus package versions. The freeze gate checks these as well.

The snapshot is for verification, not for running in place.
