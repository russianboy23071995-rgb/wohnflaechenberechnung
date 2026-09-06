"""Typen für Objekttext-Blöcke."""

from enum import Enum


class TextBlockType(str, Enum):
    """Bearbeitbare Textbereiche eines Projekts."""

    OBJECT_DESCRIPTION = "object_description"
    PREFACE = "preface"
    METHODOLOGY = "methodology"
    LIABILITY = "liability"
    SPECIAL_NOTES = "special_notes"
    MEASURE = "measure"

    @property
    def label(self) -> str:
        labels = {
            TextBlockType.OBJECT_DESCRIPTION: "Objektbeschreibung",
            TextBlockType.PREFACE: "Vorbemerkungen",
            TextBlockType.METHODOLOGY: "Aufmaßmethodik",
            TextBlockType.LIABILITY: "Haftungshinweise",
            TextBlockType.SPECIAL_NOTES: "Besondere Hinweise",
            TextBlockType.MEASURE: "Maßnahme",
        }
        return labels[self]
