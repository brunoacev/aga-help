"""Seção de especificação básica do pedido."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.ui_theme import S2, S3, dropdown_style, section_card

COL_SPEC_ROW = {"sm": 12, "md": 4, "lg": 4, "xl": 4}


class OrderSpecSection(ft.Container):
    """Número do pedido, tipo de serviço e prazo."""

    def __init__(self, input_style: dict, digits_only_filter):
        dd_style = dropdown_style()
        self.txt_order_num = ft.TextField(
            label="Nº Pedido *",
            input_filter=digits_only_filter,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
            **input_style,
        )
        self.dd_service_type = ft.Dropdown(
            label="Tipo de Serviço *",
            value="componentes",
            expand=True,
            options=[
                ft.dropdown.Option("componentes", text="Venda de Peças"),
                ft.dropdown.Option("rolo", text="Serviço em Cortina Rolô"),
                ft.dropdown.Option("horizontal", text="Serviço em Cortina Horizontal"),
            ],
            **dd_style,
        )
        self.dd_deadline_days = ft.Dropdown(
            label="Prazo *",
            value="3",
            expand=True,
            options=[
                ft.dropdown.Option(str(i), text=f"{i} dia útil" if i == 1 else f"{i} dias úteis")
                for i in range(1, 8)
            ],
            **dd_style,
        )

        form_row = ft.ResponsiveRow(
            [
                ft.Container(self.txt_order_num, col=COL_SPEC_ROW, expand=True),
                ft.Container(self.dd_service_type, col=COL_SPEC_ROW, expand=True),
                ft.Container(self.dd_deadline_days, col=COL_SPEC_ROW, expand=True),
            ],
            run_spacing=S2,
            spacing=S2,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        card = section_card("2. Especificação do Pedido", form_row, accent=True)
        super().__init__(
            bgcolor=card.bgcolor,
            border=card.border,
            border_radius=card.border_radius,
            padding=card.padding,
            content=card.content,
        )

    def get_values(self) -> dict:
        return {
            "order_number": (self.txt_order_num.value or "").strip(),
            "deadline_days": self.dd_deadline_days.value or "3",
            "service_type": self.dd_service_type.value or "componentes",
        }

    def reset(self) -> None:
        self.txt_order_num.value = ""
        self.dd_deadline_days.value = "3"
        self.dd_service_type.value = "componentes"

    def mark_invalid_fields(self, fields: set[str]) -> None:
        if "order_number" in fields:
            self.txt_order_num.border_color = colors.ERROR
        if "deadline_days" in fields:
            self.dd_deadline_days.border_color = colors.ERROR
        if "service_type" in fields:
            self.dd_service_type.border_color = colors.ERROR

    def clear_validation(self) -> None:
        self.txt_order_num.border_color = colors.BORDER_COLOR
        self.dd_deadline_days.border_color = colors.BORDER_COLOR
        self.dd_service_type.border_color = colors.BORDER_COLOR
