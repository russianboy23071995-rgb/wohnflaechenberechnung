"""Application Bootstrap."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wohnflaechen.application.app_context import AppContext
from wohnflaechen.presentation.main_window import MainWindow
from wohnflaechen.presentation.paths import pdf_static_file
from wohnflaechen.presentation.pdf.weasyprint_support import check_pdf_export_available
from wohnflaechen.presentation.theme import apply_app_theme

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Wohnflächenberechnung")
    app.setOrganizationName("NOVIKOV PLAN & Maß")
    apply_app_theme(app)
    logo_path = pdf_static_file("logo_horizontal.png")
    if logo_path.is_file():
        app.setWindowIcon(QIcon(str(logo_path)))
    context = AppContext()
    window = MainWindow(context)
    window.show()

    pdf_ok, pdf_detail = check_pdf_export_available()
    if pdf_ok:
        window.statusBar().showMessage(pdf_detail, 8000)
    else:
        window.statusBar().showMessage(
            "PDF-Export nicht verfügbar – siehe Hinweis unter Hilfe → PDF-Export prüfen",
            15000,
        )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
