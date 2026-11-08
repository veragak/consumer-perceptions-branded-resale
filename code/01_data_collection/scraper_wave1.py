"""
scraper_wave1.py - Trustpilot scraper, first collection wave

What it does
  1. Opens Chrome (undetected-chromedriver, so Trustpilot does not block it).
  2. Asks you to log in to Trustpilot once by hand; Trustpilot redirects to a
     login page after a number of review pages otherwise.
  3. For each brand in brands_config.py, opens its Trustpilot page and reads
     every review page by page: date, star rating, title, text, country.
  4. Adds the brand's study information and labels each review "pre" or
     "post" relative to the resale launch (controls get "control").
  5. Saves one CSV per brand plus a combined file.

Install:   pip install undetected-chromedriver selenium pandas
Usage (from this folder):
    python scraper_wave1.py --all            # every brand in brands_config.py
    python scraper_wave1.py --treatment      # treatment brands only
    python scraper_wave1.py --brand bash     # one brand (key from the config)
Output:    data/selenium/<brand>_trustpilot.csv and all_trustpilot_master.csv

CHROME_VERSION below must match the Chrome installed on your computer.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time, random, os, argparse
import pandas as pd
from datetime import date
from brands_config import BRANDS, get_treatment_brands, get_control_brands, print_brand_overview

CHROME_VERSION = 145  # update if your Chrome version changes

# ── Driver ────────────────────────────────────────────────────

def make_driver():
    opts = uc.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    return uc.Chrome(options=opts, version_main=CHROME_VERSION)


def login(driver):
    """Open login page and wait for user to authenticate manually."""
    driver.get("https://www.trustpilot.com/login")
    time.sleep(3)
    print("\n" + "="*60)
    print("👉 Please log in with your Google account in the browser")
    print("👉 Once logged in and you can see your profile, come back")
    input("   Press Enter AFTER you have logged in...")
    print("="*60)


# ── Review extraction ─────────────────────────────────────────

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
                "date":     pub,
                "rating":   stars,
                "title":    (r.get("title") or "").strip(),
                "text":     text,
                "verified": r.get("isVerified", False),
                "consumer_country": (r.get("consumer", {}) or {}).get("countryCode", ""),
            })
        return reviews
    except:
        return []


# ── Period labeling ───────────────────────────────────────────

def add_period_labels(df, config):
    launch = config.get("resale_launch")
    df["period"] = "outside_window"
    if launch and config.get("did_feasible") and config["group"] == "treatment":
        launch_dt = pd.Timestamp(launch)
        dt = pd.to_datetime(df["date"], errors="coerce")
        df.loc[(dt >= launch_dt - pd.DateOffset(months=12)) &
               (dt <  launch_dt), "period"] = "pre"
        df.loc[(dt >= launch_dt + pd.DateOffset(months=3)) &
               (dt <= launch_dt + pd.DateOffset(months=15)), "period"] = "post"
    elif config["group"] == "control":
        df["period"] = "control"
    return df


# ── Single brand scraper ──────────────────────────────────────

def scrape_brand(driver, brand_key, max_pages=200):
    config   = BRANDS[brand_key]
    slug     = config.get("trustpilot_slug", "")
    if not slug:
        print(f"  ⚠️  No Trustpilot slug for {config['display_name']} — skipping")
        return pd.DataFrame()

    url_base = f"https://www.trustpilot.com/review/{slug}"
    print(f"\n{'─'*60}")
    print(f"📥  {config['display_name']}  ({config['group'].upper()} · {config.get('segment','')})")
    if config.get("resale_launch"):
        did = "✅ DiD" if config.get("did_feasible") else "📊 Study 2 only"
        print(f"    Launch: {config['resale_launch'].strftime('%b %d %Y')}  {did}")

    all_reviews = []

    for page_num in range(1, max_pages + 1):
        url = f"{url_base}?page={page_num}" if page_num > 1 else url_base

        # Load page with crash recovery
        for attempt in range(3):
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                break
            except Exception as e:
                if attempt == 2:
                    print(f"\n  ❌ Failed to load page {page_num} after 3 attempts: {e}")
                    return _build_df(all_reviews, brand_key, config)
                print(f"\n  ⚠️  Crash on page {page_num}, retrying ({attempt+1}/3)...")
                try: driver.quit()
                except: pass
                time.sleep(5)
                driver = make_driver()
                login(driver)
                driver.get(url)
                time.sleep(4)

        # Accept cookies on page 1
        if page_num == 1:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(., 'Accept') or contains(., 'Agree')]"))
                )
                btn.click()
                time.sleep(2)
            except:
                pass

        # Handle login redirect
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
            print()  # newline every 10 pages

        # No early stopping — scrape all available reviews

    print(f"\n    ✅ Total raw: {len(all_reviews)} reviews")
    return _build_df(all_reviews, brand_key, config)


def _build_df(all_reviews, brand_key, config):
    if not all_reviews:
        return pd.DataFrame()
    df = pd.DataFrame(all_reviews)
    df["brand"]          = config["display_name"]
    df["brand_key"]      = brand_key
    df["segment"]        = config.get("segment", "")
    df["group"]          = config["group"]
    df["resale_program"] = config.get("resale_program", "")
    for var in ["integration_level", "messaging_intensity", "discount_depth", "service_offerings"]:
        df[var] = config.get(var)
    df = add_period_labels(df, config)

    if config.get("did_feasible") and config["group"] == "treatment":
        pre  = len(df[df["period"] == "pre"])
        post = len(df[df["period"] == "post"])
        ok_pre  = "✅" if pre  >= 20 else "⚠️  LOW"
        ok_post = "✅" if post >= 20 else "⚠️  LOW"
        print(f"    📊 Pre: {pre} {ok_pre}   Post: {post} {ok_post}")
    return df


# ── Master merge ──────────────────────────────────────────────

def merge_and_save(dfs, output_dir):
    valid = [d for d in dfs if d is not None and not d.empty]
    if not valid:
        print("⚠️  No data collected.")
        return pd.DataFrame()
    merged = (pd.concat(valid, ignore_index=True)
                .sort_values(["brand_key", "date"])
                .reset_index(drop=True))
    out = os.path.join(output_dir, "all_trustpilot_master.csv")
    merged.to_csv(out, index=False, encoding="utf-8")

    print(f"\n{'═'*60}")
    print(f"MASTER FILE: {out}  ({len(merged):,} reviews, {merged['brand'].nunique()} brands)\n")
    print(f"  {'Brand':<22} {'Group':<10} {'Total':>7}  Pre    Post")
    print(f"  {'─'*60}")
    for bk in merged["brand_key"].unique():
        bdf  = merged[merged["brand_key"] == bk]
        cfg  = BRANDS[bk]
        pre  = len(bdf[bdf["period"] == "pre"])
        post = len(bdf[bdf["period"] == "post"])
        print(f"  {cfg['display_name']:<22} {cfg['group']:<10} {len(bdf):>7}  "
              f"{pre or '—':>5}  {post or '—':>5}")
    return merged


# ── Main ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--brand",     type=str)
    grp.add_argument("--all",       action="store_true")
    grp.add_argument("--treatment", action="store_true")
    grp.add_argument("--control",   action="store_true")
    grp.add_argument("--did-only",  action="store_true", dest="did_only")
    parser.add_argument("--output", type=str, default="data/selenium")
    parser.add_argument("--pages",  type=int, default=200)
    args = parser.parse_args()

    print_brand_overview()

    if args.brand:
        if args.brand not in BRANDS:
            print(f"❌ Unknown brand: '{args.brand}'")
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

    # Single login at the start
    driver = make_driver()
    login(driver)

    dfs = []
    for i, key in enumerate(keys):
        df = scrape_brand(driver, key, max_pages=args.pages)
        if not df.empty:
            out = os.path.join(args.output, f"{key}_trustpilot.csv")
            df.to_csv(out, index=False, encoding="utf-8")
            print(f"    💾 Saved: {out}")
        dfs.append(df)
        if i < len(keys) - 1:
            pause = random.uniform(8, 15)
            print(f"    ⏸  Pausing {pause:.0f}s before next brand...")
            time.sleep(pause)

    try:
        driver.quit()
    except:
        pass

    if len(dfs) > 1:
        merge_and_save(dfs, args.output)
    elif dfs and not dfs[0].empty:
        print(f"\n✅ Done: {len(dfs[0])} reviews")


if __name__ == "__main__":
    main()
