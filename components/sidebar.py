"""Barra lateral de navegação."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import make_padding_symmetric, safe_update
from utils.ui_theme import S2, S3, S4, SIDEBAR_COLLAPSED, SIDEBAR_EXPANDED, nav_item


class Sidebar(ft.Container):
    """Menu lateral com navegação entre módulos."""

    def __init__(self, on_navigate, on_clear_click):
        self.on_navigate = on_navigate
        self.on_clear_click = on_clear_click
        self.active_view = "kanban"

        if hasattr(ft, "Border"):
            border_right = ft.Border(right=ft.BorderSide(1, colors.BORDER_COLOR))
        else:
            border_right = None

        self.txt_title = ft.Text(
            "Aga-Help",
            weight=ft.FontWeight.W_600,
            size=14,
            color=colors.TEXT_PRIMARY,
            visible=False,
        )

        nav_items = [
            ("kanban", "Quadro Kanban", "DASHBOARD_ROUNDED", "dashboard"),
            ("add", "Cadastro Pedido", "ADD_BOX_ROUNDED", "add"),
            ("agenda", "Ações Agenda", "CONTACTS_ROUNDED", "contacts"),
            ("materials", "Materiais", "INVENTORY_2_ROUNDED", "inventory"),
            ("logs", "Auditoria", "HISTORY_ROUNDED", "history"),
        ]

        self.nav_buttons: dict[str, ft.Container] = {}
        self.nav_texts: dict[str, ft.Text] = {}
        nav_controls = []

        for view_id, label, icon_name, fallback in nav_items:
            txt = ft.Text(
                label,
                size=12,
                color=colors.TEXT_PRIMARY,
                visible=False,
                weight=ft.FontWeight.W_500,
            )
            btn = nav_item(
                icon_name,
                fallback,
                txt,
                lambda _, v=view_id: self.on_navigate(v),
                active=view_id == "kanban",
            )
            self.nav_buttons[view_id] = btn
            self.nav_texts[view_id] = txt
            nav_controls.append(btn)

        self.txt_clear = ft.Text(
            "Limpar Banco",
            size=12,
            color=colors.ERROR,
            visible=False,
            weight=ft.FontWeight.W_500,
        )
        self.btn_clear = nav_item(
            "DELETE_SWEEP_ROUNDED",
            "delete_sweep",
            self.txt_clear,
            lambda _: self.on_clear_click(),
        )
        self.btn_clear.content.controls[0].color = colors.ERROR

        super().__init__(
            width=SIDEBAR_COLLAPSED,
            bgcolor=colors.BG_SURFACE,
            border=border_right,
            padding=make_padding_symmetric(horizontal=S2, vertical=S4),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT) if hasattr(ft, "Animation") else None,
            on_hover=self._handle_hover,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                getattr(ft.Icons, "VIEW_KANBAN_ROUNDED", None) or "view_kanban",
                                color=colors.PRIMARY,
                                size=24,
                            ),
                            self.txt_title,
                        ],
                        spacing=S3,
                    ),
                    ft.Divider(color=colors.BORDER_COLOR, height=S4),
                    ft.Column(nav_controls, spacing=S2, expand=True),
                    self.btn_clear,
                ],
                spacing=S3,
            ),
        )

    def set_active(self, view_name: str) -> None:
        self.active_view = view_name
        for view_id, btn in self.nav_buttons.items():
            is_active = view_id == view_name
            btn.bgcolor = colors.BG_SURFACE_LIGHT if is_active else "transparent"
            btn.content.controls[0].color = colors.PRIMARY if is_active else colors.TEXT_SECONDARY
        safe_update(self)

    def _handle_hover(self, e) -> None:
        is_hovered = e.data == "true"
        self.width = SIDEBAR_EXPANDED if is_hovered else SIDEBAR_COLLAPSED
        self.txt_title.visible = is_hovered
        for txt in self.nav_texts.values():
            txt.visible = is_hovered
        self.txt_clear.visible = is_hovered
        safe_update(self)
