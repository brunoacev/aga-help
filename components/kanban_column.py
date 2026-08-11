import flet as ft
from core import colors
from components.order_card import OrderCard

class KanbanColumn(ft.Container):
    def __init__(self, stage: str, orders: list, stage_color: str, stages: list, on_move_callback, on_delete_callback):
        self.stage = stage
        self.orders = orders
        self.stage_color = stage_color
        self.stages = stages
        self.on_move_callback = on_move_callback
        self.on_delete_callback = on_delete_callback

        header = ft.Row([
            ft.Row([
                ft.Container(width=10, height=10, border_radius=5, bgcolor=stage_color),
                ft.Text(stage, weight=ft.FontWeight.BOLD, size=12, color=colors.TEXT_PRIMARY),
            ], spacing=6),
            ft.Container(
                content=ft.Text(str(len(orders)), size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY),
                bgcolor=colors.BG_SURFACE_LIGHT,
                padding=ft.Padding(6, 2, 6, 2) if hasattr(ft, "Padding") else None,
                border_radius=8
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        cards_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        for order in orders:
            card = OrderCard(
                order=order,
                stages=stages,
                on_move_callback=on_move_callback,
                on_delete_callback=on_delete_callback
            )
            cards_list.controls.append(card)

        border_col = ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else None

        super().__init__(
            width=280, # LARGURA PADRONIZADA DAS COLUNAS DO KANBAN
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_col,
            border_radius=8,
            padding=10,
            content=ft.Column([
                header,
                ft.Divider(color=colors.BORDER_COLOR, height=6),
                cards_list
            ], spacing=6, expand=True)
        )