"""WoFlV-Assistent für einen bestehenden Auftrag (Stammdaten übernommen)."""

from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.project import Project


class MeasurementPage(QWizardPage):
    def __init__(self, auftrag: Auftrag, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Aufmaß")
        self.setSubTitle(
            "Kunden- und Objektdaten werden aus dem Auftrag übernommen. "
            "Bitte nur das Aufmaß bestätigen."
        )
        layout = QVBoxLayout(self)
        summary = QLabel(
            f"<b>Auftraggeber:</b> {auftrag.client_name}<br>"
            f"<b>Objekt:</b> {auftrag.object_name}<br>"
            f"<b>Adresse:</b> {auftrag.object_address}<br>"
            f"<b>Bearbeiter:</b> {auftrag.editor}"
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)
        form = QFormLayout()
        self.measurement_on_site = QCheckBox("Aufmaß wurde durchgeführt")
        self.measurement_on_site.setChecked(True)
        self.measurement_date_edit = QDateEdit()
        self.measurement_date_edit.setCalendarPopup(True)
        self.measurement_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.measurement_date_edit.setDate(QDate.currentDate())
        form.addRow(self.measurement_on_site)
        form.addRow("Aufmaßdatum", self.measurement_date_edit)
        layout.addLayout(form)
        self.measurement_on_site.toggled.connect(self.measurement_date_edit.setEnabled)

    def apply_to_project(self, project: Project) -> Project:
        on_site = self.measurement_on_site.isChecked()
        measurement_date = None
        if on_site:
            qdate = self.measurement_date_edit.date()
            measurement_date = date(qdate.year(), qdate.month(), qdate.day())
        project.measurement_on_site = on_site
        project.measurement_date = measurement_date
        return project


class FloorsPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Geschosse")
        self.setSubTitle("Geschosse für die Wohnflächenberechnung festlegen.")
        outer = QVBoxLayout(self)
        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("Anzahl Geschosse:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 20)
        self.count_spin.setValue(2)
        self.count_spin.valueChanged.connect(self._rebuild_floor_fields)
        count_row.addWidget(self.count_spin)
        count_row.addStretch()
        outer.addLayout(count_row)
        self.fields_container = QVBoxLayout()
        outer.addLayout(self.fields_container)
        self._floor_edits: list[QLineEdit] = []
        self._rebuild_floor_fields()

    def _rebuild_floor_fields(self) -> None:
        while self.fields_container.count():
            item = self.fields_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._floor_edits.clear()
        defaults = ["Kellergeschoss", "Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss"]
        for index in range(self.count_spin.value()):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Geschoss {index + 1}:"))
            edit = QLineEdit(defaults[index] if index < len(defaults) else f"Geschoss {index + 1}")
            self._floor_edits.append(edit)
            row.addWidget(edit)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.fields_container.addWidget(wrapper)

    def floor_names(self) -> list[str]:
        return [edit.text().strip() for edit in self._floor_edits if edit.text().strip()]

    def validatePage(self) -> bool:
        if not self.floor_names():
            QMessageBox.warning(self, "Geschosse", "Bitte mindestens ein Geschoss benennen.")
            return False
        return True


class ImportPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Excel-Rohdatei")
        self.setSubTitle("Archicad-Export (.xlsx) – optional, kann später importiert werden.")
        layout = QVBoxLayout(self)
        self.path_edit = QLineEdit()
        browse = QPushButton("Datei wählen …")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.path_edit, stretch=1)
        row.addWidget(browse)
        layout.addLayout(row)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Excel importieren", "", "Excel (*.xlsx *.xls)")
        if path:
            self.path_edit.setText(path)

    def excel_path(self) -> Path | None:
        text = self.path_edit.text().strip()
        if not text:
            return None
        path = Path(text)
        return path if path.is_file() else None


class WoflvFromAuftragWizard(QWizard):
    def __init__(self, auftrag: Auftrag, project: Project, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Wohnflächenberechnung – Auftrag")
        self.setMinimumSize(560, 420)
        self._project = project
        self.measurement_page = MeasurementPage(auftrag)
        self.floors_page = FloorsPage()
        self.import_page = ImportPage()
        self.addPage(self.measurement_page)
        self.addPage(self.floors_page)
        self.addPage(self.import_page)

    def get_project(self) -> Project:
        return self.measurement_page.apply_to_project(self._project)

    def get_floor_names(self) -> list[str]:
        return self.floors_page.floor_names()

    def get_excel_path(self) -> Path | None:
        return self.import_page.excel_path()
