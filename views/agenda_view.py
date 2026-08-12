"""View de importação de contatos VCF."""

from __future__ import annotations

import asyncio

import flet as ft

from core import colors
from core.services.contact_service import import_vcf_contacts
from utils.flet_compat import get_alignment_center, safe_update, show_snackbar
from utils.ui_theme import RADIUS_LG, S3, S4, field_style, make_primary_button, page_container, page_header, section_card, text_body
from utils.vcf_io import decode_vcf_bytes, read_vcf_from_picker_file, read_vcf_text_from_path

try:
    import flet_dropzone as ftd

    HAS_FILE_DROP = True
except ImportError:
    ftd = None  # type: ignore[assignment,misc]
    HAS_FILE_DROP = False


class AgendaView(ft.Container):
    """Importação e gerenciamento de contatos via VCF."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.file_picker = ft.FilePicker()
        services = list(page.services or [])
        if self.file_picker not in services:
            page.services = services + [self.file_picker]

        vcf_style = field_style()
        vcf_style.update(dict(min_lines=8, max_lines=14, multiline=True))

        self.txt_vcf_input = ft.TextField(
            label="Cole o conteúdo do arquivo de contatos (.VCF) aqui",
            **vcf_style,
        )
        self.lbl_agenda_msg = ft.Text("", size=12, color=colors.PRIMARY)

        upload_icon = getattr(ft.Icons, "UPLOAD_FILE_ROUNDED", None) or getattr(
            ft.Icons, "UPLOAD_FILE", "upload"
        )

        self.drop_zone_inner = ft.Container(
            height=168,
            border=ft.Border(
                top=ft.BorderSide(2, colors.PRIMARY),
                right=ft.BorderSide(2, colors.PRIMARY),
                bottom=ft.BorderSide(2, colors.PRIMARY),
                left=ft.BorderSide(2, colors.PRIMARY),
            ),
            border_radius=RADIUS_LG,
            bgcolor=colors.BG_SURFACE_LIGHT,
            alignment=get_alignment_center(),
            on_hover=self._on_drop_zone_hover,
            content=ft.Column(
                [
                    ft.Icon(upload_icon, size=48, color=colors.PRIMARY),
                    text_body(
                        "Arraste e solte o arquivo .VCF aqui ou clique no botão abaixo",
                        text_align=ft.TextAlign.CENTER,
                        color=colors.TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=S3,
            ),
        )

        self.drop_zone = self._wrap_drop_zone(self.drop_zone_inner)

        btn_import = make_primary_button(
            "Importar Contatos VCF",
            self._schedule_pick_files,
            icon=upload_icon,
        )
        btn_manual_import = make_primary_button(
            "Importar texto colado",
            self._process_manual_import,
            icon=getattr(ft.Icons, "CONTENT_PASTE", None) or "paste",
        )

        manual_section = ft.ExpansionTile(
            title=ft.Text(
                "Colar conteúdo VCF manualmente",
                size=13,
                color=colors.TEXT_SECONDARY,
                weight=ft.FontWeight.W_600,
            ),
            subtitle=ft.Text(
                "Alternativa para colar o texto bruto do arquivo",
                size=11,
                color=colors.TEXT_MUTED,
            ),
            controls=[
                self.txt_vcf_input,
                ft.Row([btn_manual_import], spacing=S3),
            ],
        )

        card_body = section_card(
            "Importação VCF",
            ft.Column(
                [
                    self.drop_zone,
                    ft.Row([btn_import, self.lbl_agenda_msg], spacing=S3, wrap=True),
                    manual_section,
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

    def _wrap_drop_zone(self, content: ft.Container) -> ft.Control:
        """Envolve a área de drop com suporte nativo quando flet-dropzone está disponível."""
        if not HAS_FILE_DROP:
            return content

        return ftd.Dropzone(
            content=content,
            allowed_file_types=["vcf"],
            on_dropped=self._schedule_drop_import,
            on_entered=lambda _e: self._set_drop_zone_highlight(True),
            on_exited=lambda _e: self._set_drop_zone_highlight(False),
        )

    def _schedule_pick_files(self, _e=None) -> None:
        asyncio.create_task(self._pick_and_import_vcf())

    def _schedule_drop_import(self, e) -> None:
        asyncio.create_task(self._handle_dropped_files(e))

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
            self._apply_feedback(error, success=False)
            return

        self._process_vcf_text(vcf_text)

    async def _handle_dropped_files(self, e) -> None:
        if not e.files:
            return

        dropzone = e.control
        for dropped in e.files:
            if not dropped.name.lower().endswith(".vcf"):
                self._apply_feedback("Apenas arquivos .VCF são aceitos.", success=False)
                continue

            try:
                if hasattr(dropzone, "read_bytes"):
                    data = await dropzone.read_bytes(dropped)
                    vcf_text, error = decode_vcf_bytes(data)
                elif dropped.path:
                    vcf_text, error = read_vcf_text_from_path(dropped.path)
                else:
                    error = "Não foi possível ler o arquivo solto."
                    vcf_text = ""

                if error:
                    self._apply_feedback(error, success=False)
                    continue

                self._process_vcf_text(vcf_text)
                return
            except OSError as exc:
                self._apply_feedback(f"Erro ao ler o arquivo: {exc}", success=False)
            except Exception as exc:
                self._apply_feedback(f"Erro ao importar arquivo: {exc}", success=False)

    def _process_manual_import(self, _e) -> None:
        vcf_data = (self.txt_vcf_input.value or "").strip()
        self._process_vcf_text(vcf_data)

    def _process_vcf_text(self, vcf_text: str) -> None:
        count, error = import_vcf_contacts(vcf_text)
        if error:
            self._apply_feedback(error, success=False)
            return

        self._apply_feedback(f"{count} contatos importados com sucesso!", success=True)
        self.txt_vcf_input.value = ""

    def _apply_feedback(self, message: str, *, success: bool) -> None:
        self.lbl_agenda_msg.value = message
        self.lbl_agenda_msg.color = colors.SUCCESS if success else colors.ERROR
        show_snackbar(self.app_page, message, success=success)
        safe_update(self, self.app_page)

    def _on_drop_zone_hover(self, e) -> None:
        hovered = str(e.data).lower() == "true"
        self._set_drop_zone_highlight(hovered)

    def _set_drop_zone_highlight(self, active: bool) -> None:
        self.drop_zone_inner.bgcolor = colors.BG_HOVER if active else colors.BG_SURFACE_LIGHT
        safe_update(self.drop_zone_inner, self.app_page)
