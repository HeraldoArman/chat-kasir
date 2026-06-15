from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.commerce import BankAccount, KnowledgeBase, Product, Store
from app.models.user import User
from app.schemas.commerce import (
    BankAccountCreate,
    BankAccountResponse,
    BankAccountUpdate,
    DashboardSummaryResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    PublicStoreResponse,
    StoreCreate,
    StoreResponse,
    StoreUpdate,
)
from app.services.bank import BankAccountService
from app.services.indexing import index_knowledge, index_product
from app.services.knowledge import KnowledgeBaseService
from app.services.order import OrderService
from app.services.product import ProductService
from app.services.store import StoreService

router = APIRouter(prefix="/stores", tags=["Stores"])

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


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    data: StoreCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Store:
    service = StoreService(db)
    try:
        return await service.create(current_user, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/me", response_model=StoreResponse)
async def get_my_store(
    db: DBSession,
    current_user: CurrentUser,
) -> Store:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    return _ensure_store_owner(store, current_user)


@router.patch("/me", response_model=StoreResponse)
async def update_my_store(
    data: StoreUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> Store:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await service.update(store, data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_store(
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    await service.delete(store)


@router.get("/{slug}", response_model=StoreResponse)
async def get_store_by_slug(
    slug: str,
    db: DBSession,
) -> Store:
    service = StoreService(db)
    store = await service.get_by_slug(slug)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store


@router.get("/{slug}/public", response_model=PublicStoreResponse)
async def get_public_store(
    slug: str,
    db: DBSession,
) -> PublicStoreResponse:
    """Return a store with its products and bank accounts for public sharing."""
    store_service = StoreService(db)
    store = await store_service.get_by_slug(slug)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    product_service = ProductService(db)
    bank_service = BankAccountService(db)

    products = await product_service.get_active_by_store(store.id)
    bank_accounts = await bank_service.list_by_store(store.id)

    return PublicStoreResponse(
        **StoreResponse.model_validate(store).model_dump(),
        products=products,
        bank_accounts=bank_accounts,
    )


@router.post("/me/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Product:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    product = await ProductService(db).create(store, data)
    await index_product(product)
    return product


@router.get("/me/products", response_model=list[ProductResponse])
async def list_my_products(
    db: DBSession,
    current_user: CurrentUser,
) -> list[Product]:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await ProductService(db).list_by_store(store.id)


@router.patch("/me/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> Product:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    if product is None or product.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    updated = await product_service.update(product, data)
    await index_product(updated)
    return updated


@router.delete("/me/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    product_service = ProductService(db)
    product = await product_service.get_by_id(product_id)
    if product is None or product.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await product_service.delete(product)


@router.post(
    "/me/bank-accounts", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED
)
async def create_bank_account(
    data: BankAccountCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> BankAccount:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await BankAccountService(db).create(store, data)


@router.get("/me/bank-accounts", response_model=list[BankAccountResponse])
async def list_my_bank_accounts(
    db: DBSession,
    current_user: CurrentUser,
) -> list[BankAccount]:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await BankAccountService(db).list_by_store(store.id)


@router.patch("/me/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: UUID,
    data: BankAccountUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> BankAccount:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    bank_service = BankAccountService(db)
    account = await bank_service.get_by_id(account_id)
    if account is None or account.store_id != store.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found"
        )
    return await bank_service.update(account, data)


@router.delete("/me/bank-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_account(
    account_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    bank_service = BankAccountService(db)
    account = await bank_service.get_by_id(account_id)
    if account is None or account.store_id != store.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found"
        )
    await bank_service.delete(account)


@router.post(
    "/me/knowledge", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED
)
async def create_knowledge(
    data: KnowledgeBaseCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> KnowledgeBase:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    entry = await KnowledgeBaseService(db).create(store, data)
    await index_knowledge(entry)
    return entry


@router.get("/me/knowledge", response_model=list[KnowledgeBaseResponse])
async def list_my_knowledge(
    db: DBSession,
    current_user: CurrentUser,
) -> list[KnowledgeBase]:
    service = StoreService(db)
    store = await service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)
    return await KnowledgeBaseService(db).list_by_store(store.id)


@router.get("/me/dashboard", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    db: DBSession,
    current_user: CurrentUser,
) -> DashboardSummaryResponse:
    store_service = StoreService(db)
    store = await store_service.get_by_owner(current_user.id)
    store = _ensure_store_owner(store, current_user)

    order_service = OrderService(db)
    product_service = ProductService(db)

    total_revenue = await order_service.get_revenue(store.id)
    order_count = len(await order_service.list_by_store(store.id))
    pending_orders = await order_service.get_pending_count(store.id)
    products = await product_service.list_by_store(store.id)
    bestseller = await order_service.get_bestseller(store.id)

    return DashboardSummaryResponse(
        store_id=store.id,
        store_name=store.name,
        total_revenue=total_revenue,
        order_count=order_count,
        pending_orders=pending_orders,
        product_count=len(products),
        bestseller=bestseller,
    )
