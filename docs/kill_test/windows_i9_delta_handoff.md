# Binding handoff: finish Phase-1 shards 5 and 7 on the Windows i9 worker

## Authority and exact scope

You are the execution agent for one frozen research handoff. Do exactly this:

1. install the verified delta input package into the exact bundled Git revision;
2. run the remaining 150 logical runs from Phase-1 shard 5 and shard 7;
3. use exactly three graph-level workers;
4. finalize the queue and export one checksummed delta return package;
5. report the final queue status and return-package checksum to the owner.

Do not redesign, optimize, analyze, interpret, or extend the experiment. Do not
run K2/K3, do not write the paper, and do not run `phase1-analyze` on this
worker. The worker deliberately does not receive the old 650 query logs, so the
800/800 scientific audit belongs on the owner's machine after verified import.

## Frozen facts

- Expected full Phase-1 matrix: 800 logical runs.
- Completed at handoff: 650.
- Pending: exactly 150.
- Allowed shards: 5 and 7 only.
- Pending graph indices: 104--119 and 145--159 (31 graph tasks, including two
  partially completed graphs).
- Scientific config digest:
  `bf345812da7b75514f7c145d92be229b55a7c333f14bcb3ca4f9c5d986e6f828`.
- Parallel unit: one graph. The five schedulers inside a graph remain ordered
  by frozen scheduler seed, with `stable_default` first when it is missing.
- Authorized concurrency: exactly three worker slots.
- Raw delta output is expected to be large (roughly 70--120+ GB). Its actual
  size is determined by the frozen runs and must not be truncated to meet a
  target size.

## Prohibited actions

- Do not run `phase1-shard`.
- Do not launch more than three `phase1-graph-worker` processes.
- Do not run duplicate worker commands outside the queue.
- Do not edit Python source, configs, parquet inventory, seeds, logical IDs,
  manifests, run rows, JSONL, or the delta contract.
- Do not use `git pull`, merge, rebase, checkout another revision, or install a
  different code version after cloning the bundle.
- Do not delete a claim, slot, partial log, or failed manifest manually.
- Do not omit raw query logs from the return package.
- Do not substitute console logs, summaries, or `runs.parquet` for raw
  artifacts.
- Do not run on battery, allow sleep/hibernate, or place the project under a
  cloud-synced directory.

If any required gate below fails, stop and report it. Do not improvise.

## Hardware gate for the i9-13900H machine

The intended machine has an Intel Core i9-13900H and 16 GB RAM. The CPU is
adequate; RAM and disk are the binding resources.

Before installation and execution:

1. reboot Windows;
2. connect AC power and select Best/High performance;
3. close browsers, IDEs, Spotify, game launchers, Docker, WSL, VMs, and sync
   clients;
4. use an NTFS NVMe or SSD project volume, never FAT32;
5. ensure the machine cannot sleep while workers are active.

Run in PowerShell:

```powershell
$os = Get-CimInstance Win32_OperatingSystem
$drive = Get-PSDrive -Name (Get-Location).Drive.Name
[pscustomobject]@{
    FreeRAMGB  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    FreeDiskGB = [math]::Round($drive.Free / 1GB, 2)
} | Format-List
```

Hard requirements before starting workers:

- free RAM: at least 9 GB;
- free disk on the project volume: at least 200 GB;
- free space on the return-package destination: at least 150 GB;
- no existing `phase1-shard` or `phase1-graph-worker` process.

If these requirements are not met, stop. Free space, close processes, or move
the entire worker checkout to a larger NTFS SSD. Do not lower the thresholds.

## 1. Clone the bundled, exact code revision

The owner supplies a directory named `phase1_delta_input` containing
`handoff_code.bundle`, `delta_package.json`, `delta_package_sha256.jsonl`, and
the small resume tree.

Set paths explicitly:

```powershell
$package = "E:\phase1_delta_input"
$workerRoot = "D:\phase1_delta_worker"
git clone (Join-Path $package "handoff_code.bundle") $workerRoot
Set-Location $workerRoot
git status --short --branch
git rev-parse HEAD
```

The worktree must be clean. The revision printed by `git rev-parse HEAD` must
equal `code_revision` in:

```powershell
Get-Content (Join-Path $package "delta_package.json") -Raw
```

Do not pull from any remote.

## 2. Create the exact Python environment

Use Python 3.14.x, preferably 3.14.7:

```powershell
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\env\core_requirements_lock.txt
python -m pip install -e . --no-deps
python --version
python -m pytest
```

Required test result: `35 passed` or more, with zero failures.

## 3. Verify and install the delta input

```powershell
python -m safety_prior.cli delta-verify-package --package $package
python -m safety_prior.cli delta-install-input --package $package
```

