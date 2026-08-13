"""
Design system AGA HELP — grid 8px, tipografia e componentes visuais.
"""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import border_all, make_padding_symmetric

# ── Grid 8px ──────────────────────────────────────────────────────────────
S1, S2, S3, S4, S5, S6 = 4, 8, 12, 16, 24, 32

INPUT_HEIGHT = 48
RADIUS = 8
RADIUS_LG = 12
SIDEBAR_WIDTH = 240
SIDEBAR_COLLAPSED = SIDEBAR_WIDTH
SIDEBAR_EXPANDED = SIDEBAR_WIDTH
KANBAN_COL_WIDTH = 296
ORDER_CARD_WIDTH = 272
MAX_CONTENT_WIDTH = 1440

# ── Tipografia (3 níveis) ─────────────────────────────────────────────────
# Nível 1 — Título de seção/página
FONT_TITLE = 15
WEIGHT_TITLE = ft.FontWeight.W_600

# Nível 2 — Rótulo de campo / cabeçalho de card
FONT_LABEL = 12
WEIGHT_LABEL = ft.FontWeight.W_600

# Nível 3 — Conteúdo / corpo
FONT_BODY = 13
FONT_CAPTION = 11
WEIGHT_BODY = ft.FontWeight.W_400

# ── Responsividade ────────────────────────────────────────────────────────
COL_FULL = {"sm": 12, "md": 12, "lg": 12, "xl": 12}
COL_HALF = {"sm": 12, "md": 6, "lg": 6, "xl": 6}
COL_THIRD = {"sm": 12, "md": 6, "lg": 4, "xl": 4}
COL_QUARTER = {"sm": 12, "md": 6, "lg": 3, "xl": 3}
COL_7 = {"sm": 12, "md": 12, "lg": 7, "xl": 7}
COL_5 = {"sm": 12, "md": 12, "lg": 5, "xl": 5}


def text_page_title(value: str) -> ft.Text:
    """Nível 1 — título principal da view."""
    return ft.Text(
        value,
        size=FONT_TITLE,
        weight=WEIGHT_TITLE,
        color=colors.TEXT_PRIMARY,
    )


def text_page_subtitle(value: str) -> ft.Text:
    """Nível 3 — subtítulo descritivo."""
    return ft.Text(
        value,
        size=FONT_BODY,
        weight=WEIGHT_BODY,
        color=colors.TEXT_MUTED,
    )


def text_section_heading(value: str, *, accent: bool = False) -> ft.Text:
    """Nível 2 — cabeçalho dentro de cards/seções."""
    return ft.Text(
        value,
        size=FONT_LABEL,
        weight=WEIGHT_LABEL,
        color=colors.PRIMARY if accent else colors.TEXT_SECONDARY,
    )


def text_body(value: str, **kwargs) -> ft.Text:
    """Nível 3 — texto de conteúdo."""
    defaults = dict(size=FONT_BODY, color=colors.TEXT_PRIMARY, weight=WEIGHT_BODY)
    defaults.update(kwargs)
    return ft.Text(value, **defaults)


def text_caption(value: str, **kwargs) -> ft.Text:
    """Nível 3 — texto secundário pequeno."""
    defaults = dict(size=FONT_CAPTION, color=colors.TEXT_MUTED, weight=WEIGHT_BODY)
    defaults.update(kwargs)
    return ft.Text(value, **defaults)


def page_header(title: str, subtitle: str | None = None) -> ft.Column:
    """Cabeçalho padronizado de view."""
    items = [text_page_title(title)]
    if subtitle:
        items.append(text_page_subtitle(subtitle))
    return ft.Column(items, spacing=S1)


def page_container(content: ft.Control, *, scroll: bool = False) -> ft.Container:
    """Shell de view com padding do grid."""
    return ft.Container(
        padding=make_padding_symmetric(horizontal=S4, vertical=S4),
        expand=True,
        bgcolor=colors.BG_PRIMARY,
        content=content,
    )


def section_card(title: str, content: ft.Control, *, accent: bool = False) -> ft.Container:
    """Card de seção com respiração visual."""
    return ft.Container(
        bgcolor=colors.BG_SURFACE,
        border=border_all(colors.BORDER_COLOR),
        border_radius=RADIUS,
        padding=S4,
        content=ft.Column(
            [
                text_section_heading(title, accent=accent),
                content,
            ],
            spacing=S3,
        ),
    )


def field_style(*, read_only: bool = False) -> dict:
    """Estilo padronizado para TextField."""
    bg = colors.BG_SURFACE if read_only else colors.BG_SURFACE_LIGHT
    text_color = colors.TEXT_SECONDARY if read_only else colors.TEXT_PRIMARY
    label_color = colors.TEXT_MUTED if read_only else colors.TEXT_SECONDARY
    return dict(
        height=INPUT_HEIGHT,
        content_padding=make_padding_symmetric(horizontal=S3, vertical=0),
        border_color=colors.BORDER_COLOR,
        bgcolor=bg,
        border_radius=RADIUS,
        text_style=ft.TextStyle(size=FONT_BODY, color=text_color),
        label_style=ft.TextStyle(size=FONT_LABEL, color=label_color, weight=WEIGHT_LABEL),
        cursor_color=colors.PRIMARY,
        selection_color=colors.PRIMARY,
    )


