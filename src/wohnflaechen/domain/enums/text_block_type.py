"""Typen für Objekttext-Blöcke."""

from enum import Enum


class TextBlockType(str, Enum):
    """Bearbeitbare Textbereiche eines Projekts."""

    OBJECT_DESCRIPTION = "object_description"
    PREFACE = "preface"
    PREFACE_ON_SITE = "preface_on_site"
    PREFACE_FROM_PLANS = "preface_from_plans"
    METHODOLOGY = "methodology"
    LIABILITY = "liability"
    SPECIAL_NOTES = "special_notes"
    MEASURE = "measure"

    @property
    def is_preface(self) -> bool:
        return self in {
            TextBlockType.PREFACE,
            TextBlockType.PREFACE_ON_SITE,
            TextBlockType.PREFACE_FROM_PLANS,
        }

    @property
    def label(self) -> str:
        labels = {
            TextBlockType.OBJECT_DESCRIPTION: "Objektbeschreibung",
            TextBlockType.PREFACE: "Vorbemerkungen",
            TextBlockType.PREFACE_ON_SITE: "Vorbemerkungen (Aufmaß)",
            TextBlockType.PREFACE_FROM_PLANS: "Vorbemerkungen (Pläne)",
            TextBlockType.METHODOLOGY: "Aufmaßmethodik",
            TextBlockType.LIABILITY: "Haftungshinweise",
            TextBlockType.SPECIAL_NOTES: "Besondere Hinweise",
            TextBlockType.MEASURE: "Maßnahme",
        }
        return labels[self]
