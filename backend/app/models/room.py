from dataclasses import dataclass


@dataclass(frozen=True)
class RoomSummary:
    room_id: str
    name: str
    capacity: int
    bed_configuration: str
    price_per_night: float
