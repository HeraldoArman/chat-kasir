"""Proactive WhatsApp notification helpers for the commerce agent."""

from __future__ import annotations

import structlog

from app.models.commerce import Order, Store
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
