# scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Optional

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; SimpleScraper/1.0; +https://example.com/bot)"
)

def fetch_html(url: str, timeout: int = 15, headers: Optional[dict] = None) -> str:
    headers = headers or {"User-Agent": DEFAULT_USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_text_from_html(html: str, selector: Optional[str] = None) -> str:
    """
    If selector is None, return the whole page text (soup.get_text()).
    If selector is provided, we attempt to return the first match's text.
    """
    soup = BeautifulSoup(html, "html.parser")
    if selector:
        elem = soup.select_one(selector)
        if elem:
            return elem.get_text(separator="\n", strip=True)
        # fallback to whole page text if selector didn't match
    return soup.get_text(separator="\n", strip=True)

def get_text_from_url(url: str, selector: Optional[str] = None) -> str:
    html = fetch_html(url)
    return extract_text_from_html(html, selector)