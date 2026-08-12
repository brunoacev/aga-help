"""View do quadro Kanban."""

from __future__ import annotations

import flet as ft

from core import colors
from core.services.order_service import delete_order, get_orders, update_order_status
from components.kanban_column import KanbanColumn
from utils.flet_compat import confirm_dialog, safe_update
from utils.ui_theme import S3, S4, page_container, page_header


class KanbanView(ft.Container):
    """Gerencia renderização e ações do quadro Kanban."""

    def __init__(self, page: ft.Page, stages: list[str], stage_colors: dict[str, str]):
        self.app_page = page
        self.stages = stages
        self.stage_colors = stage_colors
        super().__init__(expand=True, bgcolor=colors.BG_PRIMARY)
        self.refresh()

    def refresh(self) -> None:
        orders = get_orders()
        kanban_row = ft.Row(
            spacing=S3,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            wrap=False,
        )

        for stage in self.stages:
            stage_orders = [o for o in orders if o.get("status") == stage]
            kanban_row.controls.append(
                KanbanColumn(
                    stage=stage,
                    orders=stage_orders,
                    stage_color=self.stage_colors[stage],
                    stages=self.stages,
                    on_move_callback=self._move_order,
                    on_delete_callback=self._confirm_delete,
                )
            )

        self.content = page_container(
            ft.Column(
                [
                    page_header(
                        "Acompanhamento de Pedidos",
                        "Arraste mentalmente entre colunas usando as setas de cada card.",
                    ),
                    ft.Container(content=kanban_row, expand=True),
                ],
                spacing=S4,
                expand=True,
            ),
            scroll=False,
        )
        safe_update(self, self.app_page)

    def _move_order(self, order_id: int, new_stage: str) -> None:
        update_order_status(order_id, new_stage)
        self.refresh()

    def _confirm_delete(self, order_id: int) -> None:
        confirm_dialog(
            self.app_page,
            "Excluir pedido",
            "Deseja realmente excluir este pedido? Esta ação não pode ser desfeita.",
            on_confirm=lambda: self._delete_order(order_id),
            confirm_text="Excluir",
        )

    def _delete_order(self, order_id: int) -> None:
        delete_order(order_id)
        self.refresh()
