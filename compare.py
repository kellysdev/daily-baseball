# compare.py
import difflib
from typing import List

def make_unified_diff(old: str, new: str, fromfile: str = "yesterday", tofile: str = "today") -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=fromfile, tofile=tofile, lineterm="")
    return "".join(diff)

def has_changed(old: str, new: str) -> bool:
    # Simple comparison; you can normalize or ignore whitespace if desired.
    return (old or "").strip() != (new or "").strip()