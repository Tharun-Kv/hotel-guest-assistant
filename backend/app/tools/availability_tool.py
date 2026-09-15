from datetime import date
from typing import Any

from app.services.availability_service import AvailabilityService


class AvailabilityTool:
    """Explicit boundary around deterministic availability business logic."""

    def __init__(self, service: AvailabilityService | None = None) -> None:
        self.service = service or AvailabilityService()

    def run(self, check_in: date, check_out: date, adults: int, hotel_id: str = "default") -> dict[str, Any]:
        return self.service.check_availability(check_in, check_out, adults, hotel_id)
