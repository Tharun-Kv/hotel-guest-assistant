from datetime import date

from pydantic import BaseModel, Field, root_validator

from app.core.config import settings


class AvailabilityRequest(BaseModel):
    hotel_id: str = Field(default="default", min_length=1, max_length=80)
    check_in: date
    check_out: date
    adults: int = Field(..., ge=1, le=settings.MAX_GUESTS)

    @root_validator
    def validate_stay(cls, values):
        check_in = values.get("check_in")
        check_out = values.get("check_out")
        if check_in and check_out:
            if check_in < date.today():
                raise ValueError("Check-in date cannot be in the past.")
            if check_out <= check_in:
                raise ValueError("Check-out date must be after check-in date.")
        return values


class AvailabilityRoom(BaseModel):
    room_id: str
    name: str
    capacity: int
    bed_configuration: str
    description: str
    amenities: list[str]
    price_per_night: float


class AvailabilityResponse(BaseModel):
    hotel_id: str = "default"
    available: bool
    rooms: list[AvailabilityRoom]
    check_in: str
    check_out: str
    adults: int
    last_synced_at: str | None = None
