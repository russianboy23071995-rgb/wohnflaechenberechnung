"""Dialog für Rechnung erstellen / bearbeiten."""

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QDateEdit,
)

from wohnflaechen.domain.entities.invoice import Invoice


class InvoiceDialog(QDialog):
    def __init__(self, invoice: Invoice, parent=None) -> None:
        super().__init__(parent)
        self._invoice = invoice
        self.setWindowTitle("Rechnung")
        self.setMinimumWidth(560)
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.number_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.service_edit = QTextEdit()
        self.service_edit.setMinimumHeight(120)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" EUR")
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Rechnungsnummer", self.number_edit)
        form.addRow("Datum", self.date_edit)
        form.addRow("Leistung", self.service_edit)
        form.addRow("Rechnungsbetrag", self.price_spin)
        form.addRow("Bemerkungen", self.notes_edit)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self) -> None:
        self.number_edit.setText(self._invoice.number)
        if self._invoice.date:
            self.date_edit.setDate(
                QDate(self._invoice.date.year, self._invoice.date.month, self._invoice.date.day)
            )
        else:
            self.date_edit.setDate(QDate.currentDate())
        self.service_edit.setPlainText(self._invoice.service_description)
        self.price_spin.setValue(self._invoice.price)
        self.notes_edit.setPlainText(self._invoice.notes)

    def _on_accept(self) -> None:
        if not self.number_edit.text().strip():
            QMessageBox.warning(self, "Pflichtfeld", "Bitte Rechnungsnummer eingeben.")
            return
        self.accept()

    def get_invoice(self) -> Invoice:
        qdate = self.date_edit.date()
        self._invoice.number = self.number_edit.text().strip()
        self._invoice.date = date(qdate.year(), qdate.month(), qdate.day())
        self._invoice.service_description = self.service_edit.toPlainText().strip()
        self._invoice.price = self.price_spin.value()
        self._invoice.notes = self.notes_edit.toPlainText().strip()
        return self._invoice
