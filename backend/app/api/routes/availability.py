from fastapi import APIRouter, Request

from app.core.logging import logger
from app.schemas.availability import AvailabilityRequest, AvailabilityResponse
from app.services.availability_service import AvailabilityService


router = APIRouter()
service = AvailabilityService()


@router.post("/availability", response_model=AvailabilityResponse)
def get_availability(payload: AvailabilityRequest, request: Request) -> AvailabilityResponse:
    request_id = request.state.request_id
    logger.info(
        "availability tool invoked",
        extra={"request_id": request_id, "endpoint": "/api/availability", "adults": payload.adults},
    )
    result = service.check_availability(payload.check_in, payload.check_out, payload.adults, payload.hotel_id)
    return AvailabilityResponse(**result)
