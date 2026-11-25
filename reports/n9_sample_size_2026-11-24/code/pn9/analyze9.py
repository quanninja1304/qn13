"""P-N9 / Study 8 reading (rules PN9 v1 §3, §4). Frozen with the rest of the code before the main runs; reads saved outputs.

usage (Study 1 model environment):
  python -I analyze9.py PN9                      confirmatory reading; refuses unless the completeness check passed
  python -I analyze9.py DEV9 --structure-only    structure check on DEV outputs (rules §6, G6); prints no value and
                                                 exercises the figure code on placeholder values only
Writes (PN9): reports/n9_sample_size_2026-11-24/checks/pn9_reading.json and artifacts/n9_runs/figures/pn9_fig_*.png/pdf.
"""
import sys
import json
import math
import argparse
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common9 import *
import stats9 as S

ap = argparse.ArgumentParser()
ap.add_argument('set', choices=('PN9', 'DEV9'))
ap.add_argument('--structure-only', action='store_true')
a = ap.parse_args()
STRUCT = a.structure_only or a.set == 'DEV9'
CHECKS = REPORT / 'checks'
FIGS = RUNS9 / 'figures'
if not STRUCT:
    comp_file = CHECKS / 'pn9_completeness.json'
    if not comp_file.exists() or not json.loads(comp_file.read_text())['ok']:
        sys.exit('completeness check missing or failed: no reading (rules §7)')

M_H, M_D = 0.05, 1.0                                   # rules §4.1
REGIME = {'avici': lambda n: n == 200, 'cdfm': lambda n: 50 <= n <= 4096, 'foundcause': lambda n: 112 <= n <= 665,
          'sea': lambda n: 10000 <= n <= 100000}       # rules §0, §2.3
BAND = {'avici': (190, 210), 'cdfm': (50, 4096), 'foundcause': (112, 665), 'sea': (10000, 100000)}
_graph = {}


def graph_of(sysid, ci, seed):
    if sysid not in _graph:
        _graph[sysid] = target_raw(sysid, ci, seed)['g']
    return _graph[sysid]


def per_system(model, set_name):
    """{sysid: dict(ci, lin, by_n={n: values})} over the systems with both outputs at a level (rules §3)."""
    out = {}
    off = SETS9[set_name]['off']
    for sysid, ci, sseed, i in systems9(set_name):
        if model in CLASSICAL and ci not in LINEAR:
            continue
        rec = dict(ci=ci, lin=ci in LINEAR, by_n={})
        for n in GRIDS[model]:
            if model == 'sea':
                lev = GRIDS['sea'].index(n)
                sa = seed_a(i, lev, off)
                o0, o1 = load('sea', key_of(sysid, n, 'k0', sa)), load('sea', key_of(sysid, n, 'A20', sa))
                refs = [load('sea', key_of(sysid, n, 'k0', seed_b(i, lev, m, off))) for m in range(1, M_REF + 1)]
                if o0 is None or o1 is None or any(r is None for r in refs):
                    continue
            else:
                o0, o1 = load(model, key_of(sysid, n, 'k0')), load(model, key_of(sysid, n, 'A20'))
                if o0 is None or o1 is None:
                    continue
            g = graph_of(sysid, ci, sseed)
            dT = g.shape[0]
            s0, s1 = skeleton(model, o0, dT), skeleton(model, o1, dT)
            f0, f1_ = float(M1.f1(s0, g)), float(M1.f1(s1, g))
            v = dict(H=f0 - f1_, f1_0=f0, f1_1=f1_, flips=int(M1.flips(s1, s0)))
            if model not in CLASSICAL:                     # mean |change| of the pair probabilities of the target block
                pk = 'prob' if model == 'sea' else 'probs'
                v['dp'] = M1.dp(o1[pk], o0[pk], dT)[0]
            if model == 'cdfm':
                v['H_fixed'] = float(M1.f1(M1.skel_fixed(o0['probs'], dT), g) - M1.f1(M1.skel_fixed(o1['probs'], dT), g))
                v['H_frozen'] = float(f0 - M1.f1(M1.skel_frozen_cdfm(o1, dT, float(o0['threshold'])), g))
            if model == 'sea':
                sr = [skeleton('sea', r, dT) for r in refs]
                v['delta'] = float(np.mean([M1.flips(s1, x) - M1.flips(s0, x) for x in sr]))
                v['flips_seed'] = float(np.mean([M1.flips(s0, x) for x in sr]))          # k0 against k0, another seed
                v['dp_seed'] = float(np.mean([M1.dp(r['prob'], o0['prob'], dT)[0] for r in refs]))

                def alt(o):
                    return C8.as_matrix(C8.skel(o['prob'], dT, alt=True), dT)
                a0, a1, ar = alt(o0), alt(o1), [alt(r) for r in refs]
                v['delta_alt'] = float(np.mean([M1.flips(a1, x) - M1.flips(a0, x) for x in ar]))
                v['H_alt'] = float(M1.f1(a0, g) - M1.f1(a1, g))
            rec['by_n'][n] = v
        out[sysid] = rec
    return out


