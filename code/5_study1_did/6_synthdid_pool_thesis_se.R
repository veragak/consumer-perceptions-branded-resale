# =============================================================================
# 5_study1_did/6_synthdid_pool_thesis_se.R  -  rebuild Tables 3 and 4 exactly as printed
#
# Thesis: Table 3 (synthetic DiD column) and Table 4
# Produces:
#   results/tables/table3_synthdid_pooled_thesis_se.csv
#   results/tables/table4_synthdid_by_segment_thesis_se.csv
#
# Pooled synthetic DiD effects are inverse-variance weighted averages of the
# 19 brand effects, so they depend on the per-brand placebo standard errors,
# which are random (see results/thesis_run/README.md).
#
# This script takes the brand effects reproduced by 5_study1_did/4_synthdid.R, checks that
# they equal the ones saved in the thesis run, and pools them with the SEs from
# that thesis run. The result matches Tables 3 and 4 of the thesis exactly.
# =============================================================================
source("code/shared/common.R")

new    <- read_csv(file.path(TABLE_DIR, "synthdid_by_brand.csv"), show_col_types = FALSE)
thesis <- read_csv("results/thesis_run/synthdid_by_brand_thesis_run.csv", show_col_types = FALSE)

d <- new %>% select(brand, outcome, segment, att) %>%
  inner_join(thesis %>% select(brand, outcome, att_thesis = att, se), by = c("brand", "outcome"))
stopifnot(nrow(d) == 57)
max_diff <- max(abs(d$att - d$att_thesis))
cat(sprintf("Brand effects compared: %d, largest difference from thesis run: %.4f\n", nrow(d), max_diff))
stopifnot(max_diff < 1e-3)

t3 <- d %>% group_by(outcome) %>% group_modify(~ pool_ivw(.x)) %>% ungroup()
t4 <- d %>% group_by(segment, outcome) %>% group_modify(~ pool_ivw(.x)) %>% ungroup()
save_table(t3, "table3_synthdid_pooled_thesis_se.csv")
save_table(t4, "table4_synthdid_by_segment_thesis_se.csv")
print(as.data.frame(t3), digits = 3); print(as.data.frame(t4), digits = 3)
