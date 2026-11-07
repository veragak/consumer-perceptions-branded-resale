"""
Trustpilot Retry Scraper — Targeted brands only
Thesis: Consumer Perceptions of Branded Resale Channels

Fixes vs previous run:
  - ONE login at the start, session reused across all brands
  - Empty pages trigger retries (15s / 30s / 45s) instead of early stop
  - All reviews collected, no page cap for treatment brands
  - Control brands capped at 100 pages (~2,000 reviews)

Brands in this file:
  TREATMENT: Aigle, Soeur, Balzac Paris, Steve Madden, Armedangels,
             The North Face, Studio Anneloes
  CONTROL:   Organic Basics, Rouje, Sessùn

Output format matches data_thesis.xlsx exactly:
  date · rating · title · text · consumer_country · brand · segment ·
  group · resale_program · integration_level · messaging_intensity ·
  discount_depth · service_offerings · period

Usage:
    python scraper_retry.py --all
    python scraper_retry.py --treatment
    python scraper_retry.py --control
    python scraper_retry.py --brand aigle
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time, random, os, argparse
import pandas as pd
from datetime import date

CHROME_VERSION    = 146   # update to match chrome://settings/help
MAX_PAGES_CONTROL = 100   # ~2,000 reviews

# ── Brand definitions ────────────────────────────────────────────────────────

BRANDS = {

    # ── TREATMENT — Faume ────────────────────────────────────────────────────

    "aigle": {
        "display_name": "Aigle",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "resale_platform": "Faume",
        "trustpilot_slug": "www.aigle.com",
        "resale_launch": date(2020, 10, 1),
        "resale_program": "Aigle Second Souffle",
        "did_feasible": True,
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 2,
    },
    "soeur": {
        "display_name": "Soeur",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Faume",
        "trustpilot_slug": "www.soeur.fr",
        "resale_launch": date(2025, 2, 1),
        "resale_program": "Soeur Seconde Main",
        "did_feasible": False,
        "integration_level": 3,
        "messaging_intensity": 3,
        "discount_depth": 45,
        "service_offerings": 2,
    },
    "balzac_paris": {
        "display_name": "Balzac Paris",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Faume",
        "trustpilot_slug": "balzac-paris.fr",
        "resale_launch": date(2021, 11, 1),
        "resale_program": "Balzac Paris Seconde Main",
        "did_feasible": True,
        "integration_level": 2,
        "messaging_intensity": 2,
        "discount_depth": 45,
        "service_offerings": 1,
    },

    # ── TREATMENT — Trove ─────────────────────────────────────────────────────

    "steve_madden": {
        "display_name": "Steve Madden",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "stevemadden.eu",
        "resale_launch": date(2022, 1, 1),
        "resale_program": "Steve Madden Re-Booted",
        "did_feasible": True,
        "integration_level": 3,
        "messaging_intensity": 3,
        "discount_depth": 45,
        "service_offerings": 2,
    },
    "armedangels": {
        "display_name": "Armedangels",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "armedangels.com",
        "resale_launch": date(2022, 3, 1),
        "resale_program": "Armedangels Re-Loved",
        "did_feasible": True,
        "integration_level": 2,
        "messaging_intensity": 5,
        "discount_depth": 45,
        "service_offerings": 2,
    },

    # ── TREATMENT — Archive ───────────────────────────────────────────────────

    "thenorthface": {
        "display_name": "The North Face",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "resale_platform": "Archive",
        "trustpilot_slug": "www.thenorthface.com",
        "resale_launch": date(2018, 6, 1),
        "resale_program": "The North Face Renewed",
        "did_feasible": False,
        "integration_level": 3,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 3,
    },
    "studio_anneloes": {
        "display_name": "Studio Anneloes",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Archive",
        "trustpilot_slug": "www.studioanneloes.nl",
        "resale_launch": date(2024, 2, 1),
        "resale_program": "Studio Anneloes Retravel",
        "did_feasible": False,
        "integration_level": 2,
        "messaging_intensity": 3,
        "discount_depth": 40,
        "service_offerings": 1,
    },

    # ── CONTROL ───────────────────────────────────────────────────────────────

    "organic_basics": {
        "display_name": "Organic Basics",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "organicbasics.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
    "rouje": {
        "display_name": "Rouje",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "rouje.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
    "sessun": {
        "display_name": "Sessùn",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "sessun.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
    "osprey": {
        "display_name": "Osprey",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "ospreyeurope.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },

    # ── NEW CONTROLS ──────────────────────────────────────────────────────────

    "ted_baker": {
        "display_name": "Ted Baker",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "www.tedbaker.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
    "berghaus": {
        "display_name": "Berghaus",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "www.berghaus.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
    "salomon": {
        "display_name": "Salomon",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "www.salomon.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
    },
}

TREATMENT_KEYS = [k for k, v in BRANDS.items() if v["group"] == "treatment"]
CONTROL_KEYS   = [k for k, v in BRANDS.items() if v["group"] == "control"]


# ── Driver ────────────────────────────────────────────────────────────────────

def make_driver():
    opts = uc.ChromeOptions()
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    return uc.Chrome(options=opts, version_main=CHROME_VERSION)


def login(driver):
    """Manual login — called only when session is not active."""
    driver.get("https://www.trustpilot.com/login")
    time.sleep(3)
    print("\n" + "="*60)
    print("👉 Please log in with your Google account in the browser")
    print("👉 Once you can see your Trustpilot profile, come back here")
    input("   Press Enter AFTER you have logged in...")
    print("="*60 + "\n")


def is_logged_in(driver):
    """Check if current session is still active without navigating away."""
    try:
        url = driver.current_url
        return "/login" not in url and "users/connect" not in url and "authenticate" not in url
    except Exception:
        return False


# ── Review extraction ─────────────────────────────────────────────────────────

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


# ── Period labeling ───────────────────────────────────────────────────────────

def add_period_labels(df, config):
    """
    All reviews before launch  → 'pre'
    All reviews after launch   → 'post'
    Control brands             → 'control'
    Matches data_thesis.xlsx exactly.
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


