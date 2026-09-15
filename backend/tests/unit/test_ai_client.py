import json

import httpx
import pytest

from app.ai.client import AIClient
from app.core.config import settings
from app.core.exceptions import AIQuotaExceededError, AIUnavailableError


class FakeResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None) -> None:
        self.status_code = status_code
        self.payload = payload or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("request failed", request=None, response=None)

    def json(self) -> dict:
        return self.payload


def test_gemini_client_parses_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "test-model")
    monkeypatch.setattr(
        "app.ai.client.httpx.post",
        lambda *args, **kwargs: FakeResponse(
            payload={
                "candidates": [
                    {"content": {"parts": [{"text": json.dumps({"intent": "faq"})}]}}
                ]
            }
        ),
    )

    client = AIClient()

    assert client.is_available()
    assert client.classify_intent("What time is check-in?") == "faq"


def test_gemini_quota_errors_are_mapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.ai.client.httpx.post",
        lambda *args, **kwargs: FakeResponse(status_code=429),
    )

    with pytest.raises(AIQuotaExceededError):
        AIClient().extract_availability("October 10 to October 12 for two adults")


def test_client_is_unavailable_without_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

    client = AIClient()

    assert not client.is_available()
    with pytest.raises(AIUnavailableError):
        client.classify_intent("Hello")
