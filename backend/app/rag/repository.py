"""JSON-backed document and lexical retrieval repository.

The interface is intentionally storage-agnostic. The assignment uses a small
inverted-index-like scorer so it has no vector database dependency; a hosted
embedding index can replace this class later without changing the API.
"""

import hashlib
import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import DATA_DIR
from app.rag.chunker import chunk_text


STOP_WORDS = {
    "a", "an", "and", "are", "do", "does", "for", "from", "have", "how", "i", "is", "it",
    "me", "of", "on", "or", "the", "to", "what", "when", "where", "which", "with", "you",
}


def _tokens(value: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", value.lower()) if token not in STOP_WORDS and len(token) > 1]


class KnowledgeRepository:
    def __init__(self, file_path: str | Path = DATA_DIR / "knowledge.json") -> None:
        self.file_path = Path(file_path)
        self._lock = Lock()

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"documents": [], "chunks": []}
        with self.file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return {"documents": payload.get("documents", []), "chunks": payload.get("chunks", [])}

    def save(self, payload: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            temporary_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.file_path.parent, delete=False, suffix=".tmp"
                ) as temporary:
                    json.dump(payload, temporary, ensure_ascii=False, indent=2)
                    temporary_path = temporary.name
                os.replace(temporary_path, self.file_path)
            finally:
                if temporary_path and os.path.exists(temporary_path):
                    os.unlink(temporary_path)

    def upsert_document(
        self,
        source_url: str,
        title: str,
        text: str,
        hotel_id: str = "default",
    ) -> dict[str, Any]:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            raise ValueError("The document did not contain readable text.")
        document_id = hashlib.sha256(f"{hotel_id}:{source_url}".encode("utf-8")).hexdigest()[:16]
        now = datetime.now(timezone.utc).isoformat()
        chunks = chunk_text(cleaned)
        payload = self.load()
        payload["documents"] = [item for item in payload["documents"] if item["document_id"] != document_id]
        payload["chunks"] = [item for item in payload["chunks"] if item["document_id"] != document_id]
        payload["documents"].append(
            {
                "document_id": document_id,
                "hotel_id": hotel_id,
                "title": title or source_url,
                "source_url": source_url,
                "ingested_at": now,
                "chunk_count": len(chunks),
            }
        )
        payload["chunks"].extend(
            {
                "chunk_id": f"{document_id}-{index}",
                "document_id": document_id,
                "hotel_id": hotel_id,
                "title": title or source_url,
                "source_url": source_url,
                "text": chunk,
            }
            for index, chunk in enumerate(chunks)
        )
        self.save(payload)
        return payload["documents"][-1]

    def list_documents(self, hotel_id: str | None = None) -> list[dict[str, Any]]:
        documents = self.load()["documents"]
        if hotel_id is None:
            return documents
        return [item for item in documents if item["hotel_id"] == hotel_id]

    def delete_document(self, document_id: str) -> bool:
        payload = self.load()
        original_count = len(payload["documents"])
        payload["documents"] = [item for item in payload["documents"] if item["document_id"] != document_id]
        payload["chunks"] = [item for item in payload["chunks"] if item["document_id"] != document_id]
        if len(payload["documents"]) == original_count:
            return False
        self.save(payload)
        return True

    def search(self, query: str, hotel_id: str = "default", top_k: int = 5) -> list[dict[str, Any]]:
        query_terms = _tokens(query)
        if not query_terms:
            return []
        chunks = [item for item in self.load()["chunks"] if item["hotel_id"] == hotel_id]
        document_frequency: dict[str, int] = {}
        tokenized: list[tuple[dict[str, Any], list[str]]] = []
        for chunk in chunks:
            terms = _tokens(chunk["text"])
            tokenized.append((chunk, terms))
            for term in set(terms):
                document_frequency[term] = document_frequency.get(term, 0) + 1
        scored: list[dict[str, Any]] = []
        for chunk, terms in tokenized:
            if not terms:
                continue
            score = 0.0
            for term in query_terms:
                frequency = terms.count(term)
                if frequency:
                    inverse_frequency = math.log((len(chunks) + 1) / (document_frequency.get(term, 0) + 1)) + 1
                    score += (1 + math.log(frequency)) * inverse_frequency
            if score:
                scored.append({**chunk, "score": round(score, 4)})
        return sorted(scored, key=lambda item: item["score"], reverse=True)[: max(1, min(top_k, 10))]
