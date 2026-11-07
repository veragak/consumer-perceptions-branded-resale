# Data collection: Trustpilot scrapers

These scripts collected the 49,736 Trustpilot reviews used in the thesis (Section 4.1). They are included for transparency. They are not needed to reproduce the results, because the scored data is already in `data/`.

## How the data was collected

Reviews were scraped from each brand's public Trustpilot page with Selenium and `undetected-chromedriver`. The scraper opens a Chrome window and asks you to log in to Trustpilot by hand, because Trustpilot redirects to a login page after a number of review pages. It then pages through the brand's reviews. In the second wave, treatment brands were collected without a page limit, and control brands were capped at 100 pages, about 2,000 reviews. For each review it stores the date, star rating, title, text and reviewer country, together with the brand's study variables from the config file.

The data was collected in two waves:

| File | Wave | Brands |
|---|---|---|
| `scraper_wave1.py` with `brands_config.py` | First design | 24 brands |
| `scraper_wave2.py` with `brands_config_new.py` | Extended design | 29 more brands, mostly control brands |
| `scraper_wave2_retry.py` | Re-run | Brands whose first run stopped early |

Some brands were collected in both waves. `02_score_reviews.py` removes the duplicates. The final sample has 48 brands: 21 treatment and 27 control.

Both config files also contain early guesses of the design variables, such as discount depth. These were later replaced by the hand-coded values in `data/treatment_brands_moderators.csv` (thesis Appendix A.3). The analysis only uses that CSV.

## Running a scraper

```bash
pip install undetected-chromedriver selenium pandas
cd code/01_data_collection
python scraper_wave2.py --brand carhartt
```

The output goes to `data/selenium/<brand>_trustpilot.csv`, relative to where you run it. To rebuild the scored dataset, move these files to `private/raw/` and run `python code/02_score_reviews.py` from the repository root.

Trustpilot's page layout changes over time, so the CSS selectors in `extract_reviews()` may need updating. Check Trustpilot's terms of use before scraping.
