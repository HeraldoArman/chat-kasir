import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import RAGConfig
from app.services.embedding import EmbeddingService

log = structlog.get_logger()


class RAGService:
    def __init__(self, config: RAGConfig, embedding_service: EmbeddingService):
        self.config = config
        self.embedding = embedding_service
        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.config.collection_name for c in collections):
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception:
            # Degrade gracefully if Qdrant is unavailable/offline.
            pass

    def add_documents(self, texts: list[str], metadata: list[dict[str, object]]) -> None:
        try:
            vectors = self.embedding.embed_documents(texts)
            points = [
                PointStruct(id=i, vector=vec, payload={**meta, "text": text})
                for i, (text, vec, meta) in enumerate(zip(texts, vectors, metadata))
            ]
            self.client.upsert(collection_name=self.config.collection_name, points=points)
        except Exception:
            log = structlog.get_logger()
            log.warning("rag_add_documents_failed", texts_count=len(texts))

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        query_vector = self.embedding.embed_query(query)
        results = self.client.query_points(
            collection_name=self.config.collection_name,
            query=query_vector,
            limit=top_k,
        ).points
        retrieved: list[dict[str, object]] = []
        for r in results:
            payload = r.payload
            if payload is None:
                continue
            text = payload.get("text", "")
            retrieved.append(
                {
                    "text": text,
                    "score": r.score,
                    "metadata": {k: v for k, v in payload.items() if k != "text"},
                }
            )
        return retrieved

    def retrieve_with_filter(
        self, query: str, filters: dict[str, object], top_k: int = 5
    ) -> list[dict[str, object]]:
        """Semantic search scoped by metadata filters (e.g. store_id, doc_type)."""
        query_vector = self.embedding.embed_query(query)
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        conditions = [
            FieldCondition(key=key, match=MatchValue(value=value))
            for key, value in filters.items()
        ]
        results = self.client.query_points(
            collection_name=self.config.collection_name,
            query=query_vector,
            query_filter=Filter(must=conditions),
            limit=top_k,
        ).points
        retrieved: list[dict[str, object]] = []
        for r in results:
            payload = r.payload
            if payload is None:
                continue
            text = payload.get("text", "")
            retrieved.append(
                {
                    "text": text,
                    "score": r.score,
                    "metadata": {k: v for k, v in payload.items() if k != "text"},
                }
            )
        return retrieved
