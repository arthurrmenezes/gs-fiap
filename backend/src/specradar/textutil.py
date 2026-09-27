from __future__ import annotations

import re
import unicodedata


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def fold(text: str) -> str:
    folded = strip_accents(text).lower().strip()
    return re.sub(r"\s+", " ", folded)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
