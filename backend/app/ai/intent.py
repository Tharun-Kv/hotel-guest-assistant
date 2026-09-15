import re
from app.ai.client import AIClient
from app.ai.prompts import INTENTS
from app.core.exceptions import AIQuotaExceededError, AIUnavailableError


SUPPORTED_INTENTS = INTENTS

FAQ_TERMS = {"check-in", "check in", "checkin", "check-out", "check out", "checkout", "breakfast"}
AMENITY_TERMS = {"pool", "swimming", "gym", "fitness", "wifi", "wi-fi", "parking", "restaurant", "room service"}
POLICY_TERMS = {"cancellation", "cancel", "pets", "smoking", "smoke-free", "children", "extra bed", "extra beds"}
ROOM_TERMS = {"room", "suite", "accommodate", "capacity", "people", "guests", "guest"}
GREETING_PATTERN = re.compile(r"^(?:hi|hello|hey|hiya|good morning|good afternoon|good evening)(?: there)?[!,. ]*$", re.IGNORECASE)
IDENTITY_PATTERNS = (
    re.compile(r"\bwho\s+(?:are|r)\s+(?:you|u)\b"),
    re.compile(r"\bwhat\s+(?:are|r)\s+(?:you|u)\b"),
    re.compile(r"\bwhich\s+(?:assistant|assistance|asisitance)\s+are\s+(?:you|u)\b"),
    re.compile(r"\bwhat\s+(?:can|do)\s+(?:you|u)\b"),
    re.compile(r"\bare\s+you\s+(?:a|an)\s+(?:bot|assistant)\b"),
    re.compile(r"\bwhat\s+(?:kind|type)\s+of\s+(?:assistant|bot)\b"),
)


def _has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _is_identity_question(text: str) -> bool:
    return any(pattern.search(text) for pattern in IDENTITY_PATTERNS)


def deterministic_intent(message: str) -> str | None:
    text = message.lower().strip()
    if not text:
        return "unknown"
    if GREETING_PATTERN.fullmatch(text):
        return "greeting"
    if _is_identity_question(text):
        return "identity"

    has_date = bool(re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)) or bool(
        re.search(r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}", text)
    )
    if has_date or _has_any(text, {"availability", "available", "book", "booking", "stay", "staying"}):
        if has_date or _has_any(text, {"availability", "available", "book", "booking"}):
            return "availability"
    if _has_any(text, POLICY_TERMS):
        return "policy"
    if _has_any(text, FAQ_TERMS):
        return "faq"
    if _has_any(text, AMENITY_TERMS):
        return "amenity"
    if _has_any(text, ROOM_TERMS):
        return "room_information"
    return None


def detect_intent(message: str) -> str:
    return deterministic_intent(message) or "unknown"


class IntentDetector:
    def __init__(self, ai_client: AIClient | None = None) -> None:
        self.ai_client = ai_client or AIClient()

    def detect(self, message: str, context: list[dict[str, str]] | None = None) -> str:
        local_intent = deterministic_intent(message)
        if local_intent:
            return local_intent
        if not self.ai_client.is_available():
            return "unknown"
        try:
            model_intent = self.ai_client.classify_intent(message, context)
            return model_intent if model_intent in SUPPORTED_INTENTS else "unknown"
        except (AIUnavailableError, AIQuotaExceededError):
            return "unknown"
