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


class ConfirmPaymentInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")


class VerifyPaymentInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    merchant_phone: str = Field(description="Merchant WhatsApp phone number")
    order_id: str = Field(description="UUID of the order to verify")


class GetOrderStatusInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")


class AddToCartInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    product_id: str = Field(description="UUID of the product to add")
    quantity: int = Field(default=1, description="Quantity to add (default 1)")


class GetCartInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")


class UpdateCartItemInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    cart_item_id: str = Field(description="UUID of the cart item to update")
    quantity: int = Field(description="New quantity (set to 0 to remove)")


class RemoveFromCartInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    cart_item_id: str = Field(description="UUID of the cart item to remove")


class CheckoutCartInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    customer_name: str | None = Field(default=None, description="Optional customer name")
    note: str | None = Field(default=None, description="Optional order note")


class RecommendProductsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str | None = Field(default=None, description="Optional customer phone for personalized recs")
    keywords: list[str] = Field(default_factory=list, description="Keywords to refine recommendations")
    limit: int = Field(default=5, description="Maximum products to return")


class UpsellProductInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    product_id: str = Field(description="UUID of the product to find upsells for")
    customer_phone: str | None = Field(default=None, description="Optional customer phone for personalization")


class CrossSellProductInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    product_id: str = Field(description="UUID of the product to find cross-sells for")
    customer_phone: str | None = Field(default=None, description="Optional customer phone for personalization")


class GetActivePromotionsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")


class SendPaymentReminderInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    hours: int = Field(default=24, description="Hours since order creation to consider abandoned")


class SubmitComplaintInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    category: str = Field(description="Complaint category (e.g. 'produk rusak', 'pengiriman lambat')")
    description: str = Field(description="Detailed complaint description")
    order_id: str | None = Field(default=None, description="Optional UUID of related order")


class SubmitRefundRequestInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    order_id: str = Field(description="UUID of the order to request refund for")
    reason: str = Field(description="Reason for refund request")


class GetLowStockProductsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    threshold: int = Field(default=5, description="Stock threshold (products at or below this are low)")


class GetDailySummaryInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    date: str | None = Field(
        default=None, description="Date in ISO format (YYYY-MM-DD), defaults to today"
    )


class GetCustomerOrderHistoryInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    customer_phone: str = Field(description="Customer WhatsApp phone number")
    limit: int = Field(default=10, description="Maximum orders to return")


class SearchProductsSemanticInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    query: str = Field(description="Natural language search query")
    limit: int = Field(default=10, description="Maximum products to return")


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

            from app.agent.notifications import notify_merchant_new_order

            merchant_phone = store.owner.whatsapp_number or store.whatsapp_number
            if merchant_phone:
                await notify_merchant_new_order(order, merchant_phone)

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
    """Answer a frequently asked question using keyword match + optional Qdrant RAG."""
    try:
        from app.services.indexing import _get_rag_service
        from app.services.knowledge import KnowledgeBaseService

        async with async_session_factory() as db:
            svc = KnowledgeBaseService(db)
            entries = await svc.list_by_store(UUID(store_id))

        if not entries:
            return {"success": False, "message": "Belum ada FAQ yang tersedia di toko ini.", "data": []}

        # 1. Deterministic keyword fallback
        query_lower = query.lower()
        matches: list[dict[str, Any]] = []
        for entry in entries:
            question_text = entry.question or ""
            if question_text and query_lower in question_text.lower():
                matches.append({"question": question_text, "answer": entry.answer, "category": entry.category})
            elif query_lower in entry.answer.lower():
                matches.append({"question": question_text, "answer": entry.answer, "category": entry.category})

        # 2. Augment with semantic RAG when enabled
        rag = _get_rag_service()
        if rag is not None and not matches:
            try:
                rag_results = await rag.retrieve_with_filter(
                    query=query,
                    filters={"store_id": store_id, "doc_type": "faq"},
                    top_k=3,
                )
                for result in rag_results:
                    metadata_raw = result.get("metadata", {})
                    payload: dict[str, object] = metadata_raw if isinstance(metadata_raw, dict) else {}
                    text_value = str(result.get("text", ""))
                    question = payload.get("question", "")
                    category = payload.get("category", "FAQ")
                    matches.append({
                        "question": str(question) if question is not None else "",
                        "answer": text_value.split(" | ")[-1] if " | " in text_value else text_value,
                        "category": str(category) if category is not None else "FAQ",
                    })
            except Exception:
                pass

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


@tool(args_schema=ConfirmPaymentInput)
async def confirm_payment_notify_merchant(
    store_id: str,
    customer_phone: str,
) -> dict[str, Any]:
    """Record a customer payment confirmation and notify the merchant to verify."""
    try:
        from app.agent.notifications import notify_merchant_payment_confirmation
        from app.models.commerce import Store
        from app.services.order import OrderService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            order_svc = OrderService(db)
            order = await order_svc.get_latest_pending_by_customer(
                UUID(store_id), customer_phone
            )
            merchant_phone = store.owner.whatsapp_number or store.whatsapp_number

        if order is None:
            return {
                "success": False,
                "message": "Anda belum memiliki pesanan yang menunggu pembayaran.",
                "edge_case": "no_pending_order",
            }

        if merchant_phone:
            await notify_merchant_payment_confirmation(order, merchant_phone)
        return {
            "success": True,
            "message": "Terima kasih, kami akan mengonfirmasi pembayaran Anda.",
            "data": {"order_id": str(order.id), "total": int(order.total)},
        }
    except Exception as e:
        log.error("tool_confirm_payment_error", error=str(e))
        return {"success": False, "message": f"Gagal mengonfirmasi pembayaran: {e}"}


