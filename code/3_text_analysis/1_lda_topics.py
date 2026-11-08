"""
3_text_analysis/1_lda_topics.py - what do reviewers write about? (LDA topic model)

Thesis: Sections 4.3.1 and 5.1 ("LDA Topic Structure"), Figure 2, Appendix A.4
Produces:
  Figure 2   -> results/figures/figure2_lda_topics.jpg
  Table A.4b -> results/tables/tableA4b_lda_top_terms.csv
  Table A.4c -> results/tables/tableA4c_lda_topic_shares.csv

Needs the review text, so it reads the private file private/df_enriched.csv
(see data/README.md). It cannot be run from the public data alone; its outputs
are included in results/.

Purpose: a diagnostic, not a causal analysis. Before trusting the dictionary
scores, check that reviews actually talk about quality, value and service, and
whether the mix of topics shifts after launch (it does: service complaints fall
and delivery topics rise in both groups).

Method: reviews with at least 5 words; bag-of-words (scikit-learn
CountVectorizer); LDA with 7 topics (online variational Bayes, 30 iterations,
learning offset 50, seed 42). Each review is assigned to its most likely topic,
and topic shares are compared across four groups: treatment pre/post launch and
control pre/post pseudo-event date.

Note on settings: these are the settings that produced the thesis figure and
Table A.4c: up to 1,000 single words, appearing in at least 2 reviews and at
most 95% of them, English stop words removed. Section 4.3.1 of the thesis
describes a different vocabulary (3,000 unigrams and bigrams, min 30 reviews,
max 60%); the text, not this code, is out of date. The model input is the title
followed by title + body, so titles are counted twice; this is kept so the
output matches the thesis.
Topic numbers are assigned by the algorithm; labels were given by reading the
top words (TOPIC_LABELS below) and must be re-checked if settings change.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import DATA, PRIVATE, TABLES, FIGURES

src = PRIVATE / "df_enriched.csv"
if not src.exists():
    sys.exit("private/df_enriched.csv not found: this script needs the unpublished review text.")

df = pd.read_csv(src, low_memory=False)          # UTF-8, as in the thesis run
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df.loc[df['brand'].str.endswith('zane'), 'brand'] = 'Sézane'

# Control brands: pre/post split at the pseudo-event date of their matched treatment brand
pseudo = pd.read_csv(DATA / "control_brands.csv", parse_dates=['pseudo_event_date'])
df = df.merge(pseudo[['brand', 'pseudo_event_date']], on='brand', how='left')
df['ctrl_period'] = np.where(df['group'] != 'control', None,
                             np.where(df['date'] < df['pseudo_event_date'], 'pre', 'post'))

# -- Fit the model ---------------------------------------------------------------
df['text_combined'] = (df['title'].fillna('') + ' ' + df['full_text'].fillna('')).str.strip()
lda_df = df[df['text_combined'].str.split().str.len() >= 5].copy()
print(f"Reviews used: {len(lda_df):,}")

vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
dtm = vectorizer.fit_transform(lda_df['text_combined'])
lda = LatentDirichletAllocation(n_components=7, random_state=42, learning_offset=50, max_iter=30)
lda.fit(dtm)
lda_df['topic'] = lda.transform(dtm).argmax(axis=1)
words = vectorizer.get_feature_names_out()

# Labels assigned after reading each topic's top words (see Table A.4b)
TOPIC_LABELS = {5: 'Service Complaints', 6: 'Product Quality & Durability', 1: 'Delivery & Fit',
                0: 'Service & Experience', 2: 'Dutch-language reviews',
                4: 'French-language reviews', 3: 'German-language reviews'}
ORDER = [5, 6, 1, 0, 2, 4, 3]
COLORS = {5: '#E8956D', 6: '#8DB580', 1: '#6A9FC0', 0: '#C0A0C8',
          2: '#C8B86A', 4: '#B08060', 3: '#E895B0'}

top10 = {t: [words[j] for j in lda.components_[t].argsort()[-10:][::-1]] for t in range(7)}
for t in ORDER:
    print(f"  {TOPIC_LABELS[t]:<30} {', '.join(top10[t])}")

# -- Topic shares by group --------------------------------------------------------
groups = {
    'Treatment pre-launch':  lda_df[(lda_df['group'] == 'treatment') & (lda_df['period'] == 'pre')],
    'Treatment post-launch': lda_df[(lda_df['group'] == 'treatment') & (lda_df['period'] == 'post')],
    'Control pre-event':     lda_df[lda_df['ctrl_period'] == 'pre'],
    'Control post-event':    lda_df[lda_df['ctrl_period'] == 'post'],
}
shares = {g: {t: (d['topic'] == t).mean() * 100 for t in range(7)} for g, d in groups.items()}

pd.DataFrame([{'topic': i + 1, 'label': TOPIC_LABELS[t], 'top_10_terms': ', '.join(top10[t])}
              for i, t in enumerate(ORDER)]).to_csv(TABLES / 'tableA4b_lda_top_terms.csv', index=False)
pd.DataFrame([{'topic': i + 1, 'label': TOPIC_LABELS[t],
               **{g: round(shares[g][t], 1) for g in groups}} for i, t in enumerate(ORDER)]
             ).to_csv(TABLES / 'tableA4c_lda_topic_shares.csv', index=False)
print("N per group:", {g: len(d) for g, d in groups.items()})

# -- Figure 2 -----------------------------------------------------------------------
fig = plt.figure(figsize=(16, 11))
fig.suptitle(f'Figure 2. LDA Topic Model: Seven-Topic Solution (N = {len(lda_df):,} reviews)',
             fontsize=12, fontweight='bold', y=0.98)
for i, t in enumerate([5, 6, 1, 0]):               # top panel: the four English topics
    ax = fig.add_axes([0.04 + i * 0.245, 0.58, 0.21, 0.34])
    comp = lda.components_[t]
    top8 = [(words[j], comp[j] / comp.sum() * 100) for j in comp.argsort()[-8:][::-1]]
    terms, weights = zip(*top8)
    ax.barh(range(8), weights[::-1], color=COLORS[t], alpha=0.85)
    ax.set_yticks(range(8)); ax.set_yticklabels(list(terms)[::-1], fontsize=8)
    ax.set_xlabel('Relative weight (%)', fontsize=7)
    ax.set_title(f"T{ORDER.index(t) + 1}: {TOPIC_LABELS[t]}", fontsize=8, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)

ax = fig.add_axes([0.07, 0.05, 0.60, 0.44])        # bottom panel: shares by group
x = np.arange(4); bottom = np.zeros(4)
for t in ORDER:
    vals = np.array([shares[g][t] for g in groups])
    ax.bar(x, vals, 0.55, bottom=bottom, color=COLORS[t], alpha=0.88, label=TOPIC_LABELS[t])
    for xi, (v, b) in enumerate(zip(vals, bottom)):
        if v >= 5:
            ax.text(xi, b + v / 2, f'{v:.0f}%', ha='center', va='center',
                    fontsize=8, fontweight='bold', color='white')
    bottom += vals
ax.set_xticks(x)
ax.set_xticklabels(['Treatment\n(pre-launch)', 'Treatment\n(post-launch)',
                    'Control\n(pre-event)', 'Control\n(post-event)'], fontsize=9)
ax.set_ylabel('Share of reviews (%)'); ax.set_ylim(0, 105)
ax.set_title('Topic distribution by review group', fontsize=10, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
ax.legend(handles=[mpatches.Patch(color=COLORS[t], label=TOPIC_LABELS[t]) for t in ORDER],
          loc='upper left', bbox_to_anchor=(1.03, 1.0), fontsize=8, frameon=False, title='Topic')
fig.savefig(FIGURES / 'figure2_lda_topics.jpg', dpi=150, bbox_inches='tight', facecolor='white')
print("Saved", FIGURES / 'figure2_lda_topics.jpg')
