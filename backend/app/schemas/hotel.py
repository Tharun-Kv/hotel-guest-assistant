from typing import Any

from pydantic import BaseModel


class HotelResponse(BaseModel):
    hotel: dict[str, Any]
    amenities: dict[str, str]
    policies: dict[str, str]
    rooms: list[dict[str, Any]]
