"""Angebotsverwaltung."""

from datetime import date, datetime
from typing import Optional

from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.infrastructure.database.auftrag_repositories import SQLiteOfferRepository


DEFAULT_SERVICE_TEXT = (
    "Wohn- und Nutzflächenberechnung nach WoFlV inkl. Aufmaß, "
    "Erstellung der Berechnungsunterlagen und PDF-Dokumentation."
)


class OfferService:
    def __init__(self, offer_repository: SQLiteOfferRepository) -> None:
        self._offers = offer_repository

    def get_offer(self, auftrag_id: int) -> Optional[Offer]:
        return self._offers.get_by_auftrag(auftrag_id)

    def list_offers(self, auftrag_id: int) -> list[Offer]:
        return self._offers.list_by_auftrag(auftrag_id)

    def suggest_number(self) -> str:
        year = date.today().year
        count = self._offers.count_all() + 1
        return f"ANG-{year}-{count:03d}"

    def create_default_offer(self, auftrag_id: int) -> Offer:
        return Offer(
            auftrag_id=auftrag_id,
            number=self.suggest_number(),
            date=date.today(),
            service_description=DEFAULT_SERVICE_TEXT,
        )

    def save_offer(self, offer: Offer) -> Offer:
        if offer.created_at is None and offer.id is None:
            offer.created_at = datetime.now()
        return self._offers.save(offer)
