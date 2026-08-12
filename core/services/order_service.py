"""Serviço de pedidos — validação e criação."""

from __future__ import annotations

from datetime import datetime

from core.db import orders_repository
from core.db.logs_repository import add_log
from utils.dates import add_business_days
from utils.formatting import parse_brl
from utils.order_items import serialize_order_items
from utils.sanitization import sanitize_name, sanitize_text

SERVICE_PARTS = "componentes"
SERVICE_CURTAINS = frozenset({"rolo", "horizontal"})

BASE_REQUIRED_FIELDS = ("reseller_name", "order_number", "deadline_days", "service_type")


def validate_order_form(form_data: dict) -> tuple[bool, list[str]]:
    """Valida campos base sempre obrigatórios (boxes 1 e 2)."""
    missing: list[str] = []
    labels = {
        "reseller_name": "Revenda",
        "order_number": "Nº do Pedido",
        "deadline_days": "Prazo",
        "service_type": "Tipo de Serviço",
    }
    for field in BASE_REQUIRED_FIELDS:
        value = form_data.get(field)
        if value is None or not str(value).strip():
            missing.append(labels[field])
    return len(missing) == 0, missing


def create_order(form_data: dict) -> tuple[bool, str]:
    """
    Cria pedido a partir dos dados do formulário.
    Retorna (sucesso, mensagem_erro).
    """
    valid, missing = validate_order_form(form_data)
    if not valid:
        return False, f"Preencha os campos obrigatórios: {', '.join(missing)}"

    description = (form_data.get("description") or "").strip()
    if not description:
        return False, "A descrição do pedido não pode estar vazia."

    now = datetime.now()
    today_str = now.strftime("%d/%m/%Y")
    days_count = int(form_data["deadline_days"])
    deadline_dt = add_business_days(now, days_count)
    deadline_str = deadline_dt.strftime("%d/%m/%Y")
    value = parse_brl(form_data.get("value", "0"))

    orders_repository.add_order(
        order_number=sanitize_text(form_data["order_number"], max_length=30),
        reseller_name=sanitize_name(form_data["reseller_name"]),
        phone=form_data.get("phone", ""),
        address=form_data.get("address", ""),
        value=value,
        entry_date=today_str,
        deadline_date=deadline_str,
        description=sanitize_text(description),
        width=sanitize_text(form_data.get("width", ""), max_length=20),
        height=sanitize_text(form_data.get("height", ""), max_length=20),
        status="Orçamento",
        items_json=serialize_order_items(form_data.get("items") or []),
        service_type=sanitize_text(form_data.get("service_type", SERVICE_PARTS), max_length=30),
    )
    return True, ""


def get_orders() -> list[dict]:
    """Lista pedidos."""
    return orders_repository.get_orders()


def update_order_status(order_id: int, new_status: str) -> None:
    """Atualiza status do pedido."""
    orders_repository.update_order_status(order_id, new_status)
    add_log("STATUS", f"Pedido #{order_id} movido para {new_status}.")


def delete_order(order_id: int) -> None:
    """Remove pedido."""
    orders_repository.delete_order(order_id)
    add_log("EXCLUSÃO", f"Pedido #{order_id} removido do Kanban.")


def clear_all_orders() -> None:
    """Remove todos os pedidos."""
    orders_repository.clear_all_orders()
