"""Test of recheck9.py on synthetic data, before any P-N9 output was read. No P-N9 output is read here.

Part A, agreement: the six synthetic scenarios of the frozen selftest9.py (its generator and its driver, used unchanged).
  For each, synthetic outputs are written with full metadata and with input hashes from the frozen common9.inputs_at on a
  fake target block; the frozen analyze9.py reads them through the selftest9 driver (redirected paths, fake graphs); then
  recheck9 reads them again, rebuilding every input from the rules: every check must pass and every entry must agree.
Part B, faults: on one scenario, injected faults (in analyze9's reading file, in the outputs, in the figures and in the
  rebuilt inputs) must each be caught.
Runs at idle priority. Writes synthetic data under the scratch folder given as argv[1] and the result to
test_recheck9.json next to this file.
usage (Study 1 model environment): python -I test_recheck9.py <scratch dir>
"""
import copy
import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
PN9 = HERE.parents[2] / 'artifacts' / 'n9_runs' / 'pn9'
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)   # IDLE, inherited by children
sys.path.insert(0, str(PN9))
sys.path.insert(0, str(HERE))
import selftest9 as ST                     # frozen; without '--drive' importing it only defines functions and constants
import common9 as C
import recheck9 as RC

ROOT = Path(sys.argv[1]) / 'recheck9'
if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
RUN_OF = {0: 'R1', 2: 'R1', 1: 'R2', 3: 'R2', 4: 'R3', 6: 'R3', 5: 'R4', 7: 'R4'}
LEVELS = sorted({n for g in C.GRIDS.values() for n in g})
OUT = None


def fake_x(s, dT):
    return np.random.default_rng([s, 99]).standard_normal((C.NMAX, dT))


C.target_raw = lambda sysid, ci, seed: dict(g=np.zeros((C.CELLS[ci][0],) * 2, np.int8), x=fake_x(seed, C.CELLS[ci][0]),
                                            seed_used=seed, rejected=[])
t0 = time.time()
SHA = {}
for sysid, c, r, i, s in RC.systems():
    for n in LEVELS:
        d = C.inputs_at(sysid, c, s, n)    # frozen input builder on the fake target block
        SHA[(sysid, n, 'k0')], SHA[(sysid, n, 'A20')] = C.sha(d['k0']), C.sha(d['A20'])
    C.clear_caches()
print(f'input hashes from the frozen builder: {len(SHA)} in {time.time() - t0:.0f} s', flush=True)


def write_full(model, k, rec, **arrays):
    """selftest9's synthetic outputs with the full metadata of a main-run output."""
    parts = k.split('__')
    sysid, n, cond = parts[0], int(parts[1][1:]), parts[2]
    c, r = int(sysid.split('-')[1][1:]), int(sysid.split('-')[2][1:])
    dT = C.CELLS[c][0]
    meta = dict(rec, key=k, model=model, sysid=sysid, ci=c, r=r, i=15 * c + r, sys_seed=730000 + 1000 * c + r, n=n, cond=cond,
                rows=n, D=dT + (C.K if cond == 'A20' else 0), dT=dT, status='ok', set='PN9', mode=RUN_OF[c],
                input_sha=SHA[(sysid, n, cond)])
    if model == 'sea':
        meta.update(seed=int(parts[3][1:]), level=C.GRIDS['sea'].index(n), layout_ok=True, auc_ok=True)
    else:
        meta.update(seed_used=730000 + 1000 * c + r, rejected=[])
    f = OUT / model / f'{k}.npz'
    f.parent.mkdir(parents=True, exist_ok=True)
    C.save_npz(f, meta=np.array(json.dumps(meta)), **arrays)


ST.write = write_full


def generator_for(G, shift=0):
    def gen(c, s):
        sysid = f'PN9-c{c}-r{s - 730000 - 1000 * c}'
        return G[sysid].astype(np.int8), fake_x(s + shift, C.CELLS[c][0]), s, []
    return gen


results = dict(agreement={}, faults={})


