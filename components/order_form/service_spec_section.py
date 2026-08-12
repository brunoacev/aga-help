"""Seção de especificação do serviço e valor."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.ui_theme import COL_FULL, COL_QUARTER, S3, section_card


class ServiceSpecSection(ft.Container):
    """Dimensões, valor e descrição do serviço."""

    def __init__(self, input_style: dict, decimal_filter):
        self.txt_num_order = ft.TextField(
            label="Pedido Original",
            hint_text="Ex: 333333",
            input_filter=decimal_filter,
            **input_style,
        )
        self.txt_width = ft.TextField(
            label="Largura (m)",
            hint_text="Ex: 2.50",
            input_filter=decimal_filter,
            **input_style,
        )
        self.txt_height = ft.TextField(
            label="Altura (m)",
            hint_text="Ex: 2.80",
            input_filter=decimal_filter,
            **input_style,
        )
        self.txt_value = ft.TextField(
            label="Valor Total (R$)",
            hint_text="Ex: 150.00",
            input_filter=decimal_filter,
            **input_style,
        )
        self.txt_description = ft.TextField(
            label="Descrição Detalhada / Especificações do Serviço *",
            hint_text="Digite aqui as observações ou especificações técnicas do serviço...",
            min_lines=2,
            max_lines=4,
            **input_style,
        )

        dims_row = ft.ResponsiveRow(
            [
                ft.Container(self.txt_num_order, col=COL_QUARTER),
                ft.Container(self.txt_width, col=COL_QUARTER),
                ft.Container(self.txt_height, col=COL_QUARTER),
                ft.Container(self.txt_value, col=COL_QUARTER),
            ],
            run_spacing=S3,
            spacing=S3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        desc_row = ft.ResponsiveRow(
            [ft.Container(self.txt_description, col=COL_FULL)],
            run_spacing=S3,
            spacing=S3,
        )

        card = section_card(
            "4. Especificação do Serviço",
            ft.Column([dims_row, desc_row], spacing=S3),
            accent=True,
        )
        super().__init__(
            bgcolor=card.bgcolor,
            border=card.border,
            border_radius=card.border_radius,
            padding=card.padding,
            content=card.content,
        )

    def get_values(self) -> dict:
        return {
            "width": (self.txt_width.value or "").strip(),
            "height": (self.txt_height.value or "").strip(),
            "value": self.txt_value.value or "0",
            "description": (self.txt_description.value or "").strip(),
        }

    def set_description(self, text: str) -> None:
        if text:
            self.txt_description.value = text

    def reset(self) -> None:
        self.txt_num_order.value = ""
        self.txt_width.value = ""
        self.txt_height.value = ""
        self.txt_value.value = ""
        self.txt_description.value = ""

    def mark_invalid(self) -> None:
        self.txt_description.border_color = colors.ERROR

    def clear_validation(self) -> None:
        self.txt_description.border_color = colors.BORDER_COLOR
