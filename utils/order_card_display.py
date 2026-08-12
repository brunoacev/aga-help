"""Campos de resumo exibidos no card do Kanban (sem listagem de itens)."""

from __future__ import annotations

from core.services.order_service import SERVICE_CURTAINS, SERVICE_PARTS
from utils.order_items import extract_order_items, parse_items_from_description

SERVICE_LABELS = {
    SERVICE_PARTS: "Venda de Peças",
    "rolo": "Serviço em Cortina Rolô",
    "horizontal": "Serviço em Cortina Horizontal",
}


def infer_service_type(order: dict) -> str:
    """Infere tipo de serviço para pedidos legados sem campo persistido."""
    stored = (order.get("service_type") or "").strip()
    if stored:
        return stored

    items = extract_order_items(order)
    if items:
        return SERVICE_PARTS

    description = (order.get("description") or "").lower()
    if "rolô" in description or "rolo" in description:
        return "rolo"
    if "horizontal" in description:
        return "horizontal"
    if order.get("width") or order.get("height"):
        return "horizontal"
    return SERVICE_PARTS


def get_service_label(order: dict) -> str:
    """Rótulo legível do tipo de serviço."""
    service_type = infer_service_type(order)
    return SERVICE_LABELS.get(service_type, service_type.replace("_", " ").title())


def get_card_dimensions(order: dict) -> str:
    """Formata medidas do pedido, se informadas."""
    width = (order.get("width") or "").strip()
    height = (order.get("height") or "").strip()
    if not width and not height:
        return ""
    return f"{width or '?'}m × {height or '?'}m"


def get_card_notes(order: dict) -> str:
    """Observação complementar — oculta listagem de componentes redundante."""
    description = (order.get("description") or "").strip()
    if not description:
        return ""

    items = extract_order_items(order)
    if items and parse_items_from_description(description):
        return ""

    return description


def build_card_summary_lines(order: dict) -> list[str]:
    """Monta linhas de resumo para o corpo do card."""
    lines: list[str] = [f"Tipo: {get_service_label(order)}"]

    dimensions = get_card_dimensions(order)
    if dimensions:
        lines.append(f"Medidas: {dimensions}")

    notes = get_card_notes(order)
    if notes:
        lines.append(f"Obs.: {notes}")

    return lines
