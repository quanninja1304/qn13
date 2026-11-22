"""Build the P-N7 code snapshot (rules PN7 v1 §10 step 3): code plus the dependencies it uses.

Writes reports/n7_foundcause_real_tables_2026-11-22/code/:
  pn7/<file>                     P-N7 code (this directory)
  deps/n1_runs/pn1/common.py, metrics.py, fc_adapter.py, deps/n1_runs/config/er{1,2}-{lin,rff}-gauss.yaml   frozen P-N1
  deps/n2_runs/pn2/common2.py    frozen P-N2 (padding generator used by common5)
  deps/n5_runs/pn5/common5.py    frozen P-N5 (real-table and DEV5 stand-in inputs)
  SHA256SUMS                     hashes of everything above (checked against live files by verify_freeze7.py)
  DEPS_SHA256.json               hashes of the foundcause and avici package sources, the FoundCause checkpoint, the two data
                                 files, the P-N5 outputs used as comparators (PC, GES) and for description (AVICI, CDFM),
                                 the P-N5 reading and DEV5 log, the P-N1 DEV output and log used by G2; plus the data
                                 manifest, the P-N5 input hashes, the checkpoint manifest and package versions
  .gitattributes                 byte-exact snapshot (* -text)
The snapshot is a reference copy; code runs from artifacts/n7_runs/pn7. Data files are hashed, never copied.
usage: freeze7.py
"""
import hashlib, json, shutil, platform
from pathlib import Path
import importlib.metadata as md

PN7 = Path(__file__).resolve().parent
ART = PN7.parents[1]
REPO = ART.parent
SNAP = REPO / 'reports' / 'n7_foundcause_real_tables_2026-11-22' / 'code'
CODE = ['common7.py', 'run7.py', 'stats7.py', 'analyze7.py', 'completeness7.py', 'gates7.py', 'verify_freeze7.py',
        'freeze7.py', 'run_dev7.sh', 'run_pn7.sh']
DEPS_COPY = ['n1_runs/pn1/common.py', 'n1_runs/pn1/metrics.py', 'n1_runs/pn1/fc_adapter.py'] + \
            [f'n1_runs/config/er{e}-{m}-gauss.yaml' for e in (1, 2) for m in ('lin', 'rff')] + \
            ['n2_runs/pn2/common2.py', 'n5_runs/pn5/common5.py']
PKGS = ['n1_models_cpu/repos/foundcause', 'n1_models_cpu/repos/avici/avici']
CKPT = ['n1_models_cpu/checkpoints/foundcause/checkpoint.pt']
DATA = ['data_real/sachs_zenodo_7681811/extracted/cd3cd28.csv', 'data_real/uci_wine_quality_186/extracted/winequality-white.csv']
REF5 = [f'n5_runs/pn5_out/{a}/{t}__k0.npz' for a in ('pc', 'ges', 'avici', 'cdfm') for t in ('sachs', 'wine', 'standin')] + \
       [f'n5_runs/pn5_out/{a}/{t}__k20_e0__r{r:02d}.npz' for a in ('pc', 'ges', 'avici', 'cdfm') for t in ('sachs', 'wine')
        for r in range(20)] + \
       [f'n5_runs/pn5_out/{a}/standin__k20_e0__r{r:02d}.npz' for a in ('pc', 'ges', 'avici', 'cdfm') for r in range(2)] + \
       ['n5_runs/pn5_out/pn5_reading.json', 'n5_runs/pn5_out/avici/log_DEV5.jsonl']
REF1 = ['n1_runs/pn1_out/foundcause/DEV-c0-r0__-__k0__main.npz', 'n1_runs/pn1_out/foundcause/log_dev.jsonl']
REPO_FILES = ['reports/n5_real_data_consistency_2026-11-22/manifest/data_manifest.json',
              'reports/n5_real_data_consistency_2026-11-22/checks/inputs5.json',
              'reports/direction_scan_2026-11-13/n1_checkpoint_manifest.json']


def h(p):
    d = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 22), b''):
            d.update(chunk)
    return d.hexdigest()


if SNAP.exists():
    shutil.rmtree(SNAP)
(SNAP / 'pn7').mkdir(parents=True)
sums = []
for f in CODE:
    shutil.copy2(PN7 / f, SNAP / 'pn7' / f); sums.append((h(PN7 / f), f'pn7/{f}'))
for rel in DEPS_COPY:
    dst = SNAP / 'deps' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ART / rel, dst); sums.append((h(ART / rel), f'deps/{rel}'))
(SNAP / 'SHA256SUMS').write_bytes(''.join(f'{d} *{r}\n' for d, r in sums).encode())
files = {}
for pkg in PKGS:
    for p in sorted((ART / pkg).rglob('*.py')):
        files[p.relative_to(ART).as_posix()] = h(p)
for rel in CKPT + DATA + REF5 + REF1:
    files[rel] = h(ART / rel)
versions = {}
for p in ('avici', 'numpy', 'scipy', 'torch', 'jax', 'jaxlib', 'dm-haiku', 'psutil'):
    try:
        versions[p] = md.version(p)
    except md.PackageNotFoundError:
        versions[p] = None
versions['python'] = platform.python_version()
(SNAP / 'DEPS_SHA256.json').write_bytes(json.dumps(dict(files=files, manifest={r: h(REPO / r) for r in REPO_FILES},
                                                        versions=versions), indent=1).encode())
(SNAP / '.gitattributes').write_bytes(b'# Byte-exact snapshot: SHA256SUMS must verify after clone on any OS.\n* -text\n')
print(f'snapshot: {len(sums)} files in SHA256SUMS, {len(files)} dependency hashes')
