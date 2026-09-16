"""Vorbemerkungen bearbeiten."""

from PySide6.QtWidgets import QLabel, QTabWidget, QTextEdit, QVBoxLayout, QWidget

from wohnflaechen.application.services.preface_service import preface_block_type
from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.presentation.pdf.branding import PREFACE_TITLE


class PrefaceWidget(QWidget):
    """Editor für beide Vorbemerkungs-Varianten (Punkte 1–6) im PDF."""

    def __init__(
        self, text_block_service: TextBlockService, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._text_block_service = text_block_service
        self._project_id: int | None = None
        self._measurement_on_site = True
        self._blocks: dict[TextBlockType, TextBlock] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._info = QLabel()
        self._info.setWordWrap(True)
        self._info.setObjectName("hintText")
        layout.addWidget(self._info)

        self.tabs = QTabWidget()
        self.editor_on_site = QTextEdit()
        self.editor_on_site.setPlaceholderText("Vorbemerkungen bei durchgeführtem Aufmaß …")
        self.editor_from_plans = QTextEdit()
        self.editor_from_plans.setPlaceholderText(
            "Vorbemerkungen bei Berechnung nach vorhandenen Plänen …"
        )
        self.tabs.addTab(self.editor_on_site, "Variante 1 – Aufmaß erfolgt")
        self.tabs.addTab(self.editor_from_plans, "Variante 2 – Kein Aufmaß, vorhandene Pläne")
        layout.addWidget(self.tabs, stretch=1)
        self._update_info()

    def set_project(
        self, project_id: int | None, measurement_on_site: bool | None = None
    ) -> None:
        self._project_id = project_id
        if measurement_on_site is not None:
            self._measurement_on_site = measurement_on_site
        self.refresh()

    def refresh(self) -> None:
        self._blocks.clear()
        self._update_info()
        if self._project_id is None:
            self.editor_on_site.clear()
            self.editor_from_plans.clear()
            return

        on_site = self._text_block_service.get_text_block(
            self._project_id, TextBlockType.PREFACE_ON_SITE
        )
        from_plans = self._text_block_service.get_text_block(
            self._project_id, TextBlockType.PREFACE_FROM_PLANS
        )
        self._blocks[TextBlockType.PREFACE_ON_SITE] = on_site
        self._blocks[TextBlockType.PREFACE_FROM_PLANS] = from_plans
        self.editor_on_site.setPlainText(on_site.content)
        self.editor_from_plans.setPlainText(from_plans.content)
        self.tabs.setCurrentIndex(0 if self._measurement_on_site else 1)

    def save_all(self) -> None:
        if self._project_id is None:
            return

        self._save_variant(
            TextBlockType.PREFACE_ON_SITE, self.editor_on_site.toPlainText()
        )
        self._save_variant(
            TextBlockType.PREFACE_FROM_PLANS, self.editor_from_plans.toPlainText()
        )

        active_type = preface_block_type(self._measurement_on_site)
        active = self._blocks.get(active_type)
        if active is None:
            return
        mirror = self._text_block_service.get_text_block(
            self._project_id, TextBlockType.PREFACE
        )
        mirror.content = active.content
        self._text_block_service.save_text_block(mirror)

    def _save_variant(self, block_type: TextBlockType, content: str) -> None:
        block = self._blocks.get(block_type)
        if block is None:
            block = TextBlock(project_id=self._project_id, block_type=block_type)
        block.content = content
        self._blocks[block_type] = self._text_block_service.save_text_block(block)

    def _update_info(self) -> None:
        active = (
            "Variante 1 (Aufmaß erfolgt)"
            if self._measurement_on_site
            else "Variante 2 (kein Aufmaß, vorhandene Pläne)"
        )
        self._info.setText(
            f"Beide Textfassungen sind bearbeitbar. Im PDF unter „{PREFACE_TITLE}“ "
            f"erscheint derzeit {active}, abhängig von der Angabe „Aufmaß wurde "
            "durchgeführt“ in den Projektdaten. Abschnitte 1.–6. beginnen mit einer "
            "Nummerierung; die Titel werden fett gesetzt."
        )
