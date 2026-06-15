"""Order service for cart/order flow and merchant verification."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Order, OrderStatus, Product, Store
from app.schemas.commerce import OrderCreate


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

    async def list_by_store(self, store_id: UUID) -> list[Order]:
        result = await self.db.execute(
            select(Order).where(Order.store_id == store_id).order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def verify_payment(self, order: Order) -> Order:
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValueError(f"Cannot verify order in status {order.status}")
        order.status = OrderStatus.CONFIRMED
        await self.db.commit()
        await self.db.refresh(order)
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
            product = await self.db.get(Product, UUID(str(product_id)))
            if product is None:
                raise ValueError(f"Product {product_id} not found")
            if product.stock is not None and product.stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}")
            if product.stock is not None:
                product.stock -= quantity
        await self.db.flush()
