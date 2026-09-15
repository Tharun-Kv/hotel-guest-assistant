from fastapi import APIRouter

from app.schemas.hotel import HotelResponse
from app.services.hotel_service import HotelService


router = APIRouter()
service = HotelService()


@router.get("/hotel", response_model=HotelResponse)
def get_hotel() -> HotelResponse:
    return HotelResponse(**service.public_hotel_information())
