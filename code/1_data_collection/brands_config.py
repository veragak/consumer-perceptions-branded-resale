"""
brands_config.py - brand list for the FIRST scraping wave (used by scraper_wave1.py)

One entry per brand: display name, Trustpilot address ("trustpilot_slug"),
segment, treatment/control group, resale launch date and programme name.
The scraper uses the launch date to label every review "pre" or "post".

This was the first study design (24 brands); the final sample has 48 brands,
the rest were added in wave 2 (brands_config_new.py). The design variables
in this file (integration_level, messaging_intensity, discount_depth,
service_offerings) are early estimates. The values used in the analysis are
in data/treatment_brands_moderators.csv.
"""

from datetime import date

BRANDS = {

    # ════════════════════════════════════════════════════════════════
    # TREATMENT BRANDS — Segment 1: French Contemporary Fashion
    # ════════════════════════════════════════════════════════════════

    "sandro": {
        "display_name": "Sandro",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "sandro-paris.com",
        "resale_launch": date(2021, 9, 1),      # September 2021  ⚠️ low volume
        "resale_program": "Sandro Seconde Main",
        "did_feasible": True,
        "did_note": "Low Trustpilot volume (~874 reviews total) — check pre/post counts",
        # Study 2 design variables
        "integration_level": 2,        # 1=fully separate site, 5=side-by-side
        "messaging_intensity": 3,       # 1=minimal, 5=prominent sustainability framing
        "discount_depth": 50,           # approximate % discount on used vs new
        "service_offerings": 1,         # count of: warranty + repair + buyback
    },
    "bash": {
        "display_name": "Ba&sh",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "ba-sh.com",
        "resale_launch": date(2022, 3, 1),       # March 2022  ✅
        "resale_program": "Ba&sh Second Hand",
        "did_feasible": True,
        "did_note": "Good volume (~3,360 reviews)",
        "integration_level": 3,
        "messaging_intensity": 3,
        "discount_depth": 50,
        "service_offerings": 1,
    },
    "maje": {
        "display_name": "Maje",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "maje.com",
        "resale_launch": date(2022, 10, 26),     # October 26 2022 — exact date ✅
        "resale_program": "Maje Seconde Main",
        "did_feasible": True,
        "did_note": "SMCP group sister brand to Sandro",
        "integration_level": 2,
        "messaging_intensity": 3,
        "discount_depth": 45,
        "service_offerings": 1,
    },
    "claudie_pierlot": {
        "display_name": "Claudie Pierlot",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "claudiepierlot.com",
        "resale_launch": date(2024, 2, 12),      # February 12 2024 — exact date ✅
        "resale_program": "Claudie Seconde Main",
        "did_feasible": True,
        "did_note": "SMCP group, exact launch date confirmed",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 45,
        "service_offerings": 1,
    },

    # ═════════════════════════════════════════════════════════════
    # French Contemporary Fashion — backups
    # ═════════════════════════════════════════════════════════════
    "eileenfisher": {
        "display_name": "Eileen Fisher",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "eileenfisher.com",
        "resale_launch": date(2020, 1, 1),        # approximate, adjust as needed
        "resale_program": "Renew",
        "did_feasible": False,
        "did_note": "Backup for Sandro/Maje if low review volume",
        "integration_level": 3,
        "messaging_intensity": 5,
        "discount_depth": 40,
        "service_offerings": 2,
    },
    "reformation": {
        "display_name": "Reformation",
        "segment": "french_fashion",
        "group": "treatment",
        "trustpilot_slug": "thereformation.com",
        "resale_launch": date(2021, 6, 1),
        "resale_program": "RefRecycling",
        "did_feasible": False,
        "did_note": "Backup brand, sustainability focused",
        "integration_level": 3,
        "messaging_intensity": 5,
        "discount_depth": 45,
        "service_offerings": 1,
    },


    # ════════════════════════════════════════════════════════════════
    # TREATMENT BRANDS — Segment 2: Outdoor / Athletic
    # ════════════════════════════════════════════════════════════════

    "patagonia": {
        "display_name": "Patagonia",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "trustpilot_slug": "www.patagonia.com",
        "resale_launch": date(2013, 1, 1),       # 2013 — too old for DiD 📊
        "resale_program": "Worn Wear",
        "did_feasible": False,
        "did_note": "Launch too old for DiD. Use for Study 2 cross-sectional only.",
        "integration_level": 5,                  # most integrated: side-by-side
        "messaging_intensity": 5,                # strongest sustainability messaging
        "discount_depth": 35,
        "service_offerings": 3,                  # repair + warranty + buyback
    },
    "arcteryx": {
        "display_name": "Arc'teryx",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "trustpilot_slug": "arcteryx.com",
        "resale_launch": date(2021, 5, 19),      # May 19 2021 — exact date ✅
        "resale_program": "ReGear / ReBIRD",
        "did_feasible": True,
        "did_note": "Official ReBIRD launch May 19 2021 confirmed via press release",
        "integration_level": 3,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 3,
    },
    "lululemon": {
        "display_name": "Lululemon",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "trustpilot_slug": "lululemon.com",
        "resale_launch": date(2022, 4, 22),      # April 22 2022 (Earth Day — nationwide) ✅
        "resale_program": "Like New",
        "did_feasible": True,
        "did_note": "Nationwide launch April 22 2022. Pilot was May 2021 (CA+TX only — use nationwide date).",
        "integration_level": 3,
        "messaging_intensity": 4,
        "discount_depth": 50,
        "service_offerings": 2,
    },

    # ═════════════════════════════════════════════════════════════
    # Outdoor / Athletic — backups
    # ═════════════════════════════════════════════════════════════
    "allbirds": {
        "display_name": "Allbirds",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "trustpilot_slug": "allbirds.com",
        "resale_launch": date(2021, 5, 1),
        "resale_program": "ReRun",
        "did_feasible": False,
        "did_note": "Backup brand, sustainable footwear",
        "integration_level": 3,
        "messaging_intensity": 5,
        "discount_depth": 40,
        "service_offerings": 1,
    },
    "columbia_reuse": {
        "display_name": "Columbia ReUse",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "trustpilot_slug": "columbia.com",
        "resale_launch": date(2022, 1, 1),
        "resale_program": "Columbia ReUse",
        "did_feasible": False,
        "did_note": "Backup for Study 2 only",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 35,
        "service_offerings": 1,
    },

    # ════════════════════════════════════════════════════════════════
    # TREATMENT BRANDS — Segment 3: Denim / Heritage
    # ════════════════════════════════════════════════════════════════

    "levis": {
        "display_name": "Levi's",
        "segment": "denim_heritage",
        "group": "treatment",
        "trustpilot_slug": "levis.com",
        "resale_launch": date(2020, 10, 6),      # October 6 2020 — exact date ✅
        "resale_program": "Levi's SecondHand",
        "did_feasible": True,
        "did_note": "Exact date confirmed. Large English-language review volume expected.",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 60,
        "service_offerings": 1,
    },
    "lacoste": {
        "display_name": "Lacoste",
        "segment": "denim_heritage",   # closest fit — sportswear heritage
        "group": "treatment",
        "trustpilot_slug": "lacoste.com",
        "resale_launch": date(2024, 12, 1),      # December 2024  📊 very recent
        "resale_program": "Lacoste Re-Use",
        "did_feasible": False,
        "did_note": "Very recent launch — post-window will only have ~3 months of reviews. Use Study 2 only or as sensitivity check.",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 1,
    },

    # ═════════════════════════════════════════════════════════════
    # Denim / Heritage — backups
    # ═════════════════════════════════════════════════════════════
    "madewell": {
        "display_name": "Madewell",
        "segment": "denim_heritage",
        "group": "treatment",
        "trustpilot_slug": "madewell.com",
        "resale_launch": date(2022, 3, 1),
        "resale_program": "Madewell Pre-Loved",
        "did_feasible": False,
        "did_note": "Backup for Levi's/Lacoste",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 1,
    },

    # ════════════════════════════════════════════════════════════════
    # TREATMENT BRANDS — Segment 4: Premium / Luxury Fashion
    # ════════════════════════════════════════════════════════════════

    "hugoboss": {
        "display_name": "Hugo Boss",
        "segment": "premium_fashion",
        "group": "treatment",
        "trustpilot_slug": "hugoboss.com",
        "resale_launch": date(2022, 9, 1),      # Q3 2022 — exact date unconfirmed, Sept used as approximation ⚠️
        "resale_program": "Hugo Boss Pre-Loved",
        "did_feasible": True,
        "did_note": "Q3 2022 launch confirmed, exact date unconfirmed — Sept 1 used as approximation. Launched in France first; UK/DE/US expansion in 2025. Check pre/post window volume.",
        # Study 2 design variables
        "integration_level": 4,        # accessible through hugoboss.com main store
        "messaging_intensity": 5,       # CLAIM 5 strategy — strong sustainability framing
        "discount_depth": 40,           # approximate % on pre-loved vs new
        "service_offerings": 2,         # resale + care & repair service
    },


     # ═════════════════════════════════════════════════════════════
    # Premium / Luxury Fashion — backups
    # ═════════════════════════════════════════════════════════════
    "burberry": {
        "display_name": "Burberry",
        "segment": "premium_fashion",
        "group": "treatment",
        "trustpilot_slug": "burberry.com",
        "resale_launch": date(2022, 7, 1),
        "resale_program": "Burberry Pre-Loved",
        "did_feasible": False,
        "did_note": "Backup for Hugo Boss",
        "integration_level": 4,
        "messaging_intensity": 5,
        "discount_depth": 50,
        "service_offerings": 2,
    },
    "gucci_resale": {
        "display_name": "Gucci Resale",
        "segment": "premium_fashion",
        "group": "treatment",
        "trustpilot_slug": "gucci.com",
        "resale_launch": date(2022, 8, 1),
        "resale_program": "Gucci Pre-Owned",
        "did_feasible": False,
        "did_note": "Backup for Study 2 only",
        "integration_level": 4,
        "messaging_intensity": 5,
        "discount_depth": 50,
        "service_offerings": 2,
    },

    # ════════════════════════════════════════════════════════════════
    # CONTROL BRANDS — Segment 4: Premium / Luxury Fashion
    # (Add a control brand here — e.g. Ralph Lauren or Calvin Klein)
    # ════════════════════════════════════════════════════════════════

    "tommyhilfiger": {
        "display_name": "Tommy Hilfiger",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "tommy.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No first-party resale program as of Feb 2026. Strong premium fashion match to Hugo Boss with large review volume.",
    },

    # ════════════════════════════════════════════════════════════════
    # CONTROL BRANDS — Segment 1: French Contemporary Fashion
    # (matched to Sandro, Ba&sh, Maje, Claudie Pierlot)
    # ════════════════════════════════════════════════════════════════

    "iro": {
        "display_name": "IRO Paris",
        "segment": "french_fashion",
        "group": "control",
        "trustpilot_slug": "iroparis.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program as of Feb 2026. Verify before use.",
    },
    "thekooples": {
        "display_name": "The Kooples",
        "segment": "french_fashion",
        "group": "control",
        "trustpilot_slug": "thekooples.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Good volume expected.",
    },
    "zadig": {
        "display_name": "Zadig & Voltaire",
        "segment": "french_fashion",
        "group": "control",
        "trustpilot_slug": "zadig-et-voltaire.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program.",
    },

    # ════════════════════════════════════════════════════════════════
    # CONTROL BRANDS — Segment 2: Outdoor / Athletic
    # (matched to Patagonia, Arc'teryx, Lululemon)
    # ════════════════════════════════════════════════════════════════

    "thenorthface": {
        "display_name": "The North Face",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "thenorthface.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No branded first-party resale program. Large review volume expected.",
    },
    "columbia": {
        "display_name": "Columbia Sportswear",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "columbia.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Similar outdoor positioning.",
    },

    # ════════════════════════════════════════════════════════════════
    # CONTROL BRANDS — Segment 3: Denim / Heritage
    # (matched to Levi's, Lacoste)
    # ════════════════════════════════════════════════════════════════

    "wrangler": {
        "display_name": "Wrangler",
        "segment": "denim_heritage",
        "group": "control",
        "trustpilot_slug": "wrangler.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Denim heritage brand matching Levi's segment.",
    },
}


