"""Product CRUD service."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import Product, Store
from app.schemas.commerce import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, store: Store, data: ProductCreate) -> Product:
        product = Product(
            store_id=store.id,
            name=data.name,
            description=data.description,
            price=data.price,
            stock=data.stock,
            weight=data.weight,
            image_url=data.image_url,
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def search_by_keywords(
        self, store_id: UUID, keywords: list[str], limit: int = 10
    ) -> list[Product]:
        """Return active products whose name or description matches any keyword."""
        query = select(Product).where(
            Product.store_id == store_id, Product.is_active.is_(True)
        )
        if keywords:
            filters = []
            for kw in keywords:
                like = f"%{kw}%"
                filters.append(Product.name.ilike(like))
                filters.append(Product.description.ilike(like))
            query = query.where(or_(*filters))

        result = await self.db.execute(query.order_by(Product.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, product_id: UUID) -> Product | None:
        return await self.db.get(Product, product_id)

    async def list_by_store(self, store_id: UUID) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.store_id == store_id)
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, product: Product, data: ProductUpdate) -> Product:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()

    async def get_active_by_store(self, store_id: UUID) -> list[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.store_id == store_id, Product.is_active.is_(True))
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())

    def build_search_text(self, product: Product) -> str:
        """Build a single searchable text from a product."""
        parts = [product.name]
        if product.description:
            parts.append(product.description)
        parts.append(f"Harga: Rp {int(product.price):,}".replace(",", "."))
        if product.stock is not None:
            parts.append(f"Stok: {product.stock}")
        return " | ".join(parts)
