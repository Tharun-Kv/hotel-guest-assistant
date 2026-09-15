"""Bounded in-memory conversation storage for the assignment.

Its interface can be backed by Redis or a database without changing routes.
"""

from threading import Lock
from uuid import uuid4

from app.core.config import settings


class ConversationRepository:
    def __init__(self, max_messages: int = settings.MAX_CONVERSATION_HISTORY) -> None:
        self.max_messages = max_messages
        self._conversations: dict[str, list[dict[str, str]]] = {}
        self._lock = Lock()

    def create(self, messages: list[dict[str, str]] | None = None) -> str:
        conversation_id = str(uuid4())
        self.replace(conversation_id, messages or [])
        return conversation_id

    def get(self, conversation_id: str) -> list[dict[str, str]] | None:
        with self._lock:
            messages = self._conversations.get(conversation_id)
            return list(messages) if messages is not None else None

    def replace(self, conversation_id: str, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        bounded = [{"role": item["role"], "content": item["content"]} for item in messages[-self.max_messages :]]
        with self._lock:
            self._conversations[conversation_id] = bounded
        return list(bounded)

    def append(self, conversation_id: str, role: str, content: str) -> list[dict[str, str]]:
        with self._lock:
            messages = self._conversations.setdefault(conversation_id, [])
            messages.append({"role": role, "content": content})
            del messages[:-self.max_messages]
            return list(messages)
