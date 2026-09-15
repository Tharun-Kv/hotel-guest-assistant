from typing import Any

from pydantic import BaseModel, Field, root_validator


class KnowledgeIngestRequest(BaseModel):
    url: str | None = Field(default=None, max_length=2_000)
    content: str | None = Field(default=None, max_length=500_000)
    title: str | None = Field(default=None, max_length=200)
    hotel_id: str = Field(default="default", min_length=1, max_length=80)
    source_url: str | None = Field(default=None, max_length=2_000)

    @root_validator
    def require_source(cls, values):
        if not values.get("url") and not values.get("content"):
            raise ValueError("Provide either a public URL or document content.")
        if values.get("url") and values.get("content"):
            raise ValueError("Provide a URL or content, not both.")
        if values.get("content") and not values.get("title"):
            raise ValueError("A title is required for manually supplied content.")
        return values


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    hotel_id: str = Field(default="default", min_length=1, max_length=80)
    top_k: int = Field(default=5, ge=1, le=10)


class KnowledgeSource(BaseModel):
    title: str
    url: str


class KnowledgeDocument(BaseModel):
    document_id: str
    hotel_id: str
    title: str
    source_url: str
    ingested_at: str
    chunk_count: int


class KnowledgeSearchResult(BaseModel):
    chunk_id: str
    title: str
    source_url: str
    text: str
    score: float


class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeSearchResult]


class KnowledgeDocumentResponse(BaseModel):
    document: KnowledgeDocument
