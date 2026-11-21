"""P-N3 freeze gate (rules v1 §6). Run before the pilot; exits non-zero if anything is off.

Checks: (1) every file in reports/n3_mechanism_pilot_2026-11-21/code/SHA256SUMS has that SHA-256 in the snapshot and in
artifacts/n3_runs; (2) the frozen dependencies still match their snapshots: P-N2 common2.py and P-N1 common.py;
(3) no uncommitted changes in the snapshot; (4) the commit that last changed SHA256SUMS is on a remote-tracking branch.
Writes pn3_out/pn3_run_header.json.  usage: verify_freeze_pn3.py [label]
"""
import hashlib, json, subprocess, sys, datetime, platform
from pathlib import Path

RUNS3 = Path(__file__).resolve().parents[1]
REPO = RUNS3.parents[1]
SNAP = REPO / 'reports' / 'n3_mechanism_pilot_2026-11-21' / 'code'
SUMS = SNAP / 'SHA256SUMS'
DEPS = [(REPO / 'artifacts' / 'n2_runs' / 'pn2' / 'common2.py', REPO / 'reports' / 'n2_context_mechanism_2026-11-20' / 'code' / 'SHA256SUMS', 'pn2/common2.py'),
        (REPO / 'artifacts' / 'n1_runs' / 'pn1' / 'common.py', REPO / 'reports' / 'n1_irrelevant_vars_2026-11-13' / 'code' / 'SHA256SUMS', 'pn1/common.py')]


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def entries(path):
    return [l.split(None, 1) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]


bad = []
E = entries(SUMS)
for digest, rel in E:
    rel = rel.strip().lstrip('*')
    for root in (RUNS3, SNAP):
        f = root / rel
        if not f.exists():
            bad.append(f'missing {f}')
        elif h(f) != digest:
            bad.append(f'sha mismatch {f}')
for f, sums, rel in DEPS:
    d = {r.strip().lstrip('*'): x for x, r in entries(sums)}
    if d.get(rel) != h(f):
        bad.append(f'dependency {rel} differs from its frozen snapshot')
dirty = git('status', '--porcelain', '--', SNAP.relative_to(REPO).as_posix())
if dirty:
    bad.append('uncommitted changes in snapshot: ' + dirty.replace('\n', '; '))
freeze = git('log', '-1', '--format=%H', '--', SUMS.relative_to(REPO).as_posix())
remote = git('branch', '-r', '--contains', freeze) if freeze else ''
if not freeze:
    bad.append('SHA256SUMS is not committed')
elif not remote:
    bad.append(f'freeze commit {freeze} is not on any remote-tracking branch (push it first)')
hdr = dict(label=sys.argv[1] if len(sys.argv) > 1 else '', time_local=datetime.datetime.now().isoformat(timespec='seconds'),
           freeze_commit=freeze, remote_branches=remote.split(), head=git('rev-parse', 'HEAD'), sha256sums_sha=h(SUMS),
           n_files=len(E), python=platform.python_version(), ok=not bad, problems=bad)
out = RUNS3 / 'pn3_out' / 'pn3_run_header.json'
prev = json.loads(out.read_text()) if out.exists() else []
out.write_text(json.dumps(prev + [hdr], indent=1))
print(json.dumps(hdr, indent=1))
sys.exit(1 if bad else 0)
