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
}


def get_fallback(intent: str, edge_case: str | None = None) -> str:
    """Return the appropriate fallback reply for a given intent or edge case."""
    if edge_case is not None and edge_case in EDGE_CASE_FALLBACKS:
        return EDGE_CASE_FALLBACKS[edge_case]
    return INTENT_FALLBACKS.get(intent, INTENT_FALLBACKS["unknown"])
