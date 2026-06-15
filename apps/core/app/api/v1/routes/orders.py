from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.commerce import Order, Store
from app.models.user import User
from app.schemas.commerce import OrderCreate, OrderResponse
from app.services.order import OrderService
from app.services.store import StoreService

router = APIRouter(prefix="/orders", tags=["Orders"])

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


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    store_id: UUID,
    data: OrderCreate,
    db: DBSession,
) -> Order:
    """Public endpoint used by the AI agent to create an order for a store."""
    store_service = StoreService(db)
    store = await store_service.get_by_id(store_id)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    order_service = OrderService(db)
    try:
        await order_service.reserve_stock([item.model_dump() for item in data.items])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return await order_service.create(store, data)


@router.get("/stores/me", response_model=list[OrderResponse])
async def list_my_orders(
    db: DBSession,
    current_user: CurrentUser,
) -> list[Order]:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await OrderService(db).list_by_store(store.id)


@router.post("/{order_id}/verify", response_model=OrderResponse)
async def verify_order_payment(
    order_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Order:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    order = await order_service.get_by_id(order_id)
    if order is None or order.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    try:
        return await order_service.verify_payment(order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
