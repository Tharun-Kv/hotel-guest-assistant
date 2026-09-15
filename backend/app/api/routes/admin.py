from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.security import require_admin
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryResponse, InventoryUpdateRequest
from app.schemas.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentResponse,
    KnowledgeIngestRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from app.services.rag_service import RAGService


router = APIRouter()
rag_service = RAGService()
inventory_repository = InventoryRepository()


def admin_guard(request: Request) -> None:
    require_admin(request)


@router.get("/knowledge/documents", response_model=list[KnowledgeDocument], dependencies=[Depends(admin_guard)])
def list_knowledge_documents(hotel_id: str | None = None) -> list[dict]:
    return rag_service.documents(hotel_id)


@router.post("/knowledge/ingest", response_model=KnowledgeDocumentResponse, dependencies=[Depends(admin_guard)])
def ingest_knowledge(payload: KnowledgeIngestRequest) -> KnowledgeDocumentResponse:
    try:
        if payload.url:
            document = rag_service.ingest_url(payload.url, payload.title, payload.hotel_id)
        else:
            document = rag_service.ingest_text(payload.content or "", payload.title or "Manual document", payload.hotel_id, payload.source_url)
        return KnowledgeDocumentResponse(document=document)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/knowledge/documents/{document_id}", dependencies=[Depends(admin_guard)])
def delete_knowledge_document(document_id: str) -> dict[str, bool]:
    if not rag_service.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Knowledge document was not found.")
    return {"deleted": True}


@router.get("/inventory", response_model=InventoryResponse, dependencies=[Depends(admin_guard)])
def get_inventory(hotel_id: str = "default") -> InventoryResponse:
    return InventoryResponse(**inventory_repository.load(hotel_id))


@router.put("/inventory", response_model=InventoryResponse, dependencies=[Depends(admin_guard)])
def update_inventory(payload: InventoryUpdateRequest) -> InventoryResponse:
    snapshot = inventory_repository.replace(
        {
            "hotel_id": payload.hotel_id,
            "last_synced_at": payload.last_synced_at,
            "rooms": [room.dict(exclude_none=True) for room in payload.rooms],
            "bookings": [
                {
                    "room_id": booking.room_id,
                    "check_in": booking.check_in.isoformat(),
                    "check_out": booking.check_out.isoformat(),
                }
                for booking in payload.bookings
            ],
        }
    )
    return InventoryResponse(**snapshot)
