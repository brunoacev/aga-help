"""Ponto de entrada da aplicação AGA HELP."""

from __future__ import annotations

import flet as ft

from core import colors
from core.auth.auth_service import bootstrap_users
from core.auth.user_session import get_user_handle
from core.db.schema import init_db
from core.services.order_service import clear_all_orders
from core.supabase_client import get_supabase
from components.sidebar import Sidebar
from components.order_form.quick_order_bar import QuickOrderBar
from views.agenda_view import AgendaView
from views.commissions_view import CommissionsView
from views.kanban_view import KanbanView
from views.login_view import LoginView
from views.logs_view import LogsView
from views.materials_view import MaterialsView
from views.whatsapp_view import WhatsAppView
from utils.flet_compat import border_all, confirm_dialog, make_padding_symmetric
from utils.ui_theme import S2, apply_app_theme

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _offline_banner() -> ft.Container | None:
    supabase = get_supabase()
    message = ""
    if not supabase.is_configured:
        message = (
            "Modo offline/local: configure SUPABASE_URL e SUPABASE_KEY para sincronizar com a nuvem."
        )
    elif not supabase.is_online:
        message = (
            "Sem conexão com o Supabase. Os dados serão salvos localmente até a internet voltar."
        )
    if not message:
        return None
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    getattr(ft.Icons, "CLOUD_OFF", None) or "cloud_off",
                    color=colors.COLOR_ORCAMENTO,
                    size=18,
                ),
                ft.Text(message, size=12, color=colors.COLOR_ORCAMENTO, expand=True),
            ],
            spacing=S2,
        ),
        bgcolor=colors.BG_SURFACE,
        border=border_all(colors.COLOR_ORCAMENTO),
        border_radius=8,
        padding=make_padding_symmetric(horizontal=12, vertical=8),
    )


def _build_app_shell(page: ft.Page) -> ft.Control:
    stages = ["Orçamento", "Produção", "Pronto", "Faturado"]
    stage_colors = {
        "Orçamento": colors.COLOR_ORCAMENTO,
        "Produção": colors.COLOR_PRODUCAO,
        "Pronto": colors.COLOR_PRONTO,
        "Faturado": colors.COLOR_FATURADO,
    }

    content_area = ft.Container(expand=True, bgcolor=colors.BG_PRIMARY)
    commissions_view = CommissionsView(page)

    def sync_sales_data() -> None:
        commissions_view.refresh()

    kanban_view = KanbanView(
        page,
        stages,
        stage_colors,
        on_orders_changed=sync_sales_data,
    )

    def on_order_saved():
        sidebar.set_active("kanban")
        content_area.content = kanban_view
        kanban_view.refresh()
        sync_sales_data()
        snack = ft.SnackBar(
            content=ft.Text("Ordem gerada com sucesso!", color=colors.TEXT_PRIMARY),
            bgcolor=colors.BG_SURFACE_LIGHT,
            duration=3000,
        )
        if hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        else:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    quick_order_view = QuickOrderBar(stages=stages, on_save_callback=on_order_saved, page=page)
    agenda_view = AgendaView(page)
    materials_view = MaterialsView()
    logs_view = LogsView()
    whatsapp_view = WhatsAppView(page)

    def navigate_to(view_name: str) -> None:
        sidebar.set_active(view_name)
        if view_name == "kanban":
            content_area.content = kanban_view
            kanban_view.refresh()
        elif view_name == "add":
            content_area.content = quick_order_view
        elif view_name == "agenda":
            content_area.content = agenda_view
            agenda_view.refresh_contacts()
        elif view_name == "materials":
            content_area.content = materials_view
        elif view_name == "logs":
            content_area.content = logs_view
            logs_view.refresh()
        elif view_name == "commissions":
            content_area.content = commissions_view
        elif view_name == "whatsapp":
            content_area.content = whatsapp_view
        page.update()
        if view_name == "commissions":
            commissions_view.refresh()
        if view_name == "whatsapp":
            whatsapp_view.on_show()

    def on_clear_database():
        confirm_dialog(
            page,
            "Limpar banco de dados",
            "Todos os pedidos do Kanban serão excluídos permanentemente. Deseja continuar?",
            on_confirm=_execute_clear,
            confirm_text="Limpar tudo",
        )

    def _execute_clear():
        clear_all_orders()
        kanban_view.refresh()
        logs_view.refresh()
        sync_sales_data()
        snack = ft.SnackBar(
            content=ft.Text("Banco de dados limpo com sucesso!", color=colors.TEXT_PRIMARY),
            bgcolor=colors.BG_SURFACE_LIGHT,
            duration=3000,
        )
        if hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        else:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    sidebar = Sidebar(on_navigate=navigate_to, on_clear_click=on_clear_database)

    content_area.content = kanban_view
    kanban_view.refresh()
    sidebar.set_active("kanban")

    handle = get_user_handle(page)
    user_label = ft.Text(
        f"Conectado: {handle}" if handle else "",
        size=11,
        color=colors.TEXT_MUTED,
    )

    main_column_controls: list[ft.Control] = []
    banner = _offline_banner()
    if banner:
        main_column_controls.append(banner)
    main_column_controls.append(
        ft.Row(
            [
                sidebar,
                content_area,
            ],
            expand=True,
            spacing=S2,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )
    if handle:
        main_column_controls.append(user_label)

    return ft.Column(main_column_controls, expand=True, spacing=S2)


def main(page: ft.Page) -> None:
    init_db()
    bootstrap_users()

    page.title = "AGA HELP - Sistema Agatek"
    apply_app_theme(page)

    if hasattr(page, "window"):
        page.window.maximized = True

    root = ft.Container(expand=True, bgcolor=colors.BG_PRIMARY)

    def on_login_success(_user: dict) -> None:
        root.content = _build_app_shell(page)
        page.update()

    root.content = LoginView(page, on_login_success)
    page.add(root)
    page.update()


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
