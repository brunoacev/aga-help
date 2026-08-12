"""Serviço de catálogo de componentes."""

from __future__ import annotations

from core.components_data import COMPONENTS_CATALOG

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


def filter_components(query: str, *, limit: int | None = 2) -> list[dict]:
    """Filtra catálogo por código, nome ou categoria."""
    clean = (query or "").strip().lower()
    if not clean:
        result = COMPONENTS_CATALOG[: limit or len(COMPONENTS_CATALOG)]
    else:
        result = [
            c for c in COMPONENTS_CATALOG
            if clean in c["code"].lower()
            or clean in c["name"].lower()
            or clean in c["category"].lower()
        ]
        if limit:
            result = result[:limit]
    return result


def categorize_materials(catalog_items: list[dict]) -> dict[str, list[dict]]:
    """Agrupa materiais por categoria para a view de materiais."""
    buckets = {
        "horizontals": [],
        "top": [],
        "verticals": [],
        "profiles": [],
    }
    for item in catalog_items:
        category = item.get("category", "").lower()
        if any(k in category for k in ("horizonta", "horizontal", "lâmina", "lamina")):
            buckets["horizontals"].append(item)
        elif "vertical" in category or "tecidos" in category:
            buckets["verticals"].append(item)
        elif any(k in category for k in ("perfil", "tubo", "bandô", "bando", "trilho")):
            buckets["profiles"].append(item)
        elif any(k in category for k in ("top", "comando", "suporte", "rolo")):
            buckets["top"].append(item)
        else:
            buckets["top"].append(item)
    return buckets
