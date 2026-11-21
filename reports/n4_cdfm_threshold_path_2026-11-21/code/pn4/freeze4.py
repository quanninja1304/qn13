"""Build the P-N4 code snapshot (rules PN4 v1 §0 step 3): code plus the dependencies it uses.

Writes reports/n4_cdfm_threshold_path_2026-11-21/code/:
  pn4/<file>                       P-N4 code (this directory)
  deps/n1_runs/pn1/common.py       frozen P-N1 module used through common2.py
  deps/n1_runs/config/er{1,2}-rff-gauss.yaml   target-generator configs of the RFF cells
  deps/n2_runs/pn2/common2.py      frozen P-N2 module (padding generator)
  SHA256SUMS                       hashes of everything above (checked against live files by verify_freeze4.py)
  DEPS_SHA256.json                 hashes of the cdfm and avici package sources and of the CDFM checkpoint
  .gitattributes                   byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n4_runs/pn4.
usage: freeze4.py
"""
import hashlib, json, shutil, platform
from pathlib import Path
import importlib.metadata as md

PN4 = Path(__file__).resolve().parent
ART = PN4.parents[1]
REPO = ART.parent
SNAP = REPO / 'reports' / 'n4_cdfm_threshold_path_2026-11-21' / 'code'
CODE = ['common4.py', 'selector4.py', 'stats4.py', 'measures4.py', 'run4.py', 'gates4.py', 'analyze4.py', 'completeness4.py',
        'verify_freeze4.py', 'freeze4.py', 'run_pn4.sh']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/config/er1-rff-gauss.yaml', 'n1_runs/config/er2-rff-gauss.yaml',
             'n2_runs/pn2/common2.py']


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if SNAP.exists():
    shutil.rmtree(SNAP)
(SNAP / 'pn4').mkdir(parents=True)
sums = []
for f in CODE:
    shutil.copy2(PN4 / f, SNAP / 'pn4' / f); sums.append((h(PN4 / f), f'pn4/{f}'))
for rel in DEPS_COPY:
    dst = SNAP / 'deps' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ART / rel, dst); sums.append((h(ART / rel), f'deps/{rel}'))
(SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
files = {}
for pkg in ('n1_models_cpu/repos/CDFM/src/cdfm', 'n1_models_cpu/repos/avici/avici'):
    for p in sorted((ART / pkg).rglob('*.py')):
        files[p.relative_to(ART).as_posix()] = h(p)
for ck in ('config.json', 'model.safetensors'):
    files[f'n1_models_cpu/checkpoints/cdfm/{ck}'] = h(ART / 'n1_models_cpu' / 'checkpoints' / 'cdfm' / ck)
versions = {p: md.version(p) for p in ('cdfm-base', 'avici', 'numpy', 'scipy', 'torch', 'psutil')}
versions['python'] = platform.python_version()
(SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(files=files, versions=versions), indent=1).encode())
(SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes')
