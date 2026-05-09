import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _bundle = Path(sys._MEIPASS)
else:
    _bundle = Path(__file__).resolve().parent

BUNDLE_DIR = _bundle
DATA_DIR = Path.cwd()

TEMPLATES_DIR = BUNDLE_DIR / "backend" / "templates"
IBGE_PATH = BUNDLE_DIR / "backend" / "ibge_municipios.csv"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "output"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