@tool(args_schema=VerifyPaymentInput)
async def verify_order_payment(
    store_id: str,
    merchant_phone: str,
    order_id: str,
) -> dict[str, Any]:
    """Merchant-only tool: verify a pending order payment and notify the customer."""
    try:
        from app.agent.notifications import notify_customer_payment_confirmed
        from app.models.commerce import Order, Store
        from app.services.gowa_webhook import _extract_phone
        from app.services.order import OrderService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            owner_phone = store.owner.whatsapp_number
            if not owner_phone:
                return {
                    "success": False,
                    "message": "Pemilik toko belum memiliki nomor WhatsApp terdaftar.",
                }

            if _extract_phone(merchant_phone) != _extract_phone(owner_phone):
                return {
                    "success": False,
                    "message": "Maaf, fitur ini hanya tersedia untuk pemilik toko.",
                    "edge_case": "unauthorized_merchant",
                }

            order = await db.get(Order, UUID(order_id))
            if order is None or str(order.store_id) != store_id:
                return {
                    "success": False,
                    "message": "Pesanan tidak ditemukan.",
                    "edge_case": "order_not_found",
                }

            order_svc = OrderService(db)
            if order.status != "pending_payment":
                return {
                    "success": False,
                    "message": "Pesanan sudah diverifikasi sebelumnya atau tidak dapat diverifikasi.",
                    "edge_case": "already_verified",
                }

            await order_svc.verify_payment(order)
            await notify_customer_payment_confirmed(order, order.customer_phone)

            return {
                "success": True,
                "message": f"Pembayaran order {order.id} telah dikonfirmasi.",
                "data": {"order_id": str(order.id), "status": order.status},
            }
    except Exception as e:
        log.error("tool_verify_payment_error", error=str(e))
        return {"success": False, "message": f"Gagal memverifikasi pembayaran: {e}"}


@tool(args_schema=GetOrderStatusInput)
async def get_order_status(
    store_id: str,
    customer_phone: str,
) -> dict[str, Any]:
    """Return the latest order status for a customer in a store."""
    try:
        from app.models.commerce import Store
        from app.services.order import OrderService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            order_svc = OrderService(db)
            order = await order_svc.get_latest_by_customer(UUID(store_id), customer_phone)

        if order is None:
            return {"success": True, "message": "Anda belum memiliki pesanan."}

        return {
            "success": True,
            "message": "Status pesanan berhasil diambil.",
            "data": {
                "order_id": str(order.id),
                "status": order.status,
                "total": int(order.total),
                "total_display": _format_rupiah(order.total),
                "items": order.items,
                "created_at": str(order.created_at),
            },
        }
    except Exception as e:
        log.error("tool_get_order_status_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil status pesanan: {e}"}


# ---------------------------------------------------------------------------
# Cart tools
# ---------------------------------------------------------------------------


@tool(args_schema=AddToCartInput)
async def add_to_cart(
    store_id: str,
    customer_phone: str,
    product_id: str,
    quantity: int = 1,
) -> dict[str, Any]:
    """Add a product to the customer's cart. Creates cart if needed."""
    try:
        from app.services.cart import CartService

        async with async_session_factory() as db:
            svc = CartService(db)
            cart = await svc.add_item(UUID(store_id), customer_phone, UUID(product_id), quantity)
            resp = svc.to_response(cart)

        items = [
            {
                "cart_item_id": str(it.id),
                "product_id": str(it.product_id),
                "name": it.name,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "unit_price_display": _format_rupiah(it.unit_price),
                "total_price": it.total_price,
                "total_price_display": _format_rupiah(it.total_price),
            }
            for it in resp.items
        ]
        return {
            "success": True,
            "message": f"Produk ditambahkan ke keranjang. Total: {_format_rupiah(resp.total)}.",
            "data": {"cart_id": str(resp.id), "items": items, "total": resp.total, "total_display": _format_rupiah(resp.total)},
        }
    except ValueError as e:
        log.warning("tool_add_to_cart_validation", error=str(e))
        return {"success": False, "message": f"Gagal menambahkan produk: {e}", "edge_case": "validation_error"}
    except Exception as e:
        log.error("tool_add_to_cart_error", error=str(e))
        return {"success": False, "message": f"Gagal menambahkan produk ke keranjang: {e}"}


@tool(args_schema=GetCartInput)
async def get_cart(store_id: str, customer_phone: str) -> dict[str, Any]:
    """Get the customer's current cart contents."""
    try:
        from app.services.cart import CartService

        async with async_session_factory() as db:
            svc = CartService(db)
            resp = await svc.get_cart(UUID(store_id), customer_phone)

        if not resp.items:
            return {"success": True, "message": "Keranjang Anda kosong.", "data": {"items": [], "total": 0}}

        items = [
            {
                "cart_item_id": str(it.id),
                "product_id": str(it.product_id),
                "name": it.name,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "unit_price_display": _format_rupiah(it.unit_price),
                "total_price": it.total_price,
                "total_price_display": _format_rupiah(it.total_price),
            }
            for it in resp.items
        ]
        return {
            "success": True,
            "message": f"Keranjang Anda berisi {len(resp.items)} item. Total: {_format_rupiah(resp.total)}.",
            "data": {"cart_id": str(resp.id), "items": items, "total": resp.total, "total_display": _format_rupiah(resp.total)},
        }
    except Exception as e:
        log.error("tool_get_cart_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil keranjang: {e}"}


@tool(args_schema=UpdateCartItemInput)
async def update_cart_item(
    store_id: str,
    customer_phone: str,
    cart_item_id: str,
    quantity: int,
) -> dict[str, Any]:
    """Update the quantity of a cart item. Set quantity to 0 to remove it."""
    try:
        from app.services.cart import CartService

        async with async_session_factory() as db:
            svc = CartService(db)
            cart = await svc.update_item(UUID(store_id), customer_phone, UUID(cart_item_id), quantity)
            resp = svc.to_response(cart)

        items = [
            {
                "cart_item_id": str(it.id),
                "product_id": str(it.product_id),
                "name": it.name,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "unit_price_display": _format_rupiah(it.unit_price),
                "total_price": it.total_price,
                "total_price_display": _format_rupiah(it.total_price),
            }
            for it in resp.items
        ]
        return {
            "success": True,
            "message": "Keranjang diperbarui." if quantity > 0 else "Item dihapus dari keranjang.",
            "data": {"cart_id": str(resp.id), "items": items, "total": resp.total, "total_display": _format_rupiah(resp.total)},
        }
    except ValueError as e:
        log.warning("tool_update_cart_item_validation", error=str(e))
        return {"success": False, "message": f"Gagal memperbarui keranjang: {e}", "edge_case": "item_not_found"}
    except Exception as e:
        log.error("tool_update_cart_item_error", error=str(e))
        return {"success": False, "message": f"Gagal memperbarui keranjang: {e}"}


