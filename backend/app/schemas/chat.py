from typing import Literal

from pydantic import BaseModel, Field, validator

from app.core.config import settings
from app.schemas.availability import AvailabilityResponse


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=settings.MAX_MESSAGE_LENGTH)

    @validator("content")
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be empty.")
        return value


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=settings.MAX_MESSAGE_LENGTH)
    conversation_id: str | None = Field(default=None, max_length=100)
    conversation: list[ConversationMessage] = Field(default_factory=list)

    @validator("message")
    def strip_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty.")
        return value


class ChatResponse(BaseModel):
    success: bool = True
    type: Literal["answer", "availability", "clarification", "fallback"] = "answer"
    message: str
    conversation_id: str
    availability: AvailabilityResponse | None = None
    sources: list[dict[str, str]] = Field(default_factory=list)


class ConversationRequest(BaseModel):
    conversation_id: str | None = Field(default=None, max_length=100)
    messages: list[ConversationMessage] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    success: bool = True
    conversation_id: str
    messages: list[ConversationMessage]
