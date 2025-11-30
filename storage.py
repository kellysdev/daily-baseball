# storage.py
from pathlib import Path
import json
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

def read_text_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def write_text_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")

def read_json(path: Path, default=None) -> Any:
    default = [] if default is None else default
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def append_json(path: Path, entry):
    arr = read_json(path, default=[])
    arr.append(entry)
    write_text_file(path, json.dumps(arr, indent=2))