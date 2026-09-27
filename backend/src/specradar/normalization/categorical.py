"""Synonym mapping for CATEGORICAL and ENUM_LIST attributes.

Resolution order for a token:
  1. taxonomy synonym map for the attribute (PT→canonical, etc.);
  2. direct (fold-insensitive) match against the attribute's value_set;
  3. unmappable → None (caller decides; never guess a value).
"""

from __future__ import annotations

import re

from specradar.taxonomy.loader import Taxonomy
from specradar.taxonomy.models import AttributeDef
from specradar.textutil import fold

# Split ENUM_LIST raw strings on common separators incl. PT-BR " e " conjunction.
_LIST_SPLIT_RE = re.compile(r"\s*(?:,|;|/|\band\b|\be\b)\s*", re.IGNORECASE)


def _value_set_index(attr: AttributeDef) -> dict[str, str]:
    """Map fold(value) → canonical value for an attribute's value_set."""
    return {fold(v): v for v in (attr.value_set or ())}


def normalize_categorical(attr: AttributeDef, raw: str, taxonomy: Taxonomy) -> str | None:
    """Map a single raw categorical token to its canonical value, or None."""
    token = raw.strip()
    if not token:
        return None

    mapped = taxonomy.resolve_value(attr.id, token)
    if mapped is not None:
        return mapped

    direct = _value_set_index(attr).get(fold(token))
    if direct is not None:
        return direct

    return None


def normalize_enum_list(attr: AttributeDef, raw: str, taxonomy: Taxonomy) -> list[str]:
    """Split a raw enum-list string and map each token to its canonical value.

    Unmappable tokens are dropped. Order is preserved and duplicates removed.
    """
    tokens = [t for t in _LIST_SPLIT_RE.split(raw) if t.strip()]
    out: list[str] = []
    for tok in tokens:
        canonical = normalize_categorical(attr, tok, taxonomy)
        if canonical is not None and canonical not in out:
            out.append(canonical)
    return out
