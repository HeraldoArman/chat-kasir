"""Complaint intake service for merchants."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.notifications import notify_merchant_complaint
from app.models.commerce import Complaint, Order, Store


class ComplaintService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        store_id: UUID,
        customer_phone: str,
        category: str,
        description: str,
        order_id: UUID | None = None,
    ) -> Complaint:
        if order_id is not None:
            order = await self.db.get(Order, order_id)
            if order is None:
                raise ValueError(f"Order {order_id} not found")
            if order.store_id != store_id:
                raise ValueError(f"Order {order_id} does not belong to store {store_id}")

        store = await self.db.get(Store, store_id)
        if store is None:
            raise ValueError(f"Store {store_id} not found")

        complaint = Complaint(
            store_id=store_id,
            customer_phone=customer_phone,
            order_id=order_id,
            category=category,
            description=description,
            status="open",
        )
        self.db.add(complaint)
        await self.db.commit()
        await self.db.refresh(complaint)
        await notify_merchant_complaint(complaint, store)
        return complaint

    async def list(self, store_id: UUID, status: str | None = None, limit: int = 50) -> list[Complaint]:
        query = select(Complaint).where(Complaint.store_id == store_id)
        if status is not None:
            query = query.where(Complaint.status == status)
        result = await self.db.execute(query.order_by(Complaint.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, store_id: UUID, complaint_id: UUID) -> Complaint | None:
        result = await self.db.execute(
            select(Complaint).where(
                Complaint.store_id == store_id, Complaint.id == complaint_id
            )
        )
        return result.scalar_one_or_none()
