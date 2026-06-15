"""Order service for cart/order flow and merchant verification."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Order, OrderStatus, Product, Store
from app.schemas.commerce import OrderCreate
from app.services import indexing as indexing_mod

log = structlog.get_logger()


class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, store: Store, data: OrderCreate) -> Order:
        total = sum(item.total_price for item in data.items)
        order = Order(
            store_id=store.id,
            customer_phone=data.customer_phone,
            customer_name=data.customer_name,
            total=Decimal(total),
            status=OrderStatus.PENDING_PAYMENT,
            items=[item.model_dump() for item in data.items],
            note=data.note,
        )
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        return await self.db.get(Order, order_id)

    async def get_order_detail(self, store_id: UUID, order_id: UUID) -> Order | None:
        result = await self.db.execute(
            select(Order).where(Order.store_id == store_id, Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_by_store(self, store_id: UUID) -> list[Order]:
        result = await self.db.execute(
            select(Order).where(Order.store_id == store_id).order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_customer_history(
        self, store_id: UUID, customer_phone: str, limit: int
    ) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.store_id == store_id, Order.customer_phone == customer_phone)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_abandoned_payments(
        self, store_id: UUID, hours: int = 24, limit: int = 50
    ) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .where(
                Order.store_id == store_id,
                Order.status == OrderStatus.PENDING_PAYMENT,
                Order.created_at < func.now() - timedelta(hours=hours),
            )
            .order_by(Order.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_daily_summary(self, store_id: UUID, target_date: date) -> dict[str, object]:
        start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=UTC)
        end = start + timedelta(days=1)
        date_filter = (Order.created_at >= start) & (Order.created_at < end)

        revenue_result = await self.db.execute(
            select(func.coalesce(func.sum(Order.total), 0)).where(
                Order.store_id == store_id,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
                date_filter,
            )
        )
        revenue_value = revenue_result.scalar()
        revenue = int(revenue_value) if revenue_value else 0

        order_count_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.store_id == store_id,
                date_filter,
            )
        )
        order_count = order_count_result.scalar() or 0

        pending_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.store_id == store_id,
                Order.status == OrderStatus.PENDING_PAYMENT,
                date_filter,
            )
        )
        pending_orders = pending_result.scalar() or 0

        bestseller = await self._get_bestseller_for_date(store_id, start, end)

        return {
            "date": target_date.isoformat(),
            "store_id": store_id,
            "revenue": revenue,
            "order_count": order_count,
            "pending_orders": pending_orders,
            "bestseller": bestseller,
        }

    async def _get_bestseller_for_date(
        self, store_id: UUID, start: datetime, end: datetime
    ) -> dict[str, object] | None:
        orders = await self.db.execute(
            select(Order.items).where(
                Order.store_id == store_id,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
                Order.created_at >= start,
                Order.created_at < end,
            )
        )
        counts: dict[str, int] = {}
        names: dict[str, str] = {}
        for row in orders.scalars():
            for raw_item in row:
                item = dict(raw_item)
                product_id = str(item.get("product_id", ""))
                if not product_id:
                    continue
                quantity_value = item.get("quantity", 0)
                quantity = int(quantity_value) if isinstance(quantity_value, int | str) else 0
                counts[product_id] = counts.get(product_id, 0) + quantity
                names.setdefault(product_id, str(item.get("name", "")))
        if not counts:
            return None
        top_id = max(counts, key=lambda key: counts[key])
        return {"product_id": top_id, "name": names.get(top_id), "quantity": counts[top_id]}

    async def get_inventory_insight(
        self, store_id: UUID, threshold: int = 5
    ) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .where(
                Product.store_id == store_id,
                Product.is_active.is_(True),
                Product.stock <= threshold,
            )
            .order_by(Product.stock.asc())
        )
        return list(result.scalars().all())

    async def verify_payment(self, order: Order) -> Order:
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValueError(f"Cannot verify order in status {order.status}")
        order.status = OrderStatus.CONFIRMED
        await self.db.commit()
        await self.db.refresh(order)

        # Index a memory fact so the chatbot can recall past orders
        try:
            items_summary = ", ".join(
                f"{item.get('name', '?')} x{item.get('quantity', 0)}"
                for item in order.items
            ) if order.items else "no items"
            fact = (
                f"Customer {order.customer_phone or 'unknown'} completed order "
                f"{str(order.id)[:8]}: {items_summary} (Rp {int(order.total):,})".replace(
                    ",", "."
                )
            )
            await indexing_mod.index_customer_memory(
                store_id=str(order.store_id),
                customer_phone=order.customer_phone,
                fact=fact,
            )
        except Exception as exc:
            log.warning("order_memory_index_failed", order_id=str(order.id), error=str(exc))

        return order

    async def get_pending_count(self, store_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.store_id == store_id, Order.status == OrderStatus.PENDING_PAYMENT
            )
        )
        return result.scalar() or 0

    async def get_revenue(self, store_id: UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Order.total), 0)).where(
                Order.store_id == store_id,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
            )
        )
        value = result.scalar()
        return int(value) if value else 0

    async def get_latest_by_customer(
        self,
        store_id: UUID,
        customer_phone: str,
        statuses: list[OrderStatus] | None = None,
    ) -> Order | None:
        query = select(Order).where(
            Order.store_id == store_id, Order.customer_phone == customer_phone
        )
        if statuses:
            query = query.where(Order.status.in_(statuses))
        result = await self.db.execute(query.order_by(Order.created_at.desc()).limit(1))
        return result.scalar_one_or_none()

    async def get_latest_pending_by_customer(
        self, store_id: UUID, customer_phone: str
    ) -> Order | None:
        return await self.get_latest_by_customer(
            store_id, customer_phone, statuses=[OrderStatus.PENDING_PAYMENT]
        )

    async def get_bestseller(self, store_id: UUID) -> dict[str, object] | None:
        """Return the most ordered product from confirmed/paid orders by counting items JSONB."""
        orders = await self.db.execute(
            select(Order.items).where(
                Order.store_id == store_id,
                Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
            )
        )
        counts: dict[str, int] = {}
        names: dict[str, str] = {}
        for row in orders.scalars():
            for raw_item in row:
                item = dict(raw_item)
                product_id = str(item.get("product_id", ""))
                if not product_id:
                    continue
                quantity_value = item.get("quantity", 0)
                quantity = int(quantity_value) if isinstance(quantity_value, int | str) else 0
                counts[product_id] = counts.get(product_id, 0) + quantity
                names.setdefault(product_id, str(item.get("name", "")))
        if not counts:
            return None
        top_id = max(counts, key=lambda key: counts[key])
        return {"product_id": top_id, "name": names.get(top_id), "quantity": counts[top_id]}

    async def reserve_stock(self, items: list[dict[str, object]]) -> None:
        for item in items:
            product_id = item.get("product_id")
            raw_quantity = item.get("quantity", 0)
            quantity = int(raw_quantity) if isinstance(raw_quantity, int | str) else 0
            if not product_id or quantity <= 0:
                continue
            product = (
                await self.db.execute(
                    select(Product)
                    .where(Product.id == UUID(str(product_id)))
                    .with_for_update(nowait=True)
                )
            ).scalar_one_or_none()
            if product is None:
                raise ValueError(f"Product {product_id} not found")
            if product.stock is not None and product.stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}")
            if product.stock is not None:
                product.stock -= quantity
        await self.db.flush()

    async def cancel_order(self, store_id: UUID, order_id: UUID) -> Order:
        order = await self.get_order_detail(store_id, order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValueError(f"Cannot cancel order in status {order.status}")

        for raw_item in order.items:
            item = dict(raw_item)
            product_id = item.get("product_id")
            raw_quantity = item.get("quantity", 0)
            quantity = int(raw_quantity) if isinstance(raw_quantity, int | str) else 0
            if not product_id or quantity <= 0:
                continue
            product = (
                await self.db.execute(
                    select(Product)
                    .where(Product.id == UUID(str(product_id)))
                    .with_for_update(nowait=True)
                )
            ).scalar_one_or_none()
            if product is None or product.stock is None:
                continue
            product.stock += quantity

        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(order)
        return order
