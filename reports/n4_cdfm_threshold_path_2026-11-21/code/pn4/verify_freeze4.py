"""P-N4 freeze gate (rules PN4 v1 §0 step 3). Run at the start and the end of the P-N4 run; exits non-zero if anything is off.

Checks:
 (1) every file in reports/n4_cdfm_threshold_path_2026-11-21/code/SHA256SUMS has that SHA-256 in the snapshot and at its live
     location: pn4/<f> -> artifacts/n4_runs/pn4/<f>; deps/<path> -> artifacts/<path>;
 (2) the dependency copies also match the earlier freezes: P-N1 code/SHA256SUMS (common.py, YAML configs) and
     P-N2 code/SHA256SUMS (common2.py);
 (3) every entry of code/DEPS_SHA256.json (cdfm package sources, CDFM checkpoint, avici package sources) matches the live file;
 (4) the snapshot has no uncommitted changes;
 (5) the commit that last changed SHA256SUMS is on a remote-tracking branch (pushed before the run).
Writes pn4_out/pn4_run_header.json (appends one header per call).
usage: verify_freeze4.py [label]
"""
import hashlib, json, subprocess, sys, datetime, platform
from pathlib import Path

RUNS4 = Path(__file__).resolve().parents[1]            # artifacts/n4_runs
ART = RUNS4.parent
REPO = ART.parent
SNAP = REPO / 'reports' / 'n4_cdfm_threshold_path_2026-11-21' / 'code'
SUMS, DEPS = SNAP / 'SHA256SUMS', SNAP / 'DEPS_SHA256.json'
PN1_SUMS = REPO / 'reports' / 'n1_irrelevant_vars_2026-11-13' / 'code' / 'SHA256SUMS'
PN2_SUMS = REPO / 'reports' / 'n2_context_mechanism_2026-11-20' / 'code' / 'SHA256SUMS'


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def entries(path):
    return {rel.strip().lstrip('*'): d for d, rel in (l.split(None, 1) for l in path.read_text(encoding='utf-8').splitlines() if l.strip())}


def live(rel):
    return RUNS4 / rel if rel.startswith('pn4/') else ART / rel[len('deps/'):]


bad = []
E = entries(SUMS)
for rel, digest in E.items():
    for f in (SNAP / rel, live(rel)):
        if not f.exists():
            bad.append(f'missing {f}')
        elif h(f) != digest:
            bad.append(f'sha mismatch {f}')
pn1, pn2 = entries(PN1_SUMS), entries(PN2_SUMS)
for rel, digest in E.items():
    if rel.startswith('deps/n1_runs/'):
        ref = pn1.get(rel[len('deps/n1_runs/'):])
        if ref != digest:
            bad.append(f'{rel} differs from the P-N1 frozen snapshot')
    elif rel.startswith('deps/n2_runs/'):
        ref = pn2.get(rel[len('deps/n2_runs/'):])
        if ref != digest:
            bad.append(f'{rel} differs from the P-N2 frozen snapshot')
deps = json.loads(DEPS.read_text(encoding='utf-8'))
for rel, digest in deps['files'].items():
    f = ART / rel
    if not f.exists():
        bad.append(f'missing dependency {rel}')
    elif h(f) != digest:
        bad.append(f'dependency sha mismatch {rel}')
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
           deps_sha=h(DEPS), n_files=len(E), n_dependency_files=len(deps['files']), python=platform.python_version(),
           ok=not bad, problems=bad)
out = RUNS4 / 'pn4_out' / 'pn4_run_header.json'
prev = json.loads(out.read_text()) if out.exists() else []
out.write_text(json.dumps(prev + [hdr], indent=1))
print(json.dumps(hdr, indent=1))
sys.exit(1 if bad else 0)
