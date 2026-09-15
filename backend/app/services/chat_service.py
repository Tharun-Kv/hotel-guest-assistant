from typing import Any

from app.ai.orchestrator import AIOrchestrator
from app.services.conversation_service import ConversationService, conversation_service


class ChatService:
    def __init__(
        self,
        orchestrator: AIOrchestrator | None = None,
        memory_service: ConversationService | None = None,
    ) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.conversation_service = memory_service or conversation_service

    def respond(
        self,
        message: str,
        conversation_id: str | None = None,
        conversation: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        conversation_id, context = self.conversation_service.get_or_create(conversation_id, conversation or [])
        output = self.orchestrator.handle_message(message, context)
        self.conversation_service.append(conversation_id, "user", message)
        self.conversation_service.append(conversation_id, "assistant", output["message"])
        return {**output, "conversation_id": conversation_id}
