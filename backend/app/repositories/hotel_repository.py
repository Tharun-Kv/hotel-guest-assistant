"""JSON-backed hotel repository.

The public methods mirror the data access operations a future PostgreSQL
repository would expose, keeping services independent from storage details.
"""

import json
from pathlib import Path
from typing import Any

from app.core.config import HOTEL_DATA_PATH


class HotelRepository:
    def __init__(self, file_path: str | Path = HOTEL_DATA_PATH) -> None:
        self.file_path = Path(file_path)
        self._data: dict[str, Any] | None = None
        self._rooms_by_id: dict[str, dict[str, Any]] = {}
        self._faqs_by_category: dict[str, dict[str, str]] = {}

    def load(self) -> dict[str, Any]:
        if self._data is None:
            with self.file_path.open("r", encoding="utf-8") as file:
                self._data = json.load(file)
            self._rooms_by_id = {room["room_id"].lower(): room for room in self._data["rooms"]}
            self._faqs_by_category = {faq["category"].lower(): faq for faq in self._data["faqs"]}
        return self._data

    def get_hotel(self) -> dict[str, Any]:
        return self.load()["hotel"]

    def get_amenities(self) -> dict[str, str]:
        return self.load()["amenities"]

    def get_rooms(self) -> list[dict[str, Any]]:
        return self.load()["rooms"]

    def get_policies(self) -> dict[str, str]:
        return self.load()["policies"]

    def get_faqs(self) -> list[dict[str, str]]:
        return self.load()["faqs"]

    def get_booking_records(self) -> list[dict[str, Any]]:
        return self.load().get("booking_records", [])

    def get_faq_by_category(self, category: str) -> dict[str, str] | None:
        self.load()
        return self._faqs_by_category.get(category.lower())

    def get_room_by_id(self, room_id: str) -> dict[str, Any] | None:
        self.load()
        return self._rooms_by_id.get(room_id.lower())
