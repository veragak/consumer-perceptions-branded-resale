"""
11_figures_descriptive.py - model-free comparison figures

Thesis: Section 5.1 (Figure 1) and Appendix A.5 (Figure A.5)
Produces:
  Figure 1   -> results/figures/figure1_before_after.jpg
  Figure A.5 -> results/figures/figureA5_sustainability_mentions.jpg
               (+ results/tables/figureA5_sustainability_mentions.csv)

Figure 1 shows the means of Table 2 as bars: each outcome before and after
launch, for treatment brands and for control brands (split at their
pseudo-event date). Both groups improve, and controls improve more, which is
the first sign that the raw groups are not comparable.

Figure A.5 shows, per brand, the share of reviews with a positive sustainability
score (sust_score > 0). Eco-positioned control brands (Organic Basics, Rab) sit
far above everyone else. The dashed lines are the shares across all reviews
of each group (so brands with more reviews weigh more).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _common import DATA, TABLES, FIGURES, BLUE, ORANGE, GREEN, RED

df = pd.read_csv(DATA / "reviews_scored.csv", parse_dates=['date'])
pseudo = pd.read_csv(DATA / "control_brands.csv", parse_dates=['pseudo_event_date'])

# -- Figure 1 ---------------------------------------------------------------------
ctrl = df[df['group'] == 'control'].merge(pseudo[['brand', 'pseudo_event_date']], on='brand')
ctrl['split'] = np.where(ctrl['date'] < ctrl['pseudo_event_date'], 'pre', 'post')
groups = {
    'Treatment\nPre':  df[df['period'] == 'pre'],
    'Treatment\nPost': df[df['period'] == 'post'],
    'Control\nPre':    ctrl[ctrl['split'] == 'pre'],
    'Control\nPost':   ctrl[ctrl['split'] == 'post'],
}
colors = ['#93C5FD', BLUE, '#FCD34D', ORANGE]
outcomes = [('rating', 'Star rating (1-5)'), ('sust_score', 'Sustainability score'),
            ('value_vader', 'Value VADER (-1 to 1)')]

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, (col, label) in zip(axes, outcomes):
    means = [g[col].mean() for g in groups.values()]
    bars = ax.bar(range(4), means, color=colors, width=0.6, edgecolor='white', zorder=3)
    for b, v in zip(bars, means):
        ax.text(b.get_x() + b.get_width() / 2, max(v, 0) + 0.01 * max(means), f'{v:.3f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax.set_xticks(range(4)); ax.set_xticklabels(groups.keys(), fontsize=9)
    ax.set_title(label, fontweight='bold', fontsize=10); ax.set_ylabel(label)
    ax.axhline(0, color='#374151', linewidth=0.6, linestyle=':')
    ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', alpha=0.35)
fig.suptitle('Figure 1. Pre vs Post Outcomes: Treatment vs Control\n'
             '(Control split by pseudo-event date)', fontsize=11, fontweight='bold', y=1.03)
plt.tight_layout()
fig.savefig(FIGURES / 'figure1_before_after.jpg', dpi=200, bbox_inches='tight')
plt.close(fig)
print("Saved", FIGURES / 'figure1_before_after.jpg')

# -- Figure A.5 -------------------------------------------------------------------
rates = (df.assign(mention=df['sust_score'] > 0)
           .groupby(['brand', 'group'])['mention'].mean().mul(100)
           .reset_index(name='pct_positive_sust').sort_values('pct_positive_sust'))
rates.round(1).to_csv(TABLES / 'figureA5_sustainability_mentions.csv', index=False)
pooled = (df['sust_score'] > 0).groupby(df['group']).mean().mul(100)
mean_t, mean_c = pooled['treatment'], pooled['control']

fig, ax = plt.subplots(figsize=(10, 13))
col = [RED if b in ('Organic Basics', 'Rab') else (BLUE if g == 'treatment' else GREEN)
       for b, g in zip(rates['brand'], rates['group'])]
ax.barh(rates['brand'], rates['pct_positive_sust'], color=col, height=0.7)
for y, v in enumerate(rates['pct_positive_sust']):
    ax.text(v + 0.3, y, f'{v:.1f}%', va='center', fontsize=8)
ax.axvline(mean_c, color=GREEN, linestyle='--', label=f'Control mean ({mean_c:.1f}%)')
ax.axvline(mean_t, color=BLUE, linestyle='--', label=f'Treatment mean ({mean_t:.1f}%)')
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=GREEN, label='Control brand'),
                   plt.Rectangle((0, 0), 1, 1, color=BLUE, label='Treatment brand'),
                   plt.Rectangle((0, 0), 1, 1, color=RED, label='Organic Basics & Rab'),
                   *ax.get_legend_handles_labels()[0]], loc='lower right', fontsize=9)
ax.set_xlabel('Reviews containing positive sustainability language (%)')
ax.set_title('Figure A.5. Sustainability Language Mention Rate by Brand\n'
             '(% of reviews with net sustainability score > 0)', fontweight='bold')
ax.spines[['top', 'right']].set_visible(False); ax.margins(y=0.01)
plt.tight_layout()
fig.savefig(FIGURES / 'figureA5_sustainability_mentions.jpg', dpi=150, bbox_inches='tight')
print("Saved", FIGURES / 'figureA5_sustainability_mentions.jpg')
print(f"Share of all reviews with positive sustainability language: treatment {mean_t:.1f}%, control {mean_c:.1f}%")
