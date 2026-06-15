from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=50)
    whatsapp_number: str | None = Field(None, max_length=20)
    ai_personality: str = Field(default="friendly", max_length=20)
    custom_prompt: str | None = Field(None, max_length=2000)


class StoreCreate(StoreBase):
    slug: str | None = Field(None, min_length=3, max_length=100)


class StoreUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=50)
    whatsapp_number: str | None = Field(None, max_length=20)
    ai_personality: str | None = Field(None, max_length=20)
    custom_prompt: str | None = Field(None, max_length=2000)


class StoreResponse(StoreBase):
    id: UUID
    slug: str
    owner_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    price: int = Field(..., gt=0)
    stock: int | None = Field(None, ge=0)
    weight: int | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    price: int | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    weight: int | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: UUID
    store_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("price", mode="before")
    @classmethod
    def _decimal_to_int(cls, value: object) -> object:
        if isinstance(value, Decimal):
            return int(value)
        return value


class BankAccountBase(BaseModel):
    bank_name: str = Field(..., min_length=1, max_length=50)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_holder_name: str = Field(..., min_length=1, max_length=100)


class BankAccountCreate(BankAccountBase):
    is_primary: bool = False


class BankAccountUpdate(BaseModel):
    bank_name: str | None = Field(None, min_length=1, max_length=50)
    account_number: str | None = Field(None, min_length=1, max_length=50)
    account_holder_name: str | None = Field(None, min_length=1, max_length=100)
    is_primary: bool | None = None


class BankAccountResponse(BankAccountBase):
    id: UUID
    store_id: UUID
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: int = Field(..., gt=0)
    total_price: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_phone: str = Field(..., min_length=1, max_length=20)
    customer_name: str | None = Field(None, max_length=100)
    items: list[OrderItem]
    note: str | None = Field(None, max_length=500)


class OrderResponse(BaseModel):
    id: UUID
    store_id: UUID
    customer_phone: str
    customer_name: str | None
    total: int
    status: str
    items: list[dict[str, object]]
    note: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}

    @field_validator("total", mode="before")
    @classmethod
    def _decimal_to_int(cls, value: object) -> object:
        if isinstance(value, Decimal):
            return int(value)
        return value


class KnowledgeBaseCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    question: str | None = Field(None, max_length=500)
    answer: str = Field(..., min_length=1, max_length=2000)


class KnowledgeBaseResponse(KnowledgeBaseCreate):
    id: UUID
    store_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardSummaryResponse(BaseModel):
    store_id: UUID
    store_name: str
    total_revenue: int
    order_count: int
    pending_orders: int
    product_count: int
    bestseller: dict[str, object] | None


class PublicStoreResponse(StoreResponse):
    products: list[ProductResponse]
    bank_accounts: list[BankAccountResponse]

    model_config = {"from_attributes": True}


class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    quantity: int
    unit_price: int
    total_price: int

    model_config = {"from_attributes": True}

    @field_validator("unit_price", "total_price", mode="before")
    @classmethod
    def _decimal_to_int(cls, value: object) -> object:
        if isinstance(value, Decimal):
            return int(value)
        return value


class CartResponse(BaseModel):
    id: UUID
    store_id: UUID
    customer_phone: str
    items: list[CartItemResponse]
    total: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class CartCheckoutRequest(BaseModel):
    customer_name: str | None = Field(None, max_length=100)
    note: str | None = Field(None, max_length=500)


class PromotionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: int = Field(..., gt=0)
    min_quantity: int | None = Field(None, gt=0)
    start_at: str | None = None
    end_at: str | None = None
    is_active: bool = True


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    discount_type: str | None = Field(None, pattern="^(percentage|fixed)$")
    discount_value: int | None = Field(None, gt=0)
    min_quantity: int | None = Field(None, gt=0)
    start_at: str | None = None
    end_at: str | None = None
    is_active: bool | None = None


class PromotionResponse(PromotionBase):
    id: UUID
    store_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintCreate(BaseModel):
    customer_phone: str = Field(..., min_length=1, max_length=20)
    order_id: UUID | None = None
    category: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=2000)


class ComplaintResponse(BaseModel):
    id: UUID
    store_id: UUID
    customer_phone: str
    order_id: UUID | None
    category: str
    description: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RefundCreate(BaseModel):
    customer_phone: str = Field(..., min_length=1, max_length=20)
    order_id: UUID
    reason: str = Field(..., min_length=1, max_length=2000)


class RefundResponse(BaseModel):
    id: UUID
    store_id: UUID
    customer_phone: str
    order_id: UUID
    reason: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderHistoryResponse(BaseModel):
    orders: list[OrderResponse]


class OrderDetailResponse(OrderResponse):
    pass


class DailySummaryResponse(BaseModel):
    date: str
    store_id: UUID
    revenue: int
    order_count: int
    pending_orders: int
    bestseller: dict[str, object] | None


class RecommendationRequest(BaseModel):
    customer_phone: str | None = None
    keywords: list[str] | None = None
    limit: int = Field(default=5, le=20)


class RecommendationResponse(BaseModel):
    products: list[ProductResponse]
    reason: str
