"""Assistent für neue Wohnflächenberechnung."""

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

from wohnflaechen.domain.entities.project import Project


class ProjectInfoPage(QWizardPage):
    """Schritt 1: Objekt- und Projektdaten."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Projektdaten")
        self.setSubTitle("Objekt, Auftraggeber und Aufmaß-Angaben erfassen.")

        layout = QFormLayout(self)

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

        layout.addRow("Projektname", self.name_edit)
        layout.addRow("Objektbezeichnung", self.object_name_edit)
        layout.addRow("Adresse", self.address_edit)
        layout.addRow("Auftraggeber / Bauherr", self.client_edit)
        layout.addRow("Bearbeiter", self.editor_edit)
        layout.addRow(self.measurement_on_site)
        layout.addRow("Aufmaßdatum", self.measurement_date_edit)

        self.registerField("project_name*", self.name_edit)
        self.registerField("object_name*", self.object_name_edit)

    def validatePage(self) -> bool:
        if not self.name_edit.text().strip() and not self.object_name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Pflichtfeld",
                "Bitte mindestens Projektname oder Objektbezeichnung eingeben.",
            )
            return False
        return True

    def build_project(self) -> Project:
        measurement_on_site = self.measurement_on_site.isChecked()
        measurement_date = None
        if measurement_on_site:
            qdate = self.measurement_date_edit.date()
            measurement_date = date(qdate.year(), qdate.month(), qdate.day())

        return Project(
            name=self.name_edit.text().strip(),
            object_name=self.object_name_edit.text().strip(),
            address=self.address_edit.text().strip(),
            client=self.client_edit.text().strip(),
            editor=self.editor_edit.text().strip(),
            measurement_on_site=measurement_on_site,
            measurement_date=measurement_date,
        )


class FloorsPage(QWizardPage):
    """Schritt 2: Geschosse deklarieren."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Geschosse")
        self.setSubTitle(
            "Legen Sie die Anzahl und Bezeichnung der Geschosse fest "
            "(z. B. Kellergeschoss, Erdgeschoss, 1. Obergeschoss)."
        )

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
        defaults = [
            "Kellergeschoss",
            "Erdgeschoss",
            "1. Obergeschoss",
            "2. Obergeschoss",
            "3. Obergeschoss",
            "4. Obergeschoss",
            "5. Obergeschoss",
            "Dachgeschoss",
        ]
        count = self.count_spin.value()
        for index in range(count):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"Geschoss {index + 1}:"))
            edit = QLineEdit(
                defaults[index] if index < len(defaults) else f"Geschoss {index + 1}"
            )
            self._floor_edits.append(edit)
            row.addWidget(edit)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.fields_container.addWidget(wrapper)

    def floor_names(self) -> list[str]:
        names: list[str] = []
        for edit in self._floor_edits:
            name = edit.text().strip()
            if name:
                names.append(name)
        return names

    def validatePage(self) -> bool:
        if not self.floor_names():
            QMessageBox.warning(self, "Geschosse", "Bitte mindestens ein Geschoss benennen.")
            return False
        return True


class ImportPage(QWizardPage):
    """Schritt 3: Excel-Rohdatei."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTitle("Excel-Rohdatei")
        self.setSubTitle(
            "Archicad-Export (.xlsx) auswählen – die Räume werden in den Pool geladen."
        )

        layout = QVBoxLayout(self)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Pfad zur Excel-Rohdatei …")
        browse = QPushButton("Datei wählen …")
        browse.clicked.connect(self._browse)

        row = QHBoxLayout()
        row.addWidget(self.path_edit, stretch=1)
        row.addWidget(browse)
        layout.addLayout(row)

        hint = QLabel(
            "Die Datei kann auch später über Datei → Excel importieren nachgeladen werden."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintText")
        layout.addWidget(hint)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Archicad Excel importieren",
            "",
            "Excel-Dateien (*.xlsx *.xls)",
        )
        if path:
            self.path_edit.setText(path)

    def excel_path(self) -> Path | None:
        text = self.path_edit.text().strip()
        if not text:
            return None
        path = Path(text)
        return path if path.is_file() else None

    def validatePage(self) -> bool:
        text = self.path_edit.text().strip()
        if not text:
            return True
        path = Path(text)
        if not path.is_file():
            QMessageBox.warning(self, "Datei", "Die angegebene Excel-Datei wurde nicht gefunden.")
            return False
        return True


class NewProjectWizard(QWizard):
    """Mehrstufiger Assistent für neue Berechnungen."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Neue Wohnflächenberechnung")
        self.setMinimumSize(560, 420)

        self.info_page = ProjectInfoPage()
        self.floors_page = FloorsPage()
        self.import_page = ImportPage()

        self.addPage(self.info_page)
        self.addPage(self.floors_page)
        self.addPage(self.import_page)

    def get_project(self) -> Project:
        return self.info_page.build_project()

    def get_floor_names(self) -> list[str]:
        return self.floors_page.floor_names()

    def get_excel_path(self) -> Path | None:
        return self.import_page.excel_path()
