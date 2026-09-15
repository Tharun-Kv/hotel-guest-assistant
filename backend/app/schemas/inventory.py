from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, root_validator


class InventoryRoom(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=50)
    status: Literal["available", "active", "maintenance", "closed"] = "available"
    name: str | None = Field(default=None, max_length=120)
    capacity: int | None = Field(default=None, ge=1, le=50)
    bed_configuration: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2_000)
    amenities: list[str] | None = None
    price_per_night: float | None = Field(default=None, gt=0)


class InventoryBooking(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=50)
    check_in: date
    check_out: date

    @root_validator
    def validate_dates(cls, values):
        check_in = values.get("check_in")
        check_out = values.get("check_out")
        if check_in and check_out and check_out <= check_in:
            raise ValueError("Booking check-out must be after check-in.")
        return values


class InventoryUpdateRequest(BaseModel):
    hotel_id: str = Field(default="default", min_length=1, max_length=80)
    rooms: list[InventoryRoom] = Field(..., min_items=1, max_items=500)
    bookings: list[InventoryBooking] = Field(default_factory=list, max_items=10_000)
    last_synced_at: str | None = Field(default=None, max_length=80)

    @root_validator
    def validate_unique_rooms(cls, values):
        rooms = values.get("rooms", [])
        ids = [room.room_id for room in rooms]
        if len(ids) != len(set(ids)):
            raise ValueError("Each live inventory room_id must be unique.")
        return values


class InventoryResponse(BaseModel):
    hotel_id: str
    last_synced_at: str | None
    rooms: list[dict]
    bookings: list[dict]
