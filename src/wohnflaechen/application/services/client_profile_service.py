"""Auftraggeber-Profile – wiederkehrende Kunden."""

from wohnflaechen.domain.entities.client_profile import ClientProfile
from wohnflaechen.infrastructure.database.client_profile_repository import SQLiteClientProfileRepository


class ClientProfileService:
    def __init__(self, repository: SQLiteClientProfileRepository) -> None:
        self._profiles = repository

    def list_profiles(self) -> list[ClientProfile]:
        return self._profiles.list_all()

    def remember_from_auftrag(
        self,
        name: str,
        address: str,
        email: str,
        phone: str,
    ) -> ClientProfile | None:
        return self._profiles.upsert_from_fields(name, address, email, phone)

    def touch_profile(self, profile_id: int) -> None:
        profile = self._profiles.get_by_id(profile_id)
        if profile:
            self._profiles.save(profile)
