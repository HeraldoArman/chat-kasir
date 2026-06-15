"""Recommendation service with multiple strategies.

Strategies (tried in order):
  a) Customer history — products in same category as past purchases, excluding already-bought
  b) Keyword/semantic search — ProductService.search_by_keywords or RAGService.retrieve_with_filter
  c) Fallback — best sellers / popular products from order data
"""

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Order, OrderStatus, Product

log = structlog.get_logger()

_REASON_HISTORY = "Berdasarkan riwayat belanja Anda"
_REASON_KEYWORDS = "Sesuai dengan kata kunci pencarian"
_REASON_SEMANTIC = "Rekomendasi berdasarkan kesesuaian"
_REASON_POPULAR = "Populer"
_REASON_FALLBACK = "Produk unggulan"


class RecommendationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def recommend(
        self,
        store_id: UUID,
        customer_phone: str | None = None,
        keywords: list[str] | None = None,
        limit: int = 5,
        rag_service: Any | None = None,
    ) -> tuple[list[Product], str]:
        """Return (products, reason) using the first strategy that yields results.

        Parameters
        ----------
        store_id : UUID
            Scope recommendations to this store.
        customer_phone : str | None
            If provided, attempt history-based recommendations.
        keywords : list[str] | None
            If provided (and history yields nothing), use keyword / semantic search.
        limit : int
            Maximum products to return.
        rag_service : Any | None
            Optional RAGService instance for semantic search via Qdrant.
        """
        # Strategy A: customer order history
        if customer_phone is not None:
            products = await self._from_history(store_id, customer_phone, limit)
            if products:
                return products, _REASON_HISTORY

        # Strategy B: keyword / semantic search
        if keywords:
            products = await self._from_keywords(store_id, keywords, limit, rag_service)
            if products:
                return products, _REASON_KEYWORDS if rag_service is None else _REASON_SEMANTIC

        # Strategy C: popular / best sellers fallback
        products = await self._from_popular(store_id, limit)
        if products:
            return products, _REASON_POPULAR

        # Strategy D: newest products as last resort
        products = await self._from_newest(store_id, limit)
        return products, _REASON_FALLBACK

    # ── Strategy A: customer purchase history ──────────────────────────

    async def _from_history(self, store_id: UUID, customer_phone: str, limit: int) -> list[Product]:
        """Find products related to what the customer already bought."""
        # Collect product IDs from past orders
        bought_ids = await self._get_customer_product_ids(store_id, customer_phone)
        if not bought_ids:
            return []

        # Gather keywords from purchased product names for broad matching
        purchased = await self._get_products_by_ids(bought_ids)
        if not purchased:
            return []

        keywords: list[str] = []
        for p in purchased:
            if p.name:
                keywords.extend(p.name.lower().split())
            if p.description:
                keywords.extend(p.description.lower().split()[:5])

        # Deduplicate and search
        unique_kw = list(dict.fromkeys(keywords))[:10]
        if not unique_kw:
            return []

        query = select(Product).where(
            Product.store_id == store_id,
            Product.is_active.is_(True),
            (Product.stock.is_(None) | (Product.stock > 0)),
        )
        filters = []
        for kw in unique_kw:
            like = f"%{kw}%"
            filters.append(Product.name.ilike(like))
            filters.append(Product.description.ilike(like))
        query = query.where(or_(*filters))

        # Exclude already-bought products
        if bought_ids:
            query = query.where(Product.id.notin_(bought_ids))

        query = query.order_by(Product.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_customer_product_ids(self, store_id: UUID, customer_phone: str) -> list[UUID]:
        """Get product IDs from a customer's confirmed/paid orders."""
        rows = await self.db.execute(
            select(Order.items).where(
                Order.store_id == store_id,
                Order.customer_phone == customer_phone,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
            )
        )
        ids: list[UUID] = []
        for row in rows.scalars():
            for raw_item in row:
                item = dict(raw_item)
                pid = item.get("product_id")
                if pid:
                    ids.append(UUID(str(pid)))
        return list(dict.fromkeys(ids))

    async def _get_products_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        if not product_ids:
            return []
        result = await self.db.execute(select(Product).where(Product.id.in_(product_ids)))
        return list(result.scalars().all())

    # ── Strategy B: keyword / semantic search ───────────────────────────

    async def _from_keywords(
        self,
        store_id: UUID,
        keywords: list[str],
        limit: int,
        rag_service: Any | None = None,
    ) -> list[Product]:
        """Try RAGService semantic search first, fall back to DB keyword search."""
        # Attempt semantic search via Qdrant if RAG service is available
        if rag_service is not None and hasattr(rag_service, "retrieve_with_filter"):
            products = await self._semantic_search(store_id, keywords, limit, rag_service)
            if products:
                return products

        # Fallback: DB-level keyword search (delegates to ProductService pattern)
        query = select(Product).where(
            Product.store_id == store_id,
            Product.is_active.is_(True),
            (Product.stock.is_(None) | (Product.stock > 0)),
        )
        filters = []
        for kw in keywords:
            like = f"%{kw}%"
            filters.append(Product.name.ilike(like))
            filters.append(Product.description.ilike(like))
        if filters:
            query = query.where(or_(*filters))

        query = query.order_by(Product.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _semantic_search(
        self,
        store_id: UUID,
        keywords: list[str],
        limit: int,
        rag_service: Any,
    ) -> list[Product]:
        """Use RAGService.retrieve_with_filter to find products semantically."""
        try:
            results = await rag_service.retrieve_with_filter(
                query=" ".join(keywords),
                filters={"store_id": str(store_id), "doc_type": "product"},
                top_k=limit * 2,
            )
        except Exception:
            log.warning("recommendation_semantic_search_failed")
            return []

        product_ids: list[UUID] = []
        for r in results:
            metadata = r.get("metadata", {})
            pid = metadata.get("product_id")
            if pid:
                product_ids.append(UUID(str(pid)))

        if not product_ids:
            return []

        # Verify products are active and in stock
        result = await self.db.execute(
            select(Product).where(
                Product.id.in_(product_ids),
                Product.store_id == store_id,
                Product.is_active.is_(True),
                (Product.stock.is_(None) | (Product.stock > 0)),
            )
        )
        found = list(result.scalars().all())
        # Preserve ranking order from semantic search
        id_to_product = {p.id: p for p in found}
        return [id_to_product[pid] for pid in product_ids if pid in id_to_product][:limit]

    # ── Strategy C: popular / best sellers ───────────────────────────────

    async def _from_popular(self, store_id: UUID, limit: int) -> list[Product]:
        """Return most-ordered products from confirmed/paid orders."""
        rows = await self.db.execute(
            select(Order.items).where(
                Order.store_id == store_id,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
            )
        )
        counts: dict[UUID, int] = {}
        for row in rows.scalars():
            for raw_item in row:
                item = dict(raw_item)
                pid = item.get("product_id")
                if pid:
                    uid = UUID(str(pid))
                    qty = item.get("quantity", 0)
                    counts[uid] = counts.get(uid, 0) + (
                        int(qty) if isinstance(qty, int | str) else 0
                    )

        if not counts:
            return []

        # Sort by order count descending
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        top_ids = [pid for pid, _ in ranked[:limit]]

        result = await self.db.execute(
            select(Product).where(
                Product.id.in_(top_ids),
                Product.store_id == store_id,
                Product.is_active.is_(True),
                (Product.stock.is_(None) | (Product.stock > 0)),
            )
        )
        products = list(result.scalars().all())

        # Preserve popularity ranking order
        id_to_product = {p.id: p for p in products}
        return [id_to_product[pid] for pid in top_ids if pid in id_to_product]

    # ── Strategy D: newest products ──────────────────────────────────────

    async def _from_newest(self, store_id: UUID, limit: int) -> list[Product]:
        """Last resort: return the newest active, in-stock products."""
        result = await self.db.execute(
            select(Product)
            .where(
                Product.store_id == store_id,
                Product.is_active.is_(True),
                (Product.stock.is_(None) | (Product.stock > 0)),
            )
            .order_by(Product.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
