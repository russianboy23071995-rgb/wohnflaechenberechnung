"""Ausgabe-Datenmodell – unabhängig vom PDF-Format."""

from dataclasses import dataclass, field


@dataclass
class PdfRoomRow:
    """Eine Zeile in der Geschoss-Tabelle."""

    index: str
    name: str
    calculation: str
    factor: str
    usable_area: str
    living_area: str


@dataclass
class PdfFloorSection:
    """Ein Geschoss-Abschnitt im Dokument."""

    section_index: int
    name: str
    rooms: list[PdfRoomRow] = field(default_factory=list)
    sum_living: str = ""
    sum_usable: str = ""


@dataclass
class PdfFloorTotal:
    """Geschoss-Aufschlüsselung in der Zusammenfassung."""

    name: str
    living_area: str
    usable_area: str


@dataclass
class PdfClassicTableRow:
    number: str
    name: str
    calculation: str
    area_result: str


@dataclass
class PdfClassicSection:
    heading: str
    area_column_title: str
    rows: list[PdfClassicTableRow] = field(default_factory=list)
    sum_label: str = ""
    sum_value: str = ""


@dataclass
class PdfClassicSummary:
    title: str
    lines: list[tuple[str, str]] = field(default_factory=list)
    total_label: str = ""
    total_value: str = ""


@dataclass
class PdfDocument:
    """Vollständiges Dokument für beliebige Ausgabeformate."""

    object_name: str = ""
    address: str = ""
    client: str = ""
    measure_title: str = ""
    object_description: str = ""
    preface: str = ""
    methodology: str = ""
    liability: str = ""
    special_notes: str = ""
    floors: list[PdfFloorSection] = field(default_factory=list)
    total_living: str = "00,00 m²"
    total_usable: str = "00,00 m²"
    floor_totals: list[PdfFloorTotal] = field(default_factory=list)
    footer_location: str = "Hamburg"
    footer_date: str = ""
    editor: str = ""
    classic_living_sections: list[PdfClassicSection] = field(default_factory=list)
    classic_usable_sections: list[PdfClassicSection] = field(default_factory=list)
    classic_living_summary: PdfClassicSummary | None = None
    classic_usable_summary: PdfClassicSummary | None = None
