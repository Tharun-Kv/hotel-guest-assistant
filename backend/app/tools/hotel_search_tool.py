from app.services.hotel_service import HotelService


class HotelSearchTool:
    """Controlled access to grounded hotel facts; no arbitrary application state."""

    def __init__(self, service: HotelService | None = None) -> None:
        self.service = service or HotelService()

    def faq(self, category: str) -> dict[str, str] | None:
        return self.service.get_faq(category)

    def amenity(self, name: str) -> str | None:
        return self.service.get_amenity(name)

    def policy(self, name: str) -> str | None:
        return self.service.get_policy(name)
