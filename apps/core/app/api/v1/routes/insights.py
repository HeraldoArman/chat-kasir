from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.commerce import Order, Product, Store
from app.models.user import User
from app.schemas.commerce import (
    DailySummaryResponse,
    OrderDetailResponse,
    OrderResponse,
    ProductResponse,
    RecommendationResponse,
)
from app.services.order import OrderService
from app.services.product import ProductService
from app.services.recommendation import RecommendationService
from app.services.store import StoreService

router = APIRouter(prefix="/stores/me/insights", tags=["Insights"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def _ensure_store_owner(store: Store | None, user: User) -> Store:
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    if store.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this store"
        )
    return store


@router.get("/orders", response_model=list[OrderResponse])
async def list_store_orders(
    db: DBSession,
    current_user: CurrentUser,
    customer_phone: Annotated[str | None, Query(min_length=1, max_length=20)] = None,
) -> list[Order]:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    if customer_phone is not None:
        return await order_service.get_customer_history(store.id, customer_phone, limit=100)
    return await order_service.list_by_store(store.id)


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_store_order_detail(
    order_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Order:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    order = await order_service.get_order_detail(store.id, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/abandoned", response_model=list[OrderResponse])
async def list_abandoned_payments(
    db: DBSession,
    current_user: CurrentUser,
    hours: Annotated[int, Query(ge=1, le=168)] = 24,
) -> list[Order]:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    return await order_service.get_abandoned_payments(store.id, hours=hours)


@router.get("/daily-summary", response_model=DailySummaryResponse)
async def get_daily_summary(
    db: DBSession,
    current_user: CurrentUser,
    target_date: Annotated[date, Query()],
) -> DailySummaryResponse:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    summary = await order_service.get_daily_summary(store.id, target_date)
    return DailySummaryResponse(
        date=str(summary["date"]),
        store_id=summary["store_id"],
        revenue=summary["revenue"],
        order_count=summary["order_count"],
        pending_orders=summary["pending_orders"],
        bestseller=summary["bestseller"],
    )


@router.get("/inventory", response_model=list[ProductResponse])
async def get_low_stock_inventory(
    db: DBSession,
    current_user: CurrentUser,
    threshold: Annotated[int, Query(ge=0, le=100)] = 5,
) -> list[Product]:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    product_service = ProductService(db)
    return await product_service.get_low_stock(store.id, threshold)


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    db: DBSession,
    current_user: CurrentUser,
    customer_phone: Annotated[str | None, Query(min_length=1, max_length=20)] = None,
    keywords: Annotated[list[str] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecommendationResponse:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    service = RecommendationService(db)
    products, reason = await service.recommend(
        store.id,
        customer_phone=customer_phone,
        keywords=keywords,
        limit=limit,
    )
    return RecommendationResponse(
        products=products,
        reason=reason,
    )
