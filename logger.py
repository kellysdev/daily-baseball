# logger.py
from datetime import datetime
from pathlib import Path
import json
from storage import DATA_DIR, write_text_file, read_text_file, append_json

LOG_FILE = DATA_DIR / "logs.json"

def append_log(entry: dict):
    # add timestamp if not present
    entry = dict(entry)
    entry.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
    append_json(LOG_FILE, entry)