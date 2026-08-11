import flet as ft
from core import colors

def make_padding_symmetric(horizontal=0, vertical=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    if hasattr(ft, "padding") and hasattr(ft.padding, "symmetric"):
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.only(left=horizontal, right=horizontal, top=vertical, bottom=vertical)

class OrderCard(ft.Container):
    def __init__(self, order, stages, on_move_callback, on_delete_callback):
        self.order = order
        self.stages = stages
        self.on_move_callback = on_move_callback
        self.on_delete_callback = on_delete_callback

        order_id = order["id"]
        order_number = order.get("order_number", f"#{order_id}")
        reseller_name = order.get("reseller_name", "Revenda Desconhecida")
        phone = order.get("phone", "")
        address = order.get("address", "Agatek Persianas e Cortinas de Fortaleza")
        description = order.get("description", "Sem descrição")
        width = order.get("width", "")
        height = order.get("height", "")
        current_status = order.get("status", "Orçamento")
        
        value = float(order.get("value", 0.0))
        commission = value * 0.02  # Cálculo de 2% de comissão

        formatted_value = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_commission = f"R$ {commission:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Cabeçalho do Card
        card_header = ft.Row([
            ft.Text(f"Pedido #{order_number}", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY),
            ft.Text(reseller_name, size=12, color=colors.PRIMARY, weight=ft.FontWeight.W_500)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Informações de Contato e Endereço Fixo
        contact_info = []
        if phone:
            contact_info.append(ft.Text(f"📞 {phone}", size=11, color=colors.TEXT_SECONDARY))
        contact_info.append(ft.Text(f"📍 {address}", size=11, color=colors.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS))

        # Medidas
        dimensions_text = f" 📐 {width or '?'}m x {height or '?'}m" if (width or height) else ""
        desc_text = ft.Text(f"{description}{dimensions_text}", size=11, color=colors.TEXT_SECONDARY)

        # Bloco Financeiro: Valor Total + 2% Comissão
        financial_box = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("VALOR TOTAL", size=9, color=colors.TEXT_MUTED, weight=ft.FontWeight.BOLD),
                    ft.Text(formatted_value, size=13, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                ], spacing=1),
                ft.Column([
                    ft.Text("COMISSÃO (2%)", size=9, color=colors.PRIMARY, weight=ft.FontWeight.BOLD),
                    ft.Text(formatted_commission, size=12, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                ], spacing=1, alignment=ft.MainAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=colors.BG_SURFACE_LIGHT,
            padding=make_padding_symmetric(horizontal=10, vertical=6),
            border_radius=6
        )

        # Botões de ação com ÍCONES padronizados do mesmo tamanho da lixeira (size 16)
        action_buttons = []
        
        curr_index = stages.index(current_status) if current_status in stages else 0

        # Ícone de Recuar Etapa (Voltar)
        if curr_index > 0:
            prev_stage = stages[curr_index - 1]
            action_buttons.append(
                ft.IconButton(
                    icon=getattr(ft.Icons, "ARROW_BACK_ROUNDED", None) or "arrow_back",
                    icon_color=colors.TEXT_SECONDARY,
                    icon_size=16,
                    tooltip=f"Voltar para {prev_stage}",
                    on_click=lambda _: self.on_move_callback(order_id, prev_stage)
                )
            )

        # Ícone de Avançar Etapa (Avançar)
        if curr_index < len(stages) - 1:
            next_stage = stages[curr_index + 1]
            action_buttons.append(
                ft.IconButton(
                    icon=getattr(ft.Icons, "ARROW_FORWARD_ROUNDED", None) or "arrow_forward",
                    icon_color=colors.PRIMARY,
                    icon_size=16,
                    tooltip=f"Avançar para {next_stage}",
                    on_click=lambda _: self.on_move_callback(order_id, next_stage)
                )
            )

        # Ícone da Lixeira (Excluir)
        btn_delete = ft.IconButton(
            icon=getattr(ft.Icons, "DELETE_OUTLINE", None) or "delete",
            icon_color="#F85149",
            icon_size=16,
            tooltip="Excluir Pedido",
            on_click=lambda _: self.on_delete_callback(order_id)
        )

        # Rodapé com o mesmo layout: Mover à Esquerda, Lixeira à Direita
        actions_row = ft.Row([
            ft.Row(action_buttons, spacing=2),
            btn_delete
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        border_card = ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else None

        super().__init__(
            bgcolor=colors.BG_SURFACE,
            border=border_card,
            border_radius=8,
            padding=10,
            content=ft.Column([
                card_header,
                ft.Column(contact_info, spacing=2),
                desc_text,
                financial_box,
                ft.Divider(color=colors.BORDER_COLOR, height=10),
                actions_row
            ], spacing=6)
        )