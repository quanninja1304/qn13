"""Build the P-N6 code snapshot (rules PN6 v1 §11 step 3): code plus the dependencies it uses.

Writes reports/n6_fix_comparison_2026-11-22/code/:
  pn6/<file>                         P-N6 code (this directory)
  deps/n1_runs/pn1/common.py, metrics.py, deps/n1_runs/config/er{1,2}-{lin,rff}-gauss.yaml   frozen P-N1 (targets, F1)
  deps/n2_runs/pn2/common2.py, screen.py                                                  frozen P-N2 (padding, HSIC)
  deps/n4_runs/pn4/common4.py, selector4.py                                               frozen P-N4 (CDFM selector)
  deps/n5_runs/pn5/common5.py                                                             frozen P-N5 (real inputs)
  SHA256SUMS                         hashes of everything above (checked against live files by verify_freeze6.py)
  DEPS_SHA256.json                   hashes of the cdfm and avici package sources, the CDFM and AVICI checkpoints, the two
                                     data files, the P-N5 plain k0 outputs used for phi on the real tables, alpha6.json;
                                     plus the data manifest, the P-N5 input hashes and package versions
  .gitattributes                     byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n6_runs/pn6. Data files are hashed, never copied.
usage: freeze6.py
"""
import hashlib, json, shutil, platform
from pathlib import Path
import importlib.metadata as md

PN6 = Path(__file__).resolve().parent
ART = PN6.parents[1]
REPO = ART.parent
SNAP = REPO / 'reports' / 'n6_fix_comparison_2026-11-22' / 'code'
CODE = ['common6.py', 'run6.py', 'measures6.py', 'stats6.py', 'alpha6.py', 'analyze6.py', 'completeness6.py', 'gates6.py',
        'verify_freeze6.py', 'freeze6.py', 'run_dev6.sh', 'run_pn6.sh']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/pn1/metrics.py'] + \
            [f'n1_runs/config/er{e}-{m}-gauss.yaml' for e in (1, 2) for m in ('lin', 'rff')] + \
            ['n2_runs/pn2/common2.py', 'n2_runs/pn2/screen.py', 'n4_runs/pn4/common4.py', 'n4_runs/pn4/selector4.py',
             'n5_runs/pn5/common5.py']
PKGS = ['n1_models_cpu/repos/CDFM/src/cdfm', 'n1_models_cpu/repos/avici/avici']
CKPT = ['n1_models_cpu/checkpoints/cdfm/config.json', 'n1_models_cpu/checkpoints/cdfm/model.safetensors',
        'n1_models_cpu/checkpoints/avici/scm-v0/checkpoint_0300000.pkl', 'n1_models_cpu/checkpoints/avici/scm-v0/config.yaml',
        'n1_models_cpu/checkpoints/avici/scm-v0/kwargs.json']
DATA = ['data_real/sachs_zenodo_7681811/extracted/cd3cd28.csv', 'data_real/uci_wine_quality_186/extracted/winequality-white.csv']
REF5 = [f'n5_runs/pn5_out/{m}/{t}__k0.npz' for m in ('avici', 'cdfm') for t in ('sachs', 'wine')]
ALPHA = ['n6_runs/pn6_out/alpha6.json']
REPO_FILES = ['reports/n5_real_data_consistency_2026-11-22/manifest/data_manifest.json',
              'reports/n5_real_data_consistency_2026-11-22/checks/inputs5.json']


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if SNAP.exists():
    shutil.rmtree(SNAP)
(SNAP / 'pn6').mkdir(parents=True)
sums = []
for f in CODE:
    shutil.copy2(PN6 / f, SNAP / 'pn6' / f); sums.append((h(PN6 / f), f'pn6/{f}'))
for rel in DEPS_COPY:
    dst = SNAP / 'deps' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ART / rel, dst); sums.append((h(ART / rel), f'deps/{rel}'))
(SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
files = {}
for pkg in PKGS:
    for p in sorted((ART / pkg).rglob('*.py')):
        files[p.relative_to(ART).as_posix()] = h(p)
for rel in CKPT + DATA + REF5 + ALPHA:
    files[rel] = h(ART / rel)
versions = {p: md.version(p) for p in ('cdfm-base', 'avici', 'numpy', 'scipy', 'torch', 'jax', 'jaxlib', 'dm-haiku', 'psutil')}
versions['python'] = platform.python_version()
(SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(files=files, manifest={r: h(REPO / r) for r in REPO_FILES},
                                                        versions=versions), indent=1).encode())
(SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes')
