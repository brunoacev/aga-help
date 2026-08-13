"""View do quadro Kanban — 3 colunas responsivas."""

from __future__ import annotations

import flet as ft

from controllers.order_billing_controller import (
    can_delete_order,
    can_move_order,
    can_view_order_details,
)
from core import colors
from core.kanban_stages import normalize_order_status
from core.services.order_service import complete_order_billing, delete_order, get_orders, update_order_status
from components.kanban_column import KanbanColumn
from components.order_details_dialog import show_order_items_dialog
from components.order_history_dialog import show_order_history_dialog
from core.auth.user_session import get_user_handle
from utils.flet_compat import confirm_dialog, show_snackbar
from utils.responsive import (
    KANBAN_COLUMN_MIN_WIDTH,
    KANBAN_STACK_COLUMN_HEIGHT,
    kanban_layout_mode,
)
from utils.ui_theme import S2, S4, page_container, page_header


class KanbanView(ft.Container):
    """Gerencia renderização e ações do quadro Kanban."""

    def __init__(
        self,
        page: ft.Page,
        stages: list[str],
        stage_colors: dict[str, str],
        *,
        on_orders_changed=None,
        is_master: bool = False,
    ):
        self.app_page = page
        self.stages = list(stages)
        self.stage_colors = stage_colors
        self.on_orders_changed = on_orders_changed
        self.is_master = is_master
        self._layout_mode: str | None = None
        self._resize_handler = None
        super().__init__(expand=True, bgcolor=colors.BG_PRIMARY)
        self._attach_resize_listener()
        self.refresh()

    def _attach_resize_listener(self) -> None:
        def _on_resize(_e) -> None:
            mode = kanban_layout_mode(self.app_page)
            if mode != self._layout_mode:
                self.refresh()

        self._resize_handler = _on_resize
        if hasattr(self.app_page, "on_resize"):
            previous = getattr(self.app_page, "on_resize", None)
            if previous and previous is not _on_resize:

                def _chained(e):
                    previous(e)
                    _on_resize(e)

                self.app_page.on_resize = _chained
            else:
                self.app_page.on_resize = _on_resize
        elif hasattr(self.app_page, "window") and hasattr(self.app_page.window, "on_resize"):
            self.app_page.window.on_resize = _on_resize

    def _find_order(self, order_id: int) -> dict | None:
        return next((order for order in get_orders() if order.get("id") == order_id), None)

    def _notify_orders_changed(self) -> None:
        if self.on_orders_changed:
            self.on_orders_changed()

    def _make_column(self, stage: str, orders: list[dict], *, compact: bool) -> KanbanColumn:
        stage_orders = [o for o in orders if normalize_order_status(o.get("status")) == stage]
        return KanbanColumn(
            stage=stage,
            orders=stage_orders,
            stage_color=self.stage_colors[stage],
            stages=self.stages,
            on_move_callback=self._move_order,
            on_delete_callback=self._confirm_delete,
            on_details_callback=self._show_order_details,
            on_complete_callback=self._complete_billing,
            on_history_callback=self._show_order_history,
            is_master=self.is_master,
            compact=compact,
            expand=True,
        )

    def _build_board(self, orders: list[dict], mode: str, compact: bool) -> ft.Control:
        columns = [
            self._make_column(
                stage,
                [o for o in orders if normalize_order_status(o.get("status")) == stage],
                compact=compact,
            )
            for stage in self.stages
        ]

        if mode == "stack":
            stacked: list[ft.Control] = []
            for column in columns:
                stacked.append(
                    ft.Container(
                        content=column,
                        height=KANBAN_STACK_COLUMN_HEIGHT,
                        expand=False,
                    )
                )
            return ft.Column(
                stacked,
                spacing=S2,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

        if mode == "scroll":
            for column in columns:
                column.width = KANBAN_COLUMN_MIN_WIDTH
            return ft.Row(
                columns,
                spacing=S2,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )

        return ft.Row(
            columns,
            spacing=S4,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def refresh(self) -> None:
        orders = get_orders()
        mode = kanban_layout_mode(self.app_page)
        self._layout_mode = mode
        compact = mode != "row"
        board = self._build_board(orders, mode, compact)

        subtitle = {
            "row": "Produção → Pronto → Faturado. Novos pedidos entram em Produção.",
            "scroll": "Deslize horizontalmente para ver todas as etapas.",
            "stack": "Etapas empilhadas — role para navegar entre colunas.",
        }[mode]

        self.content = page_container(
            ft.Column(
                [
                    page_header("Fluxo de Produção", subtitle),
                    board,
                ],
                spacing=S2 if compact else S4,
                tight=True,
                expand=True,
            ),
            scroll=False,
        )
        if self.app_page:
            self.app_page.update()

    def _move_order(self, order_id: int, new_stage: str) -> None:
        order = self._find_order(order_id)
        if order and not can_move_order(order, is_master=self.is_master):
            show_snackbar(
                self.app_page,
                "Pedido concluído no faturamento. Apenas administradores podem alterá-lo.",
                success=False,
            )
            return
        old_status = normalize_order_status(order.get("status") if order else "")
        handle = get_user_handle(self.app_page)
        try:
            update_order_status(order_id, new_stage, user_handle=handle, old_status=old_status)
        except ValueError as exc:
            show_snackbar(self.app_page, str(exc), success=False)
            return
        self.refresh()
        self._notify_orders_changed()

    def _complete_billing(self, order_id: int) -> None:
        order = self._find_order(order_id)
        if not order:
            return
        handle = get_user_handle(self.app_page)
        complete_order_billing(order_id, user_handle=handle)
        self.refresh()
        self._notify_orders_changed()
        show_snackbar(self.app_page, "Faturamento concluído com sucesso!", success=True)

    def _show_order_details(self, order: dict) -> None:
        if not can_view_order_details(order, is_master=self.is_master):
            show_snackbar(
                self.app_page,
                "Pedido concluído no faturamento. Detalhes bloqueados para usuários comuns.",
                success=False,
            )
            return
        show_order_items_dialog(self.app_page, order)

    def _show_order_history(self, order: dict) -> None:
        show_order_history_dialog(self.app_page, order)

    def _confirm_delete(self, order_id: int) -> None:
        order = self._find_order(order_id)
        if order and not can_delete_order(order, is_master=self.is_master):
            show_snackbar(
                self.app_page,
                "Pedido concluído no faturamento. Exclusão bloqueada para usuários comuns.",
                success=False,
            )
            return
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
