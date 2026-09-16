"""Erkennung von Gebäude-Präfixen in Archicad-Raumnummern."""

import re

ROOM_PREFIX_PATTERNS: dict[str, re.Pattern[str]] = {
    "R": re.compile(r"^R-\d+", re.IGNORECASE),
    "E": re.compile(r"^E-\d+", re.IGNORECASE),
}

DEFAULT_BUILDING_NAMES: dict[str, str] = {
    "R": "Haus 1",
    "E": "Haus 2",
}


def detect_room_prefix(number: str) -> str:
    """Liefert R, E oder leer."""
    text = (number or "").strip()
    if not text:
        return ""
    for prefix, pattern in ROOM_PREFIX_PATTERNS.items():
        if pattern.match(text):
            return prefix
    return ""


def is_archicad_room_label(label: str) -> bool:
    """Raumkennung: R-XXX, E-XXX oder numerische Nr."""
    if not label:
        return False
    if detect_room_prefix(label):
        return True
    return bool(re.fullmatch(r"\d{1,4}", label.strip()))
