"""P-N8 / Study 7 freeze gate (rules PN8 v1 §7, §9). Run at the start and the end of each main run; exits non-zero if
anything is off.

Checks:
 (1) every file in reports/n8_sea_model_coverage_2026-11-23/code/SHA256SUMS has that SHA-256 in the snapshot and at its
     live location (pn8/<f> -> artifacts/n8_runs/pn8/<f>; deps/<path> -> artifacts/<path>); the SEA package list is
     recomputed and must equal sea_env_freeze.txt;
 (2) the dependency copies match their original frozen snapshots (P-N1, P-N2, P-N2 held2, P-N5, P-N7 SHA256SUMS);
 (3) every entry of code/DEPS_SHA256.json matches the live file (tracked SEA files, checkpoint, packages, data, Study 4
     outputs); the SEA clone is at the pinned commit with no modified tracked file (untracked files such as `dummy` and
     __pycache__ are ignored); the repository files listed under 'manifest' match;
 (4) the snapshot has no uncommitted changes;
 (5) the commit that last changed SHA256SUMS is on a remote-tracking branch (pushed before the run).
Appends one header per call to pn8_out/pn8_run_header.json; 'pn8_start_<run>' starts that run's budget clock.
usage (Study 1 model environment): python -I verify_freeze8.py <label>
"""
import hashlib, json, subprocess, sys, time, datetime, platform
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from freeze8 import SEA_SRC, SEA_COMMIT, sea_freeze, h

RUNS8 = Path(__file__).resolve().parents[1]
ART = RUNS8.parent
REPO = ART.parent
SNAP = REPO / 'reports' / 'n8_sea_model_coverage_2026-11-23' / 'code'
SUMS, DEPS = SNAP / 'SHA256SUMS', SNAP / 'DEPS_SHA256.json'
R = REPO / 'reports'
ORIG = {'deps/n1_runs/pn1/common.py': (R / 'n1_irrelevant_vars_2026-11-13/code/SHA256SUMS', 'pn1/common.py'),
        'deps/n1_runs/pn1/metrics.py': (R / 'n1_irrelevant_vars_2026-11-13/code/SHA256SUMS', 'pn1/metrics.py'),
        'deps/n2_runs/pn2/common2.py': (R / 'n2_context_mechanism_2026-11-20/code/SHA256SUMS', 'pn2/common2.py'),
        'deps/n2_runs/pn2/analyze_held2.py': (R / 'n2_context_mechanism_2026-11-20/code_held2/SHA256SUMS', 'pn2/analyze_held2.py'),
        'deps/n5_runs/pn5/common5.py': (R / 'n5_real_data_consistency_2026-11-22/code/SHA256SUMS', 'pn5/common5.py'),
        'deps/n7_runs/pn7/stats7.py': (R / 'n7_foundcause_real_tables_2026-11-22/code/SHA256SUMS', 'pn7/stats7.py')}
for e in (1, 2):
    for m in ('lin', 'rff'):
        ORIG[f'deps/n1_runs/config/er{e}-{m}-gauss.yaml'] = (R / 'n1_irrelevant_vars_2026-11-13/code/SHA256SUMS',
                                                              f'config/er{e}-{m}-gauss.yaml')


def git(*a, cwd=REPO):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True).stdout.strip()


def entries(path):
    return {rel.strip().lstrip('*'): d for d, rel in (l.split(None, 1) for l in path.read_text(encoding='utf-8').splitlines() if l.strip())}


def live(rel):
    if rel.startswith('pn8/'):
        return RUNS8 / rel
    if rel.startswith('deps/'):
        return ART / rel[len('deps/'):]
    return None


bad = []
E = entries(SUMS) if SUMS.exists() else {}
if not E:
    bad.append('SHA256SUMS missing or empty')
for rel, digest in E.items():
    for f in (SNAP / rel, live(rel)):
        if f is None:
            continue
        if not f.exists():
            bad.append(f'missing {f}')
        elif h(f) != digest:
            bad.append(f'sha mismatch {f}')
if (SNAP / 'sea_env_freeze.txt').exists() and sea_freeze().encode() != (SNAP / 'sea_env_freeze.txt').read_bytes():
    bad.append('SEA environment differs from sea_env_freeze.txt')
for rel, (sums, ent) in ORIG.items():
    if E.get(rel) != entries(sums).get(ent):
        bad.append(f'{rel} differs from its original frozen snapshot')
deps = json.loads(DEPS.read_text(encoding='utf-8')) if DEPS.exists() else dict(files={}, manifest={})
if not deps['files']:
    bad.append('DEPS_SHA256.json missing or empty')
for rel, digest in deps['files'].items():
    f = ART / rel
    if not f.exists():
        bad.append(f'missing dependency {rel}')
    elif h(f) != digest:
        bad.append(f'dependency sha mismatch {rel}')
sea_head = git('rev-parse', 'HEAD', cwd=SEA_SRC)
sea_mod = git('status', '--porcelain', '--untracked-files=no', cwd=SEA_SRC)
if sea_head != SEA_COMMIT or deps.get('sea_commit') != SEA_COMMIT:
    bad.append(f'SEA clone not at the pinned commit ({sea_head})')
if sea_mod:
    bad.append('SEA clone has modified tracked files: ' + sea_mod.replace('\n', '; '))
for rel, digest in deps.get('manifest', {}).items():
    if h(REPO / rel) != digest:
        bad.append(f'repository file differs from its frozen hash: {rel}')
dirty = git('status', '--porcelain', '--', SNAP.relative_to(REPO).as_posix())
if dirty:
    bad.append('uncommitted changes: ' + dirty.replace('\n', '; '))
freeze = git('log', '-1', '--format=%H', '--', SUMS.relative_to(REPO).as_posix())
remote = git('branch', '-r', '--contains', freeze) if freeze else ''
if not freeze:
    bad.append('SHA256SUMS is not committed')
elif not remote:
    bad.append(f'freeze commit {freeze} is not on any remote-tracking branch (push it first)')
hdr = dict(label=sys.argv[1] if len(sys.argv) > 1 else '', time_local=datetime.datetime.now().isoformat(timespec='seconds'),
           time_unix=time.time(), freeze_commit=freeze, remote_branches=remote.split(), head=git('rev-parse', 'HEAD'),
           sha256sums_sha=h(SUMS) if SUMS.exists() else None, deps_sha=h(DEPS) if DEPS.exists() else None, n_files=len(E),
           n_dependency_files=len(deps['files']), sea_commit=sea_head, python=platform.python_version(), ok=not bad,
           problems=bad)
out = RUNS8 / 'pn8_out' / 'pn8_run_header.json'
out.parent.mkdir(parents=True, exist_ok=True)
prev = json.loads(out.read_text()) if out.exists() else []
out.write_text(json.dumps(prev + [hdr], indent=1))
print(json.dumps(hdr, indent=1))
sys.exit(1 if bad else 0)
