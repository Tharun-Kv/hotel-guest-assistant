from fastapi import APIRouter

from app.schemas.chat import ConversationRequest, ConversationResponse
from app.services.conversation_service import conversation_service


router = APIRouter()
@router.post("/conversation", response_model=ConversationResponse)
def upsert_conversation(payload: ConversationRequest) -> ConversationResponse:
    conversation_id, messages = conversation_service.create_or_replace(
        payload.conversation_id,
        [item.dict() for item in payload.messages],
    )
    return ConversationResponse(conversation_id=conversation_id, messages=messages)
