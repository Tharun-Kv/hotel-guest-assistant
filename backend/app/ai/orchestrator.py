from datetime import date
from typing import Any

from app.ai.client import AIClient
from app.ai.extractor import AvailabilityEntities, extract_availability_entities, extract_guest_count
from app.ai.intent import IntentDetector
from app.core.exceptions import AIQuotaExceededError, AIUnavailableError
from app.services.availability_service import AvailabilityService
from app.services.hotel_service import HotelService
from app.services.response_service import ResponseService
from app.services.rag_service import RAGService
from app.tools.availability_tool import AvailabilityTool
from app.tools.hotel_search_tool import HotelSearchTool
from app.utils.text import normalize_message
from app.utils.validation import validate_date_range, validate_guest_count


class AIOrchestrator:
    def __init__(
        self,
        hotel_service: HotelService | None = None,
        availability_service: AvailabilityService | None = None,
        ai_client: AIClient | None = None,
        rag_service: RAGService | None = None,
    ) -> None:
        self.hotel_service = hotel_service or HotelService()
        self.availability_service = availability_service or AvailabilityService(hotel_service=self.hotel_service)
        self.ai_client = ai_client or AIClient()
        self.rag_service = rag_service or RAGService(ai_client=self.ai_client, hotel_repository=self.hotel_service.repository)
        self.intent_detector = IntentDetector(self.ai_client)
        self.hotel_tool = HotelSearchTool(self.hotel_service)
        self.availability_tool = AvailabilityTool(self.availability_service)

    def handle_message(self, message: str, conversation: list[dict[str, str]] | None = None) -> dict[str, Any]:
        message = normalize_message(message)
        if self._is_personal_contact_request(message):
            return ResponseService.answer(
                "Sorry, I don't have a personal phone number or contact details. "
                "Please call the hotel's help desk for direct assistance. "
                "I can also help with information about the hotel."
            )
        context = (conversation or [])[-6:]
        intent = self.intent_detector.detect(message, context)

        if intent == "greeting":
            return ResponseService.answer(
                "Hello! I'm your hotel assistant. I can help with rooms, amenities, policies, and availability."
            )
        if intent == "identity":
            return ResponseService.answer(
                "I'm your hotel's virtual assistant. I can answer hotel questions, recommend rooms, explain amenities and policies, and check live room availability."
            )
        if intent == "faq":
            answer = self._answer_faq(message)
            if answer["type"] != "fallback":
                return answer
        if intent == "amenity":
            answer = self._answer_amenity(message)
            if answer["type"] != "fallback":
                return answer
        if intent == "policy":
            answer = self._answer_policy(message)
            if answer["type"] != "fallback":
                return answer
        if intent == "room_information":
            return self._recommend_room(message)
        if intent == "availability":
            return self._check_availability(message)
        rag_answer = self.rag_service.answer(message)
        return rag_answer or ResponseService.fallback()

    @staticmethod
    def _is_personal_contact_request(message: str) -> bool:
        text = message.lower()
        personal_terms = (
            "your phone",
            "ur phone",
            "u r phone",
            "your number",
            "ur number",
            "u r number",
            "your email",
            "ur email",
            "your contact",
            "ur contact",
            "call you",
        )
        return any(term in text for term in personal_terms)

    def _answer_faq(self, message: str) -> dict[str, Any]:
        text = message.lower()
        mapping = {
            "check-in": ("check-in", "check in", "checkin"),
            "check-out": ("check-out", "check out", "checkout"),
            "breakfast": ("breakfast",),
        }
        for category, terms in mapping.items():
            if any(term in text for term in terms):
                faq = self.hotel_tool.faq(category)
                return ResponseService.answer(faq["answer"]) if faq else ResponseService.fallback()
        return ResponseService.fallback()

    def _answer_amenity(self, message: str) -> dict[str, Any]:
        text = message.lower()
        mapping = {
            "swimming pool": ("pool", "swimming"),
            "gym": ("gym", "fitness"),
            "wifi": ("wifi", "wi-fi", "internet"),
            "parking": ("parking",),
            "restaurant": ("restaurant", "dining", "dinner", "lunch"),
            "room service": ("room service",),
        }
        for amenity, terms in mapping.items():
            if any(term in text for term in terms):
                answer = self.hotel_tool.amenity(amenity)
                return ResponseService.answer(answer) if answer else ResponseService.fallback()
        return ResponseService.fallback()

    def _answer_policy(self, message: str) -> dict[str, Any]:
        text = message.lower()
        mapping = {
            "cancellation": ("cancel", "cancellation"),
            "pets": ("pet", "pets"),
            "smoking": ("smok",),
            "children": ("child", "children"),
            "extra_beds": ("extra bed", "extra beds"),
        }
        for policy, terms in mapping.items():
            if any(term in text for term in terms):
                answer = self.hotel_tool.policy(policy)
                return ResponseService.answer(answer) if answer else ResponseService.fallback()
        return ResponseService.fallback()

    def _recommend_room(self, message: str) -> dict[str, Any]:
        adults = extract_guest_count(message)
        if adults is None:
            return ResponseService.clarification("How many guests are staying?")
        try:
            validate_guest_count(adults)
        except ValueError as exc:
            return ResponseService.clarification(str(exc))
        rooms = self.hotel_service.find_suitable_rooms(adults)
        if not rooms:
            return ResponseService.answer("There is no room type in our published inventory that fits that guest count.")
        best = rooms[0]
        return ResponseService.answer(
            f"The {best['name']} is the closest fit for {adults} guests. It accommodates up to "
            f"{best['capacity']} guests and includes {best['bed_configuration']}."
        )

    def _check_availability(self, message: str) -> dict[str, Any]:
        entities = extract_availability_entities(message)
        entities = self._enrich_entities_from_ai(message, entities)
        if entities.check_in is None or entities.check_out is None:
            return ResponseService.clarification("Please provide both check-in and check-out dates in YYYY-MM-DD format.")
        if entities.adults is None:
            return ResponseService.clarification("How many guests should I check availability for?")
        try:
            validate_date_range(entities.check_in, entities.check_out)
            validate_guest_count(entities.adults)
            result = self.availability_tool.run(entities.check_in, entities.check_out, entities.adults)
        except ValueError as exc:
            return ResponseService.clarification(str(exc))
        if result["available"]:
            names = ", ".join(room["name"] for room in result["rooms"])
            message_text = f"I found {len(result['rooms'])} available option(s) for {result['adults']} guests: {names}."
        else:
            message_text = "No published room types are available for those dates and guest count."
        return {"success": True, "type": "availability", "message": message_text, "availability": result}

    def _enrich_entities_from_ai(self, message: str, entities: AvailabilityEntities) -> AvailabilityEntities:
        if (entities.check_in and entities.check_out and entities.adults) or not self.ai_client.is_available():
            return entities
        try:
            extracted = self.ai_client.extract_availability(message)
            check_in = entities.check_in or self._parse_iso_date(extracted.get("check_in"))
            check_out = entities.check_out or self._parse_iso_date(extracted.get("check_out"))
            adults = entities.adults or self._parse_adults(extracted.get("adults"))
            return AvailabilityEntities(check_in=check_in, check_out=check_out, adults=adults)
        except (AIUnavailableError, AIQuotaExceededError):
            return entities

    @staticmethod
    def _parse_iso_date(value: Any) -> date | None:
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_adults(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None
