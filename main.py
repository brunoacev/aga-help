import flet as ft
from core import colors
from core.database import init_db, clear_all_orders, get_orders, update_order_status, delete_order, import_vcf_contacts
from components.sidebar import Sidebar
from components.quick_order_bar import QuickOrderBar
from components.kanban_column import KanbanColumn
from views.materials_view import MaterialsView

def main(page: ft.Page):
    init_db()

    # Janela Maximizada e Tema com Scrollbar Claro
    page.title = "AGA HELP - Sistema Agatek"
    page.bgcolor = colors.BG_PRIMARY
    page.padding = 0
    page.spacing = 0

    if hasattr(page, "window"):
        page.window.maximized = True

    # Estilização explícita da barra de rolagem (ScrollbarVisível/Branca)
    page.theme = ft.Theme(
        scrollbar_theme=ft.ScrollbarTheme(
            thumb_color={
                ft.ControlState.HOVERED: "#FFFFFF",
                ft.ControlState.DEFAULT: "#8B949E",
            },
            thickness=8,
            radius=4,
        )
    )

    # Fluxo sem a etapa "Proposta"
    stages = ["Orçamento", "Produção", "Pronto", "Faturado"]
    stage_colors = {
        "Orçamento": colors.COLOR_ORCAMENTO,
        "Produção": colors.COLOR_PRODUCAO,
        "Pronto": colors.COLOR_PRONTO,
        "Faturado": colors.COLOR_FATURADO
    }

    content_area = ft.Container(expand=True, padding=10, bgcolor=colors.BG_PRIMARY)

    # --- KANBAN ---
    def move_order(order_id: int, new_stage: str):
        update_order_status(order_id, new_stage)
        render_kanban_view()

    def remove_order(order_id: int):
        delete_order(order_id)
        render_kanban_view()

    def render_kanban_view():
        orders = get_orders()
        kanban_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        for stage in stages:
            stage_orders = [o for o in orders if o.get("status") == stage]
            col = KanbanColumn(
                stage=stage,
                orders=stage_orders,
                stage_color=stage_colors[stage],
                stages=stages,
                on_move_callback=move_order,
                on_delete_callback=remove_order
            )
            kanban_row.controls.append(col)

        content_area.content = ft.Column([
            ft.Text("ACOMPANHAMENTO DE PEDIDOS (KANBAN)", size=13, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
            kanban_row
        ], spacing=10, expand=True)
        page.update()

    # --- NOVO PEDIDO ---
    def on_order_saved():
        sidebar.set_active("kanban")
        render_kanban_view()
        page.snack_bar = ft.SnackBar(ft.Text("Ordem gerada com sucesso!"))
        page.snack_bar.open = True
        page.update()

    quick_order_view = QuickOrderBar(stages=stages, on_save_callback=on_order_saved)

    # --- AGENDA (.VCF) ---
    txt_vcf_input = ft.TextField(
        label="Cole o conteúdo do arquivo de contatos (.VCF) aqui",
        multiline=True,
        min_lines=8,
        max_lines=12,
        border_color=colors.BORDER_COLOR,
        bgcolor=colors.BG_SURFACE_LIGHT,
        text_style=ft.TextStyle(size=11, color=colors.TEXT_PRIMARY)
    )

    lbl_agenda_msg = ft.Text("", size=11, color=colors.PRIMARY)

    def process_vcf_import(e):
        vcf_data = (txt_vcf_input.value or "").strip()
        if not vcf_data:
            lbl_agenda_msg.value = "Cole o texto VCF antes de importar."
            lbl_agenda_msg.color = "#F85149"
            page.update()
            return

        added_count = import_vcf_contacts(vcf_data)
        lbl_agenda_msg.value = f"Importação concluída! {added_count} novos contatos salvos no banco."
        lbl_agenda_msg.color = colors.COLOR_PRONTO
        txt_vcf_input.value = ""
        page.update()

    btn_import_vcf = (
        ft.Button(
            "Importar Contatos VCF",
            icon=getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or "upload",
            style=ft.ButtonStyle(bgcolor=colors.PRIMARY, color=colors.TEXT_PRIMARY),
            on_click=process_vcf_import
        ) if hasattr(ft, "Button") else ft.ElevatedButton(
            "Importar Contatos VCF",
            icon=getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or "upload",
            style=ft.ButtonStyle(bgcolor=colors.PRIMARY, color=colors.TEXT_PRIMARY),
            on_click=process_vcf_import
        )
    )

    agenda_view = ft.Container(
        padding=10,
        expand=True,
        content=ft.Column([
            ft.Text("AÇÕES AGENDA - GERENCIAMENTO E IMPORTAÇÃO DE CONTATOS", size=13, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
            ft.Text("Cole o código VCF exportado da sua agenda para alimentar o autocompletar de revendas:", size=11, color=colors.TEXT_MUTED),
            txt_vcf_input,
            ft.Row([btn_import_vcf, lbl_agenda_msg], spacing=10)
        ], spacing=10)
    )

    # --- MATERIAIS ---
    materials_view = MaterialsView()

    # --- NAVEGAÇÃO ---
    def navigate_to(view_name: str):
        sidebar.set_active(view_name)
        if view_name == "kanban":
            render_kanban_view()
        elif view_name == "add":
            content_area.content = quick_order_view
        elif view_name == "agenda":
            content_area.content = agenda_view
        elif view_name == "materials":
            content_area.content = materials_view
        page.update()

    def on_clear_database():
        clear_all_orders()
        render_kanban_view()
        page.snack_bar = ft.SnackBar(ft.Text("Banco de dados limpo com sucesso!"))
        page.snack_bar.open = True
        page.update()

    sidebar = Sidebar(on_navigate=navigate_to, on_clear_click=on_clear_database)

    main_layout = ft.Row(
        [
            sidebar,
            ft.VerticalDivider(width=1, color=colors.BORDER_COLOR),
            content_area,
        ],
        expand=True,
        spacing=0
    )

    page.add(main_layout)
    render_kanban_view()

if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)