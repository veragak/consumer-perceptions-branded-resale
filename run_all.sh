#!/usr/bin/env bash
# Reproduce every table and figure that can be built from the public data.
# Run from the repository root:  bash run_all.sh
# Takes about 2 hours; most of it is the placebo SEs of the synthetic DiD (23, 24).
set -euo pipefail

python  code/07_discount_depth.py       # discount-depth moderator from the 210 price pairs
Rscript code/10_descriptives.R          # Tables 1, 2, A.1
python  code/11_figures_descriptive.py  # Figure 1, Figure A.5
Rscript code/20_twfe_did.R              # Table 3 (TWFE), Table A.6, pooled pre-trend test
Rscript code/21_callaway_santanna.R     # Table 3 (C&S)
Rscript code/22_cs_event_study.R        # Figure 5
Rscript code/23_synthdid.R              # Table 3 (SDID), Table 4, Table 5 ATTs, fit data
Rscript code/24_synthdid_lowvol.R       # Table A.7   (needs 23)
Rscript code/26_synthdid_pool_thesis_se.R  # Tables 3 and 4 exactly as printed (needs 23)
python  code/25_figures_synthdid.py     # Figures 3, 4, 6 (needs 23)
Rscript code/30_study2_moderation.R     # Tables 6, 7 (needs 23)
Rscript code/31_study2_raw_change.R     # Table 5, Tables A.8a, A.8b (needs 23)

# Need the unpublished review text in private/ (see data/README.md):
if [ -f private/df_enriched.csv ]; then
  python code/04_lda_topics.py          # Figure 2, Tables A.4b, A.4c
  python code/05_lda_model_selection.py # Table A.4a (recomputed)
  python code/06_vader_cutoff_check.py  # VADER fallback robustness (Section 4.2.1)
fi
python code/99_check_against_thesis.py   # compare everything with the thesis PDF
echo "All done. Outputs are in results/, see results/verification_report.md."
