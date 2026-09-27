from __future__ import annotations

from specradar.config import Settings
from specradar.errors import SpecRadarError
from specradar.logging import get_logger

log = get_logger("search")


class GoogleCSEClient:
    _ENDPOINT = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str, engine_id: str) -> None:
        self._api_key = api_key
        self._engine_id = engine_id

    def search(self, query: str, *, num: int = 10) -> list[str]:
        import httpx

        urls: list[str] = []
        for start in range(1, min(num, 30) + 1, 10):
            params: dict[str, str | int] = {
                "key": self._api_key,
                "cx": self._engine_id,
                "q": query,
                "num": 10,
                "start": start,
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.get(self._ENDPOINT, params=params)
                resp.raise_for_status()
                data = resp.json()
            urls.extend(item["link"] for item in data.get("items", []))
            if len(urls) >= num:
                break
        log.info("search", query=query, results=len(urls))
        return urls[:num]


def build_search_client(settings: Settings) -> GoogleCSEClient:
    if not (settings.search_api_key and settings.search_engine_id):
        raise SpecRadarError("SEARCH_API_KEY and SEARCH_ENGINE_ID are required for live search")
    return GoogleCSEClient(settings.search_api_key, settings.search_engine_id)
