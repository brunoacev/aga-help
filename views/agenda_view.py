"""View de importação de contatos VCF."""

from __future__ import annotations

import flet as ft

from core import colors
from core.services.contact_service import import_vcf_contacts
from utils.flet_compat import safe_update
from utils.ui_theme import S3, S4, field_style, make_primary_button, page_container, page_header, section_card


class AgendaView(ft.Container):
    """Importação e gerenciamento de contatos via VCF."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        vcf_style = field_style()
        vcf_style.update(dict(min_lines=8, max_lines=14, multiline=True))

        self.txt_vcf_input = ft.TextField(
            label="Cole o conteúdo do arquivo de contatos (.VCF) aqui",
            **vcf_style,
        )
        self.lbl_agenda_msg = ft.Text("", size=12, color=colors.PRIMARY)

        btn_import = make_primary_button(
            "Importar Contatos VCF",
            self._process_import,
            icon=getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or "upload",
        )

        card_body = section_card(
            "Importação VCF",
            ft.Column(
                [
                    self.txt_vcf_input,
                    ft.Row([btn_import, self.lbl_agenda_msg], spacing=S3, wrap=True),
                ],
                spacing=S4,
            ),
        )

        super().__init__(
            expand=True,
            content=page_container(
                ft.Column(
                    [
                        page_header(
                            "Ações Agenda",
                            "Importe contatos VCF para alimentar o autocompletar de revendas.",
                        ),
                        card_body,
                    ],
                    spacing=S4,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        )

    def _process_import(self, _e):
        vcf_data = (self.txt_vcf_input.value or "").strip()
        count, error = import_vcf_contacts(vcf_data)
        if error:
            self.lbl_agenda_msg.value = error
            self.lbl_agenda_msg.color = colors.ERROR
        else:
            self.lbl_agenda_msg.value = f"Importação concluída! {count} novos contatos salvos."
            self.lbl_agenda_msg.color = colors.SUCCESS
            self.txt_vcf_input.value = ""
        safe_update(self, self.app_page)
