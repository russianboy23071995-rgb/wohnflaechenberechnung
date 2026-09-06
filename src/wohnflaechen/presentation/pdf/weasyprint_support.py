"""WeasyPrint / GTK-Vorbereitung für zuverlässigen PDF-Export unter Windows."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")

_WINDOWS_GTK_DIRS = (
    Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "GTK3-Runtime Win64" / "bin",
    Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "GTK3-Runtime Win64" / "bin",
    Path("C:/msys64/mingw64/bin"),
)


class PdfExportNotAvailableError(RuntimeError):
    """PDF-Export ist in dieser Umgebung nicht verfügbar."""


def _existing_gtk_dirs() -> list[Path]:
    dirs: list[Path] = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        dirs.append(exe_dir)

    for candidate in _WINDOWS_GTK_DIRS:
        if candidate.is_dir():
            dirs.append(candidate)

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in dirs:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def configure_pdf_runtime() -> list[Path]:
    """Ergänzt DLL-Suchpfade für WeasyPrint (v. a. Windows / PyInstaller)."""
    if sys.platform != "win32":
        return []

    gtk_dirs = _existing_gtk_dirs()
    if not gtk_dirs:
        return []

    path_parts = [str(path) for path in gtk_dirs]
    current_path = os.environ.get("PATH", "")
    for directory in reversed(path_parts):
        if directory not in current_path:
            current_path = directory + os.pathsep + current_path
    os.environ["PATH"] = current_path

    existing_dll_dirs = os.environ.get("WEASYPRINT_DLL_DIRECTORIES", "")
    merged_dll_dirs = os.pathsep.join(path_parts)
    if existing_dll_dirs:
        merged_dll_dirs = merged_dll_dirs + os.pathsep + existing_dll_dirs
    os.environ["WEASYPRINT_DLL_DIRECTORIES"] = merged_dll_dirs

    if hasattr(os, "add_dll_directory"):
        for directory in gtk_dirs:
            try:
                os.add_dll_directory(str(directory))
            except OSError:
                continue

    return gtk_dirs


def _import_weasyprint_html() -> Callable[..., T]:
    configure_pdf_runtime()
    try:
        from weasyprint import HTML as WeasyHTML
    except OSError as exc:
        raise PdfExportNotAvailableError(
            "WeasyPrint konnte die GTK-Bibliotheken nicht laden.\n\n"
            "Unter Windows: GTK3-Runtime installieren und die App neu starten.\n"
            "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows"
        ) from exc
    except ImportError as exc:
        raise PdfExportNotAvailableError(
            "WeasyPrint ist nicht installiert.\n\n"
            "Entwicklung: pip install -e .\n"
            "Desktop-App: Build mit scripts\\build_windows.ps1 neu erstellen."
        ) from exc
    return WeasyHTML


def check_pdf_export_available() -> tuple[bool, str]:
    """Prüft, ob PDF-Export funktioniert; liefert (ok, detail_message)."""
    try:
        _import_weasyprint_html()
        gtk_dirs = _existing_gtk_dirs()
        if sys.platform == "win32" and gtk_dirs:
            return True, f"PDF-Export bereit ({gtk_dirs[0]})"
        return True, "PDF-Export bereit"
    except PdfExportNotAvailableError as exc:
        return False, str(exc)


def get_weasyprint_html() -> Callable[..., T]:
    return _import_weasyprint_html()
