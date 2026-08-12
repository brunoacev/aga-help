"""Testes do serviço de catálogo."""

from core.components_data import (
    CAT_HORIZONTAL_15_25,
    CAT_HORIZONTAL_50,
    CAT_ROLO,
    CAT_TRILHOS,
    CAT_VERTICAL,
    FILTER_CATEGORY_ALL,
)
from core.services.catalog_service import categorize_materials, filter_components, is_meter_item


def test_is_meter_item_by_keyword():
    assert is_meter_item({"name": "Trilho 50mm Super Mono", "code": "10015"})
    assert not is_meter_item({"name": "Freio", "code": "1257"})


def test_is_meter_item_by_unit_type():
    assert is_meter_item({"name": "Item", "unit_type": "meter"})
    assert not is_meter_item({"name": "Item", "unit_type": "unit"})


def test_filter_components_by_code():
    results = filter_components("1248", limit=5)
    assert len(results) >= 1
    assert any(r["code"] == "1248" for r in results)


def test_filter_components_by_category():
    results = filter_components("", category=CAT_ROLO, limit=100)
    assert results
    assert all(item["category"] == CAT_ROLO for item in results)


def test_filter_components_category_and_query():
    results = filter_components("5060", category=CAT_ROLO, limit=5)
    assert len(results) == 1
    assert results[0]["code"] == "5060"


def test_filter_components_excludes_other_categories():
    results = filter_components("", category=CAT_HORIZONTAL_15_25, limit=100)
    assert results
    assert all(item["category"] == CAT_HORIZONTAL_15_25 for item in results)
    assert not any(item["category"] == CAT_ROLO for item in results)


def test_categorize_materials():
    items = [
        {"code": "1", "name": "Cavelete", "category": CAT_HORIZONTAL_15_25},
        {"code": "2", "name": "Tecido", "category": CAT_VERTICAL},
        {"code": "3", "name": "Trilho", "category": CAT_TRILHOS},
        {"code": "4", "name": "Comando", "category": CAT_ROLO},
        {"code": "5", "name": "Freio 50mm", "category": CAT_HORIZONTAL_50},
    ]
    buckets = categorize_materials(items)
    assert len(buckets[CAT_HORIZONTAL_15_25]) == 1
    assert len(buckets[CAT_VERTICAL]) == 1
    assert len(buckets[CAT_TRILHOS]) == 1
    assert len(buckets[CAT_ROLO]) == 1
    assert len(buckets[CAT_HORIZONTAL_50]) == 1


def test_filter_category_all_returns_mixed_catalog():
    results = filter_components("", category=FILTER_CATEGORY_ALL, limit=None)
    categories = {item["category"] for item in results}
    assert len(categories) > 1
