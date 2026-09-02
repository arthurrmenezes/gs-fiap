"""Fetch source documents. httpx for static pages, Playwright only as JS fallback.

Playwright is expensive/fragile → try httpx first (CLAUDE.md §15). Raw bytes are
hashed (`content_hash`) so the raw layer can cache and avoid re-extraction.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from specradar.config import Settings, get_settings
from specradar.logging import get_logger

log = get_logger("fetcher")

# Heuristic: pages this short after a static fetch likely need JS rendering.
_JS_FALLBACK_MIN_CHARS = 500


def content_hash(content: bytes | str) -> str:
    """Stable sha256 hex of document bytes, for the raw cache key."""
    data = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class FetchResult:
    url: str
    content: str
    content_type: str
    content_hash: str
    rendered_with_js: bool


class Fetcher:
    """Fetches a URL, falling back to Playwright when a page looks JS-rendered."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def fetch(self, url: str) -> FetchResult:
        content, ctype = self._fetch_static(url)
        if len(content) < _JS_FALLBACK_MIN_CHARS and self._settings.allow_playwright:
            log.info("js_fallback", url=url, static_len=len(content))
            content, ctype = self._fetch_rendered(url)
            return FetchResult(url, content, ctype, content_hash(content), True)
        return FetchResult(url, content, ctype, content_hash(content), False)

    def _fetch_static(self, url: str) -> tuple[str, str]:
        import httpx  # lazy import — not needed for offline tests

        headers = {"User-Agent": "SpecRadarBot/0.1 (+respecting robots.txt)"}
        with httpx.Client(follow_redirects=True, timeout=20.0, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "text/html")
            log.info("fetched_static", url=url, status=resp.status_code, bytes=len(resp.content))
            return resp.text, ctype

    def _fetch_rendered(self, url: str) -> tuple[str, str]:
        from playwright.sync_api import sync_playwright  # lazy import

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                html = page.content()
            finally:
                browser.close()
        return html, "text/html"
