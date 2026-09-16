"""Hilfsfunktionen für die Desktop-Oberfläche."""

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


def open_export_location(file_path: Path) -> None:
    """Öffnet den Ordner der Exportdatei im Datei-Explorer."""
    resolved = Path(file_path).resolve()
    folder = resolved.parent if resolved.is_file() else resolved

    if sys.platform == "win32":
        if resolved.is_file():
            subprocess.run(
                ["explorer", "/select,", str(resolved)],
                check=False,
            )
        else:
            subprocess.run(["explorer", str(folder)], check=False)
        return

    QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
