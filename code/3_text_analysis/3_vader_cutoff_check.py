"""
3_text_analysis/3_vader_cutoff_check.py - does the 400-character fallback matter?

Thesis: Section 4.2.1 ("Testing cutoffs from 200 to 600 characters produced
near-identical results, r > 0.92")
Produces: results/tables/vader_cutoff_check.csv

The value VADER score only looks at sentences that mention price or value.
Reviews without such a sentence fall back to their first 400 characters. This
script recomputes the score with fallbacks of 200, 300, 400, 500 and 600
characters and reports how strongly each version correlates with the 400-
character version, plus the mean score per group and period. If the
correlations are high and the means barely move, the cutoff choice does not
drive the results.

Needs the review text (private/df_enriched.csv).
"""
import re
import sys
from pathlib import Path

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import PRIVATE, TABLES

VALUE_KW = ['worth', 'value', 'price', 'expensive', 'cheap', 'overpriced',
            'quality', 'cost', 'affordable', 'bargain', 'deal', 'money',
            'paid', 'pay', 'spend']
CUTOFFS = [200, 300, 400, 500, 600]

src = PRIVATE / "df_enriched.csv"
if not src.exists():
    sys.exit("private/df_enriched.csv not found: this script needs the unpublished review text.")
df = pd.read_csv(src, low_memory=False)
analyzer = SentimentIntensityAnalyzer()


def value_text(text, cutoff):
    if not isinstance(text, str):
        return ''
    sents = re.split(r'[.!?\n]+', text)
    keep = [s.strip() for s in sents if any(k in s.lower() for k in VALUE_KW)]
    return ' '.join(keep) if keep else text[:cutoff]


scores = pd.DataFrame({c: df['text'].apply(lambda t: value_text(t, c)).apply(
    lambda t: analyzer.polarity_scores(t)['compound'] if isinstance(t, str) and t.strip() else 0.0)
    for c in CUTOFFS})

rows = []
for c in CUTOFFS:
    row = {'cutoff_chars': c, 'corr_with_400': round(scores[c].corr(scores[400]), 4)}
    for (g, p), sub in scores[c].groupby([df['group'], df['period']]):
        row[f'mean_{g}_{p}'] = round(sub.mean(), 4)
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv(TABLES / "vader_cutoff_check.csv", index=False)
print(out.to_string(index=False))
print(f"\nLowest correlation with the 400-character version: {out['corr_with_400'].min():.3f}")
