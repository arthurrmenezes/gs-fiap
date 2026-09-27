from __future__ import annotations

from specradar.logging import get_logger
from specradar.models import Document, ExtractedValue
from specradar.textutil import normalize_whitespace

log = get_logger("verifier")

_MIN_SNIPPET_LEN = 3


def verify_evidence(snippet: str | None, document_text: str) -> bool:
    if not snippet or len(snippet.strip()) < _MIN_SNIPPET_LEN:
        return False
    haystack = normalize_whitespace(document_text)
    needle = normalize_whitespace(snippet)
    return needle in haystack


def verify_extracted_value(value: ExtractedValue, document: Document) -> ExtractedValue:
    if not value.found:
        return value.model_copy(update={"evidence_verified": False})

    verified = verify_evidence(value.evidence_snippet, document.clean_text)
    if verified:
        return value.model_copy(update={"evidence_verified": True})

    log.warning(
        "suspected_hallucination",
        attribute_id=value.attribute_id,
        value_raw=value.value_raw,
        evidence_snippet=value.evidence_snippet,
        source_url=document.url,
        confidence=value.confidence,
    )
    return value.model_copy(
        update={
            "found": False,
            "value_raw": None,
            "evidence_verified": False,
        }
    )
