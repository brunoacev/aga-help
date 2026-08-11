import flet as ft
from core import colors

def make_padding_symmetric(horizontal=0, vertical=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)

def get_alignment_center():
    if hasattr(ft, "Alignment"):
        return ft.Alignment(0, 0)
    if hasattr(ft, "alignment") and hasattr(ft.alignment, "CENTER"):
        return ft.alignment.CENTER
    return "center"

class KanbanCard(ft.Container):
    def __init__(self, order, stages, on_move_callback, on_delete_callback):
        self.order = order
        self.stages = stages
        self.on_move_callback = on_move_callback
        self.on_delete_callback = on_delete_callback

        stage = order["status"]
        
        current_index = stages.index(stage) if stage in stages else 0
        next_stage = stages[current_index + 1] if current_index + 1 < len(stages) else None

        btn_action = None
        if next_stage:
            btn_bgcolor = colors.COLOR_FATURADO if next_stage == "Faturado" else colors.PRIMARY
            
            btn_action = ft.ElevatedButton(
                f"{next_stage} →",
                bgcolor=btn_bgcolor,
                color=colors.TEXT_PRIMARY,
                height=26,
                style=ft.ButtonStyle(
                    padding=make_padding_symmetric(horizontal=8, vertical=0),
                    shape=ft.RoundedRectangleBorder(radius=6) if hasattr(ft, "RoundedRectangleBorder") else None,
                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD),
                    mouse_cursor=ft.MouseCursor.CLICK
                ),
                on_click=lambda e: self.on_move_callback(order["id"], next_stage)
            )

        value_str = f"R$ {order['value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        desc_text = order.get("description", "") or ""
        phone_text = order.get("phone", "") or ""
        address_text = order.get("address", "") or ""
        
        w = order.get("width", "") or ""
        h = order.get("height", "") or ""
        dim_text = f"📐 {w}m x {h}m" if (w or h) else ""

        border_all = ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else ft.border.all(1, colors.BORDER_COLOR)

        btn_delete = ft.Container(
            content=ft.IconButton(
                icon=getattr(ft.Icons, "DELETE_OUTLINE", None) or "delete_outline",
                icon_color=colors.GH_TEXT_MUTED,
                icon_size=16,
                padding=0,
                mouse_cursor=ft.MouseCursor.CLICK,
                tooltip="Excluir Pedido",
                on_click=lambda e: self.on_delete_callback(order["id"])
            ),
            width=28,
            height=28,
            alignment=get_alignment_center(),
            border_radius=14
        )

        order_num_clean = str(order['order_number']).replace("#", "").strip()

        super().__init__(
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=border_all,
            border_radius=8,
            padding=10,
            content=ft.Column([
                # Cabeçalho: Número do Pedido + Excluir
                ft.Row([
                    ft.Container(
                        content=ft.Text(order_num_clean, weight=ft.FontWeight.BOLD, color=colors.PRIMARY, size=12),
                        bgcolor=colors.BG_SURFACE,
                        padding=make_padding_symmetric(horizontal=6, vertical=2),
                        border_radius=4
                    ),
                    btn_delete
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Nome da Revenda + Valor
                ft.Row([
                    ft.Text(order["reseller_name"], color=colors.TEXT_PRIMARY, weight=ft.FontWeight.BOLD, size=13, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(value_str, color=colors.COLOR_PRONTO, weight=ft.FontWeight.BOLD, size=13),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Telefone e Endereço Automáticos
                ft.Text(f"📞 {phone_text}", size=10, color=colors.TEXT_MUTED) if phone_text else ft.Container(),
                ft.Text(f"📍 {address_text}", size=10, color=colors.TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS) if address_text else ft.Container(),

                # Descrição Resumida
                ft.Text(desc_text, size=11, color=colors.TEXT_SECONDARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS) if desc_text else ft.Container(),
                
                # Tag de Medidas
                ft.Container(
                    content=ft.Text(dim_text, size=10, color=colors.PRIMARY, weight=ft.FontWeight.W_600),
                    bgcolor=colors.BG_SURFACE,
                    padding=make_padding_symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ) if dim_text else ft.Container(),

                ft.Divider(color=colors.BORDER_COLOR, height=4),

                # Datas + Botão Direto
                ft.Row([
                    ft.Column([
                        ft.Text(f"Entrada: {order['entry_date']}", size=10, color=colors.TEXT_MUTED),
                        ft.Text(f"Prazo: {order['deadline_date']}", size=10, color=colors.COLOR_ORCAMENTO, weight=ft.FontWeight.BOLD),
                    ], spacing=0),
                    btn_action if btn_action else ft.Container()
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=4)
        )