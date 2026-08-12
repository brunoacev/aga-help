"""View da agenda de contatos — importação VCF."""

from __future__ import annotations

import asyncio

import flet as ft

from core import colors
from core.services.contact_service import import_vcf_contacts, list_agenda_contacts
from utils.flet_compat import show_snackbar
from utils.vcf_io import read_vcf_from_picker_file


class AgendaView(ft.Container):
    """Tela simples de importação e listagem de contatos VCF."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.file_picker: ft.FilePicker | None = None

        self.contacts_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        self.status_text = ft.Text(
            "",
            size=12,
            color=colors.TEXT_MUTED,
        )

        upload_icon = getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or getattr(
            ft.Icons, "UPLOAD_FILE", "upload"
        )
        btn_import = ft.Button(
            content="Importar Contatos VCF",
            icon=upload_icon,
            bgcolor=colors.PRIMARY,
            color=colors.TEXT_PRIMARY,
            on_click=self._on_import_click,
        )

        super().__init__(
            expand=True,
            padding=20,
            bgcolor=colors.BG_PRIMARY,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Agenda de Contatos",
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=colors.TEXT_PRIMARY,
                    ),
                    ft.Row(controls=[btn_import]),
                    self.status_text,
                    ft.Container(content=self.contacts_list, expand=True),
                ],
                spacing=16,
                expand=True,
            ),
        )
        self._render_contacts()

    def refresh_contacts(self) -> None:
        """Atualiza a lista ao navegar para esta view."""
        self._render_contacts()
        self.app_page.update()

    def _on_import_click(self, _e) -> None:
        asyncio.create_task(self._import_vcf())

    async def _import_vcf(self) -> None:
        try:
            picker = self._get_file_picker()
            files = await picker.pick_files(
                dialog_title="Selecionar arquivo VCF",
                allow_multiple=False,
                with_data=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["vcf"],
            )
            if not files:
                return

            vcf_text, read_error = read_vcf_from_picker_file(files[0])
            if read_error:
                show_snackbar(self.app_page, read_error, success=False)
                return

            count, import_error = import_vcf_contacts(vcf_text)
            if import_error:
                show_snackbar(self.app_page, import_error, success=False)
                return

            show_snackbar(self.app_page, f"{count} contatos importados com sucesso!", success=True)
            self._render_contacts()
            self.app_page.update()
        except Exception as exc:
            show_snackbar(
                self.app_page,
                f"Não foi possível importar o arquivo: {exc}",
                success=False,
            )

    def _get_file_picker(self) -> ft.FilePicker:
        """Garante FilePicker registrado nos services da página (Flet 0.86+)."""
        if self.file_picker is not None:
            return self.file_picker

        self.file_picker = ft.FilePicker()
        services = list(getattr(self.app_page, "services", None) or [])
        if self.file_picker not in services:
            self.app_page.services = services + [self.file_picker]
        return self.file_picker

    def _render_contacts(self) -> None:
        """Carrega contatos do banco e preenche a lista."""
        self.contacts_list.controls.clear()
        try:
            contacts = list_agenda_contacts()
        except Exception as exc:
            self.status_text.value = "Erro ao carregar contatos."
            self.contacts_list.controls.append(
                ft.Text(
                    f"Falha ao ler a agenda: {exc}",
                    size=12,
                    color=colors.ERROR,
                )
            )
            return

        if not contacts:
            self.status_text.value = "Nenhum contato importado."
            self.contacts_list.controls.append(
                ft.Text(
                    "Importe um arquivo .VCF para começar.",
                    size=12,
                    color=colors.TEXT_MUTED,
                )
            )
            return

        self.status_text.value = f"{len(contacts)} contato(s) na agenda."
        for contact in contacts:
            name = contact.get("name", "—")
            phone = contact.get("phone", "") or "—"
            self.contacts_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(name, size=13, color=colors.TEXT_PRIMARY, expand=True),
                            ft.Text(phone, size=12, color=colors.TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    bgcolor=colors.BG_SURFACE,
                    border_radius=8,
                )
            )
