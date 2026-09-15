from app.rag.repository import KnowledgeRepository
from app.services.rag_service import RAGService


def test_rag_ingests_manual_content_and_retrieves_it(tmp_path):
    service = RAGService(knowledge_repository=KnowledgeRepository(tmp_path / "knowledge.json"))
    document = service.ingest_text(
        "Late checkout may be requested until 1 PM subject to availability.",
        "Late checkout policy",
    )

    results = service.search("late checkout")

    assert document["chunk_count"] == 1
    assert results[0]["title"] == "Late checkout policy"
    assert "1 PM" in results[0]["text"]


def test_rag_returns_grounded_fallback_without_a_model(tmp_path):
    service = RAGService(knowledge_repository=KnowledgeRepository(tmp_path / "knowledge.json"))
    service.ingest_text("The spa is open from 8 AM to 8 PM.", "Spa hours")

    answer = service.answer("When is the spa open?")

    assert answer is not None
    assert "8 AM" in answer["message"]
    assert answer["sources"][0]["title"] == "Spa hours"
