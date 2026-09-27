from __future__ import annotations

import re

from specradar.taxonomy.loader import Taxonomy
from specradar.taxonomy.models import AttributeDef
from specradar.textutil import fold

_LIST_SPLIT_RE = re.compile(r"\s*(?:,|;|/|\band\b|\be\b)\s*", re.IGNORECASE)


def _value_set_index(attr: AttributeDef) -> dict[str, str]:
    return {fold(v): v for v in (attr.value_set or ())}


def normalize_categorical(attr: AttributeDef, raw: str, taxonomy: Taxonomy) -> str | None:
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
    tokens = [t for t in _LIST_SPLIT_RE.split(raw) if t.strip()]
    out: list[str] = []
    for tok in tokens:
        canonical = normalize_categorical(attr, tok, taxonomy)
        if canonical is not None and canonical not in out:
            out.append(canonical)
    return out
