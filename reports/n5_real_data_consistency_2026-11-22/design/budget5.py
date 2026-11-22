"""P-N5 budget measurement on a synthetic stand-in table (no real data are read; no output is used for any decision except cost).

Stand-in: an ER-RFF system with d = 11 (P-N1 config er2-rff-gauss.yaml, seed 999000), n = 500, z-scored; padding from the
frozen P-N2 generator at k = 20 and 40, e = 0 (Gaussian) and e = 2 (structured), seed 999000. Times one run per input.
usage: budget5.py <avici|cdfm|pc|ges>  ->  appends to n5_runs/pn5_out/budget5.jsonl
"""
import os, sys, time, json
T = '2'
for v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[v] = T
os.environ.update(JAX_PLATFORMS='cpu', CUDA_VISIBLE_DEVICES='-1', TF_CPP_MIN_LOG_LEVEL='2', HF_HUB_OFFLINE='1',
                  XLA_FLAGS=f'--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads={T}')
from pathlib import Path
HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]
sys.path.insert(0, str(ART / 'n2_runs' / 'pn2'))
if os.name == 'nt':
    import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
import numpy as np
import psutil
from common2 import zscore, pad_params, pad_graph, pad_data
from common import cfg_path

model = sys.argv[1]
OUT = HERE.parent / 'pn5_out'; OUT.mkdir(parents=True, exist_ok=True)
from avici import simulate_data
g, x, _ = simulate_data(d=11, n=500, seed=999000, path=str(cfg_path(2, 'rff')))
x0 = zscore(x)
inputs = {'k0': x0}
for k in (20, 40):
    P = pad_params(999000, 'rff', k=k)
    for e in (0, 2):
        pad = zscore(pad_data(P, pad_graph(P, float(e), k=k), 'rff', 1.0))
        inputs[f'k{k}_e{e}'] = zscore(np.concatenate([x0, pad], 1))

if model == 'avici':
    import avici
    m = avici.load_pretrained(checkpoint_dir=str(ART / 'n1_models_cpu' / 'checkpoints/avici/scm-v0'), expects_counts=False)
    fn = lambda X: m(x=X)
elif model == 'cdfm':
    import torch; torch.set_num_threads(2)
    from cdfm import CDFM
    m = CDFM.from_pretrained(str(ART / 'n1_models_cpu' / 'checkpoints/cdfm'), device='cpu', threshold=None)
    fn = lambda X: m.predict(X, threshold=None, standardize=False)
elif model == 'pc':
    from causallearn.search.ConstraintBased.PC import pc
    fn = lambda X: pc(X.astype(np.float64), 0.05, 'fisherz', stable=True, show_progress=False)
else:
    from causallearn.search.ScoreBased.GES import ges
    fn = lambda X: ges(X.astype(np.float64), score_func='local_score_BIC')
proc = psutil.Process()
with open(OUT / 'budget5.jsonl', 'a', encoding='utf-8') as log:
    for name, X in inputs.items():
        t0 = time.perf_counter(); fn(X); dt = time.perf_counter() - t0
        rec = dict(model=model, input=name, D=int(X.shape[1]), seconds=round(dt, 2),
                   peak_wset_mb=round(getattr(proc.memory_info(), 'peak_wset', 0) / 2 ** 20, 1))
        log.write(json.dumps(rec) + '\n'); log.flush()
        print(json.dumps(rec), flush=True)
