from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class HotelInfo:
    name: str
    address: str
    check_in: str
    check_out: str
    breakfast: str
    cancellation_policy: str
    contact: Dict[str, str]


@dataclass
class FAQEntry:
    question: str
    answer: str
    category: str


@dataclass
class Room:
    room_id: str
    name: str
    capacity: int
    bed_configuration: str
    description: str
    amenities: List[str]
    price_per_night: float
    availability: Dict[str, Any]
