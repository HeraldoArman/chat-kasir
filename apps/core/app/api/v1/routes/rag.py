
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_config
from app.services.embedding import EmbeddingService
from app.services.rag import RAGService


class IngestRequest(BaseModel):
    texts: list[str]
    metadata: list[dict[str, object]]


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievedChunk(BaseModel):
    text: str
    score: float
    metadata: dict[str, object]


class QueryResponse(BaseModel):
    chunks: list[RetrievedChunk]


router = APIRouter(prefix="/rag", tags=["RAG"])

_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        config = get_config()
        if not config.rag.enabled:
            raise HTTPException(status_code=503, detail="RAG is not enabled")
        embedding_service = EmbeddingService(model_name=config.rag.embedding_model)
        _rag_service = RAGService(config.rag, embedding_service)
    return _rag_service


@router.post("/ingest")
async def ingest_documents(request: IngestRequest) -> dict[str, str | int]:
    service = get_rag_service()
    service.add_documents(request.texts, request.metadata)
    return {"status": "ok", "documents_ingested": len(request.texts)}


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    service = get_rag_service()
    results = service.retrieve(request.query, request.top_k)
    return QueryResponse(
        chunks=[RetrievedChunk(text=r["text"], score=r["score"], metadata=r["metadata"]) for r in results]
    )
