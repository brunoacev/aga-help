"""Coluna clássica do quadro Kanban (lista vertical de cards)."""

from __future__ import annotations

import flet as ft

from core import colors
from core.kanban_stages import BILLED_STAGE, stage_label
from components.kanban_card import KanbanCard
from controllers.order_billing_controller import sort_faturado_orders
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric
from utils.ui_theme import FONT_LABEL, RADIUS, S2, S3, S4, WEIGHT_LABEL


class KanbanColumn(ft.Container):
    """Coluna de etapa com cards empilhados verticalmente."""

    def __init__(
        self,
        stage: str,
        orders: list,
        stage_color: str,
        stages: list,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
        expand: bool | int = False,
        compact: bool = False,
    ):
        label = stage_label(stage)
        pad = S2 if compact else S4
        card_spacing = S2 if compact else S3
        header = ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(width=S2, height=S2, border_radius=S2, bgcolor=stage_color),
                        ft.Text(label, weight=WEIGHT_LABEL, size=FONT_LABEL, color=colors.TEXT_PRIMARY),
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
                    bgcolor=colors.BG_SURFACE_LIGHT,
                    padding=make_padding_symmetric(horizontal=S2, vertical=4),
                    border_radius=RADIUS,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        cards_list = ft.Column(
            spacing=card_spacing,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        if stage == BILLED_STAGE:
            pending, completed = sort_faturado_orders(orders)
            if pending:
                cards_list.controls.append(self._section_label("Aguardando confirmação"))
                self._append_cards(
                    cards_list, pending, stages, on_move_callback, on_delete_callback,
                    on_details_callback, on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback, is_master=is_master,
                    compact=compact,
                )
            if completed:
                if pending:
                    cards_list.controls.append(ft.Divider(color=colors.BORDER_COLOR, height=1))
                    cards_list.controls.append(self._section_label("Concluídos"))
                self._append_cards(
                    cards_list, completed, stages, on_move_callback, on_delete_callback,
                    on_details_callback, on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback, is_master=is_master,
                    compact=compact,
                )
            if not pending and not completed:
                self._append_empty_state(cards_list)
        elif orders:
            self._append_cards(
                cards_list, orders, stages, on_move_callback, on_delete_callback,
                on_details_callback, on_complete_callback=on_complete_callback,
                on_history_callback=on_history_callback, is_master=is_master,
                compact=compact,
            )
        else:
            self._append_empty_state(cards_list)

        super().__init__(
            expand=expand,
            bgcolor=colors.BG_SURFACE,
            border=border_all(colors.BORDER_COLOR),
            border_radius=RADIUS,
            padding=pad,
            content=ft.Column(
                [header, ft.Divider(color=colors.BORDER_COLOR, height=1), cards_list],
                spacing=card_spacing,
                tight=True,
                expand=True,
            ),
        )

    @staticmethod
    def _section_label(text: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(text, size=11, color=colors.TEXT_MUTED, weight=ft.FontWeight.W_600),
            padding=make_padding_symmetric(horizontal=S2, vertical=4),
        )

    @staticmethod
    def _append_empty_state(cards_list: ft.Column) -> None:
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

    @staticmethod
    def _append_cards(
        cards_list: ft.Column,
        orders: list,
        stages: list,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
        compact: bool = False,
    ) -> None:
        for order in orders:
            cards_list.controls.append(
                KanbanCard(
                    order=order,
                    stages=stages,
                    on_move_callback=on_move_callback,
                    on_delete_callback=on_delete_callback,
                    on_details_callback=on_details_callback,
                    on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback,
                    is_master=is_master,
                    compact=compact,
                )
            )
