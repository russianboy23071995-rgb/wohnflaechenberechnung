"""Persistierte Dashboard- und Panel-Breiten."""

from wohnflaechen.infrastructure.database.auftrag_repositories import SQLiteAppSettingsRepository
from wohnflaechen.presentation.dashboard_layout import (
    AUFTRAG_PANEL_DEFAULT_WIDTH,
    AUFTRAG_PANEL_MAX_WIDTH,
    AUFTRAG_PANEL_MIN_WIDTH,
    DASHBOARD_MAIN_DEFAULT_WIDTH,
    DASHBOARD_MAIN_MAX_WIDTH,
    DASHBOARD_MAIN_MIN_WIDTH,
    KEY_AUFTRAG_PANEL_WIDTH,
    KEY_DASHBOARD_MAIN_WIDTH,
)


class LayoutSettingsService:
    def __init__(self, settings: SQLiteAppSettingsRepository) -> None:
        self._settings = settings

    def get_dashboard_width(self) -> int:
        return self._clamp(
            self._read_int(KEY_DASHBOARD_MAIN_WIDTH, DASHBOARD_MAIN_DEFAULT_WIDTH),
            DASHBOARD_MAIN_MIN_WIDTH,
            DASHBOARD_MAIN_MAX_WIDTH,
        )

    def set_dashboard_width(self, width: int) -> None:
        self._settings.set(
            KEY_DASHBOARD_MAIN_WIDTH,
            str(self._clamp(width, DASHBOARD_MAIN_MIN_WIDTH, DASHBOARD_MAIN_MAX_WIDTH)),
        )

    def get_auftrag_panel_width(self) -> int:
        return self._clamp(
            self._read_int(KEY_AUFTRAG_PANEL_WIDTH, AUFTRAG_PANEL_DEFAULT_WIDTH),
            AUFTRAG_PANEL_MIN_WIDTH,
            AUFTRAG_PANEL_MAX_WIDTH,
        )

    def set_auftrag_panel_width(self, width: int) -> None:
        self._settings.set(
            KEY_AUFTRAG_PANEL_WIDTH,
            str(self._clamp(width, AUFTRAG_PANEL_MIN_WIDTH, AUFTRAG_PANEL_MAX_WIDTH)),
        )

    def restore_defaults(self) -> None:
        self.set_dashboard_width(DASHBOARD_MAIN_DEFAULT_WIDTH)
        self.set_auftrag_panel_width(AUFTRAG_PANEL_DEFAULT_WIDTH)

    def _read_int(self, key: str, default: int) -> int:
        raw = self._settings.get(key, str(default))
        try:
            return int(raw)
        except ValueError:
            return default

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
