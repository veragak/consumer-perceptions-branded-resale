"""
brands_config_new.py - brand list for the SECOND scraping wave (used by scraper_wave2.py)

Brands not collected in wave 1, mostly control brands plus treatment brands
found on the Trove and Faume partner lists. Same fields as brands_config.py.

Before scraping, check each "trustpilot_slug" by opening
trustpilot.com/review/<slug>. The design variables here are early estimates;
the analysis uses data/treatment_brands_moderators.csv.
"""

from datetime import date

BRANDS = {

    # ════════════════════════════════════════════════════════════════════════
    # TREATMENT — FAUME CLIENTS
    # ════════════════════════════════════════════════════════════════════════

    "aigle": {
        "display_name": "Aigle",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "resale_platform": "Faume",
        "trustpilot_slug": "www.aigle.com",          # VERIFY SLUG
        "resale_launch": date(2020, 10, 1),
        "resale_program": "Aigle Second Souffle",
        "did_feasible": True,
        "did_note": "Separate 'Second Souffle' microsite linked from main site. In-store repairs.",
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
        "trustpilot_slug": "www.soeur.fr",           # VERIFY SLUG — small brand, may have low volume
        "resale_launch": date(2025, 2, 1),
        "resale_program": "Soeur Seconde Main",
        "did_feasible": False,
        "did_note": "Very recent (Feb 2025). Study 2 only. In-store buyback at 28 locations + online.",
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
        "trustpilot_slug": "balzac-paris.fr",   # VERIFY SLUG
        "resale_launch": date(2021, 11, 1),
        "resale_program": "Balzac Paris Seconde Main",
        "did_feasible": True,
        "did_note": "Faume-powered separate microsite. Minimal sustainability messaging.",
        "integration_level": 2,
        "messaging_intensity": 2,
        "discount_depth": 45,
        "service_offerings": 1,
    },

    # ════════════════════════════════════════════════════════════════════════
    # TREATMENT — TROVE CLIENTS
    # ════════════════════════════════════════════════════════════════════════

    "canada_goose": {
        "display_name": "Canada Goose",
        "segment": "premium_fashion",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "www.canadagoose.com",
        "resale_launch": date(2023, 1, 1),
        "resale_program": "Canada Goose Generations",
        "did_feasible": True,
        "did_note": "Separate site generations.canadagoose.com. 1-year warranty on Generations items.",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 25,
        "service_offerings": 3,
    },
    "carhartt": {
        "display_name": "Carhartt",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "www.carhartt.com",       # VERIFY SLUG
        "resale_launch": date(2023, 3, 1),
        "resale_program": "Carhartt Reworked",
        "did_feasible": True,
        "did_note": "Separate site reworked.carhartt.com. Repair + recycling program.",
        "integration_level": 2,
        "messaging_intensity": 4,
        "discount_depth": 40,
        "service_offerings": 3,
    },
    "michael_kors": {
        "display_name": "Michael Kors",
        "segment": "premium_fashion",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "michaelkors.com",
        "resale_launch": date(2022, 8, 1),
        "resale_program": "Michael Kors Pre-Loved",
        "did_feasible": True,
        "did_note": "Separate site preloved.michaelkors.com. Peer-to-peer only.",
        "integration_level": 2,
        "messaging_intensity": 3,
        "discount_depth": 35,
        "service_offerings": 1,
    },
    "steve_madden": {
        "display_name": "Steve Madden",
        "segment": "contemporary_fashion",
        "group": "treatment",
        "resale_platform": "Trove",
        "trustpilot_slug": "stevemadden.eu",
        "resale_launch": date(2022, 1, 1),
        "resale_program": "Steve Madden Re-Booted",
        "did_feasible": True,
        "did_note": "Re-Booted integrated into stevemadden.com. SHOECYCLE take-back + recycling.",
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
        "did_note": "Separate platform via Trove/reverse.supply. Sustainability is entire brand identity.",
        "integration_level": 2,
        "messaging_intensity": 5,
        "discount_depth": 45,
        "service_offerings": 2,
    },

    # ════════════════════════════════════════════════════════════════════════
    # TREATMENT — ARCHIVE CLIENTS
    # ════════════════════════════════════════════════════════════════════════

    "thenorthface": {
        "display_name": "The North Face",
        "segment": "outdoor_athletic",
        "group": "treatment",
        "resale_platform": "Archive",
        "trustpilot_slug": "www.thenorthface.com",
        "resale_launch": date(2018, 6, 1),
        "resale_program": "The North Face Renewed",
        "did_feasible": False,
        "did_note": "2018 launch — pre-window Trustpilot coverage likely thin. Study 2 only.",
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
        "trustpilot_slug": "www.studioanneloes.nl",  # VERIFY SLUG — small Dutch brand
        "resale_launch": date(2024, 2, 1),
        "resale_program": "Studio Anneloes Retravel",
        "did_feasible": False,
        "did_note": "Small Dutch brand. Trustpilot volume likely very low. Study 2 only.",
        "integration_level": 2,
        "messaging_intensity": 3,
        "discount_depth": 40,
        "service_offerings": 1,
    },

    # ════════════════════════════════════════════════════════════════════════
    # CONTROL — Outdoor / Athletic
    # matched to: Patagonia, Arc'teryx, Lululemon, Allbirds, Carhartt, Aigle, The North Face
    # ════════════════════════════════════════════════════════════════════════

    "rab": {
        "display_name": "Rab",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "rab.equipment",      # VERIFY SLUG — unusual TLD
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Patagonia.",
    },
    "montane": {
        "display_name": "Montane",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "montane.com",        # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Patagonia.",
    },
    "jottnar": {
        "display_name": "Jöttnar",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "jottnar.com",        # VERIFY SLUG — very niche, may have no Trustpilot page
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Arc'teryx. Very niche — verify review volume.",
    },
    "vuori": {
        "display_name": "Vuori",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "vuoriclothing.com",  # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Lululemon.",
    },
    "underarmour": {
        "display_name": "Under Armour",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "www.underarmour.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Lululemon.",
    },
    "hoka": {
        "display_name": "Hoka",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "www.hoka.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Allbirds.",
    },
    "dickies": {
        "display_name": "Dickies",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "dickies.com",        # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Carhartt.",
    },
    "lechameau": {
        "display_name": "Le Chameau",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "lechameau.com",      # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Aigle.",
    },
    "osprey": {
        "display_name": "Osprey",
        "segment": "outdoor_athletic",
        "group": "control",
        "trustpilot_slug": "www.ospreypacks.com",    # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to The North Face.",
    },

    # ════════════════════════════════════════════════════════════════════════
    # CONTROL — Premium / Luxury
    # matched to: Hugo Boss, Lacoste, Canada Goose, Michael Kors
    # ════════════════════════════════════════════════════════════════════════

    "armani": {
        "display_name": "Armani",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "www.armani.com",         # VERIFY SLUG — may be giorgio-armani.com
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Hugo Boss.",
    },
    "fredperry": {
        "display_name": "Fred Perry",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "www.fredperry.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Lacoste.",
    },
    "moncler": {
        "display_name": "Moncler",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "moncler.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Canada Goose.",
    },
    "moose_knuckles": {
        "display_name": "Moose Knuckles",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "www.mooseknucklescanada.com",  # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Canada Goose.",
    },
    "furla": {
        "display_name": "Furla",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "furla.com",          # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Michael Kors.",
    },
    "toryburch": {
        "display_name": "Tory Burch",
        "segment": "premium_fashion",
        "group": "control",
        "trustpilot_slug": "www.toryburch.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Michael Kors.",
    },

    # ════════════════════════════════════════════════════════════════════════
    # CONTROL — Contemporary Fashion
    # matched to: Ba&sh / Sandro / Maje, Levi's, Steve Madden
    # ════════════════════════════════════════════════════════════════════════

    "sezane": {
        "display_name": "Sézane",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "www.sezane.com",         # VERIFY SLUG
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Ba&sh / Sandro / Maje.",
    },
    "thekooples": {
        "display_name": "The Kooples",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "thekooples.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Ba&sh / Sandro / Maje.",
    },
    "wrangler": {
        "display_name": "Wrangler",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "eu.wrangler.com",
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Levi's.",
    },
    "guess": {
        "display_name": "Guess",
        "segment": "contemporary_fashion",
        "group": "control",
        "trustpilot_slug": "www.guess.com",          # VERIFY SLUG — may be guess.eu
        "resale_launch": None,
        "resale_program": None,
        "did_feasible": True,
        "did_note": "No resale program. Matched to Steve Madden.",
    },
}


