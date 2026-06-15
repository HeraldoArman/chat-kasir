"""Persistent cart service for the commerce backend."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Cart, CartItem, Order, Product, Store
from app.schemas.commerce import CartItemResponse, CartResponse, OrderCreate, OrderItem
from app.services.order import OrderService


class CartService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_cart_query(self, store_id: UUID, customer_phone: str) -> Cart | None:
        result = await self.db.execute(
            select(Cart)
            .where(Cart.store_id == store_id, Cart.customer_phone == customer_phone)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_product(self, store_id: UUID, product_id: UUID) -> Product:
        product = await self.db.get(Product, product_id)
        if product is None:
            raise ValueError(f"Product {product_id} not found")
        if product.store_id != store_id:
            raise ValueError(f"Product {product_id} does not belong to this store")
        return product

    @staticmethod
    def _has_enough_stock(product: Product, quantity: int) -> None:
        if product.stock is not None and quantity > product.stock:
            raise ValueError(f"Insufficient stock for {product.name}")

    @staticmethod
    def _find_item_by_product_id(cart: Cart, product_id: UUID) -> CartItem | None:
        for item in cart.items:
            if item.product_id == product_id:
                return item
        return None

    async def get_or_create_cart(self, store_id: UUID, customer_phone: str) -> Cart:
        cart = await self._get_cart_query(store_id, customer_phone)
        if cart is not None:
            return cart
        store = await self.db.get(Store, store_id)
        if store is None:
            raise ValueError(f"Store {store_id} not found")
        cart = Cart(store_id=store_id, customer_phone=customer_phone)
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def add_item(
        self,
        store_id: UUID,
        customer_phone: str,
        product_id: UUID,
        quantity: int,
    ) -> Cart:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        product = await self._get_product(store_id, product_id)
        self._has_enough_stock(product, quantity)
        cart = await self.get_or_create_cart(store_id, customer_phone)
        existing_item = self._find_item_by_product_id(cart, product_id)
        if existing_item is not None:
            new_quantity = existing_item.quantity + quantity
            self._has_enough_stock(product, new_quantity)
            existing_item.quantity = new_quantity
        else:
            cart.items.append(
                CartItem(
                    product_id=product_id,
                    name=product.name,
                    quantity=quantity,
                    unit_price=Decimal(product.price),
                )
            )
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def update_item(
        self,
        store_id: UUID,
        customer_phone: str,
        cart_item_id: UUID,
        quantity: int,
    ) -> Cart:
        cart = await self.get_or_create_cart(store_id, customer_phone)
        item = next((i for i in cart.items if i.id == cart_item_id), None)
        if item is None:
            raise ValueError(f"Cart item {cart_item_id} not found")
        if quantity <= 0:
            await self.db.delete(item)
            await self.db.commit()
            await self.db.refresh(cart)
            return cart
        product = await self._get_product(store_id, item.product_id)
        self._has_enough_stock(product, quantity)
        item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def remove_item(
        self,
        store_id: UUID,
        customer_phone: str,
        cart_item_id: UUID,
    ) -> Cart:
        cart = await self.get_or_create_cart(store_id, customer_phone)
        item = next((i for i in cart.items if i.id == cart_item_id), None)
        if item is None:
            raise ValueError(f"Cart item {cart_item_id} not found")
        await self.db.delete(item)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def get_cart(self, store_id: UUID, customer_phone: str) -> CartResponse:
        cart = await self.get_or_create_cart(store_id, customer_phone)
        return self.to_response(cart)

    @staticmethod
    def _compute_total(cart: Cart) -> Decimal:
        return sum(
            (Decimal(item.unit_price) * item.quantity for item in cart.items),
            Decimal(0),
        )

    async def clear_cart(self, store_id: UUID, customer_phone: str) -> None:
        cart = await self._get_cart_query(store_id, customer_phone)
        if cart is None:
            return
        await self.db.delete(cart)
        await self.db.commit()

    async def checkout(
        self,
        store_id: UUID,
        customer_phone: str,
        customer_name: str | None,
        note: str | None,
    ) -> Order:
        cart = await self._get_cart_query(store_id, customer_phone)
        if cart is None or not cart.items:
            raise ValueError("Cart is empty")
        store = await self.db.get(Store, store_id)
        if store is None:
            raise ValueError(f"Store {store_id} not found")
        order_items: list[OrderItem] = []
        reserve_payload: list[dict[str, object]] = []
        for item in cart.items:
            product = await self._get_product(store_id, item.product_id)
            self._has_enough_stock(product, item.quantity)
            order_items.append(
                OrderItem(
                    product_id=str(item.product_id),
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=int(item.unit_price),
                    total_price=int(item.unit_price * item.quantity),
                )
            )
            reserve_payload.append(
                {"product_id": str(item.product_id), "quantity": item.quantity}
            )
        order_service = OrderService(self.db)
        await order_service.reserve_stock(reserve_payload)
        order = await order_service.create(
            store,
            OrderCreate(
                customer_phone=customer_phone,
                customer_name=customer_name,
                items=order_items,
                note=note,
            ),
        )
        await self.clear_cart(store_id, customer_phone)
        return order

    def to_response(self, cart: Cart) -> CartResponse:
        total = self._compute_total(cart)
        return CartResponse(
            id=cart.id,
            store_id=cart.store_id,
            customer_phone=cart.customer_phone,
            items=[
                CartItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=int(item.unit_price),
                    total_price=int(item.unit_price * item.quantity),
                )
                for item in cart.items
            ],
            total=int(total),
            created_at=str(cart.created_at),
            updated_at=str(cart.updated_at) if cart.updated_at is not None else None,
        )