@tool(args_schema=RemoveFromCartInput)
async def remove_from_cart(
    store_id: str,
    customer_phone: str,
    cart_item_id: str,
) -> dict[str, Any]:
    """Remove an item from the customer's cart."""
    try:
        from app.services.cart import CartService

        async with async_session_factory() as db:
            svc = CartService(db)
            cart = await svc.remove_item(UUID(store_id), customer_phone, UUID(cart_item_id))
            resp = svc.to_response(cart)

        items = [
            {
                "cart_item_id": str(it.id),
                "product_id": str(it.product_id),
                "name": it.name,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "unit_price_display": _format_rupiah(it.unit_price),
                "total_price": it.total_price,
                "total_price_display": _format_rupiah(it.total_price),
            }
            for it in resp.items
        ]
        return {
            "success": True,
            "message": "Item dihapus dari keranjang.",
            "data": {"cart_id": str(resp.id), "items": items, "total": resp.total, "total_display": _format_rupiah(resp.total)},
        }
    except ValueError as e:
        log.warning("tool_remove_from_cart_validation", error=str(e))
        return {"success": False, "message": f"Gagal menghapus item: {e}", "edge_case": "item_not_found"}
    except Exception as e:
        log.error("tool_remove_from_cart_error", error=str(e))
        return {"success": False, "message": f"Gagal menghapus item dari keranjang: {e}"}


