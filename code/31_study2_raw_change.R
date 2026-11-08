# =============================================================================
# 31_study2_raw_change.R  -  raw before/after changes and sensitivity checks
#
# Thesis: Table 5 (Delta columns), Appendix A.8 (Tables A.8a and A.8b),
#         discount-depth caveat in Section 4.2.2
# Produces:
#   Table 5   -> results/tables/table5_brand_level.csv
#   Table A.8a-> results/tables/tableA8a_moderation_raw_change.csv
#   Table A.8b-> results/tables/tableA8b_interaction_raw_change.csv
#   Extra     -> results/tables/sensitivity_excl_p2p.csv
#
# Table 5 puts two numbers side by side for each treatment brand:
#   Delta = mean after launch minus mean before launch (no control group), and
#   the synthetic DiD ATT from 23_synthdid.R (adjusted for baseline and trend).
# Large gaps between the two show how much of a raw change is not due to resale.
#
# Appendix A.8 re-runs the Study 2 regressions with Delta as the outcome
# instead of the ATT. Brands need >= 30 pre-launch and >= 50 post-launch reviews,
# which drops Claudie Pierlot (40 post-launch reviews): N = 18.
#
# Differences from the thesis PDF:
#  * Table 5 in the PDF swaps the three Delta values of Ba&sh and Balzac Paris.
#    The data give Balzac Paris +1.912 stars and Ba&sh +1.812, as the thesis
#    text itself says ("Balzac Paris ... its 1.9-star raw improvement").
#  * Tables A.8a/A.8b in the PDF mix two runs. Their discount rows and R2 come
#    from the final 10-listing discount data used here, but the integration,
#    messaging and services rows (and most of A.8b) come from an earlier run
#    with rough discount guesses. This script uses the final data throughout;
#    its output equals the file saved by the original analysis script.
#
# Extra sensitivity: Michael Kors and Steve Madden run peer-to-peer resale where
# sellers, not the brand, set prices, so their discount depth is not a brand
# decision. The A.8a models are re-run without them (N = 16).
# =============================================================================
source("code/_common.R")

df   <- did_sample(load_reviews())
mods <- load_moderators()
sdid <- read_csv(file.path(TABLE_DIR, "synthdid_by_brand.csv"), show_col_types = FALSE)

deltas <- df %>% filter(group == "treatment") %>% group_by(brand) %>%
  summarise(pre_n = sum(period == "pre"), post_n = sum(period == "post"),
            delta_rating = mean(rating[period == "post"])      - mean(rating[period == "pre"]),
            delta_sust   = mean(sust_score[period == "post"])  - mean(sust_score[period == "pre"]),
            delta_vader  = mean(value_vader[period == "post"]) - mean(value_vader[period == "pre"]),
            .groups = "drop")

# -- Table 5 -------------------------------------------------------------------------
t5 <- deltas %>%
  left_join(sdid %>% select(brand, outcome, att) %>%
              pivot_wider(names_from = outcome, values_from = att, names_prefix = "att_"),
            by = "brand") %>%
  mutate(borderline = pre_n < 50 | post_n < 50) %>%
  arrange(desc(delta_rating))
save_table(t5, "table5_brand_level.csv")

# -- Table A.8a / A.8b --------------------------------------------------------------
s2 <- deltas %>% filter(pre_n >= 30, post_n >= 50) %>%
  inner_join(mods, by = "brand") %>%
  mutate(seg_outdoor = as.integer(segment == "outdoor_athletic"),
         seg_premium = as.integer(segment == "premium_fashion"),
         int_x_msg   = integration * messaging)
cat("Brands in raw-change sample:", nrow(s2), "\n")

rhs <- "integration + messaging + discount + services + seg_outdoor + seg_premium"
a8a <- bind_rows(lapply(c("delta_rating", "delta_sust", "delta_vader"), function(y)
  hc1_table(lm(as.formula(paste(y, "~", rhs)), data = s2), y)))
save_table(a8a, "tableA8a_moderation_raw_change.csv")

a8b <- hc1_table(lm(delta_rating ~ integration + messaging + int_x_msg + discount + services +
                      seg_outdoor + seg_premium, data = s2), "delta_rating interaction")
save_table(a8b, "tableA8b_interaction_raw_change.csv")

# -- Excluding peer-to-peer brands -------------------------------------------------
s2_p2p <- s2 %>% filter(!brand %in% c("Michael Kors", "Steve Madden"))
p2p <- bind_rows(lapply(c("delta_rating", "delta_sust", "delta_vader"), function(y)
  hc1_table(lm(as.formula(paste(y, "~", rhs)), data = s2_p2p), y)))
save_table(p2p, "sensitivity_excl_p2p.csv")

cat("\nTable A.8a\n"); print(a8a[a8a$variable %in% c("integration","messaging","discount","services"),
                                c("model","variable","beta","se","p","r2","adj_r2")], digits = 3)
cat("\nTable A.8b\n"); print(a8b[, c("variable","beta","se","t","p","ci_lo","ci_hi")], digits = 3)
