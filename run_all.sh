#!/usr/bin/env bash
# Reproduce every table and figure that can be built from the public data.
# Run from the repository root:  bash run_all.sh
# Takes about 2 hours; most of it is the synthetic DiD in step 5.
set -euo pipefail

# 2. Data preparation
python  code/2_data_preparation/3_discount_depth.py     # discount-depth values from 210 price pairs

# 4. Descriptives
Rscript code/4_descriptives/1_descriptives.R            # Tables 1, 2, A.1
python  code/4_descriptives/2_figures_descriptive.py    # Figures 1, A.5

# 5. Study 1: did resale launches change perceptions?
Rscript code/5_study1_did/1_twfe_did.R                  # Table 3 (TWFE), Table A.6
Rscript code/5_study1_did/2_callaway_santanna.R         # Table 3 (C&S)
Rscript code/5_study1_did/3_cs_event_study.R            # Figure 5
Rscript code/5_study1_did/4_synthdid.R                  # Table 3 (SDID), Table 4, Table 5 effects
Rscript code/5_study1_did/5_synthdid_lowvol.R           # Table A.7
Rscript code/5_study1_did/6_synthdid_pool_thesis_se.R   # Tables 3 and 4 exactly as printed
python  code/5_study1_did/7_figures_synthdid.py         # Figures 3, 4, 6

# 6. Study 2: do resale design choices explain the effect?
Rscript code/6_study2_moderation/1_moderation.R         # Tables 6, 7
Rscript code/6_study2_moderation/2_raw_change.R         # Table 5, Tables A.8a, A.8b

# 3. Text analysis: needs the unpublished review text in private/ (see data/README.md)
if [ -f private/df_enriched.csv ]; then
  python code/3_text_analysis/1_lda_topics.py           # Figure 2, Tables A.4b, A.4c
  python code/3_text_analysis/2_lda_model_selection.py  # Table A.4a
  python code/3_text_analysis/3_vader_cutoff_check.py   # VADER robustness (Section 4.2.1)
fi

# 7. Compare everything with the thesis PDF
python code/7_verification/check_against_thesis.py

echo "All done. Outputs are in results/."
