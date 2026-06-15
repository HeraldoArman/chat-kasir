from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.commerce import Promotion, Store
from app.models.user import User
from app.schemas.commerce import PromotionCreate, PromotionResponse, PromotionUpdate
from app.services.promotion import PromotionService
from app.services.store import StoreService

router = APIRouter(prefix="/stores/me/promotions", tags=["Promotions"])

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


@router.post("", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    data: PromotionCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Promotion:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    service = PromotionService(db)
    try:
        return await service.create(store.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("", response_model=list[PromotionResponse])
async def list_promotions(
    db: DBSession,
    current_user: CurrentUser,
) -> list[Promotion]:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    service = PromotionService(db)
    return await service.list_active(store.id)


@router.patch("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: UUID,
    data: PromotionUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> Promotion:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    service = PromotionService(db)
    promotion = await service.get_by_id(store.id, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    try:
        return await service.update(promotion, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    service = PromotionService(db)
    promotion = await service.get_by_id(store.id, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    await service.delete(promotion)
