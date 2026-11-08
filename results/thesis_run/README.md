# Saved outputs of the original thesis run

These five files were written by the original analysis scripts when the thesis numbers were produced. They are kept unchanged as a reference.

| File | Thesis |
|---|---|
| `synthdid_by_brand_thesis_run.csv` | Per-brand synthetic DiD effect and placebo SE (Table 5, Figure 4) |
| `synthdid_pooled_thesis_run.csv` | Table 3, synthetic DiD column |
| `synthdid_by_segment_thesis_run.csv` | Table 4 |
| `callaway_santanna_thesis_run.csv` | Table 3, C&S column |
| `study2_raw_change_thesis_run.csv` | Tables A.8a and A.8b, as written by the original script |

## Why they are needed

The per-brand synthetic DiD **effects** are deterministic. `code/5_study1_did/4_synthdid.R` reproduces all 57 of them exactly, for 19 brands and 3 outcomes.

The per-brand **standard errors** come from the placebo method, which reassigns treatment to randomly chosen control brands. They change from run to run, by up to about ±30% for a single brand. Table 3 and Table 4 average the brand effects with inverse-variance weights, 1/SE². So the pooled numbers depend on which random SEs a run happened to draw. The thesis run had no fixed seed, so its draws cannot be regenerated.

`code/5_study1_did/6_synthdid_pool_thesis_se.R` combines the effects reproduced by `5_study1_did/4_synthdid.R` with the SEs from `synthdid_by_brand_thesis_run.csv`. It returns Tables 3 and 4 exactly as printed in the thesis. The fresh run in `results/tables/` shows how much the pooled numbers move with new placebo draws. The signs and the significance pattern stay the same.

## Appendix A.8

`study2_raw_change_thesis_run.csv` is the output of the original Study 2 script, which used the final ten-listing discount data. `code/6_study2_moderation/2_raw_change.R` reproduces it exactly. The printed Tables A.8a and A.8b in the thesis PDF differ from this file in some rows, because they partly come from an earlier run. See the main README.
