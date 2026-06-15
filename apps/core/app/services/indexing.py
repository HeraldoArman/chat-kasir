"""Indexing helpers for Qdrant/RAG.

Keeps product catalog, FAQ entries, and customer memory facts searchable by
embedding them into Qdrant. Failures degrade gracefully and do not break the
primary request.

All public functions are async so they can be awaited from async route
handlers or service methods.
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_config
from app.models.commerce import KnowledgeBase, Product
from app.services.embedding import EmbeddingService
from app.services.rag import RAGService, deterministic_id

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


async def index_product(product: Product) -> None:
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
        point_id = deterministic_id("product", str(product.store_id), str(product.id))
        await rag.add_documents([text], [metadata], point_ids=[point_id])
        log.info("product_indexed", product_id=str(product.id))
    except Exception as e:
        log.warning("product_index_failed", product_id=str(product.id), error=str(e))


async def index_knowledge(entry: KnowledgeBase) -> None:
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
        point_id = deterministic_id("faq", str(entry.store_id), str(entry.id))
        await rag.add_documents([text], [metadata], point_ids=[point_id])
        log.info("knowledge_indexed", entry_id=str(entry.id))
    except Exception as e:
        log.warning("knowledge_index_failed", entry_id=str(entry.id), error=str(e))


async def delete_document(doc_type: str, store_id: str, item_id: str) -> None:
    """Remove a single document from Qdrant by its deterministic point ID.

    Uses the same hashing scheme as ``index_product`` / ``index_knowledge``
    so the point ID is always recoverable from the primary key.
    """
    rag = _get_rag_service()
    if rag is None:
        return
    try:
        point_id = deterministic_id(doc_type, store_id, item_id)
        await rag.delete_by_point_ids([point_id])
        log.info("document_deleted", doc_type=doc_type, store_id=store_id, item_id=item_id)
    except Exception as e:
        log.warning(
            "document_delete_failed",
            doc_type=doc_type,
            store_id=store_id,
            item_id=item_id,
            error=str(e),
        )


async def index_customer_memory(store_id: str, customer_phone: str, fact: str) -> None:
    """Store a memory fact about a customer as a Qdrant point.

    Uses a deterministic ID derived from ``store_id + customer_phone + fact``
    so the same fact is idempotent (upserts overwrite).
    """
    rag = _get_rag_service()
    if rag is None:
        return
    try:
        metadata: dict[str, object] = {
            "doc_type": "memory",
            "store_id": store_id,
            "customer_phone": customer_phone,
        }
        point_id = deterministic_id("memory", store_id, customer_phone, fact)
        await rag.add_documents([fact], [metadata], point_ids=[point_id])
        log.info(
            "customer_memory_indexed",
            store_id=store_id,
            customer_phone=customer_phone,
        )
    except Exception as e:
        log.warning(
            "customer_memory_index_failed",
            store_id=store_id,
            customer_phone=customer_phone,
            error=str(e),
        )


async def bulk_reindex_store(db: AsyncSession, store_id: str) -> dict[str, int]:
    """Delete all existing points for *store_id* and re-index products + FAQ.

    Returns a summary ``{"products": n, "faq": m}``.
    """
    rag = _get_rag_service()
    if rag is None:
        return {"products": 0, "faq": 0}

    # 1. Wipe existing data for this store
    await rag.delete_by_filter({"store_id": store_id})

    # 2. Re-index all active products
    product_result = await db.execute(
        select(Product).where(Product.store_id == store_id, Product.is_active.is_(True))
    )
    products: list[Product] = list(product_result.scalars().all())

    product_texts: list[str] = []
    product_metas: list[dict[str, object]] = []
    product_ids: list[int] = []

    for p in products:
        product_texts.append(_format_product_text(p))
        product_metas.append({
            "doc_type": "product",
            "store_id": str(p.store_id),
            "product_id": str(p.id),
            "name": p.name,
            "is_active": p.is_active,
        })
        product_ids.append(deterministic_id("product", str(p.store_id), str(p.id)))

    if product_texts:
        await rag.add_documents(product_texts, product_metas, point_ids=product_ids)

    # 3. Re-index all knowledge entries
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.store_id == store_id)
    )
    entries: list[KnowledgeBase] = list(kb_result.scalars().all())

    faq_texts: list[str] = []
    faq_metas: list[dict[str, object]] = []
    faq_ids: list[int] = []

    for e in entries:
        faq_texts.append(_format_knowledge_text(e))
        faq_metas.append({
            "doc_type": "faq",
            "store_id": str(e.store_id),
            "entry_id": str(e.id),
            "category": e.category,
            "question": e.question or "",
        })
        faq_ids.append(deterministic_id("faq", str(e.store_id), str(e.id)))

    if faq_texts:
        await rag.add_documents(faq_texts, faq_metas, point_ids=faq_ids)

    log.info(
        "store_reindexed",
        store_id=store_id,
        products=len(products),
        faq=len(entries),
    )
    return {"products": len(products), "faq": len(entries)}
