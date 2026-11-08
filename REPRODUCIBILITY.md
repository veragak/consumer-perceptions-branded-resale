# Reproducibility notes

This file documents how the code in this repository was checked against the thesis PDF, and every point where the two differ.

## Verification against the thesis

`code/99_check_against_thesis.py` compares each number printed in the thesis tables with the value the code produces. It writes [`results/verification_report.md`](results/verification_report.md).

| Result of 594 checks | Count |
|---|---|
| Match the thesis | 549 |
| Differ, with a known reason | 45 |
| Differ, unexplained | 0 |

The data preparation was checked as well. The scoring code in `code/02_score_reviews.py`, applied to the raw scraped reviews, reproduces the sustainability score and the value VADER score of all 49,736 reviews exactly. The LDA script reproduces Figure 2 and Table A.4 exactly from the review text.

The 549 matches include 23 numbers that depend on random resampling and agree within tolerance, and 3 p-values printed with a different convention. Each of the 45 differences is listed in the report with its reason, and they are listed below.

## Differences between the PDF and the code

Rebuilding the analysis from scratch surfaced the points below where the PDF and the code differ. None of them change the main conclusions of Study 1 or Study 2. Point 3 changes how Appendix A.8 should be read.

1. **Synthetic DiD standard errors are random.** The per-brand effects are reproduced exactly. The placebo standard errors are random, and the thesis run had no fixed seed. Because Tables 3 and 4 average brands with weights 1/SE², the pooled numbers move with each run. `code/26_synthdid_pool_thesis_se.R` uses the standard errors saved from the thesis run and rebuilds Tables 3 and 4 exactly. A fresh run gives -0.063 (p = 0.48) for rating, -0.017 (p = 0.06) for sustainability, and -0.088 (p = 0.005) for value VADER. The signs and the significance pattern are the same. See `results/thesis_run/README.md`.
2. **Table A.7 is affected the same way.** A fresh run gives -0.135 (p = 0.14), -0.034 (p = 0.001) and -0.102 (p = 0.003). The thesis reports -0.167 (p = 0.079), -0.031 (p = 0.003) and -0.111 (p = 0.002). All effects are still negative, and sustainability and value stay significant. The thesis run did not save per-brand results for this check, so it cannot be rebuilt exactly.
3. **Tables A.8a and A.8b mix two runs.** Their discount rows and R² come from the final discount data, the ten-listing averages in Appendix A.3. The integration, messaging and services rows, and most of A.8b, come from an earlier run that used rough discount guesses. The code uses the final data throughout and matches the file the original script saved. With the final data, the integration x messaging interaction on raw rating change is -0.407 with p = 0.129, so it is **not significant**. The thesis reports p = 0.020. Appendix A.8 and the limitations section say the two outcome definitions point to different significant interactions. With the final data, the raw-change version finds no significant interaction, so the sensitivity check no longer contradicts the main result.
4. **Table 5 swaps two rows of raw changes.** The three Δ values of Ba&sh and Balzac Paris are swapped in the PDF. The data give Balzac Paris +1.912 stars and Ba&sh +1.812, which agrees with the thesis text: "Balzac Paris … its 1.9-star raw improvement". The synthetic DiD columns are correct.
5. **Table 2 has one typo.** The SD of the sustainability score for control brands after the event is 0.341, not 0.343.
6. **Table 6 p-values use the normal distribution, Table 7 uses the t distribution.** Three Table 6 cells use the t distribution. Coefficients and standard errors are identical either way. No conclusion changes. `results/tables/table6_moderation.csv` reports both.
7. **The "Within R²" in Table A.6 is the full R², including the fixed effects.** The true within R² is about 0.001. `tableA6_twfe.csv` reports both.
8. **The time axis of Figures 3 and 6 is in years.** It is labelled "quarters" in the thesis. The points are one quarter apart, so the axis running from -6 to 4 covers six years before launch and four after.
9. **Figure 4's error bars are ±1 standard error.** The thesis does not say what they show. A 95% interval would be about twice as wide.
10. **Figure 5 has one pre-launch point whose interval excludes zero.** At event time -3 the placebo estimate is 0.45 with a 95% interval of [0.06, 0.83]. The other two pre-launch points include zero. The thesis says no significant pre-treatment divergence remains. That holds for event times -2 and -1, not for -3.
11. **The LDA settings in Section 4.3.1 are not the ones the code used.** The thesis text describes 3,000 unigrams and bigrams, a minimum of 30 reviews and a maximum of 60%. The figure and Table A.4 were made with 1,000 single words, a minimum of 2 reviews and a maximum of 95%. The code is authoritative because it reproduces Table A.4 exactly.
12. **The sustainability dictionary in Appendix A.2 omits "natural".** The code's 38 patterns include it, and they split some stems into spelling variants, such as pre-owned and preowned. The thesis note on false positives mentions "natural".
13. **Discount depth uses ten listings per brand.** The Table A.3 note says five matched items, but the values are ten-listing means, as Section 4.2.2 states.
14. **An older comparison table was dropped.** An earlier hand-written Callaway & Sant'Anna average, in the original `table_cs_vs_twfe.csv`, averaged over all event times without a cap and gave wrong values. The thesis already used the `did` package estimates instead. That table is not included here.

15. **Table A.4a was recomputed.** No script for the perplexity table printed in the thesis was found in the project files. `code/05_lda_model_selection.py` recomputes it with the settings that produced the thesis topics. See `results/tables/tableA4a_lda_model_selection.csv`. The recomputed table supports the choice of seven topics. Held-out perplexity improves most from 6 to 7 topics, 352.5 to 336.2, and only slightly after that: 335.2, 331.2 and 329.7 for 8, 9 and 10 topics. From 8 topics on, the extra topics split into brand names and product words. The values are on a different scale from the printed table, about 330 to 350 instead of 2,500 to 2,850, so the printed numbers should not be compared with these.
