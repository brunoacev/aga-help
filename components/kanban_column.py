"""Coluna do quadro Kanban com grid 2x2 de cards."""

from __future__ import annotations

import flet as ft

from controllers.order_billing_controller import BILLED_STAGE, sort_faturado_orders
from core import colors
from components.kanban_card import KanbanCard
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric
from utils.ui_theme import FONT_CAPTION, FONT_LABEL, RADIUS, S1, S2, S3, S4, WEIGHT_LABEL

GRID_RUNS_COUNT = 2
GRID_MAX_EXTENT = 220
GRID_CHILD_ASPECT = 1.45


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
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
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

        cards_area = ft.Column(
            spacing=S3,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        if stage == BILLED_STAGE:
            pending, completed = sort_faturado_orders(orders)
            if pending:
                cards_area.controls.append(self._section_label("Aguardando confirmação"))
                self._append_card_grid(
                    cards_area,
                    pending,
                    stages,
                    on_move_callback,
                    on_delete_callback,
                    on_details_callback,
                    on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback,
                    is_master=is_master,
                )
            if completed:
                if pending:
                    cards_area.controls.append(ft.Divider(color=colors.BORDER_COLOR, height=1))
                    cards_area.controls.append(self._section_label("Concluídos"))
                self._append_card_grid(
                    cards_area,
                    completed,
                    stages,
                    on_move_callback,
                    on_delete_callback,
                    on_details_callback,
                    on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback,
                    is_master=is_master,
                )
            if not pending and not completed:
                self._append_empty_state(cards_area)
        else:
            if orders:
                self._append_card_grid(
                    cards_area,
                    orders,
                    stages,
                    on_move_callback,
                    on_delete_callback,
                    on_details_callback,
                    on_complete_callback=on_complete_callback,
                    on_history_callback=on_history_callback,
                    is_master=is_master,
                )
            else:
                self._append_empty_state(cards_area)

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
                    cards_area,
                ],
                spacing=S3,
                tight=True,
                expand=True,
            ),
        )

    @staticmethod
    def _section_label(text: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                text,
                size=FONT_CAPTION,
                color=colors.TEXT_MUTED,
                weight=ft.FontWeight.W_600,
            ),
            padding=make_padding_symmetric(horizontal=S2, vertical=S1),
        )

    @staticmethod
    def _append_empty_state(cards_area: ft.Column) -> None:
        cards_area.controls.append(
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
    def _build_card(
        order: dict,
        stages: list,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
    ) -> KanbanCard:
        return KanbanCard(
            order=order,
            stages=stages,
            on_move_callback=on_move_callback,
            on_delete_callback=on_delete_callback,
            on_details_callback=on_details_callback,
            on_complete_callback=on_complete_callback,
            on_history_callback=on_history_callback,
            is_master=is_master,
        )

    @classmethod
    def _append_card_grid(
        cls,
        cards_area: ft.Column,
        orders: list,
        stages: list,
        on_move_callback,
        on_delete_callback,
        on_details_callback,
        *,
        on_complete_callback=None,
        on_history_callback=None,
        is_master: bool = False,
    ) -> None:
        card_controls = [
            cls._build_card(
                order,
                stages,
                on_move_callback,
                on_delete_callback,
                on_details_callback,
                on_complete_callback=on_complete_callback,
                on_history_callback=on_history_callback,
                is_master=is_master,
            )
            for order in orders
        ]

        cards_area.controls.append(
            ft.GridView(
                controls=card_controls,
                runs_count=GRID_RUNS_COUNT,
                max_extent=GRID_MAX_EXTENT,
                child_aspect_ratio=GRID_CHILD_ASPECT,
                spacing=S2,
                run_spacing=S2,
                expand=True,
            )
        )
