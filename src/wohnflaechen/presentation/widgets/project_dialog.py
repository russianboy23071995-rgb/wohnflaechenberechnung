"""Dialog zur Projektanlage und Bearbeitung."""

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.domain.entities.project import Project


class ProjectDialog(QDialog):
    """Formular für Projektstammdaten."""

    def __init__(self, project: Project | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project = project or Project()
        self.setWindowTitle("Projekt bearbeiten" if project else "Neues Projekt")
        self.setMinimumWidth(520)
        self._build_ui()
        self._load_project()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.object_name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.client_edit = QLineEdit()
        self.editor_edit = QLineEdit()

        self.measurement_on_site = QCheckBox("Aufmaß wurde durchgeführt")
        self.measurement_on_site.setChecked(True)

        self.measurement_date_edit = QDateEdit()
        self.measurement_date_edit.setCalendarPopup(True)
        self.measurement_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.measurement_date_edit.setDate(QDate.currentDate())

        self.measurement_hint = QLabel(
            "Ohne Aufmaß wird in den Vorbemerkungen (Punkt 3) der Text "
            "für Bestandsunterlagen verwendet."
        )
        self.measurement_hint.setWordWrap(True)
        self.measurement_hint.setStyleSheet("color: #555; font-size: 9pt;")

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)

        form.addRow("Projektname", self.name_edit)
        form.addRow("Objektbezeichnung", self.object_name_edit)
        form.addRow("Adresse", self.address_edit)
        form.addRow("Auftraggeber", self.client_edit)
        form.addRow("Bearbeiter", self.editor_edit)
        form.addRow(self.measurement_on_site)
        form.addRow("Aufmaßdatum", self.measurement_date_edit)
        form.addRow("", self.measurement_hint)
        form.addRow("Freie Notizen", self.notes_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.measurement_on_site.toggled.connect(self._on_measurement_toggle)
        self._on_measurement_toggle(True)

    def _on_measurement_toggle(self, checked: bool) -> None:
        self.measurement_date_edit.setEnabled(checked)

    def _load_project(self) -> None:
        self.name_edit.setText(self._project.name)
        self.object_name_edit.setText(self._project.object_name)
        self.address_edit.setText(self._project.address)
        self.client_edit.setText(self._project.client)
        self.editor_edit.setText(self._project.editor)
        self.notes_edit.setPlainText(self._project.notes)
        self.measurement_on_site.setChecked(self._project.measurement_on_site)

        if self._project.measurement_date:
            qdate = QDate(
                self._project.measurement_date.year,
                self._project.measurement_date.month,
                self._project.measurement_date.day,
            )
            self.measurement_date_edit.setDate(qdate)
        else:
            self.measurement_date_edit.setDate(QDate.currentDate())

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip() and not self.object_name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Pflichtfeld",
                "Bitte mindestens Projektname oder Objektbezeichnung eingeben.",
            )
            return
        if self.measurement_on_site.isChecked() and not self.measurement_date_edit.date().isValid():
            QMessageBox.warning(self, "Aufmaßdatum", "Bitte ein gültiges Aufmaßdatum eingeben.")
            return
        self.accept()

    def get_project(self) -> Project:
        measurement_on_site = self.measurement_on_site.isChecked()
        measurement_date = None
        if measurement_on_site:
            qdate = self.measurement_date_edit.date()
            measurement_date = date(qdate.year(), qdate.month(), qdate.day())

        self._project.name = self.name_edit.text().strip()
        self._project.object_name = self.object_name_edit.text().strip()
        self._project.address = self.address_edit.text().strip()
        self._project.client = self.client_edit.text().strip()
        self._project.editor = self.editor_edit.text().strip()
        self._project.measurement_on_site = measurement_on_site
        self._project.measurement_date = measurement_date
        self._project.measurement_note = ""
        self._project.notes = self.notes_edit.toPlainText().strip()
        return self._project
