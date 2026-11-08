# =============================================================================
# 2_data_preparation/2_export_public_data.R  -  make the public dataset (removes the review text)
#
# Creates data/reviews_scored.csv, the public dataset every analysis script uses.
#
# Input (private, not in this repository): the scored review file produced by
#   2_data_preparation/1_score_reviews.py, which still contains the review title and text.
# Output: the same 49,736 reviews WITHOUT title, text or reviewer country.
#   Only the date, brand, group labels, star rating and the two text-derived
#   scores are kept. This is enough to reproduce every table in the thesis
#   except the LDA topic model (Figure 2, Appendix A.4), which needs the text.
#
# Usage (author only):
#   Rscript code/2_data_preparation/2_export_public_data.R path/to/df_enriched.csv
# =============================================================================
suppressPackageStartupMessages({ library(readr); library(dplyr); library(stringr) })

args <- commandArgs(trailingOnly = TRUE)
src  <- if (length(args) > 0) args[1] else "private/df_enriched.csv"
df   <- read_csv(src, show_col_types = FALSE)

# Safeguards only: on the thesis data these lines change nothing. They fix the
# brand name Sézane if a CSV round-trip mis-encoded it, and merge two early
# segment labels from the first scraping wave into "contemporary_fashion".
df$brand   <- ifelse(grepl("zane$", df$brand), "Sézane", df$brand)
df$brand   <- str_replace_all(df$brand, c("Jöttnar" = "Jottnar"))
df$segment <- str_replace_all(df$segment, c("french_fashion" = "contemporary_fashion",
                                            "denim_heritage" = "contemporary_fashion"))

out <- df %>%
  transmute(review_id = row_number(),
            date = as.Date(date), brand, segment, group, period,
            rating, sust_pos, sust_neg, sust_score, value_vader)

stopifnot(nrow(out) == 49736, n_distinct(out$brand) == 48)
write_csv(out, "data/reviews_scored.csv")
cat("Saved data/reviews_scored.csv:", nrow(out), "reviews,", n_distinct(out$brand), "brands\n")
