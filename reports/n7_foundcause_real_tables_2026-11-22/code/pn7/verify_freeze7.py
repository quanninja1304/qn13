"""P-N7 freeze gate (rules PN7 v1 §6, §10). Run at the start and the end of each main run; exits non-zero if anything is off.

Checks:
 (1) every file in reports/n7_foundcause_real_tables_2026-11-22/code/SHA256SUMS has that SHA-256 in the snapshot and at
     its live location: pn7/<f> -> artifacts/n7_runs/pn7/<f>; deps/<path> -> artifacts/<path>;
 (2) the dependency copies also match their original frozen snapshots (P-N1, P-N2, P-N5 code/SHA256SUMS);
 (3) every entry of code/DEPS_SHA256.json matches the live file; the repository files listed under 'manifest' too;
 (4) the two data files match the P-N5 data manifest (data_ok); the FoundCause checkpoint matches the P-N1 checkpoint
     manifest (checkpoint_ok);
 (5) the snapshot has no uncommitted changes;
 (6) the commit that last changed SHA256SUMS is on a remote-tracking branch (pushed before the run).
Appends one header per call to pn7_out/pn7_run_header.json (time_unix of 'pn7_start_<table>' starts that run's 3 h clock).
usage: verify_freeze7.py <label>
"""
import hashlib, json, subprocess, sys, time, datetime, platform
from pathlib import Path

RUNS7 = Path(__file__).resolve().parents[1]            # artifacts/n7_runs
ART = RUNS7.parent
REPO = ART.parent
SNAP = REPO / 'reports' / 'n7_foundcause_real_tables_2026-11-22' / 'code'
SUMS, DEPS = SNAP / 'SHA256SUMS', SNAP / 'DEPS_SHA256.json'
MANIFEST = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'manifest' / 'data_manifest.json'
CKPT_MANIFEST = REPO / 'reports' / 'direction_scan_2026-11-13' / 'n1_checkpoint_manifest.json'
CKPT = 'n1_models_cpu/checkpoints/foundcause/checkpoint.pt'
ORIG = {'deps/n1_runs/': REPO / 'reports' / 'n1_irrelevant_vars_2026-11-13' / 'code' / 'SHA256SUMS',
        'deps/n2_runs/': REPO / 'reports' / 'n2_context_mechanism_2026-11-20' / 'code' / 'SHA256SUMS',
        'deps/n5_runs/': REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'code' / 'SHA256SUMS'}
DATA = {'sachs': 'data_real/sachs_zenodo_7681811/extracted/cd3cd28.csv',
        'wine_white': 'data_real/uci_wine_quality_186/extracted/winequality-white.csv'}


def h(p):
    d = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 22), b''):
            d.update(chunk)
    return d.hexdigest()


def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def entries(path):
    return {rel.strip().lstrip('*'): d for d, rel in (l.split(None, 1) for l in path.read_text(encoding='utf-8').splitlines() if l.strip())}


def live(rel):
    return RUNS7 / rel if rel.startswith('pn7/') else ART / rel[len('deps/'):]


bad = []
E = entries(SUMS) if SUMS.exists() else {}
if not E:
    bad.append('SHA256SUMS missing or empty')
for rel, digest in E.items():
    for f in (SNAP / rel, live(rel)):
        if not f.exists():
            bad.append(f'missing {f}')
        elif h(f) != digest:
            bad.append(f'sha mismatch {f}')
orig = {pre: entries(p) for pre, p in ORIG.items()}
for rel, digest in E.items():
    for pre, ent in orig.items():
        if rel.startswith(pre) and ent.get(rel[len(pre):]) != digest:
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
for rel, digest in deps.get('manifest', {}).items():
    if h(REPO / rel) != digest:
        bad.append(f'repository file differs from its frozen hash: {rel}')
man = json.loads(MANIFEST.read_text(encoding='utf-8'))
data_sha = {k: h(ART / rel) for k, rel in DATA.items()}
data_ok = all(data_sha[k] == man[k]['member_used']['sha256'] for k in DATA)
if not data_ok:
    bad.append('a data file differs from the data manifest')
cm = json.loads(CKPT_MANIFEST.read_text(encoding='utf-8'))
ck_ref = [f['sha256'] for f in cm['files'] if f['path'].endswith(CKPT)]
ck_live = deps['files'].get(CKPT)
checkpoint_ok = bool(ck_ref) and ck_live == ck_ref[0]
if not checkpoint_ok:
    bad.append('FoundCause checkpoint differs from the P-N1 checkpoint manifest')
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
           n_dependency_files=len(deps['files']), data_sha=data_sha, data_ok=data_ok, checkpoint_ok=checkpoint_ok,
           python=platform.python_version(), ok=not bad, problems=bad)
out = RUNS7 / 'pn7_out' / 'pn7_run_header.json'
out.parent.mkdir(parents=True, exist_ok=True)
prev = json.loads(out.read_text()) if out.exists() else []
out.write_text(json.dumps(prev + [hdr], indent=1))
print(json.dumps({k: v for k, v in hdr.items() if k != 'data_sha'}, indent=1))
sys.exit(1 if bad else 0)