def scenario(k, name):
    """Part A for one scenario; returns (folder, graphs)."""
    global OUT
    t1 = time.time()
    tmp = ROOT / f'reading_{name}'
    OUT = tmp / 'pn9_out'
    ST.OUT = OUT
    (tmp / 'report' / 'checks').mkdir(parents=True)
    G = ST.make_graphs(100 + k)
    ST.build_outputs(name, 200 + k, G)
    np.savez(tmp / 'graphs.npz', **G)
    (tmp / 'report' / 'checks' / 'pn9_completeness.json').write_text(json.dumps(dict(ok=True)))
    cfg = dict(tmp=str(tmp), base=ST.BASE, reps=15, off=0, graphs=str(tmp / 'graphs.npz'))
    p = ST.drive('analyze9.py', cfg, 'PN9')
    if p.returncode != 0:
        results['agreement'][name] = dict(ok=False, analyze9_failed=p.stderr[-1500:])
        print('FAIL', name, 'analyze9 did not run', p.stderr[-800:], flush=True)
        return tmp, G
    r = RC.run(OUT, tmp / 'report' / 'checks', tmp / 'figures', generator=generator_for(G), check_inputs=True)
    got = r['recheck']['labels']
    miss = {t: (got.get(t), v) for t, v in ST.EXPECT[name].items()
            if (got.get(t) if t in ('A1', 'C1', 'S1') else set(got.get(t) or [])) != (v if t in ('A1', 'C1', 'S1') else {v})}
    results['agreement'][name] = dict(ok=r['ok'], n_outputs=sum(r['checks']['outputs_read'].values()),
                                      n_compared=r['comparison']['n_compared'], n_mismatches=r['comparison']['n_mismatches'],
                                      n_problems=r['checks']['n_problems'],
                                      first=(r['checks']['problems'] + r['comparison']['mismatches'])[:3],
                                      labels=got, planned_labels_missed=miss, seconds=round(time.time() - t1))
    print(('PASS ' if r['ok'] else 'FAIL ') + name, json.dumps(results['agreement'][name])[:600], flush=True)
    return tmp, G


names = list(ST.EXPECT)
tmp, G = scenario(names.index('effects'), 'effects')

# ---------------------------------------------------------------- part B: faults on the 'effects' scenario (run first)
OUT = tmp / 'pn9_out'
CHK, FIG = tmp / 'report' / 'checks', tmp / 'figures'
JF = CHK / 'pn9_reading.json'
J0 = JF.read_text()


def case(name, want_text, mutate_json=None, mutate_files=None, **kw):
    J = json.loads(J0)
    undo = None
    if mutate_json:
        mutate_json(J)
        JF.write_text(json.dumps(J))
    if mutate_files:
        undo = mutate_files()
    try:
        r = RC.run(OUT, CHK, FIG, generator=kw.pop('generator', generator_for(G)), check_inputs=True, **kw)
    finally:
        JF.write_text(J0)
        if undo:
            undo()
    msgs = r['checks']['problems'] + r['comparison']['mismatches']
    good = r['ok'] is False and any(want_text in x for x in msgs)
    results['faults'][name] = dict(caught=good, n_messages=len(msgs), first=msgs[:2])
    print(('PASS ' if good else 'FAIL ') + 'fault: ' + name, json.dumps(results['faults'][name])[:400], flush=True)


def bump(path, rel=1e-6):
    def f(J):
        o = J
        for p in path[:-1]:
            o = o[p]
        o[path[-1]] = o[path[-1]] * (1 + rel) + (rel if o[path[-1]] == 0 else 0)
    return f


def setv(path, v):
    def f(J):
        o = J
        for p in path[:-1]:
            o = o[p]
        o[path[-1]] = v(o[path[-1]]) if callable(v) else v
    return f


def file_fault(model, key_, how):
    def f():
        p = OUT / model / f'{key_}.npz'
        keep_ = p.read_bytes()
        with np.load(p, allow_pickle=False) as z:
            o = {a: z[a] for a in z.files}
        if how == 'delete':
            p.unlink()
        else:
            how(o)
            C.save_npz(p, **o)
        return lambda: p.write_bytes(keep_)
    return f


def meta_edit(**kv):
    def h(o):
        m = json.loads(str(o['meta']))
        m.update(kv)
        o['meta'] = np.array(json.dumps(m))
    return h


def nan_probs(o):
    o['probs'] = o['probs'].copy()
    o['probs'][0, 1] = np.nan


def rename_adj(o):
    o['adj'] = o.pop('adj_native')


def flip_pair(o):
    """Switch the target-block pair (0, 1) of a native CDFM skeleton: on -> off, off -> on."""
    a = o['adj_native'].copy()
    on = a[0, 1] != 0 or a[1, 0] != 0
    a[0, 1] = a[1, 0] = 0
    if not on:
        a[0, 1] = 1
    o['adj_native'] = a


def drop_figure():
    f = FIG / 'pn9_fig_flips.pdf'
    keep_ = f.read_bytes()
    f.unlink()
    return lambda: f.write_bytes(keep_)


def other_padding():
    old = RC.PAD_TAG
    RC.PAD_TAG = (20261125, 8)

    def undo():
        RC.PAD_TAG = old
    return undo


case('p of C1', 'C1.p', bump(['components', 'C1', 'p']))


def wrong_margin_sign(J):          # C2s with H0 beta >= +c instead of beta >= -c: both p tiny when the slope is steep
    r = J['components']['C2s']['res']
    J['components']['C2s']['p'] = float(stats.t.cdf((r['theta'] - J['margins']['c_C']) / r['se'], r['df']))


