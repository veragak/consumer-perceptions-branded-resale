# Data

Everything the analysis needs is in this folder. All scripts in `code/` read from here.

| File | Rows | What it is |
|---|---|---|
| `reviews_scored.csv` | 49,736 | One row per Trustpilot review, with the three outcome scores |
| `treatment_brands_moderators.csv` | 21 | Treatment brands: launch date, platform, and the four hand-coded design variables (thesis Appendix A.3) |
| `control_brands.csv` | 27 | Control brands: segment, matched treatment brands, pseudo-event date (thesis Appendix A.1) |
| `discount_depth_listings.csv` | 210 | 10 resale listings per treatment brand with the matching new retail price, in euros. Source of the discount moderator |

## `reviews_scored.csv`

Reviews of 48 fashion and outdoor brands, posted between March 2011 and April 2026, collected from Trustpilot.

| Column | Meaning |
|---|---|
| `review_id` | Row number |
| `date` | Date the review was posted |
| `brand` | Brand reviewed |
| `segment` | `contemporary_fashion`, `premium_fashion` or `outdoor_athletic` |
| `group` | `treatment` if the brand runs its own resale programme, `control` otherwise |
| `period` | Treatment brands: `pre` or `post`, relative to that brand's resale launch. Control brands: `control` |
| `rating` | Star rating, 1 to 5 |
| `sust_pos` | Number of positive sustainability patterns found in title and text |
| `sust_neg` | Number of greenwashing-scepticism patterns found |
| `sust_score` | Sustainability language score, `sust_pos - sust_neg` |
| `value_vader` | VADER sentiment, from -1 to 1, of the sentences about price or value. Falls back to the first 400 characters when no such sentence exists |

How the two text scores are computed is explained at the top of `code/02_score_reviews.py`.

### What was removed and why

The review title, review text and reviewer country are not published. Review text is written by individual Trustpilot users, and republishing it in bulk raises privacy and terms-of-use concerns. The scores derived from the text are kept, so every result in the thesis can be reproduced from this file except one. The LDA topic model, Figure 2 and Appendix A.4, needs the words themselves. Its outputs are included in `results/`, and its code is in `code/04_lda_topics.py`.

To rerun the text-based steps, put the scraped files in `private/raw/` and run `code/02_score_reviews.py`. Git ignores the `private/` folder.

### Provenance

`code/03_export_public_data.R` created this file from the author's scored dataset, which still contains the text. The export only drops columns. No rows or values were removed or changed. Applying `code/02_score_reviews.py` to the raw scraped reviews gives exactly the `sust_score` and `value_vader` in this file, for every review.

## `treatment_brands_moderators.csv`

The author coded these variables from each brand's resale website, press releases and marketing material around the launch. Coding followed a fixed codebook and was finished before looking at the outcome data (thesis Section 4.2.2).

| Column | Meaning |
|---|---|
| `resale_platform` | Infrastructure provider: Trove, Faume or Archive |
| `launch` | Month the resale programme launched |
| `integration` | 1 = separate website, not linked from the main site. 5 = used and new items on the same product page |
| `messaging` | 1 = purely commercial framing. 5 = resale is the core of the brand's sustainability identity |
| `discount` | Mean percentage discount of 10 resale listings against the matching new retail price |
| `discount_sd` | Standard deviation of that discount across the 10 listings |
| `services` | 1 = basic resale only. 2 = one extra service. 3 = two or more of repair, warranty and trade-in |

`discount` and `discount_sd` are computed from `discount_depth_listings.csv` by `code/07_discount_depth.py`. For each of the 10 listings, discount = (retail − resale) / retail × 100. The listings were collected by hand in May 2026, matching each resale item to the same item at current retail price.

Michael Kors and Steve Madden run peer-to-peer resale, where sellers set the prices. Their discount reflects market prices, not a brand decision. `code/31_study2_raw_change.R` checks the results without them.

## `control_brands.csv`

Control brands are in the same segments as the treatment brands but have no confirmed own resale programme. A control brand has no launch date. For the descriptive pre/post comparisons in Table 2, Figure 1 and Figure 2, each control brand inherits the launch date of the treatment brand it is matched to. That inherited date is its `pseudo_event_date`. The causal estimators in Study 1 do not use these dates. They compare each treatment brand with all 27 controls in the same calendar quarters.
