"""Compatibilidade entre versões do Flet e helpers de layout."""

from __future__ import annotations

import flet as ft


def make_padding_symmetric(horizontal: int = 0, vertical: int = 0):
    """Padding simétrico compatível com Flet antigo e novo."""
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    if hasattr(ft, "padding") and hasattr(ft.padding, "symmetric"):
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.only(
        left=horizontal, right=horizontal, top=vertical, bottom=vertical
    )


def get_alignment_center():
    """Retorna alinhamento central compatível."""
    if hasattr(ft, "Alignment"):
        return ft.Alignment(0, 0)
    if hasattr(ft, "alignment") and hasattr(ft.alignment, "CENTER"):
        return ft.alignment.CENTER
    return "center"


def border_all(color: str, width: int = 1):
    """Borda uniforme compatível."""
    if hasattr(ft, "Border"):
        return ft.Border.all(width, color)
    return ft.border.all(width, color)


def make_button(text: str, on_click, *, icon=None, bgcolor=None, color=None, style=None):
    """Botão primário compatível entre versões do Flet."""
    kwargs = {"on_click": on_click}
    if hasattr(ft, "Button"):
        kwargs["content"] = text
    else:
        kwargs["text"] = text
    if icon is not None:
        kwargs["icon"] = icon
    if style is not None:
        kwargs["style"] = style
    elif bgcolor or color:
        kwargs["style"] = ft.ButtonStyle(bgcolor=bgcolor, color=color)
    if hasattr(ft, "Button"):
        return ft.Button(**kwargs)
    return ft.ElevatedButton(text=text, on_click=on_click, icon=icon, style=kwargs.get("style"))


def dropdown_on_select(handler):
    """Retorna kwargs de evento para Dropdown (Flet 0.86+ usa on_select)."""
    import inspect

    params = inspect.signature(ft.Dropdown.__init__).parameters
    if "on_select" in params:
        return {"on_select": handler}
    if "on_change" in params:
        return {"on_change": handler}
    return {"on_select": handler}


def safe_update(control: ft.Control, page: ft.Page | None = None) -> None:
    """Atualiza controle apenas se já estiver anexado à página."""
    try:
        control.update()
    except RuntimeError:
        if page is not None:
            page.update()


def show_snackbar(
    page: ft.Page,
    message: str,
    *,
    success: bool = True,
    duration_ms: int = 3500,
) -> None:
    """Exibe feedback temporário via SnackBar."""
    from core import colors

    snack = ft.SnackBar(
        content=ft.Text(message, color=colors.TEXT_PRIMARY),
        bgcolor=colors.SUCCESS if success else colors.ERROR,
        duration=duration_ms,
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(snack)
    else:
        page.snack_bar = snack
        page.snack_bar.open = True
    page.update()


def confirm_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm,
    *,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar",
):
    """Exibe diálogo modal de confirmação."""
    from core import colors
    from utils.ui_theme import danger_button_style

    def close_dialog(_=None):
        dialog.open = False
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        page.update()

    def confirm(_=None):
        close_dialog()
        on_confirm()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, color=colors.TEXT_PRIMARY, weight=ft.FontWeight.W_600, size=15),
        content=ft.Text(message, size=13, color=colors.TEXT_SECONDARY),
        actions=[
            ft.TextButton(content=cancel_text, on_click=close_dialog),
            ft.Button(
                content=confirm_text,
                style=danger_button_style(),
                on_click=confirm,
            ),
        ],
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    else:
        page.dialog = dialog
        dialog.open = True
        page.update()
