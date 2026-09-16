"""Objekttexte bearbeiten."""

from PySide6.QtWidgets import QLabel, QTabWidget, QTextEdit, QVBoxLayout, QWidget

from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType


class TextBlocksWidget(QWidget):
    """Freitextfelder für Objektinformationen."""

    def __init__(
        self, text_block_service: TextBlockService, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._text_block_service = text_block_service
        self._project_id: int | None = None
        self._editors: dict[TextBlockType, QTextEdit] = {}
        self._blocks: dict[TextBlockType, TextBlock] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        info = QLabel(
            "Objektbeschreibung, Methodik, Haftung und Hinweise erscheinen im PDF. "
            "Die Vorbemerkungen (Variante Aufmaß / Variante Pläne) bearbeiten Sie unter "
            "Projekt → Vorbemerkungen bearbeiten."
        )
        info.setWordWrap(True)
        info.setObjectName("hintText")
        layout.addWidget(info)

        self.tabs = QTabWidget()
        for block_type in TextBlockType:
            if block_type.is_preface:
                continue
            editor = QTextEdit()
            self._editors[block_type] = editor
            self.tabs.addTab(editor, block_type.label)
        layout.addWidget(self.tabs)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self.refresh()

    def refresh(self) -> None:
        self._blocks.clear()
        for block_type, editor in self._editors.items():
            if self._project_id is None:
                editor.clear()
                continue
            block = self._text_block_service.get_text_block(self._project_id, block_type)
            self._blocks[block_type] = block
            editor.setPlainText(block.content)

    def save_all(self) -> None:
        if self._project_id is None:
            return
        for block_type, editor in self._editors.items():
            block = self._blocks.get(block_type)
            if block is None:
                block = TextBlock(project_id=self._project_id, block_type=block_type)
            block.content = editor.toPlainText()
            saved = self._text_block_service.save_text_block(block)
            self._blocks[block_type] = saved
