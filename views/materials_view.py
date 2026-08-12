"""View do catálogo de materiais."""

from __future__ import annotations

import flet as ft

from core import colors
from core.components_data import COMPONENTS_CATALOG, FILTER_CATEGORY_ALL, FILTER_CATEGORY_OPTIONS, OFFICIAL_CATEGORIES
from core.services.catalog_service import categorize_materials, filter_components
from utils.flet_compat import border_all, dropdown_on_select, make_padding_symmetric, safe_update
from utils.ui_theme import FONT_BODY, FONT_CAPTION, RADIUS, S1, S2, S3, S4, dropdown_style, field_style, page_container, page_header, text_caption, text_section_heading

GRID_COL = {"sm": 12, "md": 4}
SUMMARY_BOX_TITLE = "Resumo do Catálogo"
GRID_BOX_MIN_HEIGHT = 300


class MaterialsView(ft.Container):
    """Catálogo de materiais em grid 2 linhas x 3 colunas."""

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

        self.border_all = border_all(colors.BORDER_COLOR)
        self.category_columns: dict[str, ft.Column] = {
            category: ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
            for category in OFFICIAL_CATEGORIES
        }
        self.summary_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
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
                ),
            ),
        )

    def _build_category_box(self, title: str, list_column: ft.Column) -> ft.Container:
        return ft.Container(
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=self.border_all,
            border_radius=RADIUS,
            padding=S3,
            expand=True,
            height=GRID_BOX_MIN_HEIGHT,
            content=ft.Column(
                [
                    text_section_heading(title, accent=True),
                    ft.Divider(height=1, color=colors.BORDER_COLOR),
                    ft.Container(content=list_column, expand=True),
                ],
                spacing=S3,
                expand=True,
            ),
        )

    def _rebuild_grid(self) -> None:
        box_titles = [*OFFICIAL_CATEGORIES, SUMMARY_BOX_TITLE]
        box_columns = [*self.category_columns.values(), self.summary_column]

        self.grid_container.content = ft.ResponsiveRow(
            [
                ft.Container(
                    self._build_category_box(title, column),
                    col=GRID_COL,
                    expand=True,
                )
                for title, column in zip(box_titles, box_columns, strict=True)
            ],
            run_spacing=S3,
            spacing=S3,
            expand=True,
        )

    def _populate_summary(self, buckets: dict[str, list[dict]], total_items: int, query: str) -> None:
        self.summary_column.controls.clear()
        self.summary_column.controls.append(
            ft.Text(
                f"{total_items} material(is) exibido(s)",
                size=FONT_BODY,
                weight=ft.FontWeight.W_600,
                color=colors.TEXT_PRIMARY,
            )
        )
        if query:
            self.summary_column.controls.append(
                text_caption(f'Busca ativa: "{query}"')
            )

        self.summary_column.controls.append(ft.Divider(height=1, color=colors.BORDER_COLOR))

        for category in OFFICIAL_CATEGORIES:
            count = len(buckets.get(category, []))
            self.summary_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                category,
                                size=FONT_CAPTION,
                                color=colors.TEXT_SECONDARY,
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(count),
                                    size=FONT_CAPTION,
                                    weight=ft.FontWeight.W_600,
                                    color=colors.PRIMARY,
                                ),
                                bgcolor=colors.BG_SURFACE,
                                padding=make_padding_symmetric(horizontal=S2, vertical=S1),
                                border_radius=S2,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=make_padding_symmetric(horizontal=S2, vertical=S2),
                    border=self.border_all,
                    border_radius=RADIUS,
                )
            )

    def _load_and_categorize(self, catalog_items: list[dict]) -> None:
        buckets = categorize_materials(catalog_items)
        query = (self.txt_search.value or "").strip()

        for category in OFFICIAL_CATEGORIES:
            col = self.category_columns[category]
            col.controls.clear()
            items = buckets.get(category, [])
            if not items:
                col.controls.append(text_caption(f"Nenhum item em {category}."))
            else:
                for item in items:
                    col.controls.append(
                        self._create_material_item_card(item.get("code", ""), item.get("name", ""))
                    )

        total_items = sum(len(items) for items in buckets.values())
        self._populate_summary(buckets, total_items, query)
        self._rebuild_grid()

    def _create_material_item_card(self, code: str, name: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(code, size=FONT_CAPTION, weight=ft.FontWeight.W_600, color=colors.PRIMARY),
                        bgcolor=colors.BG_SURFACE,
                        padding=make_padding_symmetric(horizontal=S2, vertical=S2),
                        border_radius=S2,
                    ),
                    ft.Text(
                        name,
                        size=FONT_CAPTION,
                        color=colors.TEXT_PRIMARY,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=S2,
            ),
            padding=make_padding_symmetric(horizontal=S2, vertical=S2),
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=RADIUS,
        )

    def _filter_materials(self, _e):
        query = (self.txt_search.value or "").strip()
        category = self.dd_category.value or FILTER_CATEGORY_ALL
        filtered = filter_components(query, category=category, limit=None)
        self._load_and_categorize(filtered)
        safe_update(self)
