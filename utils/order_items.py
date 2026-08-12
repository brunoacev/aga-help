"""Extração e formatação de itens vinculados a pedidos."""

from __future__ import annotations

import json
import re


def format_item_qty(item: dict) -> str:
    """Formata quantidade ou metragem para exibição."""
    dim = (item.get("dim") or "").strip()
    if dim:
        return f"{dim}m"
    qty = item.get("qty", 1)
    return f"{qty} un"


def normalize_order_item(item: dict) -> dict:
    """Garante campos mínimos para exibição no modal."""
    normalized = {
        "code": str(item.get("code", "")).strip(),
        "name": str(item.get("name", "")).strip(),
        "qty": int(item.get("qty", 1) or 1),
        "dim": str(item.get("dim", "") or "").strip(),
    }
    normalized["qty_display"] = format_item_qty(normalized)
    return normalized


def parse_items_from_description(description: str) -> list[dict]:
    """Interpreta itens serializados na descrição do pedido."""
    items: list[dict] = []
    parts = re.split(r",\s*(?=\d+x\s+)", description or "")
    for part in parts:
        part = part.strip()
        if not part:
            continue

        dim = ""
        dim_match = re.search(r"\s+\((?P<dim>[\d,\.]+)m\)$", part)
        if dim_match:
            dim = dim_match.group("dim")
            part = part[: dim_match.start()].strip()

        match = re.match(r"^(?P<qty>\d+)x\s+(?P<code>\S+)\s+-\s+(?P<name>.+)$", part)
        if not match:
            continue

        items.append(
            normalize_order_item(
                {
                    "code": match.group("code"),
                    "name": match.group("name"),
                    "qty": int(match.group("qty")),
                    "dim": dim,
                }
            )
        )
    return items


def extract_order_items(order: dict) -> list[dict]:
    """Obtém itens estruturados do pedido (JSON persistido ou descrição legada)."""
    raw_items = order.get("items_json")
    if raw_items:
        try:
            parsed = json.loads(raw_items) if isinstance(raw_items, str) else raw_items
            if isinstance(parsed, list) and parsed:
                return [normalize_order_item(item) for item in parsed]
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return parse_items_from_description(order.get("description", ""))


def serialize_order_items(items: list[dict]) -> str:
    """Serializa itens do pedido para persistência."""
    payload = []
    for item in items:
        payload.append(
            {
                "code": item.get("code", ""),
                "name": item.get("name", ""),
                "qty": item.get("qty", 1),
                "dim": item.get("dim", ""),
            }
        )
    return json.dumps(payload, ensure_ascii=False)
