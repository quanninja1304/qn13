# P-N5 code snapshot (frozen before the P-N5 run)

Reference copy of the code that runs from `artifacts/n5_runs/pn5/` (git-ignored), with the dependencies it uses. Rules: [`../PN5_rules_vi.md`](../PN5_rules_vi.md) (v1, locked).

- `pn5/`: P-N5 code:
  - inputs: real tables with the SHA-256 check, row selection, normal-score, padding, [X_R | P] assembly;
  - X_R preparation;
  - runner for AVICI, CDFM, PC and GES, with the 900 s PC/GES limit and the 3 h budget stop;
  - classical worker; statistics; measures; gates; reading; completeness check; freeze gate; snapshot builder; run script.
- `deps/`: byte copies of the frozen P-N1 `common.py`, the DEV5 stand-in config `er2-rff-gauss.yaml` and the frozen P-N2 `common2.py`. The freeze gate also checks them against the P-N1 and P-N2 snapshots.
- `SHA256SUMS`: hashes of everything in `pn5/` and `deps/`. At the start and the end of the run, `verify_freeze5.py` checks each hash both in this snapshot and at the live location.
- `DEPS_SHA256.json`: hashes and package versions. The freeze gate checks every entry as well.
  - hashes: the `cdfm`, `avici` and `causallearn` package sources; the CDFM and AVICI checkpoints; the two data files; the data manifest;
  - package versions.

The data files are hashed, never copied: they stay in `artifacts/data_real/` (git-ignored). The snapshot is for verification, not for running in place.
