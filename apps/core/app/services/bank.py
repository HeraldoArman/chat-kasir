"""Bank account CRUD service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import BankAccount, Store
from app.schemas.commerce import BankAccountCreate, BankAccountUpdate


class BankAccountService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, store: Store, data: BankAccountCreate) -> BankAccount:
        account = BankAccount(
            store_id=store.id,
            bank_name=data.bank_name,
            account_number=data.account_number,
            account_holder_name=data.account_holder_name,
            is_primary=data.is_primary,
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def get_by_id(self, account_id: UUID) -> BankAccount | None:
        return await self.db.get(BankAccount, account_id)

    async def list_by_store(self, store_id: UUID) -> list[BankAccount]:
        result = await self.db.execute(
            select(BankAccount)
            .where(BankAccount.store_id == store_id)
            .order_by(BankAccount.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_primary(self, store_id: UUID) -> BankAccount | None:
        result = await self.db.execute(
            select(BankAccount).where(
                BankAccount.store_id == store_id, BankAccount.is_primary.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, account: BankAccount, data: BankAccountUpdate) -> BankAccount:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(account, field, value)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def delete(self, account: BankAccount) -> None:
        await self.db.delete(account)
        await self.db.commit()
