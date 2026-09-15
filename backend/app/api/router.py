from fastapi import APIRouter

from app.api.routes import admin, availability, chat, conversation, health, hotel, knowledge


router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(chat.router, prefix="/api", tags=["chat"])
router.include_router(availability.router, prefix="/api", tags=["availability"])
router.include_router(hotel.router, prefix="/api", tags=["hotel"])
router.include_router(conversation.router, prefix="/api", tags=["conversation"])
router.include_router(knowledge.router, prefix="/api", tags=["knowledge"])
router.include_router(admin.router, prefix="/api/admin", tags=["admin"])
