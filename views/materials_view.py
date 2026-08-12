"""View do catálogo de materiais."""

from __future__ import annotations

import flet as ft

from core import colors
from core.components_data import COMPONENTS_CATALOG, FILTER_CATEGORY_ALL, FILTER_CATEGORY_OPTIONS
from core.services.catalog_service import categorize_materials, filter_components
from utils.flet_compat import border_all, dropdown_on_select, make_padding_symmetric, safe_update
from utils.ui_theme import FONT_CAPTION, RADIUS, S2, S3, S4, dropdown_style, field_style, page_container, page_header, text_caption, text_section_heading

COL_FIFTH = {"sm": 12, "md": 6, "lg": 4, "xl": 2}


class MaterialsView(ft.Container):
    """Catálogo de materiais categorizado."""

    def __init__(self):
        self.txt_search = ft.TextField(
            label="Buscar por Código ou Nome do Material",
            hint_text="Ex: 5060, Comando, Trilho, Lâmina...",
            on_change=self._filter_materials,
            expand=True,
            **field_style(),
        )
        self.dd_category = ft.Dropdown(
            label="Categoria",
            value=FILTER_CATEGORY_ALL,
            options=[ft.dropdown.Option(cat) for cat in FILTER_CATEGORY_OPTIONS],
            width=280,
            **dropdown_style(),
            **dropdown_on_select(self._filter_materials),
        )

        self.category_columns: dict[str, ft.Column] = {
            category: ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO)
            for category in FILTER_CATEGORY_OPTIONS[1:]
        }
        self.border_all = border_all(colors.BORDER_COLOR)
        self.grid_container = ft.Container(expand=True)

        self._load_and_categorize(COMPONENTS_CATALOG)

        super().__init__(
            expand=True,
            content=page_container(
                ft.Column(
                    [
                        page_header(
                            "Catálogo de Materiais",
                            "Consulte códigos e descrições de componentes por categoria.",
                        ),
                        ft.Row([self.txt_search, self.dd_category], spacing=S3),
                        self.grid_container,
                    ],
                    spacing=S4,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        )

    def _build_column_card(self, title: str, column_control: ft.Column):
        return ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S3,
            content=ft.Column(
                [
                    text_section_heading(title),
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    ft.Container(content=column_control, expand=True, height=400),
                ],
                spacing=S3,
            ),
        )

    def _rebuild_grid(self, visible_categories: list[str]) -> None:
        if len(visible_categories) == 1:
            category = visible_categories[0]
            self.grid_container.content = self._build_column_card(
                category,
                self.category_columns[category],
            )
            return

        self.grid_container.content = ft.ResponsiveRow(
            [
                ft.Container(
                    self._build_column_card(category, self.category_columns[category]),
                    col=COL_FIFTH,
                )
                for category in visible_categories
            ],
            run_spacing=S3,
            spacing=S3,
            expand=True,
        )

    def _load_and_categorize(self, catalog_items: list[dict]) -> None:
        buckets = categorize_materials(catalog_items)
        selected = self.dd_category.value or FILTER_CATEGORY_ALL
        visible = (
            list(buckets.keys())
            if selected == FILTER_CATEGORY_ALL
            else [selected]
        )

        for category in buckets:
            col = self.category_columns[category]
            col.controls.clear()
            items = buckets[category]
            if not items:
                col.controls.append(text_caption(f"Nenhum item em {category}."))
            else:
                for item in items:
                    col.controls.append(
                        self._create_material_item_card(item.get("code", ""), item.get("name", ""))
                    )

        self._rebuild_grid(visible)

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
        query = (self.txt_search.value or "").strip()
        category = self.dd_category.value or FILTER_CATEGORY_ALL
        filtered = filter_components(query, category=category, limit=None)
        self._load_and_categorize(filtered)
        safe_update(self)
