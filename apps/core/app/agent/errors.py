"""Custom errors and deterministic fallback mapping for the commerce agent."""

from __future__ import annotations


class AgentError(Exception):
    """Base error for agent-level failures."""

    def __init__(self, message: str, intent: str = "unknown") -> None:
        self.intent = intent
        super().__init__(message)


class LLMUnavailableError(AgentError):
    """Raised when the LLM call fails after retries."""


class ToolExecutionError(AgentError):
    """Raised when a tool call returns an error dict."""


# Deterministic fallback replies (Indonesian) keyed by intent.
INTENT_FALLBACKS: dict[str, str] = {
    "product_discovery": "Maaf, saya tidak bisa mencari produk saat ini. "
    "Silakan coba beberapa saat lagi atau hubungi toko langsung.",
    "create_order": "Maaf, saya tidak bisa memproses pesanan saat ini. "
    "Silakan coba lagi nanti atau hubungi toko langsung.",
    "payment_info": "Maaf, informasi pembayaran tidak tersedia saat ini. "
    "Silakan hubungi toko untuk detail pembayaran.",
    "faq": "Maaf, saya tidak bisa menjawab pertanyaan Anda saat ini. "
    "Silakan coba beberapa saat lagi.",
    "merchant_analytics": "Maaf, data analytics tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    "greeting": "Halo! 👋 Ada yang bisa saya bantu? "
    "Silakan tanyakan tentang produk, pemesanan, atau pembayaran.",
    "unknown": "Maaf, saya tidak memahami pesan Anda. "
    "Ketik 'menu' untuk melihat produk atau tanyakan langsung.",
    # --- Cart ---
    "add_to_cart": "Maaf, saya tidak bisa menambahkan item ke keranjang saat ini. "
    "Silakan coba lagi nanti.",
    "view_cart": "Maaf, saya tidak bisa menampilkan keranjang saat ini. "
    "Silakan coba lagi nanti.",
    "update_cart": "Maaf, saya tidak bisa mengubah keranjang saat ini. "
    "Silakan coba lagi nanti.",
    "remove_from_cart": "Maaf, saya tidak bisa menghapus item dari keranjang saat ini. "
    "Silakan coba lagi nanti.",
    "checkout_cart": "Maaf, saya tidak bisa memproses checkout saat ini. "
    "Silakan coba lagi nanti atau hubungi toko langsung.",
    # --- Recommendations ---
    "recommend_products": "Maaf, saya tidak bisa memberikan rekomendasi saat ini. "
    "Silakan coba beberapa saat lagi.",
    "upsell": "Maaf, saya tidak bisa memberikan rekomendasi produk premium saat ini. "
    "Silakan coba beberapa saat lagi.",
    "cross_sell": "Maaf, saya tidak bisa memberikan rekomendasi produk pelengkap saat ini. "
    "Silakan coba beberapa saat lagi.",
    # --- Promotions & reminders ---
    "active_promotions": "Maaf, informasi promo tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    "payment_reminder": "Maaf, saya tidak bisa mengirim pengingat pembayaran saat ini. "
    "Silakan coba lagi nanti.",
    # --- Complaints & refunds ---
    "complaint_intake": "Maaf, saya tidak bisa menerima keluhan saat ini. "
    "Silakan hubungi toko langsung untuk menyampaikan keluhan Anda.",
    "refund_intake": "Maaf, saya tidak bisa memproses permintaan refund saat ini. "
    "Silakan hubungi toko langsung untuk pengembalian dana.",
    # --- Merchant insights ---
    "low_stock_insight": "Maaf, data stok rendah tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    "daily_summary": "Maaf, ringkasan harian tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    # --- History & search ---
    "customer_order_history": "Maaf, riwayat pesanan tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    "semantic_search": "Maaf, pencarian semantik tidak tersedia saat ini. "
    "Silakan coba beberapa saat lagi.",
    # --- Payment confirmations ---
    "payment_confirmation": "Maaf, konfirmasi pembayaran tidak dapat diproses saat ini. "
    "Silakan coba lagi nanti.",
    "order_status": "Maaf, status pesanan tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
    "verify_payment": "Maaf, verifikasi pembayaran tidak tersedia saat ini. "
    "Silakan coba lagi nanti.",
}

# Fallback for edge cases.
EDGE_CASE_FALLBACKS: dict[str, str] = {
    "no_active_products": "Saat ini tidak ada produk aktif di toko ini.",
    "out_of_stock": "Maaf, produk yang Anda cari sedang habis stok.",
    "missing_bank_account": "Belum ada rekening bank terdaftar di toko ini.",
    "ambiguous_quantity": "Berapa jumlah yang Anda inginkan? Silakan sebutkan angkanya.",
    "duplicate_product": "Produk tersebut sudah ada di keranjang Anda. "
    "Ingin menambah jumlahnya?",
    "non_indonesian": "Maaf, saya hanya bisa melayani dalam bahasa Indonesia. "
    "Silakan ulangi pesan Anda dalam bahasa Indonesia.",
    "empty_message": "Maaf, pesan Anda kosong. Silakan ketik pesan Anda.",
    "merchant_customer_mismatch": "Maaf, fitur ini hanya tersedia untuk pelanggan. "
    "Sebagai pemilik toko, Anda bisa mengakses dashboard untuk fitur tersebut.",
    "customer_merchant_mismatch": "Maaf, fitur ini hanya tersedia untuk pemilik toko.",
    "no_pending_order": "Anda belum memiliki pesanan yang menunggu pembayaran.",
    "order_not_found": "Pesanan tidak ditemukan.",
    "already_verified": "Pesanan sudah diverifikasi sebelumnya atau tidak dapat diverifikasi.",
    "unauthorized_merchant": "Maaf, fitur ini hanya tersedia untuk pemilik toko.",
    # --- Cart edge cases ---
    "cart_empty": "Keranjang Anda kosong. Silakan tambahkan produk terlebih dahulu.",
    "product_not_in_cart": "Produk tersebut tidak ditemukan di keranjang Anda.",
    "product_not_found": "Produk yang Anda cari tidak ditemukan di katalog.",
    # --- Promotion edge cases ---
    "no_active_promotions": "Saat ini tidak ada promo aktif di toko ini.",
    # --- Complaint & refund edge cases ---
    "complaint_submitted": "Keluhan Anda telah dicatat. Tim kami akan segera menghubungi Anda.",
    "refund_submitted": "Permintaan refund Anda telah dicatat. Proses refund membutuhkan waktu 3-5 hari kerja.",
    # --- Insight edge cases ---
    "no_low_stock": "Tidak ada produk dengan stok rendah saat ini. Stok semua produk aman.",
    "no_daily_data": "Tidak ada data penjualan untuk tanggal tersebut.",
    # --- Recommendation edge cases ---
    "no_recommendations": "Maaf, tidak ada rekomendasi yang tersedia saat ini.",
}


def get_fallback(intent: str, edge_case: str | None = None) -> str:
    """Return the appropriate fallback reply for a given intent or edge case."""
    if edge_case is not None and edge_case in EDGE_CASE_FALLBACKS:
        return EDGE_CASE_FALLBACKS[edge_case]
    return INTENT_FALLBACKS.get(intent, INTENT_FALLBACKS["unknown"])
