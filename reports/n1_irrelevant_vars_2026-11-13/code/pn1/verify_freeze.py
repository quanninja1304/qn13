"""v2.2 freeze gate. Run before any held-out job; exits non-zero (and the runner stops) if anything is off.

Checks: (1) every file in reports/.../code/SHA256SUMS has that SHA-256 both in the snapshot and in artifacts/n1_runs
(the code that actually runs); (2) the snapshot has no uncommitted changes; (3) the commit that last changed SHA256SUMS
is on a remote-tracking branch (pushed before the run). Writes pn1_out/held_run_header.json with the commit and hashes.
usage: verify_freeze.py [label]
"""
import hashlib, json, subprocess, sys, datetime, platform
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1]              # artifacts/n1_runs
REPO = RUNS.parents[1]                                  # safety_prior
SNAP = REPO / 'reports' / 'n1_irrelevant_vars_2026-11-13' / 'code'
SUMS = SNAP / 'SHA256SUMS'


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


bad = []
entries = [l.split(None, 1) for l in SUMS.read_text(encoding='utf-8').splitlines() if l.strip()]
for digest, rel in entries:
    rel = rel.strip().lstrip('*')
    for root in (RUNS, SNAP):
        f = root / rel
        if not f.exists():
            bad.append(f'missing {f}')
        elif h(f) != digest:
            bad.append(f'sha mismatch {f}')
dirty = git('status', '--porcelain', '--', str(SNAP.relative_to(REPO)))
if dirty:
    bad.append('uncommitted changes in snapshot: ' + dirty.replace('\n', '; '))
freeze = git('log', '-1', '--format=%H', '--', str(SUMS.relative_to(REPO)).replace('\\', '/'))
remote = git('branch', '-r', '--contains', freeze) if freeze else ''
if not freeze:
    bad.append('SHA256SUMS is not committed')
elif not remote:
    bad.append(f'freeze commit {freeze} is not on any remote-tracking branch (push it first)')
hdr = dict(label=sys.argv[1] if len(sys.argv) > 1 else '', time_local=datetime.datetime.now().isoformat(timespec='seconds'),
           freeze_commit=freeze, remote_branches=remote.split(), head=git('rev-parse', 'HEAD'), sha256sums_sha=h(SUMS),
           n_files=len(entries), python=platform.python_version(), ok=not bad, problems=bad)
out = RUNS / 'pn1_out' / 'held_run_header.json'
prev = json.loads(out.read_text()) if out.exists() else []
out.write_text(json.dumps(prev + [hdr], indent=1))
print(json.dumps(hdr, indent=1))
sys.exit(1 if bad else 0)
