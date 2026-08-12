"""Modal de detalhamento de itens do pedido no Kanban."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import border_all, make_padding_symmetric
from utils.order_items import extract_order_items
from utils.ui_theme import FONT_CAPTION, FONT_LABEL, RADIUS, S2, S3, WEIGHT_LABEL


def show_order_items_dialog(page: ft.Page, order: dict) -> None:
    """Abre AlertDialog com itens vinculados ao pedido."""
    order_number = order.get("order_number") or order.get("id", "")
    title = f"Itens da OS #{order_number}"
    items = extract_order_items(order)

    if not items:
        content = ft.Text(
            "Nenhum componente vinculado a este pedido.",
            size=FONT_CAPTION,
            color=colors.TEXT_SECONDARY,
        )
    else:
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("CÓDIGO", width=72, size=FONT_CAPTION, weight=WEIGHT_LABEL, color=colors.TEXT_MUTED),
                    ft.Text("NOME / DESCRIÇÃO", expand=True, size=FONT_CAPTION, weight=WEIGHT_LABEL, color=colors.TEXT_MUTED),
                    ft.Text("QTD / METRAGEM", width=108, size=FONT_CAPTION, weight=WEIGHT_LABEL, color=colors.TEXT_MUTED),
                ],
                spacing=S2,
            ),
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            bgcolor=colors.BG_SURFACE,
            border_radius=RADIUS,
        )

        rows: list[ft.Control] = [header, ft.Divider(height=1, color=colors.BORDER_COLOR)]
        for item in items:
            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(item["code"], width=72, size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                            ft.Text(
                                item["name"],
                                expand=True,
                                size=FONT_CAPTION,
                                color=colors.TEXT_PRIMARY,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=2,
                            ),
                            ft.Text(
                                item["qty_display"],
                                width=108,
                                size=FONT_CAPTION,
                                color=colors.TEXT_SECONDARY,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                        ],
                        spacing=S2,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    padding=make_padding_symmetric(horizontal=S2, vertical=S2),
                    border=border_all(colors.BORDER_COLOR),
                    border_radius=RADIUS,
                )
            )

        content = ft.Container(
            content=ft.Column(rows, spacing=S2, scroll=ft.ScrollMode.AUTO),
            height=320,
            width=520,
        )

    def close_dialog(_=None):
        dialog.open = False
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, color=colors.TEXT_PRIMARY, weight=ft.FontWeight.W_600, size=15),
        content=content,
        actions=[ft.TextButton(content="Fechar", on_click=close_dialog)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    else:
        page.dialog = dialog
        dialog.open = True
    page.update()
