from __future__ import annotations
import os
from pathlib import Path

APP_NAME = "Library Manager"
DATA_DIR = Path(os.environ.get("LIBMGR_DATA_DIR", Path(__file__).resolve().parent / "data"))
DB_PATH = DATA_DIR / "library.db"
EBOOKS_DIR = DATA_DIR / "ebooks"
BACKUP_DIR = DATA_DIR / "backups"

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

PAGINATION_PAGE_SIZE = 25
FINE_PER_DAY = 1.0  # currency units per day late
LOAN_DAYS_DEFAULT = 14

LIGHT_THEME = "light.qss"
DARK_THEME = "dark.qss"