# ── Build DataFrame ───────────────────────────────────────────────────────────

def _build_df(all_reviews, brand_key, config):
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


# ── Single brand scraper ──────────────────────────────────────────────────────

def scrape_brand(driver, brand_key, output_dir="data/selenium"):
    config     = BRANDS[brand_key]
    slug       = config.get("trustpilot_slug", "")
    is_control = config["group"] == "control"
    max_pages  = MAX_PAGES_CONTROL if is_control else 500
    url_base   = f"https://www.trustpilot.com/review/{slug}"

    print(f"\n{'─'*60}")
    plat = config.get("resale_platform", "")
    print(f"📥  {config['display_name']}  "
          f"({config['group'].upper()} · {config.get('segment', '')} · {plat})")
    if config.get("resale_launch"):
        did = "✅ DiD" if config.get("did_feasible") else "📊 Study 2"
        print(f"    Launch: {config['resale_launch'].strftime('%b %d %Y')}  {did}")
    cap = f"capped at {max_pages} pages" if is_control else "ALL pages"
    print(f"    Mode: {cap}")

    all_reviews = []

    for page_num in range(1, max_pages + 1):
        url = f"{url_base}?page={page_num}&languages=all" if page_num > 1 else f"{url_base}?languages=all"

        # Load page with crash recovery
        for attempt in range(3):
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                break
            except Exception as e:
                if attempt == 2:
                    print(f"\n  ❌ Failed page {page_num} after 3 attempts: {e}")
                    df = _build_df(all_reviews, brand_key, config)
                    _save(df, brand_key, output_dir, config)
                    return df
                print(f"\n  ⚠️  Crash p{page_num}, retrying ({attempt+1}/3)...")
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(10)
                try:
                    driver.quit()
                except Exception:
                    pass
                driver = make_driver()
                driver.get("https://www.trustpilot.com")
                time.sleep(4)
                if not is_logged_in(driver):
                    login(driver)

        # Accept cookies on page 1
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

        # Handle session expiry or crashed browser
        if not is_logged_in(driver):
            print(f"\n  ⚠️  Browser lost on page {page_num} — restarting...")
            try:
                driver.quit()
            except Exception:
                pass
            time.sleep(5)
            driver = make_driver()
            driver.get("https://www.trustpilot.com")
            time.sleep(4)
            if not is_logged_in(driver):
                login(driver)
            driver.get(url)
            time.sleep(3)

        reviews = extract_reviews(driver)

        # If page is empty, retry with delays before giving up
        if not reviews:
            retry_success = False
            for retry in range(3):
                wait = 15 * (retry + 1)
                print(f"\n    [empty p{page_num} — waiting {wait}s, retry {retry+1}/3]",
                      end="", flush=True)
                time.sleep(wait)
                driver.get(url)
                time.sleep(random.uniform(3, 5))
                reviews = extract_reviews(driver)
                if reviews:
                    retry_success = True
                    break
            if not retry_success:
                print(f"\n    [p{page_num} empty after 3 retries — genuinely no more reviews]")
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
        print(f"    ⚠️  No data to save for {config['display_name']}")
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


