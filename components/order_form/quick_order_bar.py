"""Formulário completo de cadastro de pedido."""

from __future__ import annotations

import flet as ft

from controllers.order_form_controller import OrderFormController
from core import colors
from components.order_form.components_picker import ComponentsPicker
from components.order_form.order_spec_section import OrderSpecSection
from components.order_form.reseller_section import ResellerSection
from components.order_form.service_spec_section import ServiceSpecSection
from utils.flet_compat import safe_update
from utils.ui_theme import S4, field_style, make_primary_button, page_container, page_header


class QuickOrderBar(ft.Container):
    """Orquestra seções do formulário de pedido."""

    def __init__(self, stages, on_save_callback, page: ft.Page | None = None):
        self.stages = stages
        self.on_save_callback = on_save_callback
        self.app_page = page
        self.controller = OrderFormController()

        input_style = field_style()
        readonly_style = field_style(read_only=True)
        digits_only_filter = (
            ft.NumbersOnlyInputFilter()
            if hasattr(ft, "NumbersOnlyInputFilter")
            else ft.InputFilter(regex_string=r"^[0-9]*$")
        )
        decimal_filter = ft.InputFilter(regex_string=r"^[0-9\,\.]*$")

        self.reseller_section = ResellerSection(input_style, readonly_style)
        self.reseller_section.on_reseller_change = self.controller.resolve_reseller_profile

        self.order_spec_section = OrderSpecSection(input_style, digits_only_filter)
        self.components_picker = ComponentsPicker(input_style, self.controller, page=page)
        self.components_picker.on_selection_changed = self._sync_description
        self.service_spec_section = ServiceSpecSection(input_style, decimal_filter)

        self.lbl_error = ft.Text("", size=12, color=colors.ERROR, visible=False)
        self.btn_generate_order = make_primary_button(
            "Gerar Ordem de Serviço",
            self._save,
            icon=getattr(ft.Icons, "CHECK_ROUNDED", None) or "check",
            height=44,
        )

        form_column = ft.Column(
            [
                ft.Row(
                    [
                        page_header(
                            "Cadastro de Pedido",
                            "Preencha as seções abaixo para gerar uma nova ordem de serviço.",
                        ),
                        self.lbl_error,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                self.reseller_section,
                self.order_spec_section,
                self.components_picker,
                self.service_spec_section,
                ft.Row([self.btn_generate_order], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=S4,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        super().__init__(
            expand=True,
            content=page_container(form_column, scroll=False),
        )

    def _sync_description(self, summary: str) -> None:
        if self.order_spec_section.get_values().get("service_type") == "componentes":
            self.service_spec_section.set_description(summary)

    def _collect_form_data(self) -> dict:
        form_data = {}
        form_data.update(self.reseller_section.get_values())
        form_data.update(self.order_spec_section.get_values())
        form_data.update(self.service_spec_section.get_values())
        return form_data

    def _save(self, _e):
        self.reseller_section.hide_suggestions()
        self._clear_validation()

        form_data = self._collect_form_data()
        valid, error, error_fields = self.controller.validate(form_data)
        if not valid:
            self.lbl_error.value = error
            self.lbl_error.visible = True
            self._apply_validation_errors(error_fields)
            safe_update(self)
            return

        success, persist_error = self.controller.save(form_data)
        if not success:
            self.lbl_error.value = persist_error
            self.lbl_error.visible = True
            safe_update(self)
            return

        self.lbl_error.visible = False
        self._reset_form()
        self.on_save_callback()

    def _apply_validation_errors(self, error_fields: set[str]) -> None:
        box2_fields = error_fields & {"order_number", "deadline_days", "service_type"}
        if "reseller_name" in error_fields:
            self.reseller_section.mark_invalid()
        if box2_fields:
            self.order_spec_section.mark_invalid_fields(box2_fields)
        if "components" in error_fields:
            self.components_picker.mark_invalid()
        if "description" in error_fields:
            self.service_spec_section.mark_invalid()

    def _clear_validation(self) -> None:
        self.reseller_section.clear_validation()
        self.order_spec_section.clear_validation()
        self.service_spec_section.clear_validation()
        self.components_picker.clear_validation()

    def _reset_form(self) -> None:
        self.reseller_section.reset()
        self.order_spec_section.reset()
        self.service_spec_section.reset()
        self.components_picker.reset()
        safe_update(self)
