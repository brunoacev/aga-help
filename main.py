import asyncio
from tkinter import Tk, filedialog
import flet as ft
from core import colors
from core.database import (
    init_db, get_orders, update_order_status, delete_order, 
    clear_all_orders, import_vcf_contacts, get_logs, clear_all_contacts
)
from components.kanban_column import KanbanColumn
from components.quick_order_bar import QuickOrderBar
from components.sidebar import Sidebar
from views.materials_view import MaterialsView

STAGES = ["Orçamento", "Produção", "Pronto", "Faturado"]

STAGE_COLORS = {
    "Orçamento": colors.COLOR_ORCAMENTO,
    "Produção": colors.COLOR_PRODUCAO,
    "Pronto": colors.COLOR_PRONTO,
    "Faturado": colors.COLOR_FATURADO,
}

def main(page: ft.Page):
    # Configurações da página...
    page.title = "AGA HELP - Gestão de Pedidos e Materiais"
    
    # Instância da nova tela
    materials_view = MaterialsView()

    # Adicione a exibição da tela na árvore de controles do Flet conforme o menu/navegação da sua aplicação
    page.add(materials_view)

ft.app(target=main)

def open_native_file_picker():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo da agenda (.vcf)",
        filetypes=[("Arquivos VCF / vCard", "*.vcf"), ("Todos os Arquivos", "*.*")]
    )
    root.destroy()
    return file_path

