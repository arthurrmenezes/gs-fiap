"""Parser tests: tire (DIMENSIONAL), engine + transmission (COMPOSITE)."""

from __future__ import annotations

import pytest

from specradar.errors import NormalizationError
from specradar.normalization.parsers import parse_engine, parse_tire, parse_transmission


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("285/70 R17", {"width": 285, "aspect_ratio": 70, "rim_diameter_in": 17}),
        ("285/70R17", {"width": 285, "aspect_ratio": 70, "rim_diameter_in": 17}),
        ("265/65 R 18 all-terrain", {"width": 265, "aspect_ratio": 65, "rim_diameter_in": 18}),
    ],
)
def test_parse_tire(raw: str, expected: dict[str, int]) -> None:
    assert parse_tire(raw) == expected


def test_parse_tire_invalid() -> None:
    with pytest.raises(NormalizationError):
        parse_tire("aro liga leve")


def test_parse_engine_full() -> None:
    assert parse_engine("V6 3.0L biturbo") == {
        "layout": "V",
        "cylinders": 6,
        "displacement_l": 3.0,
        "aspiration": "Biturbo",
    }


def test_parse_engine_pt_words() -> None:
    out = parse_engine("2.0 turbo, 4 cilindros")
    assert out["cylinders"] == 4
    assert out["displacement_l"] == 2.0
    assert out["aspiration"] == "Turbo"


def test_parse_engine_invalid() -> None:
    with pytest.raises(NormalizationError):
        parse_engine("motor potente")


def test_parse_transmission_full() -> None:
    assert parse_transmission("automática de 10 marchas com paddle shifters") == {
        "type": "Automática",
        "gears": 10,
        "paddle_shifters": True,
    }


def test_parse_transmission_manual_no_paddle() -> None:
    out = parse_transmission("manual de 6 marchas")
    assert out == {"type": "Manual", "gears": 6, "paddle_shifters": False}