def dropdown_style(*, read_only: bool = False) -> dict:
    """Estilo padronizado para Dropdown."""
    bg = colors.BG_SURFACE if read_only else colors.BG_SURFACE_LIGHT
    label_color = colors.TEXT_MUTED if read_only else colors.TEXT_SECONDARY
    return dict(
        height=INPUT_HEIGHT,
        content_padding=make_padding_symmetric(horizontal=S3, vertical=0),
        border_color=colors.BORDER_COLOR,
        bgcolor=bg,
        border_radius=RADIUS,
        text_style=ft.TextStyle(size=FONT_BODY, color=colors.TEXT_PRIMARY),
        label_style=ft.TextStyle(size=FONT_LABEL, color=label_color, weight=WEIGHT_LABEL),
        color=colors.TEXT_PRIMARY,
        fill_color=colors.BG_SURFACE_LIGHT,
    )


def primary_button_style() -> ft.ButtonStyle:
    """Botão primário com hover e foco."""
    shape = ft.RoundedRectangleBorder(radius=RADIUS) if hasattr(ft, "RoundedRectangleBorder") else None
    return ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: colors.PRIMARY,
            ft.ControlState.HOVERED: colors.PRIMARY_HOVER,
            ft.ControlState.DISABLED: colors.BG_SURFACE_LIGHT,
        },
        color={
            ft.ControlState.DEFAULT: colors.TEXT_PRIMARY,
            ft.ControlState.DISABLED: colors.TEXT_DISABLED,
        },
        shape=shape,
        padding=make_padding_symmetric(horizontal=S4, vertical=S2),
        elevation=0,
        animation_duration=150,
        mouse_cursor=ft.MouseCursor.CLICK,
    )


def danger_button_style() -> ft.ButtonStyle:
    """Botão de ação destrutiva."""
    shape = ft.RoundedRectangleBorder(radius=RADIUS) if hasattr(ft, "RoundedRectangleBorder") else None
    return ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: colors.ERROR,
            ft.ControlState.HOVERED: "#FF7B72",
        },
        color=colors.TEXT_PRIMARY,
        shape=shape,
        mouse_cursor=ft.MouseCursor.CLICK,
    )


def make_primary_button(content: str, on_click, *, icon=None, height: int = 40) -> ft.Button:
    """Botão primário padronizado."""
    return ft.Button(
        content=content,
        icon=icon,
        height=height,
        style=primary_button_style(),
        on_click=on_click,
    )


def clickable_tile(
    content: ft.Control,
    on_click,
    *,
    padding_h: int = S3,
    padding_v: int = S2,
    radius: int = RADIUS,
) -> ft.Container:
    """Tile clicável com hover e cursor."""
    tile = ft.Container(
        content=content,
        padding=make_padding_symmetric(horizontal=padding_h, vertical=padding_v),
        border_radius=radius,
        bgcolor=colors.BG_SURFACE,
        ink=True,
        on_click=on_click,
        animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
    )

    def on_hover(e):
        tile.bgcolor = colors.BG_HOVER if e.data == "true" else colors.BG_SURFACE
        try:
            tile.update()
        except RuntimeError:
            pass

    tile.on_hover = on_hover
    return tile


def nav_item(
    icon_name: str,
    fallback: str,
    label: ft.Text,
    on_click,
    *,
    active: bool = False,
) -> ft.Container:
    """Item de navegação lateral com microinteração."""
    icon_color = colors.PRIMARY if active else colors.TEXT_SECONDARY
    bg = colors.BG_SURFACE_LIGHT if active else "transparent"

    item = ft.Container(
        content=ft.Row(
            [
                ft.Icon(getattr(ft.Icons, icon_name, None) or fallback, color=icon_color, size=20),
                label,
            ],
            spacing=S3,
        ),
        padding=make_padding_symmetric(horizontal=S3, vertical=S2),
        border_radius=RADIUS,
        bgcolor=bg,
        on_click=on_click,
        animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT) if hasattr(ft, "Animation") else None,
    )

    def on_hover(e):
        if active:
            return
        item.bgcolor = colors.BG_HOVER if e.data == "true" else "transparent"
        try:
            item.update()
        except RuntimeError:
            pass

    item.on_hover = on_hover
    return item


def icon_button(
    icon_name: str,
    fallback: str,
    *,
    color: str,
    tooltip: str,
    on_click,
    size: int = 18,
    disabled: bool = False,
) -> ft.IconButton:
    """IconButton com área de clique confortável."""
    return ft.IconButton(
        icon=getattr(ft.Icons, icon_name, None) or fallback,
        icon_color=color,
        icon_size=size,
        tooltip=tooltip,
        disabled=disabled,
        style=ft.ButtonStyle(
            padding=S2,
            shape=ft.RoundedRectangleBorder(radius=RADIUS) if hasattr(ft, "RoundedRectangleBorder") else None,
            overlay_color=colors.BG_HOVER,
            mouse_cursor=ft.MouseCursor.CLICK,
        ),
        on_click=on_click,
    )


def apply_app_theme(page: ft.Page) -> None:
    """Aplica tema global da aplicação."""
    page.bgcolor = colors.BG_PRIMARY
    page.padding = 0
    page.spacing = 0
    page.theme = ft.Theme(
        color_scheme_seed=colors.PRIMARY,
        scrollbar_theme=ft.ScrollbarTheme(
            thumb_color={
                ft.ControlState.HOVERED: colors.TEXT_SECONDARY,
                ft.ControlState.DEFAULT: colors.TEXT_MUTED,
            },
            thickness=S2,
            radius=S1,
            track_color=colors.BG_SURFACE,
        ),
    )
    if hasattr(ft, "VisualDensity"):
        page.theme = ft.Theme(
            color_scheme_seed=colors.PRIMARY,
            visual_density=ft.VisualDensity.COMFORTABLE,
            scrollbar_theme=page.theme.scrollbar_theme,
        )
    page.theme_mode = ft.ThemeMode.DARK
