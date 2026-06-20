"""Application Bootstrap."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wohnflaechen.application.app_context import AppContext
from wohnflaechen.presentation.main_window import MainWindow

_LOGO_PATH = Path(__file__).parent / "pdf" / "static" / "logo_horizontal.png"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Wohnflächenberechnung")
    app.setOrganizationName("NOVIKOV PLAN & Maß")
    if _LOGO_PATH.is_file():
        app.setWindowIcon(QIcon(str(_LOGO_PATH)))

    context = AppContext()
    window = MainWindow(context)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
