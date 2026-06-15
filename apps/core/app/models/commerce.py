from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID as UuidType
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base
from app.models.user import User


class OrderStatus(StrEnum):
    CART = "cart"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ai_personality: Mapped[str] = mapped_column(String(20), default="friendly")
    custom_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    owner: Mapped[User] = relationship("User", lazy="selectin")
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="store", lazy="selectin", cascade="all, delete-orphan"
    )
    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount", back_populates="store", lazy="selectin", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="store", lazy="selectin"
    )
    knowledge_entries: Mapped[list["KnowledgeBase"]] = relationship(
        "KnowledgeBase", back_populates="store", lazy="selectin", cascade="all, delete-orphan"
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart", lazy="selectin", cascade="all, delete-orphan"
    )
    promotions: Mapped[list["Promotion"]] = relationship(
        "Promotion", lazy="selectin", cascade="all, delete-orphan"
    )
    complaints: Mapped[list["Complaint"]] = relationship(
        "Complaint", lazy="selectin", cascade="all, delete-orphan"
    )
    refund_requests: Mapped[list["RefundRequest"]] = relationship(
        "RefundRequest", lazy="selectin", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    store: Mapped[Store] = relationship("Store", back_populates="products", lazy="selectin")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped[Store] = relationship("Store", back_populates="bank_accounts", lazy="selectin")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(String(20), default=OrderStatus.PENDING_PAYMENT)
    items: Mapped[list[dict[str, object]]] = mapped_column(JSONB, default=list)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    store: Mapped[Store] = relationship("Store", back_populates="orders", lazy="selectin")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped[Store] = relationship(
        "Store", back_populates="knowledge_entries", lazy="selectin"
    )


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    store: Mapped[Store] = relationship("Store", lazy="selectin", overlaps="carts")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", lazy="selectin", cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    cart_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    cart: Mapped[Cart] = relationship("Cart", back_populates="items", lazy="selectin")
    product: Mapped[Product] = relationship("Product", lazy="selectin")


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    min_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped[Store] = relationship("Store", lazy="selectin", overlaps="promotions")


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    order_id: Mapped[UuidType | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped[Store] = relationship("Store", lazy="selectin", overlaps="complaints")
    order: Mapped[Order | None] = relationship("Order", lazy="selectin")


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id: Mapped[UuidType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    order_id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped[Store] = relationship("Store", lazy="selectin", overlaps="refund_requests")
    order: Mapped[Order] = relationship("Order", lazy="selectin")
