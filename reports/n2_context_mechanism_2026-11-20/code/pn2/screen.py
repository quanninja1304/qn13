"""P-N2 R arm (rules v1 §8): pairwise marginal dependence p-values, Bonferroni/BH decisions, components, screening metrics.

HSIC reproduces causal-learn KCI_UInd(kernelX='Gaussian', kernelY='Gaussian', approx=True, est_width='median'):
  width from the data as given (median heuristic, sqrt(2) * median distance), then z-score with ddof=1, then the kernel;
  statistic sum(Kxc * Kyc); gamma parameters from trace and sum of squares of the centered kernels.
The only intended difference: the tail is computed with gamma.sf instead of 1 - gamma.cdf (rules v1 §8.1).
"""
import numpy as np
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import connected_components


def p_fisherz(X):
    X = np.asarray(X, np.float64)
    n = X.shape[0]
    r = np.corrcoef(X.T)
    np.fill_diagonal(r, 0.0)
    r = np.clip(r, -1 + 1e-15, 1 - 1e-15)
    z = np.arctanh(r) * np.sqrt(n - 3)
    p = 2 * stats.norm.sf(np.abs(z))
    np.fill_diagonal(p, 1.0)
    return p


def p_spearman(X):
    X = np.asarray(X, np.float64)
    if X.shape[1] == 2:
        _, p0 = stats.spearmanr(X[:, 0], X[:, 1])
        p = np.array([[1.0, p0], [p0, 1.0]])
    else:
        _, p = stats.spearmanr(X)
        p = np.array(p, np.float64)
    np.fill_diagonal(p, 1.0)
    return p


def _centered_kernel(col):
    """Centered Gaussian kernel of one variable, exactly as KCI_UInd.kernel_matrix + HSIC_V_statistic."""
    x = col.reshape(-1, 1)
    dists = squareform(pdist(x, 'euclidean'))
    med = np.median(dists[dists > 0])
    theta = 1.0 / (np.sqrt(2.0) * med) ** 2
    xz = stats.zscore(x, ddof=1, axis=0)
    xz[np.isnan(xz)] = 0.0
    K = np.exp(-0.5 * squareform(pdist(xz, 'sqeuclidean')) * theta)
    n = K.shape[0]
    cs = K.sum(axis=0)
    return K - (cs[None, :] + cs[:, None]) / n + (cs.sum() / n ** 2)


def p_hsic(X, return_stat=False):
    X = np.asarray(X, np.float64)
    n, D = X.shape
    F = np.empty((D, n * n))
    tr = np.empty(D)
    s2 = np.empty(D)
    for i in range(D):
        Kc = _centered_kernel(X[:, i])
        F[i] = Kc.ravel()
        tr[i] = np.trace(Kc)
        s2[i] = np.sum(Kc ** 2)
    V = F @ F.T
    mean = np.outer(tr, tr) / n
    var = 2 * np.outer(s2, s2) / n / n
    k_appr = mean ** 2 / var
    theta = var / mean
    p = stats.gamma.sf(V, k_appr, loc=0, scale=theta)
    np.fill_diagonal(p, 1.0)
    return (p, V) if return_stat else p


def pvalues(X, test):
    return {'fisherz': p_fisherz, 'hsic': p_hsic, 'spearman': p_spearman}[test](X)


def upper(p):
    iu = np.triu_indices(p.shape[0], 1)
    return iu, p[iu]


def reject_bonferroni(p, alpha):
    D = p.shape[0]
    m = D * (D - 1) // 2
    R = (p < alpha / m)
    np.fill_diagonal(R, False)
    return R | R.T


def reject_bh(p, q):
    iu, pv = upper(p)
    m = len(pv)
    order = np.argsort(pv, kind='stable')
    ok = pv[order] <= q * np.arange(1, m + 1) / m
    R = np.zeros_like(p, bool)
    if ok.any():
        cut = pv[order][np.nonzero(ok)[0].max()]
        sel = pv <= cut
        R[iu[0][sel], iu[1][sel]] = True
    return R | R.T


def components(R):
    _, lab = connected_components(R.astype(np.int8), directed=False)
    return lab


def screen_metrics(lab, R, dT, gT):
    """Rules v1 §8.3. gT: [dT, dT] target DAG adjacency."""
    D = len(lab)
    k = D - dT
    tlabs = set(lab[:dT].tolist())
    merged = int(sum(1 for v in range(dT, D) if lab[v] in tlabs))
    sk = (gT + gT.T) > 0
    iu = np.triu_indices(dT, 1)
    split = int(sum(1 for a, b in zip(*iu) if sk[a, b] and lab[a] != lab[b]))
    false_cross = int(R[:dT, dT:].sum()) if k > 0 else 0
    return dict(merged=merged, split=split, false_cross=false_cross, n_target_components=len(tlabs),
                n_true_edges=int(sk[iu].sum()), k=k)


def screen(X, test, alpha, dT, gT, method='bonferroni'):
    p = pvalues(X, test)
    R = reject_bonferroni(p, alpha) if method == 'bonferroni' else reject_bh(p, alpha)
    lab = components(R)
    return dict(p=p, R=R, lab=lab, **screen_metrics(lab, R, dT, gT))
