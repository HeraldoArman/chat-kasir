"""Refund request intake service for merchants."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.notifications import notify_merchant_refund
from app.models.commerce import Order, RefundRequest, Store


class RefundService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        store_id: UUID,
        customer_phone: str,
        order_id: UUID,
        reason: str,
    ) -> RefundRequest:
        order = await self.db.get(Order, order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if order.store_id != store_id:
            raise ValueError(f"Order {order_id} does not belong to store {store_id}")
        if order.customer_phone != customer_phone:
            raise ValueError("Customer phone does not match order")

        store = await self.db.get(Store, store_id)
        if store is None:
            raise ValueError(f"Store {store_id} not found")

        refund = RefundRequest(
            store_id=store_id,
            customer_phone=customer_phone,
            order_id=order_id,
            reason=reason,
            status="pending",
        )
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        merchant_phone = store.owner.whatsapp_number or store.whatsapp_number
        if merchant_phone:
            await notify_merchant_refund(refund, merchant_phone)
        return refund

    async def list(self, store_id: UUID, status: str | None = None, limit: int = 50) -> list[RefundRequest]:
        query = select(RefundRequest).where(RefundRequest.store_id == store_id)
        if status is not None:
            query = query.where(RefundRequest.status == status)
        result = await self.db.execute(query.order_by(RefundRequest.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, store_id: UUID, refund_id: UUID) -> RefundRequest | None:
        result = await self.db.execute(
            select(RefundRequest).where(
                RefundRequest.store_id == store_id, RefundRequest.id == refund_id
            )
        )
        return result.scalar_one_or_none()
