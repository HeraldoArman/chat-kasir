"""LangChain tool callables for the commerce agent.

Each tool opens its own DB session, wraps service calls in try/except, and
returns a structured dict with ``success``, ``message``, and optional ``data``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

import structlog
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.db.session import async_session_factory

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class SearchProductsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    keywords: list[str] = Field(
        default_factory=list, description="Keywords to search product names"
    )


class CreateOrderInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    items: list[dict[str, Any]] = Field(
        description="List of order items with product_id, name, quantity, unit_price, total_price"
    )
    note: str | None = Field(default=None, description="Optional order note")


class GetPaymentInfoInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    order_total: int | None = Field(
        default=None, description="Optional order total for context"
    )


class AnswerFAQInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    query: str = Field(description="FAQ query from customer")


class GetMerchantAnalyticsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")


class GetCustomerMemoryInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _format_rupiah(amount: int | float | Decimal) -> str:
    """Format integer as Indonesian Rupiah string."""
    return f"Rp {int(amount):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool(args_schema=SearchProductsInput)
async def search_products(store_id: str, keywords: list[str]) -> dict[str, Any]:
    """Search active products in a store by keywords. Returns matching products."""
    try:
        from app.services.product import ProductService

        async with async_session_factory() as db:
            svc = ProductService(db)
            products = await svc.get_active_by_store(UUID(store_id))

        if not products:
            return {"success": False, "message": "Saat ini tidak ada produk aktif di toko ini.", "edge_case": "no_active_products", "data": []}

        if keywords:
            kw_lower = [k.lower() for k in keywords]
            filtered = [
                p
                for p in products
                if any(kw in p.name.lower() or (p.description and kw in p.description.lower()) for kw in kw_lower)
            ]
        else:
            filtered = list(products)

        if not filtered:
            return {"success": True, "message": "Tidak ditemukan produk yang cocok.", "data": []}

        items = []
        for p in filtered:
            item: dict[str, Any] = {
                "product_id": str(p.id),
                "name": p.name,
                "price": int(p.price),
                "price_display": _format_rupiah(p.price),
                "stock": p.stock,
                "description": p.description,
                "image_url": p.image_url,
            }
            if p.stock is not None and p.stock <= 0:
                item["stock_status"] = "out_of_stock"
            elif p.stock is not None and p.stock <= 5:
                item["stock_status"] = "low_stock"
            else:
                item["stock_status"] = "available"
            items.append(item)

        return {"success": True, "message": f"Ditemukan {len(items)} produk.", "data": items}
    except Exception as e:
        log.error("tool_search_products_error", error=str(e))
        return {"success": False, "message": f"Gagal mencari produk: {e}"}


@tool(args_schema=CreateOrderInput)
async def create_order(
    store_id: str,
    customer_phone: str,
    items: list[dict[str, Any]],
    note: str | None = None,
) -> dict[str, Any]:
    """Create a new order for a customer. Resolves product names to catalog items."""
    try:
        from app.models.commerce import Store
        from app.schemas.commerce import OrderCreate, OrderItem
        from app.services.order import OrderService
        from app.services.product import ProductService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            product_svc = ProductService(db)
            products = await product_svc.get_active_by_store(UUID(store_id))
            products_by_name = {p.name.lower(): p for p in products}

            order_items: list[OrderItem] = []
            for raw in items:
                name = str(raw.get("name", "")).strip()
                requested_qty = int(raw.get("quantity", 1))
                if requested_qty <= 0:
                    requested_qty = 1

                product = products_by_name.get(name.lower())
                if product is None:
                    return {
                        "success": False,
                        "message": f"Produk '{name}' tidak ditemukan di katalog aktif.",
                    }

                if product.stock is not None and product.stock < requested_qty:
                    return {
                        "success": False,
                        "message": f"Stok {product.name} hanya tersisa {product.stock}.",
                        "edge_case": "out_of_stock",
                    }

                unit_price = int(product.price)
                total_price = unit_price * requested_qty
                order_items.append(
                    OrderItem(
                        product_id=str(product.id),
                        name=product.name,
                        quantity=requested_qty,
                        unit_price=unit_price,
                        total_price=total_price,
                    )
                )

            if not order_items:
                return {"success": False, "message": "Tidak ada item yang bisa dipesan."}

            order_create = OrderCreate(
                customer_phone=customer_phone,
                items=order_items,
                note=note,
            )
            order_svc = OrderService(db)
            order = await order_svc.create(store, order_create)

            return {
                "success": True,
                "message": "Pesanan berhasil dibuat.",
                "data": {
                    "order_id": str(order.id),
                    "customer_phone": order.customer_phone,
                    "total": int(order.total),
                    "total_display": _format_rupiah(order.total),
                    "status": order.status,
                    "items": order.items,
                },
            }
    except ValueError as e:
        log.warning("tool_create_order_validation", error=str(e))
        msg = str(e)
        edge = "out_of_stock" if "stock" in msg.lower() else None
        return {"success": False, "message": f"Gagal membuat pesanan: {msg}", "edge_case": edge}
    except Exception as e:
        log.error("tool_create_order_error", error=str(e))
        return {"success": False, "message": f"Gagal membuat pesanan: {e}"}


@tool(args_schema=GetPaymentInfoInput)
async def get_payment_info(
    store_id: str,
    order_total: int | None = None,
) -> dict[str, Any]:
    """Get bank account information for a store to share payment details."""
    try:
        from app.services.bank import BankAccountService

        async with async_session_factory() as db:
            svc = BankAccountService(db)
            primary = await svc.get_primary(UUID(store_id))

        if primary is None:
            accounts = []
            async with async_session_factory() as db:
                svc = BankAccountService(db)
                accounts = await svc.list_by_store(UUID(store_id))

            if not accounts:
                return {
                    "success": False,
                    "message": "Belum ada rekening bank terdaftar di toko ini.",
                    "edge_case": "missing_bank_account",
                }
            account = accounts[0]
        else:
            account = primary

        result: dict[str, Any] = {
            "bank_name": account.bank_name,
            "account_number": account.account_number,
            "account_holder": account.account_holder_name,
        }
        if order_total is not None:
            result["total_to_pay"] = order_total
            result["total_display"] = _format_rupiah(order_total)

        return {"success": True, "message": "Informasi pembayaran ditemukan.", "data": result}
    except Exception as e:
        log.error("tool_get_payment_info_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil info pembayaran: {e}"}


@tool(args_schema=AnswerFAQInput)
async def answer_faq(store_id: str, query: str) -> dict[str, Any]:
    """Answer a frequently asked question using the store's knowledge base."""
    try:
        from app.services.knowledge import KnowledgeBaseService

        async with async_session_factory() as db:
            svc = KnowledgeBaseService(db)
            entries = await svc.list_by_store(UUID(store_id))

        if not entries:
            return {"success": False, "message": "Belum ada FAQ yang tersedia di toko ini.", "data": []}

        query_lower = query.lower()
        matches: list[dict[str, Any]] = []
        for entry in entries:
            question_text = entry.question or ""
            if question_text and query_lower in question_text.lower():
                matches.append({"question": question_text, "answer": entry.answer, "category": entry.category})
            elif query_lower in entry.answer.lower():
                matches.append({"question": question_text, "answer": entry.answer, "category": entry.category})

        if not matches:
            return {"success": True, "message": "Tidak ditemukan jawaban yang cocok untuk pertanyaan Anda.", "data": []}

        return {"success": True, "message": f"Ditemukan {len(matches)} jawaban.", "data": matches}
    except Exception as e:
        log.error("tool_answer_faq_error", error=str(e))
        return {"success": False, "message": f"Gagal menjawab FAQ: {e}"}


