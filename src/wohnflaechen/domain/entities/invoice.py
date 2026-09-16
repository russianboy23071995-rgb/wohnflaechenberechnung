"""Rechnung zu einem Auftrag."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Invoice:
    id: Optional[int] = None
    auftrag_id: int = 0
    number: str = ""
    date: Optional[date] = None
    service_description: str = ""
    price: float = 0.0
    notes: str = ""
    file_path: str = ""
    created_at: Optional[datetime] = None
