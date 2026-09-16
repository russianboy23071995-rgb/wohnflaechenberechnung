"""Verfügbare PDF-Exportlayouts."""

from enum import Enum


class PdfLayout(str, Enum):
    STANDARD = "standard"
    BAUANTRAG = "bauantrag"

    @property
    def label(self) -> str:
        labels = {
            PdfLayout.STANDARD: "Standard (NOVIKOV)",
            PdfLayout.BAUANTRAG: "Bauantrag (WoFlV klassisch)",
        }
        return labels[self]
