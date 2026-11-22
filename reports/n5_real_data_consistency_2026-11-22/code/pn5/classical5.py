"""P-N5 classical baselines (rules PN5 v1 §3), called exactly as in P-N1 run_classical.py and P-N2 run2_classical.py:
PC (causal-learn, Fisher-z, alpha 0.05, stable) and GES (causal-learn, Gaussian BIC), on the float64 copy of the input.

run_classical runs inside a worker process, so that the runner can stop a job at the 900 s limit.
Returns the skeleton of the output graph on the full table (every edge type), int8.
"""
import numpy as np


def skel(G):
    m = np.asarray(G.graph)
    return ((m != 0) | (m.T != 0)).astype(np.int8)


def run_classical(alg, X):
    X = np.asarray(X).astype(np.float64)
    if alg == 'pc':
        from causallearn.search.ConstraintBased.PC import pc
        return skel(pc(X, 0.05, 'fisherz', stable=True, show_progress=False).G)
    if alg == 'ges':
        from causallearn.search.ScoreBased.GES import ges
        return skel(ges(X, score_func='local_score_BIC')['G'])
    raise ValueError(alg)


def worker_peak_mb():
    """Peak working set of this worker process (Windows), for the memory record."""
    import psutil
    return round(getattr(psutil.Process().memory_info(), 'peak_wset', 0) / 2 ** 20, 1)
