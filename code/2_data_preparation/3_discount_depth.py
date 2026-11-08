"""
2_data_preparation/3_discount_depth.py - where the discount-depth moderator comes from

Thesis: Section 4.2.2 (discount depth and footnote 2), Appendix A.3
Input:  data/discount_depth_listings.csv - for each of the 21 treatment brands,
        10 resale listings matched by hand to the same item's current retail
        price (collected May 2026).
Output: results/tables/discount_depth_by_brand.csv

For each pair:  discount = (retail - resale) / retail x 100.
A brand's discount depth is the mean over its 10 pairs (column `discount` in
data/treatment_brands_moderators.csv); the SD shows how much prices vary within
the brand. Footnote 2 of the thesis compares the mean of the first 5 listings
with the mean of all 10 to show the measure is stable; that comparison is
reproduced here too.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import DATA, TABLES

d = pd.read_csv(DATA / "discount_depth_listings.csv")
d['discount_pct'] = (d['retail_eur'] - d['resale_eur']) / d['retail_eur'] * 100

by_brand = d.groupby('brand').agg(
    discount_mean_10=('discount_pct', 'mean'), discount_sd_10=('discount_pct', 'std'),
    discount_mean_first5=('discount_pct', lambda s: s.iloc[:5].mean())).reset_index()
by_brand['diff_10_minus_5_pp'] = by_brand['discount_mean_10'] - by_brand['discount_mean_first5']

mods = pd.read_csv(DATA / "treatment_brands_moderators.csv")[['brand', 'discount', 'discount_sd']]
by_brand = by_brand.merge(mods, on='brand')
by_brand.round(2).to_csv(TABLES / "discount_depth_by_brand.csv", index=False)

max_gap = (by_brand['discount_mean_10'] - by_brand['discount']).abs().max()
print(by_brand.round(2).to_string(index=False))
print(f"\nLargest gap to the values used in the analysis: {max_gap:.3f} pp")
print(f"Within-brand SD range: {by_brand['discount_sd_10'].min():.1f} to {by_brand['discount_sd_10'].max():.1f} pp")
print(f"10-listing minus 5-listing mean: {by_brand['diff_10_minus_5_pp'].min():+.1f} to {by_brand['diff_10_minus_5_pp'].max():+.1f} pp, "
      f"mean absolute {by_brand['diff_10_minus_5_pp'].abs().mean():.1f} pp")
