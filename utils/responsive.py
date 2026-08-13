"""Helpers de layout responsivo."""

from __future__ import annotations

import flet as ft

COMPACT_BREAKPOINT = 720
TABLET_BREAKPOINT = 1050
KANBAN_COLUMN_MIN_WIDTH = 260
KANBAN_STACK_COLUMN_HEIGHT = 300


def page_width(page: ft.Page | None) -> int:
    if not page:
        return TABLET_BREAKPOINT + 1
    if hasattr(page, "window") and page.window and page.window.width:
        return int(page.window.width or 0)
    return int(getattr(page, "width", None) or TABLET_BREAKPOINT + 1)


def kanban_layout_mode(page: ft.Page | None) -> str:
    """
    Retorna modo de layout do Kanban:
    - row: 3 colunas lado a lado (telas largas)
    - scroll: colunas com scroll horizontal (telas médias)
    - stack: colunas empilhadas verticalmente (telas pequenas)
    """
    width = page_width(page)
    if width < COMPACT_BREAKPOINT:
        return "stack"
    if width < TABLET_BREAKPOINT:
        return "scroll"
    return "row"


def is_compact_ui(page: ft.Page | None) -> bool:
    return kanban_layout_mode(page) != "row"
