# =============================================================================
# _common.R  -  shared settings and helpers for every R script in code/
#
# Every analysis script starts with  source("code/_common.R")  so that:
#   * all scripts read the same data file with the same preparation steps,
#   * sample definitions (excluded brands, low-volume controls) live in one place,
#   * the synthetic DiD loop is written once and reused by the main analysis
#     (23_synthdid.R) and the robustness check (24_synthdid_lowvol.R).
#
# Run all scripts from the repository root, e.g.
#   Rscript code/23_synthdid.R
# =============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
  library(zoo)
})

# -- Paths ---------------------------------------------------------------------
if (!file.exists("data/reviews_scored.csv")) {
  stop("Run this script from the repository root, e.g.  Rscript code/23_synthdid.R")
}
DATA_FILE  <- "data/reviews_scored.csv"
MOD_FILE   <- "data/treatment_brands_moderators.csv"
CTRL_FILE  <- "data/control_brands.csv"
TABLE_DIR  <- "results/tables"
FIG_DIR    <- "results/figures"
dir.create(TABLE_DIR, showWarnings = FALSE, recursive = TRUE)
dir.create(FIG_DIR,   showWarnings = FALSE, recursive = TRUE)

# -- Sample definitions (thesis Section 4.1) -----------------------------------
# Arc'teryx (0 pre-launch reviews) and Patagonia (2) cannot be used in a
# before/after design, so they are dropped from every Study 1 and Study 2 model.
DID_EXCLUDE <- c("Arc'teryx", "Patagonia")

# Control brands with fewer than 150 reviews (Appendix A.1), dropped in A.7.
LOW_VOLUME_CONTROLS <- c("Tommy Hilfiger", "Fred Perry", "Jottnar", "Vuori")

OUTCOMES <- c("rating", "sust_score", "value_vader")
OUTCOME_LABELS <- c(rating = "Star rating",
                    sust_score = "Sustainability score",
                    value_vader = "Value VADER")

# -- Data loading ----------------------------------------------------------------
# One row per Trustpilot review. `period` is "pre"/"post" for treatment brands
# (relative to that brand's resale launch) and "control" for control brands.
load_reviews <- function() {
  df <- read_csv(DATA_FILE, show_col_types = FALSE)
  df$date      <- as.Date(df$date)
  df$yearqtr   <- as.yearqtr(df$date)
  df$quarter   <- as.character(df$yearqtr)       # e.g. "2022 Q2", used as FE
  df$quarter_n <- as.numeric(df$yearqtr)         # e.g. 2022.25, used for timing
  df$treated   <- as.integer(df$group == "treatment")
  df$post      <- as.integer(df$period == "post")
  df$did       <- df$treated * df$post           # treated x post interaction
  df
}

load_moderators <- function() read_csv(MOD_FILE, show_col_types = FALSE)

# Study 1 sample: all 27 controls + the 19 treatment brands with a pre-period.
did_sample <- function(df) df[!df$brand %in% DID_EXCLUDE, ]

# -- Brand-quarter panel ---------------------------------------------------------
# Synthetic DiD and Callaway-Sant'Anna work on one observation per brand and
# quarter, so reviews are averaged within each brand-quarter. first_treat_q is
# the first quarter in which the brand has a post-launch review (NA = control).
brand_quarter_panel <- function(df) {
  treat_info <- df %>%
    group_by(brand) %>%
    summarise(first_treat_q = ifelse(any(period == "post"),
                                     min(quarter_n[period == "post"], na.rm = TRUE),
                                     NA_real_),
              .groups = "drop")
  df %>%
    group_by(brand, quarter_n) %>%
    summarise(rating      = mean(rating,      na.rm = TRUE),
              sust_score  = mean(sust_score,  na.rm = TRUE),
              value_vader = mean(value_vader, na.rm = TRUE),
              n           = n(),
              .groups = "drop") %>%
    left_join(treat_info, by = "brand")
}

