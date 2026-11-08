"""
shared/common.py - shared paths and settings for the Python scripts in code/.

Run every script from the repository root, e.g.
    python code/5_study1_did/7_figures_synthdid.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # code/shared/common.py -> repository root
DATA = ROOT / "data"
PRIVATE = ROOT / "private"          # not published: raw review text (see data/README.md)
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

DID_EXCLUDE = ["Arc'teryx", "Patagonia"]

BLUE, ORANGE, GREEN, RED = "#2563EB", "#D97706", "#16A34A", "#DC2626"
