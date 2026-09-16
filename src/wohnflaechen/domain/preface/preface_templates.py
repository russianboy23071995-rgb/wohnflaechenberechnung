"""Standardtexte für die Vorbemerkungen (zwei Varianten)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PrefaceSection:
    number: int
    title: str
    default_body: str


def _format_sections(sections: tuple[PrefaceSection, ...]) -> str:
    return "\n\n".join(
        f"{section.title}\n{section.default_body.strip()}" for section in sections
    )


PREFACE_ON_SITE_SECTIONS: tuple[PrefaceSection, ...] = (
    PrefaceSection(
        1,
        "1. Grundlagen der Ermittlung",
        (
            "Die vorliegende Wohnflächenberechnung wurde gemäß der Verordnung zur "
            "Berechnung der Wohnfläche (Wohnflächenverordnung – WoFlV) in der jeweils "
            "gültigen Fassung erstellt."
        ),
    ),
    PrefaceSection(
        2,
        "2. Methodik des Aufmaßes",
        (
            "Die Datenerhebung erfolgte vor Ort durch eine fachkundige Person "
            "(Bachelor of Architecture) unter Anwendung eines hybriden Aufmaßverfahrens. "
            "Hierbei wurde die digitale LiDAR-gestützte Raumerfassung durch manuelle "
            "Referenzmessungen mittels Laser-Distanzmessgerät, mechanische Winkelprüfung "
            "sowie eine bautechnische Plausibilitätskontrolle ergänzt und validiert.\n\n"
            "Die erfassten Maße und räumlichen Gegebenheiten bilden die Grundlage der "
            "nachfolgenden Wohnflächenberechnung."
        ),
    ),
    PrefaceSection(
        3,
        "3. Stichtag der Aufnahme",
        (
            "Die Wohnflächenberechnung gibt die zum Zeitpunkt des Vor-Ort-Aufmaßes "
            "festgestellten baulichen Gegebenheiten wieder. Nachträgliche bauliche "
            "Veränderungen sind nicht Bestandteil dieser Berechnung.\n\n"
            "Aufmaß erfolgt am: "
        ),
    ),
    PrefaceSection(
        4,
        "4. Messgenauigkeit und Toleranzen",
        (
            "Abweichungen im Bereich üblicher Mess- und Bautoleranzen können aufgrund "
            "von Putzstärken, Bauteilunebenheiten sowie konstruktions- und "
            "materialbedingten Gegebenheiten nicht vollständig ausgeschlossen werden.\n\n"
            "Alle Flächenangaben wurden auf zwei Dezimalstellen gerundet "
            "(z. B. 10,445 m² → 10,45 m²)."
        ),
    ),
    PrefaceSection(
        5,
        "5. Zweck und Geltungsbereich",
        (
            "Diese Wohnflächenberechnung dient der Flächenermittlung nach WoFlV.\n\n"
            "Sie stellt keine baurechtliche Prüfung, Genehmigungsbewertung sowie keine "
            "statische oder technische Zustandsbeurteilung des Gebäudes dar."
        ),
    ),
    PrefaceSection(
        6,
        "6. Hinweis zur Berechnungsgrundlage",
        (
            "Die Wohnflächenberechnung und die zugehörigen Grundrissdarstellungen wurden "
            "auf Grundlage des durchgeführten Vor-Ort-Aufmaßes erstellt. Trotz sorgfältiger "
            "Aufnahme und Berechnung können geringfügige Abweichungen innerhalb üblicher "
            "Mess-, Bau- und Rundungstoleranzen nicht vollständig ausgeschlossen werden."
        ),
    ),
)


PREFACE_FROM_PLANS_SECTIONS: tuple[PrefaceSection, ...] = (
    PrefaceSection(
        1,
        "1. Grundlagen der Ermittlung",
        (
            "Die vorliegende Wohnflächenberechnung wurde gemäß der Verordnung zur "
            "Berechnung der Wohnfläche (Wohnflächenverordnung – WoFlV) in der jeweils "
            "gültigen Fassung erstellt."
        ),
    ),
    PrefaceSection(
        2,
        "2. Berechnungsgrundlage",
        (
            "Die Wohnflächenberechnung wurde auf Grundlage der zur Verfügung gestellten "
            "Plan- und Bauunterlagen erstellt. Die für die Berechnung erforderlichen Maße "
            "und Angaben wurden diesen Unterlagen entnommen.\n\n"
            "Seitens des Auftraggebers wurde bestätigt, dass die zur Verfügung gestellten "
            "Planunterlagen dem aktuellen bzw. tatsächlich ausgeführten Stand des "
            "Gebäudes entsprechen."
        ),
    ),
    PrefaceSection(
        3,
        "3. Grundlage der Flächenermittlung",
        (
            "Die in den Planunterlagen enthaltenen Maße und baulichen Angaben wurden der "
            "Wohnflächenberechnung zugrunde gelegt.\n\n"
            "Die Übereinstimmung der übergebenen Planunterlagen mit dem tatsächlichen "
            "Gebäudebestand wird entsprechend der Bestätigung des Auftraggebers "
            "vorausgesetzt."
        ),
    ),
    PrefaceSection(
        4,
        "4. Berechnungsgenauigkeit und Rundung",
        (
            "Die Flächen wurden rechnerisch auf Grundlage der in den Planunterlagen "
            "enthaltenen Maße ermittelt.\n\n"
            "Alle Flächenangaben wurden auf zwei Dezimalstellen gerundet "
            "(z. B. 10,445 m² → 10,45 m²)."
        ),
    ),
    PrefaceSection(
        5,
        "5. Zweck und Geltungsbereich",
        (
            "Diese Wohnflächenberechnung dient der Flächenermittlung nach WoFlV.\n\n"
            "Sie stellt keine baurechtliche Prüfung, Genehmigungsbewertung sowie keine "
            "statische oder technische Zustandsbeurteilung des Gebäudes dar."
        ),
    ),
    PrefaceSection(
        6,
        "6. Hinweis zur Berechnungsgrundlage",
        (
            "Die Richtigkeit und Aktualität der zur Verfügung gestellten Plan- und "
            "Bauunterlagen sowie deren Übereinstimmung mit dem tatsächlich ausgeführten "
            "Gebäudebestand wurden durch den Auftraggeber bestätigt und der Berechnung "
            "zugrunde gelegt."
        ),
    ),
)


DEFAULT_PREFACE_ON_SITE = _format_sections(PREFACE_ON_SITE_SECTIONS)
DEFAULT_PREFACE_FROM_PLANS = _format_sections(PREFACE_FROM_PLANS_SECTIONS)
