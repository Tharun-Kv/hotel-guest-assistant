from fastapi import APIRouter, Request

from app.core.logging import logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter()
service = ChatService()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    request_id = request.state.request_id
    logger.info(
        "chat request",
        extra={"request_id": request_id, "endpoint": "/api/chat", "message_length": len(payload.message)},
    )
    output = service.respond(
        message=payload.message,
        conversation_id=payload.conversation_id,
        conversation=[item.dict() for item in payload.conversation],
    )
    logger.info(
        "chat response",
        extra={"request_id": request_id, "endpoint": "/api/chat", "intent": output["type"]},
    )
    return ChatResponse(**output)
