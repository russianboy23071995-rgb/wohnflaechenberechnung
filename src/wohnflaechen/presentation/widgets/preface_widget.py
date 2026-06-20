"""Vorbemerkungen bearbeiten."""

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.presentation.pdf.branding import PREFACE_TITLE


class PrefaceWidget(QWidget):
    """Editor für die Vorbemerkungen (Punkte 1–6) im PDF."""

    def __init__(
        self, text_block_service: TextBlockService, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._text_block_service = text_block_service
        self._project_id: int | None = None
        self._block: TextBlock | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        info = QLabel(
            f"Text erscheint im PDF unter „{PREFACE_TITLE}“. "
            "Abschnitte 1.–6. beginnen mit einer Nummerierung (z. B. „1. …“). "
            "Punkt 3 passt sich der Aufmaß-Auswahl in den Projektdaten an."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555; font-size: 9pt;")
        layout.addWidget(info)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Vorbemerkungen eingeben …")
        layout.addWidget(self.editor, stretch=1)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self.refresh()

    def refresh(self) -> None:
        if self._project_id is None:
            self._block = None
            self.editor.clear()
            return

        self._block = self._text_block_service.get_text_block(
            self._project_id, TextBlockType.PREFACE
        )
        self.editor.setPlainText(self._block.content)

    def save_all(self) -> None:
        if self._project_id is None:
            return

        block = self._block
        if block is None:
            block = TextBlock(project_id=self._project_id, block_type=TextBlockType.PREFACE)
        block.content = self.editor.toPlainText()
        self._block = self._text_block_service.save_text_block(block)