def vals(ps, n, field, lin_only=False):
    v, c = [], []
    for rec in ps.values():
        if n in rec['by_n'] and (rec['lin'] or not lin_only):
            v.append(rec['by_n'][n][field])
            c.append(rec['ci'])
    return v, c


def contrast(ps, n, n0, field):
    v, c = [], []
    for rec in ps.values():
        if n in rec['by_n'] and n0 in rec['by_n']:
            v.append(rec['by_n'][n][field] - rec['by_n'][n0][field])
            c.append(rec['ci'])
    return v, c


def slopes(ps, levels, field):
    v, c = [], []
    for rec in ps.values():
        if all(n in rec['by_n'] for n in levels):
            v.append(S.slope_per_system([rec['by_n'][n][field] for n in levels], levels))
            c.append(rec['ci'])
    return v, c


def st(v, c):
    return S.strat(v, c) if len(v) > 1 else None


def span_margin(levels, m):
    return m / math.log2(max(levels) / min(levels))


# ---------------------------------------------------------------- per-system values
PS = {m: per_system(m, a.set) for m in ALL}
counts = {m: {n: sum(n in rec['by_n'] for rec in PS[m].values()) for n in GRIDS[m]} for m in ALL}

# ---------------------------------------------------------------- the 11 components (rules §4.2)
gA, gC, gF, gS = GRIDS['avici'], GRIDS['cdfm'], GRIDS['foundcause'], GRIDS['sea']
c_C, c_F, c_S = span_margin(gC, M_H), span_margin(gF, M_H), span_margin(gS, M_D)
spec = {
    'A1': dict(model='avici', kind='persist', level=200, field='H', margin=M_H),
    'A2d': dict(model='avici', kind='two_sided', levels=(500, 200), field='H', margin=M_H),
    'A2s': dict(model='avici', kind='tost', levels=(500, 200), field='H', margin=M_H),
    'C1': dict(model='cdfm', kind='persist', level=max(gC), field='H', margin=M_H),
    'C2s': dict(model='cdfm', kind='shrinks', levels=gC, field='H', c=c_C),
    'C2t': dict(model='cdfm', kind='stable', levels=tuple(n for n in gC if n != 500), field='H', margin=M_H),
    'F1s': dict(model='foundcause', kind='shrinks', levels=gF, field='H', c=c_F),
    'F1t': dict(model='foundcause', kind='stable', levels=tuple(n for n in gF if n != 500), field='H', margin=M_H),
    'S1': dict(model='sea', kind='persist', level=max(gS), field='delta', margin=M_D),
    'S2s': dict(model='sea', kind='shrinks', levels=gS, field='delta', c=c_S),
    'S2t': dict(model='sea', kind='stable', levels=tuple(n for n in gS if n != 500), field='delta', margin=M_D),
}
comp = {}
for cid, sp in spec.items():
    ps = PS[sp['model']]
    if sp['kind'] == 'persist':
        r = st(*vals(ps, sp['level'], sp['field']))
        p = S.p_greater(r) if r else None
        comp[cid] = dict(spec=sp, res=r, p=p)
    elif sp['kind'] in ('two_sided', 'tost'):
        r = st(*contrast(ps, sp['levels'][0], sp['levels'][1], sp['field']))
        p = (S.p_two_sided(r) if sp['kind'] == 'two_sided' else S.p_tost(r, sp['margin'])) if r else None
        comp[cid] = dict(spec=sp, res=r, p=p)
    elif sp['kind'] == 'shrinks':
        r = st(*slopes(ps, sp['levels'], sp['field']))
        p = S.p_less(r, -sp['c']) if r else None
        comp[cid] = dict(spec=sp, res=r, p=p)
    else:
        rs = {n: st(*contrast(ps, n, 500, sp['field'])) for n in sp['levels']}
        ok = all(rs.values())
        comp[cid] = dict(spec=sp, res_by_level=rs, p=S.p_iut(list(rs.values()), sp['margin']) if ok else None)