def two_sided_s1(J):               # S1 two-sided instead of one-sided
    J['components']['S1']['p'] = min(1.0, 2 * J['components']['S1']['p'])


case('p of C2s with the margin of the wrong sign', 'C2s.p', wrong_margin_sign)
case('p of S1 two-sided', 'S1.p', two_sided_s1)
case('Holm decision of A1', 'A1.holm.rejected', setv(['components', 'A1', 'holm', 'rejected'], lambda v: not v))
case('label S2', 'labels.S2', setv(['labels', 'S2'], 'SHRINKS + STABLE'))
case('label A1', 'labels.A1', setv(['labels', 'A1'], 'PRESENT_BELOW_MARGIN'))
case('label A2', 'labels.A2', setv(['labels', 'A2'], 'UNCLEAR'))
case('theta of a descriptive entry', 'descriptive.avici.200.H.theta', bump(['descriptive', 'avici', '200', 'H', 'theta']))
case('SE of C2t at n = 1000', 'C2t.res_by_level.1000.se', bump(['components', 'C2t', 'res_by_level', '1000', 'se']))
case('count of FoundCause at n = 125', 'counts.foundcause.125', setv(['counts', 'foundcause', '125'], lambda v: v - 1))
case('rho of CDFM', 'rho.cdfm[0][1]', setv(['rho', 'cdfm', 0, 1], lambda v: v + 1e-6))
case('size of A2d', 'size.A2d', setv(['size', 'A2d'], lambda v: [v[0], 'LARGE' if v[1] != 'LARGE' else 'SMALL']))
case('beyond-classical entry of SEA', 'beyond_classical_linear.sea.500.theta',
     bump(['beyond_classical_linear', 'sea', '500', 'theta']))
case('df of S1', 'S1.res.df', bump(['components', 'S1', 'res', 'df']))
case('CI of A1', 'A1.res.ci95[1]', setv(['components', 'A1', 'res', 'ci95', 1], lambda v: v + 1e-6))
case('cell counts of F1s', 'F1s.res.n_by_cell', setv(['components', 'F1s', 'res', 'n_by_cell', 0], lambda v: v + 1))
case('margin c_C', 'margins.c_C', bump(['margins', 'c_C']))
case('component removed', 'components (ids)', lambda J: J['components'].pop('S2t'))
case('descriptive field removed', 'descriptive.cdfm.4000 (fields)', lambda J: J['descriptive']['cdfm']['4000'].pop('H_frozen'))
case('linear descriptive entry', 'descriptive_linear.foundcause.200.theta',
     bump(['descriptive_linear', 'foundcause', '200', 'theta']))
case('missing output', 'missing output', mutate_files=file_fault('avici', 'PN9-c3-r4__n500__k0', 'delete'))
case('wrong level in the metadata', 'n=', mutate_files=file_fault('cdfm', 'PN9-c1-r2__n1000__A20', meta_edit(n=999)))
case('non-finite probability', 'not finite', mutate_files=file_fault('avici', 'PN9-c5-r1__n200__A20', nan_probs))
case('SEA adapter flag', 'layout_ok', mutate_files=file_fault('sea', f'PN9-c2-r3__n2000__k0__s{RC.seed_b(33, 2, 3)}',
                                                               meta_edit(layout_ok=False)))
case('array missing', 'arrays', mutate_files=file_fault('foundcause', 'PN9-c6-r0__n125__k0', rename_adj))
case('output changed after the frozen reading', 'descriptive.cdfm.',
     mutate_files=file_fault('cdfm', 'PN9-c0-r0__n200__A20', flip_pair))
case('figure missing', 'figure files missing', mutate_files=drop_figure)
case('wrong target block from the generator', 'input hash differs', generator=generator_for(G, shift=1))
case('wrong padding formula', 'input hash differs', mutate_files=other_padding)
shutil.rmtree(tmp)

# ---------------------------------------------------------------- part A: the other five scenarios
for k, name in enumerate(names):
    if name != 'effects':
        shutil.rmtree(scenario(k, name)[0])

ok = all(v.get('ok') for v in results['agreement'].values()) and len(results['agreement']) == 6 and \
    all(v['caught'] for v in results['faults'].values())
results['ok'] = bool(ok)
n_ok = sum(bool(v.get('ok')) for v in results['agreement'].values())
n_caught = sum(v['caught'] for v in results['faults'].values())
print(f"agreement {n_ok} of {len(results['agreement'])} scenarios; faults caught {n_caught} of {len(results['faults'])}; "
      f"{'ALL PASS' if ok else 'SOME FAIL'}")
(HERE / 'test_recheck9.json').write_bytes((json.dumps(results, indent=1, default=str) + '\n').encode('utf-8'))
shutil.rmtree(ROOT)
sys.exit(0 if ok else 1)
