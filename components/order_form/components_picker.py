"""Seletor de componentes do catálogo."""

from __future__ import annotations

import flet as ft

from core import colors
from utils.flet_compat import border_all, get_alignment_center, make_padding_symmetric, safe_update
from utils.ui_theme import COL_5, COL_7, FONT_CAPTION, INPUT_HEIGHT, RADIUS, S1, S2, S3, S4, icon_button, section_card, text_caption, text_section_heading

# Altura fixa da área de catálogo + itens (grid 8px) — evita crescimento vertical da janela
COMPONENTS_PANEL_HEIGHT = 216
_SUBHEADING_BLOCK = 28  # título interno + spacing
SELECTED_LIST_HEIGHT = COMPONENTS_PANEL_HEIGHT - _SUBHEADING_BLOCK
CATALOG_TABLE_HEIGHT = COMPONENTS_PANEL_HEIGHT - _SUBHEADING_BLOCK - INPUT_HEIGHT - S3


class ComponentsPicker(ft.Container):
    """Catálogo filtrável e lista de itens selecionados."""

    def __init__(self, input_style: dict, controller):
        self.controller = controller
        self.on_selection_changed = None

        self.txt_component_search = ft.TextField(
            label="Buscar por Código ou Nome do Componente",
            hint_text="Ex: 5060, Comando, Suporte, Bandô...",
            on_change=self._filter_components,
            expand=True,
            **input_style,
        )
        self.components_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        self.components_table_container = ft.Container(
            content=self.components_column,
            height=CATALOG_TABLE_HEIGHT,
        )
        self.selected_items_column = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True)
        clip = ft.ClipBehavior.HARD_EDGE if hasattr(ft, "ClipBehavior") else None
        self.selected_items_container = ft.Container(
            content=self.selected_items_column,
            height=SELECTED_LIST_HEIGHT,
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all(colors.BORDER_COLOR),
            border_radius=RADIUS,
            padding=S3,
            clip_behavior=clip,
        )

        col_catalog = ft.Column(
            [
                text_section_heading("Catálogo de Componentes"),
                self.txt_component_search,
                self.components_table_container,
            ],
            spacing=S3,
            height=COMPONENTS_PANEL_HEIGHT,
        )
        col_selected = ft.Column(
            [
                text_section_heading("Itens Adicionados ao Pedido"),
                self.selected_items_container,
            ],
            spacing=S3,
            height=COMPONENTS_PANEL_HEIGHT,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        body = ft.Container(
            height=COMPONENTS_PANEL_HEIGHT,
            content=ft.ResponsiveRow(
                [
                    ft.Container(col_catalog, col=COL_7),
                    ft.Container(col_selected, col=COL_5),
                ],
                run_spacing=S4,
                spacing=S4,
            ),
        )

        card = section_card("3. Adição de Componentes (Sistema Agatek)", body, accent=True)
        super().__init__(
            bgcolor=card.bgcolor,
            border=card.border,
            border_radius=card.border_radius,
            padding=card.padding,
            content=card.content,
        )

        self.refresh_catalog()
        self.refresh_selected()

    def _filter_components(self, _e):
        query = (self.txt_component_search.value or "").strip()
        items = self.controller.filter_catalog(query, limit=2)
        self._render_catalog(items)
        safe_update(self)

    def refresh_catalog(self) -> None:
        items = self.controller.filter_catalog("", limit=2)
        self._render_catalog(items)

    def refresh_selected(self) -> None:
        self._render_selected(self.controller.selected_components)

    def _render_catalog(self, items: list[dict]) -> None:
        self.components_column.controls.clear()
        if not items:
            self.components_column.controls.append(
                text_caption("Nenhum componente encontrado no sistema.")
            )
            return

        for item in items:
            is_meter = self.controller.is_meter_item(item)
            mini_field = dict(
                height=36,
                text_size=FONT_CAPTION,
                content_padding=make_padding_symmetric(horizontal=S2, vertical=0),
                border_color=colors.BORDER_COLOR,
                border_radius=RADIUS,
                text_style=ft.TextStyle(color=colors.TEXT_PRIMARY),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            txt_dim = ft.TextField(
                hint_text="Metros (m)" if is_meter else "N/A",
                width=104,
                disabled=not is_meter,
                bgcolor=colors.BG_SURFACE_LIGHT if is_meter else colors.BG_SURFACE,
                **mini_field,
            )
            txt_qty = ft.TextField(
                value="1",
                width=48,
                bgcolor=colors.BG_SURFACE_LIGHT,
                height=mini_field["height"],
                text_size=mini_field["text_size"],
                content_padding=mini_field["content_padding"],
                border_color=mini_field["border_color"],
                border_radius=mini_field["border_radius"],
                keyboard_type=mini_field["keyboard_type"],
                text_style=ft.TextStyle(color=colors.TEXT_PRIMARY, weight=ft.FontWeight.W_600, size=FONT_CAPTION),
            )
            btn_add = ft.IconButton(
                icon=getattr(ft.Icons, "ADD_ROUNDED", None) or "add",
                icon_color=colors.TEXT_PRIMARY,
                bgcolor=colors.PRIMARY,
                icon_size=16,
                width=36,
                height=36,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=RADIUS) if hasattr(ft, "RoundedRectangleBorder") else None,
                    mouse_cursor=ft.MouseCursor.CLICK,
                ),
                tooltip="Adicionar ao Pedido",
                on_click=lambda e, comp=item, d=txt_dim, q=txt_qty: self._add_item(comp, d.value, q.value),
            )
            row_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                item["code"],
                                size=FONT_CAPTION,
                                weight=ft.FontWeight.W_600,
                                color=colors.PRIMARY,
                            ),
                            width=64,
                            bgcolor=colors.BG_SURFACE,
                            padding=make_padding_symmetric(horizontal=S1, vertical=S1),
                            border_radius=S1,
                            alignment=get_alignment_center(),
                        ),
                        ft.Text(
                            item["name"],
                            size=FONT_CAPTION,
                            color=colors.TEXT_PRIMARY,
                            expand=True,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row([txt_dim, txt_qty, btn_add], spacing=S1),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=make_padding_symmetric(horizontal=S2, vertical=S2),
                bgcolor=colors.BG_SURFACE,
                border=border_all(colors.BORDER_COLOR),
                border_radius=RADIUS,
            )
            self.components_column.controls.append(row_item)

    def _add_item(self, component: dict, dim_val: str, qty_val: str) -> None:
        self.controller.add_component(component, dim_val, qty_val)
        self.refresh_selected()
        if self.on_selection_changed:
            self.on_selection_changed(self.controller.components_summary())
        safe_update(self)

    def _render_selected(self, items: list[dict]) -> None:
        self.selected_items_column.controls.clear()
        if not items:
            self.selected_items_column.controls.append(
                text_caption("Nenhum item adicionado ao pedido.")
            )
            return

        for idx, item in enumerate(items):
            btn_remove = icon_button(
                "DELETE_OUTLINE",
                "delete",
                color=colors.ERROR,
                tooltip="Remover Item",
                on_click=lambda e, i=idx: self._remove_item(i),
                size=16,
            )
            row = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            item["display"],
                            size=FONT_CAPTION,
                            color=colors.TEXT_PRIMARY,
                            expand=True,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        btn_remove,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=make_padding_symmetric(horizontal=S2, vertical=S1),
                bgcolor=colors.BG_SURFACE,
                border_radius=S1,
            )
            self.selected_items_column.controls.append(row)

    def _remove_item(self, index: int) -> None:
        self.controller.remove_component(index)
        self.refresh_selected()
        if self.on_selection_changed:
            self.on_selection_changed(self.controller.components_summary())
        safe_update(self)

    def reset(self) -> None:
        self.txt_component_search.value = ""
        self.controller.reset()
        self.refresh_catalog()
        self.refresh_selected()
        self.clear_validation()

    def mark_invalid(self) -> None:
        self.selected_items_container.border = border_all(colors.ERROR)

    def clear_validation(self) -> None:
        self.selected_items_container.border = border_all(colors.BORDER_COLOR)
