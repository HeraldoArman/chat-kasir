"""Promotion CRUD service with active-filtering logic."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Promotion
from app.schemas.commerce import PromotionCreate, PromotionUpdate


class PromotionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, store_id: UUID, data: PromotionCreate) -> Promotion:
        promotion = Promotion(
            store_id=store_id,
            name=data.name,
            description=data.description,
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            min_quantity=data.min_quantity,
            start_at=self._parse_optional_dt(data.start_at),
            end_at=self._parse_optional_dt(data.end_at),
            is_active=data.is_active,
        )
        self.db.add(promotion)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def list_active(self, store_id: UUID) -> list[Promotion]:
        """Return promotions that are active AND within their valid date window.

        Active = is_active=True AND (start_at is null OR start_at <= now)
                               AND (end_at is null OR end_at >= now)
        """
        now = datetime.now(tz=None)
        query = select(Promotion).where(
            and_(
                Promotion.store_id == store_id,
                Promotion.is_active.is_(True),
                (Promotion.start_at.is_(None) | (Promotion.start_at <= now)),
                (Promotion.end_at.is_(None) | (Promotion.end_at >= now)),
            )
        )
        result = await self.db.execute(query.order_by(Promotion.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, store_id: UUID, promotion_id: UUID) -> Promotion | None:
        result = await self.db.execute(
            select(Promotion).where(Promotion.store_id == store_id, Promotion.id == promotion_id)
        )
        return result.scalar_one_or_none()

    async def update(self, promotion: Promotion, data: PromotionUpdate) -> Promotion:
        update_data = data.model_dump(exclude_unset=True)
        if "start_at" in update_data:
            update_data["start_at"] = self._parse_optional_dt(update_data["start_at"])
        if "end_at" in update_data:
            update_data["end_at"] = self._parse_optional_dt(update_data["end_at"])
        for field, value in update_data.items():
            setattr(promotion, field, value)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def delete(self, promotion: Promotion) -> None:
        await self.db.delete(promotion)
        await self.db.commit()

    @staticmethod
    def _parse_optional_dt(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)
