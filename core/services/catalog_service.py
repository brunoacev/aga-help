"""Serviço de catálogo de componentes."""

from __future__ import annotations

from core.components_data import COMPONENTS_CATALOG, FILTER_CATEGORY_ALL, OFFICIAL_CATEGORIES
from utils.text_search import matches_search_query, normalize_search_text

METER_KEYWORDS = (
    "metro", "m²", "tubo", "bandô", "bando", "perfil",
    "corrente", "base", "trilho", "lâmina", "lamina",
)


def is_meter_item(item: dict) -> bool:
    """Indica se o componente é vendido por metro."""
    if "unit_type" in item:
        return item["unit_type"] == "meter"
    name_lower = item.get("name", "").lower()
    return any(kw in name_lower for kw in METER_KEYWORDS)


def filter_components(
    query: str,
    *,
    category: str | None = None,
    limit: int | None = 2,
) -> list[dict]:
    """Filtra catálogo por código, nome, categoria e filtro de categoria."""
    clean = (query or "").strip()
    pool = COMPONENTS_CATALOG
    if category and category != FILTER_CATEGORY_ALL:
        pool = [c for c in pool if c["category"] == category]

    if not normalize_search_text(clean):
        result = pool[: limit or len(pool)]
    else:
        result = [
            c for c in pool
            if matches_search_query(clean, c["code"], c["name"], c["category"])
        ]
        if limit:
            result = result[:limit]
    return result


def categorize_materials(catalog_items: list[dict]) -> dict[str, list[dict]]:
    """Agrupa materiais pelas categorias oficiais do catálogo."""
    buckets = {category: [] for category in OFFICIAL_CATEGORIES}
    for item in catalog_items:
        category = item.get("category", "")
        if category in buckets:
            buckets[category].append(item)
    return buckets
