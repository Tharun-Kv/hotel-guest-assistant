from app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository | None = None) -> None:
        self.repository = repository or ConversationRepository()

    def create_or_replace(self, conversation_id: str | None, messages: list[dict[str, str]]) -> tuple[str, list[dict[str, str]]]:
        if conversation_id and self.repository.get(conversation_id) is not None:
            return conversation_id, self.repository.replace(conversation_id, messages)
        new_id = self.repository.create(messages)
        return new_id, self.repository.get(new_id) or []

    def get_or_create(self, conversation_id: str | None, initial: list[dict[str, str]]) -> tuple[str, list[dict[str, str]]]:
        if conversation_id:
            existing = self.repository.get(conversation_id)
            if existing is not None:
                return conversation_id, existing
        new_id = self.repository.create(initial)
        return new_id, self.repository.get(new_id) or []

    def append(self, conversation_id: str, role: str, content: str) -> list[dict[str, str]]:
        return self.repository.append(conversation_id, role, content)


conversation_service = ConversationService(ConversationRepository())
