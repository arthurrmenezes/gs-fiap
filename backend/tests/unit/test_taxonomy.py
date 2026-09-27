from __future__ import annotations

import pytest

from specradar.errors import UnknownAttributeError
from specradar.taxonomy.loader import Taxonomy
from specradar.taxonomy.models import DataType


def test_loads_and_has_min_attributes(taxonomy: Taxonomy) -> None:
    assert len(taxonomy.all_attributes()) >= 35


def test_all_five_hard_types_present(taxonomy: Taxonomy) -> None:
    present = {a.data_type for a in taxonomy.all_attributes()}
    for required in (
        DataType.SCALAR_UNIT,
        DataType.CATEGORICAL,
        DataType.COMPOSITE,
        DataType.DIMENSIONAL,
        DataType.ENUM_LIST,
    ):
        assert required in present


def test_resolve_canonical_id_passthrough(taxonomy: Taxonomy) -> None:
    assert taxonomy.resolve_attribute("engine.power_cv") == "engine.power_cv"


def test_resolve_synonym(taxonomy: Taxonomy) -> None:
    assert taxonomy.resolve_attribute("cavalos") == "engine.power_cv"
    assert taxonomy.resolve_attribute("Câmbio") == "transmission"


def test_resolve_display_name(taxonomy: Taxonomy) -> None:
    assert taxonomy.resolve_attribute("configuração do MOTOR") == "engine.configuration"


def test_resolve_unknown_raises(taxonomy: Taxonomy) -> None:
    with pytest.raises(UnknownAttributeError):
        taxonomy.resolve_attribute("cor do banco do motorista")


def test_source_allowlist_and_tiers(taxonomy: Taxonomy) -> None:
    src = taxonomy.source_for_domain("www.ford.com.br")
    assert src is not None and src.authority_tier == 1
    assert taxonomy.is_allowed("vendas.ford.com.br") is True
    assert taxonomy.is_allowed("randomblog.example") is False