# ────────────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────────────

def get_treatment_brands(did_only=False):
    return [k for k, v in BRANDS.items()
            if v["group"] == "treatment"
            and (not did_only or v.get("did_feasible", False))]

def get_control_brands():
    return [k for k, v in BRANDS.items() if v["group"] == "control"]

def get_brands_by_platform(platform):
    return [k for k, v in BRANDS.items()
            if v["group"] == "treatment" and v.get("resale_platform") == platform]

def print_brand_overview():
    total_t   = len(get_treatment_brands())
    total_c   = len(get_control_brands())
    total_did = len(get_treatment_brands(did_only=True))

    print("\n" + "═"*65)
    print(f"NEW BRANDS TO SCRAPE  —  {total_t} treatment · {total_c} control · {total_did} DiD-feasible")
    print("═"*65)

    print("\n  TREATMENT (by platform)")
    for plat in ["Faume", "Trove", "Archive"]:
        brands = [(k, v) for k, v in BRANDS.items()
                  if v["group"] == "treatment" and v.get("resale_platform") == plat]
        if not brands:
            continue
        print(f"\n  ── {plat} {'─'*(55-len(plat))}")
        for k, v in brands:
            launch = v["resale_launch"].strftime("%b %Y") if v["resale_launch"] else "—"
            did    = "✅ DiD" if v.get("did_feasible") else "📊 Study 2"
            print(f"    {v['display_name']:<22} {launch:<10} {did}  [{v.get('segment','')}]")

    print("\n\n  CONTROL (by segment)")
    segs = [
        ("outdoor_athletic",     "Outdoor / Athletic"),
        ("premium_fashion",      "Premium / Luxury"),
        ("contemporary_fashion", "Contemporary Fashion"),
    ]
    for seg_key, seg_label in segs:
        brands = [(k, v) for k, v in BRANDS.items()
                  if v["group"] == "control" and v.get("segment") == seg_key]
        if not brands:
            continue
        print(f"\n  ── {seg_label} {'─'*(55-len(seg_label))}")
        for k, v in brands:
            verify = "  ⚠ VERIFY" if "VERIFY" in v.get("did_note","") else ""
            print(f"    {v['display_name']:<22} {v['trustpilot_slug']}{verify}")

    print(f"\n  Slugs marked ⚠ VERIFY — check trustpilot.com/review/<slug> first")
    print()


if __name__ == "__main__":
    print_brand_overview()
