"""PDF-Export."""

from wohnflaechen.presentation.pdf.branding import COMPANY_NAME

__all__ = ["COMPANY_NAME", "PdfEngine"]


def __getattr__(name: str):
    if name == "PdfEngine":
        from wohnflaechen.presentation.pdf.engine import PdfEngine

        return PdfEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
