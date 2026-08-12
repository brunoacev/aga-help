"""Diálogo de histórico de ações do pedido."""

from __future__ import annotations

import flet as ft

from core import colors
from core.services.order_history_service import list_order_actions
from utils.ui_theme import FONT_BODY, FONT_CAPTION


def show_order_history_dialog(page: ft.Page, order: dict) -> None:
    order_id = int(order.get("id") or 0)
    order_number = order.get("order_number", order_id)
    entries = list_order_actions(order_id)

    if entries:
        lines = [
            f"{item.get('created_at', '--')} - {item.get('user_handle', '@?')} - {item.get('action_description', '')}"
            for item in entries
        ]
        body = ft.Column(
            [
                ft.Text(line, size=FONT_CAPTION, color=colors.TEXT_SECONDARY, selectable=True)
                for line in lines
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=min(360, 40 + len(lines) * 28),
        )
    else:
        body = ft.Text(
            "Nenhuma ação registrada para este pedido.",
            size=FONT_BODY,
            color=colors.TEXT_MUTED,
        )

    def close_dialog(_=None):
        dialog.open = False
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"Histórico — Pedido #{order_number}",
            color=colors.TEXT_PRIMARY,
            weight=ft.FontWeight.W_600,
        ),
        content=body,
        actions=[ft.TextButton(content="Fechar", on_click=close_dialog)],
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    else:
        page.dialog = dialog
        dialog.open = True
        page.update()
