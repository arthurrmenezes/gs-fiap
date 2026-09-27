"""Fetch source documents over HTTP (httpx).

Raw bytes are hashed (`content_hash`) so identical documents can be recognized
and are not re-extracted.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from specradar.logging import get_logger

log = get_logger("fetcher")


def content_hash(content: bytes | str) -> str:
    """Stable sha256 hex of document bytes, used as a cache key."""
    data = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class FetchResult:
    url: str
    content: str
    content_type: str
    content_hash: str


class Fetcher:
    """Fetches a URL with a plain HTTP GET (static pages only)."""

    def fetch(self, url: str) -> FetchResult:
        import httpx  # lazy import — not needed for offline tests

        headers = {"User-Agent": "SpecRadarBot/1.0 (+respecting robots.txt)"}
        with httpx.Client(follow_redirects=True, timeout=20.0, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
        ctype = resp.headers.get("content-type", "text/html")
        log.info("fetched", url=url, status=resp.status_code, bytes=len(resp.content))
        return FetchResult(url, resp.text, ctype, content_hash(resp.text))
