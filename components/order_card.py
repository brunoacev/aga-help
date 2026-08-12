"""Card de pedido no Kanban."""

from __future__ import annotations

import flet as ft

from controllers.order_billing_controller import BILLED_STAGE, is_order_billed, is_order_billing_locked
from core import colors
from utils.formatting import format_brl
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.order_card_display import build_card_summary_lines
from utils.order_dates import format_order_date_label
from utils.ui_theme import FONT_BODY, FONT_CAPTION, FONT_LABEL, RADIUS, S2, S3, icon_button


class OrderCard(ft.Container):
    """Representa um pedido na coluna Kanban."""

    def __init__(
        self,
        order,
        stages,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        is_master: bool = False,
    ):
        order_id = order["id"]
        order_number = order.get("order_number", f"#{order_id}")
        reseller_name = order.get("reseller_name", "Revenda Desconhecida")
        phone = order.get("phone", "")
        address = order.get("address", "Agatek Persianas e Cortinas de Fortaleza")
        current_status = order.get("status", "Orçamento")
        billed = is_order_billed(order)
        locked = is_order_billing_locked(order, is_master=is_master)

        value = float(order.get("value", 0.0))
        commission = value * 0.02
        formatted_value = format_brl(value)
        formatted_commission = format_brl(commission)

        order_date_label = format_order_date_label(order)
        order_title = ft.Text(
            f"Pedido #{order_number}",
            weight=ft.FontWeight.W_600,
            size=FONT_LABEL,
            color=colors.TEXT_PRIMARY,
            decoration=ft.TextDecoration.LINE_THROUGH if billed else None,
        )

        card_header = ft.Column(
            [
                ft.Row(
                    [
                        order_title,
                        ft.Text(
                            order_date_label,
                            size=FONT_CAPTION,
                            color=colors.TEXT_MUTED,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            reseller_name,
                            size=FONT_BODY,
                            color=colors.PRIMARY,
                            weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=S2 // 4,
            tight=True,
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

        summary_lines = build_card_summary_lines(order)
        summary_column = ft.Column(
            [
                ft.Text(
                    line,
                    size=FONT_CAPTION,
                    color=colors.TEXT_SECONDARY,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
                for line in summary_lines
            ],
            spacing=S2 // 4,
            tight=True,
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

        if not locked and curr_index > 0:
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

        if not locked and curr_index < len(stages) - 1:
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

        billing_action = None
        if current_status == BILLED_STAGE and not billed and on_complete_callback:
            billing_action = icon_button(
                "CHECK_CIRCLE_OUTLINE",
                "check_circle_outline",
                color=colors.SUCCESS,
                tooltip="Concluir Faturamento",
                on_click=lambda _: on_complete_callback(order_id),
            )
        elif current_status == BILLED_STAGE and billed:
            billing_action = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(getattr(ft.Icons, "VERIFIED", None) or "verified", color=colors.SUCCESS, size=16),
                        ft.Text(
                            "Faturado & Concluído",
                            size=FONT_CAPTION,
                            color=colors.SUCCESS,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=S2 // 2,
                ),
                bgcolor=colors.BG_SUCCESS_SUBTLE,
                border=border_all(colors.SUCCESS),
                border_radius=RADIUS,
                padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            )

        btn_details = icon_button(
            "LIST_ALT_ROUNDED",
            "list_alt",
            color=colors.TEXT_SECONDARY,
            tooltip="Ver Detalhes dos Itens",
            on_click=lambda _: on_details_callback(order),
            disabled=locked,
        )
        btn_delete = icon_button(
            "DELETE_OUTLINE",
            "delete",
            color=colors.ERROR,
            tooltip="Excluir Pedido",
            on_click=lambda _: on_delete_callback(order_id),
            disabled=locked,
        )

        left_actions = [btn_details, *action_buttons]
        if billing_action is not None:
            left_actions.append(billing_action)

        actions_row = ft.Row(
            [
                ft.Row(left_actions, spacing=0, wrap=True),
                btn_delete,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        card_bg = colors.BG_SUCCESS_SUBTLE if billed and current_status == BILLED_STAGE else colors.BG_SURFACE_LIGHT
        card_border = colors.SUCCESS if billed and current_status == BILLED_STAGE else colors.BORDER_COLOR

        super().__init__(
            bgcolor=card_bg,
            border=border_all(card_border),
            border_radius=RADIUS,
            padding=S3,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
            on_hover=self._on_hover,
            data={"billed": billed},
            content=ft.Column(
                [
                    card_header,
                    ft.Column(contact_info, spacing=S2 // 4, tight=True),
                    summary_column,
                    financial_box,
                    ft.Divider(color=colors.BORDER_COLOR, height=1),
                    actions_row,
                ],
                spacing=S2,
                tight=True,
            ),
        )
        self._default_bg = card_bg
        self._default_border = card_border

    def _on_hover(self, e):
        if self.data and self.data.get("billed"):
            return
        self.border = border_all(
            colors.PRIMARY if e.data == "true" else self._default_border,
        )
        self.bgcolor = colors.BG_HOVER if e.data == "true" else self._default_bg
        safe_update(self)
