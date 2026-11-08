# =============================================================================
# 5_study1_did/4_synthdid.R  -  Study 1 main estimator: synthetic difference-in-differences
#
# Thesis: Section 4.3.2 (method), Section 5.2 (results)
# Produces:
#   Table 3, column "Synthetic DiD"   -> results/tables/table3_synthdid_pooled.csv
#   Table 4  (ATT by segment)         -> results/tables/table4_synthdid_by_segment.csv
#   Table 5, three "Synth. DiD ATT" columns and Figure 4 input
#                                     -> results/tables/synthdid_by_brand.csv
#   Input for Figures 3 and 6 (pre-launch fit of raw vs synthetic control)
#                                     -> results/tables/synthdid_pretrend_fit.csv
#   Pre-launch gap numbers quoted in Section 5.2 (1.15 -> 1.03 stars, etc.)
#                                     -> results/tables/synthdid_pretrend_gaps.csv
#
# What it does
#   1. Average reviews to one value per brand and quarter.
#   2. For each of the 19 treatment brands separately, build a synthetic control
#      out of the 27 control brands (Arkhangelsky et al., 2021) and estimate the
#      brand's treatment effect (ATT) on each of the three outcomes.
#   3. Pool the 19 brand estimates with inverse-variance weights (Table 3) and,
#      separately, within each market segment (Table 4).
#   4. Save, for every pre- and post-launch quarter, the treated brand's value,
#      the plain average of the controls, and the synthetic-weighted average.
#      This shows how much the reweighting closes the pre-launch gap (Section 5.2).
#
# Note: placebo standard errors are based on random permutations. The seed is
# fixed here; the thesis run had no fixed seed, so SEs and p-values can differ
# from the thesis in the third decimal. Point estimates are identical.
# =============================================================================
source("code/shared/common.R")

df    <- did_sample(load_reviews())
panel <- brand_quarter_panel(df)
mods  <- load_moderators()

sdid <- run_synthdid_all(panel)
by_brand <- sdid$results %>%
  left_join(mods %>% select(brand, segment), by = "brand")
save_table(by_brand, "synthdid_by_brand.csv")

# -- Table 3: pooled ATT across the 19 brands -------------------------------------
pooled <- by_brand %>% group_by(outcome) %>% group_modify(~ pool_ivw(.x)) %>% ungroup()
save_table(pooled, "table3_synthdid_pooled.csv")
cat("\nTable 3 (synthetic DiD column):\n"); print(as.data.frame(pooled), digits = 3)

# -- Table 4: pooled ATT within each segment -------------------------------------
by_segment <- by_brand %>% group_by(segment, outcome) %>%
  group_modify(~ pool_ivw(.x)) %>% ungroup()
save_table(by_segment, "table4_synthdid_by_segment.csv")
cat("\nTable 4:\n"); print(as.data.frame(by_segment), digits = 3)

# -- Pre-launch fit: raw control mean vs synthetic control ----------------------
# For every brand, outcome and quarter in the estimation window: the treated
# brand's value, the plain average of the 27 controls, and the synthetic
# control (controls weighted by omega). event_time is measured in YEARS
# relative to the launch quarter (quarters are 0.25 apart).
fit_rows <- list()
for (key in names(sdid$fits)) {
  f <- sdid$fits[[key]]
  q <- as.numeric(colnames(f$Y))
  fit_rows[[key]] <- data.frame(
    outcome       = sub(" .*$", "", key),
    brand         = sub("^[a-z_]+ ", "", key),
    event_time    = q - f$treat_q,
    treated       = f$Y[f$N0 + 1, ],
    raw_control   = colMeans(f$Y[1:f$N0, , drop = FALSE]),
    synth_control = colSums(f$omega * f$Y[1:f$N0, , drop = FALSE]))
}
fit <- bind_rows(fit_rows)
save_table(fit, "synthdid_pretrend_fit.csv")

# Mean absolute pre-launch gap between treated brands and their control,
# computed brand by brand at each pre-launch quarter (Section 5.2).
pre <- fit %>% filter(event_time < 0)
gaps <- pre %>% group_by(outcome) %>%
  summarise(gap_raw_control   = mean(abs(treated - raw_control)),
            gap_synth_control = mean(abs(treated - synth_control)),
            reduction_pct     = 100 * (1 - gap_synth_control / gap_raw_control),
            .groups = "drop")
brand_gaps <- pre %>% filter(outcome == "rating") %>% group_by(brand) %>%
  summarise(gap_synth_control = mean(abs(treated - synth_control)), .groups = "drop") %>%
  arrange(gap_synth_control)
save_table(gaps, "synthdid_pretrend_gaps.csv")
save_table(brand_gaps, "synthdid_pretrend_gap_by_brand.csv")
cat("\nPre-launch fit (mean absolute gap):\n"); print(as.data.frame(gaps), digits = 3)
cat(sprintf("Per-brand synthetic fit (rating): min %.2f (%s), max %.2f (%s), mean %.2f, sd %.2f\n",
            min(brand_gaps$gap_synth_control), brand_gaps$brand[1],
            max(brand_gaps$gap_synth_control), brand_gaps$brand[nrow(brand_gaps)],
            mean(brand_gaps$gap_synth_control), sd(brand_gaps$gap_synth_control)))
