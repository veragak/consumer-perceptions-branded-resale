# Code

The code is organised in one folder per stage of the thesis, in the order the work was done. Inside each folder, files are numbered in the order they run.

```
code/
├── 1_data_collection/     scrape Trustpilot reviews
├── 2_data_preparation/    turn review text into scores; build the public dataset
├── 3_text_analysis/       what do reviews talk about? (LDA) + robustness of the VADER score
├── 4_descriptives/        describe the sample (Tables 1, 2, Figures 1, A.5)
├── 5_study1_did/          Study 1: did resale launches change perceptions?
├── 6_study2_moderation/   Study 2: do resale design choices explain the differences?
├── 7_verification/        compare every reproduced number with the thesis PDF
└── shared/                settings and helper functions used by all scripts
```

To run everything, from the repository root:

```bash
bash run_all.sh
```

Every script starts with a short header that names the thesis section, lists what it produces, and explains the method step by step.

## What each script does

### 1_data_collection
The Trustpilot scrapers and brand lists. See [`1_data_collection/README.md`](1_data_collection/README.md) for how the data and the brands were chosen.

### 2_data_preparation
| Script | What it does | Thesis |
|---|---|---|
| `1_score_reviews.py` | Computes the sustainability score (dictionary) and value VADER score for each review. Needs the raw text | 4.2.1, A.2 |
| `2_export_public_data.R` | Removes title and text to create the public `data/reviews_scored.csv` | n/a |
| `3_discount_depth.py` | Computes each brand's resale discount from 10 hand-collected price pairs | 4.2.2, A.3 |

### 3_text_analysis
These scripts need the review text, which is not published. Their outputs are included in `results/`.

| Script | What it does | Thesis |
|---|---|---|
| `1_lda_topics.py` | Seven-topic LDA model: what reviewers write about, before and after launch | Figure 2, A.4b, A.4c |
| `2_lda_model_selection.py` | Compares 5 to 10 topics to justify choosing seven | A.4a |
| `3_vader_cutoff_check.py` | Checks that the 400-character VADER fallback does not drive the results | 4.2.1 |

### 4_descriptives
| Script | What it does | Thesis |
|---|---|---|
| `1_descriptives.R` | Sample counts per brand and outcome means by group and period | Tables 1, 2, A.1 |
| `2_figures_descriptive.py` | Before/after bar chart, and sustainability mentions by brand | Figures 1, A.5 |

### 5_study1_did
| Script | What it does | Thesis |
|---|---|---|
| `1_twfe_did.R` | Standard difference-in-differences with brand and quarter fixed effects | Table 3, A.6 |
| `2_callaway_santanna.R` | DiD for staggered launch dates (Callaway & Sant'Anna) | Table 3 |
| `3_cs_event_study.R` | Effect by quarter before and after launch, to check parallel trends | Figure 5 |
| `4_synthdid.R` | **Main method.** Synthetic DiD per brand, pooled overall and by segment | Tables 3, 4, 5 |
| `5_synthdid_lowvol.R` | Robustness: synthetic DiD without the four smallest control brands | A.7 |
| `6_synthdid_pool_thesis_se.R` | Rebuilds Tables 3 and 4 exactly, using the thesis run's standard errors | Tables 3, 4 |
| `7_figures_synthdid.py` | Event-time chart, per-brand effects, pre-launch fit | Figures 3, 4, 6 |

Scripts 5 to 7 and Study 2 use the per-brand results of `4_synthdid.R`, so it runs first.

### 6_study2_moderation
| Script | What it does | Thesis |
|---|---|---|
| `1_moderation.R` | Regresses each brand's effect on the four design choices, plus the integration × messaging model | Tables 6, 7 |
| `2_raw_change.R` | Raw before/after changes per brand, and the same regressions on them | Table 5, A.8 |

### 7_verification
| Script | What it does |
|---|---|
| `check_against_thesis.py` | Compares every number printed in the thesis tables with the code's output and writes `results/verification_report.md` |

### shared
| File | What it does |
|---|---|
| `common.R` | Loaded by every R script: data loading, sample rules (excluded brands), the synthetic DiD loop, regression table helpers |
| `common.py` | Loaded by every Python script: folder locations and chart colours |

## The three estimators in Study 1

The question is whether a brand's reviews change after it launches resale, compared with what would have happened otherwise. "Otherwise" is estimated from control brands, in three ways:

1. **Two-way fixed effects** (`1_twfe_did.R`): one regression on all reviews, with a dummy for "treatment brand after launch" plus brand and quarter fixed effects. It is simple, but it assumes the 27 control brands are a fair comparison as they are, and that every brand's effect looks the same no matter when it launched.
2. **Callaway & Sant'Anna** (`2_callaway_santanna.R`, `3_cs_event_study.R`): groups brands by launch quarter and compares each group only with never-treated brands. This fixes the problem of staggered timing, but not the problem that control brands differ from treatment brands.
3. **Synthetic DiD** (`4_synthdid.R`): for each treatment brand separately, it weights the control brands, and the pre-launch quarters, so the weighted controls follow that brand's pre-launch path as closely as possible. Then it takes a DiD. The 19 brand effects are averaged with inverse-variance weights. This is the thesis's main estimator, because the raw control group starts from a different baseline (Section 5.1).

Study 2 (`6_study2_moderation/1_moderation.R`) takes each brand's synthetic DiD effect as the outcome and asks whether the resale design variables explain why it is larger for some brands than for others.

## Randomness

Two steps use random draws: the placebo standard errors in synthetic DiD and the bootstrap standard errors in Callaway & Sant'Anna. The seeds are fixed, but the original thesis runs had none, so their draws cannot be regenerated. Per-brand effects are unaffected. The pooled synthetic DiD numbers in Tables 3 and 4 weight brands by 1/SE², so they move slightly with new draws. `6_synthdid_pool_thesis_se.R` re-pools the effects with the saved thesis-run standard errors and gives the printed tables exactly; see `results/thesis_run/README.md`.
