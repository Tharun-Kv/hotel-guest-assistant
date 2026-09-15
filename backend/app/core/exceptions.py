class HotelAssistantError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(HotelAssistantError):
    def __init__(self, message: str):
        super().__init__(message, 400)


class NotFoundError(HotelAssistantError):
    def __init__(self, message: str):
        super().__init__(message, 404)


class AIUnavailableError(HotelAssistantError):
    def __init__(self, message: str = "The AI service is currently unavailable."):
        super().__init__(message, 503)


class AIQuotaExceededError(HotelAssistantError):
    def __init__(self, message: str = "AI request limit reached. Please try again shortly."):
        super().__init__(message, 429)
