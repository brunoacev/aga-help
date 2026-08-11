from datetime import datetime, timedelta
import flet as ft
from core import colors
from core.components_data import COMPONENTS_CATALOG
from core.database import add_order, search_reseller_profiles, get_profile_by_exact_name, generate_random_profile

def get_alignment_center():
    if hasattr(ft, "Alignment"):
        return ft.Alignment(0, 0)
    if hasattr(ft, "alignment") and hasattr(ft.alignment, "CENTER"):
        return ft.alignment.CENTER
    return "center"

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
        self.selected_components = []

        input_style = dict(
            height=45,
            content_padding=make_padding_symmetric(horizontal=10, vertical=0),
            border_color=colors.BORDER_COLOR,
            bgcolor=colors.BG_SURFACE_LIGHT,
            text_style=ft.TextStyle(size=12, color=colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=11, color=colors.TEXT_SECONDARY)
        )

        readonly_style = dict(
            height=45,
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

        # --- BOX 2: ESPECIFICAÇÃO DO PEDIDO ---
        self.txt_order_num = ft.TextField(label="Nº Pedido *", input_filter=digits_only_filter, keyboard_type=ft.KeyboardType.NUMBER, **input_style)
        
        self.dd_service_type = ft.Dropdown(
            label="Tipo de Serviço *",
            value="componentes",
            options=[
                ft.dropdown.Option("componentes", text="Venda de Peças"),
                ft.dropdown.Option("rolo", text="Serviço em Cortina Rolô"),
                ft.dropdown.Option("horizontal", text="Serviço em Cortina Horizontal")
            ],
            **input_style
        )

        self.dd_deadline_days = ft.Dropdown(
            label="Prazo *",
            value="3",
            options=[ft.dropdown.Option(str(i), text=f"{i} dia útil" if i == 1 else f"{i} dias úteis") for i in range(1, 8)],
            text_size=12,
            **input_style
        )

        # --- BOX 3: ADIÇÃO DE COMPONENTES ---
        self.txt_component_search = ft.TextField(
            label="Buscar por Código ou Nome do Componente",
            hint_text="Ex: 5060, Comando, Suporte, Bandô...",
            on_change=self._filter_components,
            expand=True,
            **input_style
        )

        self.components_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        self.components_table_container = ft.Container(
            content=self.components_column,
            height=95
        )

        self.selected_items_column = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
        self.selected_items_container = ft.Container(
            content=self.selected_items_column,
            height=140,
            expand=True,
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else None,
            border_radius=6,
            padding=6
        )

        # --- BOX 4: ESPECIFICAÇÃO DO SERVIÇO ---
        self.txt_num_order = ft.TextField(label="Pedido Original", hint_text="Ex: 333333", input_filter=decimal_filter, **input_style)
        self.txt_width = ft.TextField(label="Largura (m)", hint_text="Ex: 2.50", input_filter=decimal_filter, **input_style)
        self.txt_height = ft.TextField(label="Altura (m)", hint_text="Ex: 2.80", input_filter=decimal_filter, **input_style)
        self.txt_value = ft.TextField(label="Valor Total (R$)", hint_text="Ex: 150.00", input_filter=decimal_filter, **input_style)

        self.txt_description = ft.TextField(
            label="Descrição Detalhada / Especificações do Serviço *", 
            hint_text="Digite aqui as observações ou especificações técnicas do serviço...", 
            **input_style
        )

        # BOTÃO GERAR ORDEM DE SERVIÇO
        self.btn_generate_order = ft.ElevatedButton(
            "Gerar Ordem de Serviço",
            icon=getattr(ft.Icons, "CHECK_ROUNDED", None) or "check",
            style=ft.ButtonStyle(
                bgcolor=colors.PRIMARY,
                color=colors.TEXT_PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=8) if hasattr(ft, "RoundedRectangleBorder") else None,
                mouse_cursor=ft.MouseCursor.CLICK
            ),
            height=35,
            on_click=self._save
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

        # 2. CONTAINER ESPECIFICAÇÃO DO PEDIDO
        box_order = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=border_all,
            border_radius=8,
            padding=10,
            content=ft.Column([
                ft.Text("2. ESPECIFICAÇÃO DO PEDIDO", size=10, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                ft.ResponsiveRow([
                    ft.Container(self.txt_order_num, col={"sm": 12, "md": 4}),
                    ft.Container(self.dd_service_type, col={"sm": 12, "md": 4}),
                    ft.Container(self.dd_deadline_days, col={"sm": 12, "md": 4}),
                ], run_spacing=8, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=8)
        )

        # 3. CONTAINER ADIÇÃO DE COMPONENTES
        col_catalog = ft.Column([
            ft.Text("CATÁLOGO DE COMPONENTES", size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_MUTED),
            ft.Row([self.txt_component_search]),
            self.components_table_container
        ], spacing=6, expand=True)

        col_selected = ft.Column([
            ft.Text("ITENS ADICIONADOS AO PEDIDO", size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_MUTED),
            ft.Row([self.selected_items_container])
        ], spacing=6, expand=True)

        box_components = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=border_all,
            border_radius=8,
            padding=10,
            content=ft.Column([
                ft.Text("3. ADIÇÃO DE COMPONENTES (SISTEMA AGATEK)", size=10, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                ft.ResponsiveRow([
                    ft.Container(col_catalog, col={"sm": 12, "md": 7}),
                    ft.Container(col_selected, col={"sm": 12, "md": 5})
                ], run_spacing=10, spacing=10)
            ], spacing=8)
        )

        # 4. CONTAINER ESPECIFICAÇÃO DO SERVIÇO
        box_service = ft.Container(
            bgcolor=colors.BG_SURFACE,
            border=border_all,
            border_radius=8,
            padding=10,
            visible=True,
            content=ft.Column([
                ft.Text("4. ESPECIFICAÇÃO DO SERVIÇO", size=10, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                ft.ResponsiveRow([
                    ft.Container(self.txt_num_order, col={"sm": 6, "md": 3}),
                    ft.Container(self.txt_width, col={"sm": 6, "md": 3}),
                    ft.Container(self.txt_height, col={"sm": 6, "md": 3}),
                    ft.Container(self.txt_value, col={"sm": 6, "md": 3}),
                ], run_spacing=8, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.ResponsiveRow([
                    ft.Container(self.txt_description, col={"sm": 12, "md": 12}),
                ], run_spacing=8, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=10)
        )

        self._render_components_list(COMPONENTS_CATALOG[:2])
        self._render_selected_items()

        # MONTAGEM PRINCIPAL
        super().__init__(
            content=ft.Column([
                ft.Row([
                    ft.Text("CADASTRO E DETALHAMENTO DE PEDIDO", size=12, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    self.lbl_error
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                box_reseller,
                box_order,
                box_components,
                box_service,
                ft.Row([self.btn_generate_order], alignment=ft.MainAxisAlignment.END)
            ], spacing=10)
        )

    def _is_meter_item(self, item):
        if "unit_type" in item:
            return item["unit_type"] == "meter"
        meter_keywords = ["metro", "m²", "tubo", "bandô", "bando", "perfil", "corrente", "base", "trilho", "lâmina", "lamina"]
        name_lower = item.get("name", "").lower()
        return any(kw in name_lower for kw in meter_keywords)

    def _filter_components(self, e):
        query = (self.txt_component_search.value or "").strip().lower()
        if not query:
            filtered = COMPONENTS_CATALOG[:2]
        else:
            filtered = [
                c for c in COMPONENTS_CATALOG 
                if query in c["code"].lower() or query in c["name"].lower() or query in c["category"].lower()
            ][:2]
        self._render_components_list(filtered)
        self.update()

    def _render_components_list(self, items):
        self.components_column.controls.clear()
        if not items:
            self.components_column.controls.append(
                ft.Text("Nenhum componente encontrado no sistema.", size=11, color=colors.TEXT_MUTED)
            )
            return

        for item in items:
            is_meter = self._is_meter_item(item)

            txt_dim = ft.TextField(
                hint_text="Metros (m)" if is_meter else "N/A",
                width=100,
                height=32,
                text_size=11,
                disabled=not is_meter,
                content_padding=make_padding_symmetric(horizontal=6, vertical=0),
                border_color=colors.BORDER_COLOR,
                bgcolor=colors.BG_SURFACE_LIGHT if is_meter else colors.BG_SURFACE,
                keyboard_type=ft.KeyboardType.NUMBER
            )

            txt_qty = ft.TextField(
                value="1",
                width=45,
                height=32,
                text_size=11,
                content_padding=make_padding_symmetric(horizontal=6, vertical=0),
                border_color=colors.BORDER_COLOR,
                bgcolor=colors.BG_SURFACE_LIGHT,
                keyboard_type=ft.KeyboardType.NUMBER
            )

            btn_item_add = ft.IconButton(
                icon=getattr(ft.Icons, "ADD_ROUNDED", None) or "add",
                icon_color=colors.TEXT_PRIMARY,
                bgcolor=colors.PRIMARY,
                icon_size=16,
                width=32,
                height=32,
                mouse_cursor=ft.MouseCursor.CLICK,
                tooltip="Adicionar ao Pedido",
                on_click=lambda e, comp=item, d=txt_dim, q=txt_qty: self._add_item_to_selected(comp, d.value, q.value)
            )

            row_item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(f"{item['code']}", size=11, weight=ft.FontWeight.BOLD, color=colors.PRIMARY),
                        width=60,
                        bgcolor=colors.BG_SURFACE_LIGHT,
                        padding=make_padding_symmetric(horizontal=4, vertical=4),
                        border_radius=4,
                        alignment=get_alignment_center()
                    ),
                    ft.Text(item['name'], size=11, color=colors.TEXT_PRIMARY, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([
                        txt_dim,
                        txt_qty,
                        btn_item_add
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=make_padding_symmetric(horizontal=6, vertical=4),
                bgcolor=colors.BG_SURFACE,
                border=ft.Border.all(1, colors.BORDER_COLOR) if hasattr(ft, "Border") else None,
                border_radius=6
            )
            self.components_column.controls.append(row_item)

    def _add_item_to_selected(self, component, dim_val, qty_val):
        try:
            qty = int(qty_val) if int(qty_val) > 0 else 1
        except ValueError:
            qty = 1

        is_meter = self._is_meter_item(component)
        dim_str = (dim_val or "").strip()

        if is_meter and dim_str:
            display_text = f"{qty}x {component['code']} - {component['name']} ({dim_str}m)"
        else:
            display_text = f"{qty}x {component['code']} - {component['name']}"

        item_entry = {
            "code": component["code"],
            "name": component["name"],
            "qty": qty,
            "dim": dim_str if is_meter else "",
            "is_meter": is_meter,
            "display": display_text
        }

        self.selected_components.append(item_entry)
        self._sync_description_field()
        self._render_selected_items()
        self.update()

    def _remove_selected_item(self, index):
        if 0 <= index < len(self.selected_components):
            self.selected_components.pop(index)
            self._sync_description_field()
            self._render_selected_items()
            self.update()

    def _sync_description_field(self):
        if not self.selected_components:
            return
        items_summary = ", ".join([item["display"] for item in self.selected_components])
        self.txt_description.value = items_summary

    def _render_selected_items(self):
        self.selected_items_column.controls.clear()
        if not self.selected_components:
            self.selected_items_column.controls.append(
                ft.Text("Nenhum item adicionado ao pedido.", size=10, color=colors.TEXT_MUTED)
            )
            return

        for idx, item in enumerate(self.selected_components):
            btn_remove = ft.IconButton(
                icon=getattr(ft.Icons, "DELETE_OUTLINE", None) or "delete",
                icon_color="#F85149",
                icon_size=14,
                width=24,
                height=24,
                mouse_cursor=ft.MouseCursor.CLICK,
                tooltip="Remover Item",
                on_click=lambda e, i=idx: self._remove_selected_item(i)
            )

            row = ft.Container(
                content=ft.Row([
                    ft.Text(item["display"], size=11, color=colors.TEXT_PRIMARY, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    btn_remove
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=make_padding_symmetric(horizontal=6, vertical=2),
                bgcolor=colors.BG_SURFACE,
                border_radius=4
            )
            self.selected_items_column.controls.append(row)

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
                    ink=True,
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

        try:
            val_raw = (self.txt_value.value or "0").strip().replace("R$", "").replace(" ", "")
            if "," in val_raw:
                val_raw = val_raw.replace(".", "").replace(",", ".")
            val = float(val_raw) if val_raw else 0.0
        except ValueError:
            val = 0.0

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
            value=val,
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
        self.txt_num_order.value = ""
        self.txt_width.value = ""
        self.txt_height.value = ""
        self.txt_value.value = ""
        self.dd_deadline_days.value = "3"
        self.dd_service_type.value = "componentes"
        self.txt_description.value = ""
        self.txt_component_search.value = ""
        self.selected_components.clear()
        self._render_components_list(COMPONENTS_CATALOG[:2])
        self._render_selected_items()
        self.suggestions_container.visible = False
        self.update()
        self._is_updating = False