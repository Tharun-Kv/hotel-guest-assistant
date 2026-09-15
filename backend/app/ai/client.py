import json
from typing import Any

import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

from app.ai.prompts import build_availability_extraction_prompt, build_grounded_answer_prompt, build_intent_prompt
from app.core.config import settings
from app.core.exceptions import AIQuotaExceededError, AIUnavailableError


class AIClient:
    def __init__(self) -> None:
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.openai_model = settings.OPENAI_MODEL

    def is_available(self) -> bool:
        return bool(self.gemini_api_key or self.openai_client)

    def classify_intent(self, message: str, context: list[dict[str, str]] | None = None) -> str:
        result = self._json_completion(build_intent_prompt(message, context))
        return str(result.get("intent", "unknown")).lower()

    def extract_availability(self, message: str) -> dict[str, Any]:
        return self._json_completion(build_availability_extraction_prompt(message))

    def generate_grounded_answer(self, question: str, context: str) -> str:
        prompt = build_grounded_answer_prompt(question, context)
        if self.gemini_api_key:
            return self._gemini_text_completion(prompt)
        if not self.openai_client:
            raise AIUnavailableError("The AI service is not configured.")
        try:
            completion = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "Answer only from the supplied source context."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=280,
            )
            return (completion.choices[0].message.content or "").strip()
        except RateLimitError as exc:
            raise AIQuotaExceededError() from exc
        except (APIConnectionError, APITimeoutError, APIStatusError) as exc:
            raise AIUnavailableError() from exc

    def _json_completion(self, prompt: str) -> dict[str, Any]:
        if self.gemini_api_key:
            return self._gemini_json_completion(prompt)
        if not self.openai_client:
            raise AIUnavailableError("The AI service is not configured.")
        try:
            completion = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "Follow the requested JSON schema exactly."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=120,
            )
            content = completion.choices[0].message.content or "{}"
            payload = json.loads(content)
            return payload if isinstance(payload, dict) else {}
        except RateLimitError as exc:
            raise AIQuotaExceededError() from exc
        except (APIConnectionError, APITimeoutError, APIStatusError, json.JSONDecodeError) as exc:
            raise AIUnavailableError() from exc

    def _gemini_json_completion(self, prompt: str) -> dict[str, Any]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 120,
                "responseMimeType": "application/json",
            },
        }
        try:
            response = httpx.post(
                url,
                params={"key": self.gemini_api_key},
                json=payload,
                timeout=15,
            )
            if response.status_code == 429:
                raise AIQuotaExceededError()
            response.raise_for_status()
            candidates = response.json().get("candidates", [])
            content = candidates[0]["content"]["parts"][0].get("text", "{}")
            result = json.loads(content)
            return result if isinstance(result, dict) else {}
        except AIQuotaExceededError:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AIUnavailableError() from exc

    def _gemini_text_completion(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 280},
        }
        try:
            response = httpx.post(url, params={"key": self.gemini_api_key}, json=payload, timeout=15)
            if response.status_code == 429:
                raise AIQuotaExceededError()
            response.raise_for_status()
            candidates = response.json().get("candidates", [])
            return candidates[0]["content"]["parts"][0].get("text", "").strip()
        except AIQuotaExceededError:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AIUnavailableError() from exc
