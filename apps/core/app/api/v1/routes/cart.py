from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.commerce import (
    CartCheckoutRequest,
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
    OrderResponse,
)
from app.services.cart import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])

DBSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=CartResponse)
async def get_cart(
    store_id: Annotated[UUID, Query()],
    customer_phone: Annotated[str, Query(min_length=1, max_length=20)],
    db: DBSession,
) -> CartResponse:
    service = CartService(db)
    try:
        return await service.get_cart(store_id, customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(
    store_id: Annotated[UUID, Query()],
    customer_phone: Annotated[str, Query(min_length=1, max_length=20)],
    data: CartItemCreate,
    db: DBSession,
) -> CartResponse:
    service = CartService(db)
    try:
        await service.add_item(store_id, customer_phone, data.product_id, data.quantity)
        return await service.get_cart(store_id, customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.patch("/items/{cart_item_id}", response_model=CartResponse)
async def update_cart_item(
    cart_item_id: UUID,
    store_id: Annotated[UUID, Query()],
    customer_phone: Annotated[str, Query(min_length=1, max_length=20)],
    data: CartItemUpdate,
    db: DBSession,
) -> CartResponse:
    service = CartService(db)
    try:
        await service.update_item(store_id, customer_phone, cart_item_id, data.quantity)
        return await service.get_cart(store_id, customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/items/{cart_item_id}", response_model=CartResponse)
async def remove_cart_item(
    cart_item_id: UUID,
    store_id: Annotated[UUID, Query()],
    customer_phone: Annotated[str, Query(min_length=1, max_length=20)],
    db: DBSession,
) -> CartResponse:
    service = CartService(db)
    try:
        await service.remove_item(store_id, customer_phone, cart_item_id)
        return await service.get_cart(store_id, customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    store_id: Annotated[UUID, Query()],
    customer_phone: Annotated[str, Query(min_length=1, max_length=20)],
    data: CartCheckoutRequest,
    db: DBSession,
) -> OrderResponse:
    service = CartService(db)
    try:
        order = await service.checkout(
            store_id,
            customer_phone,
            customer_name=data.customer_name,
            note=data.note,
        )
        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
