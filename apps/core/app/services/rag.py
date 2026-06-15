"""RAG service backed by Qdrant vector search.

Uses AsyncQdrantClient so that calls do not block the event loop.
If Qdrant is unreachable, every public method degrades gracefully —
logs a warning and returns an empty result.
"""

from __future__ import annotations

import hashlib
from typing import Any

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from app.core.config import RAGConfig
from app.services.embedding import EmbeddingService

log = structlog.get_logger()


class RAGService:
    """Async wrapper around Qdrant for semantic search."""

    def __init__(self, config: RAGConfig, embedding_service: EmbeddingService) -> None:
        self.config = config
        self.embedding = embedding_service
        self._client: AsyncQdrantClient | None = None

    # ------------------------------------------------------------------
    # Lazy client initialisation
    # ------------------------------------------------------------------

    async def _get_client(self) -> AsyncQdrantClient:
        if self._client is not None:
            return self._client
        self._client = AsyncQdrantClient(
            url=self.config.qdrant_url,
            api_key=self.config.qdrant_api_key or None,
        )
        await self._ensure_collection()
        return self._client

    async def _ensure_collection(self) -> None:
        try:
            client = await self._get_client()
            collections = await client.get_collections()
            names = [c.name for c in collections.collections]
            if self.config.collection_name not in names:
                await client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception:
            log.warning("rag_ensure_collection_failed")

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    async def add_documents(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]],
        point_ids: list[int] | None = None,
    ) -> None:
        """Embed and upsert documents into Qdrant.

        If *point_ids* is provided, each document gets the corresponding
        deterministic ID (useful for idempotent upserts / deletes).
        """
        try:
            client = await self._get_client()
            vectors = self.embedding.embed_documents(texts)
            points: list[PointStruct] = []
            for idx, (text, vec, meta) in enumerate(
                zip(texts, vectors, metadata)
            ):
                pid = point_ids[idx] if point_ids else idx
                points.append(
                    PointStruct(id=pid, vector=vec, payload={**meta, "text": text})
                )
            await client.upsert(
                collection_name=self.config.collection_name, points=points
            )
        except Exception:
            log.warning("rag_add_documents_failed", texts_count=len(texts))

    # ------------------------------------------------------------------
    # Delete operations
    # ------------------------------------------------------------------

    async def delete_by_filter(self, filters: dict[str, object]) -> None:
        """Remove all points matching *filters* from the collection."""
        try:
            client = await self._get_client()
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filters.items()
            ]
            await client.delete(
                collection_name=self.config.collection_name,
                points_selector=Filter(must=conditions),
            )
        except Exception:
            log.warning("rag_delete_by_filter_failed", filters=filters)

    async def delete_by_point_ids(self, point_ids: list[int]) -> None:
        """Remove specific points by their numeric IDs."""
        if not point_ids:
            return
        try:
            client = await self._get_client()
            await client.delete(
                collection_name=self.config.collection_name,
                points_selector=PointIdsList(points=point_ids),
            )
        except Exception:
            log.warning("rag_delete_by_ids_failed", count=len(point_ids))

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        """Unfiltered semantic search."""
        try:
            client = await self._get_client()
            query_vector = self.embedding.embed_query(query)
            results = await client.query_points(
                collection_name=self.config.collection_name,
                query=query_vector,
                limit=top_k,
            )
            return self._format_results(results.points)
        except Exception:
            log.warning("rag_retrieve_failed", query=query[:50])
            return []

    async def retrieve_with_filter(
        self, query: str, filters: dict[str, object], top_k: int = 5
    ) -> list[dict[str, object]]:
        """Semantic search scoped by metadata filters (e.g. store_id, doc_type)."""
        try:
            client = await self._get_client()
            query_vector = self.embedding.embed_query(query)
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filters.items()
            ]
            results = await client.query_points(
                collection_name=self.config.collection_name,
                query=query_vector,
                query_filter=Filter(must=conditions),
                limit=top_k,
            )
            return self._format_results(results.points)
        except Exception:
            log.warning(
                "rag_retrieve_with_filter_failed", query=query[:50], filters=filters
            )
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_results(points: Any) -> list[dict[str, object]]:
        retrieved: list[dict[str, object]] = []
        for r in points:
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


def deterministic_id(*parts: str) -> int:
    """Return a deterministic unsigned 64-bit int from concatenated string parts.

    Used to generate repeatable Qdrant point IDs so that upserts are
    idempotent and deletes can target known IDs.
    """
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return int(digest[:16], 16)  # 64-bit unsigned
