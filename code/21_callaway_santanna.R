# =============================================================================
# 21_callaway_santanna.R  -  Study 1: staggered-adoption DiD
#
# Thesis: Section 4.3.2 (method), Section 5.2 and Table 3, column "C&S ATT"
# Produces: results/tables/table3_callaway_santanna.csv
#
# Brands launched resale in different quarters (2018-2025). A standard TWFE
# DiD can be biased when timing is staggered, because already-treated brands
# end up acting as controls. The Callaway & Sant'Anna (2021) estimator compares
# each launch cohort only with never-treated (control) brands, then averages the
# cohort effects into one ATT. Implemented with the `did` R package on the
# brand-quarter panel.
#
# The ATTs are deterministic. Their standard errors come from the package's
# multiplier bootstrap, which is random; the seed is fixed here, but the thesis
# run had none, so SEs/p-values differ slightly from Table 3 (all remain far
# from significance).
# =============================================================================
source("code/_common.R")
suppressPackageStartupMessages(library(did))

df    <- did_sample(load_reviews())
panel <- brand_quarter_panel(df)
panel$first_treat <- ifelse(is.na(panel$first_treat_q), 0, panel$first_treat_q)  # 0 = never treated
panel$id_num      <- as.integer(as.factor(panel$brand))

rows <- list()
for (y in OUTCOMES) {
  set.seed(2026)
  cs  <- att_gt(yname = y, tname = "quarter_n", idname = "id_num", gname = "first_treat",
                data = as.data.frame(panel), control_group = "nevertreated",
                est_method = "ipw", panel = FALSE, print_details = FALSE)
  agg <- aggte(cs, type = "simple", na.rm = TRUE)
  rows[[y]] <- data.frame(outcome = y, att = agg$overall.att, se = agg$overall.se,
                          p = 2 * (1 - pnorm(abs(agg$overall.att / agg$overall.se))))
}
out <- bind_rows(rows)
save_table(out, "table3_callaway_santanna.csv")
print(out, digits = 3)