# -- Synthetic DiD, one treated brand at a time (thesis Section 4.3.2) -------------
# For a treated brand b we build a brands x quarters matrix Y with the 27 control
# brands in the first rows and brand b in the last row, restricted to the quarters
# in which b has reviews. synthdid then picks control weights (omega) and
# pre-period weights (lambda) so the weighted controls track b before launch,
# and returns the DiD estimate tau_b. Standard errors use the placebo method.
#
# Missing brand-quarter cells (a brand with no reviews that quarter) are filled
# with that brand's own mean over the window, as in the thesis.
#
# Returns a list with the estimate table and, per brand, the matrix and weights
# (used for the pre-launch fit check behind Figures 3 and 6).
build_Y <- function(panel, outcome, treat_brand, control_brands) {
  treat_q     <- unique(panel$first_treat_q[panel$brand == treat_brand])
  tb_quarters <- panel$quarter_n[panel$brand == treat_brand]
  pre_qs  <- sort(tb_quarters[tb_quarters <  treat_q])
  post_qs <- sort(tb_quarters[tb_quarters >= treat_q])
  if (length(pre_qs) < 3 || length(post_qs) < 1) return(NULL)

  brands_order <- c(control_brands, treat_brand)
  wide <- panel %>%
    filter(brand %in% brands_order, quarter_n %in% c(pre_qs, post_qs)) %>%
    select(brand, quarter_n, all_of(outcome)) %>%
    pivot_wider(names_from = quarter_n, values_from = all_of(outcome),
                names_sort = TRUE)
  missing <- setdiff(brands_order, wide$brand)
  if (length(missing) > 0) {
    empty <- data.frame(brand = missing,
                        matrix(NA_real_, nrow = length(missing), ncol = ncol(wide) - 1,
                               dimnames = list(NULL, colnames(wide)[-1])),
                        check.names = FALSE)
    wide <- bind_rows(wide, empty)
  }
  wide <- wide[match(brands_order, wide$brand), ]
  Y <- as.matrix(wide[, -1]); rownames(Y) <- brands_order
  for (i in seq_len(nrow(Y))) {                     # neutral mean imputation
    m <- mean(Y[i, ], na.rm = TRUE)
    if (!is.nan(m)) Y[i, is.na(Y[i, ])] <- m
  }
  if (any(is.na(Y))) return(NULL)
  list(Y = Y, N0 = length(control_brands), T0 = length(pre_qs),
       treat_q = treat_q, n_pre = length(pre_qs), n_post = length(post_qs))
}

run_synthdid_all <- function(panel, outcomes = OUTCOMES, seed = 2026, verbose = TRUE) {
  suppressPackageStartupMessages(library(synthdid))
  # Brand order follows the panel (dplyr's alphabetical C-locale order), which
  # is the order the thesis estimates were produced with.
  brands  <- unique(panel[, c("brand", "first_treat_q")])
  controls <- brands$brand[is.na(brands$first_treat_q)]
  treated  <- brands$brand[!is.na(brands$first_treat_q)]
  rows <- list(); fits <- list()
  for (outcome in outcomes) {
    if (verbose) cat(sprintf("\n=== Synthetic DiD: %s ===\n", outcome))
    for (b in treated) {
      inp <- build_Y(panel, outcome, b, controls)
      if (is.null(inp)) { if (verbose) cat("  skipped", b, "\n"); next }
      est <- synthdid_estimate(inp$Y, N0 = inp$N0, T0 = inp$T0)
      set.seed(seed)                                 # placebo SEs are random
      se  <- sqrt(vcov(est, method = "placebo"))
      att <- as.numeric(est)
      rows[[length(rows) + 1]] <- data.frame(
        brand = b, outcome = outcome, att = att, se = as.numeric(se),
        p = 2 * (1 - pnorm(abs(att / as.numeric(se)))),
        n_pre_quarters = inp$n_pre, n_post_quarters = inp$n_post)
      fits[[paste(outcome, b)]] <- list(Y = inp$Y, N0 = inp$N0, treat_q = inp$treat_q,
                                       omega = attr(est, "weights")$omega)
      if (verbose) cat(sprintf("  %-18s ATT = %+.3f  SE = %.3f\n", b, att, se))
    }
  }
  list(results = bind_rows(rows), fits = fits, controls = controls)
}

# Inverse-variance weighted average of per-brand estimates (Tables 3, 4, A.7).
pool_ivw <- function(d) {
  w   <- 1 / d$se^2
  att <- sum(w * d$att) / sum(w)
  se  <- sqrt(1 / sum(w))
  data.frame(n_brands = nrow(d), att = att, se = se, t = att / se,
             p = 2 * (1 - pnorm(abs(att / se))))
}

# HC1 robust coefficient table for the brand-level OLS models in Study 2.
# p     = p-value from the t distribution (residual degrees of freedom), the
#         default of lmtest::coeftest. Matches Tables 7 and A.8 of the thesis.
# p_normal = p-value from the normal distribution. Table 6 of the thesis prints
#         these, so both are reported.
hc1_table <- function(model, name) {
  suppressPackageStartupMessages({ library(lmtest); library(sandwich) })
  V  <- vcovHC(model, type = "HC1")
  ct <- coeftest(model, vcov = V)
  ci <- coefci(model, vcov = V)
  data.frame(model = name, variable = rownames(ct),
             beta = ct[, 1], se = ct[, 2], t = ct[, 3], p = ct[, 4],
             p_normal = 2 * pnorm(-abs(ct[, 3])),
             ci_lo = ci[, 1], ci_hi = ci[, 2], n = nobs(model),
             r2 = summary(model)$r.squared, adj_r2 = summary(model)$adj.r.squared,
             row.names = NULL)
}

save_table <- function(d, name) {
  num <- vapply(d, is.numeric, logical(1))
  d[num] <- lapply(d[num], round, 4)
  path <- file.path(TABLE_DIR, name)
  write_csv(d, path)
  cat("Saved:", path, "\n")
}
