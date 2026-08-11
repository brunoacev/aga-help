import flet as ft
from core import colors
from core.components_data import COMPONENTS_CATALOG

def make_padding_symmetric(horizontal=0, vertical=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)

class MaterialsView(ft.Container):
    def __init__(self):
        self.txt_search = ft.TextField(
            label="Buscar por Código ou Nome do Material",
            hint_text="Ex: 5060, Comando, Perfil, Lâmina...",
            height=40,
            content_padding=make_padding_symmetric(horizontal=10, vertical=0),
            border_color=colors.BORDER_COLOR,
            bgcolor=colors.BG_SURFACE_LIGHT,
            text_style=ft.TextStyle(size=12, color=colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=11, color=colors.TEXT_SECONDARY),
            on_change=self._filter_materials,
            expand=True
        )

        # Colunas com Scroll Ativado
        self.col_horizontals = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        self.col_top = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        self.col_verticals = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        self.col_profiles = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)

        self.border_all = ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else ft.border.all(1, colors.BORDER_COLOR)

        self._load_and_categorize_materials(COMPONENTS_CATALOG)

        super().__init__(
            padding=10,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Text("CATÁLOGO DE MATERIAIS E COMPONENTES", size=13, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.txt_search]),
                ft.ResponsiveRow([
                    ft.Container(self._build_column_card("HORIZONTAIS", self.col_horizontals), col={"sm": 12, "md": 3}),
                    ft.Container(self._build_column_card("TOP (RECENTES)", self.col_top, is_highlighted=True), col={"sm": 12, "md": 3}),
                    ft.Container(self._build_column_card("VERTICAIS", self.col_verticals), col={"sm": 12, "md": 3}),
                    ft.Container(self._build_column_card("PERFIL", self.col_profiles), col={"sm": 12, "md": 3}),
                ], run_spacing=8, spacing=8, expand=True)
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
        )

    def _build_column_card(self, title: str, column_control: ft.Column, is_highlighted=False):
        title_color = colors.PRIMARY if is_highlighted else colors.TEXT_MUTED
        
        return ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=self.border_all,
            border_radius=8,
            padding=8,
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=11, weight=ft.FontWeight.BOLD, color=title_color)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=1, color=colors.BORDER_COLOR),
                ft.Container(
                    content=column_control,
                    expand=True,
                    height=420 # Altura ajustada com scroll para evitar esticar a tela
                )
            ], spacing=6)
        )

    def _load_and_categorize_materials(self, catalog_items):
        self.col_horizontals.controls.clear()
        self.col_top.controls.clear()
        self.col_verticals.controls.clear()
        self.col_profiles.controls.clear()

        for item in catalog_items:
            category = item.get("category", "").lower()
            code = item.get("code", "")
            name = item.get("name", "")

            item_card = self._create_material_item_card(code, name)

            if "top" in category or "comando" in category or "suporte" in category or "rolo" in category:
                self.col_top.controls.append(item_card)
            elif "horizontal" in category or "lâmina" in category or "lamina" in category:
                self.col_horizontals.controls.append(item_card)
            elif "vertical" in category or "tecidos" in category:
                self.col_verticals.controls.append(item_card)
            elif "perfil" in category or "tubo" in category or "bandô" in category or "bando" in category or "trilho" in category:
                self.col_profiles.controls.append(item_card)
            else:
                self.col_top.controls.append(item_card)

        for col, col_name in [(self.col_horizontals, "Horizontais"), (self.col_top, "TOP"), (self.col_verticals, "Verticais"), (self.col_profiles, "Perfil")]:
            if not col.controls:
                col.controls.append(
                    ft.Text(f"Nenhum item em {col_name}.", size=10, color=colors.TEXT_MUTED)
                )

    def _create_material_item_card(self, code: str, name: str):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(code, size=10, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                    bgcolor=colors.BG_SURFACE_LIGHT,
                    padding=make_padding_symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ),
                ft.Text("-", size=10, color=colors.TEXT_MUTED),
                ft.Text(name, size=10, color=colors.TEXT_PRIMARY, expand=True, overflow=ft.TextOverflow.ELLIPSIS)
            ], spacing=6, alignment=ft.MainAxisAlignment.START),
            padding=make_padding_symmetric(horizontal=8, vertical=4),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=self.border_all,
            border_radius=6
        )

    def _filter_materials(self, e):
        query = (self.txt_search.value or "").strip().lower()
        if not query:
            filtered = COMPONENTS_CATALOG
        else:
            filtered = [
                c for c in COMPONENTS_CATALOG 
                if query in c["code"].lower() or query in c["name"].lower() or query in c["category"].lower()
            ]
        self._load_and_categorize_materials(filtered)
        self.update()