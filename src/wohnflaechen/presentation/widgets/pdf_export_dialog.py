"""Dialog zur Auswahl des PDF-Exportlayouts."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from wohnflaechen.domain.enums.pdf_layout import PdfLayout


class PdfExportDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PDF exportieren")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)

        hint = QLabel(
            "Wählen Sie das Layout für den Export. "
            "„Bauantrag“ entspricht dem klassischen WoFlV-Aufbau mit Plankopf "
            "(Objekt, Bauherr, Maßnahme) und getrennten Wohn-/Nutzflächen."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintText")
        layout.addWidget(hint)

        self.layout_combo = QComboBox()
        for layout_option in PdfLayout:
            self.layout_combo.addItem(layout_option.label, layout_option.value)
        layout.addWidget(self.layout_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_layout(self) -> PdfLayout:
        value = self.layout_combo.currentData()
        return PdfLayout(value)
