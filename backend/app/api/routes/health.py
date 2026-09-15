from fastapi import APIRouter

from app.core.config import settings


router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok", "version": settings.APP_VERSION}
