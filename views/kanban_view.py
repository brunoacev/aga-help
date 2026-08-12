"""View do quadro Kanban."""

from __future__ import annotations

import flet as ft

from core import colors
from core.services.order_service import delete_order, get_orders, update_order_status
from components.kanban_column import KanbanColumn
from components.order_details_dialog import show_order_items_dialog
from utils.flet_compat import confirm_dialog
from utils.ui_theme import S4, page_container, page_header


class KanbanView(ft.Container):
    """Gerencia renderização e ações do quadro Kanban."""

    def __init__(
        self,
        page: ft.Page,
        stages: list[str],
        stage_colors: dict[str, str],
        *,
        on_orders_changed=None,
    ):
        self.app_page = page
        self.stages = stages
        self.stage_colors = stage_colors
        self.on_orders_changed = on_orders_changed
        super().__init__(expand=True, bgcolor=colors.BG_PRIMARY)
        self.refresh()

    def _notify_orders_changed(self) -> None:
        if self.on_orders_changed:
            self.on_orders_changed()

    def refresh(self) -> None:
        orders = get_orders()
        kanban_row = ft.Row(
            spacing=S4,
            expand=True,
            wrap=False,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
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
                    on_details_callback=self._show_order_details,
                    expand=True,
                )
            )

        self.content = page_container(
            ft.Column(
                [
                    page_header(
                        "Acompanhamento de Pedidos",
                        "Arraste mentalmente entre colunas usando as setas de cada card.",
                    ),
                    kanban_row,
                ],
                spacing=S4,
                tight=True,
                expand=True,
            ),
            scroll=False,
        )
        if self.app_page:
            self.app_page.update()

    def _move_order(self, order_id: int, new_stage: str) -> None:
        update_order_status(order_id, new_stage)
        self.refresh()
        self._notify_orders_changed()

    def _show_order_details(self, order: dict) -> None:
        show_order_items_dialog(self.app_page, order)

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
        self._notify_orders_changed()
