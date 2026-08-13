"""Barra lateral minimalista — navegação por ícones expressivos."""

from __future__ import annotations

import flet as ft

from core import colors
from core.auth.user_session import get_user_handle
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric, safe_update
from utils.ui_theme import RADIUS, RADIUS_LG, S2, S3, icon_button

SIDEBAR_WIDTH = 76
NAV_ICON_SIZE = 30
FOOTER_ICON_SIZE = 22
ACTIVE_PILL_SIZE = 48

NAV_ITEMS: tuple[tuple[str, str, str, str], ...] = (
    ("add", "Novo Pedido", "ADD_SHOPPING_CART_ROUNDED", "add_shopping_cart"),
    ("kanban", "Fluxo de Produção", "VIEW_KANBAN_ROUNDED", "view_kanban"),
    ("whatsapp", "WhatsApp / Conversas", "CHAT_BUBBLE_ROUNDED", "chat_bubble"),
    ("commissions", "Desempenho & Comissões", "SAVINGS_ROUNDED", "savings"),
    ("materials", "Catálogo de Materiais", "INVENTORY_2_ROUNDED", "inventory_2"),
    ("agenda", "Agenda de Contatos", "CONTACTS_ROUNDED", "contacts"),
)

ACTIVE_BG = "#58A6FF22"


def _border_right(color: str, width: int = 1):
    if hasattr(ft, "Border"):
        return ft.Border(right=ft.BorderSide(width, color))
    return ft.border.only(right=ft.border.BorderSide(width, color))


def _resolve_icon(icon_name: str, fallback: str):
    return getattr(ft.Icons, icon_name, None) or fallback


class Sidebar(ft.Container):
    """Menu lateral fino com ícones centralizados, tooltips e indicador ativo."""

    def __init__(
        self,
        on_navigate,
        on_clear_click,
        *,
        page: ft.Page | None = None,
        on_logout=None,
    ):
        self.on_navigate = on_navigate
        self.on_clear_click = on_clear_click
        self.app_page = page
        self.on_logout = on_logout
        self.active_view = "kanban"
        self._nav_items: dict[str, dict] = {}

        self._brand_icon = ft.Container(
            content=ft.Icon(
                _resolve_icon("VIEW_KANBAN_ROUNDED", "view_kanban"),
                color=colors.PRIMARY,
                size=26,
            ),
            width=ACTIVE_PILL_SIZE,
            height=ACTIVE_PILL_SIZE,
            alignment=get_alignment_center(),
            tooltip="AGA HELP",
        )

        nav_controls: list[ft.Control] = []
        for index, (view_id, label, icon_name, fallback) in enumerate(NAV_ITEMS):
            if index == 3:
                nav_controls.append(ft.Divider(height=1, color=colors.BORDER_COLOR))
            nav_controls.append(self._build_nav_item(view_id, label, icon_name, fallback))

        handle = get_user_handle(page) or "@?"
        handle_short = handle if len(handle) <= 10 else f"{handle[:8]}…"
        avatar_letter = (handle.replace("@", "")[:1] or "?").upper()

        self.user_badge = ft.Container(
            content=ft.Text(
                avatar_letter,
                size=13,
                weight=ft.FontWeight.W_700,
                color=colors.PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
            width=36,
            height=36,
            alignment=get_alignment_center(),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.PRIMARY),
            border_radius=18,
            tooltip=handle,
        )
        self.user_handle_label = ft.Text(
            handle_short,
            size=9,
            color=colors.TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.btn_logs = icon_button(
            "DESCRIPTION_OUTLINED",
            "description",
            color=colors.TEXT_SECONDARY,
            tooltip="Auditoria / Logs",
            on_click=lambda _: self.on_navigate("logs"),
            size=FOOTER_ICON_SIZE,
        )
        self.btn_clear = icon_button(
            "DELETE_SWEEP_ROUNDED",
            "delete_sweep",
            color=colors.ERROR,
            tooltip="Limpar banco de pedidos",
            on_click=lambda _: self.on_clear_click(),
            size=FOOTER_ICON_SIZE,
        )
        self.btn_logout = icon_button(
            "LOGOUT_ROUNDED",
            "logout",
            color=colors.TEXT_SECONDARY,
            tooltip="Sair",
            on_click=lambda _: self._handle_logout(),
            size=FOOTER_ICON_SIZE,
        )

        footer = ft.Column(
            [
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                self.user_badge,
                self.user_handle_label,
                ft.Row(
                    [self.btn_logs, self.btn_clear, self.btn_logout],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=S2,
            tight=True,
        )

        body = ft.Column(
            [
                ft.Container(content=self._brand_icon, alignment=get_alignment_center()),
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                ft.Column(
                    nav_controls,
                    spacing=S2,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                footer,
            ],
            spacing=S3,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        super().__init__(
            width=SIDEBAR_WIDTH,
            bgcolor=colors.BG_SURFACE,
            border=_border_right(colors.BORDER_COLOR),
            border_radius=RADIUS_LG,
            padding=make_padding_symmetric(horizontal=S2, vertical=S3),
            margin=make_padding_symmetric(horizontal=S2, vertical=S2),
            content=body,
        )
        self.set_active("kanban")

    def _build_nav_item(self, view_id: str, label: str, icon_name: str, fallback: str) -> ft.Container:
        icon = ft.Icon(
            _resolve_icon(icon_name, fallback),
            color=colors.TEXT_SECONDARY,
            size=NAV_ICON_SIZE,
        )
        container = ft.Container(
            content=icon,
            width=ACTIVE_PILL_SIZE,
            height=ACTIVE_PILL_SIZE,
            alignment=get_alignment_center(),
            border_radius=ACTIVE_PILL_SIZE // 2,
            bgcolor="transparent",
            tooltip=label,
            on_click=lambda _: self.on_navigate(view_id),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
        )

        def on_hover(e):
            if view_id == self.active_view:
                return
            container.bgcolor = colors.BG_HOVER if e.data == "true" else "transparent"
            safe_update(container)

        container.on_hover = on_hover
        self._nav_items[view_id] = {"container": container, "icon": icon}
        return container

    def _handle_logout(self) -> None:
        if self.on_logout:
            self.on_logout()

    def _refresh_active_styles(self) -> None:
        for view_id, item in self._nav_items.items():
            is_active = view_id == self.active_view
            container = item["container"]
            icon = item["icon"]
            if is_active:
                container.bgcolor = ACTIVE_BG
                icon.color = colors.PRIMARY
            else:
                container.bgcolor = "transparent"
                icon.color = colors.TEXT_SECONDARY

    def set_active(self, view_name: str) -> None:
        self.active_view = view_name
        self._refresh_active_styles()
        safe_update(self)

    def refresh_user_badge(self) -> None:
        handle = get_user_handle(self.app_page) or "@?"
        handle_short = handle if len(handle) <= 10 else f"{handle[:8]}…"
        avatar_letter = (handle.replace("@", "")[:1] or "?").upper()
        self.user_badge.content = ft.Text(
            avatar_letter,
            size=13,
            weight=ft.FontWeight.W_700,
            color=colors.PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )
        self.user_badge.tooltip = handle
        self.user_handle_label.value = handle_short
        safe_update(self)
