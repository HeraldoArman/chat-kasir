from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import RAGConfig
from app.services.embedding import EmbeddingService


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
        collections = self.client.get_collections().collections
        if not any(c.name == self.config.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def add_documents(self, texts: list[str], metadata: list[dict[str, object]]) -> None:
        vectors = self.embedding.embed_documents(texts)
        points = [
            PointStruct(id=i, vector=vec, payload={**meta, "text": text})
            for i, (text, vec, meta) in enumerate(zip(texts, vectors, metadata))
        ]
        self.client.upsert(collection_name=self.config.collection_name, points=points)

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
