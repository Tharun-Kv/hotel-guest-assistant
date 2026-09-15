from app.ai.orchestrator import AIOrchestrator
from app.core.exceptions import AIUnavailableError


class UnavailableAIClient:
    def is_available(self):
        return True

    def classify_intent(self, message, context=None):
        raise AIUnavailableError()

    def extract_availability(self, message):
        raise AIUnavailableError()


def test_ai_unavailable_uses_safe_fallback_without_crashing():
    result = AIOrchestrator(ai_client=UnavailableAIClient()).handle_message("Can you arrange a helicopter?")
    assert result["type"] == "fallback"
    assert "can't answer" in result["message"].lower()
