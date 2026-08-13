"""Card de pedido no Kanban — colunas clássicas Produção / Pronto / Faturado."""

from __future__ import annotations

import flet as ft

from controllers.order_billing_controller import is_order_billed, is_order_billing_locked
from core import colors
from core.kanban_stages import BILLED_STAGE, normalize_order_status, stage_label
from utils.formatting import format_brl
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.order_card_display import get_service_label
from utils.order_dates import format_order_datetime
from utils.ui_theme import FONT_BODY, FONT_CAPTION, FONT_LABEL, RADIUS, S2, S3, icon_button


def _format_order_number(order: dict) -> str:
    raw = str(order.get("order_number") or order.get("id") or "").strip()
    return raw.lstrip("#").strip() or str(order.get("id", ""))


class KanbanCard(ft.Container):
    """Card vertical com dados essenciais e ações do fluxo."""

    def __init__(
        self,
        order,
        stages,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
    ):
        order_id = order["id"]
        order_number = _format_order_number(order)
        client_name = order.get("reseller_name", "Cliente")
        current_status = normalize_order_status(order.get("status"))
        billed = is_order_billed(order)
        locked = is_order_billing_locked(order, is_master=is_master)
        created_by = (order.get("created_by") or "").strip()
        created_date = format_order_datetime(order)
        service_label = get_service_label(order)
        value = float(order.get("value", 0.0))
        formatted_value = format_brl(value)
        formatted_commission = format_brl(value * 0.02)
        title_decoration = ft.TextDecoration.LINE_THROUGH if billed else None

        header = ft.Row(
            [
                ft.Text(
                    f"Pedido {order_number}",
                    weight=ft.FontWeight.W_600,
                    size=FONT_LABEL,
                    color=colors.TEXT_PRIMARY,
                    style=ft.TextStyle(decoration=title_decoration) if title_decoration else None,
                ),
                ft.Container(expand=True),
                ft.Text(created_date, size=FONT_CAPTION, color=colors.TEXT_MUTED),
            ],
        )

        client_row = ft.Text(
            client_name,
            size=FONT_BODY,
            color=colors.PRIMARY,
            weight=ft.FontWeight.W_500,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        )

        service_row = ft.Text(
            service_label,
            size=FONT_CAPTION,
            color=colors.TEXT_SECONDARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        )

        author_badge = ft.Container(
            content=ft.Text(
                f"👤 {created_by}" if created_by else "👤 @?",
                size=10,
                color=colors.PRIMARY,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.PRIMARY),
            border_radius=RADIUS,
            padding=make_padding_symmetric(horizontal=8, vertical=4),
            visible=bool(created_by),
        )

        financial = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("VALOR", size=10, color=colors.TEXT_MUTED, weight=ft.FontWeight.W_600),
                        ft.Text(formatted_value, size=FONT_BODY, weight=ft.FontWeight.W_600),
                    ],
                    spacing=2,
                    tight=True,
                ),
                ft.Column(
                    [
                        ft.Text("COMISSÃO", size=10, color=colors.PRIMARY, weight=ft.FontWeight.W_600),
                        ft.Text(formatted_commission, size=FONT_BODY, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                    ],
                    spacing=2,
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        btn_details = icon_button(
            "LIST_ALT_ROUNDED",
            "list_alt",
            color=colors.TEXT_SECONDARY,
            tooltip="Ver Detalhes dos Itens",
            on_click=lambda _: on_details_callback(order),
            disabled=locked,
            size=18,
        )
        btn_history = icon_button(
            "HISTORY",
            "history",
            color=colors.TEXT_SECONDARY,
            tooltip="Histórico de Ações",
            on_click=lambda _: on_history_callback(order) if on_history_callback else None,
            disabled=on_history_callback is None,
            size=18,
        )

        action_buttons: list[ft.Control] = []
        curr_index = stages.index(current_status) if current_status in stages else 0

        if not locked and curr_index > 0:
            prev = stages[curr_index - 1]
            action_buttons.append(
                icon_button(
                    "ARROW_BACK_ROUNDED",
                    "arrow_back",
                    color=colors.TEXT_SECONDARY,
                    tooltip=f"Voltar para {stage_label(prev)}",
                    on_click=lambda _: on_move_callback(order_id, prev),
                    size=18,
                )
            )

        if not locked and curr_index < len(stages) - 1:
            nxt = stages[curr_index + 1]
            action_buttons.append(
                icon_button(
                    "ARROW_FORWARD_ROUNDED",
                    "arrow_forward",
                    color=colors.PRIMARY,
                    tooltip=f"Avançar para {stage_label(nxt)}",
                    on_click=lambda _: on_move_callback(order_id, nxt),
                    size=18,
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
                size=18,
            )
        elif current_status == BILLED_STAGE and billed:
            billing_action = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(getattr(ft.Icons, "VERIFIED", None) or "verified", color=colors.SUCCESS, size=16),
                        ft.Text("Faturado & Concluído", size=FONT_CAPTION, color=colors.SUCCESS, weight=ft.FontWeight.W_600),
                    ],
                    spacing=S2 // 2,
                ),
                bgcolor=colors.BG_SUCCESS_SUBTLE,
                border=border_all(colors.SUCCESS),
                border_radius=RADIUS,
                padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            )

        btn_delete = icon_button(
            "DELETE_OUTLINE",
            "delete",
            color=colors.ERROR,
            tooltip="Excluir Pedido",
            on_click=lambda _: on_delete_callback(order_id),
            disabled=locked,
            size=18,
        )

        left_actions = [btn_details, btn_history, *action_buttons]
        if billing_action is not None:
            left_actions.append(billing_action)

        actions_row = ft.Row(
            [ft.Row(left_actions, spacing=0, wrap=True), btn_delete],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        card_bg = colors.BG_SUCCESS_SUBTLE if billed and current_status == BILLED_STAGE else colors.BG_SURFACE_LIGHT
        card_border = colors.SUCCESS if billed and current_status == BILLED_STAGE else colors.BORDER_COLOR

        super().__init__(
            bgcolor=card_bg,
            border=border_all(card_border),
            border_radius=RADIUS,
            padding=S3,
            on_hover=self._on_hover,
            data={"billed": billed},
            content=ft.Column(
                [
                    header,
                    client_row,
                    service_row,
                    author_badge,
                    financial,
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
        self.border = border_all(colors.PRIMARY if e.data == "true" else self._default_border)
        self.bgcolor = colors.BG_HOVER if e.data == "true" else self._default_bg
        safe_update(self)
