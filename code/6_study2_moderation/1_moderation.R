# =============================================================================
# 6_study2_moderation/1_moderation.R  -  Study 2: do resale design choices explain the effect?
#
# Thesis: Section 4.3.3 (method), Section 5.3 (results)
# Produces:
#   Table 6 -> results/tables/table6_moderation.csv
#   Table 7 -> results/tables/table7_interaction.csv
#   Robustness mentioned in Section 5.3 (each moderator alone + segment)
#           -> results/tables/table6_single_moderator.csv
#
# Unit of analysis: the 19 treatment brands. The outcome is each brand's
# synthetic DiD effect from Study 1 (results/tables/synthdid_by_brand.csv, so run
# 5_study1_did/4_synthdid.R first). This outcome already nets out the brand's own baseline and
# the trend of its synthetic control, so what is left to explain is the part of
# the change linked to the resale launch.
#
# Moderators (coded by hand from each brand's resale site, Appendix A.3,
# data/treatment_brands_moderators.csv):
#   integration (1-5)  how visibly used items sit next to new ones
#   messaging  (1-5)   how strongly resale is framed as sustainability
#   discount   (%)     average resale discount vs. new retail price
#   services   (1-3)   repair / warranty / trade-in on top of basic resale
#
# Table 6:  ATT_b = b0 + b1 integration + b2 messaging + b3 discount + b4 services
#                   + segment dummies (contemporary fashion = reference) + e
# Table 7:  ATT_b = b0 + b1 integration + b2 messaging + b3 integration x messaging + e
# OLS with HC1 robust standard errors, one model per outcome.
#
# p-values: Table 6 in the thesis prints normal-based p-values (column p_normal
# here); Table 7 prints t-based ones (column p). Coefficients and SEs are the
# same either way. With 12-15 residual degrees of freedom the t-based p-values
# are slightly larger; no Table 6 coefficient is significant under either.
# =============================================================================
source("code/shared/common.R")

sdid <- read_csv(file.path(TABLE_DIR, "synthdid_by_brand.csv"), show_col_types = FALSE)
mods <- load_moderators()

s2 <- sdid %>% select(brand, outcome, att) %>%
  pivot_wider(names_from = outcome, values_from = att) %>%
  inner_join(mods, by = "brand") %>%
  mutate(seg_outdoor = as.integer(segment == "outdoor_athletic"),
         seg_premium = as.integer(segment == "premium_fashion"),
         int_x_msg   = integration * messaging)
stopifnot(nrow(s2) == 19)

# -- Table 6: joint model ----------------------------------------------------------
t6 <- bind_rows(lapply(OUTCOMES, function(y) {
  m <- lm(as.formula(paste(y, "~ integration + messaging + discount + services + seg_outdoor + seg_premium")), data = s2)
  hc1_table(m, paste("ATT", y))
}))
save_table(t6, "table6_moderation.csv")

# -- Each moderator on its own (with segment controls) ------------------------------
single <- bind_rows(lapply(OUTCOMES, function(y) bind_rows(lapply(
  c("integration", "messaging", "discount", "services"), function(v) {
    m <- lm(as.formula(paste(y, "~", v, "+ seg_outdoor + seg_premium")), data = s2)
    hc1_table(m, paste("ATT", y)) %>% filter(variable == v)
  }))))
save_table(single, "table6_single_moderator.csv")

# -- Table 7: integration x messaging ---------------------------------------------
t7 <- bind_rows(lapply(OUTCOMES, function(y) {
  m <- lm(as.formula(paste(y, "~ integration + messaging + int_x_msg")), data = s2)
  hc1_table(m, paste("ATT", y))
}))
save_table(t7, "table7_interaction.csv")

cat("\nTable 6\n"); print(t6[, c("model", "variable", "beta", "se", "p", "p_normal", "adj_r2")], digits = 3)
cat("\nSingle-moderator models (min p):", round(min(single$p), 3), "\n")
cat("\nTable 7\n"); print(t7[, c("model", "variable", "beta", "se", "p", "adj_r2")], digits = 3)
