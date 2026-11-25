"""Build the P-N8 / Study 7 code snapshot (rules PN8 v1 §9 step 3): code plus the dependencies it uses.

Writes reports/n8_sea_model_coverage_2026-11-23/code/:
  pn8/<file>          Study 7 code (this directory)
  deps/<path>         frozen copies used unchanged: P-N1 common.py, metrics.py, configs; P-N2 common2.py, analyze_held2.py
                      (source of the strat check); P-N5 common5.py; P-N7 stats7.py
  sea_env_freeze.txt  name==version of every package of the SEA environment (equivalent to `pip freeze`)
  SHA256SUMS          hashes of everything above (checked against live files by verify_freeze8.py)
  DEPS_SHA256.json    hashes of: the tracked files of the SEA clone (plus its commit), the SEA checkpoint, the avici and
                      causal-learn sources, the two data files, Study 4's PC/GES outputs used as descriptive comparators;
                      plus repository files (rules, input manifests) and package versions
  .gitattributes      byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n8_runs/pn8. Data files are hashed, never copied.
usage (Study 1 model environment): python -I freeze8.py
"""
import hashlib, json, shutil, platform, subprocess, sys
from pathlib import Path
import importlib.metadata as md

PN8 = Path(__file__).resolve().parent
RUNS8 = PN8.parent
ART = RUNS8.parent
REPO = ART.parent
SNAP = REPO / 'reports' / 'n8_sea_model_coverage_2026-11-23' / 'code'
CODE = ['common8.py', 'run8.py', 'sea_wrapper8.py', 'classical8.py', 'stats8.py', 'analyze8.py', 'completeness8.py',
        'gates8.py', 'verify_freeze8.py', 'freeze8.py', 'run_dev8.sh', 'run_pn8.sh']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/pn1/metrics.py'] + \
            [f'n1_runs/config/er{e}-{m}-gauss.yaml' for e in (1, 2) for m in ('lin', 'rff')] + \
            ['n2_runs/pn2/common2.py', 'n2_runs/pn2/analyze_held2.py', 'n5_runs/pn5/common5.py', 'n7_runs/pn7/stats7.py']
SEA_SRC = RUNS8 / 'sea_src'
SEA_PY = RUNS8 / 'sea_env' / 'Scripts' / 'python.exe'
SEA_COMMIT = 'bfb507b002d7f066f307a0dc15bd23fc703848b4'
PKGS = ['n1_models_cpu/repos/avici/avici', 'n1_models_cpu/.venv/Lib/site-packages/causallearn']
DATA = ['data_real/sachs_zenodo_7681811/extracted/cd3cd28.csv', 'data_real/uci_wine_quality_186/extracted/winequality-white.csv']
REF5 = [f'n5_runs/pn5_out/{a}/{t}__k0.npz' for a in ('pc', 'ges') for t in ('sachs', 'wine')] + \
       [f'n5_runs/pn5_out/{a}/{t}__k20_e0__r{r:02d}.npz' for a in ('pc', 'ges') for t in ('sachs', 'wine') for r in range(20)]
REPO_FILES = ['reports/n8_sea_model_coverage_2026-11-23/PN8_rules_vi.md',
              'reports/n5_real_data_consistency_2026-11-22/manifest/data_manifest.json',
              'reports/n5_real_data_consistency_2026-11-22/checks/inputs5.json']


def h(p):
    d = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 22), b''):
            d.update(chunk)
    return d.hexdigest()


def sea_freeze():
    """name==version of every installed distribution of the SEA environment (created with uv, which installs no pip;
    equivalent content to `pip freeze`), sorted case-insensitively."""
    code = ("import importlib.metadata as m; print('\\n'.join(sorted({f\"{d.metadata['Name']}=={d.version}\" "
            "for d in m.distributions()}, key=str.lower)))")
    return subprocess.run([str(SEA_PY), '-E', '-s', '-c', code], capture_output=True, text=True,
                          check=True).stdout.replace('\r\n', '\n')


def sea_tracked():
    head = subprocess.run(['git', '-C', str(SEA_SRC), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    files = subprocess.run(['git', '-C', str(SEA_SRC), 'ls-files', '-z'], capture_output=True, text=True).stdout.split('\0')
    return head, {f'n8_runs/sea_src/{f}': h(SEA_SRC / f) for f in files if f}


if __name__ == '__main__':
    head, sea_files = sea_tracked()
    assert head == SEA_COMMIT, head
    if SNAP.exists():
        shutil.rmtree(SNAP)
    (SNAP / 'pn8').mkdir(parents=True)
    sums = []
    for f in CODE:
        shutil.copy2(PN8 / f, SNAP / 'pn8' / f); sums.append((h(PN8 / f), f'pn8/{f}'))
    for rel in DEPS_COPY:
        dst = SNAP / 'deps' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ART / rel, dst); sums.append((h(ART / rel), f'deps/{rel}'))
    (SNAP / 'sea_env_freeze.txt').write_bytes(sea_freeze().encode())
    sums.append((h(SNAP / 'sea_env_freeze.txt'), 'sea_env_freeze.txt'))
    (SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
    files = dict(sea_files)
    for pkg in PKGS:
        for p in sorted((ART / pkg).rglob('*.py')):
            files[p.relative_to(ART).as_posix()] = h(p)
    for rel in DATA + REF5:
        files[rel] = h(ART / rel)
    versions = {}
    for p in ('avici', 'numpy', 'scipy', 'scikit-learn', 'causal-learn', 'jax', 'jaxlib'):
        try:
            versions[p] = md.version(p)
        except md.PackageNotFoundError:
            versions[p] = None
    versions['python'] = platform.python_version()
    (SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(sea_commit=head, files=files,
                                                            manifest={r: h(REPO / r) for r in REPO_FILES},
                                                            versions=versions), indent=1).encode())
    (SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
    print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes ({len(sea_files)} SEA tracked files)')
