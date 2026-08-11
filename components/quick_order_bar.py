from datetime import datetime, timedelta
import flet as ft
from core import colors
from core.database import add_order, search_reseller_profiles, get_profile_by_exact_name, generate_random_profile

def make_padding_symmetric(horizontal=0, vertical=0):
    if hasattr(ft, "Padding"):
        return ft.Padding(horizontal, vertical, horizontal, vertical)
    return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)

def add_business_days(from_date: datetime, num_days: int) -> datetime:
    current = from_date
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current

class QuickOrderBar(ft.Container):
    def __init__(self, stages, on_save_callback):
        self.stages = stages
        self.on_save_callback = on_save_callback
        self._is_updating = False

        # Padronização rigorosa para todos os inputs
        input_style = dict(
            height=38,
            content_padding=make_padding_symmetric(horizontal=10, vertical=0),
            border_color=colors.BORDER_COLOR,
            bgcolor=colors.BG_SURFACE_LIGHT,
            text_style=ft.TextStyle(size=12, color=colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=11, color=colors.TEXT_SECONDARY)
        )

        readonly_style = dict(
            height=38,
            content_padding=make_padding_symmetric(horizontal=10, vertical=0),
            border_color=colors.BORDER_COLOR,
            bgcolor=colors.BG_SURFACE,
            read_only=True,
            text_style=ft.TextStyle(size=12, color=colors.TEXT_SECONDARY),
            label_style=ft.TextStyle(size=11, color=colors.TEXT_MUTED)
        )

        digits_only_filter = ft.NumbersOnlyInputFilter() if hasattr(ft, "NumbersOnlyInputFilter") else ft.InputFilter(regex_string=r"^[0-9]*$")
        decimal_filter = ft.InputFilter(regex_string=r"^[0-9\,\.]*$")

        # --- BOX 1: IDENTIFICAÇÃO DA REVENDA ---
        self.txt_reseller = ft.TextField(label="Nome da Revenda *", on_change=self._on_reseller_change, **input_style)
        self.txt_phone = ft.TextField(label="Telefone (Auto)", hint_text="Aguardando revenda...", **readonly_style)
        self.txt_address = ft.TextField(label="Endereço de Entrega (Auto)", hint_text="Aguardando revenda...", **readonly_style)

        self.suggestions_box = ft.Column(spacing=4)
        self.suggestions_container = ft.Container(
            content=self.suggestions_box,
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=ft.Border.all(1, colors.PRIMARY) if hasattr(ft, "Border") else None,
            border_radius=6,
            padding=6,
            visible=False
        )

        # --- BOX 2: ESPECIFICAÇÕES (LINHA 1: SERVIÇO, Nº PEDIDO, MEDIDAS, PRAZO, BOTÃO) ---
        self.dd_service_type = ft.Dropdown(
            label="Tipo de Serviço *",
            value="tecido",
            options=[
                ft.dropdown.Option("tecido", text="Tecido (Cortina/Persiana)"),
                ft.dropdown.Option("rolo", text="Cortina Rolô (Em breve)"),
                ft.dropdown.Option("manutencao", text="Manutenção (Em breve)")
            ],
            **input_style
        )
        self.dd_service_type.on_change = self._on_service_type_change

        self.txt_order_num = ft.TextField(label="Nº Pedido *", input_filter=digits_only_filter, keyboard_type=ft.KeyboardType.NUMBER, **input_style)
        self.txt_width = ft.TextField(label="Largura (m) *", hint_text="2.50", value="2.50", input_filter=decimal_filter, **input_style)
        self.txt_height = ft.TextField(label="Altura (m) *", hint_text="2.80", value="2.80", input_filter=decimal_filter, **input_style)
        
        self.dd_deadline_days = ft.Dropdown(
            label="Prazo *",
            value="3",
            options=[ft.dropdown.Option(str(i), text=f"{i} dia útil" if i == 1 else f"{i} dias úteis") for i in range(1, 8)],
            text_size=12,
            **input_style
        )

        btn_icon = getattr(ft.Icons, "ADD_ROUNDED", None) or getattr(ft.Icons, "ADD", None) or "add"
        self.btn_add = ft.IconButton(
            icon=btn_icon,
            icon_color=colors.TEXT_PRIMARY,
            bgcolor=colors.PRIMARY,
            icon_size=20,
            width=38,
            height=38,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None
            ),
            tooltip="Adicionar Pedido",
            on_click=self._save
        )

        # --- BOX 2: ESPECIFICAÇÕES (LINHA 2: DESCRIÇÃO EXTENSA LOGO ABAIXO) ---
        self.txt_description = ft.TextField(
            label="Descrição Detalhada / Especificações do Serviço *", 
            hint_text="Ex: Tecido Voil Flame com bainha de 10cm...", 
            value="Tecido Voil Flame com bainha dupla e trilho suíço",
            **input_style
        )

        self.lbl_error = ft.Text("", size=11, color="#F85149", visible=False)
        border_all = ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else ft.border.all(1, colors.BORDER_COLOR)

        # 1. CONTAINER IDENTIFICAÇÃO REVENDA
        box_reseller = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=border_all,
            border_radius=8,
            padding=10,
            content=ft.Column([
                ft.Text("1. IDENTIFICAÇÃO DA REVENDA", size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_SECONDARY),
                ft.ResponsiveRow([
                    ft.Container(self.txt_reseller, col={"sm": 12, "md": 4}),
                    ft.Container(self.txt_phone, col={"sm": 6, "md": 3}),
                    ft.Container(self.txt_address, col={"sm": 6, "md": 5}),
                ], run_spacing=8, spacing=8),
                self.suggestions_container
            ], spacing=8)
        )

        # 2. CONTAINER ESPECIFICAÇÕES DO PEDIDO (GRID HARMONIOSO DE 2 LINHAS)
        box_budget = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=border_all,
            border_radius=8,
            padding=10,
            content=ft.Column([
                ft.Text("2. ESPECIFICAÇÕES DO PEDIDO", size=10, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                
                # Linha 1: Serviço, Nº Pedido, Medidas, Prazo e Ação
                ft.ResponsiveRow([
                    ft.Container(self.dd_service_type, col={"sm": 12, "md": 3}),
                    ft.Container(self.txt_order_num, col={"sm": 6, "md": 2}),
                    ft.Container(self.txt_width, col={"sm": 6, "md": 2}),
                    ft.Container(self.txt_height, col={"sm": 6, "md": 2}),
                    ft.Container(self.dd_deadline_days, col={"sm": 10, "md": 2}),
                    ft.Container(self.btn_add, col={"sm": 2, "md": 1}),
                ], run_spacing=8, spacing=10),
                
                # Linha 2: Descrição Detalhada
                ft.ResponsiveRow([
                    ft.Container(self.txt_description, col={"sm": 12, "md": 12})
                ], run_spacing=8, spacing=15)
            ], spacing=25)
        )

        super().__init__(
            content=ft.Column([
                ft.Row([
                    ft.Text("CADASTRO E DETALHAMENTO DE PEDIDO", size=12, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    self.lbl_error
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                box_reseller,
                box_budget
            ], spacing=10)
        )

    def _on_service_type_change(self, e):
        if self.dd_service_type.value == "tecido":
            self.txt_width.disabled = False
            self.txt_height.disabled = False
        else:
            self.txt_width.disabled = True
            self.txt_height.disabled = True
            self.txt_description.value = f"Pedido padrão para {self.dd_service_type.value}"
        self.update()

    def _on_reseller_change(self, e):
        if self._is_updating:
            return

        name = (self.txt_reseller.value or "").strip()
        if len(name) < 2:
            self.txt_phone.value = ""
            self.txt_address.value = ""
            self.suggestions_container.visible = False
            self.update()
            return

        existing = get_profile_by_exact_name(name)
        if existing:
            self.txt_phone.value = existing.get("phone", "")
            self.txt_address.value = existing.get("address", "")
        else:
            gen_phone, gen_addr = generate_random_profile(name)
            self.txt_phone.value = gen_phone
            self.txt_address.value = gen_addr

        profiles = search_reseller_profiles(name, limit=3)
        if profiles:
            self.suggestions_box.controls.clear()
            for profile in profiles:
                p_name = profile["reseller_name"]
                p_phone = profile.get("phone", "")
                p_addr = profile.get("address", "")
                
                item = ft.Container(
                    content=ft.Row([
                        ft.Text(f"🏢 {p_name}", weight=ft.FontWeight.BOLD, size=12, color=colors.TEXT_PRIMARY),
                        ft.Text(f"📍 {p_addr}", size=11, color=colors.TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=make_padding_symmetric(horizontal=10, vertical=6),
                    border_radius=4,
                    bgcolor=colors.BG_SURFACE,
                    on_click=lambda e, n=p_name, p=p_phone, a=p_addr: self._select_profile(n, p, a)
                )
                self.suggestions_box.controls.append(item)

            self.suggestions_container.visible = True
        else:
            self.suggestions_container.visible = False

        self.update()

    def _select_profile(self, reseller_name: str, phone: str, address: str):
        self._is_updating = True
        self.txt_reseller.value = reseller_name
        self.txt_phone.value = phone
        self.txt_address.value = address
        self.suggestions_container.visible = False
        self.update()
        self._is_updating = False

    def _save(self, e):
        self.suggestions_container.visible = False
        required_fields = [
            (self.txt_reseller, "Revenda"),
            (self.txt_order_num, "Nº do Pedido"),
            (self.dd_deadline_days, "Prazo"),
            (self.txt_description, "Descrição")
        ]

        for field, _ in required_fields:
            field.border_color = colors.BORDER_COLOR

        missing = [name for field, name in required_fields if not (field.value or "").strip()]
        if missing:
            for field, _ in required_fields:
                if not (field.value or "").strip():
                    field.border_color = "#F85149"
            self.lbl_error.value = "Preencha os campos obrigatórios (*)"
            self.lbl_error.visible = True
            self.update()
            return

        now = datetime.now()
        today_str = now.strftime("%d/%m/%Y")
        days_count = int(self.dd_deadline_days.value)
        deadline_dt = add_business_days(now, days_count)
        deadline_str = deadline_dt.strftime("%d/%m/%Y")

        add_order(
            order_number=self.txt_order_num.value.strip(),
            reseller_name=self.txt_reseller.value.strip(),
            phone=self.txt_phone.value,
            address=self.txt_address.value,
            value=0.0,
            entry_date=today_str,
            deadline_date=deadline_str,
            description=self.txt_description.value.strip(),
            width=self.txt_width.value.strip() if self.txt_width.value else "",
            height=self.txt_height.value.strip() if self.txt_height.value else "",
            status="Orçamento"
        )
        self.lbl_error.visible = False
        self._reset_fields()
        self.on_save_callback()

    def _reset_fields(self):
        self._is_updating = True
        self.txt_order_num.value = ""
        self.txt_phone.value = ""
        self.txt_address.value = ""
        self.txt_reseller.value = ""
        self.txt_width.value = "2.50"
        self.txt_height.value = "2.80"
        self.dd_deadline_days.value = "3"
        self.txt_description.value = "Tecido Voil Flame com bainha dupla e trilho suíço"
        self.suggestions_container.visible = False
        self.update()
        self._is_updating = False