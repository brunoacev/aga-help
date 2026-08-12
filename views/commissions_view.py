"""View de comissões e métricas de faturamento."""

from __future__ import annotations

import flet as ft

from controllers.commission_controller import CommissionController
from core import colors
from utils.flet_compat import border_all, dropdown_on_select, make_padding_symmetric, safe_update
from utils.period_filter import PERIOD_LABELS
from utils.ui_theme import (
    COL_QUARTER,
    FONT_BODY,
    FONT_CAPTION,
    FONT_LABEL,
    RADIUS,
    S2,
    S3,
    S4,
    dropdown_style,
    field_style,
    icon_button,
    page_container,
    page_header,
    text_caption,
    text_section_heading,
)


class CommissionsView(ft.Container):
    """Painel de KPIs e comissões por período."""

    def __init__(self):
        self.controller = CommissionController()
        self.border_all = border_all(colors.BORDER_COLOR)

        self.dd_period = ft.Dropdown(
            label="Período",
            value=self.controller.period,
            options=[ft.dropdown.Option(label) for label in PERIOD_LABELS],
            width=180,
            **dropdown_style(),
            **dropdown_on_select(self._on_filter_change),
        )
        self.lbl_period_range = ft.Text("", size=FONT_BODY, color=colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500)
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

        kpi_row = ft.ResponsiveRow(
            [
                ft.Container(self.kpi_total_billed, col=COL_QUARTER),
                ft.Container(self.kpi_orders, col=COL_QUARTER),
                ft.Container(self.kpi_avg_ticket, col=COL_QUARTER),
                ft.Container(self.kpi_commission, col=COL_QUARTER),
            ],
            spacing=S3,
            run_spacing=S3,
        )

        table_card = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S4,
            expand=True,
            content=ft.Column(
                [
                    text_section_heading("Detalhamento de Comissões"),
                    self.table_column,
                ],
                spacing=S3,
                expand=True,
            ),
        )

        super().__init__(
            expand=True,
            content=page_container(
                ft.Column(
                    [
                        page_header(
                            "Comissões e Faturamento",
                            "Métricas de pedidos faturados e comissões calculadas por período.",
                        ),
                        filters,
                        kpi_row,
                        table_card,
                    ],
                    spacing=S4,
                    expand=True,
                ),
            ),
        )
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
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(ft.Text(row["date"], size=FONT_CAPTION, color=colors.TEXT_SECONDARY), width=96),
                    ft.Container(
                        ft.Text(row["order_number"], size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                        width=80,
                    ),
                    ft.Container(
                        ft.Text(
                            row["client"],
                            size=FONT_CAPTION,
                            color=colors.TEXT_PRIMARY,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        expand=True,
                    ),
                    ft.Container(ft.Text(row["total_fmt"], size=FONT_CAPTION, color=colors.TEXT_PRIMARY), width=112),
                    ft.Container(ft.Text(f"{row['rate']:.0f}%", size=FONT_CAPTION, color=colors.TEXT_SECONDARY), width=72),
                    ft.Container(
                        ft.Text(row["commission_fmt"], size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.SUCCESS),
                        width=112,
                    ),
                    ft.Container(
                        ft.Text(row["payment_status"], size=FONT_CAPTION, color=colors.TEXT_SECONDARY),
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

    def refresh(self) -> None:
        self.controller.set_period(self.dd_period.value or "Mensal")
        self.controller.set_commission_rate(self.txt_commission_rate.value or "")
        report = self.controller.build_report()

        self.lbl_period_range.value = report["period_label"]
        metrics = report["metrics"]
        self._update_kpi(self.kpi_total_billed, metrics["total_billed_fmt"])
        self._update_kpi(self.kpi_orders, str(metrics["order_count"]))
        self._update_kpi(self.kpi_avg_ticket, metrics["avg_ticket_fmt"])
        self._update_kpi(self.kpi_commission, metrics["total_commission_fmt"])

        self.table_column.controls.clear()
        self.table_column.controls.append(self._build_table_header())
        if not report["rows"]:
            self.table_column.controls.append(
                text_caption("Nenhum pedido faturado encontrado neste período.")
            )
        else:
            for row in report["rows"]:
                self.table_column.controls.append(self._build_table_row(row))

        safe_update(self)

    def _on_filter_change(self, _e) -> None:
        self.refresh()

    def _shift_period(self, direction: int) -> None:
        self.controller.shift_period(direction)
        self.refresh()
