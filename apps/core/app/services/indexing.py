"""Indexing helpers for Qdrant/RAG.

Keeps product catalog and FAQ entries searchable by embedding them whenever
they are created or updated. Failures degrade gracefully and do not break the
primary request.
"""

from __future__ import annotations

import structlog

from app.core.config import get_config
from app.models.commerce import KnowledgeBase, Product
from app.services.embedding import EmbeddingService
from app.services.rag import RAGService

log = structlog.get_logger()


def _get_rag_service() -> RAGService | None:
    config = get_config()
    if not config.rag.enabled or not config.rag.qdrant_url:
        return None
    try:
        embedding = EmbeddingService(model_name=config.rag.embedding_model)
        return RAGService(config=config.rag, embedding_service=embedding)
    except Exception as e:
        log.warning("rag_service_init_failed", error=str(e))
        return None


def _format_product_text(product: Product) -> str:
    parts = [product.name]
    if product.description:
        parts.append(product.description)
    parts.append(f"Harga: Rp {int(product.price):,}".replace(",", "."))
    if product.stock is not None:
        parts.append(f"Stok: {product.stock}")
    return " | ".join(parts)


def _format_knowledge_text(entry: KnowledgeBase) -> str:
    parts: list[str] = []
    if entry.question:
        parts.append(entry.question)
    parts.append(entry.answer)
    return " | ".join(parts)


def index_product(product: Product) -> None:
    """Embed and upsert a product into the RAG collection."""
    rag = _get_rag_service()
    if rag is None:
        return
    try:
        text = _format_product_text(product)
        metadata: dict[str, object] = {
            "doc_type": "product",
            "store_id": str(product.store_id),
            "product_id": str(product.id),
            "name": product.name,
            "is_active": product.is_active,
        }
        rag.add_documents([text], [metadata])
        log.info("product_indexed", product_id=str(product.id))
    except Exception as e:
        log.warning("product_index_failed", product_id=str(product.id), error=str(e))


def index_knowledge(entry: KnowledgeBase) -> None:
    """Embed and upsert a knowledge entry into the RAG collection."""
    rag = _get_rag_service()
    if rag is None:
        return
    try:
        text = _format_knowledge_text(entry)
        metadata: dict[str, object] = {
            "doc_type": "faq",
            "store_id": str(entry.store_id),
            "entry_id": str(entry.id),
            "category": entry.category,
            "question": entry.question or "",
        }
        rag.add_documents([text], [metadata])
        log.info("knowledge_indexed", entry_id=str(entry.id))
    except Exception as e:
        log.warning("knowledge_index_failed", entry_id=str(entry.id), error=str(e))