computable = {cid: c['p'] is not None for cid, c in comp.items()}

# ---------------------------------------------------------------- Holm and labels (rules §4.2, §4.3)
labels = {}
if all(computable.values()):
    hol = S.holm({cid: c['p'] for cid, c in comp.items()})
    rej = {cid: hol[cid][2] for cid in comp}
    for cid in ('A1', 'C1', 'S1'):
        th, m = comp[cid]['res']['theta'], comp[cid]['spec']['margin']
        labels[cid] = 'PERSISTS' if rej[cid] and th >= m else ('PRESENT_BELOW_MARGIN' if rej[cid] else 'NOT_CONFIRMED')
    a2 = []
    if rej['A2d']:
        a2.append('HIGHER' if comp['A2d']['res']['theta'] > 0 else 'LOWER')
    if rej['A2s']:
        a2.append('SIMILAR')
    labels['A2'] = ' + '.join(sorted(a2, key=lambda s: s != 'SIMILAR')) if a2 else 'UNCLEAR'
    for t, (s_id, t_id) in (('C2', ('C2s', 'C2t')), ('F1', ('F1s', 'F1t')), ('S2', ('S2s', 'S2t'))):
        lab = [x for x, ok in (('SHRINKS', rej[s_id]), ('STABLE', rej[t_id])) if ok]
        labels[t] = ' + '.join(lab) if lab else 'UNCLEAR'
    size = {cid: S.size_label(comp[cid]['res']['ci95'], comp[cid]['spec']['margin']) for cid in ('A1', 'C1', 'S1', 'A2d')}
else:
    hol, size = None, None

# ---------------------------------------------------------------- descriptive (rules §3)
FIELDS = {m: ['H', 'flips', 'f1_0', 'f1_1'] + (['dp'] if m not in CLASSICAL else []) +
          (['H_fixed', 'H_frozen'] if m == 'cdfm' else []) +
          (['delta', 'delta_alt', 'H_alt', 'flips_seed', 'dp_seed'] if m == 'sea' else []) for m in ALL}
desc = {m: {n: {f: st(*vals(PS[m], n, f)) for f in FIELDS[m]} for n in GRIDS[m]} for m in ALL}
desc_lin = {m: {n: st(*vals(PS[m], n, 'H', lin_only=True)) for n in GRIDS[m]} for m in MODELS + ('sea',)}
beyond = {}
for m in MODELS + ('sea',):
    beyond[m] = {}
    for n in GRIDS[m]:
        v, c = [], []
        for sysid, rec in PS[m].items():
            cp, cg = PS['pc'].get(sysid), PS['ges'].get(sysid)
            if rec['lin'] and n in rec['by_n'] and cp and cg and n in cp['by_n'] and n in cg['by_n']:
                v.append(rec['by_n'][n]['H'] - max(cp['by_n'][n]['H'], cg['by_n'][n]['H']))
                c.append(rec['ci'])
        beyond[m][n] = st(v, c)
rho = {}
for m in ALL:
    field = 'delta' if m == 'sea' else 'H'
    rows = [[rec['by_n'][n][field] for n in GRIDS[m]] for rec in PS[m].values() if all(n in rec['by_n'] for n in GRIDS[m])]
    rho[m] = np.corrcoef(np.asarray(rows).T).tolist() if len(rows) > 2 else None


