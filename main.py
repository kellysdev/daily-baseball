# main.py
import os
from pathlib import Path
from datetime import datetime
import sys

from scraper import get_text_from_url
from compare import has_changed, make_unified_diff
from emailer import send_email
from storage import DATA_DIR, read_text_file, write_text_file
from logger import append_log

# Config: change these or set environment variables
URL = os.environ.get("TARGET_URL", "https://example.com")  # hardcoded default; override via env
SELECTOR = os.environ.get("TARGET_SELECTOR")  # optional CSS selector (e.g. "#main-content")
TO_EMAILS = [e.strip() for e in os.environ.get("EMAIL_TO", "").split(",") if e.strip()]
EMAIL_FROM = os.environ.get("EMAIL_FROM")
SUBJECT_TEMPLATE = os.environ.get("EMAIL_SUBJECT", "Daily Scrape Update for {url}")

YESTERDAY_PATH = DATA_DIR / "yesterday.txt"
TODAY_PATH = DATA_DIR / "today.txt"
LOGS_PATH = DATA_DIR / "logs.json"

def format_html_email(url: str, extracted_text: str, diff_text: str, changed: bool) -> str:
    title = f"Daily Scrape Update — {'Changed' if changed else 'No Change'}"
    # Basic inline style so email clients render acceptably
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{title}</title>
  </head>
  <body style="font-family: Arial, Helvetica, sans-serif; line-height:1.4; color:#111;">
    <h2>{title}</h2>
    <p><strong>URL:</strong> <a href="{url}">{url}</a></p>
    <h3>Extracted Content</h3>
    <div style="white-space:pre-wrap; border:1px solid #ddd; padding:10px; background:#f9f9f9;">
{escape_html(extracted_text)}
    </div>
    <h3>Change Summary</h3>
    <p>{'Changes detected — diff below' if changed else 'No changes detected since yesterday.'}</p>
    <pre style="white-space:pre-wrap; border:1px solid #eee; padding:10px; background:#fff; font-family: monospace; font-size:12px;">
{escape_html(diff_text or '')}
    </pre>
    <hr/>
    <footer style="font-size:12px; color:#666;">Generated at {datetime.utcnow().isoformat()}Z</footer>
  </body>
</html>
"""
    return html

def escape_html(s: str) -> str:
    import html
    return html.escape(s or "")

def main():
    if not TO_EMAILS:
        print("ERROR: No recipients configured. Set EMAIL_TO environment variable.", file=sys.stderr)
        sys.exit(1)
    print("Starting scraping job for URL:", URL)
    try:
        extracted = get_text_from_url(URL, SELECTOR)
    except Exception as e:
        append_log({
            "url": URL,
            "status": "scrape_error",
            "error": str(e),
        })
        raise

    # normalize whitespace (basic)
    new_text = "\n".join([line.rstrip() for line in extracted.splitlines()]).strip()
    old_text = read_text_file(YESTERDAY_PATH).strip()

    changed = has_changed(old_text, new_text)
    diff_text = make_unified_diff(old_text, new_text) if changed else ""

    subject = SUBJECT_TEMPLATE.format(url=URL, date=datetime.utcnow().date().isoformat())

    html_body = format_html_email(URL, new_text, diff_text, changed)

    email_status = "skipped"
    try:
        if changed:
            print("Change detected — sending email...")
            send_email(subject=subject, html_body=html_body, to_addrs=TO_EMAILS, from_addr=EMAIL_FROM)
            email_status = "sent"
        else:
            print("No change detected — no email will be sent.")
            email_status = "no_change"
    except Exception as e:
        append_log({
            "url": URL,
            "status": "email_error",
            "error": str(e),
        })
        raise

    # Save today's content as yesterday for next run
    write_text_file(YESTERDAY_PATH, new_text)
    write_text_file(TODAY_PATH, new_text)

    # Log the run
    append_log({
        "url": URL,
        "status": "ok",
        "changed": changed,
        "email_status": email_status,
        "length": len(new_text),
    })
    print("Done.")

if __name__ == "__main__":
    main()