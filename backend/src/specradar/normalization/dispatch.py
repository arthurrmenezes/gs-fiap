from __future__ import annotations

from typing import Any

from specradar.logging import get_logger
from specradar.models import Document, ExtractedValue, NormalizedValue
from specradar.normalization.categorical import normalize_categorical, normalize_enum_list
from specradar.normalization.parsers import PARSERS
from specradar.normalization.units import normalize_scalar
from specradar.taxonomy.loader import Taxonomy
from specradar.taxonomy.models import AttributeDef, DataType

log = get_logger("normalization")

_TRUE_TOKENS = {"sim", "x", "true", "1", "possui", "presente", "yes", "equipado", "disponivel"}
_FALSE_TOKENS = {"nao", "n", "false", "0", "ausente", "no", "indisponivel"}


def _normalize_boolean(raw: str) -> bool | None:
    from specradar.textutil import fold

    token = fold(raw)
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    return None


def normalize_value(
    extracted: ExtractedValue,
    attr: AttributeDef,
    doc: Document,
    taxonomy: Taxonomy,
) -> NormalizedValue | None:
    raw = extracted.value_raw
    if raw is None:
        return None

    value_norm: Any = None
    unit: str | None = None

    try:
        match attr.data_type:
            case DataType.SCALAR_UNIT:
                assert attr.canonical_unit is not None
                value_norm, unit = normalize_scalar(raw, attr.canonical_unit)
            case DataType.CATEGORICAL:
                value_norm = normalize_categorical(attr, raw, taxonomy)
            case DataType.ENUM_LIST:
                value_norm = normalize_enum_list(attr, raw, taxonomy)
            case DataType.COMPOSITE | DataType.DIMENSIONAL:
                assert attr.parser is not None
                parser = PARSERS[attr.parser]
                value_norm = parser(raw)
            case DataType.BOOLEAN:
                value_norm = _normalize_boolean(raw)
            case DataType.TEXT:
                value_norm = raw.strip()
    except Exception as exc:
        log.warning(
            "normalization_failed",
            attribute_id=attr.id,
            value_raw=raw,
            error=str(exc),
            source_url=doc.url,
        )
        return None

    if value_norm is None or (isinstance(value_norm, list) and not value_norm):
        log.info("unmappable_value", attribute_id=attr.id, value_raw=raw, source_url=doc.url)
        return None

    return NormalizedValue(
        attribute_id=attr.id,
        value_raw=raw,
        value_norm=value_norm,
        unit=unit,
        confidence=extracted.confidence,
        evidence_snippet=extracted.evidence_snippet,
        evidence_verified=extracted.evidence_verified,
        source_url=doc.url,
        source_tier=doc.source_tier,
        extracted_at=doc.fetched_at,
    )