@tool(args_schema=GetMerchantAnalyticsInput)
async def get_merchant_analytics(store_id: str) -> dict[str, Any]:
    """Get analytics summary for a store (orders, revenue, bestseller)."""
    try:
        from sqlalchemy import func, select

        from app.models.commerce import Order, Product
        from app.services.order import OrderService

        async with async_session_factory() as db:
            order_svc = OrderService(db)

            revenue = await order_svc.get_revenue(UUID(store_id))
            pending = await order_svc.get_pending_count(UUID(store_id))
            bestseller = await order_svc.get_bestseller(UUID(store_id))

            total_orders_result = await db.execute(
                select(func.count(Order.id)).where(Order.store_id == UUID(store_id))
            )
            total_orders = total_orders_result.scalar() or 0

            total_products_result = await db.execute(
                select(func.count(Product.id)).where(
                    Product.store_id == UUID(store_id), Product.is_active.is_(True)
                )
            )
            total_products = total_products_result.scalar() or 0

        data: dict[str, Any] = {
            "total_revenue": revenue,
            "total_revenue_display": _format_rupiah(revenue),
            "total_orders": total_orders,
            "pending_orders": pending,
            "total_products": total_products,
            "bestseller": bestseller,
        }

        return {"success": True, "message": "Data analytics berhasil diambil.", "data": data}
    except Exception as e:
        log.error("tool_get_merchant_analytics_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil data analytics: {e}"}


@tool(args_schema=GetCustomerMemoryInput)
async def get_customer_memory(store_id: str, customer_phone: str) -> dict[str, Any]:
    """Retrieve customer order history and preferences from the store."""
    try:
        from sqlalchemy import select

        from app.models.commerce import Order, OrderStatus

        async with async_session_factory() as db:
            result = await db.execute(
                select(Order)
                .where(
                    Order.store_id == UUID(store_id),
                    Order.customer_phone == customer_phone,
                    Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
                )
                .order_by(Order.created_at.desc())
                .limit(5)
            )
            orders = list(result.scalars().all())

        if not orders:
            return {
                "success": True,
                "message": "Belum ada riwayat pesanan untuk nomor ini.",
                "data": {"customer_phone": customer_phone, "orders": []},
            }

        order_summaries = []
        for o in orders:
            order_summaries.append({
                "order_id": str(o.id),
                "total": int(o.total),
                "total_display": _format_rupiah(o.total),
                "status": o.status,
                "created_at": str(o.created_at),
                "items": o.items,
            })

        return {
            "success": True,
            "message": f"Ditemukan {len(order_summaries)} pesanan sebelumnya.",
            "data": {"customer_phone": customer_phone, "orders": order_summaries},
        }
    except Exception as e:
        log.error("tool_get_customer_memory_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil riwayat pelanggan: {e}"}


# Collect all tools for easy registration.
ALL_TOOLS = [
    search_products,
    create_order,
    get_payment_info,
    answer_faq,
    get_merchant_analytics,
    get_customer_memory,
]
