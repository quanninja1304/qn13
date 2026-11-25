"""P-N9 / Study 8 development gates (rules PN9 v1 §6; feasibility only). No metric of §3 is read on DEV data.

usage (Study 1 model environment):
  python -I gates9.py G1     data gate, before any model run: inputs of the 16 DEV systems at every level of the union
                             grid are built twice in this process (caches cleared in between) and once by an independent
                             recomputation; target block identical between k0 and A20; hashes saved for later
                             cross-process comparison with the runners' records
  python -I gates9.py all    G1-G6 after the DEV runs; writes reports/n9_sample_size_2026-11-24/checks/gates9.json
"""
import sys
import json
import math
import re
import statistics as stt
import subprocess
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common9 import *

CHECKS = REPORT / 'checks'
CHECKS.mkdir(parents=True, exist_ok=True)
UNION = tuple(sorted(set().union(*GRIDS.values())))
EST8 = {'avici': 1.4, 'cdfm': 6.0, 'foundcause': 59.0, 'sea': 29.0, 'ges': 1.2, 'pc': 0.5}   # rules §8 (hours)
TOTAL8 = 97.0


def g1():
    rec = {}
    sys_list = systems9('DEV9')
    for pass_ in (1, 2):
        clear_caches()
        for sysid, ci, sseed, i in sys_list:
            for n in UNION:
                d = inputs_at(sysid, ci, sseed, n)            # asserts the target block is bitwise identical
                for cond in ('k0', 'A20'):
                    k = key_of(sysid, n, cond)
                    rec.setdefault(k, []).append(sha(d[cond]))
                rec.setdefault(f'{sysid}__meta', [dict(seed_used=d['seed_used'], rejected=d['rejected'], dT=d['dT'])])
    # independent recomputation of the z-score sequence with explicit prefixes of the generated arrays
    indep_ok = True
    for sysid, ci, sseed, i in sys_list:
        t, p = target_raw(sysid, ci, sseed), padding_raw(sysid, sseed)
        full_t, full_p = t['x'].copy(), p.copy()
        for n in UNION:
            assert np.array_equal(full_t[:n], t['x'][:n]) and np.array_equal(full_p[:n], p[:n])
            tx = zscore(full_t[:n])
            k0 = zscore(tx)
            a20 = zscore(np.concatenate([tx, zscore(full_p[:n])], 1))
            indep_ok &= sha(k0) == rec[key_of(sysid, n, 'k0')][0] and sha(a20) == rec[key_of(sysid, n, 'A20')][0]
    repro = all(len(v) == 2 and v[0] == v[1] for k, v in rec.items() if not k.endswith('__meta'))
    shas = {k: v[0] for k, v in rec.items() if not k.endswith('__meta')}
    meta = {k[:-6]: v[0] for k, v in rec.items() if k.endswith('__meta')}
    res = dict(pass_=bool(repro and indep_ok), rebuild_identical=bool(repro), independent_recomputation=bool(indep_ok),
               target_block_identical='asserted for every input', n_inputs=len(shas), levels=list(UNION),
               rejections={s: m['rejected'] for s, m in meta.items() if m['rejected']})
    (CHECKS / 'pn9_inputs_dev.json').write_text(json.dumps(dict(shas=shas, meta=meta), indent=1))
    return res


def logs(model):
    out = []
    for f in sorted(OUT9.glob(f'log_{model}_*.jsonl')):
        out += [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()]
    return out


def arrays_equal(z1, z2, skip=('meta', 'perm')):
    k1, k2 = set(z1.files) - set(skip), set(z2.files) - set(skip)
    return k1 == k2 and all(np.array_equal(z1[k], z2[k]) for k in k1)


def npz(path):
    return np.load(path, allow_pickle=False) if Path(path).exists() else None


def study1_times():
    """Study 1 held-out per-call times for FoundCause at n = 500, by table width (used with the gate times in G4)."""
    rx = re.compile(r'^\[(\d+)/(\d+)\]\s+(\S+)\s+d=(\d+)\s+([\d.]+)s ok')
    t, sec = {}, None
    for raw in open(ART / 'n1_runs' / 'pn1_out' / 'held_console.log', encoding='utf-8-sig', errors='replace'):
        if raw.startswith('=== '):
            sec = raw.split()[1]
            continue
        m = rx.match(raw.strip())
        if m and sec == 'FoundCause':
            t.setdefault(int(m.group(4)), []).append(float(m.group(5)))
    return {d: stt.median(v) for d, v in t.items()}


