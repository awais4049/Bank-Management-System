# Library Manager (PySide6)

Quick start:

1. Ensure Python 3.11+ with pip is available.
2. Install dependencies:
   - If venv available: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   - If not, use: `python3 -m pip install --break-system-packages -r requirements.txt`
3. Run the app:
   `python3 main.py`

Default login:
- Username: `admin`
- Password: `admin`

Build executable (Linux example):
- `python3 -m PyInstaller --noconfirm --name LibraryManager --windowed --onefile main.py`
- The binary will be in `dist/LibraryManager`.

Structure:
- `library/models.py` ORM models
- `library/db.py` engine and session factory
- `library/services/*` business logic
- `library/ui/*` PySide6 UI (pages, main window)
- `library/data/` sqlite database and assets