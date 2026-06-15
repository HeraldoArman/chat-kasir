"""Knowledge base CRUD service."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import KnowledgeBase, Store
from app.schemas.commerce import KnowledgeBaseCreate


class KnowledgeBaseService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, store: Store, data: KnowledgeBaseCreate) -> KnowledgeBase:
        entry = KnowledgeBase(
            store_id=store.id,
            category=data.category,
            question=data.question,
            answer=data.answer,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def search_by_query(
        self, store_id: UUID, query: str, limit: int = 5
    ) -> list[KnowledgeBase]:
        """Return FAQ entries matching query in question or answer."""
        q = select(KnowledgeBase).where(KnowledgeBase.store_id == store_id)
        like = f"%{query}%"
        q = q.where(or_(KnowledgeBase.question.ilike(like), KnowledgeBase.answer.ilike(like)))
        result = await self.db.execute(q.order_by(KnowledgeBase.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    def build_search_text(self, entry: KnowledgeBase) -> str:
        """Build a single searchable text from a knowledge entry."""
        parts: list[str] = []
        if entry.question:
            parts.append(entry.question)
        parts.append(entry.answer)
        return " | ".join(parts)

    async def list_by_store(self, store_id: UUID, category: str | None = None) -> list[KnowledgeBase]:
        query = select(KnowledgeBase).where(KnowledgeBase.store_id == store_id)
        if category:
            query = query.where(KnowledgeBase.category == category)
        result = await self.db.execute(query.order_by(KnowledgeBase.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, entry_id: UUID) -> KnowledgeBase | None:
        return await self.db.get(KnowledgeBase, entry_id)

    async def delete(self, entry: KnowledgeBase) -> None:
        await self.db.delete(entry)
        await self.db.commit()
