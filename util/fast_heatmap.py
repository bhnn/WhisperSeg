import seaborn as sns
import matplotlib.pyplot as plt

data = [ # cut: P1: ht, o, ud, n, e, c; P2: hw, d, up; P3: p3, se, sk, wa, ho
  # [ cl,   m,   l,  ca, sh,  b, pc, p1, cm,       +           h,  pu,  mo,  w, p2, +        t, sq,  y, hu, + ],
    [30, 7, 37, 18, 1, 4, 0, 13, 3, 23, 27, 0, 5, 0, 0, 0, 7, 2, 1, 2, 1, 181],
    [76, 4, 27, 72, 15, 2, 0, 0, 2, 7, 66, 39, 15, 0, 0, 0, 40, 0, 1, 2, 0, 368],
    [0, 0, 0, 0, 0, 0, 33, 0, 0, 0, 0, 0, 3, 23, 0, 4, 0, 0, 0, 0, 0, 63],
    [178, 63, 16, 5, 5, 3, 0, 7, 14, 7, 14, 4, 8, 0, 0, 0, 23, 3, 5, 0, 3, 358],
    [53, 17, 26, 49, 36, 30, 6, 9, 1, 5, 75, 13, 99, 20, 14, 8, 64, 2, 0, 5, 6, 538],
    [42, 87, 45, 10, 4, 2, 0, 4, 1, 6, 38, 77, 8, 1, 1, 1, 13, 2, 3, 0, 1, 346],
    [6, 29, 28, 0, 26, 6, 1, 5, 0, 5, 44, 38, 9, 1, 12, 0, 51, 1, 0, 0, 4, 266],
    [385, 207, 179, 154, 87, 47, 40, 38, 21, 53, 264, 171, 147, 45, 27, 13, 198, 10, 10, 9, 15, 2120]
]

_, ax = plt.subplots(1, 1, figsize=(6.4 * 2, 4.8 * 2))
annotations = [['' if x < 1 else f'{x:.0f}' for x in row] for row in data]
sns.heatmap(
    data=data,
    annot=annotations,
    fmt='',
    vmax=178,
    cmap='viridis',
    square=True,
    linewidths=.25,
    linecolor='#222',
    # xticklabels=['cl', 'm', 'l', 'ca', 'sh', 'b', 'pc', 'p1', 'cm', '+', 'h', 'pu', 'mo', 'w', 'p2', '+', 't', 'sq', 'y', 'hu', '+', 'Total'],
    xticklabels=['click', 'mid', 'low', 'cackle', 'short hmm', 'bark', 'pre-click', 'generic p1', 'click-series', '<20 samples', 'hmm', 'purr', 'moan', 'wail', 'generic p2', '<20 samples', 'trill', 'squiggly', 'yip', 'huh', '<20 samples', 'Total'],
    yticklabels=['File1', 'File2', 'File3', 'File4', 'File5', 'File6', 'File7', 'Total'],
    ax=ax,
    cbar_kws={"shrink": 0.45}
)

# horizontal lines
ax.axvline(x=10, linewidth=2, color='white')
ax.axvline(x=16, linewidth=2, color='white')

# secondary x axis
sec_ax = ax.secondary_xaxis('top')
sec_ax.set_ticks([5, 13, 19])
sec_ax.set_xticklabels(['P1', 'P2', 'P3'])
sec_ax.spines['bottom'].set_position(('outward', 10))
sec_ax.spines['bottom'].set_visible(False)
sec_ax.tick_params(length=0, pad=5)

plt.yticks(rotation=0)
plt.xticks(rotation=-45, ha='left')
plt.savefig(f'/usr/users/bhenne/projects/whisperseg/results/fast_heatmap.pdf', format='pdf', dpi=400, bbox_inches='tight')