"""Run SEA's own inference script in-process, unchanged, and record wall time and peak working set (Windows).

usage (SEA environment): python -E -s sea_wrapper.py <sea_src dir> <inputs.csv> <results.pkl> <seed> <out json>
The FCI configuration is copied from config/aggregator_tf_fci.yaml with three keys changed: data_file, results_file
and num_workers = 0 (one process, for repeatability). Model, sampler and FCI settings are unchanged. Runs on CPU.
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import runpy
import sys
import time
from pathlib import Path

SRC, CSV, PKL, SEED, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve(), int(sys.argv[4]), Path(sys.argv[5]).resolve()
cfg_text = (SRC / 'config' / 'aggregator_tf_fci.yaml').read_text(encoding='utf-8')
cfg = []
for line in cfg_text.splitlines():
    key = line.strip().split(':', 1)[0]
    if key == 'data_file':
        line = line.split('data_file')[0] + f'data_file: "{CSV.as_posix()}"'
    elif key == 'results_file':
        line = line.split('results_file')[0] + f'results_file: "{PKL.as_posix()}"'
    elif key == 'num_workers':
        line = line.split('num_workers')[0] + 'num_workers: 0'
    cfg.append(line)
cfg_path = OUT.with_suffix('.yaml')
cfg_path.write_text('\n'.join(cfg) + '\n', encoding='utf-8')
os.chdir(SRC)
sys.path.insert(0, str(SRC / 'src'))
sys.argv = ['src/inference.py', '--config_file', str(cfg_path), '--run_name', 'sea_fci', '--gpu', '-1',
            '--checkpoint_path', 'checkpoints/fci_synthetic/model_best_epoch=373_auprc=0.842.ckpt', '--seed', str(SEED)]
t0 = time.time()
runpy.run_path(str(SRC / 'src' / 'inference.py'), run_name='__main__')
wall = time.time() - t0


class PMC(ctypes.Structure):
    _fields_ = [('cb', wt.DWORD), ('PageFaultCount', wt.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t)]


pmc = PMC()
pmc.cb = ctypes.sizeof(PMC)
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
k32.GetCurrentProcess.restype = wt.HANDLE
k32.K32GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
k32.K32GetProcessMemoryInfo.restype = wt.BOOL
ok = k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
assert ok, 'GetProcessMemoryInfo failed'
OUT.write_text(json.dumps(dict(seed=SEED, wall_s=wall, peak_wset_mb=pmc.PeakWorkingSetSize / 2 ** 20, config=cfg), indent=1), encoding='utf-8')
print(f'SEA run done: seed {SEED}, {wall:.1f} s, peak working set {pmc.PeakWorkingSetSize / 2 ** 20:.0f} MB')
