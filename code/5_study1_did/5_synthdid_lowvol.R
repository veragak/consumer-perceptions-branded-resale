# =============================================================================
# 5_study1_did/5_synthdid_lowvol.R  -  Robustness: drop low-volume control brands
#
# Thesis: Appendix A.7 (Table A.7)
# Produces: results/tables/tableA7_synthdid_excl_lowvol.csv
#
# Four control brands have fewer than 150 reviews (Tommy Hilfiger, Fred Perry,
# Jottnar, Vuori), so their quarterly averages are noisy. This re-runs exactly
# the synthetic DiD of 5_study1_did/4_synthdid.R with those four removed from the donor pool
# (23 instead of 27 controls) and compares the pooled ATTs with the main result.
# =============================================================================
source("code/shared/common.R")

df    <- did_sample(load_reviews())
df    <- df[!df$brand %in% LOW_VOLUME_CONTROLS, ]
panel <- brand_quarter_panel(df)

sdid   <- run_synthdid_all(panel, verbose = FALSE)
pooled <- sdid$results %>% group_by(outcome) %>% group_modify(~ pool_ivw(.x)) %>% ungroup()
cat("Control brands in donor pool:", length(sdid$controls), "\n")

main <- read_csv(file.path(TABLE_DIR, "table3_synthdid_pooled.csv"), show_col_types = FALSE)
out <- main %>% select(outcome, att_main = att, p_main = p) %>%
  left_join(pooled %>% select(outcome, att_excl_lowvol = att, p_excl_lowvol = p), by = "outcome")
save_table(out, "tableA7_synthdid_excl_lowvol.csv")
print(as.data.frame(out), digits = 3)