@tool(args_schema=CheckoutCartInput)
async def checkout_cart(
    store_id: str,
    customer_phone: str,
    customer_name: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Convert the customer's cart into an order and notify the merchant."""
    try:
        from app.agent.notifications import notify_merchant_new_order
        from app.models.commerce import Store
        from app.services.cart import CartService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            svc = CartService(db)
            order = await svc.checkout(UUID(store_id), customer_phone, customer_name, note)
            merchant_phone = store.owner.whatsapp_number or store.whatsapp_number

        if merchant_phone:
            await notify_merchant_new_order(order, merchant_phone)
        return {
            "success": True,
            "message": "Pesanan berhasil dibuat dari keranjang.",
            "data": {
                "order_id": str(order.id),
                "total": int(order.total),
                "total_display": _format_rupiah(order.total),
                "status": order.status,
                "items": order.items,
            },
        }
    except ValueError as e:
        log.warning("tool_checkout_cart_validation", error=str(e))
        msg = str(e)
        edge = "empty_cart" if "empty" in msg.lower() else "validation_error"
        return {"success": False, "message": f"Gagal checkout: {msg}", "edge_case": edge}
    except Exception as e:
        log.error("tool_checkout_cart_error", error=str(e))
        return {"success": False, "message": f"Gagal checkout keranjang: {e}"}


# ---------------------------------------------------------------------------
# Recommendation / upsell / cross-sell tools
# ---------------------------------------------------------------------------


@tool(args_schema=RecommendProductsInput)
async def recommend_products(
    store_id: str,
    customer_phone: str | None = None,
    keywords: list[str] | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Recommend products based on customer history, keywords, or popularity."""
    try:
        from app.services.indexing import _get_rag_service
        from app.services.recommendation import RecommendationService

        if keywords is None:
            keywords = []

        async with async_session_factory() as db:
            svc = RecommendationService(db)
            rag = _get_rag_service()
            products, reason = await svc.recommend(
                store_id=UUID(store_id),
                customer_phone=customer_phone,
                keywords=keywords,
                limit=limit,
                rag_service=rag,
            )

        if not products:
            return {"success": True, "message": "Tidak ada rekomendasi produk saat ini.", "data": []}

        items = [
            {
                "product_id": str(p.id),
                "name": p.name,
                "price": int(p.price),
                "price_display": _format_rupiah(p.price),
                "description": p.description,
                "stock": p.stock,
            }
            for p in products
        ]
        return {"success": True, "message": f"{reason}. Ditemukan {len(items)} rekomendasi.", "data": items}
    except Exception as e:
        log.error("tool_recommend_products_error", error=str(e))
        return {"success": False, "message": f"Gagal merekomendasikan produk: {e}"}


@tool(args_schema=UpsellProductInput)
async def upsell_product(
    store_id: str,
    product_id: str,
    customer_phone: str | None = None,
) -> dict[str, Any]:
    """Suggest a higher-value alternative or premium add-on for the given product."""
    try:
        from app.models.commerce import Product
        from app.services.recommendation import RecommendationService

        async with async_session_factory() as db:
            source = await db.get(Product, UUID(product_id))
            if source is None or str(source.store_id) != store_id:
                return {"success": False, "message": "Produk tidak ditemukan di toko ini."}

            svc = RecommendationService(db)
            keywords = source.name.lower().split() if source.name else []
            products, reason = await svc.recommend(
                store_id=UUID(store_id),
                customer_phone=customer_phone,
                keywords=keywords,
                limit=3,
            )

        # Filter to products priced higher than the source (upsell logic)
        upsells = [p for p in products if p.price > source.price]
        if not upsells:
            return {
                "success": True,
                "message": f"Tidak ada alternatif yang lebih premium untuk {source.name}.",
                "data": {"source_product": source.name, "upsells": []},
            }

        items = [
            {
                "product_id": str(p.id),
                "name": p.name,
                "price": int(p.price),
                "price_display": _format_rupiah(p.price),
                "description": p.description,
                "stock": p.stock,
            }
            for p in upsells
        ]
        return {
            "success": True,
            "message": f"{reason}. {len(items)} alternatif premium untuk {source.name}.",
            "data": {
                "source_product": source.name,
                "source_price": int(source.price),
                "source_price_display": _format_rupiah(source.price),
                "upsells": items,
            },
        }
    except Exception as e:
        log.error("tool_upsell_product_error", error=str(e))
        return {"success": False, "message": f"Gagal mencari upsell: {e}"}


@tool(args_schema=CrossSellProductInput)
async def cross_sell_product(
    store_id: str,
    product_id: str,
    customer_phone: str | None = None,
) -> dict[str, Any]:
    """Suggest complementary products that pair well with the given product."""
    try:
        from app.models.commerce import Product
        from app.services.recommendation import RecommendationService

        async with async_session_factory() as db:
            source = await db.get(Product, UUID(product_id))
            if source is None or str(source.store_id) != store_id:
                return {"success": False, "message": "Produk tidak ditemukan di toko ini."}

            svc = RecommendationService(db)
            keywords = (source.name or "").lower().split()
            if source.description:
                keywords.extend(source.description.lower().split()[:5])
            products, reason = await svc.recommend(
                store_id=UUID(store_id),
                customer_phone=customer_phone,
                keywords=keywords,
                limit=5,
            )

        # Exclude the source product itself from cross-sell suggestions
        cross_sells = [p for p in products if str(p.id) != product_id]
        if not cross_sells:
            return {
                "success": True,
                "message": f"Tidak ada produk pelengkap untuk {source.name}.",
                "data": {"source_product": source.name, "cross_sells": []},
            }

        items = [
            {
                "product_id": str(p.id),
                "name": p.name,
                "price": int(p.price),
                "price_display": _format_rupiah(p.price),
                "description": p.description,
                "stock": p.stock,
            }
            for p in cross_sells
        ]
        return {
            "success": True,
            "message": f"{reason}. {len(items)} produk pelengkap untuk {source.name}.",
            "data": {"source_product": source.name, "cross_sells": items},
        }
    except Exception as e:
        log.error("tool_cross_sell_product_error", error=str(e))
        return {"success": False, "message": f"Gagal mencari cross-sell: {e}"}


# ---------------------------------------------------------------------------
# Promotion / recovery / complaint / refund tools
# ---------------------------------------------------------------------------


@tool(args_schema=GetActivePromotionsInput)
async def get_active_promotions(store_id: str) -> dict[str, Any]:
    """Return all currently active promotions for a store."""
    try:
        from app.services.promotion import PromotionService

        async with async_session_factory() as db:
            svc = PromotionService(db)
            promotions = await svc.list_active(UUID(store_id))

        if not promotions:
            return {"success": True, "message": "Saat ini tidak ada promosi aktif.", "data": []}

        items = [
            {
                "promotion_id": str(p.id),
                "name": p.name,
                "description": p.description,
                "discount_type": p.discount_type,
                "discount_value": p.discount_value,
                "min_quantity": p.min_quantity,
                "start_at": str(p.start_at) if p.start_at else None,
                "end_at": str(p.end_at) if p.end_at else None,
            }
            for p in promotions
        ]
        return {"success": True, "message": f"Ditemukan {len(items)} promosi aktif.", "data": items}
    except Exception as e:
        log.error("tool_get_active_promotions_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil promosi: {e}"}


@tool(args_schema=SendPaymentReminderInput)
async def send_payment_reminder(store_id: str, hours: int = 24) -> dict[str, Any]:
    """Send payment reminders to customers with abandoned orders older than the given hours."""
    try:
        from app.agent.notifications import notify_customer_recovery
        from app.models.commerce import Store
        from app.services.order import OrderService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            order_svc = OrderService(db)
            abandoned = await order_svc.get_abandoned_payments(UUID(store_id), hours=hours)

        if not abandoned:
            return {"success": True, "message": "Tidak ada pesanan yang menunggu pembayaran.", "data": {"reminded": 0}}

        reminded = 0
        for order in abandoned:
            try:
                await notify_customer_recovery(order, order.customer_phone)
                reminded += 1
            except Exception:
                log.warning("send_payment_reminder_single_failed", order_id=str(order.id))

        return {
            "success": True,
            "message": f"Pengingat pembayaran dikirim ke {reminded} pelanggan.",
            "data": {"reminded": reminded, "total_abandoned": len(abandoned)},
        }
    except Exception as e:
        log.error("tool_send_payment_reminder_error", error=str(e))
        return {"success": False, "message": f"Gagal mengirim pengingat pembayaran: {e}"}


@tool(args_schema=SubmitComplaintInput)
async def submit_complaint(
    store_id: str,
    customer_phone: str,
    category: str,
    description: str,
    order_id: str | None = None,
) -> dict[str, Any]:
    """Submit a customer complaint and notify the merchant."""
    try:
        from app.services.complaint import ComplaintService

        async with async_session_factory() as db:
            svc = ComplaintService(db)
            complaint = await svc.create(
                store_id=UUID(store_id),
                customer_phone=customer_phone,
                category=category,
                description=description,
                order_id=UUID(order_id) if order_id else None,
            )

        return {
            "success": True,
            "message": "Komplain berhasil dikirim. Tim kami akan segera menindaklanjuti.",
            "data": {
                "complaint_id": str(complaint.id),
                "category": complaint.category,
                "status": complaint.status,
            },
        }
    except ValueError as e:
        log.warning("tool_submit_complaint_validation", error=str(e))
        return {"success": False, "message": f"Gagal mengirim komplain: {e}"}
    except Exception as e:
        log.error("tool_submit_complaint_error", error=str(e))
        return {"success": False, "message": f"Gagal mengirim komplain: {e}"}


@tool(args_schema=SubmitRefundRequestInput)
async def submit_refund_request(
    store_id: str,
    customer_phone: str,
    order_id: str,
    reason: str,
) -> dict[str, Any]:
    """Submit a refund request and notify the merchant."""
    try:
        from app.services.refund import RefundService

        async with async_session_factory() as db:
            svc = RefundService(db)
            refund = await svc.create(
                store_id=UUID(store_id),
                customer_phone=customer_phone,
                order_id=UUID(order_id),
                reason=reason,
            )

        return {
            "success": True,
            "message": "Permintaan refund berhasil dikirim. Tim kami akan segera meninjau.",
            "data": {
                "refund_id": str(refund.id),
                "order_id": str(refund.order_id),
                "status": refund.status,
            },
        }
    except ValueError as e:
        log.warning("tool_submit_refund_request_validation", error=str(e))
        return {"success": False, "message": f"Gagal mengirim permintaan refund: {e}"}
    except Exception as e:
        log.error("tool_submit_refund_request_error", error=str(e))
        return {"success": False, "message": f"Gagal mengirim permintaan refund: {e}"}


# ---------------------------------------------------------------------------
# Insight / history / search tools
# ---------------------------------------------------------------------------


@tool(args_schema=GetLowStockProductsInput)
async def get_low_stock_products(store_id: str, threshold: int = 5) -> dict[str, Any]:
    """Return products with stock at or below the given threshold. Notifies merchant of low stock items."""
    try:
        from app.agent.notifications import notify_merchant_low_stock
        from app.models.commerce import Store
        from app.services.order import OrderService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            order_svc = OrderService(db)
            products = await order_svc.get_inventory_insight(UUID(store_id), threshold=threshold)
            merchant_phone = store.owner.whatsapp_number or store.whatsapp_number

        if not products:
            return {"success": True, "message": "Semua produk masih memiliki stok yang cukup.", "data": []}

        items = [
            {
                "product_id": str(p.id),
                "name": p.name,
                "stock": p.stock,
                "price": int(p.price),
                "price_display": _format_rupiah(p.price),
            }
            for p in products
        ]

        # Notify merchant about low-stock products
        if merchant_phone:
            for product in products:
                try:
                    await notify_merchant_low_stock(product, merchant_phone)
                except Exception:
                    log.warning("low_stock_notify_failed", product_id=str(product.id))

        return {
            "success": True,
            "message": f"Ditemukan {len(items)} produk dengan stok rendah (≤{threshold}).",
            "data": items,
        }
    except Exception as e:
        log.error("tool_get_low_stock_products_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil data stok rendah: {e}"}


@tool(args_schema=GetDailySummaryInput)
async def get_daily_summary(store_id: str, date: str | None = None) -> dict[str, Any]:
    """Get a daily business summary for the store. Optionally specify a date (YYYY-MM-DD)."""
    try:
        from datetime import date as date_type

        from app.agent.notifications import notify_merchant_daily_summary
        from app.models.commerce import Store
        from app.services.order import OrderService

        target_date = date_type.fromisoformat(date) if date else date_type.today()

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            order_svc = OrderService(db)
            summary = await order_svc.get_daily_summary(UUID(store_id), target_date)
            merchant_phone = store.owner.whatsapp_number or store.whatsapp_number

        revenue_raw = summary.get("revenue", 0)
        revenue = int(revenue_raw) if isinstance(revenue_raw, int | float) else 0
        order_count_raw = summary.get("order_count", 0)
        order_count = int(order_count_raw) if isinstance(order_count_raw, int | float) else 0
        pending_raw = summary.get("pending_orders", 0)
        pending_orders = int(pending_raw) if isinstance(pending_raw, int | float) else 0
        data: dict[str, Any] = {
            "date": summary.get("date"),
            "revenue": revenue,
            "revenue_display": _format_rupiah(revenue),
            "order_count": order_count,
            "pending_orders": pending_orders,
            "bestseller": summary.get("bestseller"),
        }

        # Send merchant daily summary notification
        bestseller_name: str | None = None
        bestseller_raw = summary.get("bestseller")
        if bestseller_raw and isinstance(bestseller_raw, dict):
            name_val = bestseller_raw.get("name")
            bestseller_name = str(name_val) if name_val is not None else None
        if merchant_phone:
            try:
                await notify_merchant_daily_summary(
                    merchant_phone,
                    total_revenue=revenue,
                    order_count=order_count,
                    pending_orders=pending_orders,
                    bestseller=bestseller_name,
                )
            except Exception:
                log.warning("daily_summary_notify_failed", store_id=store_id)

        return {"success": True, "message": "Ringkasan harian berhasil diambil.", "data": data}
    except Exception as e:
        log.error("tool_get_daily_summary_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil ringkasan harian: {e}"}


@tool(args_schema=GetCustomerOrderHistoryInput)
async def get_customer_order_history(
    store_id: str,
    customer_phone: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Return a customer's order history for a given store."""
    try:
        from app.services.order import OrderService

        async with async_session_factory() as db:
            svc = OrderService(db)
            orders = await svc.get_customer_history(UUID(store_id), customer_phone, limit=limit)

        if not orders:
            return {
                "success": True,
                "message": "Belum ada riwayat pesanan untuk nomor ini.",
                "data": {"customer_phone": customer_phone, "orders": []},
            }

        order_summaries = [
            {
                "order_id": str(o.id),
                "total": int(o.total),
                "total_display": _format_rupiah(o.total),
                "status": o.status,
                "created_at": str(o.created_at),
                "items": o.items,
            }
            for o in orders
        ]
        return {
            "success": True,
            "message": f"Ditemukan {len(order_summaries)} pesanan.",
            "data": {"customer_phone": customer_phone, "orders": order_summaries},
        }
    except Exception as e:
        log.error("tool_get_customer_order_history_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil riwayat pesanan: {e}"}


@tool(args_schema=SearchProductsSemanticInput)
async def search_products_semantic(
    store_id: str,
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search products using semantic vector similarity. Falls back to keyword search if RAG is unavailable."""
    try:
        from app.services.product import ProductService

        async with async_session_factory() as db:
            svc = ProductService(db)
            results = await svc.search_semantic_products(query, UUID(store_id), limit=limit)

        if not results:
            # Fallback to keyword search
            keywords = query.lower().split()
            async with async_session_factory() as db:
                svc = ProductService(db)
                products = await svc.search_by_keywords(UUID(store_id), keywords, limit=limit)

            if not products:
                return {"success": True, "message": "Tidak ditemukan produk yang cocok.", "data": []}

            keyword_items: list[dict[str, Any]] = [
                {
                    "product_id": str(p.id),
                    "name": p.name,
                    "price": int(p.price),
                    "price_display": _format_rupiah(p.price),
                    "stock": p.stock,
                    "description": p.description,
                    "image_url": p.image_url,
                }
                for p in products
            ]
            return {"success": True, "message": f"Ditemukan {len(keyword_items)} produk (pencarian kata kunci).", "data": keyword_items}

        # Semantic results are dicts from RAG
        semantic_items: list[dict[str, Any]] = []
        for r in results:
            metadata_raw = r.get("metadata", {})
            metadata: dict[str, Any] = metadata_raw if isinstance(metadata_raw, dict) else {}
            price_val = metadata.get("price", 0)
            score_val = r.get("score", 0.0)
            semantic_items.append({
                "product_id": str(metadata.get("product_id", "")),
                "name": str(metadata.get("name", "")),
                "price": int(price_val) if isinstance(price_val, int | float) else 0,
                "description": str(r.get("text", "")),
                "score": float(score_val) if isinstance(score_val, int | float) else 0.0,
            })
        return {"success": True, "message": f"Ditemukan {len(semantic_items)} produk (pencarian semantik).", "data": semantic_items}
    except Exception as e:
        log.error("tool_search_products_semantic_error", error=str(e))
        return {"success": False, "message": f"Gagal mencari produk secara semantik: {e}"}


# ---------------------------------------------------------------------------
# Merchant CRUD tools
# ---------------------------------------------------------------------------


class UpdateProductStockInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    product_id: str = Field(description="UUID of the product to update")
    quantity_add: int = Field(description="Quantity to ADD to current stock (e.g. 20)")


class CreateProductInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    name: str = Field(description="Product name")
    price: int = Field(description="Product price in Rupiah")
    stock: int = Field(default=0, description="Initial stock quantity")
    description: str | None = Field(default=None, description="Optional product description")
    weight: int | None = Field(default=None, description="Optional weight in grams")
    image_url: str | None = Field(default=None, description="Optional product image URL")


class GetAllOrdersInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    status: str | None = Field(default=None, description="Filter by status: pending_payment, confirmed, paid, cancelled")


@tool(args_schema=UpdateProductStockInput)
async def update_product_stock(
    store_id: str,
    product_id: str,
    quantity_add: int,
) -> dict[str, Any]:
    """Merchant-only: Add stock quantity to an existing product."""
    try:
        from app.models.commerce import Store
        from app.services.product import ProductService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            product_svc = ProductService(db)
            product = await product_svc.get_by_id(UUID(product_id))
            if product is None or product.store_id != store.id:
                return {"success": False, "message": "Produk tidak ditemukan di toko ini."}

            old_stock = product.stock or 0
            new_stock = old_stock + quantity_add
            from app.schemas.commerce import ProductUpdate
            await product_svc.update(product, ProductUpdate(stock=new_stock))

            return {
                "success": True,
                "message": f"Stok {product.name} berhasil ditambah {quantity_add} (dari {old_stock} jadi {new_stock}).",
                "data": {"product_id": str(product.id), "name": product.name, "stock": new_stock},
            }
    except Exception as e:
        log.error("tool_update_stock_error", error=str(e))
        return {"success": False, "message": f"Gagal mengupdate stok: {e}"}


@tool(args_schema=CreateProductInput)
async def create_product(
    store_id: str,
    name: str,
    price: int,
    stock: int = 0,
    description: str | None = None,
    weight: int | None = None,
    image_url: str | None = None,
) -> dict[str, Any]:
    """Merchant-only: Create a new product in the store."""
    try:
        from app.models.commerce import Store
        from app.schemas.commerce import ProductCreate
        from app.services.product import ProductService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            product_svc = ProductService(db)
            data = ProductCreate(
                name=name,
                price=price,
                stock=stock,
                description=description or "",
                weight=weight,
                image_url=image_url,
            )
            product = await product_svc.create(store, data)

            return {
                "success": True,
                "message": f"Produk {product.name} berhasil dibuat!",
                "data": {"product_id": str(product.id), "name": product.name, "price": product.price, "stock": product.stock},
            }
    except Exception as e:
        log.error("tool_create_product_error", error=str(e))
        return {"success": False, "message": f"Gagal membuat produk: {e}"}


@tool(args_schema=GetAllOrdersInput)
async def get_all_orders(
    store_id: str,
    status: str | None = None,
) -> dict[str, Any]:
    """Merchant-only: List all orders for the store, optionally filtered by status."""
    try:
        from app.models.commerce import OrderStatus
        from app.services.order import OrderService

        async with async_session_factory() as db:
            order_svc = OrderService(db)
            orders = await order_svc.list_by_store(UUID(store_id))

            if status:
                status_upper = status.upper()
                try:
                    target_status = OrderStatus(status_upper) if status_upper in {s.value for s in OrderStatus} else None
                except ValueError:
                    target_status = None
                if target_status:
                    orders = [o for o in orders if o.status == target_status]

            if not orders:
                return {"success": True, "message": "Belum ada transaksi.", "data": []}

            items = []
            for o in orders:
                items.append({
                    "order_id": str(o.id),
                    "customer_phone": o.customer_phone,
                    "customer_name": o.customer_name,
                    "total": int(o.total) if o.total else 0,
                    "status": o.status.value if hasattr(o.status, "value") else str(o.status),
                    "items": o.items,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                })

            return {
                "success": True,
                "message": f"Ditemukan {len(items)} transaksi.",
                "data": items,
            }
    except Exception as e:
        log.error("tool_get_all_orders_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil daftar transaksi: {e}"}


# ---------------------------------------------------------------------------
# Stats tool
# ---------------------------------------------------------------------------


class GetStoreStatsInput(BaseModel):
    store_id: str = Field(description="UUID of the store")


@tool(args_schema=GetStoreStatsInput)
async def get_store_stats(store_id: str) -> dict[str, Any]:
    """Merchant-only: Get comprehensive store statistics (revenue, orders, products, top sellers)."""
    try:
        from collections import Counter

        from sqlalchemy import func, select

        from app.models.commerce import Order, OrderStatus, Product
        from app.services.order import OrderService

        async with async_session_factory() as db:
            order_svc = OrderService(db)

            # ── Aggregate stats ──────────────────────────────────────────
            revenue = await order_svc.get_revenue(UUID(store_id))
            pending = await order_svc.get_pending_count(UUID(store_id))

            total_orders = (
                await db.execute(
                    select(func.count(Order.id)).where(Order.store_id == UUID(store_id))
                )
            ).scalar() or 0

            # ── Order status breakdown ───────────────────────────────────
            status_rows = await db.execute(
                select(Order.status, func.count(Order.id).label("cnt"))
                .where(Order.store_id == UUID(store_id))
                .group_by(Order.status)
            )
            status_breakdown = {str(row.status.value if hasattr(row.status, 'value') else row.status): row.cnt for row in status_rows}

            # ── Paid / confirmed orders for per-order calculations ──────
            paid_confirmed = [OrderStatus.PAID, OrderStatus.CONFIRMED]
            paid_count = await db.execute(
                select(func.count(Order.id)).where(
                    Order.store_id == UUID(store_id),
                    Order.status.in_(paid_confirmed),
                )
            )
            paid_total = paid_count.scalar() or 0
            avg_order_value = int(revenue / paid_total) if paid_total > 0 else 0

            # ── Top 5 products by sales volume ───────────────────────────
            sales_rows = await db.execute(
                select(Order.items).where(
                    Order.store_id == UUID(store_id),
                    Order.status.in_(paid_confirmed),
                )
            )
            product_counts: Counter[str] = Counter()
            product_names: dict[str, str] = {}
            for row in sales_rows.scalars():
                for raw in row:
                    item = dict(raw)
                    pid = str(item.get("product_id", ""))
                    if pid:
                        qty_raw = item.get("quantity", 0)
                        if isinstance(qty_raw, int):
                            qty = qty_raw
                        elif isinstance(qty_raw, str):
                            qty = int(qty_raw) if qty_raw.strip().isdigit() else 0
                        else:
                            qty = 0
                        product_counts[pid] += qty
                        product_names.setdefault(pid, str(item.get("name", "")))

            top_products = [
                {"product_id": pid, "name": product_names.get(pid, ""), "quantity_sold": qty}
                for pid, qty in product_counts.most_common(5)
            ]

            # ── Low stock count ──────────────────────────────────────────
            low_stock_count = (
                await db.execute(
                    select(func.count(Product.id)).where(
                        Product.store_id == UUID(store_id),
                        Product.is_active.is_(True),
                        Product.stock <= 5,
                    )
                )
            ).scalar() or 0

            # ── Distinct customers ──────────────────────────────────────
            customer_count = (
                await db.execute(
                    select(func.count(func.distinct(Order.customer_phone)))
                    .where(Order.store_id == UUID(store_id))
                )
            ).scalar() or 0

            # ── Active products count ────────────────────────────────────
            active_products = (
                await db.execute(
                    select(func.count(Product.id)).where(
                        Product.store_id == UUID(store_id),
                        Product.is_active.is_(True),
                    )
                )
            ).scalar() or 0

        data: dict[str, Any] = {
            "total_revenue": revenue,
            "total_revenue_display": _format_rupiah(revenue),
            "total_orders": total_orders,
            "paid_orders": paid_total,
            "pending_orders": pending,
            "average_order_value": avg_order_value,
            "average_order_value_display": _format_rupiah(avg_order_value) if avg_order_value else "Rp 0",
            "active_products": active_products,
            "low_stock_products": low_stock_count,
            "total_customers": customer_count,
            "order_status_breakdown": status_breakdown,
            "top_products": top_products,
        }

        return {"success": True, "message": f"Ada {total_orders} pesanan, omzet {_format_rupiah(revenue)}, {active_products} produk aktif.", "data": data}
    except Exception as e:
        log.error("tool_get_store_stats_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil statistik toko: {e}"}


# ---------------------------------------------------------------------------
# Cancel order (merchant only)
# ---------------------------------------------------------------------------


class CancelOrderInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    order_id: str = Field(description="UUID of the order to cancel")


@tool(args_schema=CancelOrderInput)
async def cancel_order(store_id: str, order_id: str) -> dict[str, Any]:
    """Merchant-only: Cancel a pending order and restore product stock."""
    try:
        from app.services.order import OrderService

        async with async_session_factory() as db:
            order_svc = OrderService(db)
            order = await order_svc.cancel_order(UUID(store_id), UUID(order_id))

            return {
                "success": True,
                "message": f"Pesanan {order.id} berhasil dibatalkan.",
                "data": {"order_id": str(order.id), "status": str(order.status)},
            }
    except ValueError as e:
        return {"success": False, "message": str(e), "edge_case": "cancel_not_allowed"}
    except Exception as e:
        log.error("tool_cancel_order_error", error=str(e))
        return {"success": False, "message": f"Gagal membatalkan pesanan: {e}"}


# ---------------------------------------------------------------------------
# Update product info (merchant only)
# ---------------------------------------------------------------------------


class UpdateProductInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    product_id: str = Field(description="UUID of the product to update")
    name: str | None = Field(default=None, description="New product name")
    price: int | None = Field(default=None, description="New price in Rupiah")
    description: str | None = Field(default=None, description="New description")
    stock: int | None = Field(default=None, description="New stock quantity (absolute, not delta)")
    is_active: bool | None = Field(default=None, description="Set to false to nonaktifkan produk")


@tool(args_schema=UpdateProductInput)
async def update_product(
    store_id: str,
    product_id: str,
    name: str | None = None,
    price: int | None = None,
    description: str | None = None,
    stock: int | None = None,
    is_active: bool | None = None,
) -> dict[str, Any]:
    """Merchant-only: Update an existing product's name, price, description, stock, or status."""
    try:
        from app.models.commerce import Store
        from app.schemas.commerce import ProductUpdate
        from app.services.product import ProductService

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            product_svc = ProductService(db)
            product = await product_svc.get_by_id(UUID(product_id))
            if product is None or product.store_id != store.id:
                return {"success": False, "message": "Produk tidak ditemukan di toko ini."}

            update_data = ProductUpdate(
                name=name,
                price=price,
                description=description,
                stock=stock,
                is_active=is_active,
            )
            updated = await product_svc.update(product, update_data)

            return {
                "success": True,
                "message": f"Produk {updated.name} berhasil diupdate.",
                "data": {
                    "product_id": str(updated.id),
                    "name": updated.name,
                    "price": int(updated.price) if updated.price else 0,
                    "stock": updated.stock,
                    "is_active": updated.is_active,
                },
            }
    except Exception as e:
        log.error("tool_update_product_error", error=str(e))
        return {"success": False, "message": f"Gagal mengupdate produk: {e}"}


# ---------------------------------------------------------------------------
# Revenue report (merchant only)
# ---------------------------------------------------------------------------


class GetRevenueReportInput(BaseModel):
    store_id: str = Field(description="UUID of the store")
    days: int = Field(default=7, description="Number of days to look back (e.g. 7 for weekly, 30 for monthly)")


@tool(args_schema=GetRevenueReportInput)
async def get_revenue_report(store_id: str, days: int = 7) -> dict[str, Any]:
    """Merchant-only: Get revenue report for the last N days with daily breakdown."""
    try:
        from datetime import UTC, date, datetime, timedelta

        from sqlalchemy import func, select

        from app.models.commerce import Order, OrderStatus

        async with async_session_factory() as db:
            end_date = date.today()
            start_date = end_date - timedelta(days=days - 1)

            daily_breakdown: list[dict[str, Any]] = []
            total_revenue = 0
            total_orders = 0

            for i in range(days):
                day = end_date - timedelta(days=days - 1 - i)
                start_dt = datetime.combine(day, datetime.min.time()).replace(tzinfo=UTC)
                end_dt = start_dt + timedelta(days=1)

                revenue_result = await db.execute(
                    select(func.coalesce(func.sum(Order.total), 0)).where(
                        Order.store_id == UUID(store_id),
                        Order.status.in_([OrderStatus.PAID, OrderStatus.CONFIRMED]),
                        Order.created_at >= start_dt,
                        Order.created_at < end_dt,
                    )
                )
                day_revenue = int(revenue_result.scalar() or 0)

                count_result = await db.execute(
                    select(func.count(Order.id)).where(
                        Order.store_id == UUID(store_id),
                        Order.created_at >= start_dt,
                        Order.created_at < end_dt,
                    )
                )
                day_orders = count_result.scalar() or 0

                daily_breakdown.append({
                    "date": day.isoformat(),
                    "revenue": day_revenue,
                    "revenue_display": _format_rupiah(day_revenue),
                    "orders": day_orders,
                })
                total_revenue += day_revenue
                total_orders += day_orders

        period_label = f"{days} hari terakhir"
        return {
            "success": True,
            "message": f"Omzet {period_label}: {_format_rupiah(total_revenue)}, {total_orders} pesanan.",
            "data": {
                "period": period_label,
                "total_revenue": total_revenue,
                "total_revenue_display": _format_rupiah(total_revenue),
                "total_orders": total_orders,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily_breakdown": daily_breakdown,
            },
        }
    except Exception as e:
        log.error("tool_get_revenue_report_error", error=str(e))
        return {"success": False, "message": f"Gagal mengambil laporan omzet: {e}"}


# ---------------------------------------------------------------------------
# Forward message to store owner (customer → merchant)
# ---------------------------------------------------------------------------


class ForwardToMerchantInput(BaseModel):
    store_id: str = Field(description="UUID of the store (injected)")
    customer_phone: str = Field(description="Customer's phone number (injected)")
    message: str = Field(min_length=1, max_length=2000, description="The message the customer wants to send to the store owner")


@tool(args_schema=ForwardToMerchantInput)
async def forward_to_merchant(store_id: str, customer_phone: str, message: str) -> dict[str, Any]:
    """Forward a message from the customer to the store owner via WhatsApp.

    Use this when the customer explicitly asks to send a message, complaint,
    or question directly to the store owner (e.g. "tolong sampaikan ke
    pemilik toko bahwa ...").
    """
    try:
        from app.models.commerce import Store
        from app.services.gowa import GowaClient

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

            owner_phone = (store.owner.whatsapp_number if store.owner else None) or store.whatsapp_number
            if not owner_phone:
                return {"success": False, "message": "Pemilik toko belum memiliki nomor WhatsApp terdaftar."}

        sender = customer_phone.strip()
        body = (
            f"📩 *Pesan dari pelanggan*\n"
            f"Dari: {sender}\n\n"
            f"{message}\n\n"
            f"---\n"
            f"Balas dengan chat biasa ya kak."
        )

        client = GowaClient()
        await client.send_text_message(owner_phone, body)

        return {
            "success": True,
            "message": "Pesan sudah diteruskan ke pemilik toko ya kak.",
            "data": {"forwarded_to": owner_phone},
        }
    except Exception as e:
        log.error("tool_forward_to_merchant_error", error=str(e))
        return {"success": False, "message": f"Gagal meneruskan pesan: {e}"}


# ---------------------------------------------------------------------------
# Forward message to customer (merchant → customer)
# ---------------------------------------------------------------------------


class ForwardToCustomerInput(BaseModel):
    store_id: str = Field(description="UUID of the store (injected)")
    customer_phone: str = Field(description="Target customer's WhatsApp phone number")
    message: str = Field(min_length=1, max_length=2000, description="The message the merchant wants to send to the customer")


@tool(args_schema=ForwardToCustomerInput)
async def forward_to_customer(store_id: str, customer_phone: str, message: str) -> dict[str, Any]:
    """Merchant-only: Forward a message from the store owner to a customer via WhatsApp.

    Use this when the merchant explicitly asks to send a message or reply
    directly to a customer (e.g. "tolong sampaikan ke pelanggan ini bahwa ...").
    """
    try:
        from app.models.commerce import Store
        from app.services.gowa import GowaClient

        async with async_session_factory() as db:
            store = await db.get(Store, UUID(store_id))
            if store is None:
                return {"success": False, "message": "Toko tidak ditemukan."}

        body = (
            f"📩 *Pesan dari pemilik toko {store.name}*\n\n"
            f"{message}\n\n"
            f"---\n"
            f"Balas dengan chat biasa ya kak."
        )

        client = GowaClient()
        await client.send_text_message(customer_phone, body)

        return {
            "success": True,
            "message": f"Pesan sudah diteruskan ke pelanggan {customer_phone}.",
            "data": {"forwarded_to": customer_phone},
        }
    except Exception as e:
        log.error("tool_forward_to_customer_error", error=str(e))
        return {"success": False, "message": f"Gagal meneruskan pesan: {e}"}


# Collect all tools for easy registration.
ALL_TOOLS = [
    search_products,
    create_order,
    get_payment_info,
    answer_faq,
    get_merchant_analytics,
    get_customer_memory,
    confirm_payment_notify_merchant,
    verify_order_payment,
    get_order_status,
    add_to_cart,
    get_cart,
    update_cart_item,
    remove_from_cart,
    checkout_cart,
    recommend_products,
    upsell_product,
    cross_sell_product,
    get_active_promotions,
    send_payment_reminder,
    submit_complaint,
    submit_refund_request,
    get_low_stock_products,
    get_daily_summary,
    get_customer_order_history,
    search_products_semantic,
    update_product_stock,
    create_product,
    get_all_orders,
    get_store_stats,
    cancel_order,
    update_product,
    get_revenue_report,
    forward_to_merchant,
    forward_to_customer,
]
