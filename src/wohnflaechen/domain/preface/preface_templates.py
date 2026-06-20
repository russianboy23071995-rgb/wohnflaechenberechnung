"""Standardtexte für die Vorbemerkungen (WoFlV-Vorlage)."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PrefaceSection:
    number: int
    title: str
    default_body: str


SECTION_1_BODY = (
    "Die vorliegende Wohnflächenberechnung wurde gemäß der Verordnung zur "
    "Berechnung der Wohnfläche (Wohnflächenverordnung – WoFlV) in der jeweils "
    "gültigen Fassung erstellt."
)

SECTION_2_BODY = (
    "Die Datenerhebung erfolgte vor Ort durch eine fachkundige Person "
    "(Bachelor of Architecture) unter Anwendung eines hybriden Aufmaß-Verfahrens. "
    "Hierbei wurde die digitale LiDAR-gestützte Raum-Erfassung durch manuelle "
    "Referenzmessungen (Laser-Distanzmessung), mechanische Winkelprüfung sowie "
    "eine bautechnische Plausibilitätskontrolle validiert.\n\n"
    "Diese methodische Kombination garantiert eine präzise Abbildung der baulichen "
    "Gegebenheiten und erfüllt die Anforderungen für Bankfinanzierungen und "
    "notarielle Unterlagen."
)

SECTION_3_BODY_NO_MEASUREMENT = (
    "Es wurde kein Aufmaß erstellt. Die folgende Berechnung wurde anhand von "
    "vorliegender Bestandsunterlagen erstellt."
)

SECTION_4_BODY = (
    "Abweichungen im Bereich üblicher Messtoleranzen sind aufgrund von Putzstärken, "
    "Bauteilunebenheiten sowie konstruktiven und materialbedingten Verformungen "
    "möglich.\n\n"
    "Alle Flächenangaben wurden auf zwei Dezimalstellen gerundet. "
    "(z.B.10,445 → 10,45)"
)

SECTION_5_BODY = (
    "Diese Wohnflächenberechnung dient ausschließlich der Flächenermittlung nach WoFlV.\n\n"
    "Sie stellt keine baurechtliche Prüfung, keine Genehmigungsbewertung und keine "
    "statische oder technische Zustandsbeurteilung des Gebäudes dar."
)

SECTION_6_BODY = (
    "Die vorliegende Wohnflächenberechnung sowie die zugehörigen Grundrissdarstellungen "
    "wurden auf Grundlage eines Vor-Ort Aufmaßes erstellt. Eine Gewähr für die "
    "Richtigkeit, Vollständigkeit sowie Maßhaltigkeit der Angaben wird ausdrücklich "
    "nicht übernommen. Abweichungen zum tatsächlichen Bestand können nicht "
    "ausgeschlossen werden."
)

DEFAULT_PREFACE_SECTIONS: tuple[PrefaceSection, ...] = (
    PrefaceSection(1, "1. Grundlagen der Ermittlung", SECTION_1_BODY),
    PrefaceSection(2, "2. Methodik des Aufmaßes", SECTION_2_BODY),
    PrefaceSection(3, "3. Stichtag der Aufnahme", ""),
    PrefaceSection(4, "4. Messgenauigkeit und Toleranzen", SECTION_4_BODY),
    PrefaceSection(5, "5. Zweck und Geltungsbereich der Berechnung", SECTION_5_BODY),
    PrefaceSection(6, "6. Haftungshinweis", SECTION_6_BODY),
)


def section_3_with_measurement(measurement_date: date) -> str:
    formatted = measurement_date.strftime("%d.%m.%Y")
    return (
        f"Das Aufmaß erfolgte am {formatted}. Jegliche danach getätigte bauliche "
        "Veränderungen, sind nicht berücksichtigt."
    )


def section_3_body(measurement_on_site: bool, measurement_date: date | None) -> str:
    if measurement_on_site and measurement_date:
        return section_3_with_measurement(measurement_date)
    return SECTION_3_BODY_NO_MEASUREMENT
