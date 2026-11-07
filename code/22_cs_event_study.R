# =============================================================================
# 22_cs_event_study.R  -  Study 1: parallel-trends check by launch cohort
#
# Thesis: Section 5.2 "Baseline imbalance" and Figure 5
# Produces:
#   Figure 5 -> results/figures/figure5_cs_event_study_rating.jpg
#   (plus the same plot for the two text outcomes, used as supporting material)
#   Event-study estimates -> results/tables/figure5_cs_event_study.csv
#
# Why this check exists: a pooled test (20_twfe_did.R) suggests treatment and
# control brands were already drifting apart before launch. But brands launched
# years apart, and putting them on one calendar axis can create a fake trend
# difference. Here every launch cohort is compared with never-treated brands on
# its own timeline, following Callaway & Sant'Anna (2021):
#
#   ATT(g, t) = [mean_g(t) - mean_g(ref)] - [mean_control(t) - mean_control(ref)]
#
# where g is a cohort (brands launching in the same quarter) and ref is the
# quarter one year (4 quarters) before g's launch. Cohort effects are averaged
# by event time, weighted by the number of brands in each cohort. Event times
# before 0 are placebo checks: if they are near zero, the parallel-trends
# assumption is supported. 95% CIs come from a brand-level bootstrap (500 draws).
#
# This is a hand-written version of the estimator, used for the event-study
# figure. The overall C&S ATT in Table 3 comes from the `did` package
# (21_callaway_santanna.R).
# =============================================================================
source("code/_common.R")
suppressPackageStartupMessages(library(ggplot2))

df <- did_sample(load_reviews())

# Launch quarter of each treatment brand = quarter of its first post-launch review
timing <- df %>% filter(group == "treatment") %>% group_by(brand) %>%
  summarise(launch_qtr = as.character(as.yearqtr(min(date[period == "post"]))), .groups = "drop") %>%
  mutate(ref_qtr = as.character(as.yearqtr(launch_qtr) - 1))       # 4 quarters earlier
cohorts <- timing %>% group_by(launch_qtr) %>%
  summarise(brands = list(brand), n_brands = n(), ref_qtr = first(ref_qtr), .groups = "drop")
controls <- unique(df$brand[df$group == "control"])

# Brand x quarter matrix of means, one per outcome
bq <- df %>% group_by(brand, quarter) %>%
  summarise(across(all_of(OUTCOMES), mean), .groups = "drop")
all_qtrs <- sort(unique(bq$quarter))
mean_matrix <- function(y) {
  w <- bq %>% select(brand, quarter, v = all_of(y)) %>% pivot_wider(names_from = quarter, values_from = v)
  m <- as.matrix(w[, -1]); rownames(m) <- w$brand; m
}

# Event-study estimates for a given set of treatment rows and control rows
event_study <- function(mat, treat_rows, ctrl_rows) {
  treat_names <- rownames(mat)[treat_rows]
  out <- list()
  for (i in seq_len(nrow(cohorts))) {
    g  <- cohorts$launch_qtr[i]; ref <- cohorts$ref_qtr[i]
    if (!(ref %in% colnames(mat))) next
    rows_g <- treat_rows[treat_names %in% cohorts$brands[[i]]]
    if (length(rows_g) == 0) next
    ref_t <- mean(mat[rows_g, ref], na.rm = TRUE)
    ref_c <- mean(mat[ctrl_rows, ref], na.rm = TRUE)
    if (is.nan(ref_t) || is.nan(ref_c)) next
    g_idx <- which(all_qtrs == g)
    for (t in all_qtrs[all_qtrs > ref]) {
      if (!(t %in% colnames(mat))) next
      m_t <- mean(mat[rows_g, t], na.rm = TRUE)
      m_c <- mean(mat[ctrl_rows, t], na.rm = TRUE)
      if (is.nan(m_t) || is.nan(m_c)) next
      out[[length(out) + 1]] <- data.frame(cohort = g, n_brands = cohorts$n_brands[i],
                                           event_time = which(all_qtrs == t) - g_idx,
                                           att = (m_t - ref_t) - (m_c - ref_c))
    }
  }
  bind_rows(out) %>% group_by(event_time) %>%
    summarise(att = weighted.mean(att, n_brands), .groups = "drop")
}

results <- list()
for (y in OUTCOMES) {
  mat <- mean_matrix(y)
  t_rows <- which(rownames(mat) %in% timing$brand)
  c_rows <- which(rownames(mat) %in% controls)
  est <- event_study(mat, t_rows, c_rows)

  set.seed(42)                                   # brand-level bootstrap
  boot <- bind_rows(lapply(1:500, function(b) {
    e <- event_study(mat, sample(t_rows, replace = TRUE), sample(c_rows, replace = TRUE))
    if (!is.null(e) && nrow(e) > 0) e$draw <- b
    e
  }))
  se <- boot %>% group_by(event_time) %>% summarise(se = sd(att, na.rm = TRUE), .groups = "drop")
  results[[y]] <- est %>% left_join(se, by = "event_time") %>%
    mutate(outcome = y, ci_lo = att - 1.96 * se, ci_hi = att + 1.96 * se)
  cat("Done:", y, "\n")
}
es <- bind_rows(results)
save_table(es %>% filter(event_time >= -8, event_time <= 12), "figure5_cs_event_study.csv")

# -- Figure 5 -------------------------------------------------------------------
plot_es <- function(y, file) {
  d <- es %>% filter(outcome == y, event_time >= -8, event_time <= 12) %>%
    mutate(period = ifelse(event_time < 0, "Pre-treatment", "Post-treatment"))
  cols <- c("Pre-treatment" = "#D55E00", "Post-treatment" = "#0072B2")
  p <- ggplot(d, aes(event_time, att, colour = period)) +
    geom_hline(yintercept = 0, linetype = "dashed", colour = "grey60") +
    geom_vline(xintercept = -0.5, linetype = "dotted", colour = "grey60") +
    geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi, fill = period), alpha = 0.15, colour = NA) +
    geom_line(linewidth = 0.8) + geom_point(size = 2.5) +
    scale_colour_manual(values = cols) + scale_fill_manual(values = cols) +
    labs(title = paste("Callaway & Sant'Anna (2021) Event Study:", OUTCOME_LABELS[[y]]),
         x = "Quarters relative to resale programme launch (reference = quarter -4)",
         y = paste("ATT:", OUTCOME_LABELS[[y]]), colour = NULL, fill = NULL,
         caption = "95% bootstrap CI. Orange = pre-treatment placebo; blue = post-treatment effect.") +
    theme_minimal(base_size = 12) + theme(legend.position = "bottom", plot.title = element_text(size = 11))
  ggsave(file.path(FIG_DIR, file), p, width = 9, height = 5, dpi = 300)
  cat("Saved:", file.path(FIG_DIR, file), "\n")
}
plot_es("rating",      "figure5_cs_event_study_rating.jpg")
plot_es("sust_score",  "supp_cs_event_study_sustainability.jpg")
plot_es("value_vader", "supp_cs_event_study_value_vader.jpg")

print(as.data.frame(es %>% filter(outcome == "rating", event_time >= -3, event_time <= 12)), digits = 3)
