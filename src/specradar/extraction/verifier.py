"""Evidence verification — the anti-hallucination core (CLAUDE.md §8).

The LLM is required to cite a literal `evidence_snippet`. We confirm that snippet
is a substring of the cleaned document (whitespace-normalized comparison). If it
is not, the value is hallucinated: it is discarded and marked NA.

This verification is what makes the solution defensable in production. It is NOT
optional (CLAUDE.md §15).
"""

from __future__ import annotations

from specradar.logging import get_logger
from specradar.models import Document, ExtractedValue
from specradar.textutil import normalize_whitespace

log = get_logger("verifier")

# An evidence snippet must be at least this many chars to count as real evidence.
_MIN_SNIPPET_LEN = 3


def verify_evidence(snippet: str | None, document_text: str) -> bool:
    """Return True iff `snippet` is a literal substring of `document_text`.

    Comparison normalizes whitespace on both sides so formatting differences
    (line wraps, multiple spaces) do not cause false negatives, while still
    requiring the actual characters to be present.
    """
    if not snippet or len(snippet.strip()) < _MIN_SNIPPET_LEN:
        return False
    haystack = normalize_whitespace(document_text)
    needle = normalize_whitespace(snippet)
    return needle in haystack


def verify_extracted_value(value: ExtractedValue, document: Document) -> ExtractedValue:
    """Verify one extracted value against its document.

    Returns a copy with `evidence_verified` set. A found value whose evidence
    fails verification is downgraded to not-found (value cleared) and logged as a
    suspected hallucination.
    """
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
