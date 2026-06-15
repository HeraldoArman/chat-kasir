"""Store CRUD service with slug generation."""

import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Store
from app.models.user import User
from app.schemas.commerce import StoreCreate, StoreUpdate

_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _slugify(text: str) -> str:
    value = text.lower().strip().replace(" ", "-")
    value = _SLUG_RE.sub("", value)
    return value[:100].strip("-")


class StoreService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, owner: User, data: StoreCreate) -> Store:
        existing_owner = await self.get_by_owner(owner.id)
        if existing_owner is not None:
            raise ValueError("You already have a store")
        slug = _slugify(data.slug or data.name)
        if not slug or len(slug) < 3:
            raise ValueError("Store slug must be at least 3 characters")

        existing = await self.get_by_slug(slug)
        if existing is not None:
            raise ValueError(f"Store slug '{slug}' is already taken")

        store = Store(
            owner_id=owner.id,
            name=data.name,
            slug=slug,
            description=data.description,
            category=data.category,
            whatsapp_number=data.whatsapp_number,
            ai_personality=data.ai_personality,
            custom_prompt=data.custom_prompt,
        )
        self.db.add(store)
        await self.db.commit()
        await self.db.refresh(store)
        return store

    async def get_by_id(self, store_id: UUID) -> Store | None:
        return await self.db.get(Store, store_id)

    async def get_by_slug(self, slug: str) -> Store | None:
        result = await self.db.execute(select(Store).where(Store.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> Store | None:
        result = await self.db.execute(select(Store).where(Store.owner_id == owner_id))
        return result.scalar_one_or_none()

    async def update(self, store: Store, data: StoreUpdate) -> Store:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(store, field, value)
        await self.db.commit()
        await self.db.refresh(store)
        return store

    async def delete(self, store: Store) -> None:
        await self.db.delete(store)
        await self.db.commit()
