# Data collection: Trustpilot scrapers

These scripts collected the 49,736 Trustpilot reviews used in the thesis (Section 4.1). They are included for transparency. They are not needed to reproduce the results, because the scored data is already in `data/`.

## Why Trustpilot

Brand sales data is confidential, so the thesis measures perception through reviews. Customers write them unprompted, they carry a timestamp, and they are public. Other sources were considered and dropped (thesis Section 4.1, footnote 1):

| Source | Why it was not used |
|---|---|
| Avis Vérifiés | Restricts programmatic access |
| Bazaarvoice | Data is not organised in a way that allows tracking brands over time |
| Wayback Machine | Trustpilot pages are not archived in a usable form |
| Reddit | The application for API access was denied |

## How the brands were chosen

**Treatment brands, 21 in total, run their own resale programme.** They were identified from the public partner lists of the two largest resale infrastructure providers: Trove, mostly North American brands, and Faume, mostly European brands. Two brands run on Archive. Using published partner lists makes the selection transparent and repeatable. Each brand's launch month comes from press releases and the brand's own site; see `data/treatment_brands_moderators.csv`.

**Control brands, 27 in total, have no confirmed own resale programme.** They were picked in the same market segment and product category as specific treatment brands. For example, Moncler and Moose Knuckles were picked for Canada Goose, and Hoka for Allbirds. Where Trustpilot had enough candidates, one treatment brand got several controls. This is why there are more controls than treatment brands: a bigger donor pool gives synthetic DiD more room to match each treatment brand. The matching is listed in `data/control_brands.csv`.

**Three segments:** contemporary fashion, premium fashion, and outdoor and athletic.

**Exclusions:** Arc'teryx (0 reviews before launch) and Patagonia (2) are collected but not used in the before/after analysis. Their resale programmes are older than their Trustpilot history.

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
