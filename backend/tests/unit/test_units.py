from __future__ import annotations

import math

import pytest

from specradar.errors import NormalizationError
from specradar.normalization.units import normalize_scalar, parse_number, to_canonical


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("397", 397.0),
        ("3.0", 3.0),
        ("5,8", 5.8),
        ("2.283", 2283.0),
        ("180.000", 180000.0),
        ("1.234,56", 1234.56),
        ("1,234.56", 1234.56),
        ("-12,5", -12.5),
    ],
)
def test_parse_number(raw: str, expected: float) -> None:
    assert parse_number(raw) == pytest.approx(expected)


def test_parse_number_no_number() -> None:
    with pytest.raises(NormalizationError):
        parse_number("abc")


def test_power_hp_to_cv_and_back() -> None:
    cv = to_canonical(100.0, "hp", "cv")
    assert cv == pytest.approx(101.387, abs=1e-3)
    hp_back = cv / 1.01387
    assert hp_back == pytest.approx(100.0, abs=1e-3)


def test_power_kw_to_cv() -> None:
    assert to_canonical(100.0, "kW", "cv") == pytest.approx(135.962, abs=1e-3)


def test_torque_kgfm_and_lbft_to_nm() -> None:
    assert to_canonical(10.0, "kgfm", "Nm") == pytest.approx(98.0665, abs=1e-3)
    assert to_canonical(100.0, "lbft", "Nm") == pytest.approx(135.582, abs=1e-3)


def test_displacement_cc_to_litres() -> None:
    assert to_canonical(2998.0, "cc", "L") == pytest.approx(2.998, abs=1e-6)


def test_consumption_l_per_100km_reciprocal() -> None:
    assert to_canonical(8.0, "L/100km", "km/L") == pytest.approx(12.5)


def test_missing_unit_assumed_canonical() -> None:
    assert to_canonical(10.0, None, "gears") == 10.0


def test_unknown_unit_raises() -> None:
    with pytest.raises(NormalizationError):
        to_canonical(1.0, "furlongs", "cv")


def test_normalize_scalar_extracts_unit() -> None:
    value, unit = normalize_scalar("397 cv", "cv")
    assert (value, unit) == (397.0, "cv")
    value, unit = normalize_scalar('17"', "in")
    assert math.isclose(value, 17.0)
