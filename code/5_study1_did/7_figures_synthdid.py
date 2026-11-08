"""
5_study1_did/7_figures_synthdid.py - figures built from the synthetic DiD output

Thesis: Section 5.2, Figures 3, 4 and 6
Inputs (written by 5_study1_did/4_synthdid.R):
  results/tables/synthdid_pretrend_fit.csv
  results/tables/synthdid_by_brand.csv
Produces:
  Figure 3 -> results/figures/figure3_event_time_rating.jpg
  Figure 4 -> results/figures/figure4_synthdid_by_brand.jpg
  Figure 6 -> results/figures/figure6_pretrend_fit.jpg

Figure 3: average star rating of the treatment brands, each aligned on its own
  launch date, against the plain average of the 27 control brands in the same
  calendar quarters. Brand-quarter means, so each brand counts equally. Shown:
  event times with at least 6 brands, from 6 years before launch onwards. The
  gap before launch is a difference in level, not a diverging trend. The
  1.96 vs 2.62 stars quoted in Section 5.2 are the averages over pre-launch
  event times with at least 3 brands (saved to figure3_pre_launch_means.csv).

Figure 4: each treatment brand's synthetic DiD effect on star rating. Error
  bars are +/- 1 standard error, as in the thesis figure (which does not state
  this; a 95% interval would be about twice as wide). Dark bars: p < 0.05. The effects
  come from 5_study1_did/4_synthdid.R. The SEs are the placebo SEs of the thesis run
  (results/thesis_run/), as in Tables 3 and 4, because placebo SEs are random:
  with a fresh draw one brand (Michael Kors) can cross the 5% line.

Figure 6: the pre-launch part of Figure 3, plus the synthetic control (each
  brand's controls weighted with its own synthdid weights). Reweighting moves
  the control line towards the treated brands but a level gap remains.

Time axis: event_time is the difference between two calendar quarters written
as years (2022 Q2 = 2022.25), so 1.0 on the axis is one year and the points
are one quarter apart. The thesis figures label this axis "Quarters relative to
launch"; the axis is labelled in years here.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import TABLES, FIGURES, BLUE, ORANGE, GREEN

fit = pd.read_csv(TABLES / "synthdid_pretrend_fit.csv")
fit = fit[fit['outcome'] == 'rating']
MIN_BRANDS = 6        # thesis Figure 3 note
WINDOW_START = -6     # years before launch shown in Figures 3 and 6

by_t = (fit.groupby('event_time')
           .agg(treated=('treated', 'mean'), raw_control=('raw_control', 'mean'),
                synth_control=('synth_control', 'mean'), n_brands=('brand', 'nunique'))
           .reset_index())
# Section 5.2 text: pre-launch averages over event times with >= 3 brands
pre_all = by_t[(by_t['event_time'] < 0) & (by_t['n_brands'] >= 3)]
pd.DataFrame({'group': ['treatment', 'control (unweighted)'],
              'pre_launch_mean_rating': [pre_all['treated'].mean(), pre_all['raw_control'].mean()]}
             ).round(4).to_csv(TABLES / "figure3_pre_launch_means.csv", index=False)
print(f"Pre-launch mean rating: treatment {pre_all['treated'].mean():.2f}, "
      f"controls {pre_all['raw_control'].mean():.2f}")

by_t = by_t[(by_t['n_brands'] >= MIN_BRANDS) & (by_t['event_time'] >= WINDOW_START)]
by_t.round(4).to_csv(TABLES / "figure3_figure6_event_time_means.csv", index=False)
pre = by_t[by_t['event_time'] < 0]

# -- Figure 3 ------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5))
ax.axvspan(by_t['event_time'].min() - 0.5, -0.125, color=ORANGE, alpha=0.06)
ax.axvline(0, color='#374151', linestyle='--', linewidth=1.2)
ax.text(0.1, 1.05, 'Launch', fontsize=9, color='#374151')
ax.plot(by_t['event_time'], by_t['treated'], color=BLUE, marker='o', markersize=4, linewidth=2,
        label='Treatment brands (aligned on own launch date)')
ax.plot(by_t['event_time'], by_t['raw_control'], color=ORANGE, marker='s', markersize=4, linewidth=2,
        label='Control brands (same calendar quarters, unweighted)')
ax.set_ylim(1, 3.5)
ax.set_xlabel('Years relative to resale programme launch (one point per quarter)')
ax.set_ylabel('Mean Trustpilot star rating')
ax.set_title('Figure 3. Mean Star Rating by Event Time: Treatment vs Control', fontweight='bold')
ax.legend(loc='upper left', fontsize=9); ax.grid(alpha=0.3)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig(FIGURES / 'figure3_event_time_rating.jpg', dpi=200); plt.close(fig)

# -- Figure 4 ------------------------------------------------------------------------
b = pd.read_csv(TABLES / "synthdid_by_brand.csv")
b = b[b['outcome'] == 'rating'].drop(columns=['se', 'p'])
thesis_se = pd.read_csv(TABLES.parent / "thesis_run" / "synthdid_by_brand_thesis_run.csv")
b = b.merge(thesis_se.loc[thesis_se['outcome'] == 'rating', ['brand', 'se', 'p']], on='brand')
b = b.sort_values('att')
fig, ax = plt.subplots(figsize=(8, 7))
ax.barh(b['brand'], b['att'], color=[BLUE if p < 0.05 else '#93C5FD' for p in b['p']],
        xerr=b['se'], capsize=3)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Synthetic DiD ATT (star rating); error bars = ±1 standard error')
ax.set_title('Figure 4. Synthetic DiD Treatment Effect per Brand (Star Rating)')
ax.text(0.98, 0.02, 'Dark blue = p < 0.05', transform=ax.transAxes, ha='right', color=BLUE, fontsize=9)
fig.tight_layout(); fig.savefig(FIGURES / 'figure4_synthdid_by_brand.jpg', dpi=150); plt.close(fig)

# -- Figure 6 ------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(pre['event_time'], pre['treated'], color=BLUE, marker='o', label='Treatment brands')
ax.plot(pre['event_time'], pre['raw_control'], color=ORANGE, marker='s', linestyle='--',
        label='Control, unweighted (as in Figure 3)')
ax.plot(pre['event_time'], pre['synth_control'], color=GREEN, marker='^',
        label='Control, synthetic DiD weights')
ax.set_ylim(0, 3)
ax.set_xlabel('Years before resale programme launch (one point per quarter)')
ax.set_ylabel('Mean star rating')
ax.set_title('Figure 6. Pre-launch fit: raw control vs synthetic-weighted control')
ax.legend(loc='lower right'); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(FIGURES / 'figure6_pretrend_fit.jpg', dpi=200); plt.close(fig)
print("Saved Figures 3, 4 and 6 to", FIGURES)
