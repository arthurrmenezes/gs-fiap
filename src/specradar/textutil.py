"""Small, pure text helpers shared across stages."""

from __future__ import annotations

import re
import unicodedata


def strip_accents(text: str) -> str:
    """Remove diacritics: 'Potência' → 'Potencia'."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def fold(text: str) -> str:
    """Case- and accent-insensitive fold for synonym lookup.

    Collapses internal whitespace and trims. Used as the canonical lookup key.
    """
    folded = strip_accents(text).lower().strip()
    return re.sub(r"\s+", " ", folded)


def normalize_whitespace(text: str) -> str:
    """Collapse all runs of whitespace to single spaces and strip.

    This is the canonical form used by the evidence verifier so that snippet
    matching is robust to formatting differences between LLM output and the
    cleaned document.
    """
    return re.sub(r"\s+", " ", text).strip()
