"""View de comissões e métricas de faturamento."""

from __future__ import annotations

import flet as ft

from controllers.commission_controller import CommissionController
from core import colors
from utils.flet_compat import border_all, dropdown_on_select, make_padding_symmetric
from utils.formatting import format_brl, safe_float
from utils.period_filter import PERIOD_LABELS
from utils.ui_theme import (
    FONT_BODY,
    FONT_CAPTION,
    RADIUS,
    S2,
    S3,
    S4,
    dropdown_style,
    field_style,
    icon_button,
    page_header,
    text_caption,
    text_section_heading,
)

EMPTY_STATE_MESSAGE = "Nenhum orçamento/faturamento encontrado para o período"


class CommissionsView(ft.Container):
    """Painel de KPIs e comissões por período."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.controller = CommissionController()
        self.border_all = border_all(colors.BORDER_COLOR)
        self._is_refreshing = False

        self.dd_period = ft.Dropdown(
            label="Período",
            value=self.controller.period,
            options=[ft.dropdown.Option(label) for label in PERIOD_LABELS],
            width=180,
            **dropdown_style(),
            **dropdown_on_select(self._on_filter_change),
        )
        self.lbl_period_range = ft.Text(
            "Selecione um período",
            size=FONT_BODY,
            color=colors.TEXT_SECONDARY,
            weight=ft.FontWeight.W_500,
        )
        self.txt_commission_rate = ft.TextField(
            label="Comissão padrão (%)",
            value=str(int(self.controller.commission_rate)),
            width=160,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_filter_change,
            **field_style(),
        )

        self.kpi_total_billed = self._build_kpi_card("Total Faturado", "R$ 0,00", colors.PRIMARY)
        self.kpi_orders = self._build_kpi_card("Pedidos Concluídos", "0", colors.SUCCESS)
        self.kpi_avg_ticket = self._build_kpi_card("Ticket Médio", "R$ 0,00", colors.TEXT_PRIMARY)
        self.kpi_commission = self._build_kpi_card("Comissão Gerada", "R$ 0,00", colors.COLOR_ORCAMENTO)

        self.table_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)

        filters = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Row(
                [
                    self.dd_period,
                    icon_button(
                        "CHEVRON_LEFT_ROUNDED",
                        "chevron_left",
                        color=colors.TEXT_SECONDARY,
                        tooltip="Período anterior",
                        on_click=lambda _: self._shift_period(-1),
                    ),
                    icon_button(
                        "CHEVRON_RIGHT_ROUNDED",
                        "chevron_right",
                        color=colors.TEXT_SECONDARY,
                        tooltip="Próximo período",
                        on_click=lambda _: self._shift_period(1),
                    ),
                    self.lbl_period_range,
                    ft.Container(expand=True),
                    self.txt_commission_rate,
                ],
                spacing=S3,
                vertical_alignment=ft.CrossAxisAlignment.END,
                wrap=True,
            ),
        )

        kpi_row = ft.Row(
            [
                ft.Container(content=self.kpi_total_billed, expand=1),
                ft.Container(content=self.kpi_orders, expand=1),
                ft.Container(content=self.kpi_avg_ticket, expand=1),
                ft.Container(content=self.kpi_commission, expand=1),
            ],
            spacing=S3,
            wrap=True,
        )

        table_section = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            expand=True,
            content=ft.Column(
                [
                    text_section_heading("Detalhamento de Comissões"),
                    ft.Container(content=self.table_column, expand=True),
                ],
                spacing=S3,
                expand=True,
            ),
        )

        super().__init__(
            expand=True,
            bgcolor=colors.BG_PRIMARY,
            padding=make_padding_symmetric(horizontal=S4, vertical=S4),
            content=ft.Column(
                [
                    page_header(
                        "Comissões e Faturamento",
                        "Métricas de pedidos faturados e comissões calculadas por período.",
                    ),
                    filters,
                    kpi_row,
                    table_section,
                ],
                spacing=S4,
                expand=True,
            ),
        )

    def did_mount(self) -> None:
        """Carrega dados somente após a view estar na árvore Flet."""
        self.refresh()

    def _build_kpi_card(self, title: str, value: str, accent: str) -> ft.Container:
        return ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            content=ft.Column(
                [
                    ft.Text(title, size=FONT_CAPTION, color=colors.TEXT_MUTED, weight=ft.FontWeight.W_600),
                    ft.Text(value, size=20, color=accent, weight=ft.FontWeight.W_600),
                ],
                spacing=S2,
                tight=True,
            ),
        )

    def _update_kpi(self, card: ft.Container, value: str) -> None:
        card.content.controls[1].value = value

    def _reset_kpis(self) -> None:
        zero = format_brl(0.0)
        self._update_kpi(self.kpi_total_billed, zero)
        self._update_kpi(self.kpi_orders, "0")
        self._update_kpi(self.kpi_avg_ticket, zero)
        self._update_kpi(self.kpi_commission, zero)

    def _build_table_header(self) -> ft.Container:
        headers = [
            ("Data", 96),
            ("Nº OS", 80),
            ("Cliente", None),
            ("Valor Total", 112),
            ("% Com.", 72),
            ("Comissão", 112),
            ("Pagamento", 104),
        ]
        cells = []
        for label, width in headers:
            text = ft.Text(label, size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.TEXT_MUTED)
            if width:
                cells.append(ft.Container(content=text, width=width))
            else:
                cells.append(ft.Container(content=text, expand=True))
        return ft.Container(
            content=ft.Row(cells, spacing=S2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border_radius=RADIUS,
        )

    def _build_table_row(self, row: dict) -> ft.Container:
        rate = safe_float(row.get("rate"))
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        ft.Text(str(row.get("date") or "11/08/2026"), size=FONT_CAPTION, color=colors.TEXT_SECONDARY),
                        width=96,
                    ),
                    ft.Container(
                        ft.Text(
                            str(row.get("order_number") or "—"),
                            size=FONT_CAPTION,
                            weight=ft.FontWeight.W_600,
                            color=colors.PRIMARY,
                        ),
                        width=80,
                    ),
                    ft.Container(
                        ft.Text(
                            str(row.get("client") or "—"),
                            size=FONT_CAPTION,
                            color=colors.TEXT_PRIMARY,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        expand=True,
                    ),
                    ft.Container(
                        ft.Text(str(row.get("total_fmt") or format_brl(0.0)), size=FONT_CAPTION, color=colors.TEXT_PRIMARY),
                        width=112,
                    ),
                    ft.Container(ft.Text(f"{rate:.0f}%", size=FONT_CAPTION, color=colors.TEXT_SECONDARY), width=72),
                    ft.Container(
                        ft.Text(
                            str(row.get("commission_fmt") or format_brl(0.0)),
                            size=FONT_CAPTION,
                            weight=ft.FontWeight.W_600,
                            color=colors.SUCCESS,
                        ),
                        width=112,
                    ),
                    ft.Container(
                        ft.Text(str(row.get("payment_status") or "Pendente"), size=FONT_CAPTION, color=colors.TEXT_SECONDARY),
                        width=104,
                    ),
                ],
                spacing=S2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=self.border_all,
            border_radius=RADIUS,
        )

    def _render_empty_table(self, message: str = EMPTY_STATE_MESSAGE) -> None:
        self.table_column.controls.clear()
        self.table_column.controls.append(self._build_table_header())
        self.table_column.controls.append(text_caption(message))

    def _apply_report(self, report: dict) -> None:
        self.lbl_period_range.value = report.get("period_label") or ""
        metrics = report.get("metrics") or {}
        self._update_kpi(self.kpi_total_billed, metrics.get("total_billed_fmt") or format_brl(0.0))
        self._update_kpi(self.kpi_orders, str(metrics.get("order_count") or 0))
        self._update_kpi(self.kpi_avg_ticket, metrics.get("avg_ticket_fmt") or format_brl(0.0))
        self._update_kpi(self.kpi_commission, metrics.get("total_commission_fmt") or format_brl(0.0))

        rows = report.get("rows") or []
        self.table_column.controls.clear()
        self.table_column.controls.append(self._build_table_header())
        if not rows:
            self.table_column.controls.append(text_caption(EMPTY_STATE_MESSAGE))
        else:
            for row in rows:
                self.table_column.controls.append(self._build_table_row(row))

    def refresh(self) -> None:
        if self._is_refreshing:
            return
        self._is_refreshing = True
        try:
            self.controller.set_period(self.dd_period.value or "Mensal")
            self.controller.set_commission_rate(self.txt_commission_rate.value or "")
            report = self.controller.build_report()
            self._apply_report(report)
        except Exception:
            self._reset_kpis()
            self.lbl_period_range.value = ""
            self._render_empty_table()
        finally:
            self._is_refreshing = False

        if self.app_page:
            self.app_page.update()

    def _on_filter_change(self, _e) -> None:
        if self._is_refreshing:
            return
        self.refresh()

    def _shift_period(self, direction: int) -> None:
        self.controller.shift_period(direction)
        self.refresh()