# ---------------------------------------------------------------- figures (rules §4.4)
def figures(desc_, desc_lin_, out_dir, tag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    BLUE, GRAY, INK, INK2, MUTED, GRID, AXIS, WASH = '#2a78d6', '#898781', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#cde2fb'
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Segoe UI', 'DejaVu Sans', 'Arial'], 'font.size': 8,
                         'axes.edgecolor': AXIS, 'axes.labelcolor': INK2, 'axes.titlesize': 9, 'axes.titleweight': 'bold',
                         'axes.titlecolor': INK, 'axes.titlelocation': 'left', 'axes.linewidth': 0.8, 'xtick.color': MUTED,
                         'ytick.color': MUTED, 'xtick.labelcolor': INK2, 'ytick.labelcolor': INK2, 'legend.frameon': False,
                         'savefig.dpi': 300, 'pdf.fonttype': 42})
    names = {'avici': 'AVICI', 'cdfm': 'CDFM', 'foundcause': 'FoundCause', 'sea': 'SEA'}

    def panel(ax, m, table, field, title, color=BLUE, ref=None):
        lo_b, hi_b = BAND[m]
        ax.axvspan(lo_b, hi_b, color=WASH, lw=0, zorder=0)
        ax.axvline(500, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=1)
        ax.axhline(0, color=AXIS, lw=0.8, zorder=1)
        if field:   # table[n] = {field: strat result}
            xs = [n for n in GRIDS[m] if table.get(n) and table[n].get(field)]

            def get(n):
                return table[n][field]
        else:       # table[n] = strat result
            xs = [n for n in GRIDS[m] if table.get(n)]

            def get(n):
                return table[n]
        ys = [get(n)['theta'] for n in xs]
        ax.plot(xs, ys, color=color, lw=1.6, zorder=2)
        for n in xs:
            r = get(n)
            ax.plot([n, n], r['ci95'], color=color, lw=1.6, solid_capstyle='round', zorder=2)
            inside = REGIME[m](n)
            ax.plot([n], [r['theta']], marker='o', ms=5.5, zorder=3, color=color if inside else 'white',
                    markeredgecolor='white' if inside else color, markeredgewidth=1.2 if inside else 1.4)
        if ref:
            for rlab, rtab, rcol in ref:
                rx = [n for n in sorted(rtab) if rtab.get(n)]
                ax.plot(rx, [rtab[n]['theta'] for n in rx], color=rcol, lw=1.0, ls='-', marker='o', ms=3, zorder=1.5)
        ax.set_xscale('log')
        ax.set_xlim(80, 30000)                                                 # SEA's training band continues to 100,000
        ax.set_xticks([100, 500, 2000, 20000])
        ax.set_xticklabels(['100', '500', '2k', '20k'])
        ax.set_xticks([125, 200, 1000, 4000, 5000], minor=True)
        ax.set_xticklabels([], minor=True)
        for s_ in ('top', 'right'):
            ax.spines[s_].set_visible(False)
        ax.grid(axis='y', color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.set_title(title, pad=8)

    def key(fig, extra=()):      # one key below the panels; extra: (label, color) of reference lines
        h = [Line2D([], [], color=BLUE, lw=1.6, marker='o', ms=5.5, markeredgecolor='white', markeredgewidth=1.2),
             Line2D([], [], color=BLUE, lw=1.6, marker='o', ms=5.5, markerfacecolor='white', markeredgecolor=BLUE,
                    markeredgewidth=1.4), Patch(facecolor=WASH)]
        lab = ['n inside the training regime', 'n outside', 'training regime']
        for rlab, rcol in extra:
            h.append(Line2D([], [], color=rcol, lw=1.0, marker='o', ms=3))
            lab.append(rlab)
        fig.legend(h, lab, loc='lower center', ncol=len(h), fontsize=6.8, handlelength=1.8, columnspacing=1.4, borderaxespad=0.2)

    out_dir.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.75), sharey=True)
    for ax, m in zip(axs, ('avici', 'cdfm', 'foundcause', 'sea')):
        panel(ax, m, desc_[m], 'H', names[m])
        ax.set_xlabel('n (log scale)')
    axs[0].set_ylabel('F1 lost at k = 20')
    key(fig)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.285, wspace=0.12)
    for ext in ('png', 'pdf'):
        fig.savefig(out_dir / f'pn9_fig_main{tag}.{ext}')
    plt.close(fig)
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.75), sharey=True)
    for ax, m in zip(axs, ('avici', 'cdfm', 'foundcause', 'sea')):
        panel(ax, m, desc_lin_[m], None, names[m] + ', linear',
              ref=[('PC', {n: desc_['pc'][n]['H'] for n in GRIDS['pc']}, GRAY),
                   ('GES', {n: desc_['ges'][n]['H'] for n in GRIDS['ges']}, INK2)])
        ax.set_xlabel('n (log scale)')
    axs[0].set_ylabel('F1 lost at k = 20')
    key(fig, (('PC', GRAY), ('GES', INK2)))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.285, wspace=0.12)
    for ext in ('png', 'pdf'):
        fig.savefig(out_dir / f'pn9_fig_linear{tag}.{ext}')
    plt.close(fig)
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.75), sharey=True)
    for ax, m in zip(axs, ('avici', 'cdfm', 'foundcause', 'sea')):
        ref = [('two seeds, k = 0', {n: desc_['sea'][n]['flips_seed'] for n in GRIDS['sea']}, GRAY)] if m == 'sea' else None
        panel(ax, m, desc_[m], 'flips', names[m], ref=ref)
        ax.set_xlabel('n (log scale)')
    axs[0].set_ylabel('flips, k = 20 vs k = 0')
    key(fig, (('SEA: two seeds at k = 0', GRAY),))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.285, wspace=0.12)
    for ext in ('png', 'pdf'):
        fig.savefig(out_dir / f'pn9_fig_flips{tag}.{ext}')
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(3.4, 2.75))
    panel(ax, 'sea', desc_['sea'], 'delta', 'SEA: Δ (pairs)')
    ax.set_xlabel('n (log scale)')
    ax.set_ylabel('Δ, pairs')
    key(fig)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.88, bottom=0.285)
    for ext in ('png', 'pdf'):
        fig.savefig(out_dir / f'pn9_fig_sea_delta{tag}.{ext}')
    plt.close(fig)


