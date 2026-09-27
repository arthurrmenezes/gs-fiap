from __future__ import annotations

from typing import Any, Protocol

from specradar.errors import ExtractionError
from specradar.extraction.prompts import (
    SYSTEM_PROMPT,
    build_tool_schema,
    build_user_prompt,
    tool_name,
)
from specradar.extraction.verifier import verify_extracted_value
from specradar.logging import get_logger
from specradar.models import Document, ExtractedValue
from specradar.taxonomy.models import AttributeDef

log = get_logger("extractor")


class LLMClient(Protocol):
    def extract(
        self,
        *,
        system: str,
        user: str,
        tool: dict[str, Any],
        tool_name: str,
    ) -> list[dict[str, Any]]: ...


def _to_extracted(raw: dict[str, Any]) -> ExtractedValue:
    try:
        return ExtractedValue.model_validate(raw)
    except Exception as exc:
        raise ExtractionError(f"LLM returned a schema-invalid value: {raw!r}: {exc}") from exc


def extract_attributes(
    client: LLMClient,
    attributes: list[AttributeDef],
    document: Document,
) -> list[ExtractedValue]:
    if not attributes:
        return []

    tool = build_tool_schema(attributes)
    user = build_user_prompt(attributes, document.clean_text)
    raw_values = client.extract(system=SYSTEM_PROMPT, user=user, tool=tool, tool_name=tool_name())

    requested = {a.id for a in attributes}
    verified: list[ExtractedValue] = []
    for raw in raw_values:
        value = _to_extracted(raw)
        if value.attribute_id not in requested:
            log.warning("unrequested_attribute", attribute_id=value.attribute_id, url=document.url)
            continue
        verified.append(verify_extracted_value(value, document))

    log.info(
        "extracted",
        source_url=document.url,
        requested=len(attributes),
        returned=len(verified),
        found=sum(1 for v in verified if v.found),
    )
    return verified


class Extractor:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def extract(self, attributes: list[AttributeDef], document: Document) -> list[ExtractedValue]:
        return extract_attributes(self._client, attributes, document)


class AnthropicLLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ExtractionError("ANTHROPIC_API_KEY is required for the live LLM client")
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def extract(
        self,
        *,
        system: str,
        user: str,
        tool: dict[str, Any],
        tool_name: str,
    ) -> list[dict[str, Any]]:
        response: Any = self._client.messages.create(  # type: ignore[call-overload]
            model=self._model,
            max_tokens=4096,
            system=system,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": user}],
        )
        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                values = block.input.get("values", [])
                if not isinstance(values, list):
                    raise ExtractionError("tool output 'values' is not a list")
                return values
        raise ExtractionError("LLM did not return the forced tool call")
