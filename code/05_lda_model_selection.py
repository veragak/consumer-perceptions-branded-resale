"""
05_lda_model_selection.py - how many topics? (recomputed Table A.4a)

Thesis: Appendix A.4, Table A.4a
Produces: results/tables/tableA4a_lda_model_selection.csv

Fits the same LDA as 04_lda_topics.py with 5, 6, 7, 8, 9 and 10 topics and
compares held-out perplexity: the model is trained on 90% of the reviews and
scored on the other 10%. Lower perplexity means the model predicts unseen
reviews better. Perplexity usually keeps falling as topics are added, so the
choice also rests on whether the topics are readable, which is judged from the
top words printed for each solution.

Note: no script for the perplexity table printed in the thesis (Table A.4a) was
found in the project files. This script recomputes it with the settings that
produced the thesis topics, so the numbers differ from the printed table.

Result: perplexity improves most from 6 to 7 topics (352.5 -> 336.2) and only
slightly after that (335.2, 331.2, 329.7), and from 8 topics on the extra
topics split into brand and product words. This supports the 7-topic choice.

Needs the review text (private/df_enriched.csv).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent))
from _common import PRIVATE, TABLES

src = PRIVATE / "df_enriched.csv"
if not src.exists():
    sys.exit("private/df_enriched.csv not found: this script needs the unpublished review text.")

df = pd.read_csv(src, low_memory=False)
text = (df['title'].fillna('') + ' ' + df['full_text'].fillna('')).str.strip()
text = text[text.str.split().str.len() >= 5]
train, test = train_test_split(text, test_size=0.10, random_state=42)

vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
X_train = vectorizer.fit_transform(train)
X_test = vectorizer.transform(test)
words = vectorizer.get_feature_names_out()
print(f"Train {X_train.shape[0]:,} reviews, test {X_test.shape[0]:,} reviews")

rows = []
for k in range(5, 11):
    lda = LatentDirichletAllocation(n_components=k, random_state=42, learning_offset=50, max_iter=30)
    lda.fit(X_train)
    perp = lda.perplexity(X_test)
    tops = [' '.join(words[j] for j in comp.argsort()[-6:][::-1]) for comp in lda.components_]
    rows.append({'n_topics': k, 'heldout_perplexity': round(perp, 1), 'topics_top_words': ' | '.join(tops)})
    print(f"\n{k} topics: held-out perplexity {perp:,.1f}")
    for t in tops:
        print("   ", t)

pd.DataFrame(rows).to_csv(TABLES / "tableA4a_lda_model_selection.csv", index=False)
print("\nSaved", TABLES / "tableA4a_lda_model_selection.csv")
