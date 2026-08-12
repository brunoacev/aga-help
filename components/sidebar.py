"""Barra lateral de navegação retrátil."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import get_alignment_center, make_padding_symmetric, safe_update
from utils.ui_theme import RADIUS, RADIUS_LG, S1, S2, S3, S4, SIDEBAR_COLLAPSED, SIDEBAR_EXPANDED, icon_button

APP_VERSION = "AGA HELP v1.0"

NAV_SECTIONS: tuple[tuple[str, tuple[tuple[str, str, str, str], ...]], ...] = (
    (
        "PRINCIPAL / OPERACIONAL",
        (
            ("kanban", "Quadro Kanban", "DASHBOARD_ROUNDED", "dashboard"),
            ("add", "Cadastro Pedido", "ADD_BOX_ROUNDED", "add_box"),
        ),
    ),
    (
        "CADASTROS & GESTÃO",
        (
            ("materials", "Materiais", "INVENTORY_2_ROUNDED", "inventory_2"),
            ("agenda", "Agenda de Contatos", "CONTACTS_ROUNDED", "contacts"),
        ),
    ),
    (
        "GESTÃO / OPERACIONAL",
        (
            ("commissions", "Comissões", "PAYMENTS_ROUNDED", "payments"),
        ),
    ),
)


def _border_right(color: str, width: int = 1):
    if hasattr(ft, "Border"):
        return ft.Border(right=ft.BorderSide(width, color))
    return ft.border.only(right=ft.border.BorderSide(width, color))


def _border_left_accent(color: str, width: int = 3):
    if hasattr(ft, "Border"):
        return ft.Border(left=ft.BorderSide(width, color))
    return ft.border.only(left=ft.border.BorderSide(width, color))


class Sidebar(ft.Container):
    """Menu lateral flutuante, colapsável e com indicador de rota ativa."""

    def __init__(self, on_navigate, on_clear_click):
        self.on_navigate = on_navigate
        self.on_clear_click = on_clear_click
        self.active_view = "kanban"
        self.expanded = True
        self._nav_items: dict[str, dict] = {}

        self.txt_brand = ft.Text(
            "Aga-Help",
            weight=ft.FontWeight.W_600,
            size=14,
            color=colors.TEXT_PRIMARY,
        )
        self.btn_toggle = icon_button(
            "CHEVRON_LEFT_ROUNDED",
            "chevron_left",
            color=colors.TEXT_SECONDARY,
            tooltip="Recolher menu",
            on_click=self._toggle_sidebar,
            size=18,
        )

        self.section_labels: list[ft.Text] = []
        self.nav_controls: list[ft.Control] = []
        for section_title, items in NAV_SECTIONS:
            section_label = ft.Text(
                section_title,
                size=10,
                color=colors.TEXT_MUTED,
                weight=ft.FontWeight.W_600,
            )
            self.section_labels.append(section_label)
            self.nav_controls.append(section_label)
            for view_id, label, icon_name, fallback in items:
                self.nav_controls.append(self._build_nav_item(view_id, label, icon_name, fallback))

        self.txt_version = ft.Text(
            APP_VERSION,
            size=10,
            color=colors.TEXT_MUTED,
            weight=ft.FontWeight.W_500,
        )
        self.txt_clear = ft.Text(
            "Limpar Banco",
            size=11,
            color=colors.ERROR,
            weight=ft.FontWeight.W_500,
        )
        self.btn_settings = icon_button(
            "SETTINGS_OUTLINED",
            "settings",
            color=colors.TEXT_SECONDARY,
            tooltip="Auditoria / Logs",
            on_click=lambda _: self.on_navigate("logs"),
            size=18,
        )
        self.btn_clear = icon_button(
            "DELETE_SWEEP_ROUNDED",
            "delete_sweep",
            color=colors.ERROR,
            tooltip="Limpar banco de pedidos",
            on_click=lambda _: self.on_clear_click(),
            size=18,
        )

        self._header_expanded = ft.Row(
            [
                ft.Icon(
                    getattr(ft.Icons, "VIEW_KANBAN_ROUNDED", None) or "view_kanban",
                    color=colors.PRIMARY,
                    size=22,
                ),
                self.txt_brand,
                ft.Container(expand=True),
                self.btn_toggle,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._header_collapsed = ft.Container(
            content=ft.Icon(
                getattr(ft.Icons, "VIEW_KANBAN_ROUNDED", None) or "view_kanban",
                color=colors.PRIMARY,
                size=20,
            ),
            alignment=get_alignment_center(),
            tooltip="Expandir menu",
            on_click=self._toggle_sidebar,
        )

        self.footer_expanded = ft.Container(
            content=ft.Column(
                [
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    ft.Row(
                        [self.btn_settings, self.txt_version],
                        spacing=S2,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [self.btn_clear, self.txt_clear],
                        spacing=S2,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=S2,
                tight=True,
            ),
        )
        self.footer_collapsed = ft.Container(
            content=ft.Column(
                [
                    ft.Container(content=self.btn_toggle, alignment=get_alignment_center()),
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    self.btn_settings,
                    self.btn_clear,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=S2,
                tight=True,
            ),
            alignment=get_alignment_center(),
        )

        self._body_column = ft.Column(
            [
                self._header_expanded,
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                ft.Column(self.nav_controls, spacing=S1, expand=True, scroll=ft.ScrollMode.AUTO),
                self.footer_expanded,
            ],
            spacing=S3,
            expand=True,
        )

        super().__init__(
            width=SIDEBAR_EXPANDED,
            bgcolor=colors.BG_SURFACE,
            border=_border_right(colors.BORDER_COLOR),
            border_radius=RADIUS_LG,
            padding=make_padding_symmetric(horizontal=S3, vertical=S4),
            margin=make_padding_symmetric(horizontal=S3, vertical=S3),
            animate=ft.Animation(220, ft.AnimationCurve.EASE_IN_OUT) if hasattr(ft, "Animation") else None,
            content=self._body_column,
        )
        self.set_active("kanban")
        self._apply_layout()

    def _build_nav_item(self, view_id: str, label: str, icon_name: str, fallback: str) -> ft.Container:
        icon = ft.Icon(
            getattr(ft.Icons, icon_name, None) or fallback,
            color=colors.TEXT_SECONDARY,
            size=20,
        )
        label_text = ft.Text(
            label,
            size=12,
            color=colors.TEXT_SECONDARY,
            weight=ft.FontWeight.W_500,
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
        self._nav_items[view_id] = {
            "container": container,
            "icon": icon,
            "label": label_text,
            "title": label,
        }
        return container

    def _update_toggle_button(self) -> None:
        if self.expanded:
            self.btn_toggle.icon = getattr(ft.Icons, "CHEVRON_LEFT_ROUNDED", None) or "chevron_left"
            self.btn_toggle.tooltip = "Recolher menu"
        else:
            self.btn_toggle.icon = getattr(ft.Icons, "CHEVRON_RIGHT_ROUNDED", None) or "chevron_right"
            self.btn_toggle.tooltip = "Expandir menu"

    def _apply_layout(self) -> None:
        self.width = SIDEBAR_EXPANDED if self.expanded else SIDEBAR_COLLAPSED
        self.padding = make_padding_symmetric(
            horizontal=S3 if self.expanded else S2,
            vertical=S4,
        )
        self.txt_brand.visible = self.expanded
        self._update_toggle_button()
        self._body_column.controls[0] = self._header_expanded if self.expanded else self._header_collapsed

        for section_label in self.section_labels:
            section_label.visible = self.expanded

        for item in self._nav_items.values():
            item["label"].visible = self.expanded
            item["container"].tooltip = None if self.expanded else item["title"]
            if self.expanded:
                item["container"].content = ft.Row(
                    [item["icon"], item["label"]],
                    spacing=S3,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            else:
                item["container"].content = ft.Container(
                    content=item["icon"],
                    alignment=get_alignment_center(),
                    width=40,
                )

        self._body_column.controls[-1] = self.footer_expanded if self.expanded else self.footer_collapsed
        self.txt_clear.visible = self.expanded
        self.txt_version.visible = self.expanded
        self._refresh_active_styles()

    def _toggle_sidebar(self, _e) -> None:
        self.expanded = not self.expanded
        self._apply_layout()
        safe_update(self)

    def _refresh_active_styles(self) -> None:
        for view_id, item in self._nav_items.items():
            is_active = view_id == self.active_view
            container = item["container"]
            item["icon"].color = colors.PRIMARY if is_active else colors.TEXT_SECONDARY
            item["label"].color = colors.PRIMARY if is_active else colors.TEXT_SECONDARY
            item["label"].weight = ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500

            if is_active:
                container.bgcolor = colors.BG_SURFACE_LIGHT
                container.border = _border_left_accent(colors.PRIMARY)
            else:
                container.bgcolor = "transparent"
                container.border = None

    def set_active(self, view_name: str) -> None:
        self.active_view = view_name
        self._refresh_active_styles()
        safe_update(self)
