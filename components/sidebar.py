"""Barra lateral com ícones e rótulos — layout dashboard clássico."""

from __future__ import annotations

import flet as ft

from core import colors
from core.auth.user_session import get_user_handle
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric, safe_update
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S1, S2, S3, S4, icon_button

SIDEBAR_WIDTH = 240
NAV_ICON_SIZE = 20
BRAND_ICON_SIZE = 22

NAV_ITEMS: tuple[tuple[str, str, str, str], ...] = (
    ("kanban", "Produção", "VIEW_KANBAN_ROUNDED", "view_kanban"),
    ("add", "Novo Pedido", "ADD_SHOPPING_CART_ROUNDED", "add_shopping_cart"),
    ("whatsapp", "WhatsApp", "CHAT_BUBBLE_ROUNDED", "chat_bubble"),
    ("commissions", "Comissões", "SAVINGS_ROUNDED", "savings"),
    ("materials", "Materiais", "INVENTORY_2_ROUNDED", "inventory_2"),
    ("agenda", "Agenda", "CONTACTS_ROUNDED", "contacts"),
)

ACTIVE_BG = colors.BG_SURFACE_LIGHT


def _border_right(color: str, width: int = 1):
    if hasattr(ft, "Border"):
        return ft.Border(right=ft.BorderSide(width, color))
    return ft.border.only(right=ft.border.BorderSide(width, color))


def _resolve_icon(icon_name: str, fallback: str):
    return getattr(ft.Icons, icon_name, None) or fallback


class Sidebar(ft.Container):
    """Menu lateral fixo: marca no topo, navegação com nomes e perfil no rodapé."""

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

        brand_icon = ft.Container(
            content=ft.Icon(
                _resolve_icon("VIEW_KANBAN_ROUNDED", "view_kanban"),
                color=colors.PRIMARY,
                size=BRAND_ICON_SIZE,
            ),
            width=40,
            height=40,
            alignment=get_alignment_center(),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border_radius=RADIUS,
        )
        brand_header = ft.Row(
            [
                brand_icon,
                ft.Column(
                    [
                        ft.Text(
                            "AGA HELP",
                            size=14,
                            weight=ft.FontWeight.W_700,
                            color=colors.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Sistema Agatek",
                            size=FONT_CAPTION,
                            color=colors.TEXT_MUTED,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                    tight=True,
                ),
            ],
            spacing=S3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        nav_controls: list[ft.Control] = []
        for view_id, label, icon_name, fallback in NAV_ITEMS:
            nav_controls.append(self._build_nav_item(view_id, label, icon_name, fallback))

        handle = get_user_handle(page) or "@?"
        avatar_letter = (handle.replace("@", "")[:1] or "?").upper()

        self.user_avatar = ft.Container(
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
            border=border_all(colors.BORDER_COLOR),
            border_radius=18,
        )
        self.user_name_label = ft.Text(
            handle,
            size=FONT_BODY,
            weight=ft.FontWeight.W_600,
            color=colors.TEXT_PRIMARY,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.user_role_label = ft.Text(
            "Operador",
            size=FONT_CAPTION,
            color=colors.TEXT_MUTED,
        )

        self.btn_logs = icon_button(
            "DESCRIPTION_OUTLINED",
            "description",
            color=colors.TEXT_SECONDARY,
            tooltip="Logs",
            on_click=lambda _: self.on_navigate("logs"),
            size=18,
        )
        self.btn_clear = icon_button(
            "DELETE_SWEEP_ROUNDED",
            "delete_sweep",
            color=colors.ERROR,
            tooltip="Limpar pedidos",
            on_click=lambda _: self.on_clear_click(),
            size=18,
        )
        self.btn_logout = icon_button(
            "LOGOUT_ROUNDED",
            "logout",
            color=colors.TEXT_SECONDARY,
            tooltip="Sair",
            on_click=lambda _: self._handle_logout(),
            size=18,
        )

        user_footer = ft.Container(
            bgcolor=colors.BG_SURFACE_LIGHT,
            border_radius=RADIUS,
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            content=ft.Row(
                [
                    self.user_avatar,
                    ft.Column(
                        [self.user_name_label, self.user_role_label],
                        spacing=2,
                        expand=True,
                        tight=True,
                    ),
                    ft.Row(
                        [self.btn_logs, self.btn_clear, self.btn_logout],
                        spacing=0,
                        tight=True,
                    ),
                ],
                spacing=S3,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        body = ft.Column(
            [
                brand_header,
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                ft.Column(
                    nav_controls,
                    spacing=S1,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                user_footer,
            ],
            spacing=S3,
            expand=True,
        )

        super().__init__(
            width=SIDEBAR_WIDTH,
            bgcolor=colors.BG_SURFACE,
            border=_border_right(colors.BORDER_COLOR),
            padding=make_padding_symmetric(horizontal=S3, vertical=S4),
            content=body,
        )
        self.set_active("kanban")

    def _build_nav_item(self, view_id: str, label: str, icon_name: str, fallback: str) -> ft.Container:
        icon = ft.Icon(
            _resolve_icon(icon_name, fallback),
            color=colors.TEXT_SECONDARY,
            size=NAV_ICON_SIZE,
        )
        label_text = ft.Text(
            label,
            size=FONT_BODY,
            color=colors.TEXT_SECONDARY,
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        container = ft.Container(
            content=ft.Row(
                [icon, label_text],
                spacing=S3,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            border_radius=RADIUS,
            bgcolor="transparent",
            on_click=lambda _: self.on_navigate(view_id),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
        )

        def on_hover(e):
            if view_id == self.active_view:
                return
            container.bgcolor = colors.BG_HOVER if e.data == "true" else "transparent"
            safe_update(container)

        container.on_hover = on_hover
        self._nav_items[view_id] = {"container": container, "icon": icon, "label": label_text}
        return container

    def _handle_logout(self) -> None:
        if self.on_logout:
            self.on_logout()

    def _refresh_active_styles(self) -> None:
        for view_id, item in self._nav_items.items():
            is_active = view_id == self.active_view
            container = item["container"]
            icon = item["icon"]
            label = item["label"]
            if is_active:
                container.bgcolor = ACTIVE_BG
                icon.color = colors.PRIMARY
                label.color = colors.TEXT_PRIMARY
                label.weight = ft.FontWeight.W_600
            else:
                container.bgcolor = "transparent"
                icon.color = colors.TEXT_SECONDARY
                label.color = colors.TEXT_SECONDARY
                label.weight = ft.FontWeight.W_400

    def set_active(self, view_name: str) -> None:
        self.active_view = view_name
        self._refresh_active_styles()
        safe_update(self)

    def refresh_user_badge(self) -> None:
        handle = get_user_handle(self.app_page) or "@?"
        avatar_letter = (handle.replace("@", "")[:1] or "?").upper()
        self.user_avatar.content = ft.Text(
            avatar_letter,
            size=13,
            weight=ft.FontWeight.W_700,
            color=colors.PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )
        self.user_name_label.value = handle
        safe_update(self)
