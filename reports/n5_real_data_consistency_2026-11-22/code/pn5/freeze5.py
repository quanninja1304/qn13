"""Build the P-N5 code snapshot (rules PN5 v1 §11 step 3): code plus the dependencies it uses.

Writes reports/n5_real_data_consistency_2026-11-22/code/:
  pn5/<file>                         P-N5 code (this directory)
  deps/n1_runs/pn1/common.py         frozen P-N1 module used through common2.py (zscore, sha, cfg_path)
  deps/n1_runs/config/er2-rff-gauss.yaml   config of the DEV5 stand-in table (gates only)
  deps/n2_runs/pn2/common2.py        frozen P-N2 module (padding generator)
  SHA256SUMS                         hashes of everything above (checked against live files by verify_freeze5.py)
  DEPS_SHA256.json                   hashes of the cdfm, avici and causallearn package sources, of the CDFM and AVICI
                                     checkpoints, of the two data files and of the data manifest; package versions
  .gitattributes                     byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n5_runs/pn5. Data files are hashed, never copied.
usage: freeze5.py
"""
import hashlib, json, shutil, platform
from pathlib import Path
import importlib.metadata as md

PN5 = Path(__file__).resolve().parent
ART = PN5.parents[1]
REPO = ART.parent
SNAP = REPO / 'reports' / 'n5_real_data_consistency_2026-11-22' / 'code'
CODE = ['common5.py', 'stats5.py', 'measures5.py', 'classical5.py', 'prep5.py', 'run5.py', 'gates5.py', 'analyze5.py',
        'completeness5.py', 'verify_freeze5.py', 'freeze5.py', 'run_pn5.sh']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/config/er2-rff-gauss.yaml', 'n2_runs/pn2/common2.py']
PKGS = ['n1_models_cpu/repos/CDFM/src/cdfm', 'n1_models_cpu/repos/avici/avici', 'n1_models_cpu/.venv/Lib/site-packages/causallearn']
CKPT = ['n1_models_cpu/checkpoints/cdfm/config.json', 'n1_models_cpu/checkpoints/cdfm/model.safetensors',
        'n1_models_cpu/checkpoints/avici/scm-v0/checkpoint_0300000.pkl', 'n1_models_cpu/checkpoints/avici/scm-v0/config.yaml',
        'n1_models_cpu/checkpoints/avici/scm-v0/kwargs.json']
DATA = ['data_real/sachs_zenodo_7681811/extracted/cd3cd28.csv', 'data_real/uci_wine_quality_186/extracted/winequality-white.csv']
MANIFEST = 'reports/n5_real_data_consistency_2026-11-22/manifest/data_manifest.json'


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if SNAP.exists():
    shutil.rmtree(SNAP)
(SNAP / 'pn5').mkdir(parents=True)
sums = []
for f in CODE:
    shutil.copy2(PN5 / f, SNAP / 'pn5' / f); sums.append((h(PN5 / f), f'pn5/{f}'))
for rel in DEPS_COPY:
    dst = SNAP / 'deps' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ART / rel, dst); sums.append((h(ART / rel), f'deps/{rel}'))
(SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
files = {}
for pkg in PKGS:
    for p in sorted((ART / pkg).rglob('*.py')):
        files[p.relative_to(ART).as_posix()] = h(p)
for rel in CKPT + DATA:
    files[rel] = h(ART / rel)
versions = {p: md.version(p) for p in ('cdfm-base', 'avici', 'causal-learn', 'numpy', 'scipy', 'torch', 'jax', 'jaxlib',
                                       'dm-haiku', 'networkx', 'psutil')}
versions['python'] = platform.python_version()
(SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(files=files, manifest={MANIFEST: h(REPO / MANIFEST)},
                                                        versions=versions), indent=1).encode())
(SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes (incl. 2 data files)')