# ────────────────────────────────────────────────────────────────────
# Helper functions used by all scrapers
# ────────────────────────────────────────────────────────────────────

def get_treatment_brands(did_only=False):
    """Return treatment brand keys, optionally only those feasible for DiD."""
    return [k for k, v in BRANDS.items()
            if v["group"] == "treatment"
            and (not did_only or v.get("did_feasible", False))]

def get_control_brands():
    return [k for k, v in BRANDS.items() if v["group"] == "control"]

def get_brands_by_segment(segment):
    return [k for k, v in BRANDS.items() if v.get("segment") == segment]

def print_brand_overview():
    """Print a formatted summary of the full brand design."""
    segments = ["french_fashion", "outdoor_athletic", "denim_heritage", "premium_fashion"]
    seg_labels = {
        "french_fashion":   "Segment 1 — French Contemporary Fashion",
        "outdoor_athletic": "Segment 2 — Outdoor / Athletic",
        "denim_heritage":   "Segment 3 — Denim / Heritage",
        "premium_fashion":  "Segment 4 — Premium / Luxury Fashion",
    }

    print("\n" + "═"*70)
    print("FULL BRAND DESIGN  (10 treatment + 6 control = 16 brands)")
    print("═"*70)

    for seg in segments:
        print(f"\n  {seg_labels[seg]}")
        print(f"  {'─'*65}")

        treatment = [(k, v) for k, v in BRANDS.items()
                     if v["group"] == "treatment" and v.get("segment") == seg]
        control   = [(k, v) for k, v in BRANDS.items()
                     if v["group"] == "control"   and v.get("segment") == seg]

        print(f"  TREATMENT:")
        for k, v in treatment:
            launch = v["resale_launch"].strftime("%b %d %Y") if v["resale_launch"] else "—"
            did = "✅ DiD" if v.get("did_feasible") else "📊 Study 2 only"
            print(f"    {v['display_name']:<22} launch: {launch:<15} {did}")
            if v.get("did_note"):
                print(f"    {'':22}         {v['did_note']}")

        print(f"  CONTROL:")
        for k, v in control:
            print(f"    {v['display_name']:<22} (no resale)")

    print(f"\n  DiD-feasible treatment brands: {len(get_treatment_brands(did_only=True))}")
    print(f"  Study 2 treatment brands:      {len(get_treatment_brands(did_only=False))}")
    print(f"  Control brands:                {len(get_control_brands())}")
    print()


if __name__ == "__main__":
    print_brand_overview()
