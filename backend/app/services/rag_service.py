"""Retrieval-augmented hotel knowledge service."""

import json
from typing import Any

from app.ai.client import AIClient
from app.ai.prompts import build_grounded_answer_prompt
from app.core.exceptions import AIQuotaExceededError, AIUnavailableError
from app.rag.repository import KnowledgeRepository
from app.rag.scraper import scrape_url
from app.repositories.hotel_repository import HotelRepository


class RAGService:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository | None = None,
        hotel_repository: HotelRepository | None = None,
        ai_client: AIClient | None = None,
    ) -> None:
        self.repository = knowledge_repository or KnowledgeRepository()
        self.hotel_repository = hotel_repository or HotelRepository()
        self.ai_client = ai_client or AIClient()
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        if self.repository.list_documents("default"):
            return
        data = self.hotel_repository.load()
        sections = [
            f"Hotel information: {json.dumps(data.get('hotel', {}), ensure_ascii=False)}",
            f"Amenities: {json.dumps(data.get('amenities', {}), ensure_ascii=False)}",
            f"Policies: {json.dumps(data.get('policies', {}), ensure_ascii=False)}",
            f"Rooms: {json.dumps(data.get('rooms', []), ensure_ascii=False)}",
            f"FAQs: {json.dumps(data.get('faqs', []), ensure_ascii=False)}",
        ]
        self.repository.upsert_document(
            source_url="knowledge-base://hotel.json",
            title="Hotel knowledge base",
            text="\n".join(sections),
        )

    def ingest_url(self, url: str, title: str | None = None, hotel_id: str = "default") -> dict[str, Any]:
        scraped_title, text = scrape_url(url)
        return self.repository.upsert_document(url, title or scraped_title, text, hotel_id)

    def ingest_text(self, content: str, title: str, hotel_id: str = "default", source_url: str | None = None) -> dict[str, Any]:
        return self.repository.upsert_document(source_url or f"manual://{title}", title, content, hotel_id)

    def search(self, query: str, hotel_id: str = "default", top_k: int = 5) -> list[dict[str, Any]]:
        return self.repository.search(query, hotel_id=hotel_id, top_k=top_k)

    def answer(self, query: str, hotel_id: str = "default") -> dict[str, Any] | None:
        hits = self.search(query, hotel_id=hotel_id)
        if not hits:
            return None
        context = "\n\n".join(
            f"SOURCE: {hit['title']} ({hit['source_url']})\n{hit['text']}" for hit in hits
        )
        answer: str | None = None
        if self.ai_client.is_available():
            try:
                answer = self.ai_client.generate_grounded_answer(query, context)
            except (AIUnavailableError, AIQuotaExceededError):
                answer = None
        if not answer:
            answer = f"According to {hits[0]['title']}: {hits[0]['text']}"
        sources = [{"title": hit["title"], "url": hit["source_url"]} for hit in hits]
        return {"success": True, "type": "answer", "message": answer.strip(), "sources": sources}

    def documents(self, hotel_id: str | None = None) -> list[dict[str, Any]]:
        return self.repository.list_documents(hotel_id)

    def delete_document(self, document_id: str) -> bool:
        return self.repository.delete_document(document_id)
