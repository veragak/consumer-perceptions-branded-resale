"""
_common.py - shared paths and settings for the Python scripts in code/.

Run every script from the repository root, e.g.
    python code/25_figures_synthdid.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRIVATE = ROOT / "private"          # not published: raw review text (see data/README.md)
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

DID_EXCLUDE = ["Arc'teryx", "Patagonia"]

BLUE, ORANGE, GREEN, RED = "#2563EB", "#D97706", "#16A34A", "#DC2626"
