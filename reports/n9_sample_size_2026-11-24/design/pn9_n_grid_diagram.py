"""P-N9 design diagram: the proposed sample sizes of each model on a log axis, against its training regime.
No data: the diagram shows the design only (palette and style of the N1 figures).
usage: python -I -X utf8 pn9_n_grid_diagram.py <out.png>
"""
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BLUE, GRAY = '#2a78d6', '#898781'
INK, INK2, MUTED, GRID, AXIS = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
BLUE_WASH = '#cde2fb'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Segoe UI', 'DejaVu Sans', 'Arial'], 'font.size': 8,
    'axes.edgecolor': AXIS, 'axes.labelcolor': INK2, 'axes.titlesize': 9, 'axes.titleweight': 'bold',
    'axes.titlecolor': INK, 'axes.titlelocation': 'left', 'axes.linewidth': 0.8,
    'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.labelcolor': INK2, 'ytick.labelcolor': INK2,
    'xtick.major.size': 0, 'ytick.major.size': 0, 'legend.frameon': False, 'legend.fontsize': 7.5,
    'savefig.dpi': 200, 'figure.dpi': 150,
})

# rows: label, training band (lo, hi) in n or None, band note, points [(n, inside, confirmatory)], colour
rows = [
    ('AVICI', (190, 210), 'trained on 200-row examples',
     [(100, False, False), (200, True, True), (500, False, True), (1000, False, False)], BLUE),
    ('CDFM', (50, 4096), 'trained on n in [50, 4096]',
     [(100, True, False), (200, True, False), (500, True, False), (1000, True, False), (2000, True, False),
      (4000, True, True)], BLUE),
    ('FoundCause', (112, 665), '100–599 rows per run (each run uses 90% of n)',
     [(125, True, False), (200, True, False), (500, True, False)], BLUE),
    ('SEA', (10000, 100000), 'training data sets of 1000·N rows, N = 10–100',
     [(500, False, False), (1000, False, False), (2000, False, False), (5000, False, False), (20000, True, True)], BLUE),
    ('PC, GES', None, 'GES up to 4000; PC at every n',
     [(100, None, False), (125, None, False), (200, None, False), (500, None, False), (1000, None, False),
      (2000, None, False), (4000, None, False), (5000, None, False), (20000, None, False)], GRAY),
]

fig, ax = plt.subplots(figsize=(7.2, 3.3))
for i, (name, band, note, pts, col) in enumerate(rows):
    y = i
    if band:
        ax.add_patch(plt.Rectangle((band[0], y - 0.28), band[1] - band[0], 0.56, color=BLUE_WASH, zorder=1, lw=0))
    ax.text(1.02, y, note, transform=ax.get_yaxis_transform(), ha='left', va='center', fontsize=6.6, color=INK2)
    xs = [p[0] for p in pts]
    ax.plot([min(xs), max(xs)], [y, y], color=AXIS, linewidth=0.8, zorder=2)
    for n, inside, conf in pts:
        filled = inside is None or inside
        ax.plot([n], [y], marker='o', markersize=6, zorder=4, color=col if filled else 'white',
                markeredgecolor='white' if filled else col, markeredgewidth=1.2 if filled else 1.4)
        if conf:
            ax.plot([n], [y], marker='o', markersize=11, zorder=3, color='none', markeredgecolor=INK, markeredgewidth=0.9)
ax.axvline(500, color=MUTED, linewidth=0.8, linestyle=(0, (3, 2)), zorder=0)
ax.text(500, len(rows) - 0.45, 'n of Studies 1–7', ha='center', va='bottom', fontsize=6.6, color=INK2)
ax.text(520, 3 - 0.36, 'b = n: every batch holds the same 500 rows', ha='left', va='top', fontsize=6.2, color=INK2)
ax.set_xscale('log')
ax.set_xlim(60, 120000)
ticks = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 100000]
ax.set_xticks(ticks)
ax.set_xticklabels(['100', '200', '500', '1k', '2k', '5k', '10k', '20k', '100k'])
ax.minorticks_off()
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows])
ax.set_ylim(len(rows) - 0.4, -0.6)
ax.set_xlabel('sample size n (rows of the target table and of the appended columns; log scale)')
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.grid(axis='x', color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
ax.set_title('Proposed sample sizes against each training regime', pad=16)
handles = [Line2D([], [], marker='o', linestyle='', markersize=6, color=BLUE, markeredgecolor='white', label='inside the training regime'),
           Line2D([], [], marker='o', linestyle='', markersize=6, color='white', markeredgecolor=BLUE, markeredgewidth=1.4,
                  label='outside it'),
           Line2D([], [], marker='o', linestyle='', markersize=11, color='none', markeredgecolor=INK, markeredgewidth=0.9,
                  label='n of a confirmatory test at one n'),
           plt.Rectangle((0, 0), 1, 1, color=BLUE_WASH, label='training regime')]
ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.0, -0.2), ncol=4, fontsize=6.8, handletextpad=0.4,
          columnspacing=1.2)
fig.subplots_adjust(left=0.11, right=0.70, top=0.86, bottom=0.27)
fig.savefig(sys.argv[1])
print('saved', sys.argv[1])
