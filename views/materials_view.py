"""View do catálogo de materiais."""

from __future__ import annotations

import flet as ft

from core import colors
from core.components_data import COMPONENTS_CATALOG
from core.services.catalog_service import categorize_materials
from utils.flet_compat import border_all, make_padding_symmetric, safe_update
from utils.ui_theme import COL_QUARTER, FONT_CAPTION, RADIUS, S2, S3, S4, field_style, page_container, page_header, text_caption, text_section_heading


class MaterialsView(ft.Container):
    """Catálogo de materiais categorizado."""

    def __init__(self):
        self.txt_search = ft.TextField(
            label="Buscar por Código ou Nome do Material",
            hint_text="Ex: 5060, Comando, Perfil, Lâmina...",
            on_change=self._filter_materials,
            expand=True,
            **field_style(),
        )

        self.col_horizontals = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO)
        self.col_top = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO)
        self.col_verticals = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO)
        self.col_profiles = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO)
        self.border_all = border_all(colors.BORDER_COLOR)

        self._load_and_categorize(COMPONENTS_CATALOG)

        grid = ft.ResponsiveRow(
            [
                ft.Container(self._build_column_card("Horizontais", self.col_horizontals), col=COL_QUARTER),
                ft.Container(self._build_column_card("TOP (Recentes)", self.col_top, is_highlighted=True), col=COL_QUARTER),
                ft.Container(self._build_column_card("Verticais", self.col_verticals), col=COL_QUARTER),
                ft.Container(self._build_column_card("Perfil", self.col_profiles), col=COL_QUARTER),
            ],
            run_spacing=S3,
            spacing=S3,
            expand=True,
        )

        super().__init__(
            expand=True,
            content=page_container(
                ft.Column(
                    [
                        page_header(
                            "Catálogo de Materiais",
                            "Consulte códigos e descrições de componentes por categoria.",
                        ),
                        self.txt_search,
                        grid,
                    ],
                    spacing=S4,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        )

    def _build_column_card(self, title: str, column_control: ft.Column, is_highlighted=False):
        return ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S3,
            content=ft.Column(
                [
                    text_section_heading(title, accent=is_highlighted),
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    ft.Container(content=column_control, expand=True, height=400),
                ],
                spacing=S3,
            ),
        )

    def _load_and_categorize(self, catalog_items: list[dict]) -> None:
        buckets = categorize_materials(catalog_items)
        mapping = [
            (self.col_horizontals, "Horizontais", buckets["horizontals"]),
            (self.col_top, "TOP", buckets["top"]),
            (self.col_verticals, "Verticais", buckets["verticals"]),
            (self.col_profiles, "Perfil", buckets["profiles"]),
        ]
        for col, col_name, items in mapping:
            col.controls.clear()
            if not items:
                col.controls.append(text_caption(f"Nenhum item em {col_name}."))
            else:
                for item in items:
                    col.controls.append(
                        self._create_material_item_card(item.get("code", ""), item.get("name", ""))
                    )

    def _create_material_item_card(self, code: str, name: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(code, size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                        bgcolor=colors.BG_SURFACE_LIGHT,
                        padding=make_padding_symmetric(horizontal=S2, vertical=S2),
                        border_radius=S2,
                    ),
                    ft.Text(name, size=FONT_CAPTION, color=colors.TEXT_PRIMARY, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=S2,
            ),
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=self.border_all,
            border_radius=RADIUS,
        )

    def _filter_materials(self, _e):
        query = (self.txt_search.value or "").strip().lower()
        filtered = COMPONENTS_CATALOG if not query else [
            c for c in COMPONENTS_CATALOG
            if query in c["code"].lower() or query in c["name"].lower() or query in c["category"].lower()
        ]
        self._load_and_categorize(filtered)
        safe_update(self)
