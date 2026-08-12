"""View de importação de contatos VCF."""

from __future__ import annotations

import asyncio

import flet as ft

from core import colors
from core.services.contact_service import import_vcf_contacts, list_agenda_contacts
from utils.flet_compat import make_padding_symmetric, safe_update, show_snackbar
from utils.ui_theme import (
    FONT_CAPTION,
    FONT_LABEL,
    RADIUS,
    S2,
    S3,
    S4,
    field_style,
    make_primary_button,
    page_container,
    page_header,
    section_card,
    text_caption,
)
from utils.vcf_io import read_vcf_from_picker_file


class AgendaView(ft.Container):
    """Importação e consulta de contatos via VCF."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.file_picker = ft.FilePicker()
        services = list(page.services or [])
        if self.file_picker not in services:
            page.services = services + [self.file_picker]

        search_style = field_style()
        search_style.pop("height", None)
        search_style.update(dict(hint_text="Nome ou telefone"))

        self.txt_search = ft.TextField(
            label="Buscar contatos",
            expand=True,
            on_change=self._on_search_change,
            **search_style,
        )
        self.lbl_contact_count = ft.Text("", size=FONT_CAPTION, color=colors.TEXT_MUTED)
        self.contacts_list = ft.Column(spacing=S2, scroll=ft.ScrollMode.AUTO, expand=True, tight=True)

        upload_icon = getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or getattr(
            ft.Icons, "UPLOAD_FILE", "upload"
        )
        btn_import = make_primary_button(
            "Importar Contatos VCF",
            self._schedule_pick_files,
            icon=upload_icon,
        )

        actions_row = ft.Row(
            [
                ft.Container(content=self.txt_search, expand=True),
                btn_import,
            ],
            spacing=S3,
            vertical_alignment=ft.CrossAxisAlignment.END,
            wrap=True,
        )

        contacts_panel = section_card(
            "Contatos importados",
            ft.Column(
                [
                    self.lbl_contact_count,
                    ft.Container(content=self.contacts_list, expand=True),
                ],
                spacing=S3,
                tight=True,
                expand=True,
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
                        actions_row,
                        ft.Container(content=contacts_panel, expand=True),
                    ],
                    spacing=S4,
                    tight=True,
                    expand=True,
                ),
            ),
        )
        self.refresh_contacts()

    def refresh_contacts(self) -> None:
        """Recarrega a tabela de contatos conforme o filtro atual."""
        query = (self.txt_search.value or "").strip()
        contacts = list_agenda_contacts(query)
        self.contacts_list.controls.clear()

        if not contacts:
            self.lbl_contact_count.value = "Nenhum contato encontrado."
            self.contacts_list.controls.append(
                text_caption(
                    "Importe um arquivo .VCF para começar a popular a agenda.",
                    color=colors.TEXT_MUTED,
                )
            )
        else:
            self.lbl_contact_count.value = f"{len(contacts)} contato(s) exibido(s)."
            self.contacts_list.controls.append(self._build_table_header())
            for contact in contacts:
                self.contacts_list.controls.append(self._build_contact_row(contact))

        safe_update(self.contacts_list, self.app_page)
        safe_update(self.lbl_contact_count, self.app_page)

    def _build_table_header(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Nome", size=FONT_LABEL, weight=ft.FontWeight.W_600, color=colors.TEXT_SECONDARY, width=220),
                    ft.Text("Telefone", size=FONT_LABEL, weight=ft.FontWeight.W_600, color=colors.TEXT_SECONDARY, width=140),
                    ft.Text("Endereço", size=FONT_LABEL, weight=ft.FontWeight.W_600, color=colors.TEXT_SECONDARY, expand=True),
                ],
                spacing=S3,
            ),
            padding=make_padding_symmetric(horizontal=S3, vertical=0),
        )

    def _build_contact_row(self, contact: dict) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        contact.get("name", ""),
                        size=FONT_CAPTION,
                        color=colors.TEXT_PRIMARY,
                        width=220,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        contact.get("phone", "") or "—",
                        size=FONT_CAPTION,
                        color=colors.TEXT_SECONDARY,
                        width=140,
                    ),
                    ft.Text(
                        contact.get("address", "") or "—",
                        size=FONT_CAPTION,
                        color=colors.TEXT_MUTED,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=S3,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=colors.BG_SURFACE_LIGHT,
            border=ft.Border(
                bottom=ft.BorderSide(1, colors.BORDER_COLOR),
            ),
            padding=make_padding_symmetric(horizontal=S3, vertical=S2),
            border_radius=RADIUS,
        )

    def _on_search_change(self, _e) -> None:
        self.refresh_contacts()

    def _schedule_pick_files(self, _e=None) -> None:
        asyncio.create_task(self._pick_and_import_vcf())

    async def _pick_and_import_vcf(self) -> None:
        files = await self.file_picker.pick_files(
            dialog_title="Selecionar arquivo VCF",
            allow_multiple=False,
            with_data=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["vcf"],
        )
        if not files:
            return

        vcf_text, error = read_vcf_from_picker_file(files[0])
        if error:
            show_snackbar(self.app_page, error, success=False)
            return

        count, error = import_vcf_contacts(vcf_text)
        if error:
            show_snackbar(self.app_page, error, success=False)
            return

        show_snackbar(self.app_page, f"{count} contatos importados com sucesso!", success=True)
        self.refresh_contacts()
        self.app_page.update()