def gate_all():
    G = {}
    G['G1'] = json.loads((CHECKS / 'gates9_G1.json').read_text())
    shas = json.loads((CHECKS / 'pn9_inputs_dev.json').read_text())['shas']
    cross = []
    for m in ALL:
        for r in logs(m):
            if r.get('status') == 'ok' and r.get('set') == 'DEV9' and r.get('role') in ('main', 'ref', 'rerun', 'mem', 'zerodag'):
                k = key_of(r['sysid'], r['n'], r['cond'])
                cross.append(shas.get(k) == r['input_sha'])
    G['G1']['cross_process_input_hashes'] = dict(n=len(cross), all_equal=bool(cross) and all(cross))
    G['G1']['pass_'] = bool(G['G1']['pass_'] and cross and all(cross))
    # G2: rerun in a fresh process gives an identical output
    g2 = {}
    for m in ALL:
        t, sp = dev_jobs(m)
        rr = next(j for j in sp if j['gate'] == 'G2')
        z1, z2 = npz(out_path(m, rr['of'])), npz(out_path(m, rr['key']))
        g2[m] = None if z1 is None or z2 is None else bool(arrays_equal(z1, z2))
    G['G2'] = dict(pass_=all(v is True for v in g2.values()), by_model=g2)
    # G3: peak working set at the largest n on a D = 40 input
    g3 = {}
    for m in G3_N:
        mem = next(j for j in dev_jobs(m)[1] if j['gate'] == 'G3')
        z = npz(out_path(m, mem['key']))
        if z is None:
            g3[m] = dict(n=G3_N[m], peak_mb=None, ok=None)
            continue
        meta = json.loads(str(z['meta']))
        g3[m] = dict(n=G3_N[m], D=meta['D'], peak_mb=meta['peak_wset_mb'], ok=bool(meta['peak_wset_mb'] <= MEM_LIMIT_MB))
    G['G3'] = dict(pass_=all(v['ok'] is True for v in g3.values()), limit_mb=MEM_LIMIT_MB, by_model=g3,
                   fallbacks_needed=[m for m, v in g3.items() if v['ok'] is False])
    # G4: time estimate of the main runs from the DEV timings
    fc500 = study1_times()
    g4, prop = {}, {}
    for m in ALL:
        tm = {}
        for r in logs(m):
            if r.get('status') == 'ok' and r.get('set') == 'DEV9' and r.get('role') in ('main', 'ref', 'rerun'):
                sec = r['wall_total_s'] if m == 'sea' else r['runtime_s']
                tm.setdefault((r['n'], r['D']), []).append(float(sec))
        med = {k: stt.median(v) for k, v in tm.items()}
        gate500 = {}                                   # FoundCause at n = 500: times measured at this gate (G3, REPRO)
        if m == 'foundcause':
            for r in logs(m):
                if r.get('status') == 'ok' and r.get('role') in ('mem', 'repro1') and r['rows'] == 500:
                    gate500[r['D']] = float(r['runtime_s'])
            slow = max((v / fc500[d] for d, v in gate500.items()), default=1.0)   # other widths: Study 1 median x this

        def est(n, D):
            if (n, D) in med:
                return med[(n, D)], 'dev'
            if m == 'foundcause' and n == 500:
                return (gate500[D], 'gate_n500') if D in gate500 else (fc500[D] * max(1.0, slow), 'study1_scaled')
            same_d = sorted((nn, v) for (nn, dd), v in med.items() if dd == D)
            if m == 'sea' and same_d:
                return max(v for _, v in same_d), 'sea_max_measured'
            if same_d:   # nearest measured level, scaled linearly in n (conservative above, exact below)
                nn, v = min(same_d, key=lambda x: abs(math.log(x[0] / n)))
                return v * max(1.0, n / nn), f'scaled_from_n{nn}'
            return None, 'missing'
        runs = {}
        sources = {}
        for run in RUN_CELLS:
            tot = 0.0
            for j in run_jobs(m, run):
                D = (CELLS[j['ci']][0] + (K if j['cond'] == 'A20' else 0))
                v, src = est(j['n'], D)
                sources[src] = sources.get(src, 0) + 1
                tot += v if v is not None else float('nan')
            runs[run] = tot / 3600
        g4[m] = dict(runs_h=runs, total_h=sum(v for v in runs.values()), sources=sources, estimate_rules_h=EST8[m])
        if m == 'foundcause':
            g4[m].update(gate_n500_s=gate500, study1_n500_median_s=fc500, slowdown_vs_study1=slow)
        prop[m] = {run: (math.ceil(15 * h) / 10 if h > 0 else 0.0) for run, h in runs.items()}   # 1.5 x, rounded up 0.1 h
    total = sum(v['total_h'] for v in g4.values())
    G['G4'] = dict(pass_=bool(total <= 1.5 * TOTAL8), total_h=total, limit_h=1.5 * TOTAL8, by_model=g4,
                   proposed_BUDGET_H=prop, note='if pass_ is false: report to the user before any main run (rules §6)')
    # G5: adapters
    g5 = {}
    for m in MODELS + CLASSICAL:
        eq = {}
        for j in repro1_jobs(m):
            z_new, z_old = npz(out_path(m, j['key'])), npz(OUT1 / m / f"{j['of']}.npz")
            eq[j['key']] = None if z_new is None or z_old is None else bool(arrays_equal(z_new, z_old))
        sane = True
        if m in MODELS:
            for f in (OUT9 / m).glob('DEV9-*.npz'):
                z = np.load(f, allow_pickle=False)
                p = z['probs']
                sane &= p.ndim == 2 and p.shape[0] == p.shape[1] and bool(np.isfinite(p).all()) and p.min() >= 0 and p.max() <= 1
        g5[m] = dict(reproduces_study1=eq, outputs_sane=bool(sane))
    sea_recs = [r for r in logs('sea') if r.get('status') == 'ok']
    zd = next(j for j in dev_jobs('sea')[1] if j['gate'] == 'G5')
    z0, zz = npz(out_path('sea', zd['of'])), npz(out_path('sea', zd['key']))
    r8 = repro8_job()
    zn, zo = npz(out_path('sea', r8['key'])), npz(OUT8 / 'sea' / f"{r8['of']}.npz")
    g5['sea'] = dict(layout_ok_all=all(r.get('layout_ok') is True for r in sea_recs),
                     auc_ok_never_false=all(r.get('auc_ok') is not False for r in sea_recs), n_outputs=len(sea_recs),
                     zero_dag_identical=None if z0 is None or zz is None else bool(np.array_equal(z0['prob'], zz['prob'])),
                     reproduces_study7=None if zn is None or zo is None else bool(np.array_equal(zn['prob'], zo['prob'])))
    ok5 = all(all(v is True for v in g5[m]['reproduces_study1'].values()) and g5[m]['outputs_sane'] for m in MODELS + CLASSICAL)
    ok5 &= all(g5['sea'][k] is True for k in ('layout_ok_all', 'auc_ok_never_false', 'zero_dag_identical', 'reproduces_study7'))
    G['G5'] = dict(pass_=bool(ok5), by_model=g5)
    # G6: reading code in structure-only mode on the DEV outputs
    p = subprocess.run([sys.executable, '-I', str(HERE / 'analyze9.py'), 'DEV9', '--structure-only'], capture_output=True,
                       text=True)
    G['G6'] = dict(pass_=p.returncode == 0, returncode=p.returncode, stdout=p.stdout[-4000:], stderr=p.stderr[-2000:])
    G['all_pass'] = all(G[g]['pass_'] for g in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6'))
    (CHECKS / 'gates9.json').write_text(json.dumps(G, indent=1, default=str))
    return G


if __name__ == '__main__':
    if sys.argv[1] == 'G1':
        r = g1()
        (CHECKS / 'gates9_G1.json').write_text(json.dumps(r, indent=1))
        print(json.dumps(r, indent=1))
        sys.exit(0 if r['pass_'] else 1)
    G = gate_all()
    print(json.dumps({g: G[g]['pass_'] for g in ('G1', 'G2', 'G3', 'G4', 'G5', 'G6')}, indent=1))
    print('all_pass:', G['all_pass'])
    sys.exit(0 if G['all_pass'] else 1)
