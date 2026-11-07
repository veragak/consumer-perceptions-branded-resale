"""
02_score_reviews.py - turn raw Trustpilot reviews into the three outcome measures

Thesis: Section 4.2.1 (dependent variables), Appendix A.2 (dictionary)

Input  (private, not published): private/raw/*_trustpilot.csv, the files written
        by the scrapers in code/01_data_collection/. Each row is one review with
        date, rating, title, text, brand, segment, group (treatment/control) and
        period (pre/post launch for treatment brands, "control" otherwise).
Output (private): private/df_enriched.csv, the same reviews plus:

  sust_pos, sust_neg, sust_score
      Sustainability language score. Title + text are lower-cased and matched
      against a positive dictionary (circular economy and environmental terms)
      and a negative dictionary (greenwashing scepticism). Each pattern counts
      at most once per review. sust_score = positives - negatives.
      Note: the list below has 38 patterns. It contains "natural", which is not
      printed in Table A.2a, and splits some stems into spelling variants
      (pre-owned / preowned). This list is the one the thesis results use.

  value_vader
      Value sentiment. Sentences of the review text that mention price or value
      (worth, value, price, expensive, cheap, ...) are kept and scored with VADER
      (compound score, -1 to 1). Reviews without such a sentence fall back to
      their first 400 characters.

Next step: 03_export_public_data.R removes title/text and writes the public
data/reviews_scored.csv.
"""
import re
import sys
from pathlib import Path

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.insert(0, str(Path(__file__).parent))
from _common import PRIVATE

SUST_POS = [
    r'sustain', r'recycl', r'circular', r'resale', r'second.hand',
    r'secondhand', r'pre.owned', r'preowned', r'pre.loved', r'preloved',
    r'upcycl', r'repair', r'reuse', r'reusing', r'reused',
    r'\bgreen\b', r'\beco\b', r'environmental', r'responsible',
    r'ethical', r'conscious', r'\bwaste\b', r'renew',
    r'carbon', r'\bplanet\b', r'climate', r'longevity',
    r'\bdurable\b', r'durability', r'lifecycle', r'life.cycle',
    r'low.impact', r'fair.trade', r'fairtrade', r'organic',
    r'natural', r'biodegradable', r'zero.waste',
]
SUST_NEG = [r'greenwash', r'hypocri', r'performativ', r'virtue.signal',
            r'mislead', r'deceptive', r'fake.green']
VALUE_KW = ['worth', 'value', 'price', 'expensive', 'cheap', 'overpriced',
            'quality', 'cost', 'affordable', 'bargain', 'deal', 'money',
            'paid', 'pay', 'spend']


def count_matches(text, patterns):
    if not isinstance(text, str):
        return 0
    t = text.lower()
    return sum(1 for p in patterns if re.search(p, t))


def value_sentences(text):
    """Keep only sentences mentioning price/value; else the first 400 characters."""
    if not isinstance(text, str):
        return ''
    sentences = re.split(r'[.!?\n]+', text)
    keep = [s.strip() for s in sentences if any(k in s.lower() for k in VALUE_KW)]
    return ' '.join(keep) if keep else text[:400]


def main():
    files = sorted((PRIVATE / "raw").glob("*_trustpilot.csv"))
    if not files:
        sys.exit("No raw files in private/raw/. Raw review text is not published; see data/README.md.")
    df = pd.concat([pd.read_csv(f, encoding='latin-1', low_memory=False) for f in files],
                   ignore_index=True)
    # Brands scraped in both collection waves appear twice
    df = df.drop_duplicates(subset=['date', 'brand', 'rating', 'text'])
    df['brand'] = df['brand'].str.replace('\x8e', 'é', regex=False)
    df['date'] = pd.to_datetime(df['date'])
    df['segment'] = df['segment'].replace({'french_fashion': 'contemporary_fashion',
                                           'denim_heritage': 'contemporary_fashion'})

    df['full_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
    df['sust_pos'] = df['full_text'].apply(lambda x: count_matches(x, SUST_POS))
    df['sust_neg'] = df['full_text'].apply(lambda x: count_matches(x, SUST_NEG))
    df['sust_score'] = df['sust_pos'] - df['sust_neg']

    analyzer = SentimentIntensityAnalyzer()
    df['value_pool'] = df['text'].apply(value_sentences)
    df['value_vader'] = df['value_pool'].apply(
        lambda t: analyzer.polarity_scores(t)['compound'] if isinstance(t, str) and t.strip() else 0.0)

    out = PRIVATE / "df_enriched.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"Saved {out}: {len(df):,} reviews, {df['brand'].nunique()} brands")


if __name__ == '__main__':
    main()
