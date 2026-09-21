# Phase-1 Windows-to-VPS migration

This handoff is an execution migration, not a scientific-contract change.
Schedulers, graph generation, seeds, metrics, thresholds, and the frozen config
digest remain unchanged.

## Fixed roles

- Source laptop: read-only archive after source preparation.
- VPS: sole writer while Phase 1 is active.
- External storage: durable immutable copy of the final artifact tree.
- The provider disk is execution storage, not the only backup.

Never run shard 5 or shard 7 on both machines. Never merge run rows or edit a
completed JSONL file manually.

## VPS target

The Phase-1 target is 4 vCPU, 32 GB RAM, and 500 GB NVMe. The vCPUs are not
described as dedicated unless the provider confirms that separately. Use an
x86-64 Ubuntu image. The source gate recorded Python 3.14.7, so reproduce
Python 3.14.x (preferably 3.14.7) and the pinned core package versions before
trying another minor version.

## Source gate (Windows)

1. Confirm that no `phase1-shard` worker is running.
2. Run all tests.
3. Create the frozen source snapshot, five-scheduler replay reference,
   environment records, and SHA-256 manifest:

```powershell
python -m pytest
python -m safety_prior.cli migration-prepare
```

Expected outputs include:

- `env/windows_source_freeze.txt`
- `env/windows_source_environment.json`
- `env/core_requirements_lock.txt`
- `artifacts/kill_test/phase1/migration_snapshot.json`
- `artifacts/kill_test/phase1/migration_replay_reference.json`
- `artifacts/kill_test/phase1/migration_sha256.jsonl`
- `artifacts/kill_test/phase1/migration_sha256_summary.json`

The checksum manifest retains complete project-relative paths. It does not
resolve files by basename. Do not modify the source after this gate; if a
required file changes, prepare a new snapshot and checksum manifest.

This checkout currently has no Git metadata. The SHA-256 source-tree digest is
therefore the code/artifact handoff identifier. A Git commit/tag can be added
later without replacing the scientific config digest.

## Transfer

Transfer the tree directly with resumable `rsync`, `rclone`, or SFTP. Do not
create a local archive on drive D. Preserve paths under a single target root,
recommended as `/srv/safety_prior`.

The source root

```text
D:\REsearch\causal multi-agent\safety_prior
```

maps deterministically to

```text
/srv/safety_prior
```

while retaining every relative component below the root.

## Target gate (Linux VPS)

Create and activate a Python 3.14.x virtual environment, install the pinned
core packages and the project without re-resolving dependencies, then run:

```bash
python -m pip install -r env/core_requirements_lock.txt
python -m pip install -e . --no-deps
python -m pytest
python -m safety_prior.cli migration-validate
```

`migration-validate` must pass both gates:

1. every transferred source file matches its size and SHA-256;
2. five completed runs (all five schedulers on graph 001) reproduce the exact
   graph digest, canonical output graph, CI count, weighted cost, and scientific
   query-sequence digest. Per-query timing is deliberately excluded.

It records the Linux environment separately in:

- `env/linux_vps_freeze.txt`
- `env/linux_vps_environment.json`

Do not resume if validation fails.

## Resume

After target validation passes, run only the two incomplete deterministic
shards under `tmux` or a service manager:

```bash
python -m safety_prior.cli phase1-shard --shard 5
python -m safety_prior.cli phase1-shard --shard 7
```

Use separate sessions. The runners skip immutable completed rows and retry an
incomplete logical run with its original graph seed, scheduler seed, config
digest, and logical run ID.

Monitor free disk, resident memory, CPU steal time, and process liveness. Do not
evaluate K1 from a subset.

## Completion and archive

After both shards finish:

```bash
python -m safety_prior.cli phase1-analyze
```

Require completion audit 800/800, failed 0, missing 0, duplicate 0, and
unexpected 0 before interpreting K1. Then freeze a final SHA-256 inventory and
copy the raw artifacts to external storage. Verify the external copy before
deleting the VPS. The laptop only needs code, configs, reports, manifests,
checksums, and selected results if its local disk cannot hold all raw JSONL.
