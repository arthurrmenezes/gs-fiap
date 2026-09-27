from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from specradar.errors import ExtractionError
from specradar.models import Document
from specradar.sources.fetcher import content_hash


class FixtureLLMClient:
    def __init__(self, responses: list[list[dict[str, Any]]]) -> None:
        self._responses = responses
        self._index = 0

    def extract(
        self,
        *,
        system: str,
        user: str,
        tool: dict[str, Any],
        tool_name: str,
    ) -> list[dict[str, Any]]:
        if self._index >= len(self._responses):
            raise ExtractionError("FixtureLLMClient exhausted — more calls than responses")
        values = self._responses[self._index]
        self._index += 1
        return values


def load_fixture(
    fixture_dir: str | Path,
    *,
    now: datetime | None = None,
) -> tuple[list[Document], list[list[dict[str, Any]]]]:
    now = now or datetime(2026, 1, 1, tzinfo=UTC)
    base = Path(fixture_dir)
    manifest_path = base / "extraction.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"fixture manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents: list[Document] = []
    responses: list[list[dict[str, Any]]] = []

    for entry in manifest["documents"]:
        text_file = base / "documents" / entry["text_file"]
        clean = text_file.read_text(encoding="utf-8")
        documents.append(
            Document(
                url=entry["url"],
                domain=entry["domain"],
                source_tier=int(entry["source_tier"]),
                clean_text=clean,
                content_hash=content_hash(clean),
                fetched_at=now,
            )
        )
        responses.append(entry.get("values", []))

    return documents, responses
