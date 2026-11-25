"""Build the P-N9 / Study 8 code snapshot (rules PN9 v1 §9 step 4): code plus the dependencies it uses.

Writes reports/n9_sample_size_2026-11-24/code/:
  pn9/<file>          Study 8 code (this directory)
  deps/<path>         frozen copies used unchanged: P-N1 common.py, metrics.py, configs; P-N8 common8.py, stats8.py,
                      sea_wrapper8.py, freeze8.py; P-N7 stats7.py; P-N2 common2.py, analyze_held2.py; P-N5 common5.py
  sea_env_freeze.txt  name==version of every package of the SEA environment (frozen P-N8 function)
  SHA256SUMS          hashes of everything above (checked against live files by verify_freeze9.py)
  DEPS_SHA256.json    hashes of: the tracked files of the SEA clone (plus its commit); the model checkpoints; the sources of
                      the packages imported by the runners (resolved without importing them); the Study 1 and Study 7
                      outputs used by the G5 reproduction checks; repository files (rules, design, gate results)
  .gitattributes      byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n9_runs/pn9. Data and checkpoints are hashed, never copied.
usage (Study 1 model environment): python -I freeze9.py
"""
import importlib.util
import importlib.metadata as md
import json
import platform
import shutil
import sys
from pathlib import Path

PN9 = Path(__file__).resolve().parent
RUNS9 = PN9.parent
ART = RUNS9.parent
REPO = ART.parent
SNAP = REPO / 'reports' / 'n9_sample_size_2026-11-24' / 'code'
sys.path.insert(1, str(ART / 'n8_runs' / 'pn8'))
from freeze8 import h, sea_freeze, sea_tracked, SEA_COMMIT     # frozen P-N8

CODE = ['common9.py', 'stats9.py', 'run9.py', 'run9_sea.py', 'run9_classical.py', 'gates9.py', 'analyze9.py',
        'completeness9.py', 'selftest9.py', 'freeze9.py', 'verify_freeze9.py', 'run_dev9.sh', 'run_dev9_foundcause.ps1',
        'run_main9_short.sh', 'run_main9_long.ps1']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/pn1/metrics.py'] + \
            [f'n1_runs/config/er{e}-{m}-gauss.yaml' for e in (1, 2) for m in ('lin', 'rff')] + \
            ['n8_runs/pn8/common8.py', 'n8_runs/pn8/stats8.py', 'n8_runs/pn8/sea_wrapper8.py', 'n8_runs/pn8/freeze8.py',
             'n7_runs/pn7/stats7.py', 'n2_runs/pn2/common2.py', 'n2_runs/pn2/analyze_held2.py', 'n5_runs/pn5/common5.py']
CKPT = ['n1_models_cpu/checkpoints/avici/scm-v0', 'n1_models_cpu/checkpoints/cdfm', 'n1_models_cpu/checkpoints/foundcause']
PKGS = ('avici', 'cdfm', 'causallearn', 'jax', 'torch')
FOUNDCAUSE_SRC = 'n1_models_cpu/repos/foundcause'
G5_REF = [f'n1_runs/pn1_out/{m}/HELD-c0-r0__{t}__main.npz' for m in ('avici', 'cdfm', 'pc', 'ges') for t in ('-__k0', 'A__k20')] + \
         ['n1_runs/pn1_out/foundcause/HELD-c0-r0__-__k0__main.npz', 'n8_runs/pn8_out/sea/PN8-c0-r0__k0__s600000.npz']
REPO_FILES = ['reports/n9_sample_size_2026-11-24/PN9_rules_vi.md', 'reports/n9_sample_size_2026-11-24/PN9_n_grid_design_vi.md',
              'reports/n9_sample_size_2026-11-24/checks/gates9.json', 'reports/n9_sample_size_2026-11-24/checks/gates9_G1.json',
              'reports/n9_sample_size_2026-11-24/checks/pn9_inputs_dev.json',
              'reports/n9_sample_size_2026-11-24/checks/selftest9.json']


def pkg_files(name):
    """Source files of an importable package, located with find_spec (the package is not imported)."""
    spec = importlib.util.find_spec(name)
    root = Path(spec.submodule_search_locations[0]) if spec.submodule_search_locations else Path(spec.origin).parent
    return root, sorted(root.rglob('*.py'))


if __name__ == '__main__':
    head, sea_files = sea_tracked()
    assert head == SEA_COMMIT, head
    if SNAP.exists():
        shutil.rmtree(SNAP)
    (SNAP / 'pn9').mkdir(parents=True)
    sums = []
    for f in CODE:
        shutil.copy2(PN9 / f, SNAP / 'pn9' / f)
        sums.append((h(PN9 / f), f'pn9/{f}'))
    for rel in DEPS_COPY:
        dst = SNAP / 'deps' / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ART / rel, dst)
        sums.append((h(ART / rel), f'deps/{rel}'))
    (SNAP / 'sea_env_freeze.txt').write_bytes(sea_freeze().encode())
    sums.append((h(SNAP / 'sea_env_freeze.txt'), 'sea_env_freeze.txt'))
    (SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
    files = dict(sea_files)
    for c in CKPT:
        for p in sorted((ART / c).rglob('*')):
            if p.is_file():
                files[p.relative_to(ART).as_posix()] = h(p)
    pkg_roots = {}
    for name in PKGS:
        root, fl = pkg_files(name)
        pkg_roots[name] = root.relative_to(ART).as_posix() if root.is_relative_to(ART) else 'outside artifacts'
        for p in fl:
            try:
                rel = p.relative_to(ART).as_posix()
            except ValueError:
                rel = p.as_posix()
            files[rel] = h(p)
    for p in sorted((ART / FOUNDCAUSE_SRC).glob('*.py')):
        files[p.relative_to(ART).as_posix()] = h(p)
    for rel in G5_REF:
        files[rel] = h(ART / rel)
    versions = {}
    for p in ('avici', 'cdfm', 'numpy', 'scipy', 'scikit-learn', 'causal-learn', 'jax', 'jaxlib', 'torch', 'matplotlib'):
        try:
            versions[p] = md.version(p)
        except md.PackageNotFoundError:
            versions[p] = None
    versions['python'] = platform.python_version()
    (SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(sea_commit=head, files=files, package_roots=pkg_roots,
                                                            manifest={r: h(REPO / r) for r in REPO_FILES},
                                                            versions=versions), indent=1).encode())
    (SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
    print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes ({len(sea_files)} SEA tracked files)')