def main(page: ft.Page):
    init_db()
    
    page.title = "Aga-Help - Controle de Pedidos"
    page.bg_color = colors.GH_BG
    page.bgcolor = colors.GH_BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    current_view = "kanban"
    toast_timer_task = None

    toast_text = ft.Text("", size=12, color=colors.TEXT_PRIMARY, weight=ft.FontWeight.W_500)
    toast_icon = ft.Icon(getattr(ft.Icons, "CHECK_CIRCLE", None) or "check", size=16, color="#3FB950")
    
    toast_container = ft.Container(
        content=ft.Row([toast_icon, toast_text], spacing=8),
        bgcolor=colors.BG_SURFACE_LIGHT,
        border=ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else None,
        border_radius=8,
        padding=ft.Padding(12, 8, 12, 8) if hasattr(ft, "Padding") else None,
        visible=False,
        animate_opacity=200
    )

    def show_toast(message: str, is_error: bool = False, display_seconds: float = 3.0):
        nonlocal toast_timer_task

        if toast_timer_task and not toast_timer_task.done():
            toast_timer_task.cancel()

        toast_text.value = message
        if is_error:
            toast_icon.name = getattr(ft.Icons, "ERROR_OUTLINE", None) or "error"
            toast_icon.color = "#F85149"
            toast_container.border = ft.Border.all(1, "#F85149") if hasattr(ft, "Border") else None
        else:
            toast_icon.name = getattr(ft.Icons, "CHECK_CIRCLE", None) or "check"
            toast_icon.color = "#3FB950"
            toast_container.border = ft.Border.all(1, colors.PRIMARY) if hasattr(ft, "Border") else None
        
        toast_container.visible = True
        page.update()

        async def auto_hide():
            await asyncio.sleep(display_seconds)
            toast_container.visible = False
            page.update()

        toast_timer_task = page.run_task(auto_hide)

    kanban_grid = ft.ResponsiveRow(spacing=12, run_spacing=12)

    def refresh_kanban():
        orders = get_orders()
        kanban_grid.controls.clear()

        for stage in STAGES:
            stage_orders = [o for o in orders if o["status"] == stage]
            col_component = KanbanColumn(
                stage=stage,
                orders=stage_orders,
                stage_color=STAGE_COLORS[stage],
                stages=STAGES,
                on_move_callback=move_stage,
                on_delete_callback=remove_order
            )
            kanban_grid.controls.append(ft.Container(col_component, col={"sm": 12, "md": 3}))

        if current_view == "kanban":
            render_view()

    def move_stage(order_id: int, new_status: str):
        update_order_status(order_id, new_status)
        show_toast(f"Pedido movido para {new_status}")
        refresh_kanban()

    def remove_order(order_id: int):
        delete_order(order_id)
        show_toast("Pedido excluído do sistema", is_error=True)
        refresh_kanban()

    def handle_clear_all():
        clear_all_orders()
        show_toast("Banco de dados zerado com sucesso", is_error=True)
        refresh_kanban()

    def handle_import_vcf():
        file_path = open_native_file_picker()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    vcf_text = f.read()
                count = import_vcf_contacts(vcf_text)
                if count > 0:
                    show_toast(f"{count} contatos importados da agenda!")
                else:
                    show_toast("Nenhum contato novo para importar.", is_error=True)
                render_view()
            except Exception:
                show_toast("Erro ao ler arquivo VCF", is_error=True)

    def handle_clear_contacts():
        clear_all_contacts()
        show_toast("Contatos da agenda removidos", is_error=True)
        render_view()

    def handle_quick_save():
        show_toast("Novo pedido cadastrado com sucesso!")
        refresh_kanban()

    view_container = ft.Container(expand=True, padding=16)
    quick_bar = QuickOrderBar(stages=STAGES, on_save_callback=handle_quick_save)

    def build_logs_view():
        logs = get_logs()
        log_rows = []

        for log in logs:
            badge_color = colors.PRIMARY if log["action_type"] in ("IMPORTAÇÃO", "NOVO PEDIDO") else "#F85149"
            log_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(log["created_at"], size=11, color=colors.TEXT_MUTED)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(log["action_type"], size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                        bgcolor=badge_color,
                        padding=ft.Padding(6, 2, 6, 2) if hasattr(ft, "Padding") else None,
                        border_radius=4
                    )),
                    ft.DataCell(ft.Text(log["description"], size=12, color=colors.TEXT_PRIMARY)),
                ])
            )

        if not log_rows:
            return ft.Text("Nenhuma ocorrência registrada até o momento.", size=12, color=colors.TEXT_MUTED)

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data e Hora", size=11, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY)),
                ft.DataColumn(ft.Text("Ação", size=11, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY)),
                ft.DataColumn(ft.Text("Detalhes da Ocorrência", size=11, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY)),
            ],
            rows=log_rows,
            border_radius=8,
            bgcolor=colors.BG_SURFACE,
        )

    def render_view():
        view_container.content = None
        
        if current_view == "kanban":
            view_container.content = ft.Column([
                ft.Row([
                    ft.Text("1. Acompanhamento de Pedidos (Kanban)", size=16, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    toast_container
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=colors.BORDER_COLOR, height=8),
                ft.Column([kanban_grid], scroll=ft.ScrollMode.AUTO, expand=True)
            ], spacing=10, expand=True)

        elif current_view == "add":
            view_container.content = ft.Column([
                ft.Row([
                    ft.Text("2. Cadastro de Novo Pedido", size=16, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    toast_container
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=colors.BORDER_COLOR, height=8),
                quick_bar
            ], spacing=10, expand=True)

        else:
            view_container.content = ft.Column([
                ft.Row([
                    ft.Text("3. Ações da Agenda e Histórico de Ocorrências", size=16, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    toast_container
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=colors.BORDER_COLOR, height=8),
                
                ft.Row([
                    ft.Button(
                        "Importar Agenda (.VCF)",
                        icon=getattr(ft.Icons, "CONTACTS", None) or "contacts",
                        style=ft.ButtonStyle(bgcolor=colors.PRIMARY, color=colors.TEXT_PRIMARY),
                        on_click=lambda _: handle_import_vcf()
                    ),
                    ft.OutlinedButton(
                        "Limpar Agenda de Contatos",
                        icon=getattr(ft.Icons, "DELETE_SWEEP", None) or "delete",
                        style=ft.ButtonStyle(color="#F85149"),
                        on_click=lambda _: handle_clear_contacts()
                    )
                ], spacing=12),
                
                ft.Divider(color=colors.BORDER_COLOR, height=12),
                ft.Text("Histórico de Ocorrências e Registros de Importação", size=13, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY),
                
                ft.Column([build_logs_view()], scroll=ft.ScrollMode.AUTO, expand=True)
            ], spacing=10, expand=True)
            
        page.update()

    def navigate_to(view_name):
        nonlocal current_view
        current_view = view_name
        sidebar.set_active(view_name)
        render_view()

    sidebar = Sidebar(
        on_navigate=navigate_to,
        on_clear_click=handle_clear_all
    )

    app_layout = ft.Row([
        sidebar,
        view_container
    ], spacing=0, expand=True)

    page.add(app_layout)

    if hasattr(page, "window"):
        page.window.maximized = True
    else:
        page.window_maximized = True

    refresh_kanban()

if __name__ == "__main__":
    run_app = getattr(ft, "run", None) or getattr(ft, "app", None)
    if run_app:
        run_app(main)