# ── Master merge ──────────────────────────────────────────────────────────────

def merge_and_save(dfs, output_dir):
    valid = [d for d in dfs if d is not None and not d.empty]
    if not valid:
        print("⚠️  No data collected.")
        return pd.DataFrame()

    merged = (pd.concat(valid, ignore_index=True)
                .sort_values(["brand", "date"])
                .reset_index(drop=True))

    out = os.path.join(output_dir, "retry_trustpilot_master.csv")
    merged.to_csv(out, index=False, encoding="utf-8")

    print(f"\n{'═'*65}")
    print(f"MASTER FILE: {out}")
    print(f"  {len(merged):,} reviews  |  {merged['brand'].nunique()} brands\n")
    print(f"  {'Brand':<24} {'Group':<11} {'Total':>7}  Pre    Post")
    print(f"  {'─'*60}")
    for k, v in BRANDS.items():
        bdf = merged[merged["brand"] == v["display_name"]]
        if bdf.empty:
            continue
        pre  = len(bdf[bdf["period"] == "pre"])
        post = len(bdf[bdf["period"] == "post"])
        print(f"  {v['display_name']:<24} {v['group']:<11} "
              f"{len(bdf):>7}  {pre or '—':>5}  {post or '—':>5}")
    return merged


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--brand",     type=str)
    grp.add_argument("--all",       action="store_true")
    grp.add_argument("--treatment", action="store_true")
    grp.add_argument("--control",   action="store_true")
    parser.add_argument("--output", type=str, default="data/selenium")
    args = parser.parse_args()

    if args.brand:
        if args.brand not in BRANDS:
            print(f"❌ Unknown brand: '{args.brand}'")
            print(f"   Valid keys: {', '.join(BRANDS.keys())}")
            return
        keys = [args.brand]
    elif args.all:
        keys = list(BRANDS.keys())
    elif args.treatment:
        keys = TREATMENT_KEYS
    elif args.control:
        keys = CONTROL_KEYS
    else:
        keys = []

    print(f"\nBrands to scrape: {[BRANDS[k]['display_name'] for k in keys]}\n")

    os.makedirs(args.output, exist_ok=True)

    # ── Single login at the very start ────────────────────────────────────────
    driver = make_driver()
    driver.get("https://www.trustpilot.com")
    time.sleep(4)
    if not is_logged_in(driver):
        login(driver)
    else:
        print("✅ Session active — no login needed\n")

    # ── Scrape all brands — no re-login between them unless session expires ───
    dfs = []
    try:
        for i, key in enumerate(keys):
            df = scrape_brand(driver, key, output_dir=args.output)
            dfs.append(df)
            if i < len(keys) - 1:
                pause = random.uniform(8, 15)
                print(f"    ⏸  Pausing {pause:.0f}s before next brand...")
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
