"""DTOs für die Application-Schicht."""

from dataclasses import dataclass, field


@dataclass
class ImportResult:
    """Ergebnis eines Excel-Imports."""

    imported_count: int = 0
    skipped_count: int = 0
    new_floors: list[str] = field(default_factory=list)
    new_buildings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
