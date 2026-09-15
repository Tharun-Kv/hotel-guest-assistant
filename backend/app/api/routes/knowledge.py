from fastapi import APIRouter, HTTPException

from app.schemas.knowledge import KnowledgeSearchRequest, KnowledgeSearchResponse
from app.services.rag_service import RAGService


router = APIRouter()
service = RAGService()


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(payload: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(results=service.search(payload.query, payload.hotel_id, payload.top_k))
