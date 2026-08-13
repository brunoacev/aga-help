"""Card de pedido no Kanban — layout compacto com 4 linhas padronizadas."""

from __future__ import annotations

import flet as ft

from controllers.order_billing_controller import BILLED_STAGE, is_order_billed, is_order_billing_locked
from core import colors
from utils.formatting import format_br_phone, format_brl
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.order_card_display import get_service_label
from utils.order_dates import format_order_datetime
from utils.ui_theme import FONT_CAPTION, RADIUS_LG, S2, icon_button

CARD_PADDING = 12


def _sep() -> ft.Text:
    return ft.Text("|", size=FONT_CAPTION, color=colors.TEXT_MUTED)


def _line_text(
    value: str,
    *,
    weight=ft.FontWeight.W_400,
    color: str | None = None,
    expand: bool = False,
    decoration=None,
) -> ft.Text:
    return ft.Text(
        value,
        size=FONT_CAPTION,
        weight=weight,
        color=color or colors.TEXT_SECONDARY,
        overflow=ft.TextOverflow.ELLIPSIS,
        max_lines=1,
        expand=expand,
        style=ft.TextStyle(decoration=decoration) if decoration else None,
    )


def _content_line(*parts: ft.Control) -> ft.Row:
    controls: list[ft.Control] = []
    for index, part in enumerate(parts):
        if index > 0:
            controls.append(_sep())
        controls.append(part)
    return ft.Row(
        controls,
        spacing=S2 // 2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        wrap=True,
    )


class KanbanCard(ft.Container):
    """Representa um pedido no grid Kanban (4 linhas sequenciais)."""

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
        order_number = order.get("order_number", f"#{order_id}")
        client_name = order.get("reseller_name", "Cliente")
        phone_raw = order.get("phone", "")
        phone = format_br_phone(phone_raw) if phone_raw else "Sem telefone"
        current_status = order.get("status", "Orçamento")
        billed = is_order_billed(order)
        locked = is_order_billing_locked(order, is_master=is_master)
        created_by = (order.get("created_by") or "").strip()

        value = float(order.get("value", 0.0))
        commission = value * 0.02
        formatted_value = format_brl(value)
        formatted_commission = format_brl(commission)
        created_date = format_order_datetime(order)
        service_label = get_service_label(order)

        title_decoration = ft.TextDecoration.LINE_THROUGH if billed else None

        line1 = _content_line(
            _line_text(
                f"#{order_number}",
                weight=ft.FontWeight.W_700,
                color=colors.TEXT_PRIMARY,
                decoration=title_decoration,
            ),
            _line_text(client_name, expand=True, color=colors.PRIMARY),
            _line_text(created_date, color=colors.TEXT_MUTED),
        )

        line2 = _content_line(
            _line_text(phone),
            _line_text(service_label, color=colors.TEXT_PRIMARY),
        )

        line3 = _content_line(
            _line_text(
                formatted_value,
                weight=ft.FontWeight.W_600,
                color=colors.TEXT_PRIMARY,
            ),
            _line_text(
                f"Comis.: {formatted_commission}",
                weight=ft.FontWeight.W_600,
                color=colors.PRIMARY,
            ),
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

        status_actions: list[ft.Control] = []
        curr_index = stages.index(current_status) if current_status in stages else 0

        if not locked and curr_index > 0:
            prev_stage = stages[curr_index - 1]
            status_actions.append(
                icon_button(
                    "ARROW_BACK_ROUNDED",
                    "arrow_back",
                    color=colors.TEXT_SECONDARY,
                    tooltip=f"Voltar para {prev_stage}",
                    on_click=lambda _: on_move_callback(order_id, prev_stage),
                    size=18,
                )
            )

        if not locked and curr_index < len(stages) - 1:
            next_stage = stages[curr_index + 1]
            status_actions.append(
                icon_button(
                    "ARROW_FORWARD_ROUNDED",
                    "arrow_forward",
                    color=colors.PRIMARY,
                    tooltip=f"Avançar para {next_stage}",
                    on_click=lambda _: on_move_callback(order_id, next_stage),
                    size=18,
                )
            )

        if current_status == BILLED_STAGE and not billed and on_complete_callback:
            status_actions.append(
                icon_button(
                    "CHECK_CIRCLE_OUTLINE",
                    "check_circle_outline",
                    color=colors.SUCCESS,
                    tooltip="Concluir Faturamento",
                    on_click=lambda _: on_complete_callback(order_id),
                    size=18,
                )
            )
        elif current_status == BILLED_STAGE and billed:
            status_actions.append(
                ft.Container(
                    content=ft.Text(
                        "Faturado",
                        size=10,
                        color=colors.SUCCESS,
                        weight=ft.FontWeight.W_600,
                    ),
                    bgcolor=colors.BG_SUCCESS_SUBTLE,
                    border=border_all(colors.SUCCESS),
                    border_radius=8,
                    padding=make_padding_symmetric(horizontal=6, vertical=2),
                )
            )

        if not status_actions:
            status_actions.append(
                ft.Container(width=24, height=24)
            )

        author_badge = ft.Container(
            content=ft.Text(
                f"👤 {created_by}" if created_by else "👤 @?",
                size=9,
                color=colors.PRIMARY,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.PRIMARY),
            border_radius=8,
            padding=make_padding_symmetric(horizontal=6, vertical=2),
            visible=bool(created_by),
        )

        line4 = ft.Row(
            [
                btn_details,
                btn_history,
                ft.Row(status_actions, spacing=0),
                ft.Container(expand=True),
                author_badge,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

        card_bg = colors.BG_SUCCESS_SUBTLE if billed and current_status == BILLED_STAGE else colors.BG_SURFACE
        card_border = colors.SUCCESS if billed and current_status == BILLED_STAGE else colors.BORDER_COLOR

        super().__init__(
            bgcolor=card_bg,
            border=border_all(card_border),
            border_radius=RADIUS_LG,
            padding=CARD_PADDING,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
            on_hover=self._on_hover,
            data={"billed": billed, "order_id": order_id, "locked": locked},
            content=ft.Column(
                [line1, line2, line3, line4],
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
