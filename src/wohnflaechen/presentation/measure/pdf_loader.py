"""PDF-Seiten als Pixmaps für den Maß-Canvas."""

from pathlib import Path

from PySide6.QtGui import QImage, QPixmap


def pdf_page_count(file_path: Path) -> int:
    import fitz

    with fitz.open(file_path) as doc:
        return doc.page_count


def pdf_page_to_pixmap(file_path: Path, page_index: int = 0, dpi: float = 144.0) -> QPixmap:
    """Rendert eine PDF-Seite als QPixmap."""
    import fitz

    with fitz.open(file_path) as doc:
        if page_index < 0 or page_index >= doc.page_count:
            raise IndexError(f"Seite {page_index} existiert nicht in {file_path.name}")
        page = doc[page_index]
        scale = dpi / 72.0
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(image.copy())
