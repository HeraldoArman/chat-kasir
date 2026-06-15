"""Proactive WhatsApp notification helpers for the commerce agent."""

from __future__ import annotations

import structlog

from app.models.commerce import Complaint, Order, Product, RefundRequest, Store
from app.services.gowa import GowaClient, GowaClientError

log = structlog.get_logger()


def format_order_summary(order: Order) -> str:
    """Return a concise Indonesian order summary for WhatsApp."""
    total_value = int(order.total) if isinstance(order.total, int | float) else 0
    lines = [
        f"Pesanan: {order.id}",
        f"Pelanggan: {order.customer_phone}",
        f"Total: Rp {total_value:,}".replace(",", "."),
        f"Status: {order.status}",
        "Item:",
    ]
    for raw_item in order.items:
        item = dict(raw_item)
        name = item.get("name", "Produk")
        qty = item.get("quantity", 1)
        unit_price = item.get("unit_price", 0)
        price_value = int(unit_price) if isinstance(unit_price, int | float) else 0
        lines.append(f"- {name} x{qty} @ Rp {price_value:,}".replace(",", "."))
    if order.note:
        lines.append(f"Catatan: {order.note}")
    return "\n".join(lines)


async def notify_merchant_new_order(order: Order, store: Store) -> None:
    """Send a new-order alert to the merchant's WhatsApp number."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    summary = format_order_summary(order)
    message = f"📦 Pesanan baru masuk!\n\n{summary}\n\nBalas 'verifikasi {order.id}' untuk mengkonfirmasi pembayaran."
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_new_order_failed", order_id=str(order.id))


async def notify_merchant_payment_confirmation(order: Order, store: Store) -> None:
    """Ask the merchant to verify a payment for an existing order."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    summary = format_order_summary(order)
    message = (
        f"💰 Pelanggan mengonfirmasi transfer untuk pesanan:\n\n{summary}\n\n"
        f"Balas 'verifikasi {order.id}' setelah transfer masuk."
    )
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_payment_confirmation_failed", order_id=str(order.id))


async def notify_customer_payment_confirmed(order: Order, customer_phone: str) -> None:
    """Tell the customer their payment has been verified."""
    message = (
        f"✅ Pembayaran untuk pesanan {order.id} telah dikonfirmasi.\n\n"
        f"Total: Rp {int(order.total):,}".replace(",", ".")
        + "\nStatus: Dikonfirmasi\n\nTerima kasih telah berbelanja!"
    )
    try:
        await GowaClient().send_text_message(phone=customer_phone, message=message)
    except GowaClientError:
        log.warning("notify_customer_payment_confirmed_failed", order_id=str(order.id))


async def notify_customer_recovery(order: Order, customer_phone: str) -> None:
    """Remind a customer about an unpaid order."""
    message = (
        f"⏰ Hai! Pesanan Anda {order.id} masih menunggu pembayaran.\n\n"
        f"Total: Rp {int(order.total):,}".replace(",", ".")
        + "\n\nJika sudah transfer, balas 'sudah bayar'. "
        "Butuh bantuan? Balas saja pesan ini."
    )
    try:
        await GowaClient().send_text_message(phone=customer_phone, message=message)
    except GowaClientError:
        log.warning("notify_customer_recovery_failed", order_id=str(order.id))


async def notify_merchant_complaint(complaint: Complaint, store: Store) -> None:
    """Alert merchant about a new customer complaint."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    order_ref = f"Pesanan: {complaint.order_id}" if complaint.order_id else "Tanpa pesanan"
    message = (
        f"⚠️ Komplain baru dari {complaint.customer_phone}\n\n"
        f"Kategori: {complaint.category}\n"
        f"{order_ref}\n\n"
        f"Pesan:\n{complaint.description}"
    )
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_complaint_failed", complaint_id=str(complaint.id))


async def notify_merchant_refund(refund: RefundRequest, store: Store) -> None:
    """Alert merchant about a refund request."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    message = (
        f"🔄 Permintaan refund dari {refund.customer_phone}\n\n"
        f"Pesanan: {refund.order_id}\n"
        f"Alasan:\n{refund.reason}"
    )
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_refund_failed", refund_id=str(refund.id))


async def notify_merchant_low_stock(product: Product, store: Store) -> None:
    """Alert merchant when a product is running low on stock."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    stock = product.stock if product.stock is not None else 0
    message = (
        f"📉 Stok produk hampir habis!\n\n"
        f"Produk: {product.name}\n"
        f"Sisa stok: {stock}\n\n"
        f"Segera restock agar tidak kehabisan."
    )
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_low_stock_failed", product_id=str(product.id))


async def notify_merchant_daily_summary(
    store: Store,
    total_revenue: int,
    order_count: int,
    pending_orders: int,
    bestseller: str | None,
) -> None:
    """Send merchant a daily summary via WhatsApp."""
    if not store.whatsapp_number:
        log.warning("merchant_whatsapp_missing", store_id=str(store.id))
        return

    lines = [
        "📊 Ringkasan Harian",
        "",
        f"Omzet: Rp {total_revenue:,}".replace(",", "."),
        f"Total pesanan: {order_count}",
        f"Menunggu pembayaran: {pending_orders}",
    ]
    if bestseller:
        lines.append(f"Produk terlaris: {bestseller}")
    if pending_orders > 0:
        lines.append("\nJangan lupa follow up pelanggan yang belum bayar.")
    message = "\n".join(lines)
    try:
        await GowaClient().send_text_message(phone=store.whatsapp_number, message=message)
    except GowaClientError:
        log.warning("notify_merchant_daily_summary_failed", store_id=str(store.id))
