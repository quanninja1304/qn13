# P-N7 code snapshot (frozen before the P-N7 main runs)

Reference copy of the code that runs from `artifacts/n7_runs/pn7/` (git-ignored), with the dependencies it uses. Rules: [`../PN7_rules_vi.md`](../PN7_rules_vi.md) (v1, locked).

- `pn7/`: P-N7 code:
  - jobs, inputs (frozen P-N5 `assemble5`), FoundCause calls as in P-N1 (package API and the frozen P-N1 schedule adapter), and the schedule checks (source lines and row indices; no model call);
  - runner with the 3 h budget stop per run and the early stops (k0 rerun not bitwise; adapter at base 42 beyond 1e-6);
  - statistics (one-sided paired t, DEGENERATE, Holm), reading, completeness check, gates G1–G8, freeze gate, snapshot builder, run scripts (DEV7; two main runs, Sachs then Wine).
- `deps/`: byte copies of the frozen modules the code imports, checked against their original snapshots:
  - P-N1 `common.py`, `metrics.py`, `fc_adapter.py` and the four target configs;
  - P-N2 `common2.py` (padding generator, used by `common5.py`);
  - P-N5 `common5.py`.
- `SHA256SUMS`: hashes of everything in `pn7/` and `deps/`. At the start and the end of each main run, `verify_freeze7.py` checks each hash both in this snapshot and at the live location.
- `DEPS_SHA256.json`: hashes that the freeze gate also checks:
  - the `foundcause` and `avici` package sources; the FoundCause checkpoint, which must also match the P-N1 checkpoint manifest; the two data files;
  - the P-N5 outputs used as comparators (PC, GES) and for description (AVICI, CDFM) on the same inputs; the P-N5 reading and DEV5 log;
  - the P-N1 DEV output and log used by G2;
  - the data manifest, the P-N5 input hashes, the checkpoint manifest, and package versions.

The data files are hashed, never copied: they stay in `artifacts/data_real/` (git-ignored). The snapshot is for verification, not for running in place.
