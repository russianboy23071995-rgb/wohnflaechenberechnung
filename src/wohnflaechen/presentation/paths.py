"""Pfade zu UI- und PDF-Ressourcen (Entwicklung und PyInstaller-Bundle)."""

import sys
from pathlib import Path


def presentation_dir() -> Path:
    """Verzeichnis `presentation` – Templates, Static, Widgets."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "wohnflaechen" / "presentation"
    return Path(__file__).resolve().parent


def pdf_templates_dir() -> Path:
    return presentation_dir() / "pdf" / "templates"


def pdf_static_dir() -> Path:
    return presentation_dir() / "pdf" / "static"


def pdf_static_file(name: str) -> Path:
    return pdf_static_dir() / name
