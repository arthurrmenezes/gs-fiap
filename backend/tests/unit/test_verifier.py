from __future__ import annotations

from datetime import UTC, datetime

from specradar.extraction.verifier import verify_evidence, verify_extracted_value
from specradar.models import Document, ExtractedValue

_DOC_TEXT = "Potência: 397 cv a 5.650 rpm.\nTorque: 583 Nm a 3.500 rpm."


def _doc() -> Document:
    return Document(
        url="https://ford.com.br/x",
        domain="ford.com.br",
        source_tier=1,
        clean_text=_DOC_TEXT,
        content_hash="abc",
        fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_verify_evidence_substring_match() -> None:
    assert verify_evidence("Potência: 397 cv", _DOC_TEXT) is True


def test_verify_evidence_whitespace_insensitive() -> None:
    assert verify_evidence("Potência:    397   cv", _DOC_TEXT) is True


def test_verify_evidence_absent_snippet() -> None:
    assert verify_evidence("Potência: 500 cv", _DOC_TEXT) is False


def test_verify_evidence_empty() -> None:
    assert verify_evidence(None, _DOC_TEXT) is False
    assert verify_evidence("", _DOC_TEXT) is False


def test_verified_value_kept() -> None:
    value = ExtractedValue(
        attribute_id="engine.power_cv",
        value_raw="397 cv",
        evidence_snippet="Potência: 397 cv",
        confidence=0.9,
        found=True,
    )
    out = verify_extracted_value(value, _doc())
    assert out.found is True
    assert out.evidence_verified is True
    assert out.value_raw == "397 cv"


def test_hallucinated_value_discarded() -> None:
    value = ExtractedValue(
        attribute_id="engine.torque_nm",
        value_raw="600 Nm",
        evidence_snippet="Torque combinado de 600 Nm",
        confidence=0.6,
        found=True,
    )
    out = verify_extracted_value(value, _doc())
    assert out.found is False
    assert out.evidence_verified is False
    assert out.value_raw is None
