from __future__ import annotations

import hashlib
from dataclasses import dataclass

from specradar.logging import get_logger

log = get_logger("fetcher")


def content_hash(content: bytes | str) -> str:
    data = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class FetchResult:
    url: str
    content: str
    content_type: str
    content_hash: str


class Fetcher:
    def fetch(self, url: str) -> FetchResult:
        import httpx

        headers = {"User-Agent": "SpecRadarBot/1.0 (+respecting robots.txt)"}
        with httpx.Client(follow_redirects=True, timeout=20.0, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
        ctype = resp.headers.get("content-type", "text/html")
        log.info("fetched", url=url, status=resp.status_code, bytes=len(resp.content))
        return FetchResult(url, resp.text, ctype, content_hash(resp.text))