# ---------------------------------------------------------------- output
if STRUCT:
    print('structure-only reading of', a.set, '(no value is printed)')
    print('systems with both outputs, by model and level:', json.dumps(counts))
    print('components computable:', json.dumps(computable))
    print('descriptive cells computed:', {m: sum(1 for n in GRIDS[m] for f in FIELDS[m] if desc[m][n][f]) for m in ALL})
    print('rho matrices:', {m: (None if rho[m] is None else f'{len(rho[m])}x{len(rho[m])}') for m in ALL})

    def placeholder(t):   # same structure, every value replaced by 0, to exercise the figure code without reading values
        if isinstance(t, dict):
            if 'theta' in t:
                return dict(t, theta=0.0, ci95=[0.0, 0.0])
            return {k: placeholder(v) for k, v in t.items()}
        return t
    tmp = WORK9 / 'g6_placeholder_figures'
    figures(placeholder(desc), placeholder(desc_lin), tmp, '_placeholder')
    made = sorted(p.name for p in tmp.glob('*'))
    for p in tmp.glob('*'):
        p.unlink()
    tmp.rmdir()
    print('figure code ran on placeholder values; files made and deleted:', made)
    sys.exit(0)

hdrs = json.loads((OUT9 / 'pn9_run_header.json').read_text()) if (OUT9 / 'pn9_run_header.json').exists() else []
res = dict(rules='PN9 v1 (locked 5146c74)', set=a.set, counts=counts, margins=dict(H=M_H, delta=M_D, c_C=c_C, c_F=c_F, c_S=c_S),
           components={cid: dict(spec={k: (list(v) if isinstance(v, tuple) else v) for k, v in c['spec'].items()},
                                 p=c['p'], res=c.get('res'),
                                 res_by_level={str(k): v for k, v in c.get('res_by_level', {}).items()} or None,
                                 holm=None if hol is None else dict(rank=hol[cid][0], threshold=hol[cid][1], rejected=hol[cid][2]))
                       for cid, c in comp.items()},
           labels=labels, size={k: list(v) for k, v in (size or {}).items()},
           descriptive={m: {str(n): desc[m][n] for n in GRIDS[m]} for m in ALL},
           descriptive_linear={m: {str(n): desc_lin[m][n] for n in GRIDS[m]} for m in desc_lin},
           beyond_classical_linear={m: {str(n): beyond[m][n] for n in GRIDS[m]} for m in beyond},
           rho=rho, freeze_headers=[h['label'] for h in hdrs])
CHECKS.mkdir(parents=True, exist_ok=True)
(CHECKS / 'pn9_reading.json').write_text(json.dumps(res, indent=1))
figures(desc, desc_lin, FIGS, '')
print(json.dumps(dict(labels=labels, p={cid: c['p'] for cid, c in comp.items()}), indent=1))
