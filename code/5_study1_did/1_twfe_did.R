# =============================================================================
# 5_study1_did/1_twfe_did.R  -  Study 1 starting point: two-way fixed effects DiD
#
# Thesis: Section 4.3.2 (method), Section 5.2 (results), Appendix A.6
# Produces:
#   Table 3, column "TWFE"  and  Table A.6 -> results/tables/tableA6_twfe.csv
#   Pooled pre-trend test quoted in Section 5.2 ("interaction -0.124, p < 0.001")
#                                          -> results/tables/pretrend_pooled_test.csv
#
# Model (review level, 45,368 reviews from 46 brands):
#   outcome_ibt = beta * (treated_b x post_bt) + brand FE + quarter FE + error
# Standard errors are clustered by brand (Bertrand, Duflo & Mullainathan, 2004).
#
# The thesis treats this estimate as a diagnostic, not the headline result:
# treatment and control brands start from different baselines, which the
# synthetic DiD in 5_study1_did/4_synthdid.R corrects for.
# =============================================================================
source("code/shared/common.R")
suppressPackageStartupMessages({ library(lfe); library(lmtest); library(sandwich) })

df <- did_sample(load_reviews())
df$brand_f   <- factor(df$brand)
df$quarter_f <- factor(df$quarter)

rows <- list()
for (y in OUTCOMES) {
  m  <- felm(as.formula(paste(y, "~ did | brand_f + quarter_f | 0 | brand_f")), data = df)
  s  <- summary(m)
  ct <- s$coefficients
  # 95% CI as beta +/- 1.96 SE (as in Table A.6).
  # r2_full is the R-squared including the fixed effects; this is the number
  # shown in Table A.6 under the label "Within R²". The true within R-squared
  # (variation explained after removing brand and quarter effects) is tiny and
  # is reported separately as r2_within.
  rows[[y]] <- data.frame(
    outcome = OUTCOME_LABELS[[y]], beta = ct["did", 1], se = ct["did", 2],
    t = ct["did", 3], p = ct["did", 4],
    ci_lo = ct["did", 1] - 1.96 * ct["did", 2], ci_hi = ct["did", 1] + 1.96 * ct["did", 2],
    n = nobs(m), r2_full = s$r.squared, r2_within = s$P.r.squared,
    clusters = n_distinct(df$brand))
}
twfe <- bind_rows(rows)
save_table(twfe, "tableA6_twfe.csv")
print(twfe, digits = 3)

# -- Pooled pre-trend test --------------------------------------------------------
# Fits one linear calendar-time trend for pre-launch treatment reviews and one
# for control reviews, and tests whether the slopes differ. Section 5.2 explains
# why this pooled test is misleading with staggered launch dates; the
# cohort-based check is in 5_study1_did/3_cs_event_study.R (Figure 5).
pt <- df %>% filter(period %in% c("pre", "control")) %>%
  mutate(year_n = as.numeric(format(date, "%Y")) + (as.numeric(format(date, "%m")) - 1) / 12,
         treat_pre = as.integer(period == "pre"))
m_pt <- lm(rating ~ year_n * treat_pre, data = pt)
ct   <- coeftest(m_pt, vcov = vcovHC(m_pt, type = "HC1"))
pt_out <- data.frame(term = "year_n:treat_pre", beta = ct["year_n:treat_pre", 1],
                     se = ct["year_n:treat_pre", 2], p = ct["year_n:treat_pre", 4])
save_table(pt_out, "pretrend_pooled_test.csv")
print(pt_out, digits = 3)