Both commands must report `status: PASS`. Installation must report:

```text
completed = 650
pending = 150
workers = 3
```

Validate deterministic replay on Windows:

```powershell
@'
from safety_prior.migration import validate_replay_reference
result = validate_replay_reference()
print(result["status"])
if result["status"] != "PASS":
    raise SystemExit(1)
'@ | python -
```

The final line must be `PASS`.

Prepare the graph queue exactly once:

```powershell
python -m safety_prior.cli phase1-queue-prepare
python -m safety_prior.cli phase1-queue-status
```

Expected initial queue status:

```text
expected_pending = 150
completed_pending = 0
missing_pending = 150
failed_or_invalid = 0
```

## 4. Launch exactly three workers

Do not launch until the hardware gate still passes. Then:

```powershell
$env:OMP_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

$logDir = Join-Path (Get-Location) "worker_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$pythonExe = (Get-Command python).Source

$workers = foreach ($number in 1..3) {
    $workerId = "worker-$number"
    Start-Process -FilePath $pythonExe `
        -ArgumentList @("-m","safety_prior.cli","phase1-graph-worker","--worker-id",$workerId) `
        -WorkingDirectory (Get-Location) `
        -RedirectStandardOutput (Join-Path $logDir "$workerId-$stamp.out.log") `
        -RedirectStandardError  (Join-Path $logDir "$workerId-$stamp.err.log") `
        -WindowStyle Hidden -PassThru
}

foreach ($process in $workers) {
    (Get-Process -Id $process.Id).PriorityClass = "AboveNormal"
}

$workers | Select-Object Id, StartTime | Format-Table -AutoSize
```

The queue enforces three atomic slots and one exclusive claim per graph. A
worker dynamically claims the next incomplete graph, so fixed graph ranges are
not assigned manually.

## 5. Monitor without modifying state

Use read-only commands:

```powershell
python -m safety_prior.cli phase1-queue-status

Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match '^python' -and
    $_.CommandLine -match 'phase1-graph-worker'
} |
Select-Object ProcessId, CreationDate, CommandLine | Format-List

$os = Get-CimInstance Win32_OperatingSystem
$drive = Get-PSDrive -Name (Get-Location).Drive.Name
[pscustomobject]@{
    FreeRAMGB  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    FreeDiskGB = [math]::Round($drive.Free / 1GB, 2)
} | Format-List
```

Inspect errors without editing them:

```powershell
Get-ChildItem .\worker_logs\*.err.log |
Sort-Object LastWriteTime -Descending |
ForEach-Object { "--- $($_.Name) ---"; Get-Content $_.FullName -Tail 80 }
```

Operational thresholds:

- if free RAM remains below 3 GB or paging is sustained, stop one worker by
  exact PID and continue with two;
- if free disk falls below 50 GB, stop all three exact worker PIDs and obtain
  more storage before resuming;
- never kill all Python processes by name;
- never delete stale claims manually.

After an environmental interruption, confirm the old PID is gone and rerun the
same worker command. Startup automatically recovers claims owned by dead local
processes and immutable completed rows are skipped. For a scientific/code/config
error, stop and report; do not patch it on the worker machine.

## 6. Finalize the queue

Wait until no `phase1-graph-worker` process remains, then run:

```powershell
python -m safety_prior.cli phase1-queue-status --finalize
```

Required result:

```text
status = COMPLETED
expected_pending = 150
completed_pending = 150
missing_pending = 0
failed_or_invalid = 0
active_slots = []
shard 5 completed = 100
shard 7 completed = 100
```

If any value differs, do not export and do not claim success.

Do not run `phase1-analyze` here.

## 7. Export the raw delta return package

Use a new empty directory on an NTFS disk with at least 150 GB free:

```powershell
$returnPackage = "E:\phase1_delta_return"
python -m safety_prior.cli delta-export-return --output $returnPackage
python -m safety_prior.cli delta-verify-package --package $returnPackage
```

Both commands must report `status: PASS`. The export includes exactly the 150
frozen pending run rows, every referenced query/event/graph artifact, rebuilt
shard 5/7 manifests, queue manifests, metadata, and SHA-256 manifest.

Do not remove raw files to force the package near 70 GB. If the deterministic
runs produce 100 GB or more, return all of it.

## 8. Report and hand back

Give the owner:

1. the complete `phase1_delta_return` directory;
2. the three worker stdout/stderr log pairs separately;
3. the full output of `phase1-queue-status --finalize`;
4. `tree_sha256`, file count, and byte count from `delta-export-return`;
5. any restart, low-memory, low-disk, or thermal warning.

The owner will verify hashes, import the delta into the frozen 650-run source,
and run `phase1-analyze`. That final audit is not delegated to this worker.

