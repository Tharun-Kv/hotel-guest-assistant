from datetime import date
from typing import Any

from app.repositories.hotel_repository import HotelRepository
from app.repositories.inventory_repository import InventoryRepository
from app.services.hotel_service import HotelService
from app.utils.validation import validate_date_range, validate_guest_count


class AvailabilityService:
    def __init__(
        self,
        hotel_service: HotelService | None = None,
        repository: HotelRepository | None = None,
        inventory_repository: InventoryRepository | None = None,
    ) -> None:
        self.repository = repository or (hotel_service.repository if hotel_service else HotelRepository())
        self.hotel_service = hotel_service or HotelService(repository=self.repository)
        self.inventory_repository = inventory_repository or (None if repository else InventoryRepository())

    @staticmethod
    def has_overlap(requested_in: date, requested_out: date, existing_in: date, existing_out: date) -> bool:
        """Standard half-open interval overlap: [check-in, check-out)."""
        return existing_in < requested_out and existing_out > requested_in

    _has_overlap = has_overlap

    def _live_rooms(self, hotel_id: str) -> list[dict[str, Any]]:
        if self.inventory_repository is None:
            return self.hotel_service.list_rooms()
        return self.inventory_repository.get_rooms(hotel_id)

    def _live_bookings(self, hotel_id: str) -> list[dict[str, Any]]:
        if self.inventory_repository is None:
            return self.repository.get_booking_records()
        return self.inventory_repository.get_booking_records(hotel_id)

    def _is_room_available(self, room: dict[str, Any], check_in: date, check_out: date, hotel_id: str) -> bool:
        for booking in self._live_bookings(hotel_id):
            if booking.get("room_id") != room["room_id"]:
                continue
            existing_in = date.fromisoformat(booking["check_in"])
            existing_out = date.fromisoformat(booking["check_out"])
            if self.has_overlap(check_in, check_out, existing_in, existing_out):
                return False
        return True

    def _candidate_rooms(self, adults: int, hotel_id: str) -> list[dict[str, Any]]:
        base_by_id = {room["room_id"]: room for room in self.hotel_service.list_rooms()}
        live_rooms = self._live_rooms(hotel_id)
        if self.inventory_repository is None:
            return self.hotel_service.find_suitable_rooms(adults)
        candidates: list[dict[str, Any]] = []
        for live in live_rooms:
            base = base_by_id.get(live["room_id"], {})
            # A live feed may omit optional metadata or send null for fields
            # that are maintained in the hotel catalogue. Keep the catalogue
            # value in that case so one partial feed row cannot break search.
            room = {**base, **{key: value for key, value in live.items() if value is not None}}
            room.setdefault("name", room["room_id"])
            room.setdefault("bed_configuration", "Flexible room layout")
            room.setdefault("description", "Live inventory room")
            room.setdefault("amenities", [])
            room.setdefault("price_per_night", 0)
            if room.get("status", "available") not in {"available", "active"}:
                continue
            if (room.get("capacity") or 0) >= adults:
                candidates.append(room)
        return sorted(candidates, key=lambda item: (item["capacity"], item.get("price_per_night", 0)))

    def check_availability(self, check_in: date, check_out: date, adults: int, hotel_id: str = "default") -> dict[str, Any]:
        validate_date_range(check_in, check_out)
        validate_guest_count(adults)
        rooms = [
            {
                "room_id": room["room_id"],
                "name": room["name"],
                "capacity": room["capacity"],
                "bed_configuration": room["bed_configuration"],
                "description": room.get("description", ""),
                "amenities": room.get("amenities", []),
                "price_per_night": room["price_per_night"],
            }
            for room in self._candidate_rooms(adults, hotel_id)
            if self._is_room_available(room, check_in, check_out, hotel_id)
        ]
        return {
            "hotel_id": hotel_id,
            "available": bool(rooms),
            "rooms": rooms,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "adults": adults,
            "last_synced_at": self.inventory_repository.get_last_synced_at(hotel_id) if self.inventory_repository else None,
        }
