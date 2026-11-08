# Code

Scripts are numbered in the order they run. Run them all from the repository root:

```bash
bash run_all.sh
```

Every script starts with a header that names the thesis section, the tables and figures it produces, and what the method does. R scripts share `_common.R` and Python scripts share `_common.py`. Both hold the data paths, the sample rules, such as excluded brands, and the helper functions. This way every script uses the same sample.

## Pipeline

```
Trustpilot ──► 01_data_collection/ ──► private/raw/*.csv           (not published)
                                            │
                              02_score_reviews.py: sustainability score + value VADER
                                            │
                                   private/df_enriched.csv          (not published: has review text)
                                   │                    │
                    03_export_public_data.R      04-06: topic model, VADER check
                                   │
                         data/reviews_scored.csv     (public, no text)
                                   │
       ┌──────────────┬────────────┼──────────────────┬─────────────────┐
  10, 11            20, 21, 22     23 synthetic DiD    24 robustness     30, 31
  descriptives      TWFE, C&S      ──► by-brand ATTs ──► 25 figures ──► Study 2
```

## Scripts

| Script | Thesis section | Produces |
|---|---|---|
| `01_data_collection/` | 4.1 | Raw reviews. See the README in that folder |
| `02_score_reviews.py` | 4.2.1, A.2 | Sustainability and value-sentiment scores. Needs raw text |
| `03_export_public_data.R` | n/a | `data/reviews_scored.csv`, by dropping the text columns |
| `04_lda_topics.py` | 4.3.1, 5.1, A.4 | Figure 2, Tables A.4b and A.4c. Needs raw text |
| `05_lda_model_selection.py` | A.4 | Table A.4a, recomputed: held-out perplexity for 5 to 10 topics. Needs raw text |
| `06_vader_cutoff_check.py` | 4.2.1 | Robustness of value VADER to the 200-600 character fallback. Needs raw text |
| `07_discount_depth.py` | 4.2.2, A.3 | Discount-depth moderator from 210 hand-collected price pairs, plus the 5-vs-10 listing check |
| `10_descriptives.R` | 4.1, 5.1, A.1 | Tables 1, 2 and A.1 |
| `11_figures_descriptive.py` | 5.1, A.5 | Figures 1 and A.5 |
| `20_twfe_did.R` | 5.2, A.6 | Table 3 TWFE column, Table A.6, pooled pre-trend test |
| `21_callaway_santanna.R` | 5.2 | Table 3 C&S column |
| `22_cs_event_study.R` | 5.2 | Figure 5 |
| `23_synthdid.R` | 4.3.2, 5.2 | Table 3 SDID column, Table 4, Table 5 ATT columns, pre-launch fit |
| `24_synthdid_lowvol.R` | A.7 | Table A.7 |
| `25_figures_synthdid.py` | 5.2 | Figures 3, 4 and 6 |
| `26_synthdid_pool_thesis_se.R` | 5.2 | Tables 3 and 4 exactly as printed, using the thesis run's placebo SEs |
| `30_study2_moderation.R` | 4.3.3, 5.3 | Tables 6 and 7 |
| `31_study2_raw_change.R` | 5.2, A.8 | Table 5, Tables A.8a and A.8b, peer-to-peer sensitivity check |
| `99_check_against_thesis.py` | all | `results/verification_report.md`, every reproduced number compared with the PDF |

Scripts 24, 25, 26, 30 and 31 read `results/tables/synthdid_by_brand.csv`, so run `23_synthdid.R` first.

## The three estimators in Study 1

The question is whether a brand's reviews change after it launches resale, compared with what would have happened otherwise. "Otherwise" is estimated from control brands, in three ways:

1. **Two-way fixed effects (`20`)**: one regression on all reviews, with a dummy for "treatment brand after launch" plus brand and quarter fixed effects. It is simple, but it assumes the 27 control brands are a fair comparison as they are, and that every brand's effect looks the same no matter when it launched.
2. **Callaway & Sant'Anna (`21`, `22`)**: groups brands by launch quarter and compares each group only with never-treated brands. This fixes the problem of staggered timing, but not the problem that control brands differ from treatment brands.
3. **Synthetic DiD (`23`)**: for each treatment brand separately, it weights the control brands, and the pre-launch quarters, so the weighted controls follow that brand's pre-launch path as closely as possible. Then it takes a DiD. The 19 brand effects are averaged with inverse-variance weights. This is the thesis's main estimator, because the raw control group starts from a different baseline (Section 5.1).

Study 2 (`30`) takes each brand's synthetic DiD effect as the outcome and asks whether the resale design variables explain why it is larger for some brands than for others.

## Randomness

Two steps use random draws: the placebo standard errors in synthetic DiD and the bootstrap standard errors in Callaway & Sant'Anna. The seeds are now fixed, but the original thesis runs had no fixed seed, so their draws cannot be regenerated. Per-brand effects are unaffected. The pooled synthetic DiD numbers in Tables 3 and 4 are affected, because they weight brands by 1/SE². `26_synthdid_pool_thesis_se.R` therefore re-pools the reproduced effects with the saved thesis-run SEs, in `results/thesis_run/`, which gives the printed tables exactly. The repository README explains this, and `results/verification_report.md` lists every comparison.
