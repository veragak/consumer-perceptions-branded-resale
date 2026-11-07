"""
Trustpilot Scraper — NEW BRANDS ONLY
Thesis: Consumer Perceptions of Branded Resale Channels

Scraping strategy:
  Treatment brands — ALL available reviews (no page cap)
  Control brands   — max 100 pages (~2,000 reviews)

Output format matches data_thesis.xlsx:
  date · rating · title · text · consumer_country · brand · segment ·
  group · resale_program · integration_level · messaging_intensity ·
  discount_depth · service_offerings · period

Install:
    pip install undetected-chromedriver selenium

Usage:
    python trustpilot_selenium_scraper.py --all
    python trustpilot_selenium_scraper.py --treatment
    python trustpilot_selenium_scraper.py --control
    python trustpilot_selenium_scraper.py --brand carhartt

Output:
    data/selenium/<brand>_trustpilot.csv
    data/selenium/all_trustpilot_master.csv
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time, random, os, argparse
import pandas as pd
from brands_config_new import BRANDS, get_treatment_brands, get_control_brands, print_brand_overview

CHROME_VERSION      = 146   # update to match your installed Chrome version
MAX_PAGES_CONTROL   = 100   # ~2,000 reviews
MAX_PAGES_TREATMENT = 500   # effectively unlimited


# ── Driver ───────────────────────────────────────────────────────────────────

def make_driver():
    opts = uc.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    return uc.Chrome(options=opts, version_main=CHROME_VERSION)


def login(driver):
    driver.get("https://www.trustpilot.com/login")
    time.sleep(3)
    print("\n" + "="*60)
    print("👉 Please log in with your Google account in the browser")
    print("👉 Once logged in and you can see your profile, come back")
    input("   Press Enter AFTER you have logged in...")
    print("="*60)


# ── Review extraction ────────────────────────────────────────────────────────

def extract_reviews(driver):
    try:
        script = driver.find_element(By.ID, "__NEXT_DATA__")
        data   = json.loads(script.get_attribute("innerHTML"))
        raw    = (data.get("props", {})
                      .get("pageProps", {})
                      .get("reviews", []))
        reviews = []
        for r in raw:
            dates  = r.get("dates", {}) or {}
            rating = r.get("rating", {})
            stars  = rating if isinstance(rating, int) else (rating or {}).get("stars", 0)
            pub    = (dates.get("publishedDate") or "")[:10]
            text   = (r.get("text") or "").strip()
            if text in ("[deleted]", "[removed]", ""):
                text = ""
            reviews.append({
                "date":             pub,
                "rating":           stars,
                "title":            (r.get("title") or "").strip(),
                "text":             text,
                "consumer_country": (r.get("consumer", {}) or {}).get("countryCode", ""),
            })
        return reviews
    except Exception:
        return []


# ── Period labeling ──────────────────────────────────────────────────────────

def add_period_labels(df, config):
    """
    All reviews before launch date  → 'pre'
    All reviews after launch date   → 'post'
    Control brands                  → 'control'

    DiD windowing (12-month pre, 3-15 month post buffer) is applied
    at analysis time, not here. This matches data_thesis.xlsx exactly.
    """
    launch = config.get("resale_launch")
    df["period"] = "outside_window"

    if launch and config["group"] == "treatment":
        launch_dt = pd.Timestamp(launch)
        dt = pd.to_datetime(df["date"], errors="coerce")
        df.loc[dt < launch_dt,  "period"] = "pre"
        df.loc[dt >= launch_dt, "period"] = "post"
    elif config["group"] == "control":
        df["period"] = "control"

    return df


# ── Build DataFrame ──────────────────────────────────────────────────────────

def _build_df(all_reviews, brand_key, config):
    """Columns match data_thesis.xlsx exactly."""
    if not all_reviews:
        return pd.DataFrame()

    df = pd.DataFrame(all_reviews)
    df["brand"]          = config["display_name"]
    df["segment"]        = config.get("segment", "")
    df["group"]          = config["group"]
    df["resale_program"] = config.get("resale_program")

    for var in ["integration_level", "messaging_intensity", "discount_depth", "service_offerings"]:
        df[var] = config.get(var)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = add_period_labels(df, config)
    df = df[df["text"].str.len() >= 30].copy()

    cols = [
        "date", "rating", "title", "text", "consumer_country",
        "brand", "segment", "group", "resale_program",
        "integration_level", "messaging_intensity", "discount_depth",
        "service_offerings", "period",
    ]
    return df[[c for c in cols if c in df.columns]].sort_values("date").reset_index(drop=True)


# ── Single brand scraper ─────────────────────────────────────────────────────

def scrape_brand(driver, brand_key, output_dir="data/selenium"):
    config     = BRANDS[brand_key]
    slug       = config.get("trustpilot_slug", "")
    is_control = config["group"] == "control"
    max_pages  = MAX_PAGES_CONTROL if is_control else MAX_PAGES_TREATMENT
    url_base   = f"https://www.trustpilot.com/review/{slug}"

    if not slug:
        print(f"  ⚠️  No slug for {config['display_name']} — skipping")
        return pd.DataFrame()

    print(f"\n{'─'*60}")
    plat = config.get("resale_platform", "")
    print(f"📥  {config['display_name']}  "
          f"({config['group'].upper()} · {config.get('segment','')} · {plat})")
    if config.get("resale_launch"):
        did = "✅ DiD" if config.get("did_feasible") else "📊 Study 2"
        print(f"    Launch: {config['resale_launch'].strftime('%b %d %Y')}  {did}")
    cap = f"capped at {max_pages} pages (~{max_pages*20:,} reviews)" if is_control else "ALL pages"
    print(f"    Mode: {cap}")

    all_reviews = []

    for page_num in range(1, max_pages + 1):
        url = f"{url_base}?page={page_num}" if page_num > 1 else url_base

        for attempt in range(3):
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                break
            except Exception as e:
                if attempt == 2:
                    print(f"\n  ❌ Failed page {page_num}: {e}")
                    df = _build_df(all_reviews, brand_key, config)
                    _save(df, brand_key, output_dir, config)
                    return df
                print(f"\n  ⚠️  Crash p{page_num}, retrying ({attempt+1}/3)...")
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(5)
                driver = make_driver()
                login(driver)

        if page_num == 1:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Accept') or contains(., 'Agree')]"))
                )
                btn.click()
                time.sleep(2)
            except Exception:
                pass

        if "users/connect" in driver.current_url or "login" in driver.current_url:
            print(f"\n  ⚠️  Session expired on page {page_num} — please log in again")
            login(driver)
            driver.get(url)
            time.sleep(3)

        reviews = extract_reviews(driver)
        if not reviews:
            print(f"\n    [empty page {page_num} — stopping]")
            break

        all_reviews.extend(reviews)
        dates    = sorted([r["date"] for r in reviews if r["date"]])
        earliest = dates[0] if dates else "?"
        latest   = dates[-1] if dates else "?"
        print(f"    p{page_num}:{len(reviews)} ({earliest}→{latest})", end=" ", flush=True)
        if page_num % 10 == 0:
            print(f"  [{len(all_reviews):,} total]")

    print(f"\n    ✅ Total raw: {len(all_reviews):,} reviews")
    df = _build_df(all_reviews, brand_key, config)
    _save(df, brand_key, output_dir, config)
    return df


def _save(df, brand_key, output_dir, config):
    if df.empty:
        return
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, f"{brand_key}_trustpilot.csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"    💾 Saved: {out}  ({len(df):,} rows)")
    if config.get("did_feasible") and config["group"] == "treatment":
        pre  = len(df[df["period"] == "pre"])
        post = len(df[df["period"] == "post"])
        print(f"    📊 Pre:  {pre:,}  {'✅' if pre  >= 50 else '⚠️ LOW'}")
        print(f"    📊 Post: {post:,}  {'✅' if post >= 50 else '⚠️ LOW'}")


# ── Master merge ─────────────────────────────────────────────────────────────

def merge_and_save(dfs, output_dir):
    valid = [d for d in dfs if d is not None and not d.empty]
    if not valid:
        print("⚠️  No data collected.")
        return pd.DataFrame()

    merged = (pd.concat(valid, ignore_index=True)
                .sort_values(["brand", "date"])
                .reset_index(drop=True))

    out = os.path.join(output_dir, "all_trustpilot_master.csv")
    merged.to_csv(out, index=False, encoding="utf-8")

    print(f"\n{'═'*65}")
    print(f"MASTER FILE: {out}")
    print(f"  {len(merged):,} reviews  |  {merged['brand'].nunique()} brands\n")
    print(f"  {'Brand':<24} {'Group':<11} {'Platform':<10} {'Total':>7}  Pre    Post")
    print(f"  {'─'*65}")
    for k, v in BRANDS.items():
        bdf = merged[merged["brand"] == v["display_name"]]
        if bdf.empty:
            continue
        pre  = len(bdf[bdf["period"] == "pre"])
        post = len(bdf[bdf["period"] == "post"])
        plat = v.get("resale_platform", "—")
        print(f"  {v['display_name']:<24} {v['group']:<11} {plat:<10} "
              f"{len(bdf):>7}  {pre or '—':>5}  {post or '—':>5}")
    return merged


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--brand",     type=str)
    grp.add_argument("--all",       action="store_true")
    grp.add_argument("--treatment", action="store_true")
    grp.add_argument("--control",   action="store_true")
    grp.add_argument("--did-only",  action="store_true", dest="did_only")
    parser.add_argument("--output", type=str, default="data/selenium")
    args = parser.parse_args()

    print_brand_overview()

    if args.brand:
        if args.brand not in BRANDS:
            print(f"❌ Unknown brand: '{args.brand}'")
            print(f"   Valid keys: {', '.join(BRANDS.keys())}")
            return
        keys = [args.brand]
    elif args.all:
        keys = list(BRANDS.keys())
    elif args.treatment:
        keys = get_treatment_brands()
    elif args.control:
        keys = get_control_brands()
    elif args.did_only:
        keys = get_treatment_brands(did_only=True)
    else:
        keys = []

    os.makedirs(args.output, exist_ok=True)

    driver = make_driver()
    driver.get("https://www.trustpilot.com")
    time.sleep(4)
    if "login" in driver.current_url or "users/connect" in driver.current_url:
        login(driver)
    else:
        print("\n✅ Session active — no login needed\n")

    dfs = []
    try:
        for i, key in enumerate(keys):
            df = scrape_brand(driver, key, output_dir=args.output)
            dfs.append(df)
            if i < len(keys) - 1:
                pause = random.uniform(8, 15)
                print(f"    ⏸  Pausing {pause:.0f}s...")
                time.sleep(pause)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    if len(dfs) > 1:
        merge_and_save(dfs, args.output)
    elif dfs and not dfs[0].empty:
        print(f"\n✅ Done: {len(dfs[0]):,} reviews for {keys[0]}")


if __name__ == "__main__":
    main()
