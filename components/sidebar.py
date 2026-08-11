import flet as ft
from core import colors

def make_padding_symmetric(horizontal=0, vertical=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    if hasattr(ft, "padding") and hasattr(ft.padding, "symmetric"):
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.only(left=horizontal, right=horizontal, top=vertical, bottom=vertical)

class Sidebar(ft.Container):
    def __init__(self, on_navigate, on_clear_click):
        self.on_navigate = on_navigate
        self.on_clear_click = on_clear_click
        self.active_view = "kanban"

        border_right = ft.Border(right=ft.BorderSide(1, colors.BORDER_COLOR)) if hasattr(ft, "Border") else None

        self.txt_title = ft.Text("Aga-Help", weight=ft.FontWeight.BOLD, size=14, color=colors.TEXT_PRIMARY, visible=False)

        # Módulo 1: Kanban
        self.txt_kanban = ft.Text("1. Quadro Kanban", size=12, color=colors.TEXT_PRIMARY, visible=False, weight=ft.FontWeight.W_500)
        self.btn_kanban = ft.Container(
            content=ft.Row([
                ft.Icon(getattr(ft.Icons, "DASHBOARD_ROUNDED", None) or "dashboard", color=colors.PRIMARY, size=20),
                self.txt_kanban
            ], spacing=12),
            padding=make_padding_symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor=colors.BG_SURFACE_LIGHT,
            on_click=lambda _: self.on_navigate("kanban")
        )

        # Módulo 2: Cadastro de Pedido
        self.txt_add = ft.Text("2. Cadastro Pedido", size=12, color=colors.TEXT_PRIMARY, visible=False, weight=ft.FontWeight.W_500)
        self.btn_add = ft.Container(
            content=ft.Row([
                ft.Icon(getattr(ft.Icons, "ADD_BOX_ROUNDED", None) or "add", color=colors.TEXT_SECONDARY, size=20),
                self.txt_add
            ], spacing=12),
            padding=make_padding_symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor="transparent",
            on_click=lambda _: self.on_navigate("add")
        )

        # Módulo 3: Agenda & Histórico
        self.txt_contacts = ft.Text("3. Ações Agenda", size=12, color=colors.TEXT_PRIMARY, visible=False, weight=ft.FontWeight.W_500)
        self.btn_contacts = ft.Container(
            content=ft.Row([
                ft.Icon(getattr(ft.Icons, "CONTACTS_ROUNDED", None) or "contacts", color=colors.TEXT_SECONDARY, size=20),
                self.txt_contacts
            ], spacing=12),
            padding=make_padding_symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor="transparent",
            on_click=lambda _: self.on_navigate("agenda")
        )

        # Botão Limpar Banco (Rodapé)
        self.txt_clear = ft.Text("Limpar Banco", size=12, color="#F85149", visible=False, weight=ft.FontWeight.W_500)
        self.btn_clear = ft.Container(
            content=ft.Row([
                ft.Icon(getattr(ft.Icons, "DELETE_SWEEP_ROUNDED", None) or "delete_sweep", color="#F85149", size=20),
                self.txt_clear
            ], spacing=12),
            padding=make_padding_symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor="transparent",
            on_click=lambda _: self.on_clear_click()
        )

        super().__init__(
            width=64,
            bgcolor=colors.BG_SURFACE,
            border=border_right,
            padding=make_padding_symmetric(horizontal=8, vertical=16),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT) if hasattr(ft, "Animation") else None,
            on_hover=self._handle_hover,
            content=ft.Column([
                ft.Row([
                    ft.Icon(getattr(ft.Icons, "VIEW_KANBAN_ROUNDED", None) or "view_kanban", color=colors.PRIMARY, size=22),
                    self.txt_title
                ], spacing=12),
                
                ft.Divider(color=colors.BORDER_COLOR, height=16),
                
                ft.Column([
                    self.btn_kanban,
                    self.btn_add,
                    self.btn_contacts
                ], spacing=6, expand=True),

                self.btn_clear
            ], spacing=10)
        )

    def set_active(self, view_name: str):
        self.active_view = view_name
        self.btn_kanban.bgcolor = colors.BG_SURFACE_LIGHT if view_name == "kanban" else "transparent"
        self.btn_add.bgcolor = colors.BG_SURFACE_LIGHT if view_name == "add" else "transparent"
        self.btn_contacts.bgcolor = colors.BG_SURFACE_LIGHT if view_name == "agenda" else "transparent"
        
        self.btn_kanban.content.controls[0].color = colors.PRIMARY if view_name == "kanban" else colors.TEXT_SECONDARY
        self.btn_add.content.controls[0].color = colors.PRIMARY if view_name == "add" else colors.TEXT_SECONDARY
        self.btn_contacts.content.controls[0].color = colors.PRIMARY if view_name == "agenda" else colors.TEXT_SECONDARY
        self.update()

    def _handle_hover(self, e):
        is_hovered = e.data == "true"
        self.width = 180 if is_hovered else 64

        self.txt_title.visible = is_hovered
        self.txt_kanban.visible = is_hovered
        self.txt_add.visible = is_hovered
        self.txt_contacts.visible = is_hovered
        self.txt_clear.visible = is_hovered

        self.update()