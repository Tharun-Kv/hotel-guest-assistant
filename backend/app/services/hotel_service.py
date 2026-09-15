from typing import Any

from app.repositories.hotel_repository import HotelRepository
from app.utils.validation import validate_guest_count


class HotelService:
    def __init__(self, repository: HotelRepository | None = None) -> None:
        self.repository = repository or HotelRepository()

    def get_hotel(self) -> dict[str, Any]:
        return self.repository.get_hotel()

    def get_faq(self, key: str) -> dict[str, str] | None:
        return self.repository.get_faq_by_category(key)

    def get_room_by_id(self, room_id: str) -> dict[str, Any] | None:
        return self.repository.get_room_by_id(room_id)

    def list_rooms(self) -> list[dict[str, Any]]:
        return self.repository.get_rooms()

    def find_suitable_rooms(self, adults: int) -> list[dict[str, Any]]:
        """Filter O(n), then rank O(n log n) by smallest fitting capacity."""
        validate_guest_count(adults)
        candidates = [room for room in self.list_rooms() if room["capacity"] >= adults]
        return sorted(candidates, key=lambda room: (room["capacity"], room["price_per_night"]))

    def get_amenity(self, name: str) -> str | None:
        key = name.strip().lower().replace(" ", "_")
        return self.repository.get_amenities().get(key)

    def get_policy(self, key: str) -> str | None:
        return self.repository.get_policies().get(key.lower())

    def public_hotel_information(self) -> dict[str, Any]:
        return {
            "hotel": self.get_hotel(),
            "amenities": self.repository.get_amenities(),
            "policies": self.repository.get_policies(),
            "rooms": self.list_rooms(),
        }
