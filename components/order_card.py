"""Card de pedido no Kanban."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.formatting import format_brl
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.ui_theme import FONT_BODY, FONT_CAPTION, FONT_LABEL, RADIUS, S2, S3, icon_button


class OrderCard(ft.Container):
    """Representa um pedido na coluna Kanban."""

    def __init__(self, order, stages, on_move_callback, on_delete_callback, on_details_callback):
        order_id = order["id"]
        order_number = order.get("order_number", f"#{order_id}")
        reseller_name = order.get("reseller_name", "Revenda Desconhecida")
        phone = order.get("phone", "")
        address = order.get("address", "Agatek Persianas e Cortinas de Fortaleza")
        description = order.get("description", "Sem descrição")
        width = order.get("width", "")
        height = order.get("height", "")
        current_status = order.get("status", "Orçamento")

        value = float(order.get("value", 0.0))
        commission = value * 0.02
        formatted_value = format_brl(value)
        formatted_commission = format_brl(commission)

        card_header = ft.Row(
            [
                ft.Text(
                    f"Pedido #{order_number}",
                    weight=ft.FontWeight.W_600,
                    size=FONT_LABEL,
                    color=colors.TEXT_PRIMARY,
                ),
                ft.Text(
                    reseller_name,
                    size=FONT_BODY,
                    color=colors.PRIMARY,
                    weight=ft.FontWeight.W_500,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        contact_info = []
        if phone:
            contact_info.append(ft.Text(f"📞 {phone}", size=FONT_CAPTION, color=colors.TEXT_SECONDARY))
        contact_info.append(
            ft.Text(
                f"📍 {address}",
                size=FONT_CAPTION,
                color=colors.TEXT_MUTED,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )

        dimensions_text = f" · {width or '?'}m × {height or '?'}m" if (width or height) else ""
        desc_text = ft.Text(
            f"{description}{dimensions_text}",
            size=FONT_CAPTION,
            color=colors.TEXT_SECONDARY,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        financial_box = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("VALOR TOTAL", size=10, color=colors.TEXT_MUTED, weight=ft.FontWeight.W_600),
                            ft.Text(formatted_value, size=FONT_BODY, weight=ft.FontWeight.W_600, color=colors.TEXT_PRIMARY),
                        ],
                        spacing=S2 // 4,
                    ),
                    ft.Column(
                        [
                            ft.Text("COMISSÃO (2%)", size=10, color=colors.PRIMARY, weight=ft.FontWeight.W_600),
                            ft.Text(formatted_commission, size=FONT_BODY, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                        ],
                        spacing=S2 // 4,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=colors.BG_SURFACE_LIGHT,
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            border_radius=RADIUS,
        )

        action_buttons = []
        curr_index = stages.index(current_status) if current_status in stages else 0

        if curr_index > 0:
            prev_stage = stages[curr_index - 1]
            action_buttons.append(
                icon_button(
                    "ARROW_BACK_ROUNDED",
                    "arrow_back",
                    color=colors.TEXT_SECONDARY,
                    tooltip=f"Voltar para {prev_stage}",
                    on_click=lambda _: on_move_callback(order_id, prev_stage),
                )
            )

        if curr_index < len(stages) - 1:
            next_stage = stages[curr_index + 1]
            action_buttons.append(
                icon_button(
                    "ARROW_FORWARD_ROUNDED",
                    "arrow_forward",
                    color=colors.PRIMARY,
                    tooltip=f"Avançar para {next_stage}",
                    on_click=lambda _: on_move_callback(order_id, next_stage),
                )
            )

        btn_details = icon_button(
            "LIST_ALT_ROUNDED",
            "list_alt",
            color=colors.TEXT_SECONDARY,
            tooltip="Ver Detalhes dos Itens",
            on_click=lambda _: on_details_callback(order),
        )
        btn_delete = icon_button(
            "DELETE_OUTLINE",
            "delete",
            color=colors.ERROR,
            tooltip="Excluir Pedido",
            on_click=lambda _: on_delete_callback(order_id),
        )

        actions_row = ft.Row(
            [
                ft.Row([btn_details, *action_buttons], spacing=0),
                btn_delete,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        super().__init__(
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.BORDER_COLOR),
            border_radius=RADIUS,
            padding=S3,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
            on_hover=self._on_hover,
            content=ft.Column(
                [
                    card_header,
                    ft.Column(contact_info, spacing=S2 // 4, tight=True),
                    desc_text,
                    financial_box,
                    ft.Divider(color=colors.BORDER_COLOR, height=1),
                    actions_row,
                ],
                spacing=S2,
                tight=True,
            ),
        )

    def _on_hover(self, e):
        self.border = border_all(
            colors.PRIMARY if e.data == "true" else colors.BORDER_COLOR,
        )
        self.bgcolor = colors.BG_HOVER if e.data == "true" else colors.BG_SURFACE_LIGHT
        safe_update(self)
