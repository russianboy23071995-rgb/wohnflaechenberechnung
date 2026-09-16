"""Dialog für Auftragsstammdaten (Bearbeiten aus dem Auftrag-Hub)."""



from PySide6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QVBoxLayout



from wohnflaechen.domain.entities.auftrag import Auftrag

from wohnflaechen.presentation.widgets.auftrag_form_widget import AuftragFormWidget





class AuftragDialog(QDialog):

    def __init__(self, auftrag: Auftrag | None = None, parent=None) -> None:

        super().__init__(parent)

        self._auftrag = auftrag or Auftrag()

        self.setWindowTitle("Auftrag bearbeiten" if auftrag else "Neuer Auftrag")

        self.setMinimumWidth(620)

        self._build_ui()

        self.form.load_auftrag(self._auftrag)



    def _build_ui(self) -> None:

        layout = QVBoxLayout(self)

        layout.setSpacing(16)

        self.form = AuftragFormWidget()

        layout.addWidget(self.form)

        buttons = QDialogButtonBox(

            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        )

        buttons.accepted.connect(self._on_accept)

        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)



    def _on_accept(self) -> None:

        error = self.form.validate()

        if error:

            QMessageBox.warning(self, "Pflichtfeld", error)

            return

        self.accept()



    def get_auftrag(self) -> Auftrag:

        return self.form.build_auftrag(self._auftrag)


