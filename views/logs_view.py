"""View de auditoria e logs."""

from __future__ import annotations

import flet as ft

from core import colors
from core.db.logs_repository import get_logs
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.ui_theme import FONT_CAPTION, RADIUS, S2, S3, S4, page_container, page_header, text_caption


class LogsView(ft.Container):
    """Exibe histórico de ações do sistema."""

    def __init__(self):
        self.logs_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        super().__init__(expand=True)
        self.refresh()

    def refresh(self) -> None:
        logs = get_logs(limit=50)
        self.logs_column.controls.clear()

        if not logs:
            self.logs_column.controls.append(text_caption("Nenhum registro de auditoria."))
        else:
            for entry in logs:
                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(entry.get("created_at", ""), size=FONT_CAPTION, color=colors.TEXT_MUTED, width=136),
                            ft.Container(
                                content=ft.Text(
                                    entry.get("action_type", ""),
                                    size=FONT_CAPTION,
                                    weight=ft.FontWeight.W_600,
                                    color=colors.PRIMARY,
                                ),
                                width=104,
                            ),
                            ft.Text(
                                entry.get("description", ""),
                                size=FONT_CAPTION,
                                color=colors.TEXT_PRIMARY,
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=S3,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=make_padding_symmetric(horizontal=S3, vertical=S2),
                    bgcolor=colors.BG_SURFACE,
                    border=border_all(colors.BORDER_COLOR),
                    border_radius=RADIUS,
                )
                self.logs_column.controls.append(row)

        self.content = page_container(
            ft.Column(
                [
                    page_header(
                        "Auditoria do Sistema",
                        "Registro das últimas 50 ações realizadas no sistema.",
                    ),
                    ft.Container(content=self.logs_column, expand=True),
                ],
                spacing=S4,
                expand=True,
            ),
        )
        safe_update(self)
