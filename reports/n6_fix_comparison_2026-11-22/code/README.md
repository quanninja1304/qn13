# P-N6 code snapshot (frozen before the P-N6 run)

Reference copy of the code that runs from `artifacts/n6_runs/pn6/` (git-ignored), with the dependencies it uses. Rules: [`../PN6_rules_vi.md`](../PN6_rules_vi.md) (v1, locked).

- `pn6/`: P-N6 code:
  - inputs, keys and screening decisions (R-L: fixed per-pair HSIC level; R-H: Bonferroni over the whole table);
  - runner for the HSIC p-values, plain models and the two fixes, with the DEV6-only modes (every component timed, R-oracle, reruns) and the 3 h budget stop;
  - alpha choice by J on DEV6 (no model output); measures; statistics (stratified t, non-inferiority composite, Holm, Clopper–Pearson); gates; reading; completeness check; freeze gate; snapshot builder; run scripts.
- `deps/`: byte copies of the frozen modules the code imports, checked against their original snapshots:
  - P-N1 `common.py`, `metrics.py` and the four target configs;
  - P-N2 `common2.py`, `screen.py`;
  - P-N4 `common4.py`, `selector4.py`;
  - P-N5 `common5.py`.
- `SHA256SUMS`: hashes of everything in `pn6/` and `deps/`. At the start and the end of the run, `verify_freeze6.py` checks each hash both in this snapshot and at the live location.
- `DEPS_SHA256.json`: hashes that the freeze gate also checks:
  - the `cdfm` and `avici` package sources; the CDFM and AVICI checkpoints; the two data files;
  - the P-N5 plain k0 outputs used for φ on the real tables; the chosen alpha levels (`alpha6.json`);
  - the data manifest and the P-N5 input hashes; package versions.

The data files are hashed, never copied: they stay in `artifacts/data_real/` (git-ignored). The snapshot is for verification, not for running in place.
