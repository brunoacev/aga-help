"""Coluna do quadro Kanban."""

from __future__ import annotations

import flet as ft

from core import colors
from components.order_card import OrderCard
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric
from utils.ui_theme import FONT_LABEL, RADIUS, S1, S2, S3, S4, WEIGHT_LABEL


class KanbanColumn(ft.Container):
    """Coluna de etapa do Kanban."""

    def __init__(
        self,
        stage: str,
        orders: list,
        stage_color: str,
        stages: list,
        on_move_callback,
        on_delete_callback,
        *,
        expand: bool | int = False,
    ):
        header = ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(width=S2, height=S2, border_radius=S2, bgcolor=stage_color),
                        ft.Text(
                            stage,
                            weight=WEIGHT_LABEL,
                            size=FONT_LABEL,
                            color=colors.TEXT_PRIMARY,
                        ),
                    ],
                    spacing=S2,
                ),
                ft.Container(
                    content=ft.Text(
                        str(len(orders)),
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=colors.TEXT_SECONDARY,
                    ),
                    bgcolor=colors.BG_SURFACE,
                    padding=make_padding_symmetric(horizontal=S2, vertical=S1),
                    border_radius=RADIUS,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        cards_list = ft.Column(spacing=S3, scroll=ft.ScrollMode.AUTO, expand=True, tight=True)
        for order in orders:
            cards_list.controls.append(
                OrderCard(
                    order=order,
                    stages=stages,
                    on_move_callback=on_move_callback,
                    on_delete_callback=on_delete_callback,
                )
            )

        if not orders:
            cards_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum pedido nesta etapa",
                        size=11,
                        color=colors.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=S4,
                    alignment=get_alignment_center(),
                )
            )

        super().__init__(
            expand=expand,
            bgcolor=colors.BG_SURFACE,
            border=border_all(colors.BORDER_COLOR),
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    header,
                    ft.Divider(color=colors.BORDER_COLOR, height=1),
                    cards_list,
                ],
                spacing=S3,
                tight=True,
                expand=True,
            ),
        )
