from typing import Any


class ResponseService:
    SAFE_FALLBACK = "I'm sorry, I can't answer that from the hotel information I have. Please contact the front desk for help."

    @staticmethod
    def answer(message: str) -> dict[str, Any]:
        return {"success": True, "type": "answer", "message": message}

    @staticmethod
    def clarification(message: str) -> dict[str, Any]:
        return {"success": True, "type": "clarification", "message": message}

    @classmethod
    def fallback(cls) -> dict[str, Any]:
        return {"success": True, "type": "fallback", "message": cls.SAFE_FALLBACK}
