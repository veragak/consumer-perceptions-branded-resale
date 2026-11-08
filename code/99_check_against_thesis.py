"""
99_check_against_thesis.py - compare every reproduced number with the thesis PDF

Run after run_all.sh:   python code/99_check_against_thesis.py
Writes results/verification_report.md and prints a summary.

Each expected value below was copied by hand from the thesis PDF
(thesis/Master_Thesis_Vera_Gak_Anagrova.pdf). The thesis reports 3 decimals,
so a reproduced value MATCHES when it rounds to the printed value
(tolerance 0.0015 to allow for rounding of rounded numbers).

Values that come from random resampling (placebo SEs in synthetic DiD,
bootstrap SEs in Callaway & Sant'Anna) cannot match exactly, because the thesis
runs had no fixed seed. They are checked with a wider tolerance and labelled
"random" in the report.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _common import ROOT, TABLES

TOL, TOL_RANDOM = 0.0015, 0.05
rows = []


def check(item, expected, got, random=False, tol=None):
    tol = tol if tol is not None else (TOL_RANDOM if random else TOL)
    ok = got is not None and abs(float(got) - expected) <= tol
    rows.append({'item': item, 'thesis': expected,
                 'reproduced': None if got is None else round(float(got), 4),
                 'status': ('MATCH' if ok else 'DIFFERENT') + (' (random)' if random else '')})


def t(name):
    return pd.read_csv(TABLES / name)


# -- Table 1 and 2 -----------------------------------------------------------------
t1 = t('table1_treatment_sample.csv').set_index('brand')
for b, pre, post in [('Ba&sh', 65, 568), ('Sandro', 116, 235), ('Maje', 106, 188),
                     ('Claudie Pierlot', 70, 40), ('Balzac Paris', 32, 1448), ('Soeur', 284, 298),
                     ('Steve Madden', 92, 1145), ('Armedangels', 479, 1011),
                     ('Studio Anneloes', 197, 3208), ("Levi's", 288, 586), ('Hugo Boss', 366, 508),
                     ('Lacoste', 557, 91), ('Canada Goose', 434, 2047), ('Michael Kors', 679, 412),
                     ('Lululemon', 611, 595), ('Allbirds', 549, 1451), ('Aigle', 66, 953),
                     ('Carhartt', 425, 241), ('The North Face', 39, 2008), ("Arc'teryx", 0, 4000),
                     ('Patagonia', 2, 366)]:
    check(f'Table 1 {b} pre n', pre, t1.loc[b, 'pre_n'], tol=0)
    check(f'Table 1 {b} post n', post, t1.loc[b, 'post_n'], tol=0)

t2 = t('table2_descriptives.csv').set_index('group_period')
for g, vals in {'Treatment: pre-launch':  (5457, 2.294, 1.772, 0.078, 0.308, 0.016, 0.563),
                'Treatment: post-launch': (21399, 3.329, 1.868, 0.063, 0.294, 0.129, 0.510),
                'Control: pre-event':     (3798, 2.128, 1.706, 0.137, 0.456, 0.000, 0.593),
                'Control: post-event':    (19082, 3.609, 1.797, 0.089, 0.343, 0.330, 0.544)}.items():
    for col, v in zip(['n', 'mean_rating', 'sd_rating', 'mean_sust', 'sd_sust', 'mean_vader', 'sd_vader'], vals):
        check(f'Table 2 {g} {col}', v, t2.loc[g, col], tol=0 if col == 'n' else TOL)

tA1 = t('tableA1_control_brands.csv').set_index('brand')
for b, n in [('Zadig & Voltaire', 456), ('Sézane', 1855), ('The Kooples', 720), ('Wrangler', 211),
             ('Guess', 878), ('Organic Basics', 1496), ('Rouje', 1084), ('Tommy Hilfiger', 140),
             ('Ted Baker', 1780), ('Armani', 264), ('Fred Perry', 146), ('Moncler', 366),
             ('Moose Knuckles', 194), ('Furla', 198), ('Tory Burch', 261), ('Columbia Sportswear', 748),
             ('Rab', 1172), ('Berghaus', 1746), ('Salomon', 1127), ('Montane', 1778), ('Jottnar', 99),
             ('Vuori', 99), ('Under Armour', 959), ('Hoka', 1832), ('Dickies', 172),
             ('Le Chameau', 1817), ('Osprey', 1282)]:
    check(f'Table A.1 {b} reviews', n, tA1.loc[b, 'total_reviews'], tol=0)

# -- Figure A.5 and LDA (Appendix A.4) -------------------------------------------------
a5 = t('figureA5_sustainability_mentions.csv').set_index('brand')
check('Figure A.5 Organic Basics %', 37.2, a5.loc['Organic Basics', 'pct_positive_sust'], tol=0.05)
check('Figure A.5 Rab %', 28.0, a5.loc['Rab', 'pct_positive_sust'], tol=0.05)
if (TABLES / 'tableA4c_lda_topic_shares.csv').exists():
    lda = t('tableA4c_lda_topic_shares.csv').set_index('label')
    expected = {'Service Complaints': (42.8, 21.7, 59.2, 24.9),
                'Product Quality & Durability': (25.4, 15.3, 18.0, 16.9),
                'Delivery & Fit': (10.0, 18.5, 7.5, 35.5), 'Service & Experience': (4.7, 7.5, 9.3, 15.3),
                'Dutch-language reviews': (4.0, 17.3, 0.1, 0.7),
                'French-language reviews': (5.1, 12.6, 0.9, 3.9),
                'German-language reviews': (8.0, 7.0, 5.1, 2.8)}
    for label, vals in expected.items():
        for col, v in zip(lda.columns[1:], vals):
            check(f'Table A.4c {label} {col} %', v, lda.loc[label, col], tol=0.05)

# -- Measurement checks quoted in Section 4.2 -------------------------------------
dd = t('discount_depth_by_brand.csv')
check('Footnote 2 discount SD, lowest brand', 4.8, dd['discount_sd_10'].min(), tol=0.05)
check('Footnote 2 discount SD, highest brand', 22.8, dd['discount_sd_10'].max(), tol=0.05)
check('Footnote 2 10-vs-5 listings, most negative (pp)', -8.9, dd['diff_10_minus_5_pp'].min(), tol=0.05)
check('Footnote 2 10-vs-5 listings, most positive (pp)', 3.7, dd['diff_10_minus_5_pp'].max(), tol=0.05)
check('Footnote 2 10-vs-5 listings, mean absolute (pp)', 2.7, dd['diff_10_minus_5_pp'].abs().mean(), tol=0.05)
if (TABLES / 'vader_cutoff_check.csv').exists():
    vc = t('vader_cutoff_check.csv')
    ok = vc['corr_with_400'].min() > 0.92
    rows.append({'item': 'Section 4.2.1 VADER cutoffs 200-600: all r > 0.92', 'thesis': 0.92,
                 'reproduced': vc['corr_with_400'].min(), 'status': 'MATCH' if ok else 'DIFFERENT'})

# -- Study 1 -------------------------------------------------------------------------
pt = t('pretrend_pooled_test.csv')
check('Section 5.2 pooled pre-trend interaction', -0.124, pt['beta'][0])

twfe = t('tableA6_twfe.csv').set_index('outcome')
for o, (b, se, tt, p, lo, hi, r2) in {
        'Star rating': (0.244, 0.233, 1.045, 0.301, -0.214, 0.701, 0.441),
        'Sustainability score': (0.005, 0.021, 0.227, 0.822, -0.037, 0.046, 0.087),
        'Value VADER': (0.022, 0.054, 0.415, 0.680, -0.083, 0.128, 0.225)}.items():
    for col, v in zip(['beta', 'se', 't', 'p', 'ci_lo', 'ci_hi', 'r2_full'], (b, se, tt, p, lo, hi, r2)):
        check(f'Table 3/A.6 TWFE {o} {col}', v, twfe.loc[o, col], tol=0.002 if col == 't' else TOL)
    check(f'Table A.6 {o} N', 45368, twfe.loc[o, 'n'], tol=0)

cs = t('table3_callaway_santanna.csv').set_index('outcome')
for o, (a, p) in {'rating': (-0.337, 0.225), 'sust_score': (-0.014, 0.427),
                  'value_vader': (-0.052, 0.328)}.items():
    check(f'Table 3 C&S {o} ATT', a, cs.loc[o, 'att'])
    check(f'Table 3 C&S {o} p', p, cs.loc[o, 'p'], random=True)

T3_SDID = {'rating': (-0.078, 0.419), 'sust_score': (-0.018, 0.052), 'value_vader': (-0.103, 0.002)}
T4 = {('contemporary_fashion', 'rating'): (0.297, 0.129, 0.022),
      ('contemporary_fashion', 'sust_score'): (-0.037, 0.014, 0.009),
      ('contemporary_fashion', 'value_vader'): (-0.017, 0.046, 0.709),
      ('outdoor_athletic', 'rating'): (-0.780, 0.182, 0.000),
      ('outdoor_athletic', 'sust_score'): (-0.066, 0.017, 0.000),
      ('outdoor_athletic', 'value_vader'): (-0.294, 0.063, 0.000),
      ('premium_fashion', 'rating'): (-0.155, 0.237, 0.512),
      ('premium_fashion', 'sust_score'): (0.080, 0.019, 0.000),
      ('premium_fashion', 'value_vader'): (-0.066, 0.071, 0.355)}
# (a) brand effects pooled with the thesis run's placebo SEs: must match exactly
sd = t('table3_synthdid_pooled_thesis_se.csv').set_index('outcome')
for o, (a, p) in T3_SDID.items():
    check(f'Table 3 SDID {o} ATT', a, sd.loc[o, 'att'])
    check(f'Table 3 SDID {o} p', p, sd.loc[o, 'p'])
seg = t('table4_synthdid_by_segment_thesis_se.csv').set_index(['segment', 'outcome'])
for (sg, o), (a, se, p) in T4.items():
    check(f'Table 4 {sg} {o} ATT', a, seg.loc[(sg, o), 'att'])
    check(f'Table 4 {sg} {o} SE', se, seg.loc[(sg, o), 'se'])
    check(f'Table 4 {sg} {o} p', p, seg.loc[(sg, o), 'p'])
# (b) the same tables with fresh placebo SEs from this run
sd = t('table3_synthdid_pooled.csv').set_index('outcome')
for o, (a, p) in T3_SDID.items():
    check(f'Table 3 SDID {o} ATT, fresh placebo SEs', a, sd.loc[o, 'att'], random=True)
    check(f'Table 3 SDID {o} p, fresh placebo SEs', p, sd.loc[o, 'p'], random=True)
seg = t('table4_synthdid_by_segment.csv').set_index(['segment', 'outcome'])
for (sg, o), (a, se, p) in T4.items():
    check(f'Table 4 {sg} {o} ATT, fresh placebo SEs', a, seg.loc[(sg, o), 'att'], random=True, tol=0.2)

t5 = t('table5_brand_level.csv').set_index('brand')
T5 = {'Canada Goose': (2.164, -0.117, 0.432, 0.417, 0.135, 0.288),
      'Ba&sh': (1.912, -0.047, 0.096, 0.614, 0.105, 0.182),
      'Balzac Paris': (1.812, 0.011, 0.534, -0.020, -0.018, 0.063),
      'Aigle': (1.112, -0.021, 0.050, 0.652, 0.025, -0.047),
      'Soeur': (0.756, -0.023, 0.064, 1.257, -0.040, 0.022),
      'Maje': (0.716, 0.013, 0.178, 0.226, -0.123, -0.101),
      'Steve Madden': (0.539, 0.000, 0.070, -0.569, -0.070, 0.093),
      'Sandro': (0.237, -0.009, 0.084, 0.052, -0.117, 0.314),
      'Lacoste': (0.191, 0.063, 0.072, 0.059, 0.158, 0.017),
      'Studio Anneloes': (0.133, 0.001, 0.021, 0.575, 0.032, 0.033),
      'Claudie Pierlot': (0.089, -0.021, 0.131, -1.132, -0.005, 0.265),
      'Carhartt': (-0.092, 0.049, 0.015, 0.351, -0.225, -0.223),
      'Michael Kors': (-0.098, 0.042, -0.010, -0.976, 0.063, -0.038),
      "Levi's": (-0.150, 0.034, -0.044, -0.728, 0.022, -0.339),
      'Armedangels': (-0.153, -0.006, -0.152, 1.398, -0.029, 0.350),
      'Lululemon': (-0.305, -0.009, -0.060, -1.831, 0.011, -0.328),
      'Hugo Boss': (-0.342, -0.001, -0.178, -0.099, 0.019, -0.288),
      'Allbirds': (-0.386, -0.041, -0.152, 0.583, -0.153, -0.092),
      'The North Face': (-0.886, -0.217, -0.338, -0.960, -0.059, -0.544)}
cols5 = ['delta_rating', 'delta_sust', 'delta_vader', 'att_rating', 'att_sust_score', 'att_value_vader']
for b, vals in T5.items():
    for col, v in zip(cols5, vals):
        check(f'Table 5 {b} {col}', v, t5.loc[b, col])

gaps = t('synthdid_pretrend_gaps.csv').set_index('outcome')
for o, (raw, syn) in {'rating': (1.15, 1.03), 'sust_score': (0.129, 0.115),
                      'value_vader': (0.304, 0.286)}.items():
    tol = 0.005 if o == 'rating' else TOL
    check(f'Section 5.2 pre-launch gap {o} raw control', raw, gaps.loc[o, 'gap_raw_control'], tol=tol)
    check(f'Section 5.2 pre-launch gap {o} synthetic', syn, gaps.loc[o, 'gap_synth_control'], tol=tol)
bg = t('synthdid_pretrend_gap_by_brand.csv').set_index('brand')['gap_synth_control']
check('Section 5.2 best synthetic fit (Studio Anneloes)', 0.64, bg['Studio Anneloes'], tol=0.006)  # 0.635 printed as 0.64
check('Section 5.2 worst synthetic fit (Allbirds)', 1.58, bg['Allbirds'], tol=0.005)
check('Section 5.2 synthetic fit SD across brands', 0.22, bg.std(), tol=0.005)
pm = t('figure3_pre_launch_means.csv')['pre_launch_mean_rating']
check('Section 5.2 pre-launch mean rating, treatment', 1.96, pm[0], tol=0.005)
check('Section 5.2 pre-launch mean rating, controls', 2.62, pm[1], tol=0.005)
ev = t('figure3_figure6_event_time_means.csv')
check('Figure 3 first event time (years)', -6.0, ev['event_time'].min(), tol=0)
check('Figure 3 last event time (years)', 4.25, ev['event_time'].max(), tol=0)
check('Figure 3 treated at -6 (read from figure)', 2.17, ev['treated'].iloc[0], tol=0.02)
check('Figure 3 control at -6 (read from figure)', 2.68, ev['raw_control'].iloc[0], tol=0.02)

if (TABLES / 'tableA7_synthdid_excl_lowvol.csv').exists():
    a7 = t('tableA7_synthdid_excl_lowvol.csv').set_index('outcome')
    for o, (a, p) in {'rating': (-0.167, 0.079), 'sust_score': (-0.031, 0.003),
                      'value_vader': (-0.111, 0.002)}.items():
        check(f'Table A.7 {o} ATT', a, a7.loc[o, 'att_excl_lowvol'], random=True)
        check(f'Table A.7 {o} p', p, a7.loc[o, 'p_excl_lowvol'], random=True, tol=0.1)

# -- Study 2 ---------------------------------------------------------------------------
def check_ols(table, prefix, model_names, expected, adj, pcol='p'):
    d = t(table)
    for i, m in enumerate(model_names):
        sub = d[d['model'] == m].set_index('variable')
        for var, triples in expected.items():
            b, se, p = triples[i]
            check(f'{prefix} {m} {var} beta', b, sub.loc[var, 'beta'])
            check(f'{prefix} {m} {var} SE', se, sub.loc[var, 'se'])
            if pcol != 'p' and abs(sub.loc[var, pcol] - p) > TOL and abs(sub.loc[var, 'p'] - p) <= TOL:
                # Table 6 mixes conventions: a few rows print the t-based p-value
                rows.append({'item': f'{prefix} {m} {var} p', 'thesis': p,
                             'reproduced': round(float(sub.loc[var, 'p']), 4),
                             'status': 'MATCH (t-based p-value)'})
            else:
                check(f'{prefix} {m} {var} p', p, sub.loc[var, pcol])
        check(f'{prefix} {m} adj. R2', adj[i], sub['adj_r2'].iloc[0])


check_ols('table6_moderation.csv', 'Table 6',
          ['ATT rating', 'ATT sust_score', 'ATT value_vader'],
          {'integration': [(-0.210, 0.478, 0.661), (0.014, 0.055, 0.803), (-0.115, 0.105, 0.272)],
           'messaging':   [(0.177, 0.248, 0.476), (0.015, 0.027, 0.588), (0.003, 0.083, 0.974)],
           'discount':    [(-0.021, 0.027, 0.432), (-0.001, 0.003, 0.649), (-0.004, 0.010, 0.711)],
           'services':    [(0.072, 0.351, 0.838), (-0.041, 0.048, 0.393), (-0.029, 0.118, 0.809)],
           'seg_outdoor': [(-0.990, 0.824, 0.230), (-0.061, 0.066, 0.356), (-0.323, 0.194, 0.121)],
           'seg_premium': [(-0.805, 0.546, 0.141), (0.101, 0.057, 0.074), (-0.139, 0.157, 0.392)],
           '(Intercept)': [(1.298, 1.691, 0.443), (0.041, 0.200, 0.838), (0.588, 0.603, 0.349)]},
          [-0.275, 0.169, 0.107], pcol='p_normal')
check_ols('table7_interaction.csv', 'Table 7',
          ['ATT rating', 'ATT sust_score', 'ATT value_vader'],
          {'integration': [(1.354, 0.897, 0.152), (0.211, 0.070, 0.009), (0.210, 0.230, 0.374)],
           'messaging':   [(1.200, 0.712, 0.113), (0.163, 0.072, 0.039), (0.205, 0.226, 0.379)],
           'int_x_msg':   [(-0.486, 0.301, 0.126), (-0.070, 0.026, 0.016), (-0.113, 0.085, 0.205)],
           '(Intercept)': [(-3.315, 2.152, 0.144), (-0.496, 0.191, 0.020), (-0.310, 0.617, 0.623)]},
          [-0.032, 0.032, 0.167])
check_ols('tableA8a_moderation_raw_change.csv', 'Table A.8a',
          ['delta_rating', 'delta_sust', 'delta_vader'],
          {'integration': [(-0.155, 0.374, 0.678), (-0.033, 0.035, 0.345), (-0.029, 0.098, 0.764)],
           'messaging':   [(-0.362, 0.211, 0.085), (0.011, 0.015, 0.458), (-0.117, 0.053, 0.026)],
           'discount':    [(-0.067, 0.031, 0.051), (-0.001, 0.003, 0.731), (-0.013, 0.007, 0.093)],
           'services':    [(0.284, 0.425, 0.504), (-0.043, 0.037, 0.249), (0.082, 0.095, 0.389)]},
          [0.290, 0.016, 0.363])
check_ols('tableA8b_interaction_raw_change.csv', 'Table A.8b', ['delta_rating interaction'],
          {'integration': [(1.644, 0.721, 0.023)], 'messaging': [(0.924, 0.613, 0.132)],
           'int_x_msg': [(-0.544, 0.235, 0.020)], 'discount': [(-0.061, 0.033, 0.090)],
           'services': [(0.116, 0.468, 0.804)]},
          [0.333])

# Appendix A.8 against the file the original script saved (exact reproduction)
orig = pd.read_csv(ROOT / 'results' / 'thesis_run' / 'study2_raw_change_thesis_run.csv')
name_map = {'S2_delta_rating': 'delta_rating', 'S2_delta_sust': 'delta_sust',
            'S2_delta_vader': 'delta_vader', 'S2_interact_rating': 'delta_rating interaction'}
new = pd.concat([t('tableA8a_moderation_raw_change.csv'), t('tableA8b_interaction_raw_change.csv')])
for _, r in orig.iterrows():
    sub = new[(new['model'] == name_map[r['model']]) & (new['variable'] == r['variable'])]
    for col_o, col_n in [('beta', 'beta'), ('se', 'se'), ('p_value', 'p')]:
        rows.append({'item': f"A.8 vs original script output: {name_map[r['model']]} {r['variable']} {col_n}",
                     'thesis': r[col_o], 'reproduced': round(float(sub[col_n].iloc[0]), 4),
                     'status': 'MATCH' if abs(float(sub[col_n].iloc[0]) - r[col_o]) <= 0.00051 else 'DIFFERENT'})


# -- Report ------------------------------------------------------------------------------
def md_table(d):
    lines = ['| ' + ' | '.join(d.columns) + ' |', '|' + '---|' * len(d.columns)]
    lines += ['| ' + ' | '.join('' if pd.isna(v) else str(v) for v in r) + ' |' for r in d.itertuples(index=False)]
    return '\n'.join(lines) + '\n'


rep = pd.DataFrame(rows)

# Known, explained differences (see README "Notes and corrections")
REASONS = [
    ('Table 5 Ba&sh delta', 'PDF swaps the Delta values of Ba&sh and Balzac Paris; thesis text agrees with the data'),
    ('Table 5 Balzac Paris delta', 'PDF swaps the Delta values of Ba&sh and Balzac Paris; thesis text agrees with the data'),
    ('Table A.8', 'PDF rows partly from an earlier run with rough discount values; code matches the original script output (A.8 vs original rows)'),
    ('Table 2 Control: post-event sd_sust', 'Typo in PDF: data give 0.341'),
    ('Table 3 SDID', 'Placebo SEs are random; exact match uses thesis-run SEs (rows without "fresh")'),
    ('Table A.7', 'Placebo SEs are random; thesis run did not save per-brand results for this check'),
    ('Table 3 C&S', 'Bootstrap SEs are random'),
]
def reason(item, status):
    if status.startswith('MATCH') and 'random' not in status:
        return ''
    for prefix, why in REASONS:
        if item.startswith(prefix):
            return why
    return 'UNEXPLAINED' if status.startswith('DIFFERENT') else ''
rep['reason'] = [reason(i, st) for i, st in zip(rep['item'], rep['status'])]
summary = rep['status'].value_counts()
out = ROOT / 'results' / 'verification_report.md'
with open(out, 'w') as f:
    f.write('# Verification report\n\n')
    f.write('Generated by `code/99_check_against_thesis.py`. Every number printed in the thesis '
            'tables is compared with the value reproduced by the code in this repository.\n\n')
    f.write('A value MATCHES when it rounds to the number printed in the thesis. '
            '"random" marks numbers that depend on random resampling (placebo or bootstrap '
            'standard errors), which cannot be regenerated exactly because the thesis runs had no '
            'fixed seed. Every difference is listed below with its reason.\n\n')
    f.write('| Status | Count |\n|---|---|\n')
    for s, n in summary.items():
        f.write(f'| {s} | {n} |\n')
    diff = rep[rep['status'].str.startswith('DIFFERENT')]
    f.write('\n## Differences\n\n')
    f.write(md_table(diff) if len(diff) else 'None.\n')
    f.write('\n\n## All checks\n\n' + md_table(rep) + '\n')
print(summary.to_string())
unexplained = rep[rep['reason'] == 'UNEXPLAINED']
print(f"\nUnexplained differences: {len(unexplained)}")
if len(unexplained):
    print(unexplained.to_string(index=False))
print('\nSaved', out)
