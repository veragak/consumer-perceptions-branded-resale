# =============================================================================
# 10_descriptives.R  -  sample description
#
# Thesis: Sections 4.1 and 5.1, Appendix A.1
# Produces:
#   Table 1   treatment brand sample reconciliation -> table1_treatment_sample.csv
#   Table 2   outcomes by group and period           -> table2_descriptives.csv
#   Table A.1 control brand overview                 -> tableA1_control_brands.csv
#
# Control brands have no launch date. To split them into "pre" and "post" for
# Table 2 (and Figure 1, Figure 2), each control brand inherits the launch date
# of the treatment brand(s) it is matched to: its pseudo-event date
# (data/control_brands.csv).
# =============================================================================
source("code/_common.R")

df   <- load_reviews()
mods <- load_moderators()
ctrl <- read_csv(CTRL_FILE, show_col_types = FALSE)

# -- Table 1: pre/post review counts per treatment brand -------------------------
# Study 1 needs at least 50 reviews on each side of the launch; brands with one
# side below 50 are kept but flagged as borderline. Arc'teryx and Patagonia have
# (almost) no pre-launch reviews and are excluded from both studies.
t1 <- df %>% filter(group == "treatment") %>%
  group_by(brand) %>%
  summarise(pre_n = sum(period == "pre"), post_n = sum(period == "post"), .groups = "drop") %>%
  left_join(mods %>% select(brand, segment, launch), by = "brand") %>%
  mutate(study1 = case_when(brand %in% DID_EXCLUDE ~ "excluded (no pre-period)",
                            pre_n  < 50 ~ "borderline (pre < 50)",
                            post_n < 50 ~ "borderline (post < 50)",
                            TRUE ~ "included"),
         study2 = ifelse(brand %in% DID_EXCLUDE, "excluded", "included")) %>%
  select(brand, segment, launch, pre_n, post_n, study1, study2) %>%
  arrange(segment, desc(post_n))
save_table(t1, "table1_treatment_sample.csv")

# -- Table 2: means and SDs by group and period ----------------------------------
ctrl_split <- df %>% filter(group == "control") %>%
  left_join(ctrl %>% select(brand, pseudo_event_date), by = "brand") %>%
  mutate(period = ifelse(date < as.Date(pseudo_event_date), "pre", "post"))
stopifnot(!any(is.na(ctrl_split$pseudo_event_date)))

describe <- function(d, label) {
  data.frame(group_period = label, n = nrow(d),
             mean_rating = mean(d$rating),      sd_rating = sd(d$rating),
             mean_sust   = mean(d$sust_score),  sd_sust   = sd(d$sust_score),
             mean_vader  = mean(d$value_vader), sd_vader  = sd(d$value_vader))
}
t2 <- bind_rows(
  describe(filter(df, period == "pre"),          "Treatment: pre-launch"),
  describe(filter(df, period == "post"),         "Treatment: post-launch"),
  describe(filter(ctrl_split, period == "pre"),  "Control: pre-event"),
  describe(filter(ctrl_split, period == "post"), "Control: post-event"))
save_table(t2, "table2_descriptives.csv")
print(t2, digits = 3)

# -- Table A.1: control brands with review volume flags ---------------------------
# Low = fewer than 150 reviews (dropped in robustness check A.7); Marginal = 150-499.
tA1 <- df %>% filter(group == "control") %>% count(brand, name = "total_reviews") %>%
  right_join(ctrl %>% select(brand, segment, matched_to), by = "brand") %>%
  mutate(volume_flag = case_when(total_reviews < 150 ~ "Low",
                                 total_reviews < 500 ~ "Marginal",
                                 TRUE ~ "OK")) %>%
  select(brand, segment, matched_to, total_reviews, volume_flag)
save_table(tA1, "tableA1_control_brands.csv")

cat(sprintf("\nSample: %d reviews, %d brands (%d treatment, %d control), %s to %s\n",
            nrow(df), n_distinct(df$brand),
            n_distinct(df$brand[df$group == "treatment"]),
            n_distinct(df$brand[df$group == "control"]),
            min(df$date), max(df$date)))
