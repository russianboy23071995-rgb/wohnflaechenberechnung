"""Dialog für Dokumentenablage und Layout."""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, documents_root: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.root_edit = QLineEdit()
        self.root_edit.setText(documents_root)
        browse = QPushButton("Ordner wählen …")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.root_edit, stretch=1)
        row.addWidget(browse)
        form.addRow("Dokumentenablage", row)
        hint = QLabel(
            "Unterordner: Angebote, Rechnungen, Wohnflaechenberechnung. "
            "Angebote und Rechnungen werden dort automatisch abgelegt."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintText")
        layout.addLayout(form)
        layout.addWidget(hint)

        layout_hint = QLabel(
            "Dashboard-Breite und Projektpanel-Breite können am rechten Rand "
            "per Maus gezogen werden. Mit der Schaltfläche unten stellen Sie "
            "die Standardansicht wieder her."
        )
        layout_hint.setWordWrap(True)
        layout_hint.setObjectName("hintText")
        layout.addWidget(layout_hint)

        self.restore_layout_btn = QPushButton("Standardansicht wiederherstellen")
        self.restore_layout_btn.setObjectName("secondaryButton")
        self.restore_layout_btn.clicked.connect(self._on_restore_layout)
        layout.addWidget(self.restore_layout_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._restore_layout_requested = False

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Dokumentenablage wählen", self.root_edit.text())
        if path:
            self.root_edit.setText(path)

    def _on_restore_layout(self) -> None:
        self._restore_layout_requested = True

    def documents_root(self) -> str:
        return self.root_edit.text().strip()

    def restore_layout_requested(self) -> bool:
        return self._restore_layout_requested
