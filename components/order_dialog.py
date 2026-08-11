import flet as ft
from core import colors
from core.database import add_order

class OrderDialog(ft.AlertDialog):
    def __init__(self, stages, on_save_callback):
        self.stages = stages
        self.on_save_callback = on_save_callback

        self.txt_order_num = ft.TextField(label="Nº do Pedido", height=40, border_color=colors.BORDER_COLOR, bgcolor=colors.BG_SURFACE_LIGHT)
        self.txt_reseller = ft.TextField(label="Nome da Revenda", height=40, border_color=colors.BORDER_COLOR, bgcolor=colors.BG_SURFACE_LIGHT)
        self.txt_value = ft.TextField(label="Valor (R$)", height=40, border_color=colors.BORDER_COLOR, bgcolor=colors.BG_SURFACE_LIGHT)
        self.txt_entry_date = ft.TextField(label="Data de Entrada", hint_text="DD/MM/AAAA", height=40, border_color=colors.BORDER_COLOR, bgcolor=colors.BG_SURFACE_LIGHT)
        self.txt_deadline = ft.TextField(label="Prazo de Conclusão", hint_text="DD/MM/AAAA", height=40, border_color=colors.BORDER_COLOR, bgcolor=colors.BG_SURFACE_LIGHT)
        self.dd_status = ft.Dropdown(
            label="Etapa Inicial",
            value="Proposta",
            options=[ft.dropdown.Option(s) for s in self.stages],
            height=40,
            border_color=colors.BORDER_COLOR,
            bgcolor=colors.BG_SURFACE_LIGHT
        )

        super().__init__(
            modal=True,
            title=ft.Text("Novo Pedido de Empresa", color=colors.TEXT_PRIMARY, size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.txt_order_num,
                self.txt_reseller,
                self.txt_value,
                self.txt_entry_date,
                self.txt_deadline,
                self.dd_status
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=self._cancel),
                ft.ElevatedButton("Salvar Pedido", bgcolor=colors.PRIMARY, color=colors.TEXT_PRIMARY, on_click=self._save)
            ]
        )

    def _cancel(self, e):
        self.open = False
        self.page.update()

    def _save(self, e):
        try:
            val = float(self.txt_value.value.replace(".", "").replace(",", ".")) if self.txt_value.value else 0.0
            add_order(
                order_number=self.txt_order_num.value or "000",
                reseller_name=self.txt_reseller.value or "Sem Revenda",
                value=val,
                entry_date=self.txt_entry_date.value or "--/--/----",
                deadline_date=self.txt_deadline.value or "--/--/----",
                status=self.dd_status.value
            )
            self.open = False
            self._reset_fields()
            self.on_save_callback()
        except ValueError:
            pass

    def _reset_fields(self):
        self.txt_order_num.value = ""
        self.txt_reseller.value = ""
        self.txt_value.value = ""
        self.txt_entry_date.value = ""
        self.txt_deadline.value = ""