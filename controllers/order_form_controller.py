"""Controller do formulário de pedido."""

from __future__ import annotations

from core.constants import AGATEK_ADDRESS
from core.services.catalog_service import filter_components, is_meter_item
from core.services.contact_service import get_profile_by_exact_name, search_reseller_profiles
from core.services.order_service import SERVICE_CURTAINS, SERVICE_PARTS, create_order, validate_order_form
from utils.formatting import format_meters, parse_meters


class OrderFormController:
    """Gerencia estado e regras de negócio do cadastro de pedidos."""

    def __init__(self) -> None:
        self.selected_components: list[dict] = []

    def resolve_reseller_profile(self, name: str) -> dict:
        """Resolve telefone/endereço para revenda."""
        clean = (name or "").strip()
        if len(clean) < 2:
            return {"phone": "", "address": "", "suggestions": []}

        existing = get_profile_by_exact_name(clean)
        phone = existing.get("phone", "") if existing else ""
        address = existing.get("address", "") if existing else AGATEK_ADDRESS
        if not phone and not existing:
            phone = ""
            address = AGATEK_ADDRESS

        suggestions = search_reseller_profiles(clean, limit=3)
        return {"phone": phone, "address": address, "suggestions": suggestions}

    def filter_catalog(self, query: str, limit: int = 2, category: str | None = None) -> list[dict]:
        """Filtra componentes do catálogo."""
        return filter_components(query, limit=limit, category=category)

    def is_meter_item(self, item: dict) -> bool:
        """Delega verificação de item por metro."""
        return is_meter_item(item)

    def add_component(self, component: dict, dim_val: str, qty_val: str) -> tuple[bool, str, dict | None]:
        """Adiciona componente à lista selecionada. Retorna (sucesso, erro, item)."""
        try:
            qty = int(qty_val) if int(qty_val) > 0 else 1
        except ValueError:
            qty = 1

        is_meter = is_meter_item(component)
        dim_str = ""

        if is_meter:
            meters = parse_meters(dim_val)
            if meters is None:
                return False, "Informe a metragem em metros (m) para adicionar este componente.", None
            dim_str = format_meters(meters)

        if is_meter:
            display = f"{qty}x {component['code']} - {component['name']} ({dim_str}m)"
        else:
            display = f"{qty}x {component['code']} - {component['name']}"

        entry = {
            "code": component["code"],
            "name": component["name"],
            "qty": qty,
            "dim": dim_str,
            "is_meter": is_meter,
            "display": display,
        }
        self.selected_components.append(entry)
        return True, "", entry

    def remove_component(self, index: int) -> None:
        """Remove componente pelo índice."""
        if 0 <= index < len(self.selected_components):
            self.selected_components.pop(index)

    def components_summary(self) -> str:
        """Retorna resumo textual dos componentes selecionados."""
        if not self.selected_components:
            return ""
        return ", ".join(item["display"] for item in self.selected_components)

    def validate(self, form_data: dict) -> tuple[bool, str, set[str]]:
        """
        Valida formulário com regras condicionais por tipo de serviço.
        Retorna (válido, mensagem_erro, campos_com_erro).
        """
        error_fields: set[str] = set()
        valid_base, missing_labels = validate_order_form(form_data)
        if not valid_base:
            label_to_field = {
                "Revenda": "reseller_name",
                "Nº do Pedido": "order_number",
                "Prazo": "deadline_days",
                "Tipo de Serviço": "service_type",
            }
            for label in missing_labels:
                if label in label_to_field:
                    error_fields.add(label_to_field[label])
            return False, f"Preencha os campos obrigatórios: {', '.join(missing_labels)}", error_fields

        service_type = form_data.get("service_type", SERVICE_PARTS)

        if service_type == SERVICE_PARTS:
            if not self.selected_components:
                error_fields.add("components")
                return (
                    False,
                    "Para Venda de Peças, adicione pelo menos 1 componente ao pedido.",
                    error_fields,
                )
            missing_meter = [
                item["code"]
                for item in self.selected_components
                if item.get("is_meter") and not item.get("dim")
            ]
            if missing_meter:
                error_fields.add("components")
                return (
                    False,
                    "Informe a metragem (m) dos componentes vendidos por metro.",
                    error_fields,
                )
        elif service_type in SERVICE_CURTAINS:
            if not (form_data.get("description") or "").strip():
                error_fields.add("description")
                return (
                    False,
                    "Preencha a descrição/obrigatórios do serviço (Box 4).",
                    error_fields,
                )

        return True, "", set()

    def save(self, form_data: dict) -> tuple[bool, str]:
        """Valida e persiste pedido."""
        valid, error, _ = self.validate(form_data)
        if not valid:
            return False, error

        service_type = form_data.get("service_type", SERVICE_PARTS)
        if service_type == SERVICE_PARTS and not (form_data.get("description") or "").strip():
            form_data["description"] = self.components_summary()
        if service_type == SERVICE_PARTS:
            form_data["items"] = [
                {
                    "code": item["code"],
                    "name": item["name"],
                    "qty": item["qty"],
                    "dim": item.get("dim", ""),
                }
                for item in self.selected_components
            ]
        else:
            form_data["items"] = []

        success, persist_error = create_order(form_data)
        if success:
            self.reset()
        return success, persist_error

    def reset(self) -> None:
        """Limpa componentes selecionados."""
        self.selected_components.clear()
